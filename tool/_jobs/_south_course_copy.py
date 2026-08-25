# -*- coding: utf-8 -*-
"""Load south-region course copy from i18n JSON so inject cannot wipe edited strings."""
from __future__ import annotations

import json
from pathlib import Path

LANGS = ["ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru"]
REGIONS = ["chungcheong", "jeolla", "gyeongsang", "busan", "jeju"]
I18N = Path(__file__).resolve().parents[2] / "i18n" / "pages" / "travel-courses"

COURSES: dict = {region: {} for region in REGIONS}
for lang in LANGS:
    data = json.loads((I18N / f"{lang}.json").read_text(encoding="utf-8"))
    curated = data["travelCourses"]["curated"]
    for region in REGIONS:
        courses = curated[region]["courses"]
        for cid, item in courses.items():
            COURSES[region].setdefault(cid, {})[lang] = item
