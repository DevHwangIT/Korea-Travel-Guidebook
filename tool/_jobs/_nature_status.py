# -*- coding: utf-8 -*-
"""Status of nature place images vs nature.jpg fallback."""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "Images" / "places"
FB = IMG / "_types" / "nature.jpg"
COORDS = ROOT / "data" / "places" / "places-coords.js"


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    fb = hashlib.md5(FB.read_bytes()).hexdigest()
    ok: list[str] = []
    fb_list: list[str] = []
    miss: list[str] = []
    for line in COORDS.read_text(encoding="utf-8").splitlines():
        if 'type: "nature"' not in line:
            continue
        m = re.search(r'slug:\s*"([^"]+)"', line)
        if not m:
            continue
        slug = m.group(1)
        p = IMG / f"{slug}.jpg"
        if not p.exists():
            miss.append(slug)
            print(f"MISSING {slug}")
            continue
        h = hashlib.md5(p.read_bytes()).hexdigest()
        if h == fb:
            fb_list.append(slug)
            print(f"FALLBACK {slug}")
        else:
            ok.append(slug)
            print(f"OK {slug} {p.stat().st_size}")
    print(f"\nok={len(ok)} fallback={len(fb_list)} missing={len(miss)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
