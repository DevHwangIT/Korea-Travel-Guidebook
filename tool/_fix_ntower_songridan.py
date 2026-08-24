# -*- coding: utf-8 -*-
from __future__ import annotations

import io
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "Images" / "places"
UA = "KoreaTravelGuidebook/1.0 (course photo audit; educational; rate-limited)"
CTX = ssl._create_unverified_context()
SLEEP = 7.0


def log(*a):
    print(*a, flush=True)


def landscape_crop(im: Image.Image, ratio: float = 1.5) -> Image.Image:
    w, h = im.size
    target_h = int(w / ratio)
    if target_h <= h:
        top = max(0, int((h - target_h) * 0.28))
        return im.crop((0, top, w, top + target_h))
    target_w = int(h * ratio)
    left = max(0, (w - target_w) // 2)
    return im.crop((left, 0, left + target_w, h))


def save_landscape_jpeg(dest: Path, data: bytes) -> int:
    im = Image.open(io.BytesIO(data)).convert("RGB")
    w, h = im.size
    log(f"    src {w}x{h} r={round(w / h, 3)}")
    if w / h < 1.2 or w / h > 2.05:
        im = landscape_crop(im)
    im.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=86, optimize=True)
    dest.write_bytes(buf.getvalue())
    return len(buf.getvalue())


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
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=90, context=CTX) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 4:
                log(f"    HTTP {e.code} sleep {delay:.0f}s")
                time.sleep(delay)
                delay = min(delay * 1.5, 80)
                continue
            raise
    raise RuntimeError("dl fail")


def try_titles(dest_name: str, titles: list[str]) -> bool:
    dest = P / dest_name
    for title in titles:
        log(f"  try {title}")
        url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(
            title.replace(" ", "_")
        )
        try:
            data = http_get(url)
        except Exception as exc:  # noqa: BLE001
            log(f"    fail {exc}")
            time.sleep(SLEEP)
            continue
        if not data or data[:1] == b"<" or len(data) < 14000:
            log(f"    not image {len(data) if data else 0}")
            time.sleep(SLEEP)
            continue
        try:
            n = save_landscape_jpeg(dest, data)
        except Exception as exc:  # noqa: BLE001
            log(f"    jpeg {exc}")
            time.sleep(SLEEP)
            continue
        log(f"  OK {dest_name} <- {title} ({n})")
        time.sleep(SLEEP)
        return True
    return False


def main() -> None:
    ok = try_titles(
        "n-seoul-tower.jpg",
        [
            "N-Seoul-Tower and Namsan Park (26876783888).jpg",
            "Korea Namsan NTower 06 (13238790903).jpg",
            "Korea Namsan NTower 08 (13238639995).jpg",
            "Seoul tower - panoramio - yamarhythm.jpg",
        ],
    )
    if not ok:
        log("FAILED n-seoul-tower.jpg")


if __name__ == "__main__":
    main()
