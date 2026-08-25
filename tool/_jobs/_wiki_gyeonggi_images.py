# -*- coding: utf-8 -*-
"""Fetch Wikipedia lead images for remaining Gyeonggi stops."""
from __future__ import annotations

import json
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMG = ROOT / "Images" / "places" / "_courses"
UA = "KoreaTravelGuidebook/1.0 (place covers; educational)"

PAGES = {
    "garden-of-morning-calm": [
        ("ko.wikipedia.org", "아침고요수목원"),
        ("en.wikipedia.org", "The Garden of Morning Calm"),
    ],
    "gwangmyeong-cave": [
        ("ko.wikipedia.org", "광명동굴"),
        ("en.wikipedia.org", "Gwangmyeong Cave"),
    ],
    "yeoju-outlet": [
        ("ko.wikipedia.org", "여주프리미엄아울렛"),
        ("ko.wikipedia.org", "프리미엄 아울렛"),
    ],
    "gwangmyeong-market": [
        ("ko.wikipedia.org", "광명전통시장"),
        ("ko.wikipedia.org", "광명시"),
    ],
    "haengnidangil": [
        ("ko.wikipedia.org", "행궁동"),
        ("ko.wikipedia.org", "화성행궁"),
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


def http_get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60, context=ssl_ctx()) as r:
        return r.read()


def pageimage(host: str, title: str) -> str | None:
    api = f"https://{host}/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "query",
            "titles": title,
            "prop": "pageimages",
            "pithumbsize": "1280",
            "format": "json",
        }
    )
    data = json.loads(http_get(api).decode())
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        thumb = (page.get("thumbnail") or {}).get("source")
        orig = (page.get("original") or {}).get("source")
        return orig or thumb
    return None


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
    if not (
        data[:3] == b"\xff\xd8\xff"
        or data[:8] == b"\x89PNG\r\n\x1a\n"
        or data[:4] == b"RIFF"
    ):
        print("  bad magic", flush=True)
        return False
    dest.write_bytes(data)
    return True


def main() -> int:
    IMG.mkdir(parents=True, exist_ok=True)
    for slug, pages in PAGES.items():
        print(f"\n## {slug}", flush=True)
        dest = IMG / f"{slug}.jpg"
        got = False
        for host, title in pages:
            print(f"  wiki {host} {title}", flush=True)
            try:
                url = pageimage(host, title)
            except Exception as exc:
                print(f"  api err: {exc}", flush=True)
                time.sleep(2)
                continue
            print(f"  image {url}", flush=True)
            if url and save_image(url, dest):
                print(f"+ {slug} ({dest.stat().st_size})", flush=True)
                got = True
                break
            time.sleep(2)
        if not got:
            print(f"! FAIL {slug}", flush=True)
        time.sleep(2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
