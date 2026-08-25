# -*- coding: utf-8 -*-
"""Copy generated assets into Images/places/_courses and duplicate same-place files."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "Images" / "places" / "_courses"
ASSETS = Path(r"C:\Users\HwangInTae\.cursor\projects\c-Users-HwangInTae-Desktop-guide-book-Korea-Travel-Guidebook\assets")

NAMES = [
    "muryeong-tomb.jpg",
    "jemincheon.jpg",
    "gungnamji.jpg",
    "mancheonha.jpg",
    "danyang-jando.jpg",
    "danyang-paragliding.jpg",
    "danyang-market.jpg",
    "yi-sunsin-square.jpg",
    "metaprovence.jpg",
    "yulpo-beach.jpg",
    "geoje-pier.jpg",
    "amnam-park.jpg",
    "osiria.jpg",
    "jeolyeong-trail.jpg",
    "jeonpo.jpg",
    "tapdong.jpg",
]

DUP = {
    "yulpo-walk.jpg": "yulpo-beach.jpg",
    "jeonpo-shops.jpg": "jeonpo.jpg",
}


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    for name in NAMES:
        src = ASSETS / name
        if not src.exists():
            print("MISSING ASSET", src)
            continue
        shutil.copy2(src, DEST / name)
        print("copied", name, src.stat().st_size)
    for dest_name, src_name in DUP.items():
        src = DEST / src_name
        if src.exists() and src.stat().st_size > 8000:
            shutil.copy2(src, DEST / dest_name)
            print("dup", dest_name)


if __name__ == "__main__":
    main()
