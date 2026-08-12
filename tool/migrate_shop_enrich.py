# -*- coding: utf-8 -*-
"""Enrich all restaurant shops from place links (Naver-first rich scrape).

- Fix oto → Naver place id 37629568
- Resolve search URLs to real place IDs when possible
- Scrape name/address/phone/hours/about/menus/photos
- Download images into pages/.../media/ (no hotlinking)
- Sync shop HTML visuals, rebuild i18n, bump cache version

Usage:
  python tool/migrate_shop_enrich.py
  python tool/migrate_shop_enrich.py --slug oto
  python tool/migrate_shop_enrich.py --force
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any

TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from lib import i18n_store  # noqa: E402
from lib.cache_bust import bump_asset_version  # noqa: E402
from lib.content import find_shop_page  # noqa: E402
from lib.images import shop_media_dir, shop_photo_path  # noqa: E402
from lib.place_scrape import (  # noqa: E402
    download_image_to,
    enrich_from_place_url,
    naver_canonical_place_url,
    scrape_naver_place,
)
from lib.scaffold import sync_all_shop_page_visuals, sync_shop_page_visual  # noqa: E402
from lib.shop_maps import (  # noqa: E402
    apply_maps_and_preview,
    google_embed_from_coords,
    normalize_place_url,
)

# Known corrections: slug → Naver place id
FORCE_PLACE_IDS: dict[str, str] = {
    "oto": "37629568",
}

SYNC_KEYS = (
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
)


def _pick_signature_menu(menus: list[dict[str, Any]]) -> dict[str, Any] | None:
    for m in menus:
        if m.get("recommend") and str(m.get("name") or "").strip():
            return m
    for m in menus:
        if str(m.get("name") or "").strip():
            return m
    return None


def _download_shop_media(
    kind: str,
    dish: str,
    slug: str,
    scraped: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    """Download cover / menu item / gallery images. Returns (menuItems, photos, notes)."""
    notes: list[str] = []
    media = shop_media_dir(kind, dish, slug)
    media.mkdir(parents=True, exist_ok=True)

    # Cover
    cover = shop_photo_path(kind, dish, slug)
    cover_url = ""
    photos_remote = list(scraped.get("photos") or [])
    boards = list(scraped.get("menuBoardImages") or [])
    if photos_remote:
        cover_url = photos_remote[0]
    elif scraped.get("imageUrl"):
        cover_url = str(scraped["imageUrl"])
    if cover_url and download_image_to(cover, cover_url):
        notes.append(f"cover 저장: {cover.relative_to(ROOT).as_posix()}")
    elif cover_url:
        notes.append("cover 다운로드 실패 (기존 파일 유지)")

    # Menu item images + structured menu (name kept KO here;
    # run tool/migrate_menu_i18n.py for {ko,en,ja,zh} name objects)
    menu_items: list[dict[str, Any]] = []
    menus = list(scraped.get("menus") or [])
    for i, m in enumerate(menus, start=1):
        name = str(m.get("name") or "").strip()
        if not name:
            continue
        entry: dict[str, Any] = {
            "name": name,
            "price": str(m.get("price") or "").strip(),
        }
        if m.get("recommend"):
            entry["recommend"] = True
        remote = str(m.get("image") or "").strip()
        if remote:
            dest = media / f"menu-item-{i}.jpg"
            if download_image_to(dest, remote):
                entry["image"] = f"media/menu-item-{i}.jpg"
                notes.append(f"메뉴 이미지: menu-item-{i}.jpg")
        menu_items.append(entry)

    # Gallery: remaining store photos + menu boards (local)
    local_photos: list[str] = []
    gal_i = 0
    for remote in photos_remote[:8]:
        gal_i += 1
        dest = media / f"gallery-{gal_i}.jpg"
        if download_image_to(dest, remote):
            local_photos.append(f"media/gallery-{gal_i}.jpg")
            notes.append(f"갤러리: gallery-{gal_i}.jpg")
    for remote in boards[:6]:
        board_n = len([p for p in local_photos if "menu-board-" in p]) + 1
        dest = media / f"menu-board-{board_n}.jpg"
        if download_image_to(dest, remote):
            local_photos.append(f"media/{dest.name}")
            notes.append(f"메뉴판: {dest.name}")

    return menu_items, local_photos, notes


def enrich_one(
    slug: str,
    entry: dict[str, Any],
    *,
    force: bool = False,
) -> tuple[dict[str, Any], list[str], str]:
    """Return (updated_entry, notes, status). status: enriched|partial|skipped|failed."""
    notes: list[str] = []
    updated = dict(entry)
    name = str(entry.get("name") or "").strip()
    location = str(entry.get("location") or "").strip()
    place = normalize_place_url(str(entry.get("placeUrl") or entry.get("mapsUrl") or ""))

    forced_id = FORCE_PLACE_IDS.get(slug)
    scraped: dict[str, Any]
    if forced_id:
        scraped = scrape_naver_place(forced_id, force=force)
        scraped["placeUrl"] = naver_canonical_place_url(forced_id)
        scraped["placeId"] = forced_id
        notes.append(f"강제 place id {forced_id}")
        if not scraped.get("hours"):
            from lib.place_scrape import resolve_naver_search

            q = " ".join(
                x
                for x in (
                    scraped.get("name") or name,
                    scraped.get("address") or location,
                )
                if x
            ).strip()
            if q:
                hit = resolve_naver_search(q, prefer_id=forced_id, force=force)
                if hit.get("hours"):
                    scraped["hours"] = hit["hours"]
                    notes.append(f"영업시간(검색): {hit['hours']}")
    else:
        scraped = enrich_from_place_url(
            place,
            source_type=str(entry.get("sourceType") or "naver"),
            name_hint=name,
            address_hint=location,
            force=force,
        )

    notes.extend(scraped.get("notes") or [])
    for w in scraped.get("warnings") or []:
        notes.append(f"경고: {w}")

    if not scraped.get("ok") and not scraped.get("placeId"):
        return updated, notes, "failed"

    # Maps / place URL
    place_url = str(scraped.get("placeUrl") or place)
    if scraped.get("placeId"):
        place_url = naver_canonical_place_url(str(scraped["placeId"]))
    updated = apply_maps_and_preview(
        updated,
        place_url=place_url,
        location=str(scraped.get("address") or location),
        name=str(scraped.get("name") or name),
        source_type="naver" if scraped.get("placeId") or str(entry.get("sourceType")) == "naver" else str(entry.get("sourceType") or "naver"),
        fetch_preview=False,
        regenerate=True,
    )
    if scraped.get("lat") and scraped.get("lng"):
        updated["mapsEmbedUrl"] = google_embed_from_coords(
            str(scraped["lat"]), str(scraped["lng"])
        )

    # Text fields — keep editorial tip/body; refresh factual fields
    if scraped.get("name"):
        updated["name"] = scraped["name"]
    if scraped.get("address"):
        updated["location"] = scraped["address"]
    if scraped.get("phone"):
        updated["phone"] = scraped["phone"]
    if scraped.get("hours"):
        updated["hours"] = scraped["hours"]
    if scraped.get("about"):
        old_about = str(entry.get("about") or "").strip()
        if not old_about or scraped.get("score") or len(scraped["about"]) >= len(old_about):
            updated["about"] = scraped["about"]
    if scraped.get("category"):
        updated["category"] = scraped["category"]
    if scraped.get("score"):
        updated["score"] = str(scraped["score"])
    if scraped.get("placeId"):
        updated["placeId"] = str(scraped["placeId"])
    if scraped.get("imageUrl"):
        updated["previewImage"] = scraped["imageUrl"]
        updated["previewTitle"] = scraped.get("name") or updated.get("name") or ""

    found = find_shop_page(slug)
    menu_items: list[dict[str, Any]] = []
    photos: list[str] = []
    if found:
        kind, dish, _page = found
        menu_items, photos, media_notes = _download_shop_media(
            kind, dish, slug, scraped
        )
        notes.extend(media_notes)
    else:
        # Keep remote URLs as last resort (Pages may hotlink-break)
        for m in scraped.get("menus") or []:
            item = {
                "name": str(m.get("name") or "").strip(),
                "price": str(m.get("price") or "").strip(),
            }
            if m.get("recommend"):
                item["recommend"] = True
            if m.get("image"):
                item["image"] = m["image"]
            if item["name"]:
                menu_items.append(item)
        photos = list(scraped.get("photos") or [])[:8]
        notes.append("페이지 폴더 없음 — 원격 이미지 URL 유지")

    if menu_items:
        updated["menuItems"] = menu_items
        sig = _pick_signature_menu(menu_items)
        if sig:
            updated["menu"] = sig["name"]
            if sig.get("price"):
                updated["price"] = sig["price"]
    if photos:
        updated["photos"] = photos

    status = "enriched" if (menu_items or photos or scraped.get("phone")) else "partial"
    return updated, notes, status


def apply_to_bundle(
    bundle: dict[str, dict[str, Any]],
    slug: str,
    updated: dict[str, Any],
) -> None:
    for lang in i18n_store.LANGS:
        restaurants = bundle[lang].setdefault("restaurants", {})
        entry = dict(restaurants.get(slug) or {})
        # Language-specific text: keep EN/JA name/location/about/menu/price/tip/body
        # but sync factual shared fields from KO update.
        if lang == "ko":
            entry.update(updated)
        else:
            for key in SYNC_KEYS:
                if key in updated:
                    entry[key] = updated[key]
            # Keep localized name if present; still refresh location when scraped KO address
            if updated.get("location"):
                # Only overwrite EN/JA location when empty or looks like old KO copy
                if not str(entry.get("location") or "").strip():
                    entry["location"] = updated["location"]
            if updated.get("menu") and not str(entry.get("menu") or "").strip():
                entry["menu"] = updated["menu"]
            if updated.get("price") and not str(entry.get("price") or "").strip():
                entry["price"] = updated["price"]
            # menuItems names stay KO (Naver source); acceptable for travelers
            if updated.get("menuItems"):
                entry["menuItems"] = updated["menuItems"]
            if updated.get("photos"):
                entry["photos"] = updated["photos"]
        restaurants[slug] = entry


def main() -> int:
    parser = argparse.ArgumentParser(description="Enrich shops from place scrape")
    parser.add_argument("--slug", action="append", default=[], help="Only these slugs")
    parser.add_argument("--force", action="store_true", help="Bypass scrape cache")
    parser.add_argument("--sleep", type=float, default=0.9, help="Pause between shops")
    args = parser.parse_args()

    bundle = i18n_store.load_all()
    restaurants = bundle["ko"].get("restaurants") or {}
    slugs = list(args.slug) if args.slug else sorted(restaurants.keys())

    stats = {"enriched": 0, "partial": 0, "failed": 0, "skipped": 0}
    report: list[str] = []

    for i, slug in enumerate(slugs):
        entry = restaurants.get(slug)
        if not isinstance(entry, dict):
            report.append(f"[skip] {slug}: missing")
            stats["skipped"] += 1
            continue
        print(f"[{i + 1}/{len(slugs)}] enriching {slug}…")
        try:
            updated, notes, status = enrich_one(
                slug, entry, force=bool(args.force)
            )
        except Exception as exc:  # noqa: BLE001 — batch resilience
            report.append(f"[failed] {slug}: {exc}")
            stats["failed"] += 1
            continue
        apply_to_bundle(bundle, slug, updated)
        restaurants[slug] = updated
        stats[status] = stats.get(status, 0) + 1
        report.append(f"[{status}] {slug}: " + " | ".join(notes[:6]))
        found = find_shop_page(slug)
        if found:
            kind, dish, _ = found
            for n in sync_shop_page_visual(kind, dish, slug):
                report.append(f"  html: {n}")
        if i + 1 < len(slugs):
            time.sleep(max(0.0, float(args.sleep)))

    i18n_store.save_all(bundle)
    build_msg = i18n_store.build_bundle()
    report.append(build_msg)

    if not args.slug:
        for n in sync_all_shop_page_visuals():
            report.append(n)
    else:
        # Ensure menu/gallery markup on touched shops only (already synced above)
        pass

    summary = bump_asset_version()
    report.append(
        f"cache version → {summary['version']} "
        f"(files_updated={summary['files_updated']})"
    )

    print("\n=== Summary ===")
    print(stats)
    print(f"enriched shops: {stats['enriched'] + stats['partial']}")
    for line in report:
        print(line)
    return 0 if stats["failed"] < len(slugs) else 1


if __name__ == "__main__":
    raise SystemExit(main())
