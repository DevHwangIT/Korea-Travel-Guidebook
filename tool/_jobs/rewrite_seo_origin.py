# -*- coding: utf-8 -*-
"""Replace legacy GitHub Pages SEO origin with custom domain in known public files.

Usage:
  python tool/rewrite_seo_origin.py
"""
from __future__ import annotations

import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from lib.paths import ROOT  # noqa: E402

OLD = "https://devhwangit.github.io/Korea-Travel-Guidebook"
NEW = "https://korea-guidebook.cloud"

# Explicit list: hub HTML + template + README (docs). sitemap regenerated separately.
TARGETS = [
    "index.html",
    "templates/page-template.html",
    "pages/apps/index.html",
    "pages/before-trip/index.html",
    "pages/buy/index.html",
    "pages/convenience-store/index.html",
    "pages/emergency/index.html",
    "pages/festivals/index.html",
    "pages/food-life/index.html",
    "pages/foods/index.html",
    "pages/prep/index.html",
    "pages/transportation/index.html",
    "pages/travel-tips/index.html",
]


def main() -> int:
    n = 0
    for rel in TARGETS:
        path = ROOT / rel
        if not path.is_file():
            print(f"skip missing: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        if OLD not in text:
            print(f"unchanged: {rel}")
            continue
        path.write_text(text.replace(OLD, NEW), encoding="utf-8")
        n += 1
        print(f"updated: {rel}")
    print(f"Updated {n} files → {NEW}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
