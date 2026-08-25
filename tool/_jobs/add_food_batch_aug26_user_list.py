# -*- coding: utf-8 -*-
"""Add food dishes/shops from 2026-08-26 user list.

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
from migrate_menu_i18n import migrate_menu_items  # noqa: E402
from migrate_shop_enrich import apply_to_bundle, enrich_one  # noqa: E402

COVER_SIZE = (1400, 933)

NEW_DISHES = [
    {
        "kind": "meals",
        "slug": "juk",
        "emoji": "🥣",
        "texts": {
            "ko": {
                "title": "죽",
                "desc": "쌀을 오래 끓인 부드러운 한식 죽",
                "about": "죽은 쌀을 오래 끓여 부드럽게 만든 한식입니다. 속이 편하고 든든해서 아침·회복식으로도 많이 찾습니다.",
            },
            "en": {
                "title": "Juk (Korean rice porridge)",
                "desc": "Slow-simmered Korean rice porridge",
                "about": "Juk is Korean rice porridge simmered until silky. A gentle, filling breakfast or comfort meal.",
            },
        },
    },
    {
        "kind": "meals",
        "slug": "jaecheopguk",
        "emoji": "🍲",
        "texts": {
            "ko": {
                "title": "재첩국",
                "desc": "낙동강 재첩으로 끓인 맑은 국",
                "about": "재첩국은 낙동강 재첩을 넣어 끓인 맑고 시원한 국입니다. 부산·김해 일대에서 대표적인 아침·해장 음식으로 먹습니다.",
            },
            "en": {
                "title": "Jaecheop-guk (marsh clam soup)",
                "desc": "Clear soup with Nakdong River marsh clams",
                "about": "Jaecheop-guk is a light, briny soup made with freshwater marsh clams, a Busan-area classic for breakfast or a hangover cure.",
            },
        },
    },
    {
        "kind": "meals",
        "slug": "agu-jjim",
        "emoji": "🌶️",
        "texts": {
            "ko": {
                "title": "아구찜",
                "desc": "아귀와 콩나물을 매콤하게 찐 요리",
                "about": "아구찜은 아귀와 콩나물·미나리를 매콤한 양념에 쪄낸 해물 요리입니다. 밥과 함께 나눠 먹기 좋은 안주·식사 메뉴입니다.",
            },
            "en": {
                "title": "Agu-jjim (spicy braised monkfish)",
                "desc": "Spicy steamed monkfish with bean sprouts",
                "about": "Agu-jjim is monkfish steamed with bean sprouts and greens in a spicy sauce — a shareable Korean seafood classic.",
            },
        },
    },
    {
        "kind": "desserts",
        "slug": "chapssal-kwabaegi",
        "emoji": "🥨",
        "texts": {
            "ko": {
                "title": "찹쌀 꽈배기",
                "desc": "쫄깃한 찹쌀 반죽 꽈배기",
                "about": "찹쌀 꽈배기는 찹쌀 반죽을 꽈서 튀긴 길거리 간식입니다. 겉은 바삭하고 속은 쫄깃해 시장·카페 앞에서 많이 팝니다.",
            },
            "en": {
                "title": "Chapssal kwabaegi (glutinous-rice twist doughnut)",
                "desc": "Chewy glutinous-rice twist doughnut",
                "about": "Chapssal kwabaegi is a twisted doughnut made with glutinous rice flour — crisp outside, chewy inside, a market snack favorite.",
            },
        },
    },
]

# Skip: 백년옥 (sundubu-jjigae/baeknyeonok, same place), 청와옥 (gukbap/cheongwaok),
# 깃뜰 listed twice.
SHOPS: list[dict] = [
    {
        "kind": "meals",
        "dish": "juk",
        "slug": "bonjuk-gyeongbokgung",
        "name": "본죽&비빔밥cafe 경복궁역점",
        "place_id": "1104591824",
    },
    {
        "kind": "meals",
        "dish": "jaecheopguk",
        "slug": "halmae-jaecheopguk-busan",
        "name": "할매재첩국 부산본점",
        "place_id": "11873587",
    },
    {
        "kind": "meals",
        "dish": "samgyeopsal",
        "slug": "gitteul-hongdae",
        "name": "깃뜰 홍대본점",
        "place_id": "",
        "search": "깃뜰 홍대본점",
    },
    {
        "kind": "meals",
        "dish": "samgyeopsal",
        "slug": "oneul-gimhae-dwitgogi",
        "name": "오늘김해뒷고기 본점",
        "place_id": "31234524",
    },
    {
        "kind": "meals",
        "dish": "samgyeopsal",
        "slug": "kkupdang",
        "name": "꿉당",
        "place_id": "1082960799",
    },
    {
        "kind": "meals",
        "dish": "samgyeopsal",
        "slug": "busandaek-seomyeon",
        "name": "부산댁 서면본점",
        "place_id": "",
        "search": "부산댁 서면본점",
    },
    {
        "kind": "meals",
        "dish": "samgyeopsal",
        "slug": "seolyameok-seomyeon",
        "name": "설야멱 부산서면",
        "place_id": "",
        "search": "설야멱 부산서면",
    },
    {
        "kind": "meals",
        "dish": "samgyeopsal",
        "slug": "jeongdeunjip-itaewon",
        "name": "이태원 정든집",
        "place_id": "1376882672",
    },
    {
        "kind": "meals",
        "dish": "kimbap",
        "slug": "nangman-kimbap",
        "name": "낭만김밥",
        "place_id": "1194565227",
    },
    {
        "kind": "meals",
        "dish": "makguksu",
        "slug": "apgujeong-sanghoe",
        "name": "압구정상회",
        "place_id": "2042225573",
    },
    {
        "kind": "meals",
        "dish": "budae-jjigae",
        "slug": "yungane-uijeongbu-budae",
        "name": "윤가네의정부부대찌개",
        "place_id": "1050572124",
    },
    {
        "kind": "meals",
        "dish": "bossam",
        "slug": "yeongjung-minari-bossam",
        "name": "영중미나리보쌈",
        "place_id": "",
        "search": "영중미나리보쌈",
    },
    {
        "kind": "meals",
        "dish": "samgyetang",
        "slug": "samojeong-seomyeon",
        "name": "삼오정 서면점",
        "place_id": "",
        "search": "삼오정 서면점",
    },
    {
        "kind": "meals",
        "dish": "agu-jjim",
        "slug": "nojak-jinseong-agu-dongtan",
        "name": "노작진성아구찜 동탄본점",
        "place_id": "1792061156",
    },
    {
        "kind": "meals",
        "dish": "gukbap",
        "slug": "bonjeon-dwaeji-gukbap",
        "name": "본전돼지국밥",
        "place_id": "13485911",
    },
    {
        "kind": "desserts",
        "dish": "cafe",
        "slug": "chacha-tea-club-changsin",
        "name": "차차티클럽 창신한옥",
        "place_id": "37542108",
    },
    {
        "kind": "desserts",
        "dish": "cafe",
        "slug": "bean-brothers-hapjeong",
        "name": "빈브라더스 커피하우스",
        "place_id": "",
        "search": "합정역 빈브라더스 커피하우스 서울",
    },
    {
        "kind": "desserts",
        "dish": "cafe",
        "slug": "starbucks-gyeongju-daereungwon",
        "name": "스타벅스 경주대릉원점",
        "place_id": "35201864",
    },
    {
        "kind": "desserts",
        "dish": "chapssal-kwabaegi",
        "slug": "ilhosanghoe-gwangjang",
        "name": "광장시장 일호상회",
        "place_id": "1469402434",
    },
]

TAG_UPDATES = {
    "juk": {
        "tags": ["soup", "warm", "mild", "light", "nonspicy"],
    },
    "jaecheopguk": {
        "tags": ["soup", "seafood", "warm", "light", "mild"],
    },
    "agu-jjim": {
        "tags": ["seafood", "spicy", "hearty", "nosoup", "share"],
    },
    "chapssal-kwabaegi": {
        "tags": ["sweet", "snack", "street", "portable", "quickbite"],
    },
}


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
    meal_adds = ('    "juk",\n', '    "jaecheopguk",\n', '    "agu-jjim",\n')
    if '"juk"' not in text.split("MEAL_DISH_SLUGS_FALLBACK", 1)[-1].split("}", 1)[0]:
        text = text.replace(
            '    "baekban",\n}',
            '    "baekban",\n'
            + "".join(meal_adds)
            + "}",
            1,
        )
        notes.append("MEAL_DISH_SLUGS_FALLBACK += juk, jaecheopguk, agu-jjim")
    dessert_block = text.split("DESSERT_DISH_SLUGS_FALLBACK", 1)[-1].split("}", 1)[0]
    if '"chapssal-kwabaegi"' not in dessert_block:
        text = text.replace(
            '    "nangman-sandwich",\n}',
            '    "nangman-sandwich",\n    "chapssal-kwabaegi",\n}',
            1,
        )
        notes.append("DESSERT_DISH_SLUGS_FALLBACK += chapssal-kwabaegi")
    if notes:
        cpath.write_text(text, encoding="utf-8", newline="\n")
    else:
        notes.append("fallback slugs already present")
    return notes


def update_recommend_tags() -> None:
    path = TOOL_DIR.parent / "data" / "food" / "recommend-tags.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.setdefault("items", {})
    items.update(TAG_UPDATES)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
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
        time.sleep(0.3)
    return notes


def ensure_shop(shop: dict) -> list[str]:
    notes: list[str] = []
    slug = shop["slug"]
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

    shop["place_url"] = naver_canonical_place_url(place_id)
    page = shop_page_path(shop["kind"], shop["dish"], slug)
    if page.exists():
        notes.append(f"[skip shop] {slug}")
        return notes

    bundle = i18n_store.load_all()
    orphan = False
    for lang in i18n_store.LANGS:
        restaurants = bundle[lang].get("restaurants") or {}
        if slug in restaurants:
            del restaurants[slug]
            orphan = True
    if orphan:
        i18n_store.save_all(bundle)
        notes.append(f"[cleared orphan i18n] {slug}")

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
    time.sleep(0.5)
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
    all_notes.extend(ensure_dishes())
    for n in all_notes[-12:]:
        print(n, flush=True)

    print(f"=== shops ({len(SHOPS)}) ===", flush=True)
    created: list[dict] = []
    for shop in SHOPS:
        notes = ensure_shop(shop)
        all_notes.extend(notes)
        print("\n".join(notes), flush=True)
        if any(n.startswith("[created]") or n.startswith("[skip shop]") for n in notes):
            created.append(shop)

    print("=== enrich ===", flush=True)
    bundle = i18n_store.load_all()
    restaurants = bundle["ko"].setdefault("restaurants", {})
    for i, shop in enumerate(SHOPS):
        slug = shop["slug"]
        place_id = str(shop.get("place_id") or "").strip()
        place_url = str(shop.get("place_url") or naver_canonical_place_url(place_id))
        if not place_id:
            print(f"[enrich skip] {slug} no place id", flush=True)
            continue
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
        if i + 1 < len(SHOPS):
            time.sleep(1.0)

    i18n_store.save_all(bundle)
    bundle = i18n_store.load_all()

    print("=== dish covers ===", flush=True)
    for n in copy_dish_covers(SHOPS):
        print(n, flush=True)
        all_notes.append(n)

    print("=== localize ===", flush=True)
    st = localize_scalars(bundle, SHOPS)
    all_notes.extend(st.note_lines())
    i18n_store.save_all(bundle)

    print("=== menu i18n ===", flush=True)
    try:
        migrate_menu_items()
        all_notes.append("menu items migrated")
    except Exception as exc:  # noqa: BLE001
        all_notes.append(f"menu migrate skip: {exc}")

    all_notes.append(i18n_store.build_bundle())
    all_notes.append(content.rebuild_food_recommend_catalog())
    try:
        all_notes.append(str(bump_asset_version()))
    except OSError as exc:
        all_notes.append(f"version bump deferred: {exc}")

    print("\n=== SUMMARY ===", flush=True)
    fails = [n for n in all_notes if n.startswith("[FAIL]")]
    for n in fails:
        print(n, flush=True)
    print(f"shops={len(SHOPS)} fails={len(fails)}", flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
