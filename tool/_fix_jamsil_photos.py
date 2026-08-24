# -*- coding: utf-8 -*-
"""Fix Seokchon Lake placeholder + tall-strip Jamsil/Songridan photos."""
from __future__ import annotations

import io
import ssl
import time
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "Images" / "places"
UA = "KoreaTravelGuidebook/1.0 (course photo audit; educational; rate-limited)"
CTX = ssl._create_unverified_context()
SLEEP = 7.0

COMMONS = {
    "seokchon-lake.jpg": [
        "Seokchonhosu.jpg",
        "Seokchon Lake.jpg",
        "Seokchon Lake Park.jpg",
        "석촌호수.jpg",
        "Lotte World Tower from Seokchon Lake.jpg",
        "Seokchon Lake with Lotte World Tower.jpg",
        "Cherry blossoms at Seokchon Lake.jpg",
        "Seokchon Lake cherry blossoms.jpg",
        "Lotte_World_Tower_and_Seokchon_Lake.jpg",
        "Seoul Seokchon Lake.jpg",
    ],
    "jamsil-skyline.jpg": [
        "Lotte World Tower.jpg",
        "Lotte World Tower Seoul.jpg",
        "Lotte World Tower in 2017.jpg",
        "Lotte World Tower Seoul South Korea.jpg",
        "롯데월드타워.jpg",
    ],
    "songridan-gil.jpg": [
        "Lotte World Tower.jpg",
        "Seokchonhosu.jpg",
        "Lotte World Tower from Seokchon Lake.jpg",
        "Seokchon Lake Park.jpg",
    ],
}


def log(*a):
    print(*a, flush=True)


def to_jpeg(data: bytes, max_side: int = 1600) -> bytes:
    im = Image.open(io.BytesIO(data)).convert("RGB")
    im.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=86, optimize=True)
    return buf.getvalue()


def landscape_crop(im: Image.Image, ratio: float = 1.5) -> Image.Image:
    w, h = im.size
    target_h = int(w / ratio)
    if target_h <= h:
        # portrait or square -> crop vertically, bias toward top (landmarks)
        top = max(0, int((h - target_h) * 0.22))
        return im.crop((0, top, w, top + target_h))
    target_w = int(h * ratio)
    left = max(0, (w - target_w) // 2)
    return im.crop((left, 0, left + target_w, h))


def save_landscape_jpeg(dest: Path, data: bytes) -> int:
    im = Image.open(io.BytesIO(data)).convert("RGB")
    w, h = im.size
    if w / h < 1.15 or w / h > 2.1:
        im = landscape_crop(im)
    im.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=86, optimize=True)
    raw = buf.getvalue()
    if len(raw) < 12000:
        raise RuntimeError(f"too small {len(raw)}")
    dest.write_bytes(raw)
    return len(raw)


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


def recrop_local(name: str) -> None:
    path = P / name
    im = Image.open(path).convert("RGB")
    w, h = im.size
    if 1.2 <= w / h <= 1.9:
        log(f"SKIP recrop {name} already {w}x{h}")
        return
    im = landscape_crop(im)
    im.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=86, optimize=True)
    path.write_bytes(buf.getvalue())
    log(f"RECROP {name} -> {im.size} {len(buf.getvalue())}")


def main() -> None:
    failed = []
    for dest, titles in COMMONS.items():
        log(f"== {dest}")
        if not try_titles(dest, titles):
            failed.append(dest)
            log(f"  NONE {dest}")
        time.sleep(1.2)
    # Always recrop remaining extreme portraits used in Seoul courses
    for name in (
        "jamsil-skyline.jpg",
        "songridan-gil.jpg",
        "n-seoul-tower.jpg",
        "hansung-univ.jpg",
        "ihwa-mural-village.jpg",
        "namdaemun-market.jpg",
        "gyeongnidan-gil.jpg",
        "yongridan-gil.jpg",
        "bus-terminal-seoul-express.jpg",
    ):
        recrop_local(name)
    log("FAILED downloads:", failed or "none")


if __name__ == "__main__":
    main()
