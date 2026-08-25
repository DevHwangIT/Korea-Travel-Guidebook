# -*- coding: utf-8 -*-
import json
import pathlib
import re

root = pathlib.Path(__file__).resolve().parents[2]
js = (root / "data/courses/gyeonggi-curated.js").read_text(encoding="utf-8")
ids = re.findall(r'id:\s*"(c\d+)"', js)
parts = re.split(r"\{\s*id:", js)[1:]
stop_counts = {}
print("courses in js", len(ids), ids)
for p, cid in zip(parts, ids):
    n = len(re.findall(r"time:", p.split("]")[0] if "]" in p else p))
    stop_counts[cid] = n
    print(cid, "stops", n)

langs = ["ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru"]
ok = True
for lang in langs:
    data = json.loads(
        (root / "i18n/pages/travel-courses" / f"{lang}.json").read_text(
            encoding="utf-8"
        )
    )
    gg = data["travelCourses"]["curated"]["gyeonggi"]["courses"]
    for cid, n in stop_counts.items():
        c = gg.get(cid)
        if not c:
            print("MISSING", lang, cid)
            ok = False
            continue
        st = c.get("stops") or []
        if len(st) != n:
            print("STOP MISMATCH", lang, cid, "i18n", len(st), "js", n)
            ok = False
        for i, s in enumerate(st):
            if not s.get("name") or not s.get("desc"):
                print("EMPTY STOP", lang, cid, i, s)
                ok = False
        for k in ("title", "summary", "route", "tips"):
            if not c.get(k):
                print("EMPTY FIELD", lang, cid, k)
                ok = False
    if not gg.get("c05", {}).get("notice"):
        print("MISSING NOTICE", lang)
        ok = False
print("OK" if ok else "ISSUES")
