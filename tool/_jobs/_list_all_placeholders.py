# -*- coding: utf-8 -*-
from __future__ import annotations

import hashlib
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COORDS = ROOT / "data" / "places" / "places-coords.js"
IMG = ROOT / "Images" / "places"


def sha1(p: Path) -> str:
    h = hashlib.sha1()
    h.update(p.read_bytes())
    return h.hexdigest()


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    text = COORDS.read_text(encoding="utf-8")
    type_hashes = {}
    for name in (
        "nature",
        "heritage",
        "port",
        "city",
        "mountain",
        "beach",
        "lake",
        "airport",
        "info",
        "locker",
        "bus-terminal",
        "market",
    ):
        f = IMG / "_types" / f"{name}.jpg"
        if f.exists():
            type_hashes[sha1(f)] = name

    recs = re.findall(
        r'slug:\s*"([^"]+)".*?type:\s*"([^"]+)".*?note:\s*"([^"]*)"',
        text,
        re.S,
    )
    ok = Counter()
    ph = Counter()
    missing = Counter()
    ph_rows = []
    miss_rows = []
    for slug, typ, note in recs:
        path = None
        for ext in (".jpg", ".png", ".webp"):
            cand = IMG / f"{slug}{ext}"
            if cand.exists():
                path = cand
                break
        if path is None:
            missing[typ] += 1
            miss_rows.append((slug, typ, note))
            continue
        digest = sha1(path)
        if digest in type_hashes:
            ph[typ] += 1
            ph_rows.append((slug, typ, note, type_hashes[digest]))
        else:
            ok[typ] += 1

    print("OK by type", dict(ok), "total", sum(ok.values()))
    print("PLACEHOLDER by type", dict(ph), "total", sum(ph.values()))
    print("MISSING by type", dict(missing), "total", sum(missing.values()))
    print("total recs", len(recs))
    print("--- MISSING ---")
    for row in miss_rows:
        print(f"  {row[1]}\t{row[0]}\t{row[2]}")
    print("--- PLACEHOLDER slugs ---")
    for row in ph_rows:
        print(f"  {row[1]}={row[3]}\t{row[0]}\t{row[2]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
