# -*- coding: utf-8 -*-
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
files = [
    ROOT / "data/courses/chungcheong-curated.js",
    ROOT / "data/courses/jeolla-curated.js",
    ROOT / "data/courses/gyeongsang-curated.js",
    ROOT / "data/courses/busan-curated.js",
    ROOT / "data/courses/jeju-curated.js",
]
pat = re.compile(r'(?:cover:|image:)\s*"(\.\./\.\./Images/[^"]+)"')
seen = set()
missing = []
for fp in files:
    for rel in pat.findall(fp.read_text(encoding="utf-8")):
        if rel in seen:
            continue
        seen.add(rel)
        p = ROOT / rel.replace("../../", "")
        if not p.exists() or p.stat().st_size < 8000:
            missing.append((p.relative_to(ROOT).as_posix(), p.stat().st_size if p.exists() else 0))
print("missing", len(missing))
for rel, size in missing:
    print(f"  {rel} {size}")
