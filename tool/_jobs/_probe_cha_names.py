# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET

sys.path.insert(0, ".")
from tool._fill_from_cha import (  # noqa: E402
    LIST_URL,
    fetch_xml,
    image_list,
    search,
    xml_text,
)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    for q in (
        "광주 월봉서원",
        "월봉서원",
        "취가정",
        "이상화생가",
        "이상화 생가",
        "대구 이상화",
        "서상돈",
        "육신사",
        "임실 사선대",
        "사선대",
        "황매산성",
        "세종 독락정",
        "독락정",
        "대구읍성",
        "직지사",
        "장흥 천관산",
    ):
        time.sleep(1.2)
        items = search(q)
        print(f"\nQ {q} n={len(items)}")
        for it in items[:8]:
            print(f"  [{it['cat']}] {it['name']} kd={it['kd']} asno={it['asno']} ct={it['ct']}")
        if q in ("취가정", "광주 월봉서원", "월봉서원") and items:
            it = items[0]
            time.sleep(1.2)
            images = image_list(it["kd"], it["asno"], it["ct"])
            print(f"  images for {it['name']}: {len(images)}")
            for im in images[:8]:
                print(f"    nuri={im['nuri']} desc={im['desc'][:80]!r}")
                print(f"    {im['url']}")


if __name__ == "__main__":
    main()
