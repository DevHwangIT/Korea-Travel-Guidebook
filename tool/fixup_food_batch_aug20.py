# -*- coding: utf-8 -*-
"""Finish failed shops from add_food_batch_aug20_user_list + enrich + catalog."""
from __future__ import annotations

import sys
import time
from pathlib import Path
from urllib.parse import quote

TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from lib import content, i18n_store  # noqa: E402
from lib.cache_bust import bump_asset_version  # noqa: E402
from lib.place_scrape import naver_canonical_place_url  # noqa: E402
from lib.scaffold import shop_page_path, sync_shop_page_visual  # noqa: E402
from migrate_shop_enrich import apply_to_bundle, enrich_one  # noqa: E402

# Import shop list from batch module
from add_food_batch_aug20_user_list import SHOPS  # noqa: E402


def clear_orphan_i18n(slug: str) -> bool:
    bundle = i18n_store.load_all()
    cleared = False
    for lang in i18n_store.LANGS:
        restaurants = bundle[lang].setdefault("restaurants", {})
        if slug in restaurants:
            del restaurants[slug]
            cleared = True
    if cleared:
        i18n_store.save_all(bundle)
    return cleared


def ensure_shop(shop: dict) -> list[str]:
    notes: list[str] = []
    slug = shop["slug"]
    page = shop_page_path(shop["kind"], shop["dish"], slug)
    if page.exists():
        notes.append(f"[ok] {slug}")
        return notes

    if clear_orphan_i18n(slug):
        notes.append(f"[cleared orphan] {slug}")

    pid = str(shop.get("place_id") or "").strip()
    place_url = (
        naver_canonical_place_url(pid)
        if pid
        else f"https://map.naver.com/p/search/{quote(shop.get('search') or shop['name'])}"
    )
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
            place_url=place_url,
            source_type="naver",
            fetch_preview=True,
        )
        notes.append(f"[created] {slug}")
        notes.extend(cnotes[:8])
        notes.extend(status.note_lines()[:4])
    except Exception as exc:  # noqa: BLE001
        notes.append(f"[FAIL] {slug}: {exc}")
    time.sleep(0.6)
    return notes


def enrich_missing(shops: list[dict]) -> list[str]:
    notes: list[str] = []
    bundle = i18n_store.load_all()
    for shop in shops:
        slug = shop["slug"]
        page = shop_page_path(shop["kind"], shop["dish"], slug)
        if not page.exists():
            continue
        restaurants = bundle["ko"].setdefault("restaurants", {})
        entry = dict(restaurants.get(slug) or {"name": shop["name"]})
        # Skip if already has address + placeId
        if entry.get("placeId") and entry.get("location") and entry.get("phone"):
            notes.append(f"[enrich skip] {slug}")
            continue
        pid = str(shop.get("place_id") or entry.get("placeId") or "").strip()
        if pid:
            entry["placeUrl"] = naver_canonical_place_url(pid)
            entry["placeId"] = pid
            entry["sourceType"] = "naver"
        try:
            updated, enotes, st = enrich_one(slug, entry, force=True)
            apply_to_bundle(bundle, slug, updated)
            restaurants[slug] = updated
            notes.append(f"[enrich] {slug}={st}")
            for n in sync_shop_page_visual(shop["kind"], shop["dish"], slug)[:3]:
                notes.append(f"  {n}")
        except Exception as exc:  # noqa: BLE001
            notes.append(f"[enrich fail] {slug}: {exc}")
        time.sleep(0.9)
    i18n_store.save_all(bundle)
    return notes


def main() -> int:
    print("=== fix missing shop pages ===", flush=True)
    fails = 0
    for shop in SHOPS:
        for line in ensure_shop(shop):
            print(line, flush=True)
            if line.startswith("[FAIL]"):
                fails += 1

    print("=== enrich ===", flush=True)
    for line in enrich_missing(SHOPS):
        print(line, flush=True)

    print("=== bundle/catalog ===", flush=True)
    try:
        print(i18n_store.build_bundle(), flush=True)
    except Exception as exc:  # noqa: BLE001
        print(f"bundle warn: {exc}", flush=True)
    try:
        print(content.rebuild_food_recommend_catalog(), flush=True)
    except Exception as exc:  # noqa: BLE001
        print(f"catalog warn: {exc}", flush=True)
    try:
        print(bump_asset_version(), flush=True)
    except Exception as exc:  # noqa: BLE001
        print(f"cache warn: {exc}", flush=True)

    # Verify ice-cream + counts
    from lib.scaffold import dish_index_path

    print("ice-cream page:", dish_index_path("desserts", "ice-cream").exists(), flush=True)
    print("yogurt-ice page:", dish_index_path("desserts", "yogurt-ice").exists(), flush=True)
    missing = [
        s["slug"]
        for s in SHOPS
        if not shop_page_path(s["kind"], s["dish"], s["slug"]).exists()
    ]
    print(f"still missing pages: {len(missing)} {missing}", flush=True)
    print(f"create fails this run: {fails}", flush=True)
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
