# -*- coding: utf-8 -*-
"""Add/update bakery + dakhanmari shops and enrich from Naver place IDs."""
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
from lib.images import shop_photo_path  # noqa: E402
from lib.place_scrape import (  # noqa: E402
    naver_canonical_place_url,
    resolve_naver_search,
)
from lib.scaffold import shop_page_path, sync_shop_page_visual  # noqa: E402
from lib.translate import BatchStatus, fill_scalar_texts  # noqa: E402
from migrate_menu_i18n import migrate_menu_items  # noqa: E402
from migrate_shop_enrich import apply_to_bundle, enrich_one  # noqa: E402

COVER_SIZE = (1400, 933)

NEW_SHOPS = [
    {
        "kind": "desserts",
        "dish": "bread",
        "slug": "butter-and-shelter",
        "name": "버터앤쉘터",
        "place_id": "2021650754",
        "menu_hint": "빵",
    },
    {
        "kind": "desserts",
        "dish": "bread",
        "slug": "index-caramel",
        "name": "인덱스카라멜",
        "place_id": "1120415606",
        "menu_hint": "빵",
    },
    {
        "kind": "meals",
        "dish": "dakhanmari",
        "slug": "hyodam-myeongdong",
        "name": "효담칼국수 닭한마리 명동본점",
        "place_id": "",  # resolve via search
        "search": "효담칼국수 닭한마리 명동본점",
        "menu_hint": "닭한마리",
    },
]

UPDATE_SHOPS = [
    {
        "kind": "desserts",
        "dish": "bread",
        "slug": "paris-baguette",
        "name": "파리바게트 김포공항점",
        "place_id": "36693181",
    },
]


def _resize_cover(kind: str, dish: str, slug: str) -> str:
    path = shop_photo_path(kind, dish, slug)
    if not path.is_file():
        return f"cover missing: {slug}"
    try:
        from PIL import Image

        with Image.open(path) as im:
            im = im.convert("RGB")
            if im.size == COVER_SIZE:
                return f"cover ok {COVER_SIZE[0]}x{COVER_SIZE[1]}: {slug}"
            im = im.resize(COVER_SIZE, Image.Resampling.LANCZOS)
            im.save(path, "JPEG", quality=88, optimize=True)
        return f"cover resized → {COVER_SIZE[0]}x{COVER_SIZE[1]}: {slug}"
    except Exception as exc:  # noqa: BLE001
        return f"cover resize failed {slug}: {exc}"


def _ensure_created(shop: dict) -> list[str]:
    notes: list[str] = []
    slug = shop["slug"]
    page = shop_page_path(shop["kind"], shop["dish"], slug)
    place_id = str(shop.get("place_id") or "").strip()
    if not place_id and shop.get("search"):
        hit = resolve_naver_search(str(shop["search"]), force=True)
        place_id = str(hit.get("placeId") or "").strip()
        shop["place_id"] = place_id
        notes.append(
            f"resolved placeId={place_id} name={hit.get('name')!r} ok={hit.get('ok')}"
        )
        for w in hit.get("warnings") or []:
            notes.append(f"search warn: {w}")
    if not place_id:
        notes.append("ERROR: no place id")
        return notes
    place_url = naver_canonical_place_url(place_id)
    shop["place_url"] = place_url

    if page.exists():
        notes.append(f"[skip create] {slug} already exists")
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


def _update_paris(shop: dict) -> list[str]:
    notes: list[str] = []
    slug = shop["slug"]
    place_id = shop["place_id"]
    place_url = naver_canonical_place_url(place_id)
    shop["place_url"] = place_url
    bundle = i18n_store.load_all()
    for lang in i18n_store.LANGS:
        restaurants = bundle[lang].setdefault("restaurants", {})
        entry = dict(restaurants.get(slug) or {})
        entry["placeId"] = place_id
        entry["placeUrl"] = place_url
        entry["mapsUrl"] = place_url
        entry["sourceType"] = "naver"
        if lang == "ko":
            entry["name"] = shop["name"]
            entry["previewTitle"] = shop["name"]
            # Clear Muan/Mugyo-era address so enrich refreshes cleanly
            for key in ("location", "phone", "hours", "about", "previewImage"):
                if key in entry and (
                    "무안" in str(entry.get(key) or "")
                    or "무교" in str(entry.get(key) or "")
                ):
                    entry[key] = ""
            entry["location"] = ""
        restaurants[slug] = entry
    i18n_store.save_all(bundle)
    notes.append(f"[updated place] {slug} → {place_id} 김포공항점")
    return notes


def _localize_scalars(bundle: dict, shops: list[dict]) -> BatchStatus:
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


def main() -> int:
    results: list[str] = []

    # Resolve hyodam first so place_id is set before create
    for shop in NEW_SHOPS:
        for n in _ensure_created(shop):
            print(n)
            results.append(n)
        time.sleep(0.5)

    for shop in UPDATE_SHOPS:
        for n in _update_paris(shop):
            print(n)
            results.append(n)

    all_shops = NEW_SHOPS + UPDATE_SHOPS
    bundle = i18n_store.load_all()
    restaurants = bundle["ko"].setdefault("restaurants", {})

    enrich_stats: dict[str, str] = {}
    for i, shop in enumerate(all_shops):
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
        if slug == "paris-baguette":
            entry["name"] = shop["name"]
        print(f"[enrich] {slug} placeId={place_id}…")
        updated, notes, st = enrich_one(slug, entry, force=True)
        apply_to_bundle(bundle, slug, updated)
        restaurants[slug] = updated
        enrich_stats[slug] = st
        print(f"  status={st}")
        for n in notes[:10]:
            print(" ", n)
            results.append(f"{slug}: {n}")
        for n in sync_shop_page_visual(shop["kind"], shop["dish"], slug):
            print("  html:", n)
        cover_note = _resize_cover(shop["kind"], shop["dish"], slug)
        print(" ", cover_note)
        results.append(cover_note)
        if i + 1 < len(all_shops):
            time.sleep(1.0)

    # Persist enrich before translate/menu i18n
    i18n_store.save_all(bundle)
    bundle = i18n_store.load_all()

    st = _localize_scalars(bundle, all_shops)
    print("scalar translate:")
    for n in st.note_lines():
        print(" ", n)

    menu_st = BatchStatus()
    for shop in all_shops:
        slug = shop["slug"]
        ko_restaurants = bundle["ko"].setdefault("restaurants", {})
        entry = ko_restaurants.get(slug) or {}
        items = list(entry.get("menuItems") or [])
        if not items:
            print(f"[menu-i18n skip] {slug}: no menuItems")
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
    for n in menu_st.note_lines():
        print(n)

    summary = bump_asset_version()
    print(f"cache → {summary['version']}")

    print("\n=== RESULT ===")
    for shop in all_shops:
        slug = shop["slug"]
        pid = shop.get("place_id") or ""
        page = shop_page_path(shop["kind"], shop["dish"], slug)
        print(
            f"{slug}: placeId={pid} status={enrich_stats.get(slug)} "
            f"path={page.relative_to(ROOT).as_posix()}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
