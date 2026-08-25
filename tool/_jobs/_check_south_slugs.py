# -*- coding: utf-8 -*-
from pathlib import Path
import re, json

ROOT = Path(__file__).resolve().parents[2]
coords_js = (ROOT / "js/seoul-curated-courses.js").read_text(encoding="utf-8")
m = re.search(r"SLUG_COORDS\s*=\s*\{([\s\S]*?)\n\s*\};", coords_js)
slugs = set(re.findall(r'"([^"]+)":\s*\[', m.group(1)))
places = (ROOT / "data/places/places-coords.js").read_text(encoding="utf-8")
places_slugs = set(re.findall(r'slug:\s*"([^"]+)"', places))
alias_m = re.search(r"SLUG_ALIAS\s*=\s*\{([\s\S]*?)\n\s*\};", coords_js)
aliases = set(re.findall(r'"([^"]+)":', alias_m.group(1))) if alias_m else set()

missing = []
for fp in (ROOT / "data/courses").glob("*-curated.js"):
    if not any(fp.name.startswith(p) for p in ("chungcheong", "jeolla", "gyeongsang", "busan", "jeju")):
        continue
    for place in re.findall(r'place:\s*"([^"]+)"', fp.read_text(encoding="utf-8")):
        if place in slugs or place in places_slugs or place in aliases:
            continue
        missing.append(f"{fp.name} {place}")
print("unresolved", len(missing))
for row in missing:
    print(" ", row)
