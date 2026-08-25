# -*- coding: utf-8 -*-
"""Download known-good Commons files for remaining course stops."""
from __future__ import annotations

import ssl
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "Images" / "places" / "_courses"
UA = "KoreaTravelGuidebook/1.2 (course photos)"
CTX = ssl._create_unverified_context()

FILES = {
    "everland-safari.jpg": "20241009 용인 에버랜드 주토피아 레서판다.jpg",
    "minsokchon-exit.jpg": "Architecture of Yongin Folk Village in South Korea.jpg",
    "gwangmyeong-market.jpg": "박승원 광명시장.jpg",
    "everland-amazon.jpg": "20241009 용인 에버랜드 아마존 익스프레스.jpg",
}


def http_get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
        return r.read()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for dest_name, title in FILES.items():
        dest = OUT / dest_name
        enc = urllib.parse.quote(title.replace(" ", "_"))
        url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{enc}?width=1600"
        print("GET", title, flush=True)
        try:
            data = http_get(url)
        except Exception as exc:
            print("  fail", exc, flush=True)
            continue
        if len(data) < 20000 or data[:32].lstrip()[:1] == b"<":
            print("  bad", len(data), flush=True)
            continue
        dest.write_bytes(data)
        print("  saved", dest.name, dest.stat().st_size, flush=True)


if __name__ == "__main__":
    main()
