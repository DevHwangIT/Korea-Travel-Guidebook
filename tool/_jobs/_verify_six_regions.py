# -*- coding: utf-8 -*-
import json
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
html = urllib.request.urlopen(
    "http://127.0.0.1:8766/pages/travel-courses/index.html", timeout=10
).read().decode("utf-8", "replace")
needles = [
    "gangwon-curated.js",
    "chungcheong-curated.js",
    "jeolla-curated.js",
    "gyeongsang-curated.js",
    "busan-curated.js",
    "jeju-curated.js",
    "data-courseRegion-tab=\"gangwon\"",
    "data-region-curated=\"jeju\"",
    "20260825201439",
]
for n in needles:
    print("OK" if n in html else "MISS", n)

samples = [
    "Images/places/mountain/seoraksan.jpg",
    "Images/places/_courses/daecheon-skybike.jpg",
    "Images/places/food-bibimbap-jeonju.jpg",
    "Images/places/beach/haeundae.jpg",
    "Images/places/nature/seongsan.jpg",
    "Images/places/_courses/cheonjiyeon.jpg",
]
for s in samples:
    im = Image.open(ROOT / s)
    print(Path(s).name, im.size, "ratio", round(im.size[0] / im.size[1], 3))

d = json.loads((ROOT / "i18n/pages/travel-courses/ko.json").read_text(encoding="utf-8"))
print("hallasan notice", bool(d["travelCourses"]["curated"]["jeju"]["courses"]["c07"].get("notice")))
print("oedo notice", bool(d["travelCourses"]["curated"]["gyeongsang"]["courses"]["c04"].get("notice")))
print("gangwon featured", d["travelCourses"]["curated"]["gangwon"].get("featuredLabel"))
print("chungcheong featured", d["travelCourses"]["curated"]["chungcheong"].get("featuredLabel"))
