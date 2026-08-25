# -*- coding: utf-8 -*-
"""Download Incheon course place photos from Wikimedia Commons."""
from __future__ import annotations

import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMG = ROOT / "Images" / "places" / "_courses"
UA = "KoreaTravelGuidebook/1.0 (incheon course covers; educational; rate-limited)"

FILES = {
    "jayu-park": [
        "Jayu Park Incheon.jpg",
        "Freedom Park Incheon.jpg",
        "Incheon Jayu Park.jpg",
        "자유공원 인천.jpg",
        "Jayu Park.jpg",
    ],
    "wolmido-night": [
        "Wolmido Ferris Wheel.jpg",
        "Wolmi Theme Park.jpg",
        "Wolmido Incheon.jpg",
        "월미도.jpg",
        "Wolmido night.jpg",
    ],
    "tribowl": [
        "Tri-bowl Songdo.jpg",
        "Tribowl Songdo.jpg",
        "Songdo Tri-bowl.jpg",
        "트라이보울.jpg",
        "Tri-bowl.jpg",
    ],
    "songdo-park": [
        "Songdo Central Park.jpg",
        "Songdo IBD Central Park.jpg",
        "송도 센트럴파크.jpg",
        "Songdo International City Central Park.jpg",
    ],
    "songdo-night": [
        "Songdo Central Park night.jpg",
        "Songdo night.jpg",
        "송도 야경.jpg",
        "Songdo IBD night.jpg",
    ],
    "songdo-outlet": [
        "Hyundai Premium Outlet Songdo.jpg",
        "Hyundai Premium Outlets Songdo.jpg",
        "송도 현대프리미엄아울렛.jpg",
        "Songdo outlet.jpg",
    ],
    "paradise-city": [
        "Paradise City Incheon.jpg",
        "Paradise City Hotel Incheon.jpg",
        "파라다이스시티.jpg",
        "Paradise City Yeongjong.jpg",
    ],
    "masian-beach": [
        "Masian Beach.jpg",
        "마시안해변.jpg",
        "Masian Beach Incheon.jpg",
        "Muuido Masian.jpg",
    ],
    "eulwangni-beach": [
        "Eulwangri Beach.jpg",
        "을왕리해수욕장.jpg",
        "Eulwangni Beach Incheon.jpg",
        "Eurwangni Beach.jpg",
    ],
    "dongmak-beach": [
        "Dongmak Beach.jpg",
        "동막해수욕장.jpg",
        "Dongmak Beach Ganghwa.jpg",
        "Ganghwa Dongmak.jpg",
    ],
    "ganghwa-peace": [
        "Ganghwa Peace Observatory.jpg",
        "강화평화전망대.jpg",
        "Ganghwa Peace Observatory 01.jpg",
        "Ganghwado Peace Observatory.jpg",
    ],
    "chojijin": [
        "Chojijin Fort.jpg",
        "초지진.jpg",
        "Chojijin Ganghwa.jpg",
        "Chojijin.jpg",
    ],
}

CTX = None


def ssl_ctx():
    global CTX
    if CTX is None:
        try:
            import certifi

            CTX = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            CTX = ssl._create_unverified_context()
    return CTX


def http_get(url: str, timeout: int = 90) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx()) as r:
        return r.read()


def special_filepath(title: str, width: int = 1280) -> str:
    enc = urllib.parse.quote(title.replace(" ", "_"))
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{enc}?width={width}"


def commons_search(query: str, limit: int = 10) -> list[str]:
    import json

    api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srnamespace": "6",
            "srlimit": str(limit),
            "format": "json",
        }
    )
    try:
        data = json.loads(http_get(api).decode())
    except Exception as exc:
        print(f"  search err: {exc}", flush=True)
        return []
    out = []
    for item in data.get("query", {}).get("search", []):
        t = item.get("title", "")
        if t.startswith("File:"):
            out.append(t[5:])
    return out


SEARCH = {
    "jayu-park": "Jayu Park Incheon Freedom Park",
    "wolmido-night": "Wolmido Ferris Wheel Incheon",
    "tribowl": "Tri-bowl Songdo Incheon",
    "songdo-park": "Songdo Central Park Incheon",
    "songdo-night": "Songdo Central Park night Incheon",
    "songdo-outlet": "Hyundai Premium Outlet Songdo",
    "paradise-city": "Paradise City Incheon hotel",
    "masian-beach": "Masian Beach Incheon Muuido",
    "eulwangni-beach": "Eulwangri Beach Incheon",
    "dongmak-beach": "Dongmak Beach Ganghwa",
    "ganghwa-peace": "Ganghwa Peace Observatory",
    "chojijin": "Chojijin Fort Ganghwa",
}

REJECT = ("portrait", "selfie", "map", "logo", "svg", "diagram", "stamp", "people", "crowd")


def ok_title(title: str) -> bool:
    low = title.lower()
    if low.endswith((".pdf", ".svg", ".gif", ".tif", ".tiff", ".djvu", ".webm")):
        return False
    return not any(b in low for b in REJECT)


def save_image(url: str, dest: Path) -> bool:
    try:
        data = http_get(url)
    except Exception as exc:
        print(f"  dl err: {exc}", flush=True)
        return False
    if len(data) < 12000:
        print(f"  too small ({len(data)})", flush=True)
        return False
    head = data[:32].lstrip()
    if head.startswith(b"<") or head.startswith(b"<!DO"):
        print("  rejected html", flush=True)
        return False
    if not (data[:3] == b"\xff\xd8\xff" or data[:8] == b"\x89PNG\r\n\x1a\n" or data[:4] == b"RIFF"):
        print("  bad magic", flush=True)
        return False
    dest.write_bytes(data)
    return True


def fetch_one(slug: str) -> bool:
    dest = IMG / f"{slug}.jpg"
    titles = list(FILES.get(slug, []))
    for t in commons_search(SEARCH.get(slug, slug), limit=10):
        if t not in titles:
            titles.append(t)
    for title in titles:
        if not ok_title(title):
            print(f"  skip title: {title}", flush=True)
            continue
        print(f"  try {title}", flush=True)
        if save_image(special_filepath(title), dest):
            print(f"+ {slug} <- {title} ({dest.stat().st_size})", flush=True)
            return True
        time.sleep(1.5)
    print(f"! FAIL {slug}", flush=True)
    return False


def main() -> int:
    IMG.mkdir(parents=True, exist_ok=True)
    ok = fail = 0
    for slug in FILES:
        print(f"\n## {slug}", flush=True)
        if fetch_one(slug):
            ok += 1
        else:
            fail += 1
        time.sleep(2.5)
    print(f"\ndone ok={ok} fail={fail}", flush=True)
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
