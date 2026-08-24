# -*- coding: utf-8 -*-
"""Aug 18 batch: samgyetang/gukbap/samgyeopsal shops + cover fixes.

Shops:
  samgyetang: panax (11725476), tosokchon (35597924), pyeongsangjip-sindorim (1357279842)
  gukbap: suyeong-bonga-dwaeji-gukbap (1681791009)
  samgyeopsal: yeongcheon-yeonghwa (13124988)
  geumdwaeji already exists with placeId 37869877 — skip create, optional re-enrich

Covers:
  galbijjim hub → Wikimedia Galbijjim dish photo
  junghwaru → force Naver enrich cover
"""
from __future__ import annotations

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
from lib.place_scrape import download_image_to, naver_canonical_place_url  # noqa: E402
from lib.scaffold import sync_shop_page_visual  # noqa: E402
from lib.translate import BatchStatus, fill_scalar_texts  # noqa: E402
from migrate_menu_i18n import migrate_menu_items  # noqa: E402
from migrate_shop_enrich import apply_to_bundle, enrich_one  # noqa: E402

COVER_SIZE = (1400, 933)

# Popular braised short-rib dish photo (Wikimedia Commons)
GALBIJJIM_COVER = (
    "https://commons.wikimedia.org/wiki/Special:FilePath/"
    "Galbi-jjim_2.jpg"
)

SHOPS = [
    {
        "kind": "meals",
        "dish": "samgyetang",
        "slug": "panax",
        "name": "파낙스",
        "place_id": "11725476",
        "menu_hint": "삼계탕",
    },
    {
        "kind": "meals",
        "dish": "samgyetang",
        "slug": "tosokchon",
        "name": "토속촌삼계탕",
        "place_id": "35597924",
        "menu_hint": "삼계탕",
    },
    {
        "kind": "meals",
        "dish": "samgyetang",
        "slug": "pyeongsangjip-sindorim",
        "name": "평상집 신도림점",
        "place_id": "1357279842",
        "menu_hint": "삼계탕",
    },
    {
        "kind": "meals",
        "dish": "gukbap",
        "slug": "suyeong-bonga-dwaeji-gukbap",
        "name": "수영본가돼지국밥",
        "place_id": "1681791009",
        "menu_hint": "돼지국밥",
    },
    {
        "kind": "meals",
        "dish": "samgyeopsal",
        "slug": "yeongcheon-yeonghwa",
        "name": "영천영화",
        "place_id": "13124988",
        "menu_hint": "삼겹살",
    },
]

EXISTING_REENRICH = [
    {
        "kind": "meals",
        "dish": "korean-chinese",
        "slug": "junghwaru",
        "place_id": "11887656",
    },
]


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


def fix_galbijjim_cover() -> list[str]:
    notes: list[str] = []
    cover = dish_cover_path("galbijjim", "meals")
    cover.parent.mkdir(parents=True, exist_ok=True)
    if download_image_to(cover, GALBIJJIM_COVER):
        notes.append("galbijjim hub cover downloaded (Wikimedia Galbi-jjim_2.jpg)")
        notes.append(_resize_jpeg(cover))
    else:
        notes.append("WARN: galbijjim cover download failed")
    return notes


def ensure_shop(shop: dict) -> list[str]:
    notes: list[str] = []
    slug = shop["slug"]
    place_id = str(shop["place_id"]).strip()
    place_url = naver_canonical_place_url(place_id)
    shop["place_url"] = place_url
    from lib.scaffold import shop_page_path

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


def enrich_shop(bundle: dict, shop: dict) -> None:
    slug = shop["slug"]
    place_id = str(shop["place_id"]).strip()
    place_url = str(shop.get("place_url") or naver_canonical_place_url(place_id))
    restaurants = bundle["ko"].setdefault("restaurants", {})
    entry = restaurants.get(slug) or {
        "name": shop.get("name") or slug,
        "placeUrl": place_url,
        "sourceType": "naver",
        "placeId": place_id,
    }
    entry["placeUrl"] = place_url
    entry["placeId"] = place_id
    entry["sourceType"] = "naver"
    print(f"[enrich] {slug} placeId={place_id}…")
    updated, notes, st = enrich_one(slug, entry, force=True)
    apply_to_bundle(bundle, slug, updated)
    restaurants[slug] = updated
    print(f"  status={st}")
    for n in notes[:10]:
        print(" ", n)
    for n in sync_shop_page_visual(shop["kind"], shop["dish"], slug):
        print("  html:", n)
    cover = shop_photo_path(shop["kind"], shop["dish"], slug)
    print(" ", _resize_jpeg(cover))


def patch_samgyetang_hub() -> None:
    """Replace emptyPlaces with shopsHelp after first shop cards exist."""
    hub = ROOT / "pages" / "foods" / "meals" / "samgyetang" / "index.html"
    if not hub.is_file():
        return
    html = hub.read_text(encoding="utf-8")
    if "common.emptyPlaces" in html and "card-grid" in html:
        html = html.replace(
            '<p class="tabs-help" data-i18n="common.shopsComing"></p>\n'
            '    <p data-i18n="common.emptyPlaces">등록된 곳이 아직 없습니다.</p>',
            '<p class="tabs-help" data-i18n="common.shopsHelp"></p>',
        )
        hub.write_text(html, encoding="utf-8", newline="\n")
        print("  samgyetang hub: emptyPlaces → shopsHelp")


def main() -> int:
    print("=== galbijjim cover ===")
    for n in fix_galbijjim_cover():
        print(" ", n)

    print("=== create shops ===")
    for shop in SHOPS:
        for n in ensure_shop(shop):
            print(" ", n)
        time.sleep(0.3)

    patch_samgyetang_hub()

    print("=== enrich new shops ===")
    bundle = i18n_store.load_all()
    for i, shop in enumerate(SHOPS):
        enrich_shop(bundle, shop)
        if i + 1 < len(SHOPS):
            time.sleep(1.0)

    print("=== re-enrich junghwaru cover ===")
    for shop in EXISTING_REENRICH:
        enrich_shop(bundle, shop)
        time.sleep(0.8)

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

    summary = bump_asset_version()
    print(f"cache → {summary['version']}")

    print("\n=== SUMMARY ===")
    print("  geumdwaeji already exists placeId=37869877 (금돼지식당) — skipped")
    for shop in SHOPS:
        print(f"  {shop['slug']}: placeId={shop['place_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
