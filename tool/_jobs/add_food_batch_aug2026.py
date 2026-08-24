# -*- coding: utf-8 -*-
"""Add/update food dishes + shops (Aug 2026 batch).

- Merge gomtang → gukbap (keep shops, redirect hub)
- New dishes: dakgangjeong, doenjang-jjigae
- Shops under kimbap / gukbap / dakgangjeong / samgyeopsal /
  kalguksu / doenjang-jjigae / bingsu / jeon
- Enrich from Naver place IDs, dish covers, i18n, catalog, cache bump
"""
from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from lib import content, i18n_store  # noqa: E402
from lib.cache_bust import bump_asset_version  # noqa: E402
from lib.images import dish_cover_path, shop_photo_path  # noqa: E402
from lib.place_scrape import (  # noqa: E402
    download_image_to,
    naver_canonical_place_url,
    resolve_naver_search,
)
from lib.scaffold import (  # noqa: E402
    dish_dir,
    hub_index_path,
    remove_card_referencing,
    shop_card_html,
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
        "slug": "dakgangjeong",
        "emoji": "🍗",
        "title": "닭강정",
        "desc": "바삭한 닭튀에 달콤매콤 양념을 입힌 한식",
        "about": (
            "닭강정은 작게 썬 닭고기를 바삭하게 튀긴 뒤 "
            "달콤매콤한 양념을 입힌 한식입니다. "
            "강릉 안목 해변의 만석닭강정처럼 관광지·시장에서도 "
            "포장해 먹기 좋은 메뉴로 유명합니다."
        ),
        "cover": "https://commons.wikimedia.org/wiki/Special:FilePath/Dak-gangjeong_2.jpg",
    },
    {
        "kind": "meals",
        "slug": "doenjang-jjigae",
        "emoji": "🍲",
        "title": "된장찌개",
        "desc": "된장 국물에 두부·채소를 끓인 한식 찌개",
        "about": (
            "된장찌개는 발효 된장으로 맛을 낸 한국의 대표 찌개입니다. "
            "두부·호박·감자·고추 등을 넣고 끓이며, "
            "밥·반찬과 함께 일상적으로 즐깁니다. "
            "외국인에게도 접근하기 쉬운 한식입니다."
        ),
        "cover": "https://commons.wikimedia.org/wiki/Special:FilePath/Doenjang-jjigae_4.jpg",
    },
]

SHOPS = [
    {
        "kind": "meals",
        "dish": "kimbap",
        "slug": "myeongran-kimbap",
        "name": "명란김밥",
        "place_id": "1833851386",
        "menu_hint": "명란김밥",
        "lng": "129.061081",
        "lat": "35.1631412",
    },
    {
        "kind": "meals",
        "dish": "gukbap",
        "slug": "okdongsik",
        "name": "옥동식",
        "place_id": "859857359",
        "menu_hint": "돼지곰탕",
        "lng": "126.9144811",
        "lat": "37.5526833",
    },
    {
        "kind": "meals",
        "dish": "gukbap",
        "slug": "daeseongjip",
        "name": "대성집",
        "place_id": "13517178",
        "menu_hint": "도가니탕",
    },
    {
        "kind": "meals",
        "dish": "dakgangjeong",
        "slug": "manseok-dakgangjeong-anmok",
        "name": "만석닭강정 안목직영점",
        "place_id": "1131801693",
        "menu_hint": "닭강정",
        "lng": "128.9485796",
        "lat": "37.771371",
    },
    {
        "kind": "meals",
        "dish": "samgyeopsal",
        "slug": "gogi-daetongryeong",
        "name": "고기대통령 본점",
        "place_id": "1353235634",
        "menu_hint": "삼겹살",
    },
    {
        "kind": "meals",
        "dish": "kalguksu",
        "slug": "chanyangjip",
        "name": "찬양집",
        "place_id": "11717523",
        "menu_hint": "칼국수",
        "lng": "126.9903224",
        "lat": "37.5727548",
    },
    {
        "kind": "meals",
        "dish": "doenjang-jjigae",
        "slug": "ttukbaegijip",
        "name": "뚝배기집",
        "place_id": "11717175",
        "menu_hint": "된장찌개",
        "lng": "126.9885481",
        "lat": "37.5695483",
    },
    {
        "kind": "desserts",
        "dish": "bingsu",
        "slug": "ikseondang",
        "name": "익선당",
        "place_id": "2065912317",
        "menu_hint": "빙수",
    },
    {
        "kind": "desserts",
        "dish": "bingsu",
        "slug": "appipore",
        "name": "아삐뽀레",
        "place_id": "1129588734",  # resolved via Naver search (아삐보레)
        "search": "아삐보레",
        "menu_hint": "빙수",
        "note": "검색명 아삐보레 → 네이버 상호 아삐뽀레",
    },
    {
        "kind": "meals",
        "dish": "jeon",
        "slug": "wonjo-sunhine-bindaetteok",
        "name": "원조순희네빈대떡",
        "place_id": "11619260",
        "menu_hint": "빈대떡",
    },
    {
        "kind": "meals",
        "dish": "jeon",
        "slug": "uirak-mangwon",
        "name": "우이락 망원본점",
        "place_id": "1040939211",
        "menu_hint": "전",
        "lng": "126.9059919",
        "lat": "37.5564437",
    },
    {
        "kind": "meals",
        "dish": "jeon",
        "slug": "mapo-cheonghakdong",
        "name": "마포청학동부침개 마포본점",
        "place_id": "11717814",
        "menu_hint": "부침개",
        "lng": "126.9537601",
        "lat": "37.5446386",
    },
    {
        "kind": "meals",
        "dish": "jeon",
        "slug": "bakgane-bindaetteok",
        "name": "박가네 빈대떡",
        "place_id": "13493819",
        "menu_hint": "빈대떡",
    },
    {
        "kind": "meals",
        "dish": "jeon",
        "slug": "imone-wangpajeon",
        "name": "이모네 왕파전",
        "place_id": "20601524",
        "menu_hint": "파전",
        "lng": "127.0560852",
        "lat": "37.5892538",
    },
]

GUKBAP_TEXTS = {
    "ko": {
        "title": "국밥",
        "desc": "국밥·곰탕·도가니탕 등 국과 밥을 함께 즐기는 든든한 한식",
        "about": (
            "국밥은 국과 밥을 한 그릇(또는 함께) 내는 한국의 든든한 한 끼입니다. "
            "돼지국밥·순대국·설렁탕은 물론, 곰탕·도가니탕처럼 오래 고아 낸 "
            "맑고 깊은 국물 요리도 이 카테고리에서 함께 소개합니다. "
            "아침·심야에도 찾기 쉬운 현지 맛집 문화입니다."
        ),
    }
}


def _redirect_html(target_rel: str, label: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="refresh" content="0;url={target_rel}">
  <link rel="canonical" href="{target_rel}">
  <title>{label}</title>
  <script>location.replace("{target_rel}");</script>
</head>
<body>
  <p><a href="{target_rel}">{label}로 이동</a></p>
</body>
</html>
"""


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


def merge_gomtang_into_gukbap() -> list[str]:
    notes: list[str] = []
    src_shop = dish_dir("meals", "gomtang") / "yeongchunok"
    dst_shop = dish_dir("meals", "gukbap") / "yeongchunok"
    if src_shop.is_dir() and not dst_shop.exists():
        shutil.move(str(src_shop), str(dst_shop))
        notes.append("moved yeongchunok: gomtang → gukbap")
    elif dst_shop.exists():
        notes.append("yeongchunok already under gukbap")
    else:
        notes.append("WARN: yeongchunok source missing")

    if dst_shop.is_dir():
        page = dst_shop / "index.html"
        if page.is_file():
            text = page.read_text(encoding="utf-8")
            text2 = text.replace("dishes.gomtang.", "dishes.gukbap.")
            if text2 != text:
                page.write_text(text2, encoding="utf-8", newline="\n")
                notes.append("yeongchunok back-link → dishes.gukbap")

    gukbap_index = dish_dir("meals", "gukbap") / "index.html"
    if gukbap_index.is_file():
        html = gukbap_index.read_text(encoding="utf-8")
        if "yeongchunok" not in html:
            from lib.scaffold import insert_before_card_grid_close

            html = insert_before_card_grid_close(
                html, shop_card_html("meals", "gukbap", "yeongchunok")
            )
            gukbap_index.write_text(html, encoding="utf-8", newline="\n")
            notes.append("gukbap hub: yeongchunok card added")

    # Redirects under gomtang/
    gomtang = dish_dir("meals", "gomtang")
    gomtang.mkdir(parents=True, exist_ok=True)
    (gomtang / "index.html").write_text(
        _redirect_html("../gukbap/index.html", "국밥"),
        encoding="utf-8",
        newline="\n",
    )
    notes.append("gomtang/index.html → redirect gukbap")
    yredir = gomtang / "yeongchunok"
    yredir.mkdir(parents=True, exist_ok=True)
    (yredir / "index.html").write_text(
        _redirect_html("../../gukbap/yeongchunok/index.html", "영춘옥"),
        encoding="utf-8",
        newline="\n",
    )
    notes.append("gomtang/yeongchunok → redirect")

    hub = hub_index_path("meals")
    if hub.is_file():
        html = hub.read_text(encoding="utf-8")
        html2 = remove_card_referencing(html, "./gomtang/")
        if html2 != html:
            hub.write_text(html2, encoding="utf-8", newline="\n")
            notes.append("meals hub: removed gomtang card")

    # Update gukbap dish copy (force translate)
    cnotes, status = content.save_dish_fields(
        "meals", "gukbap", GUKBAP_TEXTS, force_translate=True
    )
    notes.extend(cnotes)
    notes.extend(status.note_lines())
    return notes


def ensure_dishes() -> list[str]:
    notes: list[str] = []
    for d in NEW_DISHES:
        slug = d["slug"]
        page = dish_dir(d["kind"], slug) / "index.html"
        if page.exists():
            notes.append(f"[skip dish] {slug} exists")
        else:
            texts = {
                "ko": {
                    "title": d["title"],
                    "desc": d["desc"],
                    "about": d["about"],
                },
                "en": {},
                "ja": {},
                "zh": {},
            }
            cnotes, st = content.create_dish(
                d["kind"], slug, texts, emoji=d["emoji"]
            )
            notes.append(f"[created dish] {slug}")
            notes.extend(cnotes)
            notes.extend(st.note_lines())

        cover = dish_cover_path(slug, d["kind"])
        if not cover.is_file() and d.get("cover"):
            if download_image_to(cover, d["cover"]):
                notes.append(f"dish cover downloaded: {slug}")
                notes.append(_resize_jpeg(cover))
            else:
                notes.append(f"WARN: dish cover failed: {slug}")
        elif cover.is_file():
            notes.append(_resize_jpeg(cover))
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
            f"resolved {shop['search']!r} → placeId={place_id} "
            f"name={hit.get('name')!r}"
        )
    if not place_id:
        notes.append(f"ERROR: no place id for {slug}")
        return notes

    place_url = naver_canonical_place_url(place_id)
    shop["place_url"] = place_url
    page = shop_page_path(shop["kind"], shop["dish"], slug)
    if page.exists():
        notes.append(f"[skip create] {slug}")
        return notes

    texts = {
        "ko": {
            "name": shop["name"],
            "location": "",
            "menu": shop.get("menu_hint") or "",
            "price": "",
            "tip": "",
            "about": "",
        },
        "en": {},
        "ja": {},
        "zh": {},
    }
    cnotes, status = content.create_shop(
        shop["kind"],
        shop["dish"],
        slug,
        texts,
        place_url=place_url,
        source_type="naver",
        fetch_preview=True,
    )
    notes.append(f"[created] {slug}")
    notes.extend(cnotes)
    notes.extend(status.note_lines())
    if shop.get("note"):
        notes.append(f"note: {shop['note']}")
    return notes


def apply_coords(entry: dict, shop: dict) -> None:
    lat = str(shop.get("lat") or "").strip()
    lng = str(shop.get("lng") or "").strip()
    if not (lat and lng):
        return
    # Prefer enrich coords if present; else use provided
    if not (str(entry.get("lat") or "").strip() and str(entry.get("lng") or "").strip()):
        entry["lat"] = lat
        entry["lng"] = lng
    # Always ensure embed uses known good coords when user supplied
    entry["mapsEmbedUrl"] = (
        f"https://maps.google.com/maps?q={lat},{lng}&hl=ko&z=16&output=embed"
    )


def localize_scalars(bundle: dict, shops: list[dict]) -> BatchStatus:
    st = BatchStatus()
    for shop in shops:
        slug = shop["slug"]
        ko_entry = (bundle["ko"].get("restaurants") or {}).get(slug) or {}
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
            ):
                if key in ko:
                    entry[key] = ko[key]
            entry.pop("photos", None)
            entry.pop("gallery", None)
            items = entry.get("menuItems")
            if isinstance(items, list):
                for it in items:
                    if isinstance(it, dict):
                        it.pop("image", None)
            restaurants_lang[slug] = entry
    return st


def update_recommend_tags() -> None:
    path = ROOT / "data" / "food" / "recommend-tags.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.setdefault("items", {})
    items["gomtang"] = {"exclude": True}
    items["gukbap"] = {
        "tags": ["soup", "warm", "hearty", "meat", "mild", "nonspicy"]
    }
    items["dakgangjeong"] = {
        "tags": ["chicken", "spicy", "nosoup", "hearty", "quickbite"]
    }
    items["doenjang-jjigae"] = {
        "tags": ["soup", "warm", "mild", "hearty", "nonspicy"]
    }
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def patch_fallbacks() -> list[str]:
    notes: list[str] = []
    # content.py MEAL_DISH_SLUGS_FALLBACK
    cpath = TOOL_DIR / "lib" / "content.py"
    text = cpath.read_text(encoding="utf-8")
    for slug in ("dakgangjeong", "doenjang-jjigae"):
        needle = f'"{slug}"'
        if needle not in text:
            text = text.replace(
                '"gomtang",\n',
                f'"gomtang",\n    "{slug}",\n',
                1,
            )
            notes.append(f"content.py fallback +{slug}")
    cpath.write_text(text, encoding="utf-8", newline="\n")

    spath = TOOL_DIR / "lib" / "sections.py"
    stext = spath.read_text(encoding="utf-8")
    if '"dakgangjeong"' not in stext:
        stext = stext.replace(
            '"gukbap": "국밥",\n        "gomtang": "곰탕",',
            '"gukbap": "국밥",\n        "gomtang": "곰탕(리다이렉트)",\n'
            '        "dakgangjeong": "닭강정",\n'
            '        "doenjang-jjigae": "된장찌개",',
            1,
        )
        spath.write_text(stext, encoding="utf-8", newline="\n")
        notes.append("sections.py labels updated")

    # catalog heuristics
    cat = TOOL_DIR / "build-food-recommend-catalog.py"
    ct = cat.read_text(encoding="utf-8")
    if "dakgangjeong" not in ct:
        ct = ct.replace(
            r'(re.compile(r"dak|chicken|samgyetang"), ["chicken"]),',
            r'(re.compile(r"dak|chicken|samgyetang|dakgangjeong"), ["chicken"]),\n'
            r'    (re.compile(r"dakgangjeong|yangnyeom-chicken"), ["spicy", "nosoup", "quickbite"]),\n'
            r'    (re.compile(r"doenjang"), ["soup", "warm", "mild"]),',
            1,
        )
        cat.write_text(ct, encoding="utf-8", newline="\n")
        notes.append("catalog heuristics +dakgangjeong/doenjang")
    return notes


def main() -> int:
    print("=== merge gomtang → gukbap ===")
    for n in merge_gomtang_into_gukbap():
        print(" ", n)

    print("=== ensure dishes ===")
    for n in ensure_dishes():
        print(" ", n)

    print("=== patch fallbacks / tags ===")
    update_recommend_tags()
    print("  recommend-tags.json updated")
    for n in patch_fallbacks():
        print(" ", n)

    print("=== create shops ===")
    for shop in SHOPS:
        for n in ensure_shop(shop):
            print(" ", n)
        time.sleep(0.4)

    print("=== enrich ===")
    bundle = i18n_store.load_all()
    restaurants = bundle["ko"].setdefault("restaurants", {})
    enrich_stats: dict[str, str] = {}
    for i, shop in enumerate(SHOPS):
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
        print(f"[enrich] {slug} placeId={place_id}…")
        updated, notes, st = enrich_one(slug, entry, force=True)
        apply_coords(updated, shop)
        apply_to_bundle(bundle, slug, updated)
        restaurants[slug] = updated
        enrich_stats[slug] = st
        print(f"  status={st}")
        for n in notes[:8]:
            print(" ", n)
        for n in sync_shop_page_visual(shop["kind"], shop["dish"], slug):
            print("  html:", n)
        cover = shop_photo_path(shop["kind"], shop["dish"], slug)
        print(" ", _resize_jpeg(cover))
        if i + 1 < len(SHOPS):
            time.sleep(1.0)

    i18n_store.save_all(bundle)
    bundle = i18n_store.load_all()

    print("=== translate scalars ===")
    st = localize_scalars(bundle, SHOPS)
    for n in st.note_lines():
        print(" ", n)

    print("=== menu i18n ===")
    menu_st = BatchStatus()
    for shop in SHOPS:
        slug = shop["slug"]
        ko_restaurants = bundle["ko"].setdefault("restaurants", {})
        entry = ko_restaurants.get(slug) or {}
        items = list(entry.get("menuItems") or [])
        if not items:
            print(f"[menu-i18n skip] {slug}")
            continue
        migrated = migrate_menu_items(items, menu_st)
        entry["menuItems"] = migrated
        sig = next((m for m in migrated if m.get("recommend")), migrated[0])
        sig_name = sig.get("name") if isinstance(sig.get("name"), dict) else {}
        if isinstance(sig_name, dict) and sig_name.get("ko"):
            entry["menu"] = sig_name["ko"]
        for lang in i18n_store.LANGS:
            restaurants_lang = bundle[lang].setdefault("restaurants", {})
            other = dict(restaurants_lang.get(slug) or {})
            other["menuItems"] = migrated
            if lang != "ko" and isinstance(sig_name, dict) and sig_name.get(lang):
                other["menu"] = sig_name[lang]
            elif lang == "ko" and isinstance(sig_name, dict):
                other["menu"] = sig_name.get("ko") or other.get("menu") or ""
            restaurants_lang[slug] = other
        print(f"[menu-i18n] {slug}: {len(migrated)} items")

    i18n_store.save_all(bundle)
    print(i18n_store.build_bundle())
    print(content.rebuild_food_recommend_catalog())
    for n in menu_st.note_lines():
        print(n)

    summary = bump_asset_version()
    print(f"cache → {summary['version']}")

    print("\n=== SUMMARY ===")
    for shop in SHOPS:
        slug = shop["slug"]
        page = shop_page_path(shop["kind"], shop["dish"], slug)
        print(
            f"{slug}: placeId={shop.get('place_id')} "
            f"status={enrich_stats.get(slug)} "
            f"exists={page.exists()}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
