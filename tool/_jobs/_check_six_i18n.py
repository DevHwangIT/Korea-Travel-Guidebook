# -*- coding: utf-8 -*-
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LANGS = ["ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru"]
REGIONS = {
    "gangwon": 7,
    "chungcheong": 6,
    "jeolla": 6,
    "gyeongsang": 9,
    "busan": 6,
    "jeju": 10,
}

def main() -> None:
    for lang in LANGS:
        p = ROOT / f"i18n/pages/travel-courses/{lang}.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        curated = (((data.get("travelCourses") or {}).get("curated")) or {})
        for rid, n in REGIONS.items():
            block = curated.get(rid) or {}
            courses = block.get("courses") or {}
            missing = [f"c{str(i).zfill(2)}" for i in range(1, n + 1) if f"c{str(i).zfill(2)}" not in courses]
            if missing:
                print(lang, rid, "MISSING", missing)
            else:
                # check each course has title/stops
                bad = []
                for cid, c in courses.items():
                    if not c.get("title") or not c.get("stops"):
                        bad.append(cid)
                extra = [k for k in courses if k.startswith("c") and k not in [f"c{str(i).zfill(2)}" for i in range(1, n+1)]]
                print(lang, rid, "ok", len(courses), "bad", bad, "extra", extra)
        # region chrome
        for key in ("regionGangwon", "regionChungcheong", "regionJeolla", "regionGyeongsang", "regionBusan", "regionJeju"):
            if key not in (data.get("travelCourses") or {}):
                print(lang, "missing chrome", key)

if __name__ == "__main__":
    main()
