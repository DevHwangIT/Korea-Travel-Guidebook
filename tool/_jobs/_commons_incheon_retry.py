# -*- coding: utf-8 -*-
"""Retry Commons search for leftover Incheon photos."""
from __future__ import annotations

import json
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMG = ROOT / "Images" / "places" / "_courses"
UA = "KoreaTravelGuidebook/1.0 (incheon covers)"

QUERIES = {
    "wolmido-night": ["Wolmido", "Wolmi Theme Park", "월미도", "월미바다열차"],
    "tribowl": ["Tri-bowl Songdo", "트라이보울", "Songdo Tribowl"],
    "paradise-city": ["Paradise City Incheon", "파라다이스시티 인천", "Paradise City hotel Incheon"],
    "dongmak-beach": ["Dongmak Beach", "동막해수욕장", "Ganghwa Dongmak"],
    "ganghwa-peace": ["Ganghwa Peace Observatory", "강화평화전망대"],
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


def http_get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60, context=ssl_ctx()) as r:
        return r.read()


def search(q: str) -> list[str]:
    api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "query",
            "list": "search",
            "srsearch": q,
            "srnamespace": "6",
            "srlimit": "8",
            "format": "json",
        }
    )
    data = json.loads(http_get(api).decode())
    titles = []
    for hit in data.get("query", {}).get("search", []):
        titles.append(hit.get("title", ""))
    return titles


def save_image(url: str, dest: Path) -> bool:
    try:
        data = http_get(url)
    except Exception as exc:
        print(f"  dl err: {exc}", flush=True)
        return False
    if len(data) < 12000:
        print(f"  too small ({len(data)})", flush=True)
        return False
    if data[:32].lstrip()[:1] == b"<":
        print("  html", flush=True)
        return False
    if not (data[:3] == b"\xff\xd8\xff" or data[:8] == b"\x89PNG\r\n\x1a\n" or data[:4] == b"RIFF"):
        print("  magic", data[:8], flush=True)
        return False
    dest.write_bytes(data)
    return True


def special(title: str) -> str:
    name = title.split(":", 1)[-1]
    enc = urllib.parse.quote(name.replace(" ", "_"))
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{enc}?width=1280"


def main() -> int:
    IMG.mkdir(parents=True, exist_ok=True)
    for slug, queries in QUERIES.items():
        print(f"\n## {slug}", flush=True)
        dest = IMG / f"{slug}.jpg"
        got = False
        for q in queries:
            print(f"  search {q}", flush=True)
            try:
                titles = search(q)
            except Exception as exc:
                print(f"  err {exc}", flush=True)
                time.sleep(8)
                continue
            for title in titles:
                low = title.lower()
                if low.endswith((".svg", ".gif", ".pdf", ".djvu")):
                    continue
                print(f"  try {title}", flush=True)
                if save_image(special(title), dest):
                    print(f"+ {slug} <- {title} ({dest.stat().st_size})", flush=True)
                    got = True
                    break
                time.sleep(4)
            if got:
                break
            time.sleep(8)
        if not got:
            print(f"! FAIL {slug}", flush=True)
        time.sleep(8)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
