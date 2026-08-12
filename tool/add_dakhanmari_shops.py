# -*- coding: utf-8 -*-
"""Create dakhanmari shops and enrich from Naver place IDs."""
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
from migrate_shop_enrich import apply_to_bundle, enrich_one  # noqa: E402
from lib.scaffold import sync_shop_page_visual  # noqa: E402

SHOPS = [
    {
        "slug": "jinokhwa",
        "name": "진옥화",
        "place_id": "11619295",
        "place_url": "https://map.naver.com/p/entry/place/11619295",
    },
    {
        "slug": "suin-insadong",
        "name": "수인인사동닭한마리",
        "place_id": "1954667241",
        "place_url": "https://map.naver.com/p/entry/place/1954667241",
    },
]


def main() -> int:
    for shop in SHOPS:
        slug = shop["slug"]
        page = content.shop_page_path("meals", "dakhanmari", slug) if hasattr(content, "shop_page_path") else None
        from lib.scaffold import shop_page_path

        page = shop_page_path("meals", "dakhanmari", slug)
        if page.exists():
            print(f"[skip create] {slug} already exists")
            continue
        texts = {
            "ko": {
                "name": shop["name"],
                "location": "",
                "menu": "닭한마리",
                "price": "",
                "tip": "",
                "about": "",
            },
            "en": {},
            "ja": {},
            "zh": {},
        }
        notes, status = content.create_shop(
            "meals",
            "dakhanmari",
            slug,
            texts,
            place_url=shop["place_url"],
            source_type="naver",
            fetch_preview=True,
        )
        print(f"[created] {slug}")
        for n in notes:
            print(" ", n)
        for n in status.note_lines():
            print(" ", n)

    # Enrich both
    bundle = i18n_store.load_all()
    restaurants = bundle["ko"].setdefault("restaurants", {})
    for i, shop in enumerate(SHOPS):
        slug = shop["slug"]
        entry = restaurants.get(slug) or {
            "name": shop["name"],
            "placeUrl": shop["place_url"],
            "sourceType": "naver",
            "placeId": shop["place_id"],
        }
        # Ensure place URL / id before enrich
        entry["placeUrl"] = shop["place_url"]
        entry["placeId"] = shop["place_id"]
        entry["sourceType"] = "naver"
        print(f"[enrich] {slug}…")
        updated, notes, st = enrich_one(slug, entry, force=True)
        apply_to_bundle(bundle, slug, updated)
        restaurants[slug] = updated
        print(f"  status={st}")
        for n in notes[:8]:
            print(" ", n)
        for n in sync_shop_page_visual("meals", "dakhanmari", slug):
            print("  html:", n)
        if i + 1 < len(SHOPS):
            time.sleep(1.0)

    # Translate shop scalar fields for new shops into en/ja/zh
    from lib.translate import BatchStatus, fill_scalar_texts

    st = BatchStatus()
    for shop in SHOPS:
        slug = shop["slug"]
        ko_entry = (bundle["ko"].get("restaurants") or {}).get(slug) or {}
        texts = {
            "ko": {
                f: str(ko_entry.get(f) or "")
                for f in content.SHOP_TEXT_FIELDS
            },
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
            if lang == "ko":
                continue
            for f in content.SHOP_TEXT_FIELDS:
                if filled.get(lang, {}).get(f):
                    entry[f] = filled[lang][f]
            # Keep synced menuItems/photos from KO
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
                "photos",
                "category",
                "score",
            ):
                if key in ko:
                    entry[key] = ko[key]
            restaurants_lang[slug] = entry

    i18n_store.save_all(bundle)
    print(i18n_store.build_bundle())
    for n in st.note_lines():
        print(n)
    summary = bump_asset_version()
    print(f"cache → {summary['version']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
