# -*- coding: utf-8 -*-
"""Download known-good Commons files for course photo fixes."""
from __future__ import annotations

import ssl
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMG = ROOT / "Images" / "places" / "_courses"
UA = "KoreaTravelGuidebook/1.0 (course photo fix; educational)"

FILES = {
    IMG / "wolmido-sea.jpg": "Sunshine on Wolmido.jpg",
    IMG / "wolmido-view.jpg": "Incheon from Wolmido.jpg",
    IMG / "songdo-park-clean.jpg": "South Korea, Incheon, Songdo, the Sharp Central Park Towers.jpg",
    IMG / "songdo-bridge.jpg": "View of Buildings from Central Park Bridge, Songdo IBD.jpg",
    IMG / "yeongjong-airport-beach.jpg": "Korea-A Beach near Incheon International Airport-01.jpg",
    IMG / "wangsan-empty.jpg": "Wangsan Beach, near Incheon Airport.jpg",
    IMG / "heyri-clean.jpg": "Heyri Artvalley 01 (31713169650).jpg",
    IMG / "pocheon-art-clean.jpg": "Art Valley In Korea (65750913).jpeg",
    IMG / "pocheon-cliff.jpg": "Geology of South Korea - Cliff(\uc808\ubcbd) (34264247890).jpg",
    IMG / "nami-island.jpg": "Winter Sonata Nami Island.jpg",
    IMG / "nami-trees.jpg": "Nami island winter.jpg",
    IMG / "nami-view.jpg": "View of Nami Island.JPG",
}

WIKI = {
    IMG / "paradise-city-resort.jpg": "https://ko.wikipedia.org/api/rest_v1/page/summary/%ED%8C%8C%EB%9D%BC%EB%8B%A4%EC%9D%B4%EC%8A%A4%EC%8B%9C%ED%8B%B0",
    IMG / "ganghwa-peace.jpg": "https://ko.wikipedia.org/api/rest_v1/page/summary/%EA%B0%95%ED%99%94%ED%8F%89%ED%99%94%EC%A0%84%EB%A7%9D%EB%8C%80",
    IMG / "dongmak-beach.jpg": "https://ko.wikipedia.org/api/rest_v1/page/summary/%EB%8F%99%EB%A7%89%ED%95%B4%EC%88%98%EC%9A%95%EC%9E%A5",
    IMG / "masian-beach.jpg": "https://ko.wikipedia.org/api/rest_v1/page/summary/%EB%AC%B4%EC%9D%98%EB%8F%84",
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
    with urllib.request.urlopen(req, timeout=90, context=ssl_ctx()) as r:
        return r.read()


def thumb_url(title: str, width: int = 1280) -> str:
    enc = urllib.parse.quote(title.replace(" ", "_"))
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{enc}?width={width}"


def save(dest: Path, title: str) -> bool:
    url = thumb_url(title)
    print(f"GET {title}", flush=True)
    try:
        data = http_get(url)
    except Exception as exc:
        print(f"  err {exc}", flush=True)
        return False
    if len(data) < 12000 or data[:32].lstrip().startswith(b"<"):
        print(f"  bad payload {len(data)}", flush=True)
        return False
    dest.write_bytes(data)
    print(f"+ {dest.name} ({dest.stat().st_size})", flush=True)
    return True


def wiki_thumb(dest: Path, api: str) -> bool:
    import json

    print(f"WIKI {dest.name}", flush=True)
    try:
        data = json.loads(http_get(api).decode())
    except Exception as exc:
        print(f"  err {exc}", flush=True)
        return False
    src = (data.get("originalimage") or data.get("thumbnail") or {}).get("source")
    if not src:
        print("  no image", flush=True)
        return False
    try:
        blob = http_get(src)
    except Exception as exc:
        print(f"  img err {exc}", flush=True)
        return False
    if len(blob) < 12000:
        print(f"  too small {len(blob)}", flush=True)
        return False
    dest.write_bytes(blob)
    print(f"+ {dest.name} ({dest.stat().st_size}) <- {src}", flush=True)
    return True


def main() -> int:
    ok = fail = 0
    for dest, title in FILES.items():
        if save(dest, title):
            ok += 1
        else:
            fail += 1
    for dest, api in WIKI.items():
        if wiki_thumb(dest, api):
            ok += 1
        else:
            fail += 1
    print(f"done ok={ok} fail={fail}", flush=True)
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
