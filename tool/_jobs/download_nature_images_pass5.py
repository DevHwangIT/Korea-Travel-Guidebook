# -*- coding: utf-8 -*-
"""Pass 5: last remaining nature covers with verified titles."""
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
    "geomundo": [
        "Geomundo 1.jpg",
        "Geomundo 2.jpg",
        "Geomundo and Baekdo from Bultanbong.jpg",
    ],
    "geumodo": [
        "Korea Geumodo Bireong trail (7800583572).jpg",
    ],
    "baekdo": [
        "Geomundo and Baekdo from Bultanbong.jpg",
    ],
    "soesoggak": [
        "Soesokkak.jpg",
        "Soesokkak Jeju.jpg",
        "쇠소깍.jpg",
        "Soesokkak estuary Jeju.jpg",
        "Jeju Soesokkak.jpg",
    ],
    "saryeoni-forest": [
        "Saryeoni Forest.jpg",
        "Saryeoni Forest Path.jpg",
        "사려니숲길.jpg",
        "Saryeoni Forest Trail Jeju.jpg",
        "Jeju Saryeoni.jpg",
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
    # Avoid reusing baekdo/geomundo same file: process geomundo first, then baekdo with alt.
    used = set()
    replaced = []
    still = []

    print("Cooldown 60s…", flush=True)
    time.sleep(60)

    for slug, titles in MUST.items():
        dest = IMG / f"{slug}.jpg"
        if dest.exists() and md5_file(dest) != fb:
            print(f"KEEP {slug}", flush=True)
            continue
        print(f"\n=== {slug} ===", flush=True)
        ok = False
        for title in titles:
            print(f"  TRY {title}", flush=True)
            time.sleep(5.0)
            for url in urls_for(title):
                data, err = fetch(url)
                if err == "http:404":
                    continue
                if err == "http:429":
                    print("  429 pause 150s", flush=True)
                    time.sleep(150)
                    data, err = fetch(url)
                if err or not data:
                    print(f"  {err}", flush=True)
                    continue
                if len(data) < 12000:
                    continue
                if not (data[:3] == b"\xff\xd8\xff" or data[:8] == b"\x89PNG\r\n\x1a\n"):
                    continue
                dest.write_bytes(data)
                h = md5_file(dest)
                if h == fb or h in used:
                    dest.write_bytes(TYPE_FALLBACK.read_bytes())
                    print("  skip dup", flush=True)
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
            print("  STILL", flush=True)
        time.sleep(6.0)

    print(f"\nreplaced={replaced}\nstill={still}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
