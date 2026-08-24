# -*- coding: utf-8 -*-
"""Pass 6: yeosu-jangdo + last-resort searches for remaining fallbacks."""
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

MUST: dict[str, list[str]] = {
    "yeosu-jangdo": [
        "Jangdo (Yeosu) 01.jpg",
        "Jangdo (Yeosu) 02.jpg",
        "Jangdo.jpg",
    ],
    "saryeoni-forest": [
        "Jeju forest path.jpg",
        "Jeju cedar forest.jpg",
        "Forest trail Jeju.jpg",
        # avoid Hallasan Yeongsil — wrong place
    ],
    "dalseong-wetland": [
        "Dalseong wetland.jpg",
        "달성습지생태공원.jpg",
        "Nakdonggang Dalseong.jpg",
    ],
    "yeojaman": [
        "Yeoja Bay tidal flat.jpg",
        "여자만 갯벌.jpg",
        "Suncheon Bay Yeoja.jpg",
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


def fetch(url: str):
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
    used = {md5_file(p) for p in IMG.glob("*.jpg")}
    replaced, still = [], []
    print("Cooldown 45s…", flush=True)
    time.sleep(45)

    for slug, titles in MUST.items():
        dest = IMG / f"{slug}.jpg"
        if dest.exists() and md5_file(dest) != fb:
            print(f"KEEP {slug}", flush=True)
            continue
        print(f"\n=== {slug} ===", flush=True)
        ok = False
        for title in titles:
            print(f"  TRY {title}", flush=True)
            time.sleep(5)
            for url in urls_for(title):
                data, err = fetch(url)
                if err == "http:404":
                    continue
                if err == "http:429":
                    print("  429 pause 120s", flush=True)
                    time.sleep(120)
                    data, err = fetch(url)
                if err or not data or len(data) < 12000:
                    if err:
                        print(f"  {err}", flush=True)
                    continue
                if not (data[:3] == b"\xff\xd8\xff" or data[:8] == b"\x89PNG\r\n\x1a\n"):
                    continue
                h = hashlib.md5(data).hexdigest()
                if h == fb or h in used:
                    print("  dup", flush=True)
                    continue
                dest.write_bytes(data)
                used.add(h)
                print(f"  OK {len(data)}", flush=True)
                ok = True
                break
            if ok:
                break
        (replaced if ok else still).append(slug)
        if not ok:
            print("  STILL", flush=True)
        time.sleep(5)

    print(f"\nreplaced={replaced}\nstill={still}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
