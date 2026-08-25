# -*- coding: utf-8 -*-
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
pat = re.compile(r'"(\.\./\.\./Images/[^"]+)"')
missing = []
ok = 0
for fp in sorted((ROOT / "data/courses").glob("*-curated.js")):
    if fp.name in {"seoul-curated.js", "incheon-curated.js", "gyeonggi-curated.js"}:
        continue
    for rel in pat.findall(fp.read_text(encoding="utf-8")):
        p = ROOT / rel.replace("../../", "")
        if p.exists():
            ok += 1
        else:
            missing.append(str(p.relative_to(ROOT)).replace("\\", "/"))
print("ok", ok, "missing", len(missing))
for m in missing:
    print(m)
