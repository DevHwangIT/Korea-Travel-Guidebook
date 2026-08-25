# -*- coding: utf-8 -*-
"""HTTP check: course page + a sample of south-region images."""
from __future__ import annotations

import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = "http://127.0.0.1:8766"
UA = "KoreaTravelGuidebook/1.0"


def get(url: str) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status, r.read()


def main() -> None:
    status, body = get(BASE + "/pages/travel-courses/?lang=ko")
    text = body.decode("utf-8", "replace")
    print("page", status, "len", len(body))
    for name in ("chungcheong-curated.js", "jeolla-curated.js", "gyeongsang-curated.js", "busan-curated.js", "jeju-curated.js"):
        print("script", name, name in text)
    print("version 20260825200647", "20260825200647" in text)

    samples = [
        "/Images/places/heritage/gotsanseot.jpg",
        "/Images/places/_courses/muryeong-tomb.jpg",
        "/Images/places/_courses/gungnamji.jpg",
        "/Images/places/heritage/jeonju.jpg",
        "/Images/places/_courses/juknokwon.jpg",
        "/Images/places/heritage/bulguksa.jpg",
        "/Images/places/_courses/oedo-botania.jpg",
        "/Images/places/beach/haeundae.jpg",
        "/Images/places/_courses/jeonpo.jpg",
        "/Images/places/nature/seongsan.jpg",
        "/Images/places/_courses/osulloc.jpg",
        "/Images/places/_courses/tapdong.jpg",
        "/Images/places/food-bibimbap-jeonju.jpg",
        "/Images/places/food-blackpork-hallasan.jpg",
    ]
    for rel in samples:
        path = ROOT / rel.lstrip("/")
        st, data = get(BASE + rel)
        print(rel, "http", st, "bytes", len(data), "disk", path.stat().st_size)


if __name__ == "__main__":
    main()
