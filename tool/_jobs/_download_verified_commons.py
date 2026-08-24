# -*- coding: utf-8 -*-
"""Download only Commons files whose file page already names the place."""
from __future__ import annotations

import importlib.util
import sys
import time
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "fill_ph", ROOT / "tool" / "_fill_placeholder_photos.py"
)
fill = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fill)

# slug -> Commons File title. Only pages we opened and confirmed.
FILES: dict[str, str] = {
    "soyang-lake": "20241108 HPGkiji 소양호.jpg",
    "soyang-lake-inje": "20241108 HPGkiji 소양호.jpg",
    "yeongsan-lake": "Yeongsanho.jpg",
    "seonyudo-beach": "군산시 선유도(AMJ).jpg",
    "byeonsan-beach": "A Buan Beach - panoramio.jpg",
    "seoknalsa": "울주 석남사 삼층석탑.jpg",
    "ulsan-seoknalsa": "울주 석남사 삼층석탑.jpg",
    "kkotji-beach": "꽃지해변.jpg",
    "iho-tewoo-beach": "Ihoteu beach1.jpg",
}


def filepath(name: str) -> str:
    return (
        "https://commons.wikimedia.org/wiki/Special:FilePath/"
        + urllib.parse.quote(name)
        + "?width=800"
    )


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    hashes = fill.type_hashes()
    ok = 0
    for slug, name in FILES.items():
        dest = fill.dest_path(slug)
        print(f"{slug} <- {name}", flush=True)
        time.sleep(2.4)
        if fill.try_save(filepath(name), dest, hashes, f"ok:{name}"):
            ok += 1
        else:
            print("  fail")
    print(f"DONE ok={ok}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
