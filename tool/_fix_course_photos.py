# -*- coding: utf-8 -*-
"""Replace mismatched Seoul course photos with local dish shots or Commons files."""
from __future__ import annotations

import io
import shutil
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PLACES = ROOT / "Images" / "places"
UA = "KoreaTravelGuidebook/1.0 (course photo audit; educational; rate-limited)"
CTX = ssl._create_unverified_context()
SLEEP = 7.5

LOCAL_COPIES = [
    # dest, src — dish photos already in the repo
    (
        PLACES / "food-toast.jpg",
        ROOT / "pages/foods/desserts/toast/media/cover.jpg",
    ),
    (
        PLACES / "food-chicken.jpg",
        ROOT / "pages/foods/meals/dakgangjeong/media/cover.jpg",
    ),
    (
        PLACES / "food-chicken-hbc.jpg",
        ROOT / "pages/foods/meals/dakgangjeong/media/cover.jpg",
    ),
    (
        PLACES / "food-kalguksu.jpg",
        ROOT / "pages/foods/meals/guksu/media/cover.jpg",
    ),
]

PNG_TO_JPEG = [
    PLACES / "food-hotteok.jpg",
    PLACES / "mangwon-market.jpg",
]

# dest filename -> exact Commons File: titles (first usable wins)
COMMONS = {
    "n-seoul-tower.jpg": [
        "Namsan Tower, Seoul - Namsan2299.jpg",
        "Namsan Seoul Tower.jpg",
        "N Seoul Tower.jpg",
        "Korea-Seoul-N.Seoul.Tower-02.jpg",
        "N Seoul Tower Panorama Night.jpg",
        "Namsan.JPG",
    ],
    "food-kalguksu.jpg": [
        "Kalguksu.jpg",
        "Korean.cuisine-Kalguksu-01.jpg",
        "Kalguksu 1.jpg",
    ],
    "food-kimbap.jpg": [
        "Gimbap.jpg",
        "Kimbap.jpg",
        "Korean cuisine-Gimbap-01.jpg",
        "Gimbap 1.jpg",
    ],
    "food-gukbap.jpg": [
        "Dwaeji-gukbap.jpg",
        "Seolleongtang.jpg",
        "Sundae-gukbap.jpg",
        "Dwaeji gukbap.jpg",
    ],
    "food-dakhanmari.jpg": [
        "Dak-hanmari.jpg",
        "Korean.cuisine-Dakhanmari-01.jpg",
        "Dakhanmari.jpg",
        "Dak hanmari.jpg",
    ],
    "food-cafe.jpg": [
        "Caffe latte.jpg",
        "Cafe latte.jpg",
        "Latte art.jpg",
        "Iced caffe latte.jpg",
        "Cafe Americano.jpg",
    ],
    "food-samgyeopsal.jpg": [
        "Samgyeopsal.jpg",
        "Korean barbecue-Samgyeopsal-01.jpg",
        "Samgyeopsal 1.jpg",
    ],
    "food-bindaetteok.jpg": [
        "Bindaetteok.jpg",
        "Korean pancake-Bindaetteok-01.jpg",
        "Bindaetteok 1.jpg",
    ],
    "cheongdam-fashion.jpg": [
        "Garosu-gil in Sinsa-dong, Seoul.jpg",
        "Cheongdam-dong.jpg",
        "Apgujeong Rodeo Street.jpg",
        "Sinsa-dong Garosu-gil Seoul.jpg",
    ],
    "seochon.jpg": [
        "Seochon scene.jpg",
        "Sejong Village.jpg",
        "TongIn Market Entrance.jpg",
    ],
    "songridan-gil.jpg": [
        "Lotte World Tower and Seokchon Lake.jpg",
        "Seokchon Lake and Lotte World Tower.jpg",
        "Seokchon Lake Seoul.jpg",
    ],
    "duryunsan.jpg": [
        "11-03956.JPG",
        "Duryunsan.jpg",
        "Duryunsan Provincial Park.jpg",
    ],
}


def log(*a):
    print(*a, flush=True)


def is_jpeg(data: bytes) -> bool:
    return len(data) >= 3 and data[:3] == b"\xff\xd8\xff"


def to_jpeg_bytes(data: bytes, max_side: int = 1600) -> bytes:
    if is_jpeg(data) and len(data) < 2_400_000:
        return data
    im = Image.open(io.BytesIO(data)).convert("RGB")
    im.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=86, optimize=True)
    return buf.getvalue()


def http_get(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "image/*,*/*;q=0.8",
            "Referer": "https://commons.wikimedia.org/",
        },
    )
    delay = 12.0
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=90, context=CTX) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 5:
                log(f"    HTTP {e.code} sleep {delay:.0f}s")
                time.sleep(delay)
                delay = min(delay * 1.6, 90)
                continue
            raise
    raise RuntimeError("download failed")


def save_jpeg(dest: Path, data: bytes) -> int:
    jpeg = to_jpeg_bytes(data)
    if len(jpeg) < 12000:
        raise RuntimeError(f"too small {len(jpeg)}")
    dest.write_bytes(jpeg)
    return len(jpeg)


def copy_local() -> None:
    for dest, src in LOCAL_COPIES:
        if not src.exists():
            log(f"SKIP copy missing {src}")
            continue
        data = src.read_bytes()
        n = save_jpeg(dest, data)
        log(f"COPY {src.name} -> {dest.name} ({n})")


def convert_pngs() -> None:
    for path in PNG_TO_JPEG:
        if not path.exists():
            continue
        data = path.read_bytes()
        if is_jpeg(data):
            log(f"ALREADY JPEG {path.name}")
            continue
        n = save_jpeg(path, data)
        log(f"CONVERT PNG->JPEG {path.name} ({n})")


def try_commons(dest_name: str, titles: list[str]) -> bool:
    dest = PLACES / dest_name
    for title in titles:
        url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(
            title.replace(" ", "_")
        )
        log(f"  try {title}")
        try:
            data = http_get(url)
        except Exception as exc:  # noqa: BLE001
            log(f"    fail {exc}")
            time.sleep(SLEEP)
            continue
        if data[:1] == b"<" or len(data) < 12000:
            log(f"    not image ({len(data)})")
            time.sleep(SLEEP)
            continue
        try:
            n = save_jpeg(dest, data)
        except Exception as exc:  # noqa: BLE001
            log(f"    jpeg fail {exc}")
            time.sleep(SLEEP)
            continue
        log(f"  OK {dest_name} <- {title} ({n})")
        time.sleep(SLEEP)
        return True
    return False


def main() -> None:
    copy_local()
    convert_pngs()
    failed = []
    for i, (dest_name, titles) in enumerate(COMMONS.items(), 1):
        log(f"[{i}/{len(COMMONS)}] {dest_name}")
        if not try_commons(dest_name, titles):
            failed.append(dest_name)
            log(f"  NONE worked for {dest_name}")
        time.sleep(1.5)
    log("FAILED:", failed or "none")


if __name__ == "__main__":
    main()
