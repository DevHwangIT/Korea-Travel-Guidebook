# -*- coding: utf-8 -*-
"""Add sundubu/gejang shops + merge tangsuyuk+jajangmyeon → korean-chinese.

- Shops under sundubu-jjigae / ganjang-gejang / korean-chinese
- Enrich from Naver place IDs, strip live hours snapshots
- Redirect old dish hubs, update meals hub / recommend / cache
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

from clean_hours_snapshots import clean_hours  # noqa: E402
from lib import content, i18n_store  # noqa: E402
from lib.cache_bust import bump_asset_version  # noqa: E402
from lib.images import shop_photo_path  # noqa: E402
from lib.place_scrape import (  # noqa: E402
    naver_canonical_place_url,
    resolve_naver_search,
)
from lib.scaffold import (  # noqa: E402
    dish_card_html,
    dish_dir,
    hub_index_path,
    insert_before_card_grid_close,
    remove_card_referencing,
    shop_card_html,
    shop_page_path,
    sync_shop_page_visual,
)
from lib.translate import BatchStatus, fill_scalar_texts  # noqa: E402
from migrate_menu_i18n import migrate_menu_items  # noqa: E402
from migrate_shop_enrich import apply_to_bundle, enrich_one  # noqa: E402

COVER_SIZE = (1400, 933)

KOREAN_CHINESE_TEXTS = {
    "ko": {
        "title": "한국식 중국요리",
        "desc": "짜장면·탕수육·짬뽕 등 한국에서 즐기는 중화요리",
        "about": (
            "한국식 중국요리(중화요리)는 짜장면·짬뽕·탕수육처럼 "
            "한국에서 발전한 중식 메뉴를 말합니다. "
            "배달·동네 중식당부터 오래된 노포까지 폭넓게 찾을 수 있고, "
            "관광객에게도 익숙한 맛으로 인기가 많습니다."
        ),
    }
}

SHOPS = [
    # —— 순두부찌개 ——
    {
        "kind": "meals",
        "dish": "sundubu-jjigae",
        "slug": "jaedong-sundubu",
        "name": "재동순두부",
        "place_id": "32239055",
        "menu_hint": "순두부찌개",
        "lng": "126.9860789",
        "lat": "37.5778683",
    },
    {
        "kind": "meals",
        "dish": "sundubu-jjigae",
        "slug": "bukchangdong-sundubu",
        "name": "북창동순두부 본점",
        "place_id": "1470022792",
        "menu_hint": "순두부찌개",
    },
    {
        "kind": "meals",
        "dish": "sundubu-jjigae",
        "slug": "baeknyeonok",
        "name": "백년옥",
        "place_id": "11678686",
        "menu_hint": "순두부찌개",
        "lng": "127.0137749",
        "lat": "37.4811951",
    },
    # —— 간장게장 ——
    {
        "kind": "meals",
        "dish": "ganjang-gejang",
        "slug": "kkotdol-gejang-1beonga",
        "name": "꽃돌게장1번가",
        "place_id": "36469012",
        "menu_hint": "간장게장",
    },
    {
        "kind": "meals",
        "dish": "ganjang-gejang",
        "slug": "seogil-sikdang",
        "name": "석일식당",
        "place_id": "",
        "search": "석일식당 간장게장",
        "menu_hint": "간장게장",
    },
    {
        "kind": "meals",
        "dish": "ganjang-gejang",
        "slug": "odarijip-daejanggeum",
        "name": "오다리집&대장금",
        "place_id": "2075313783",
        "menu_hint": "간장게장",
    },
    # —— 한국식 중국요리 ——
    {
        "kind": "meals",
        "dish": "korean-chinese",
        "slug": "yunyunchaina",
        "name": "윤윤차이나",
        "place_id": "1582460401",
        "menu_hint": "짜장면",
        "lng": "126.9268836",
        "lat": "37.4991281",
    },
    {
        "kind": "meals",
        "dish": "korean-chinese",
        "slug": "junghwaru",
        "name": "중화루",
        "place_id": "11887656",
        "menu_hint": "짜장면",
    },
    {
        "kind": "meals",
        "dish": "korean-chinese",
        "slug": "dowon-banjeom",
        "name": "도원반점",
        "place_id": "2006863459",
        "menu_hint": "탕수육",
    },
    {
        "kind": "meals",
        "dish": "korean-chinese",
        "slug": "beijing-hwagok",
        "name": "베이징 화곡본점",
        "place_id": "36250000",
        "menu_hint": "짜장면",
    },
    {
        "kind": "meals",
        "dish": "korean-chinese",
        "slug": "bokseonggak",
        "name": "복성각",
        "place_id": "13458464",
        "menu_hint": "탕수육",
    },
]


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


def strip_entry_hours(entry: dict) -> None:
    hours = entry.get("hours")
    if isinstance(hours, str) and hours:
        entry["hours"] = clean_hours(hours)


def merge_into_korean_chinese() -> list[str]:
    notes: list[str] = []
    src = dish_dir("meals", "tangsuyuk")
    dst = dish_dir("meals", "korean-chinese")

    if dst.exists() and (dst / "index.html").is_file():
        # Already merged / renamed
        index = (dst / "index.html").read_text(encoding="utf-8")
        if "meta http-equiv=\"refresh\"" in index:
            notes.append("WARN: korean-chinese looks like a redirect")
        else:
            notes.append("korean-chinese hub already exists")
    elif src.is_dir() and (src / "index.html").is_file():
        # Rename tangsuyuk → korean-chinese (moves taehyang too)
        rnotes = content.rename_dish("meals", "tangsuyuk", "korean-chinese")
        notes.append("renamed tangsuyuk → korean-chinese")
        notes.extend(rnotes)
    else:
        # Create fresh hub if neither exists usefully
        texts = {
            "ko": dict(KOREAN_CHINESE_TEXTS["ko"]),
            "en": {},
            "ja": {},
            "zh": {},
        }
        cnotes, st = content.create_dish(
            "meals", "korean-chinese", texts, emoji="🥡"
        )
        notes.append("[created dish] korean-chinese")
        notes.extend(cnotes)
        notes.extend(st.note_lines())

    # Update copy + emoji on hub page
    cnotes, status = content.save_dish_fields(
        "meals", "korean-chinese", KOREAN_CHINESE_TEXTS, force_translate=True
    )
    notes.extend(cnotes)
    notes.extend(status.note_lines())

    hub_page = dst / "index.html"
    if hub_page.is_file():
        html = hub_page.read_text(encoding="utf-8")
        html2 = html
        # Prefer takeout box emoji for the merged category
        html2 = html2.replace(">🍖 <span", ">🥡 <span", 1)
        html2 = html2.replace(">🍝 <span", ">🥡 <span", 1)
        if html2 != html:
            hub_page.write_text(html2, encoding="utf-8", newline="\n")
            notes.append("korean-chinese hub emoji updated")

    # Ensure taehyang back-link points at korean-chinese
    tae = dst / "taehyang" / "index.html"
    if tae.is_file():
        text = tae.read_text(encoding="utf-8")
        text2 = text.replace("dishes.tangsuyuk.", "dishes.korean-chinese.")
        text2 = text2.replace("dishes.jajangmyeon.", "dishes.korean-chinese.")
        if text2 != text:
            tae.write_text(text2, encoding="utf-8", newline="\n")
            notes.append("taehyang back-link → dishes.korean-chinese")

    # Redirects for old hubs (+ shop path for tangsuyuk/taehyang)
    for old_slug, label in (
        ("tangsuyuk", "한국식 중국요리"),
        ("jajangmyeon", "한국식 중국요리"),
    ):
        old_dir = dish_dir("meals", old_slug)
        # Preserve media if present under redirect shell
        if old_dir.exists() and old_slug == "tangsuyuk":
            # After rename, tangsuyuk folder is gone — recreate redirect shell
            pass
        old_dir.mkdir(parents=True, exist_ok=True)
        # Remove leftover non-redirect content carefully
        old_index = old_dir / "index.html"
        # If rename left nothing, just write redirect
        if old_slug == "jajangmyeon":
            # Keep media folder if any, but replace index with redirect
            for child in list(old_dir.iterdir()):
                if child.name == "media":
                    continue
                if child.name == "index.html":
                    continue
                if child.is_dir():
                    shutil.rmtree(child, ignore_errors=True)
                    notes.append(f"removed leftover under jajangmyeon/{child.name}")
                elif child.is_file() and child.name != "index.html":
                    child.unlink(missing_ok=True)
        old_index.write_text(
            _redirect_html("../korean-chinese/index.html", label),
            encoding="utf-8",
            newline="\n",
        )
        notes.append(f"{old_slug}/index.html → redirect korean-chinese")

    # tangsuyuk/taehyang old shop URL
    tshop = dish_dir("meals", "tangsuyuk") / "taehyang"
    tshop.mkdir(parents=True, exist_ok=True)
    (tshop / "index.html").write_text(
        _redirect_html("../../korean-chinese/taehyang/index.html", "태향"),
        encoding="utf-8",
        newline="\n",
    )
    notes.append("tangsuyuk/taehyang → redirect")

    # Meals hub: one korean-chinese card, drop jajangmyeon/tangsuyuk leftovers
    hub = hub_index_path("meals")
    if hub.is_file():
        html = hub.read_text(encoding="utf-8")
        html2 = remove_card_referencing(html, "./jajangmyeon/")
        html2 = remove_card_referencing(html2, "./tangsuyuk/")
        if "./korean-chinese/" not in html2:
            html2 = insert_before_card_grid_close(
                html2, dish_card_html("meals", "korean-chinese", "🥡")
            )
            notes.append("meals hub: added korean-chinese card")
        else:
            # Ensure emoji on existing card
            html2 = html2.replace(
                'href="./korean-chinese/index.html">\n          <img',
                'href="./korean-chinese/index.html">\n          <img',
                1,
            )
            # Replace h2 emoji if still old
            import re

            html2 = re.sub(
                r'(href="\./korean-chinese/[^"]*"[\s\S]*?<h2>)[^<]*(<span data-i18n="dishes\.korean-chinese\.title")',
                r"\1🥡 \2",
                html2,
                count=1,
            )
        if html2 != html:
            hub.write_text(html2, encoding="utf-8", newline="\n")
            notes.append("meals hub: removed jajangmyeon/tangsuyuk cards")

    return notes


def ensure_shop(shop: dict) -> list[str]:
    notes: list[str] = []
    slug = shop["slug"]
    place_id = str(shop.get("place_id") or "").strip()
    if not place_id and shop.get("search"):
        hit = resolve_naver_search(str(shop["search"]), force=True)
        place_id = str(hit.get("placeId") or "").strip()
        shop["place_id"] = place_id
        if hit.get("lat") and hit.get("lng") and not shop.get("lat"):
            shop["lat"] = str(hit["lat"])
            shop["lng"] = str(hit["lng"])
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
    return notes


def apply_coords(entry: dict, shop: dict) -> None:
    lat = str(shop.get("lat") or "").strip()
    lng = str(shop.get("lng") or "").strip()
    if not (lat and lng):
        return
    if not (
        str(entry.get("lat") or "").strip() and str(entry.get("lng") or "").strip()
    ):
        entry["lat"] = lat
        entry["lng"] = lng
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
    items["tangsuyuk"] = {"exclude": True}
    items["jajangmyeon"] = {"exclude": True}
    items["korean-chinese"] = {
        "tags": ["noodles", "meat", "mild", "nosoup", "nonspicy", "hearty"]
    }
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def patch_fallbacks() -> list[str]:
    notes: list[str] = []
    cpath = TOOL_DIR / "lib" / "content.py"
    text = cpath.read_text(encoding="utf-8")
    if '"korean-chinese"' not in text:
        text = text.replace(
            '"tangsuyuk",\n',
            '"tangsuyuk",\n    "korean-chinese",\n',
            1,
        )
        cpath.write_text(text, encoding="utf-8", newline="\n")
        notes.append("content.py fallback +korean-chinese")

    spath = TOOL_DIR / "lib" / "sections.py"
    stext = spath.read_text(encoding="utf-8")
    if '"korean-chinese"' not in stext:
        stext = stext.replace(
            '"tangsuyuk": "탕수육",',
            '"tangsuyuk": "탕수육(리다이렉트)",\n'
            '        "jajangmyeon": "짜장면(리다이렉트)",\n'
            '        "korean-chinese": "한국식 중국요리",',
            1,
        )
        # Avoid duplicate jajangmyeon key if already present elsewhere
        spath.write_text(stext, encoding="utf-8", newline="\n")
        notes.append("sections.py labels updated")

    cat = TOOL_DIR / "build-food-recommend-catalog.py"
    ct = cat.read_text(encoding="utf-8")
    if "korean-chinese" not in ct:
        ct = ct.replace(
            r'(re.compile(r"samgyeopsal|gopchang|tangsuyuk|bulgogi|bossam|tteokgalbi|jeyuk"), ["meat", "nosoup"]),',
            r'(re.compile(r"samgyeopsal|gopchang|tangsuyuk|korean-chinese|bulgogi|bossam|tteokgalbi|jeyuk"), ["meat", "nosoup"]),',
            1,
        )
        ct = ct.replace(
            r'(re.compile(r"jajang|tangsuyuk|bulgogi|bossam|tteokgalbi"), ["mild", "nosoup"]),',
            r'(re.compile(r"jajang|tangsuyuk|korean-chinese|bulgogi|bossam|tteokgalbi"), ["mild", "nosoup"]),',
            1,
        )
        ct = ct.replace(
            r'(re.compile(r"kalguksu|kongguksu|naengmyeon|jajang|makguksu|jjolmyeon"), ["noodles"]),',
            r'(re.compile(r"kalguksu|kongguksu|naengmyeon|jajang|korean-chinese|makguksu|jjolmyeon"), ["noodles"]),',
            1,
        )
        cat.write_text(ct, encoding="utf-8", newline="\n")
        notes.append("catalog heuristics +korean-chinese")
    return notes


def _safe_print(*args: object) -> None:
    try:
        print(*args)
    except UnicodeEncodeError:
        print(*(str(a).encode("ascii", "replace").decode("ascii") for a in args))


def main() -> int:
    _safe_print("=== merge tangsuyuk + jajangmyeon -> korean-chinese ===")
    for n in merge_into_korean_chinese():
        _safe_print(" ", n)

    _safe_print("=== patch fallbacks / tags ===")
    update_recommend_tags()
    _safe_print("  recommend-tags.json updated")
    for n in patch_fallbacks():
        _safe_print(" ", n)

    _safe_print("=== create shops ===")
    for shop in SHOPS:
        for n in ensure_shop(shop):
            _safe_print(" ", n)
        time.sleep(0.4)

    _safe_print("=== enrich ===")
    bundle = i18n_store.load_all()
    restaurants = bundle["ko"].setdefault("restaurants", {})
    enrich_stats: dict[str, str] = {}
    for i, shop in enumerate(SHOPS):
        slug = shop["slug"]
        place_id = str(shop.get("place_id") or "").strip()
        if not place_id:
            _safe_print(f"[enrich skip] {slug}: no place id")
            continue
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
        _safe_print(f"[enrich] {slug} placeId={place_id}…")
        updated, notes, st = enrich_one(slug, entry, force=True)
        apply_coords(updated, shop)
        strip_entry_hours(updated)
        apply_to_bundle(bundle, slug, updated)
        restaurants[slug] = updated
        enrich_stats[slug] = st
        _safe_print(f"  status={st} hours={updated.get('hours')!r}")
        for n in notes[:8]:
            _safe_print(" ", n)
        for n in sync_shop_page_visual(shop["kind"], shop["dish"], slug):
            _safe_print("  html:", n)
        cover = shop_photo_path(shop["kind"], shop["dish"], slug)
        _safe_print(" ", _resize_jpeg(cover))
        if i + 1 < len(SHOPS):
            time.sleep(1.0)

    i18n_store.save_all(bundle)
    bundle = i18n_store.load_all()

    _safe_print("=== translate scalars ===")
    st = localize_scalars(bundle, SHOPS)
    for n in st.note_lines():
        _safe_print(" ", n)

    _safe_print("=== menu i18n ===")
    menu_st = BatchStatus()
    for shop in SHOPS:
        slug = shop["slug"]
        ko_restaurants = bundle["ko"].setdefault("restaurants", {})
        entry = ko_restaurants.get(slug) or {}
        items = list(entry.get("menuItems") or [])
        if not items:
            _safe_print(f"[menu-i18n skip] {slug}")
            continue
        migrated = migrate_menu_items(items, menu_st)
        entry["menuItems"] = migrated
        strip_entry_hours(entry)
        sig = next((m for m in migrated if m.get("recommend")), migrated[0])
        sig_name = sig.get("name") if isinstance(sig.get("name"), dict) else {}
        if isinstance(sig_name, dict) and sig_name.get("ko"):
            entry["menu"] = sig_name["ko"]
        for lang in i18n_store.LANGS:
            restaurants_lang = bundle[lang].setdefault("restaurants", {})
            other = dict(restaurants_lang.get(slug) or {})
            other["menuItems"] = migrated
            if "hours" in entry:
                other["hours"] = entry["hours"]
            if lang != "ko" and isinstance(sig_name, dict) and sig_name.get(lang):
                other["menu"] = sig_name[lang]
            elif lang == "ko" and isinstance(sig_name, dict):
                other["menu"] = sig_name.get("ko") or other.get("menu") or ""
            restaurants_lang[slug] = other
        _safe_print(f"[menu-i18n] {slug}: {len(migrated)} items")

    i18n_store.save_all(bundle)
    _safe_print(i18n_store.build_bundle())
    _safe_print(content.rebuild_food_recommend_catalog())
    for n in menu_st.note_lines():
        _safe_print(n)

    summary = bump_asset_version()
    _safe_print(f"cache → {summary['version']}")

    _safe_print("\n=== SUMMARY ===")
    _safe_print("merged: tangsuyuk + jajangmyeon → korean-chinese")
    for shop in SHOPS:
        slug = shop["slug"]
        page = shop_page_path(shop["kind"], shop["dish"], slug)
        _safe_print(
            f"{shop['dish']}/{slug}: placeId={shop.get('place_id')} "
            f"status={enrich_stats.get(slug)} exists={page.exists()}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
