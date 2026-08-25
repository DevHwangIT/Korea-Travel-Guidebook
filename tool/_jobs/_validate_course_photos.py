# -*- coding: utf-8 -*-
import re
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parents[2]
js = (root / "js/seoul-curated-courses.js").read_text(encoding="utf-8")
coords = set(re.findall(r'"([^"]+)": \[', js.split("var SLUG_ALIAS")[0]))
for name in ["incheon-curated.js", "gyeonggi-curated.js"]:
    text = (root / "data/courses" / name).read_text(encoding="utf-8")
    places = re.findall(r'place: "([^"]+)"', text)
    imgs = re.findall(r'image: "([^"]+)"', text)
    print("===", name, "===")
    missing = [p for p in places if p not in coords]
    print("missing coords:", missing or "none")
    dups = [k for k, v in Counter(imgs).items() if v > 1]
    print("dup images in file:", dups or "none")
    for p in imgs:
        rel = p.replace("../../", "")
        if not (root / rel).exists():
            print(" MISSING FILE", rel)
    print("stops with place", len(places), "images", len(imgs))
