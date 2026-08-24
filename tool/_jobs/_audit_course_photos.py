# -*- coding: utf-8 -*-
from pathlib import Path
from PIL import Image
import hashlib
import re

root = Path(__file__).resolve().parents[1]
js = (root / "data/courses/seoul-curated.js").read_text(encoding="utf-8")
imgs = sorted(set(re.findall(r"Images/places/([^\"']+)", js)))
types = root / "Images/places/_types"
ph_hashes = {}
if types.exists():
    for p in types.glob("*"):
        if p.is_file():
            ph_hashes[hashlib.md5(p.read_bytes()).hexdigest()] = p.name

print("=== ALL COURSE IMAGES ===")
for name in imgs:
    p = root / "Images/places" / name
    if not p.exists():
        print(f"{name} MISSING")
        continue
    data = p.read_bytes()
    md5 = hashlib.md5(data).hexdigest()
    flag = []
    if md5 in ph_hashes:
        flag.append("PLACEHOLDER:" + ph_hashes[md5])
    head = data[:80].lstrip()
    if head.startswith(b"<!") or b"<html" in data[:200].lower():
        print(f"{name} HTML {len(data)}b !! HTML")
        continue
    try:
        im = Image.open(p)
        w, h = im.size
        ratio = round(w / h, 3) if h else 0
        kind = im.format
        if kind == "PNG":
            flag.append("PNG")
        if ratio > 2.4:
            flag.append("PANORAMA")
        if ratio < 0.7:
            flag.append("TALL")
        if w < 400 or h < 400:
            flag.append("SMALL")
        if w <= 2 and h <= 2:
            flag.append("1x1")
        if len(data) < 8000:
            flag.append("TINYFILE")
        mark = " !! " + ",".join(flag) if flag else ""
        print(f"{name} {w}x{h} r={ratio} {kind} {len(data)}b{mark}")
    except Exception as e:
        print(f"{name} ERR {e} {len(data)}b")
print("COUNT", len(imgs))
