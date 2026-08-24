# -*- coding: utf-8 -*-
"""One-shot migration: split i18n/{lang}.json into common/ + pages/ groups.

Usage (from repo root):
  python tool/migrate_i18n_split.py
  python tool/migrate_i18n_split.py --dry-run

Reads each i18n/{lang}.json, writes owner files per KEY_OWNERS, then runs
build-bundle.py and verifies leaf-key counts match.
Does NOT delete content — residual assembled files are refreshed by the build.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parent
I18N_DIR = ROOT / "i18n"

sys.path.insert(0, str(I18N_DIR))
sys.path.insert(0, str(TOOL_DIR))

from locale_routing import (  # noqa: E402
    KEY_OWNERS,
    LANGS,
    count_leaf_keys,
    load_merged_lang,
    owner_for_key,
    split_by_owner,
    write_json,
    write_sources_for_lang,
)


def _read_residual(lang: str) -> dict:
    path = I18N_DIR / f"{lang}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Split central i18n JSON into common + pages")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned owners only; do not write files",
    )
    args = parser.parse_args()

    # Snapshot leaf counts from residual before split
    before: dict[str, int] = {}
    for lang in LANGS:
        data = _read_residual(lang)
        before[lang] = count_leaf_keys(data)
        unknown = [k for k in data if k not in KEY_OWNERS]
        print(f"[{lang}] top-level={len(data)} leaves={before[lang]}")
        if unknown:
            print(f"  → unmapped keys → {owner_for_key(unknown[0])}: {unknown}")

        buckets = split_by_owner(data)
        for owner, partial in sorted(buckets.items()):
            print(f"  {owner}: {list(partial.keys())}")

        if args.dry_run:
            continue

        written = write_sources_for_lang(lang, data)
        print(f"  wrote {len(written)} source files")

    if args.dry_run:
        print("dry-run complete (no files written)")
        return 0

    # Rebuild assembled residual + messages.js
    from lib import i18n_store  # noqa: E402

    print(i18n_store.build_bundle())

    # Verify
    ok = True
    for lang in LANGS:
        merged = load_merged_lang(lang)
        after = count_leaf_keys(merged)
        residual = _read_residual(lang)
        residual_leaves = count_leaf_keys(residual)
        has_panax = (
            isinstance(merged.get("restaurants"), dict)
            and "panax" in merged["restaurants"]
        )
        has_home = "home" in merged
        status = "OK" if after == before[lang] else "MISMATCH"
        if after != before[lang] or residual_leaves != before[lang]:
            ok = False
        print(
            f"verify [{lang}] before={before[lang]} merged={after} "
            f"residual={residual_leaves} home={has_home} restaurants.panax={has_panax} {status}"
        )

    # Smoke via i18n_store.load_all
    bundle = i18n_store.load_all()
    ko = bundle["ko"]
    smoke_panax = "panax" in (ko.get("restaurants") or {})
    smoke_home = "home" in ko
    print(f"smoke load_all: restaurants.panax={smoke_panax} home={smoke_home}")
    if not smoke_panax or not smoke_home:
        ok = False

    if not ok:
        print("VERIFICATION FAILED", file=sys.stderr)
        return 1
    print("split + verify OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
