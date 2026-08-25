# -*- coding: utf-8 -*-
"""Search Commons and download thumbs for remaining missing course photos."""
from __future__ import annotations

import json
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "Images" / "places" / "_courses"
UA = "KoreaTravelGuidebook/1.0 (educational; thumbnail download; rate-limited)"
CTX = ssl.create_default_context()

QUERIES = {
    "amnam-park.jpg": "Amnam Park Busan",
    "anmyeondo.jpg": "Anmyeondo Taean pine forest",
    "cheorwon-dmz.jpg": "Cheorwon Peace Observatory",
    "daecheon-skybike.jpg": "Daecheon Sky Bike Boryeong",
    "danyang-jando.jpg": "Danyanggang Jando",
    "danyang-market.jpg": "Danyang Gujeong Market",
    "danyang-paragliding.jpg": "Danyang paragliding",
    "dojjaebigol.jpg": "Dojjaebigol Skyvalley Donghae",
    "geoje-pier.jpg": "Geoje Oedo ferry pier",
    "gijang-coast.jpg": "Gijang coast Busan",
    "gongju-museum.jpg": "Gongju National Museum",
    "goseokjeong.jpg": "Goseokjeong Cheorwon",
    "gungnamji.jpg": "Gungnamji Buyeo",
    "jemincheon.jpg": "Jemincheon Gongju",
    "jeolyeong-trail.jpg": "Jeolyeong coastal trail Yeongdo",
    "jeongnimsaji.jpg": "Jeongnimsaji pagoda Buyeo",
    "jeonpo.jpg": "Jeonpo cafe street Busan",
    "mancheonha.jpg": "Mancheonha Skywalk Danyang",
    "metaprovence.jpg": "Metaprovence Damyang",
    "mukho-nongol.jpg": "Mukho Nongol Damgil",
    "muryeong-tomb.jpg": "Tomb of King Muryeong Gongju",
    "osiria.jpg": "Ananti Cove Busan Osiria",
    "sagye-coast.jpg": "Sagye coast Jeju",
    "sehwa-beach.jpg": "Sehwa Beach Jeju",
    "tapdong.jpg": "Tapdong Jeju",
    "uiamho.jpg": "Uiamho Chuncheon",
    "yi-sunsin-square.jpg": "Yi Sun-sin Square Yeosu",
    "yongnuni.jpg": "Yongnuni Oreum Jeju",
    "yulpo-beach.jpg": "Yulpo Beach Boseong",
    "cheonjiyeon.jpg": "Cheonjiyeon Falls Seogwipo",
}


def api(params: dict) -> dict:
    q = urllib.parse.urlencode(params)
    url = "https://commons.wikimedia.org/w/api.php?" + q
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def search_file(query: str) -> tuple[str, str] | None:
    data = api(
        {
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrsearch": query,
            "gsrnamespace": "6",
            "gsrlimit": "8",
            "prop": "imageinfo",
            "iiprop": "url|mime|size",
            "iiurlwidth": "1600",
        }
    )
    pages = (data.get("query") or {}).get("pages") or {}
    skip = ("map", "diagram", "svg", "logo", "icon", "flag", "coat of", "location")
    for page in pages.values():
        title = (page.get("title") or "").lower()
        infos = page.get("imageinfo") or []
        if not infos:
            continue
        info = infos[0]
        mime = (info.get("mime") or "").lower()
        if "jpeg" not in mime and "jpg" not in mime and "png" not in mime:
            continue
        if any(s in title for s in skip):
            continue
        thumb = info.get("thumburl") or info.get("url")
        if thumb:
            return page.get("title") or "", thumb
    return None


def download(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, context=CTX, timeout=60) as r:
        dest.write_bytes(r.read())


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    for name, query in QUERIES.items():
        dest = DEST / name
        if dest.exists() and dest.stat().st_size > 1000:
            print("skip", name)
            continue
        print("search", name, query)
        try:
            hit = search_file(query)
        except Exception as e:
            print("  ERR", e)
            time.sleep(4)
            continue
        if not hit:
            print("  none")
            time.sleep(3)
            continue
        title, url = hit
        try:
            download(url, dest)
            print("  +", name, "<-", title, dest.stat().st_size)
        except Exception as e:
            print("  dl", e)
            if dest.exists():
                dest.unlink()
        time.sleep(3.5)


if __name__ == "__main__":
    main()
