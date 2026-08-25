# -*- coding: utf-8 -*-
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
files = [
    "data/courses/gangwon-curated.js",
    "data/courses/chungcheong-curated.js",
    "data/courses/jeolla-curated.js",
    "data/courses/gyeongsang-curated.js",
    "data/courses/busan-curated.js",
    "data/courses/jeju-curated.js",
]
pat = re.compile(r'(?:cover:|image:)\s*"(\.\./\.\./Images/[^"]+)"')
missing = set()
ok = set()
for fp in files:
    text = (ROOT / fp).read_text(encoding="utf-8")
    for rel in pat.findall(text):
        path = ROOT / rel.replace("../../", "")
        if path.exists():
            ok.add(str(path.as_posix()))
        else:
            missing.add(str(path.as_posix()))
print("OK unique", len(ok))
print("MISSING unique", len(missing))
for m in sorted(missing):
    print(m)
