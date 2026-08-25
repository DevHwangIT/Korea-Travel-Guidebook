# -*- coding: utf-8 -*-
"""Search Wikimedia Commons and save missing south-course stills."""
from __future__ import annotations

import json
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COURSES = ROOT / "Images" / "places" / "_courses"
UA = "KoreaTravelGuidebook/1.0 (educational travel guide)"
CTX = ssl._create_unverified_context()

MISSING = {
    "muryeong-tomb.jpg": "Songsan-ri tombs Gongju",
    "gongju-museum.jpg": "Gongju National Museum",
    "jemincheon.jpg": "Gongju Jemincheon",
    "gungnamji.jpg": "Gungnamji Buyeo",
    "jeongnimsaji.jpg": "Jeongnimsa pagoda Buyeo",
    "mancheonha.jpg": "Mancheonha Skywalk Danyang",
    "danyang-jando.jpg": "Danyanggang Jando",
    "danyang-paragliding.jpg": "Danyang paragliding",
    "danyang-market.jpg": "Danyang market",
    "daecheon-skybike.jpg": "Daecheon Beach",
    "anmyeondo.jpg": "Anmyeondo Taean",
    "daejeon-science-museum.jpg": "National Science Museum Korea Daejeon",
    "daejeon-oldtown.jpg": "Daejeon downtown",
    "yi-sunsin-square.jpg": "Yi Sun-sin Square Yeosu",
    "metaprovence.jpg": "Metaprovence Damyang",
    "yulpo-beach.jpg": "Yulpo Beach Boseong",
    "mokpo-peace-plaza.jpg": "Mokpo Gatbawi",
    "byeongsan-seowon.jpg": "Byeongsan Seowon",
    "geoje-pier.jpg": "Geoje ferry terminal Haegeumgang",
    "windy-hill.jpg": "Windy Hill Geoje",
    "amnam-park.jpg": "Amnam Park Busan",
    "gijang-coast.jpg": "Gijang coastline Korea",
    "osiria.jpg": "Ananti Cove Busan",
    "jeolyeong-trail.jpg": "Jeolyeong coastal trail Yeongdo",
    "jeonpo.jpg": "Jeonpo cafe street Busan",
    "jeonpo-shops.jpg": "Jeonpo Dong Busan",
    "tapdong.jpg": "Tapdong Jeju waterfront",
    "yongnuni.jpg": "Yongnuni Oreum",
    "sehwa-beach.jpg": "Sehwa Beach Jeju",
    "sagye-coast.jpg": "Sagye Beach Jeju",
}

# Do not use wrong-place photos for osiria/jeonpo/tapdong — search first.


def api(params: dict) -> dict:
    q = urllib.parse.urlencode(params)
    url = "https://commons.wikimedia.org/w/api.php?" + q
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40, context=CTX) as r:
        return json.loads(r.read().decode("utf-8"))


def search_title(query: str) -> str | None:
    data = api({
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srnamespace": "6",
        "srlimit": "8",
        "format": "json",
    })
    hits = data.get("query", {}).get("search", [])
    for h in hits:
        title = h.get("title", "")
        if title.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            return title
        if title.startswith("File:"):
            return title
    return hits[0]["title"] if hits else None


def download_file(file_title: str, dest: Path) -> bool:
    if not file_title.startswith("File:"):
        file_title = "File:" + file_title
    data = api({
        "action": "query",
        "titles": file_title,
        "prop": "imageinfo",
        "iiprop": "url",
        "iiurlwidth": "1280",
        "format": "json",
    })
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        info = (page.get("imageinfo") or [{}])[0]
        url = info.get("thumburl") or info.get("url")
        if not url:
            continue
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=45, context=CTX) as r:
            blob = r.read()
        if len(blob) < 8000:
            return False
        dest.write_bytes(blob)
        return True
    return False


def main() -> None:
    COURSES.mkdir(parents=True, exist_ok=True)
    for name, query in MISSING.items():
        dest = COURSES / name
        if dest.exists() and dest.stat().st_size > 8000:
            continue
        print("search", name, query)
        try:
            title = search_title(query)
        except Exception as e:
            print("  search err", e)
            continue
        if not title:
            print("  no hit")
            continue
        print("  hit", title)
        time.sleep(0.4)
        try:
            ok = download_file(title, dest)
        except Exception as e:
            print("  dl err", e)
            continue
        print("  OK" if ok else "  dl fail", dest.stat().st_size if dest.exists() else 0)
        time.sleep(0.3)


if __name__ == "__main__":
    main()
