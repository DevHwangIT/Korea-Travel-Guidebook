# -*- coding: utf-8 -*-
"""Download real Seoul attraction photos for curated courses (Wikimedia Commons).

Prefer exterior / place shots; skip portraits, celebrities, maps, logos.
"""
from __future__ import annotations

import json
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "Images" / "places"
UA = "KoreaTravelGuidebook/1.0 (seoul course covers; educational; rate-limited)"
SLEEP = 2.2

# slug -> preferred Commons File: titles (first usable wins)
FILES: dict[str, list[str]] = {
    "ikseon-dong": [
        "Ikseon-dong 익선동 October 1 2020 3.jpg",
        "Ikseon-dong 익선동 October 1 2020 2.jpg",
        "Ikseon-dong 익선동 October 1 2020 7.jpg",
        "Ikseon-dong 익선동 October 1 2020 10.jpg",
    ],
    "seoullo-7017": [
        "Seoullo 7017 Overview (2).jpg",
        "Seoullo 7017 02.jpg",
        "Seoullo 7017.jpg",
        "Seoullo 7017 01.jpg",
        "Seoullo 7017 night time city lights.jpg",
    ],
    "n-seoul-tower": [
        "Namsan Tower sunset, Seoul.jpg",
        "Namsan Tower, Seoul - Namsan2299.jpg",
        "N Seoul Tower Panorama Night.jpg",
    ],
    "ttukseom-hangang": [
        "Ttukseom Hangang Park 20260416 2.jpg",
        "Ttukseom Hangang Park 20260416 1.jpg",
        "Ttukseom Hangang Park 20260416 3.jpg",
        "NIght view at Ttukseom Hangang Park.jpg",
    ],
    "konkuk-university": [
        "Konkuk University, Seoul.jpg",
        "Ilgam Lake.jpg",
        "Konkuk05.jpg",
    ],
    "yeonnam-dong": [
        "연남동 (20240803) 2.jpg",
        "연남동 (20240803) 1.jpg",
        "연남옥탑에서 보이는 전망 1.jpg",
    ],
    "mangwon-hangang": [
        "Mangwon Hangang Park.png",
    ],
    "ihwa-mural-village": [
        "Ihwa Mural Village 11.jpg",
        "Ihwa Mural Village 27.jpg",
        "Ihwa Mural Village 9.jpg",
        "Ihwa Mural Village 12.jpg",
    ],
    "daehangno": [
        "Seoul daehangno.JPG",
        "Seoul-Daehakro-01.jpg",
        "20240601 144028 Daehangno Street, Seoul 04.jpg",
        "Seoul-Daehangno at night-01.jpg",
    ],
    "ddp": [
        "Dongdaemun Design Plaza at night, Seoul, Korea.jpg",
        "Dongdaemun Design Plaza grass.jpg",
        "Dongdaemun Design Plaza - DDP2376.jpg",
        "20240601 144028 Dongdaemun Design Plaza, Seoul 08.jpg",
        "DongDaemun Design Plaza (동대문디자인플라자 (DDP)), Seoul, South Korea (Unsplash aNSniQXO424).jpg",
    ],
    "national-museum-korea": [
        "Exterior of the National Museum of Korea in Seoul.jpg",
        "Front view of national museum of korea.jpg",
        "National Museum of Korea 국립중앙박물관 (5452976818).jpg",
        "National Museum of Korea 20150417 01 (17299785764).jpg",
    ],
    "sebit-seom": [
        "Korea Sevit Island 15 (15540663165).jpg",
        "Korea Sevit Island 02 (15354607748).jpg",
        "Korea Sevit Island 10 (15538039701).jpg",
        "Korea Sevit Island 06 (15540748615).jpg",
    ],
    "dosan-park": [
        "Korea-Seoul-Dosan Park-05.jpg",
        "Korea-Seoul-Dosan Park-01.jpg",
        "Korea-Seoul-Dosan Park-04.jpg",
        "Dosan Memorial Park - Seoul, South Korea - DSC00412.JPG",
    ],
    "euljiro": [
        "Night of Euljiro Alley.jpg",
        "Seoul CBD along Euljiro near Euljiro 1-ga Station.jpg",
        "Night view of Euljiro 1-ga intersection and the Sogong-dong Lotte town.jpg",
        "LED shop in Euljiro Seoul.jpg",
    ],
    "ssamziegil": [
        "Ssamziegil.jpg",
        "쌈지길.jpg",
        "Ssamzigil in Insadong.jpg",
        "Seoul-Insadong-Ssamzie Market-01.jpg",
    ],
    "seochon": [
        "Seochon scene.jpg",
        "Seochon Cafe.jpg",
        "Sejong Village.jpg",
        "Seochon Dae-o Bookstore.jpg",
        "TongIn Market Entrance.jpg",
    ],
    "yeouido": [
        "Yeouido, view from highway.jpg",
        "Korea-Seoul-Yeouido-National Assembly Building-03.jpg",
        "Mapo Bridge, Seoul.jpg",
    ],
    "haebangchon": [
        "Haebangchon.jpg",
        "Haebangchon Seoul.jpg",
        "해방촌.jpg",
    ],
    "hannam-dong": [
        "Hannam-dong.jpg",
        "Hannam Bridge Seoul.jpg",
        "한남동.jpg",
    ],
    "ichon-hangang": [
        "Ichon Hangang Park.jpg",
        "이촌한강공원.jpg",
        "Hangang Ichon.jpg",
    ],
    "jamsil-skyline": [
        "Lotte World Tower and Seokchon Lake.jpg",
        "Lotte World Tower Seoul.jpg",
        "Jamsil Seoul night.jpg",
    ],
}

SEARCH: dict[str, str] = {
    "ikseon-dong": "Ikseon-dong Seoul 익선동",
    "seoullo-7017": "Seoullo 7017",
    "n-seoul-tower": "N Seoul Tower Namsan",
    "ttukseom-hangang": "Ttukseom Hangang Park",
    "konkuk-university": "Konkuk University Seoul",
    "yeonnam-dong": "연남동 Yeonnam-dong Seoul",
    "mangwon-hangang": "Mangwon Hangang Park",
    "ihwa-mural-village": "Ihwa Mural Village",
    "daehangno": "Daehangno Seoul Daehakro",
    "ddp": "Dongdaemun Design Plaza DDP",
    "national-museum-korea": "National Museum of Korea exterior",
    "sebit-seom": "Sebitseom Sevit Island Seoul",
    "dosan-park": "Dosan Park Seoul",
    "euljiro": "Euljiro Seoul alley",
    "ssamziegil": "Ssamziegil Insadong",
    "seochon": "Seochon Seoul street",
    "yeouido": "Yeouido Seoul skyline",
    "haebangchon": "Haebangchon Seoul",
    "hannam-dong": "Hannam-dong Seoul",
    "ichon-hangang": "Ichon Hangang Park Seoul",
    "jamsil-skyline": "Lotte World Tower Seoul exterior",
}

REJECT = (
    "portrait",
    "jung woo",
    "정우성",
    "woman in",
    "man in",
    "busking",
    "logo",
    "map",
    "svg",
    "diagram",
    "flag",
    "cropped",
    "selfie",
    "people",
)

CTX = None


def ssl_ctx() -> ssl.SSLContext:
    global CTX
    if CTX is None:
        try:
            import certifi

            CTX = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            CTX = ssl._create_unverified_context()
    return CTX


def http_get(url: str, timeout: int = 60) -> bytes:
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
    except Exception as exc:  # noqa: BLE001
        print(f"  search err: {exc}", flush=True)
        return []
    out = []
    for item in data.get("query", {}).get("search", []):
        t = item.get("title", "")
        if t.startswith("File:"):
            out.append(t[5:])
    return out


def ok_title(title: str) -> bool:
    if not title:
        return False
    low = title.lower()
    if low.endswith((".pdf", ".svg", ".gif", ".tif", ".tiff", ".djvu", ".webm")):
        return False
    return not any(b in low for b in REJECT)


def save_image(url: str, dest: Path) -> bool:
    try:
        data = http_get(url, timeout=90)
    except Exception as exc:  # noqa: BLE001
        print(f"  dl err: {exc}", flush=True)
        return False
    if len(data) < 12000:
        print(f"  too small ({len(data)})", flush=True)
        return False
    head = data[:32].lstrip()
    if head.startswith(b"<") or head.startswith(b"<!DO"):
        print("  rejected html", flush=True)
        return False
    if not (
        data[:3] == b"\xff\xd8\xff"
        or data[:8] == b"\x89PNG\r\n\x1a\n"
        or data[:4] == b"RIFF"
    ):
        print("  bad magic", flush=True)
        return False
    # Always store as .jpg path; keep original bytes if jpeg/png/webp
    dest.write_bytes(data)
    return True


def fetch_one(slug: str) -> bool:
    dest = IMG / f"{slug}.jpg"
    if dest.exists() and dest.stat().st_size > 20000:
        print(f"= skip existing {slug} ({dest.stat().st_size})", flush=True)
        return True

    titles = list(FILES.get(slug, []))
    for t in commons_search(SEARCH.get(slug, slug), limit=10):
        if t not in titles:
            titles.append(t)

    for title in titles:
        if not ok_title(title):
            print(f"  skip title: {title}", flush=True)
            continue
        url = special_filepath(title)
        print(f"  try {title}", flush=True)
        if save_image(url, dest):
            print(f"+ {slug} <- {title} ({dest.stat().st_size})", flush=True)
            return True
        time.sleep(1.0)
    print(f"! FAIL {slug}", flush=True)
    return False


def main() -> int:
    IMG.mkdir(parents=True, exist_ok=True)
    ok = 0
    fail = 0
    for slug in FILES:
        print(f"\n## {slug}", flush=True)
        if fetch_one(slug):
            ok += 1
        else:
            fail += 1
        time.sleep(SLEEP)
    print(f"\ndone ok={ok} fail={fail}", flush=True)
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
