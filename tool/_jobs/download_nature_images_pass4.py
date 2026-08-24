# -*- coding: utf-8 -*-
"""Pass 4: high-confidence remaining nature covers only."""
from __future__ import annotations

import hashlib
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "Images" / "places"
TYPE_FALLBACK = IMG / "_types" / "nature.jpg"
UA = "KoreaTravelGuidebook/1.0 (nature covers; educational)"
CTX = None

# Only titles already confirmed on Commons file/category pages.
MUST: dict[str, list[str]] = {
    "udo": [
        "Udo, Jeju Province, South Korea 01.jpg",
        "Udo Bong Scenery.jpg",
        "우도 풍경.jpg",
    ],
    "jusangjeolli": [
        "Daepo Jusangjeolli Cliff 01.jpg",
    ],
    "bijarim": [
        "Bijarim nutmeg forest jeju korea 6.jpg",
    ],
    "gotjawal": [
        "Gotjawal Forest.jpg",
    ],
    "seopjikoji": [
        "Seopjikoji.jpg",
        "Seopjiokji Coastline.jpg",
    ],
    "sangumburi": [
        "Silver Grass, Sangumburi, Jeju (억새, 제주 산굼부리) - panoramio.jpg",
    ],
    "jeongbang-falls": [
        "Jeongbang Falls.jpg",
        "Jeongbang 1 Jeju Island 제주도.jpg",
    ],
    "yongmeori-coast": [
        "Yongmeori Coast.jpg",
    ],
    "manjanggul": [
        "Jeju Manjanggul.jpg",
        "Manjanggul in Jeju.jpg",
        "Jeju LavaTube.JPG",
    ],
}


def ssl_ctx() -> ssl.SSLContext:
    global CTX
    if CTX is None:
        try:
            import certifi

            CTX = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            CTX = ssl._create_unverified_context()
    return CTX


def md5_file(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def urls_for(title: str, width: int = 1280) -> list[str]:
    name = title.replace(" ", "_")
    d = hashlib.md5(name.encode("utf-8")).hexdigest()
    q = urllib.parse.quote(name, safe="()-_,.'!")
    return [
        f"https://upload.wikimedia.org/wikipedia/commons/thumb/{d[0]}/{d[:2]}/{q}/{width}px-{q}",
        f"https://upload.wikimedia.org/wikipedia/commons/{d[0]}/{d[:2]}/{q}",
    ]


def fetch(url: str) -> tuple[bytes | None, str | None]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=70, context=ssl_ctx()) as r:
            return r.read(), None
    except urllib.error.HTTPError as e:
        return None, f"http:{e.code}"
    except Exception as e:  # noqa: BLE001
        return None, f"err:{e}"


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    fb = md5_file(TYPE_FALLBACK)
    used: set[str] = set()
    replaced: list[str] = []
    still: list[str] = []

    print("Cooldown 90s…", flush=True)
    time.sleep(90)

    for i, (slug, titles) in enumerate(MUST.items()):
        dest = IMG / f"{slug}.jpg"
        if dest.exists() and md5_file(dest) != fb:
            print(f"KEEP {slug}", flush=True)
            continue
        print(f"\n[{i+1}/{len(MUST)}] {slug}", flush=True)
        ok = False
        for title in titles:
            print(f"  TRY {title}", flush=True)
            time.sleep(6.0)
            for url in urls_for(title):
                data, err = fetch(url)
                if err == "http:404":
                    continue
                if err == "http:429":
                    print("  429 — pause 180s", flush=True)
                    time.sleep(180)
                    data, err = fetch(url)
                if err or data is None:
                    print(f"  {err}", flush=True)
                    continue
                if len(data) < 12000 or data[:3] != b"\xff\xd8\xff" and data[:8] != b"\x89PNG\r\n\x1a\n":
                    print("  bad payload", flush=True)
                    continue
                if data[:4] == b"%PDF" or data[:1] == b"<":
                    continue
                dest.write_bytes(data)
                h = md5_file(dest)
                if h == fb or h in used:
                    dest.write_bytes(TYPE_FALLBACK.read_bytes())
                    print("  skip hash", flush=True)
                    continue
                used.add(h)
                print(f"  OK {len(data)}", flush=True)
                ok = True
                break
            if ok:
                break
        if ok:
            replaced.append(slug)
        else:
            still.append(slug)
            print("  STILL FALLBACK", flush=True)
        time.sleep(8.0)

    print("\n=== PASS4 ===", flush=True)
    print(f"replaced: {replaced}", flush=True)
    print(f"still: {still}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
