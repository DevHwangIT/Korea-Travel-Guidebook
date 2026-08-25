# -*- coding: utf-8 -*-
"""Fetch missing Incheon/Gyeonggi course photos from Wikimedia Commons."""
from __future__ import annotations

import json
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMG = ROOT / "Images" / "places" / "_courses"
FOOD = ROOT / "Images" / "places"
UA = "KoreaTravelGuidebook/1.0 (course photo review; educational; rate-limited)"

JOBS = [
    {
        "dest": IMG / "wolmido-sea.jpg",
        "titles": [
            "Wolmido Island.jpg",
            "Wolmido.jpg",
            "Wolmi Island Incheon.jpg",
            "Incheon Wolmido.jpg",
            "월미도.jpg",
            "Wolmido seashore.jpg",
        ],
        "search": "Wolmido Incheon beach sea",
    },
    {
        "dest": IMG / "jayu-park-view.jpg",
        "titles": [
            "Jayu Park Incheon.jpg",
            "Freedom Park Incheon.jpg",
            "Incheon Jayu Park.jpg",
            "MacArthur statue Jayu Park.jpg",
            "Jayu Park.jpg",
            "자유공원 인천.jpg",
        ],
        "search": "Jayu Park Incheon MacArthur",
    },
    {
        "dest": IMG / "paradise-city-resort.jpg",
        "titles": [
            "Paradise City Incheon.jpg",
            "Paradise City Hotel Incheon.jpg",
            "Paradise City Yeongjong.jpg",
            "파라다이스시티 인천.jpg",
            "Paradise City.jpg",
        ],
        "search": "Paradise City Incheon hotel resort",
    },
    {
        "dest": IMG / "masian-beach.jpg",
        "titles": [
            "Masian Beach.jpg",
            "마시안해변.jpg",
            "Masian Beach Incheon.jpg",
            "Muuido beach.jpg",
            "Muui Island beach.jpg",
        ],
        "search": "Masian Beach Muuido Incheon",
    },
    {
        "dest": IMG / "eulwangni-empty.jpg",
        "titles": [
            "Eulwangri Beach.jpg",
            "Eurwangni Beach.jpg",
            "을왕리해수욕장.jpg",
            "Eulwangni Beach Incheon.jpg",
            "Yeongjongdo beach.jpg",
        ],
        "search": "Eulwangri Beach Incheon Yeongjong",
    },
    {
        "dest": IMG / "dongmak-beach.jpg",
        "titles": [
            "Dongmak Beach.jpg",
            "동막해수욕장.jpg",
            "Dongmak Beach Ganghwa.jpg",
            "Ganghwa Dongmak.jpg",
            "Ganghwado beach.jpg",
        ],
        "search": "Dongmak Beach Ganghwa",
    },
    {
        "dest": IMG / "ganghwa-peace.jpg",
        "titles": [
            "Ganghwa Peace Observatory.jpg",
            "강화평화전망대.jpg",
            "Ganghwa Peace Observatory 01.jpg",
            "Ganghwado Peace Observatory.jpg",
        ],
        "search": "Ganghwa Peace Observatory",
    },
    {
        "dest": IMG / "songdo-park-clean.jpg",
        "titles": [
            "Songdo Central Park.jpg",
            "Songdo IBD Central Park.jpg",
            "송도 센트럴파크.jpg",
            "Songdo International City Central Park.jpg",
            "Songdo canal.jpg",
        ],
        "search": "Songdo Central Park canal Incheon",
    },
    {
        "dest": IMG / "nami-island.jpg",
        "titles": [
            "Nami Island.jpg",
            "Namiseom.jpg",
            "남이섬.jpg",
            "Nami Island metasequoia.jpg",
            "Namiseom Gapyeong.jpg",
        ],
        "search": "Nami Island Gapyeong metasequoia",
    },
    {
        "dest": IMG / "heyri-clean.jpg",
        "titles": [
            "Heyri Art Valley.jpg",
            "Heyri Art Village.jpg",
            "Paju Heyri.jpg",
            "헤이리 예술마을.jpg",
            "Heyri.jpg",
        ],
        "search": "Heyri Art Village Paju architecture",
    },
    {
        "dest": IMG / "pocheon-art-clean.jpg",
        "titles": [
            "Pocheon Art Valley.jpg",
            "포천아트밸리.jpg",
            "Cheonjuho Lake Pocheon.jpg",
            "Pocheon Art Valley lake.jpg",
        ],
        "search": "Pocheon Art Valley quarry lake",
    },
    {
        "dest": IMG / "dora-observatory.jpg",
        "titles": [
            "Dora Observatory.jpg",
            "Dora Observatory Paju.jpg",
            "도라전망대.jpg",
            "Dorasan Observatory.jpg",
        ],
        "search": "Dora Observatory Paju building",
    },
    {
        "dest": FOOD / "food-jajang.jpg",
        "titles": [
            "Jjajangmyeon.jpg",
            "Jajangmyeon.jpg",
            "Korean jajangmyeon.jpg",
            "짜장면.jpg",
            "Jjajangmyeon 01.jpg",
        ],
        "search": "Jjajangmyeon Korean noodles",
    },
    {
        "dest": FOOD / "food-seafood.jpg",
        "titles": [
            "Korean seafood stew.jpg",
            "Haemul-jeongol.jpg",
            "Jogae-gui.jpg",
            "Korean grilled clams.jpg",
            "Haemul-tang.jpg",
            "Korean seafood.jpg",
        ],
        "search": "Korean seafood stew haemul",
    },
    {
        "dest": IMG / "everland-garden.jpg",
        "titles": [
            "Everland Four Seasons Garden.jpg",
            "Everland flower garden.jpg",
            "Everland Yongin.jpg",
            "에버랜드.jpg",
        ],
        "search": "Everland garden flowers Yongin",
    },
    {
        "dest": IMG / "gwangmyeong-market.jpg",
        "titles": [
            "Gwangmyeong Traditional Market.jpg",
            "광명전통시장.jpg",
            "Gwangmyeong market.jpg",
        ],
        "search": "Gwangmyeong Traditional Market",
    },
    {
        "dest": IMG / "yeoju-outlet.jpg",
        "titles": [
            "Yeoju Premium Outlets.jpg",
            "여주프리미엄아울렛.jpg",
            "Yeoju Premium Outlet.jpg",
        ],
        "search": "Yeoju Premium Outlets",
    },
    {
        "dest": IMG / "sinpo-market.jpg",
        "titles": [
            "Sinpo International Market.jpg",
            "신포국제시장.jpg",
            "Sinpo Market Incheon.jpg",
        ],
        "search": "Sinpo International Market Incheon",
    },
]

CTX = None
REJECT = ("portrait", "selfie", "map", "logo", "svg", "diagram", "stamp", "crowd")


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


def commons_search(query: str, limit: int = 8) -> list[str]:
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
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return True


def fetch_one(job: dict) -> bool:
    dest = job["dest"]
    titles = list(job.get("titles") or [])
    for t in commons_search(job.get("search") or dest.stem, limit=8):
        if t not in titles:
            titles.append(t)
    for title in titles:
        if not ok_title(title):
            print(f"  skip title: {title}", flush=True)
            continue
        print(f"  try {title}", flush=True)
        if save_image(special_filepath(title), dest):
            print(f"+ {dest.name} <- {title} ({dest.stat().st_size})", flush=True)
            return True
        time.sleep(1.2)
    print(f"! FAIL {dest.name}", flush=True)
    return False


def main() -> int:
    ok = fail = 0
    for job in JOBS:
        print(f"\n## {job['dest'].name}", flush=True)
        if fetch_one(job):
            ok += 1
        else:
            fail += 1
        time.sleep(2.0)
    print(f"\ndone ok={ok} fail={fail}", flush=True)
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
