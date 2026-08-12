# -*- coding: utf-8 -*-
"""Migrate restaurants.* to sourceType + mapsEmbedUrl model.

Rules:
  - If placeUrl or mapsUrl is a Naver/Kakao/Google map link → set matching
    sourceType and regenerate mapsEmbedUrl / mapsUrl / placeUrl.
  - Shops with no map URL stay sourceType=custom (photo-first).
  - Already-correct map shops are refreshed when embed/sourceType missing.

Usage:
  python tool/migrate_shop_source.py

For tip-image cleanup + Naver-first re-resolve, prefer:
  python tool/migrate_shop_detail_cleanup.py
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path
from typing import Any

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from lib import i18n_store  # noqa: E402
from lib.shop_maps import (  # noqa: E402
    apply_maps_and_preview,
    detect_provider,
    infer_source_type,
    is_blocked_place_page_embed,
    normalize_place_url,
)


def _candidate_url(entry: dict[str, Any]) -> str:
    place = normalize_place_url(str(entry.get("placeUrl") or ""))
    if place:
        return place
    maps = normalize_place_url(str(entry.get("mapsUrl") or ""))
    return maps


def migrate_shop(entry: dict[str, Any], *, fetch_preview: bool = False) -> tuple[dict[str, Any], str]:
    """Return (updated_entry, action_label)."""
    old_st = str(entry.get("sourceType") or "").strip().lower()
    url = _candidate_url(entry)
    detected = detect_provider(url) if url else "none"

    if not url:
        # True custom: no map link
        updated = apply_maps_and_preview(
            entry,
            place_url="",
            location=str(entry.get("location") or ""),
            name=str(entry.get("name") or ""),
            source_type="custom",
            fetch_preview=False,
            regenerate=True,
        )
        if old_st != "custom" or entry.get("mapsEmbedUrl"):
            return updated, "custom"
        return entry, "skip-custom"

    # Map URL present — never leave as photo-first custom
    st = infer_source_type(
        source_type="" if old_st == "custom" else old_st,
        place_url=url,
        maps_provider=str(entry.get("mapsProvider") or ""),
    )
    if st == "custom":
        # Unknown host with a URL → treat as google panel
        st = "google" if detected in ("google", "other", "none") else detected

    needs = (
        old_st != st
        or not str(entry.get("mapsEmbedUrl") or "").strip()
        or not str(entry.get("placeUrl") or "").strip()
        or not str(entry.get("sourceType") or "").strip()
        or is_blocked_place_page_embed(str(entry.get("mapsEmbedUrl") or ""))
    )
    if not needs and old_st in ("naver", "kakao", "google"):
        return entry, "skip-ok"

    updated = apply_maps_and_preview(
        entry,
        place_url=url,
        location=str(entry.get("location") or ""),
        name=str(entry.get("name") or ""),
        source_type=st,
        fetch_preview=fetch_preview and bool(url),
        regenerate=True,
    )
    return updated, f"→{updated.get('sourceType')}"


def main() -> int:
    bundle = i18n_store.load_all()
    ko_restaurants = bundle["ko"].setdefault("restaurants", {})
    actions: list[tuple[str, str]] = []
    counts: Counter[str] = Counter()

    for slug, ko_entry in sorted(ko_restaurants.items()):
        if not isinstance(ko_entry, dict):
            continue
        updated, action = migrate_shop(ko_entry, fetch_preview=False)
        actions.append((slug, action))
        if action.startswith("skip"):
            counts[action] += 1
            continue
        counts[action] += 1
        for lang in i18n_store.LANGS:
            restaurants = bundle[lang].setdefault("restaurants", {})
            entry = dict(restaurants.get(slug) or {})
            # Keep per-lang text fields; sync map registration fields from KO result
            if lang == "ko":
                restaurants[slug] = updated
                continue
            for key in (
                "placeUrl",
                "mapsUrl",
                "mapsEmbedUrl",
                "mapsProvider",
                "sourceType",
                "previewTitle",
                "previewImage",
            ):
                if key in updated:
                    entry[key] = updated[key]
            restaurants[slug] = entry

    i18n_store.save_all(bundle)
    build_msg = i18n_store.build_bundle()

    print("Shop sourceType migration")
    for slug, action in actions:
        print(f"  {slug}: {action}")
    print("Counts:", dict(counts))
    # Final distribution
    final = Counter()
    for slug, r in (bundle["ko"].get("restaurants") or {}).items():
        if isinstance(r, dict):
            final[str(r.get("sourceType") or "(none)")] += 1
    print("Final sourceType:", dict(final))
    print(build_msg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
