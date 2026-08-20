# -*- coding: utf-8 -*-
"""Download only curated Special:FilePath targets — no Wikimedia API."""
from __future__ import annotations

import hashlib
import io
import json
import random
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Images" / "places"
FB = hashlib.md5((OUT / "_types" / "mountain.jpg").read_bytes()).hexdigest()
LOG = ROOT / "tool" / "_mountain-photo-curated-log.json"
UA = "KoreaTravelGuidebook/1.0 (educational static site; offline asset mirror)"
CTX = ssl._create_unverified_context()

# Commons filenames known to depict the mountain (or its slopes/landscape)
CURATED = {
    "odaesan": "Odaesan_Mountain.jpg",
    "bangtaesan": "When_Autumn_Comes_To_Korea_(125962645).jpeg",
    "duryunsan": "11-03956.JPG",
    "goryeosan": "Azalea_photo4.jpg",
    "manisan": "Mt_mani_2.jpg",
    "baegamsan": "Baekyangsan.JPG",
    # Woljeongsa is on Odaesan — already have odaesan file above
    # Additional known commons
    "yongmunsan": "양평_용문사_은행나무.jpg",  # Yongmunsa on Yongmunsan (Yangpyeong) — tree landmark; prefer mountain if possible
}


def log(*a):
    print(*a, flush=True)


def md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def is_fb(slug: str) -> bool:
    p = OUT / f"{slug}.jpg"
    return (not p.exists()) or md5(p) == FB


def download(url: str) -> bytes:
    clean = url.split("?")[0]
    req = urllib.request.Request(
        clean,
        headers={"User-Agent": UA, "Accept": "image/*", "Referer": "https://commons.wikimedia.org/"},
    )
    delay = 15.0
    for attempt in range(8):
        try:
            with urllib.request.urlopen(req, context=CTX, timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 7:
                w = delay + random.uniform(0, 5)
                log(f"    HTTP {e.code} sleep {w:.1f}s")
                time.sleep(w)
                delay = min(delay * 1.5, 150)
                continue
            raise
    raise RuntimeError("dl fail")


def to_jpeg(data: bytes, dest: Path) -> int:
    if data[:3] == b"\xff\xd8\xff":
        dest.write_bytes(data)
        return len(data)
    if Image is None:
        raise RuntimeError("PIL")
    im = Image.open(io.BytesIO(data)).convert("RGB")
    im.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=88, optimize=True)
    raw = buf.getvalue()
    dest.write_bytes(raw)
    return len(raw)


def main():
    # skip yongmunsan ginkgo — not a mountain landscape; remove from curated for quality
    curated = {k: v for k, v in CURATED.items() if k != "yongmunsan"}
    todo = [(s, f) for s, f in curated.items() if is_fb(s)]
    log(f"Curated todo: {len(todo)}")
    log("Cooldown 60s...")
    time.sleep(60)
    results = []
    for i, (slug, fname) in enumerate(todo, 1):
        log(f"[{i}/{len(todo)}] {slug} <- {fname}")
        try:
            url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(fname)
            raw = download(url)
            if len(raw) < 8000:
                raise RuntimeError(f"small {len(raw)}")
            n = to_jpeg(raw, OUT / f"{slug}.jpg")
            log(f"  OK {n}")
            results.append({"slug": slug, "ok": True, "file": fname})
        except Exception as e:
            log(f"  FAIL: {e}")
            results.append({"slug": slug, "ok": False, "error": str(e)})
        time.sleep(8 + random.uniform(1, 4))
    LOG.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    log("DONE curated")


if __name__ == "__main__":
    main()
