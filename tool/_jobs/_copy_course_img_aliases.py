# -*- coding: utf-8 -*-
"""Copy existing course photos onto the filenames referenced by new region JS."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
C = ROOT / "Images" / "places" / "_courses"
P = ROOT / "Images" / "places"

# dest filename (as used in JS) <- source path that already exists
COPIES: list[tuple[str, Path]] = [
    ("mokpo-cablecar.jpg", C / "mokpo-cable.jpg"),
    ("saeyeon-bridge.jpg", C / "saeyeongyo.jpg"),
    ("space-walk.jpg", C / "spacewalk.jpg"),
    ("yeosu-cablecar.jpg", C / "yeosu-cable.jpg"),
    ("tongyeong-park.jpg", C / "yi-sun-sin-park.jpg"),
    ("suncheon-yongsan.jpg", C / "yongsan-observatory.jpg"),
    ("woljeongsa-fir.jpg", C / "woljeongsa.jpg"),
    ("apsan-night.jpg", C / "apsan.jpg"),
    ("oedo-botania.jpg", C / "oeodo-botania.jpg"),
]

# extra copies if dest missing
OPTIONAL = [
    ("muryeong-tomb.jpg", C / "muryeong-tombs.jpg"),
    ("gijang-sunset.jpg", P / "heritage" / "haedong.jpg"),  # nearby coast, last resort only if no gijang-coast
]


def copy_if(dest_name: str, src: Path) -> None:
    dest = C / dest_name
    if dest.exists() and dest.stat().st_size > 1000:
        print("skip exists", dest_name)
        return
    if not src.exists():
        print("NO SRC", dest_name, "<-", src)
        return
    shutil.copy2(src, dest)
    print("copied", dest_name, "<-", src.name, src.stat().st_size)


def main() -> None:
    for dest, src in COPIES:
        copy_if(dest, src)
    for dest, src in OPTIONAL:
        copy_if(dest, src)


if __name__ == "__main__":
    main()
