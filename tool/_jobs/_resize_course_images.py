# -*- coding: utf-8 -*-
"""Crop-resize every image used by regional curated courses to 1200x800 (3:2).

Does not stretch. Center-crops (and letterbox-crops) then scales with LANCZOS.
Shared files are resized once. End-of-day stops without images are ignored.
"""
from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[2]
TARGET_W, TARGET_H = 1200, 800
QUALITY = 88
COURSE_FILES = [
    ROOT / "data/courses/incheon-curated.js",
    ROOT / "data/courses/gyeonggi-curated.js",
    ROOT / "data/courses/seoul-curated.js",
    ROOT / "data/courses/gangwon-curated.js",
    ROOT / "data/courses/chungcheong-curated.js",
    ROOT / "data/courses/jeolla-curated.js",
    ROOT / "data/courses/gyeongsang-curated.js",
    ROOT / "data/courses/busan-curated.js",
    ROOT / "data/courses/jeju-curated.js",
]


def collect_paths() -> list[Path]:
    seen: set[str] = set()
    out: list[Path] = []
    pat = re.compile(r'(?:cover:|"cover":|image:|"image":)\s*"(\.\./\.\./Images/[^"]+)"')
    for fp in COURSE_FILES:
        text = fp.read_text(encoding="utf-8")
        for rel in pat.findall(text):
            if rel in seen:
                continue
            seen.add(rel)
            path = ROOT / rel.replace("../../", "")
            out.append(path)
    # leftover files in travel-courses that are not currently referenced
    for extra in (ROOT / "Images/travel-courses").rglob("*.jpg"):
        key = "../../" + extra.relative_to(ROOT).as_posix()
        if key in seen:
            continue
        seen.add(key)
        out.append(extra)
    return out


def crop_to_size(im: Image.Image) -> Image.Image:
    im = ImageOps.exif_transpose(im)
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    elif im.mode == "L":
        im = im.convert("RGB")
    src_w, src_h = im.size
    target_ratio = TARGET_W / TARGET_H
    src_ratio = src_w / src_h
    if src_ratio > target_ratio:
        new_w = int(round(src_h * target_ratio))
        left = (src_w - new_w) // 2
        im = im.crop((left, 0, left + new_w, src_h))
    elif src_ratio < target_ratio:
        new_h = int(round(src_w / target_ratio))
        top = (src_h - new_h) // 2
        im = im.crop((0, top, src_w, top + new_h))
    return im.resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)


def main() -> int:
    paths = collect_paths()
    print("unique course images:", len(paths))
    ok = 0
    skip = 0
    missing = 0
    for path in paths:
        if not path.exists():
            print("MISSING", path)
            missing += 1
            continue
        try:
            with Image.open(path) as im:
                w, h = im.size
                if (w, h) == (TARGET_W, TARGET_H) and path.suffix.lower() in {".jpg", ".jpeg"}:
                    skip += 1
                    continue
                out = crop_to_size(im)
        except Exception as e:
            print("SKIP-BAD", path.relative_to(ROOT).as_posix(), e)
            missing += 1
            continue
        out.save(path, format="JPEG", quality=QUALITY, optimize=True, progressive=True)
        print("%s  %dx%d -> %dx%d  %d" % (path.relative_to(ROOT).as_posix(), w, h, TARGET_W, TARGET_H, path.stat().st_size))
        ok += 1
    print("resized", ok, "already", skip, "missing", missing)
    return 0 if missing == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
