# -*- coding: utf-8 -*-
"""Backfill restaurants.*.region from Korean location addresses.

Derives city/district/dong via lib.region_parse, writes the same Korean
region object onto every GUIDE_LANG restaurant entry, then rebuilds
messages.js.

Usage:
  python tool/backfill_shop_regions.py
  python tool/backfill_shop_regions.py --dry-run
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from lib import i18n_store  # noqa: E402
from lib.region_parse import region_object  # noqa: E402


def backfill(bundle: dict[str, dict[str, Any]]) -> tuple[int, int, list[str]]:
    """Return (tagged, untagged, failure_lines)."""
    restaurants = bundle["ko"].get("restaurants") or {}
    tagged = 0
    untagged = 0
    failures: list[str] = []

    for slug in sorted(restaurants.keys()):
        entry = restaurants.get(slug)
        if not isinstance(entry, dict):
            untagged += 1
            failures.append(f"[skip] {slug}: not a dict")
            continue
        loc = str(entry.get("location") or "").strip()
        reg = region_object(loc)
        if not reg:
            untagged += 1
            failures.append(f"[untagged] {slug}: {loc or '(empty location)'}")
            continue
        for lang in i18n_store.LANGS:
            restaurants_lang = bundle[lang].setdefault("restaurants", {})
            other = dict(restaurants_lang.get(slug) or {})
            other["region"] = dict(reg)
            restaurants_lang[slug] = other
        tagged += 1

    return tagged, untagged, failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill shop region taxonomy")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and report only; do not write i18n",
    )
    args = parser.parse_args()

    bundle = i18n_store.load_all()
    tagged, untagged, failures = backfill(bundle)

    if not args.dry_run:
        i18n_store.save_all(bundle)
        print(i18n_store.build_bundle())

    print(f"tagged={tagged} untagged={untagged} total={tagged + untagged}")
    for line in failures:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
