# -*- coding: utf-8 -*-
"""Apply ?v=VERSION to local CSS/JS references in all HTML files.

Thin wrapper around tool/lib/cache_bust.py (shared with tool/update-version.py).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tool"))

from lib.cache_bust import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
