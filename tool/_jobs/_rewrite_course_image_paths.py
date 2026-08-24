# -*- coding: utf-8 -*-
"""Rewrite hardcoded place image paths to Images/places/{type}/{slug}.jpg
and remove leftover root copies. Does not change food-/quiz- shared files.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COORDS = ROOT / "data" / "places" / "places-coords.js"
IMG = ROOT / "Images" / "places"
FILES = [
    ROOT / "data" / "courses" / "seoul-curated.js",
    ROOT / "js" / "course-recommend.js",
]
KEEP_PREFIXES = ("food-", "quiz-")


def sha1(path: Path) -> str:
    h = hashlib.sha1()
    h.update(path.read_bytes())
    return h.hexdigest()


def slug_types() -> dict[str, str]:
    text = COORDS.read_text(encoding="utf-8")
    return dict(re.findall(r'slug:\s*"([^"]+)".*?type:\s*"([^"]+)"', text, re.S))


def find_typed(slug: str) -> str | None:
    for folder in IMG.iterdir():
        if not folder.is_dir() or folder.name in {"_types", "_tmp"}:
            continue
        for ext in (".jpg", ".png", ".webp"):
            if (folder / f"{slug}{ext}").exists():
                return f"Images/places/{folder.name}/{slug}{ext}"
    return None


def rewrite_file(path: Path, types: dict[str, str]) -> int:
    text = path.read_text(encoding="utf-8")
    n = 0

    def repl(m: re.Match[str]) -> str:
        nonlocal n
        dots = m.group(1)
        slug = m.group(2)
        ext = m.group(3)
        if slug.startswith(KEEP_PREFIXES):
            return m.group(0)
        typed = find_typed(slug)
        if not typed:
            kind = types.get(slug)
            if kind:
                cand = IMG / kind / f"{slug}.{ext}"
                if cand.exists():
                    typed = f"Images/places/{kind}/{slug}.{ext}"
        if not typed:
            return m.group(0)
        n += 1
        return f"{dots}{typed}"

    text2 = re.sub(
        r'((?:\.\./)*)Images/places/([a-z0-9-]+)\.(jpg|png|webp)',
        repl,
        text,
    )
    if n:
        path.write_text(text2, encoding="utf-8")
    return n


def cleanup_root(types: dict[str, str]) -> tuple[int, int]:
    type_hashes = {}
    tdir = IMG / "_types"
    if tdir.exists():
        for f in tdir.glob("*.jpg"):
            type_hashes[sha1(f)] = f.stem
    removed = 0
    leftover = 0
    for f in list(IMG.glob("*.jpg")) + list(IMG.glob("*.png")) + list(IMG.glob("*.webp")):
        if f.name.startswith(KEEP_PREFIXES):
            continue
        slug = f.stem
        typed = find_typed(slug)
        if typed:
            f.unlink()
            removed += 1
            continue
        if sha1(f) in type_hashes:
            f.unlink()
            removed += 1
            continue
        leftover += 1
        print(f"ROOT leftover {f.name}", flush=True)
    return removed, leftover


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    types = slug_types()
    total = 0
    for path in FILES:
        n = rewrite_file(path, types)
        print(f"rewrite {path.relative_to(ROOT).as_posix()} {n}", flush=True)
        total += n
    removed, leftover = cleanup_root(types)
    print(f"DONE path_rewrites={total} root_removed={removed} root_leftover={leftover}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
