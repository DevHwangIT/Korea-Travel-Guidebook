# -*- coding: utf-8 -*-
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ko = json.loads((ROOT / "i18n/pages/travel-courses/ko.json").read_text(encoding="utf-8"))
cur = ko["travelCourses"]["curated"]
pat_id = re.compile(r'id:\s*"c(\d+)"')
pat_stop = re.compile(r"\{ time:")

for region in ["gangwon", "chungcheong", "jeolla", "gyeongsang", "busan", "jeju"]:
    js = (ROOT / f"data/courses/{region}-curated.js").read_text(encoding="utf-8")
    # split courses by id
    parts = re.split(r"\n  \{\n    id:", js)
    courses_js = {}
    for m in re.finditer(
        r'id:\s*"(c\d+)"[\s\S]*?stops:\s*\[([\s\S]*?)\]\s*\n  \}', js
    ):
        cid = m.group(1)
        n = len(re.findall(r"\{ time:", m.group(2)))
        courses_js[cid] = n
    i18n_c = cur[region]["courses"]
    print("==", region)
    for cid, n in courses_js.items():
        ni = len(i18n_c.get(cid, {}).get("stops", []))
        mark = "OK" if n == ni else "MISMATCH"
        print(f"  {cid} js={n} i18n={ni} {mark}")
        if cid not in i18n_c:
            print("   missing i18n")
