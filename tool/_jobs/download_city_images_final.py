# -*- coding: utf-8 -*-
"""Final slow FilePath downloads + promote verified temp candidates."""
from __future__ import annotations

import hashlib
import ssl
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "Images" / "places"
TMP = ROOT / "tool" / "_tmp" / "city_imgs"
FB = IMG / "_types" / "city.jpg"
UA = "KoreaTravelGuidebook/1.0 (city covers final; educational)"
CTX = None
SLEEP = 20.0

# Exact Commons titles only (no search)
FILES: dict[str, list[str]] = {
    "busan-x-the-sky": ["Haeundae Beach.jpg"],  # beachfront district of the tower
    "seouldal": ["Street hongdae Seoul.jpg", "Hongdae night.jpg"],
    "hyundai-premium-outlet-songdo": ["Songdo Central Park in 2021.jpg"],
    "daegu-shinsegae": [
        "20211120 동대구역 3번 출구.jpg",
        "Dongdaegu Station.jpg",
        "Korea-Daegu-Dongdaegu Station-01.jpg",
    ],
    "yeosu-nangman-pocha": [
        "Yeosu night view from Odongdo.jpg",
        "Yeosu Harbor.jpg",
        "Expo 2012 Yeosu night.jpg",
        "Yeosu Korea night.jpg",
    ],
    "cheongdam": [
        "Cheongdam-dong Seoul.jpg",
        "Gangnam Seoul street.jpg",
    ],
    "paradise-city": [
        # Avoid Guns N' Roses "Paradise City"
        "Paradise City Incheon.jpg",
        "Incheon Paradise City Hotel.jpg",
        "Yeongjong Island.jpg",
        "Incheon Airport Casino.jpg",
    ],
    "inspire-resort": [
        "Yeongjongdo.jpg",
        "Yeongjong Island Incheon.jpg",
    ],
    "arte-museum-jeju": [],
    "nohyeong-supermarket": [],
    "83-tower": ["E WORLD in Daegu on April 5th 2013.jpg"],
}


def ssl_ctx():
    global CTX
    if CTX is None:
        try:
            import certifi

            CTX = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            CTX = ssl._create_unverified_context()
    return CTX


def md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90, context=ssl_ctx()) as r:
        return r.read()


def filepath(title: str) -> str:
    enc = urllib.parse.quote(title.replace(" ", "_"))
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{enc}?width=1280"


def save_jpeg(data: bytes, dest: Path) -> bool:
    if len(data) < 20000:
        return False
    if data[:3] != b"\xff\xd8\xff":
        return False
    dest.write_bytes(data)
    return True


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    fb = md5(FB)
    TMP.mkdir(parents=True, exist_ok=True)

    # Promote already-verified temp candidates
    promotes = {
        "busan-x-the-sky": TMP / "busan-x-the-sky_file0.jpg",
        "hyundai-premium-outlet-songdo": TMP / "hyundai-premium-outlet-songdo_file1.jpg",
        "83-tower": TMP / "83-tower_file0.jpg",
    }
    for slug, src in promotes.items():
        if src.exists() and src.stat().st_size > 20000:
            dest = IMG / f"{slug}.jpg"
            dest.write_bytes(src.read_bytes())
            print(f"PROMOTE {slug} <- {src.name} ({dest.stat().st_size})", flush=True)

    # Download remaining via FilePath only
    for slug, titles in FILES.items():
        dest = IMG / f"{slug}.jpg"
        if dest.exists() and md5(dest) != fb and slug not in (
            "paradise-city",  # still album art
            "the-bay-101",  # keep existing aerial if real
        ):
            # paradise still bad; others with real keep
            if slug == "paradise-city" or (dest.exists() and md5(dest) == fb):
                pass
            elif slug not in ("seouldal", "cheongdam", "daegu-shinsegae", "yeosu-nangman-pocha",
                              "inspire-resort", "arte-museum-jeju", "nohyeong-supermarket",
                              "paradise-city"):
                print(f"KEEP {slug}", flush=True)
                continue

        if dest.exists() and md5(dest) != fb and slug not in (
            "paradise-city", "seouldal", "cheongdam", "daegu-shinsegae",
            "yeosu-nangman-pocha", "inspire-resort", "arte-museum-jeju",
            "nohyeong-supermarket",
        ):
            print(f"KEEP {slug}", flush=True)
            continue

        if not titles:
            print(f"SKIP empty {slug}", flush=True)
            continue

        ok = False
        for title in titles:
            print(f"TRY {slug} <- {title}", flush=True)
            time.sleep(SLEEP)
            try:
                data = get(filepath(title))
            except Exception as exc:  # noqa: BLE001
                print(f"  err {exc}", flush=True)
                continue
            if save_jpeg(data, dest) and md5(dest) != fb:
                print(f"  OK {dest.stat().st_size}", flush=True)
                ok = True
                break
            print("  reject", flush=True)
        if not ok:
            print(f"MISS {slug}", flush=True)

    # Final tally for newly-added city slugs
    newish = list(FILES.keys()) + [
        "seongsu-dong", "coex", "byeolmadang-library", "apgujeong", "lotte-world",
        "namsan-cable-car", "haeundae-blueline-park", "lotte-world-adventure-busan",
        "shinsegae-centum-city", "the-bay-101", "busan-cinema-center", "wolmido",
        "incheon-chinatown", "dongseong-ro", "eworld", "aquaplanet-yeosu", "981-park",
    ]
    # unique preserve order
    seen = set()
    slugs = []
    for s in newish:
        if s not in seen:
            seen.add(s)
            slugs.append(s)

    real, fall = [], []
    for s in slugs:
        p = IMG / f"{s}.jpg"
        if not p.exists() or md5(p) == fb:
            fall.append(s)
        else:
            real.append(s)
    print(f"\nREAL={len(real)} FALLBACK={len(fall)}", flush=True)
    print("FALLBACK:", ", ".join(fall), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
