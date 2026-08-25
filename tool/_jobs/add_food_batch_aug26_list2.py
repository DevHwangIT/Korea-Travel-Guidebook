# -*- coding: utf-8 -*-
"""Add food dishes/shops from 2026-08-26 second user list.

Skip shops that already exist (same place or same brand already listed).
Create missing dish menus. Enrich from Naver, localize, rebuild catalog.
"""
from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path

JOBS_DIR = Path(__file__).resolve().parent
TOOL_DIR = JOBS_DIR.parent
if str(JOBS_DIR) not in sys.path:
    sys.path.insert(0, str(JOBS_DIR))
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from lib import content, i18n_store  # noqa: E402
from lib.cache_bust import bump_asset_version  # noqa: E402
from lib.images import dish_cover_path, shop_photo_path  # noqa: E402
from lib.place_scrape import naver_canonical_place_url, resolve_naver_search  # noqa: E402
from lib.scaffold import (  # noqa: E402
    dish_card_html,
    dish_index_path,
    hub_index_path,
    insert_before_card_grid_close,
    shop_page_path,
    sync_shop_page_visual,
)
from lib.translate import BatchStatus, fill_scalar_texts  # noqa: E402
from migrate_shop_enrich import apply_to_bundle, enrich_one  # noqa: E402

COVER_SIZE = (1400, 933)

NEW_DISHES = [
    {
        "kind": "meals",
        "slug": "mandu",
        "emoji": "🥟",
        "texts": {
            "ko": {
                "title": "만두",
                "desc": "고기·채소를 속에 넣은 한식 만두",
                "about": "만두는 밀가루 피에 고기와 채소를 넣어 찌거나 굽거나 튀긴 한식입니다. 시장 포장부터 전문점 코스까지 다양합니다.",
            },
            "en": {
                "title": "Mandu (Korean dumplings)",
                "desc": "Korean dumplings with meat and vegetables",
                "about": "Mandu are Korean dumplings filled with meat and vegetables, steamed, pan-fried, or deep-fried.",
            },
        },
    },
    {
        "kind": "meals",
        "slug": "hamburger",
        "emoji": "🍔",
        "texts": {
            "ko": {
                "title": "햄버거",
                "desc": "한국에서 즐기기 좋은 햄버거",
                "about": "한국에서 자주 찾는 햄버거 브랜드와 가게를 모았습니다. 여행 중 빠르고 익숙한 한 끼로 좋습니다.",
            },
            "en": {
                "title": "Hamburger",
                "desc": "Burger spots popular with travelers in Korea",
                "about": "Korean burger chains and shops that are easy to find while traveling — a familiar, quick meal.",
            },
        },
    },
    {
        "kind": "meals",
        "slug": "nakji",
        "emoji": "🐙",
        "texts": {
            "ko": {
                "title": "낙지",
                "desc": "낙지볶음·연포탕 등 낙지 요리",
                "about": "낙지는 매콤한 볶음이나 맑은 연포탕으로 많이 먹습니다. 밥과 함께 나눠 먹기 좋은 해물 요리입니다.",
            },
            "en": {
                "title": "Nakji (octopus)",
                "desc": "Spicy stir-fried octopus and nakji soups",
                "about": "Nakji is Korean octopus, often stir-fried spicy or simmered in a clear soup. A shareable seafood meal.",
            },
        },
    },
    {
        "kind": "meals",
        "slug": "galbitang",
        "emoji": "🍲",
        "texts": {
            "ko": {
                "title": "갈비탕",
                "desc": "소갈비를 넣고 끓인 맑은 국밥",
                "about": "갈비탕은 소갈비를 오래 끓여 맑고 진한 국물을 낸 한식입니다. 해장·식사로 든든하게 먹습니다.",
            },
            "en": {
                "title": "Galbitang (short-rib soup)",
                "desc": "Clear beef short-rib soup",
                "about": "Galbitang is a clear, rich soup simmered with beef short ribs. A hearty Korean meal or hangover cure.",
            },
        },
    },
    {
        "kind": "meals",
        "slug": "hoetjip",
        "emoji": "🐟",
        "texts": {
            "ko": {
                "title": "횟집",
                "desc": "신선한 회와 해물을 즐기는 집",
                "about": "횟집은 그날 들어온 생선회와 해물을 내는 곳입니다. 시장 안 가게부터 코스 요리까지 여행 중 해산물을 먹기 좋습니다.",
            },
            "en": {
                "title": "Hoetjip (sashimi restaurant)",
                "desc": "Fresh raw fish and seafood houses",
                "about": "A hoetjip serves the day’s catch as hoe (Korean sashimi) and seafood. Markets and coastal spots are traveler favorites.",
            },
        },
    },
]

# Skip: 능동미나리 성수지점 (gukbap/neungdong-minari-seongsu, place 1594044291)
# Skip: 토속촌삼계탕 (samgyetang/tosokchon)
SHOPS: list[dict] = [
    {"kind": "meals", "dish": "samgyeopsal", "slug": "dosan-jeongyuk", "name": "도산정육 본점", "place_id": "1254940478"},
    {"kind": "meals", "dish": "samgyeopsal", "slug": "yuksanjang-hongdae", "name": "육산장 홍대본점", "place_id": "1351889411"},
    {"kind": "meals", "dish": "samgyeopsal", "slug": "wangbijip", "name": "왕비집", "place_id": "13527033"},
    {"kind": "meals", "dish": "samgyeopsal", "slug": "gojip", "name": "고짚", "place_id": "1371712780"},
    {"kind": "meals", "dish": "samgyeopsal", "slug": "seumugogae-haeundae", "name": "스무고개 해운대점", "place_id": "", "search": "스무고개 해운대점"},
    {"kind": "meals", "dish": "samgyeopsal", "slug": "hongojip-myeongdong", "name": "혼고집 명동직영점", "place_id": "", "search": "혼고집 명동직영점"},
    {"kind": "meals", "dish": "samgyeopsal", "slug": "cheongwadae-sogeumgui", "name": "청와대 소금구이", "place_id": "", "search": "선릉 청와대 소금구이"},
    {"kind": "meals", "dish": "samgyeopsal", "slug": "jikhwajangin-yongsan", "name": "직화장인 용산점", "place_id": "1537561929"},
    {"kind": "meals", "dish": "mandu", "slug": "manmanjeong-seomyeon", "name": "서면시장통 만만정", "place_id": "", "search": "서면시장통 만만정"},
    {"kind": "meals", "dish": "yukhoe", "slug": "buan-yukbi", "name": "부안육비", "place_id": "1550997885"},
    {"kind": "meals", "dish": "hamburger", "slug": "momstouch-seongsu", "name": "맘스터치 성수역점", "place_id": "1120117445"},
    {"kind": "meals", "dish": "kalguksu", "slug": "milbon-seongsu", "name": "밀본 성수본점", "place_id": "99238059"},
    {"kind": "meals", "dish": "kalguksu", "slug": "darin-daebo-kalguksu", "name": "달인대보칼국수 본점", "place_id": "1446545627"},
    {"kind": "meals", "dish": "kalguksu", "slug": "gayang-kalguksu", "name": "가양칼국수버섯매운탕", "place_id": "", "search": "가양칼국수버섯매운탕"},
    {"kind": "meals", "dish": "gamjatang", "slug": "namdareun-gamjatang", "name": "남다른감자탕", "place_id": "37463934"},
    {"kind": "meals", "dish": "gopchang", "slug": "byeolyangjip", "name": "별양집", "place_id": "", "search": "별양집"},
    {"kind": "meals", "dish": "gukbap", "slug": "nampo-seolleongtang", "name": "남포설렁탕", "place_id": "1745388715"},
    {"kind": "meals", "dish": "gukbap", "slug": "dongdong-gomguk", "name": "동동곰국", "place_id": "", "search": "동동곰국"},
    {"kind": "meals", "dish": "gukbap", "slug": "hapcheon-illyu-dwaeji-gukbap", "name": "합천일류돼지국밥", "place_id": "20299805"},
    {"kind": "meals", "dish": "makguksu", "slug": "gangnam-makguksu-bossam", "name": "강남막국수&보쌈", "place_id": "1447948679"},
    {"kind": "meals", "dish": "nakji", "slug": "yongho-nakji", "name": "용호낙지", "place_id": "2018000464"},
    {"kind": "meals", "dish": "nakji", "slug": "obongjip", "name": "오봉집", "place_id": "1587074506"},
    {"kind": "meals", "dish": "nakji", "slug": "inakesanda", "name": "이낙에산다", "place_id": "1235585297"},
    {"kind": "meals", "dish": "ganjang-gejang", "slug": "sura-gejang", "name": "수라게장", "place_id": "2025015878"},
    {"kind": "meals", "dish": "juk", "slug": "damijuk", "name": "다미죽", "place_id": "1030064285"},
    {"kind": "meals", "dish": "galbitang", "slug": "jinurin-haejang", "name": "진우린해장", "place_id": "", "search": "진우린해장"},
    {"kind": "meals", "dish": "galbitang", "slug": "silbiok", "name": "실비옥", "place_id": "", "search": "실비옥"},
    {"kind": "meals", "dish": "dolsotbap", "slug": "damsot", "name": "담솥", "place_id": "1242460653"},
    {"kind": "meals", "dish": "dolsotbap", "slug": "daraksot-pangyo", "name": "다락솥 판교파미어스몰점", "place_id": "1225058517"},
    {"kind": "meals", "dish": "kongguksu", "slug": "jinjujip", "name": "진주집", "place_id": "11678773"},
    {"kind": "meals", "dish": "kongguksu", "slug": "piyang-kong-halmeoni", "name": "피양콩할마니", "place_id": "", "search": "피양콩할마니"},
    {"kind": "meals", "dish": "hoetjip", "slug": "tamna-eomarket", "name": "탐나종합어시장", "place_id": "1037104770"},
    {"kind": "meals", "dish": "jokbal", "slug": "mongttang-jokbal", "name": "몽땅족발", "place_id": "11859729"},
    {"kind": "meals", "dish": "jangeo-gui", "slug": "haemok-nonhyeon", "name": "해목 논현점", "place_id": "1926429712"},
    {"kind": "meals", "dish": "jogae-gui", "slug": "jogaedaegyo-seomyeon", "name": "조개대교 서면 전포점", "place_id": "", "search": "조개대교 서면 전포점"},
    {"kind": "meals", "dish": "bibimbap", "slug": "sanchon", "name": "산촌", "place_id": "11715378"},
    {"kind": "meals", "dish": "makguksu", "slug": "bukchon-makguksu", "name": "북촌막국수제면소", "place_id": "", "search": "북촌막국수제면소"},
    {"kind": "desserts", "dish": "cafe", "slug": "jeokdang", "name": "적당", "place_id": "1250997417"},
    {"kind": "desserts", "dish": "cafe", "slug": "arari-bukchon", "name": "아라리 북촌", "place_id": "2016778779"},
    {"kind": "desserts", "dish": "cafe", "slug": "starbucks-daegu-jongno-gotaek", "name": "스타벅스 대구종로고택점", "place_id": "1318910127"},
    {"kind": "desserts", "dish": "bread", "slug": "bokhodu-gyeongbokgung", "name": "복호두", "place_id": "2000807420"},
    {"kind": "desserts", "dish": "bread", "slug": "oile-bakery", "name": "오일레베이커리", "place_id": "", "search": "오일레베이커리"},
    {"kind": "desserts", "dish": "bread", "slug": "london-bagel-museum-dosan", "name": "런던베이글뮤지엄 도산", "place_id": "", "search": "런던베이글뮤지엄 도산"},
    {"kind": "desserts", "dish": "bread", "slug": "butterscotch-euljiro", "name": "버터스카치 을지로", "place_id": "", "search": "버터스카치 을지로"},
    {"kind": "desserts", "dish": "bread", "slug": "donar", "name": "도나르", "place_id": "1729501476"},
    {"kind": "desserts", "dish": "bread", "slug": "haneip-bagel-seongsu", "name": "한입베이글 성수점", "place_id": "1529924272"},
    {"kind": "desserts", "dish": "hotteok", "slug": "jjoljjol-hotteok", "name": "쫄쫄호떡", "place_id": "11783797"},
    {"kind": "desserts", "dish": "tteok", "slug": "obok-tteokjip", "name": "오복떡집", "place_id": "11722259"},
    {"kind": "desserts", "dish": "bingsu", "slug": "idorim-cafe", "name": "이도림 카페", "place_id": "", "search": "이도림 카페"},
]

TAG_UPDATES = {
    "mandu": {"tags": ["portable", "nosoup", "mild", "hearty", "meat"]},
    "hamburger": {"tags": ["portable", "quickbite", "nosoup", "mild", "hearty"]},
    "nakji": {"tags": ["seafood", "spicy", "nosoup", "hearty"]},
    "galbitang": {"tags": ["soup", "warm", "meat", "hearty", "mild"]},
    "hoetjip": {"tags": ["seafood", "cold", "nosoup", "light"]},
}

SKIP_PLACE_IDS = {"1594044291"}  # 능동미나리 성수지점 already listed
SKIP_SLUGS = {"tosokchon", "neungdong-minari-seongsu"}


def _resize_jpeg(path: Path) -> str:
    if not path.is_file():
        return f"cover missing: {path}"
    try:
        from PIL import Image

        with Image.open(path) as im:
            im = im.convert("RGB")
            if im.size != COVER_SIZE:
                im = im.resize(COVER_SIZE, Image.Resampling.LANCZOS)
            im.save(path, "JPEG", quality=88, optimize=True)
        return f"cover resized {COVER_SIZE[0]}x{COVER_SIZE[1]}: {path.name}"
    except Exception as exc:  # noqa: BLE001
        return f"cover resize failed: {exc}"


def patch_fallbacks() -> list[str]:
    notes: list[str] = []
    cpath = TOOL_DIR / "lib" / "content.py"
    text = cpath.read_text(encoding="utf-8")
    meal_adds = (
        '    "mandu",\n',
        '    "hamburger",\n',
        '    "nakji",\n',
        '    "galbitang",\n',
        '    "hoetjip",\n',
    )
    block = text.split("MEAL_DISH_SLUGS_FALLBACK", 1)[-1].split("}", 1)[0]
    if '"mandu"' not in block:
        text = text.replace(
            '    "agu-jjim",\n}',
            '    "agu-jjim",\n' + "".join(meal_adds) + "}",
            1,
        )
        notes.append("MEAL_DISH_SLUGS_FALLBACK += mandu, hamburger, nakji, galbitang, hoetjip")
    if notes:
        content._write_text_retry(cpath, text)
    else:
        notes.append("fallback slugs already present")
    return notes


def update_recommend_tags() -> None:
    path = TOOL_DIR.parent / "data" / "food" / "recommend-tags.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.setdefault("items", {})
    items.update(TAG_UPDATES)
    content._write_text_retry(
        path,
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
    )


def ensure_hub_card(kind: str, slug: str, emoji: str) -> str:
    hub = hub_index_path(kind)
    if not hub.is_file():
        return f"[hub missing] {kind}"
    html = hub.read_text(encoding="utf-8")
    if f"./{slug}/index.html" in html:
        return f"[hub ok] {slug}"
    html = insert_before_card_grid_close(html, dish_card_html(kind, slug, emoji))
    content._write_text_retry(hub, html)
    return f"[hub card] {slug}"


def ensure_dishes() -> list[str]:
    notes: list[str] = []
    for d in NEW_DISHES:
        page = dish_index_path(d["kind"], d["slug"])
        if page.exists():
            notes.append(f"[skip dish] {d['slug']}")
            notes.append(ensure_hub_card(d["kind"], d["slug"], d["emoji"]))
            continue
        texts = {
            "ko": d["texts"]["ko"],
            "en": d["texts"].get("en") or {},
            "ja": {},
            "zh": {},
        }
        try:
            cnotes, st = content.create_dish(
                d["kind"], d["slug"], texts, emoji=d["emoji"]
            )
            notes.append(f"[dish] {d['slug']}")
            notes.extend(cnotes)
            notes.extend(st.note_lines())
        except ValueError as exc:
            notes.append(f"[dish warn] {d['slug']}: {exc}")
            notes.append(ensure_hub_card(d["kind"], d["slug"], d["emoji"]))
        time.sleep(0.2)
    return notes


def existing_place_index(bundle: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    for slug, entry in (bundle["ko"].get("restaurants") or {}).items():
        if not isinstance(entry, dict):
            continue
        pid = str(entry.get("placeId") or "").strip()
        if pid:
            out[pid] = slug
    return out


def ensure_shop(shop: dict, place_index: dict[str, str]) -> list[str]:
    notes: list[str] = []
    slug = shop["slug"]
    if slug in SKIP_SLUGS:
        notes.append(f"[skip listed] {slug}")
        return notes

    place_id = str(shop.get("place_id") or "").strip()
    if not place_id and shop.get("search"):
        hit = resolve_naver_search(str(shop["search"]), force=True)
        place_id = str(hit.get("placeId") or "").strip()
        shop["place_id"] = place_id
        notes.append(
            f"resolved {shop['search']!r} → placeId={place_id} name={hit.get('name')!r}"
        )
    if not place_id:
        notes.append(f"[FAIL] {slug}: no place id")
        return notes
    if place_id in SKIP_PLACE_IDS or place_id in place_index:
        existing = place_index.get(place_id, "listed")
        notes.append(f"[skip dup place] {slug} placeId={place_id} already={existing}")
        return notes

    shop["place_url"] = naver_canonical_place_url(place_id)
    page = shop_page_path(shop["kind"], shop["dish"], slug)
    if page.exists():
        notes.append(f"[skip shop] {slug}")
        return notes

    texts = {
        "ko": {
            "name": shop["name"],
            "location": "",
            "menu": "",
            "price": "",
            "tip": "",
            "about": "",
        },
        "en": {},
        "ja": {},
        "zh": {},
    }
    try:
        cnotes, status = content.create_shop(
            shop["kind"],
            shop["dish"],
            slug,
            texts,
            place_url=shop["place_url"],
            source_type="naver",
            fetch_preview=True,
        )
    except Exception as exc:  # noqa: BLE001
        notes.append(f"[FAIL] {slug}: {exc}")
        return notes
    notes.append(f"[created] {slug}")
    notes.extend(cnotes)
    notes.extend(status.note_lines())
    place_index[place_id] = slug
    time.sleep(0.3)
    return notes


def localize_scalars(bundle: dict, shops: list[dict]) -> BatchStatus:
    st = BatchStatus()
    for shop in shops:
        slug = shop["slug"]
        ko_entry = (bundle["ko"].get("restaurants") or {}).get(slug) or {}
        if not ko_entry:
            continue
        texts = {
            "ko": {f: str(ko_entry.get(f) or "") for f in content.SHOP_TEXT_FIELDS},
            "en": {},
            "ja": {},
            "zh": {},
        }
        filled = fill_scalar_texts(
            texts, content.SHOP_TEXT_FIELDS, force=True, status=st
        )
        for lang in i18n_store.LANGS:
            restaurants_lang = bundle[lang].setdefault("restaurants", {})
            entry = dict(restaurants_lang.get(slug) or {})
            if lang != "ko":
                for f in content.SHOP_TEXT_FIELDS:
                    if filled.get(lang, {}).get(f):
                        entry[f] = filled[lang][f]
            ko = (bundle["ko"].get("restaurants") or {}).get(slug) or {}
            for key in (
                "placeUrl",
                "mapsUrl",
                "mapsEmbedUrl",
                "mapsProvider",
                "sourceType",
                "previewTitle",
                "previewImage",
                "phone",
                "hours",
                "placeId",
                "menuItems",
                "category",
                "score",
                "lat",
                "lng",
                "region",
                "body",
            ):
                if key in ko and ko[key] not in (None, ""):
                    entry[key] = ko[key]
            restaurants_lang[slug] = entry
    return st


def copy_dish_covers(shops: list[dict]) -> list[str]:
    notes: list[str] = []
    for shop in shops:
        cover = dish_cover_path(shop["dish"], shop["kind"])
        if cover.is_file():
            continue
        src = shop_photo_path(shop["kind"], shop["dish"], shop["slug"])
        if not src.is_file():
            continue
        cover.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, cover)
        notes.append(_resize_jpeg(cover))
        notes.append(f"dish cover from {shop['slug']}: {shop['dish']}")
    return notes


def main() -> int:
    all_notes: list[str] = []
    print("=== fallbacks / tags ===", flush=True)
    all_notes.extend(patch_fallbacks())
    update_recommend_tags()
    all_notes.append("recommend-tags.json updated")

    print("=== dishes ===", flush=True)
    dish_notes = ensure_dishes()
    all_notes.extend(dish_notes)
    for n in dish_notes:
        print(n, flush=True)

    print("=== load i18n for dup check ===", flush=True)
    bundle = i18n_store.load_all()
    place_index = existing_place_index(bundle)

    print(f"=== shops ({len(SHOPS)}) ===", flush=True)
    created: list[dict] = []
    for shop in SHOPS:
        notes = ensure_shop(shop, place_index)
        all_notes.extend(notes)
        print("\n".join(notes), flush=True)
        if any(
            n.startswith("[created]") or n.startswith("[skip shop]")
            for n in notes
        ):
            created.append(shop)

    print("=== enrich ===", flush=True)
    bundle = i18n_store.load_all()
    restaurants = bundle["ko"].setdefault("restaurants", {})
    enrich_targets = [
        s for s in SHOPS
        if str(s.get("place_id") or "").strip()
        and s["slug"] not in SKIP_SLUGS
        and str(s.get("place_id")) not in SKIP_PLACE_IDS
        and shop_page_path(s["kind"], s["dish"], s["slug"]).exists()
    ]
    for i, shop in enumerate(enrich_targets):
        slug = shop["slug"]
        place_id = str(shop.get("place_id") or "").strip()
        place_url = str(shop.get("place_url") or naver_canonical_place_url(place_id))
        entry = restaurants.get(slug) or {
            "name": shop["name"],
            "placeUrl": place_url,
            "sourceType": "naver",
            "placeId": place_id,
        }
        entry["placeUrl"] = place_url
        entry["placeId"] = place_id
        entry["sourceType"] = "naver"
        print(f"[enrich] {slug} placeId={place_id}…", flush=True)
        try:
            updated, enotes, st = enrich_one(slug, entry, force=True)
            apply_to_bundle(bundle, slug, updated)
            restaurants[slug] = updated
            print(f"  status={st}", flush=True)
            for n in enotes[:8]:
                print(" ", n, flush=True)
            for n in sync_shop_page_visual(shop["kind"], shop["dish"], slug):
                print("  html:", n, flush=True)
            print(" ", _resize_jpeg(shop_photo_path(shop["kind"], shop["dish"], slug)), flush=True)
        except Exception as exc:  # noqa: BLE001
            print(f"[enrich fail] {slug}: {exc}", flush=True)
            all_notes.append(f"[enrich fail] {slug}: {exc}")
        if i + 1 < len(enrich_targets):
            time.sleep(0.8)

    i18n_store.save_all(bundle)
    bundle = i18n_store.load_all()

    print("=== dish covers ===", flush=True)
    for n in copy_dish_covers(enrich_targets):
        print(n, flush=True)
        all_notes.append(n)

    print("=== localize ===", flush=True)
    st = localize_scalars(bundle, enrich_targets)
    all_notes.extend(st.note_lines())
    i18n_store.save_all(bundle)

    print("=== bundle / catalog / version ===", flush=True)
    all_notes.append(i18n_store.build_bundle())
    all_notes.append(content.rebuild_food_recommend_catalog())
    try:
        all_notes.append(str(bump_asset_version()))
    except OSError as exc:
        all_notes.append(f"version bump deferred: {exc}")

    print("\n=== SUMMARY ===", flush=True)
    fails = [n for n in all_notes if n.startswith("[FAIL]")]
    skips = [n for n in all_notes if n.startswith("[skip")]
    for n in skips:
        print(n, flush=True)
    for n in fails:
        print(n, flush=True)
    print(f"shops={len(SHOPS)} created_or_existing={len(created)} fails={len(fails)}", flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
