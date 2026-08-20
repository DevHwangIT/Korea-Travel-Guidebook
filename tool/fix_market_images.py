# -*- coding: utf-8 -*-
"""Force-redownload specific market covers with curated Commons titles only (no search)."""
from __future__ import annotations

import json
import ssl
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "Images" / "places"
UA = "KoreaTravelGuidebook/1.0 (market cover fix)"

# Only known-good File titles — no search (search returns PDFs)
FIX: dict[str, list[str]] = {
    "jagalchi-market": [
        "Korea-Busan-Jagalchi Fish Market-01.jpg",
        "Jagalchi Market 02.jpg",
        "Jagalchi Market 01.jpg",
    ],
    "seomun-market": [
        "Seomun Night Market, Daegu.jpg",
        "Seomun Night Market, Daegu on April 7th, 2017.jpg",
        "Seomun Market Gate.JPG",
        "Seommunmarket2005.JPG",
    ],
    "suwon-paldalmun-market": [
        "Suwon Paldalmun.jpg",
        "Paldalmun Gate.jpg",
        "Suwon Hwaseong Fortress Paldalmun.jpg",
        "Korea-Suwon-Paldalmun-01.jpg",
        "Paldalmun.jpg",
    ],
    "pohang-jukdo-market": [
        "Jukdo Market Pohang.jpg",
        "포항 죽도시장.jpg",
        "Pohang Jukdo Market.jpg",
        "Jukdo Traditional Market.jpg",
    ],
    "jeonju-jungang-market": [
        "Jeonju Central Market.jpg",
        "전주 중앙시장.jpg",
        "Jeonju market.jpg",
    ],
    "gongju-sanseong-market": [
        "Gongju Gongsanseong.jpg",
        "공산성.jpg",
        "Gongsanseong Fortress.jpg",
    ],
    "tongyeong-jungang-market": [
        "Tongyeong Jungang Market.jpg",
        "Tongyeong Central Market.jpg",
        "통영중앙시장.jpg",
    ],
    "mokpo-fish-market": [
        "Mokpo Port.jpg",
        "Mokpo Harbor.jpg",
        "목포항.jpg",
    ],
    "gyeongju-jungang-market": [
        "Gyeongju Jungang Market.jpg",
        "경주 중앙시장.jpg",
    ],
}


def ctx() -> ssl.SSLContext:
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl._create_unverified_context()


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=50, context=ctx()) as r:
        return r.read()


def resolve(title: str) -> str | None:
    api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "query",
            "titles": f"File:{title}",
            "prop": "imageinfo",
            "iiprop": "url|mime",
            "iiurlwidth": "1280",
            "format": "json",
        }
    )
    data = json.loads(get(api).decode())
    for page in data.get("query", {}).get("pages", {}).values():
        if "missing" in page:
            return None
        infos = page.get("imageinfo") or []
        if not infos:
            return None
        info = infos[0]
        mime = (info.get("mime") or "").lower()
        if "pdf" in mime or "html" in mime:
            return None
        return info.get("thumburl") or info.get("url")
    return None


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    for slug, titles in FIX.items():
        dest = IMG / f"{slug}.jpg"
        print(f"\n=== {slug} ===", flush=True)
        done = False
        for title in titles:
            print(f" try {title}", flush=True)
            time.sleep(2.0)
            try:
                url = resolve(title)
            except Exception as e:
                print(f"  api {e}", flush=True)
                time.sleep(5)
                continue
            if not url:
                print("  missing", flush=True)
                continue
            try:
                data = get(url)
            except Exception as e:
                print(f"  dl {e}", flush=True)
                continue
            if len(data) < 15000 or data[:4] == b"%PDF" or data[:1] == b"<":
                print("  bad payload", flush=True)
                continue
            dest.write_bytes(data)
            print(f"  OK {len(data)} bytes", flush=True)
            done = True
            break
        if not done:
            print("  STILL MISSING", flush=True)
        time.sleep(2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
