# -*- coding: utf-8 -*-
"""Copy dessert shop food photos onto shop covers (1400x933)."""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from PIL import Image

JOBS_DIR = Path(__file__).resolve().parent
TOOL_DIR = JOBS_DIR.parent
ROOT = TOOL_DIR.parent
sys.path.insert(0, str(TOOL_DIR))

from lib.cache_bust import iter_html_files, process_html, VERSION_FILE  # noqa: E402
from lib.content import _write_text_retry  # noqa: E402

ASSETS = Path(
    r"C:\Users\HwangInTae\.cursor\projects\c-Users-HwangInTae-Desktop-guide-book-Korea-Travel-Guidebook\assets"
)
COVER_SIZE = (1400, 933)

# (asset filename, kind, dish, shop slug)
JOBS = [
    ("shop-jeokdang.jpg", "desserts", "cafe", "jeokdang"),
    ("shop-arari.jpg", "desserts", "cafe", "arari-bukchon"),
    ("shop-starbucks-coffee.jpg", "desserts", "cafe", "starbucks-daegu-jongno-gotaek"),
    ("shop-starbucks-coffee.jpg", "desserts", "cafe", "starbucks-gyeongju-daereungwon"),
    ("shop-chacha-tea.jpg", "desserts", "cafe", "chacha-tea-club-changsin"),
    ("shop-bean-brothers.jpg", "desserts", "cafe", "bean-brothers-hapjeong"),
    ("shop-bokhodu.jpg", "desserts", "bread", "bokhodu-gyeongbokgung"),
    ("shop-london-bagel.jpg", "desserts", "bread", "london-bagel-museum-dosan"),
    ("shop-butterscotch.jpg", "desserts", "bread", "butterscotch-euljiro"),
    ("shop-donar.jpg", "desserts", "bread", "donar"),
    ("shop-jjoljjol.jpg", "desserts", "hotteok", "jjoljjol-hotteok"),
    ("shop-obok-tteok.jpg", "desserts", "tteok", "obok-tteokjip"),
    ("shop-idorim.jpg", "desserts", "bingsu", "idorim-cafe"),
    ("dish-chapssal-kwabaegi.jpg", "desserts", "chapssal-kwabaegi", "ilhosanghoe-gwangjang"),
]


def fit_cover(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tw, th = COVER_SIZE
    target_ratio = tw / th
    with Image.open(src) as im:
        im = im.convert("RGB")
        w, h = im.size
        ratio = w / h
        if ratio > target_ratio:
            nw = int(h * target_ratio)
            left = (w - nw) // 2
            im = im.crop((left, 0, left + nw, h))
        else:
            nh = int(w / target_ratio)
            top = (h - nh) // 2
            im = im.crop((0, top, w, top + nh))
        im = im.resize(COVER_SIZE, Image.Resampling.LANCZOS)
        im.save(dest, "JPEG", quality=88, optimize=True)
    print(f"cover {dest.relative_to(ROOT)}", flush=True)


def bump() -> None:
    ver = datetime.now().strftime("%Y%m%d%H%M%S")
    text = (
        "/* Single source of truth for static asset cache-busting.\n"
        " * Bump SITE_ASSET_VERSION via tool/update-version.py (or edit here),\n"
        " * then HTML ?v= is applied automatically by that tool / apply-cache-bust.\n"
        " */\n"
        f'window.SITE_ASSET_VERSION = "{ver}";\n'
    )
    _write_text_retry(VERSION_FILE, text)
    print("wrote version", ver, flush=True)
    updated = 0
    skipped = []
    for html_path in iter_html_files(ROOT):
        original = html_path.read_text(encoding="utf-8")
        new_text, n = process_html(original, ver)
        if new_text == original:
            continue
        try:
            _write_text_retry(html_path, new_text)
            updated += 1
        except OSError as exc:
            skipped.append((html_path.name, str(exc)))
    print("updated", updated, "skipped", skipped, flush=True)


def main() -> int:
    missing = []
    for fname, kind, dish, slug in JOBS:
        src = ASSETS / fname
        dest = ROOT / "pages" / "foods" / kind / dish / slug / "media" / "cover.jpg"
        if not src.is_file():
            missing.append(str(src))
            print("MISSING", src, flush=True)
            continue
        fit_cover(src, dest)
    if missing:
        return 1
    bump()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
