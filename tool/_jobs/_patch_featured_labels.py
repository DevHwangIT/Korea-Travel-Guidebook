# -*- coding: utf-8 -*-
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _i18n_six_lib import FEATURED, LANGS, ROOT

for lang in LANGS:
    p = ROOT / f"i18n/pages/travel-courses/{lang}.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    curated = data["travelCourses"]["curated"]
    feat, more = FEATURED[lang]
    for rid in ("gangwon", "chungcheong"):
        curated[rid]["featuredLabel"] = feat
        curated[rid]["moreLabel"] = more
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("patched", lang)
