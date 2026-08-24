# -*- coding: utf-8 -*-
"""Direct upload.wikimedia.org downloads — no API / Special:FilePath."""
from __future__ import annotations

import hashlib
import io
import json
import random
import ssl
import time
import urllib.error
import urllib.request
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Images" / "places"
FB = hashlib.md5((OUT / "_types" / "mountain.jpg").read_bytes()).hexdigest()
LOG = ROOT / "tool" / "_mountain-direct-dl-log.json"
UA = "KoreaTravelGuidebook/1.0 (educational static site; offline asset mirror)"
CTX = ssl._create_unverified_context()

# Direct upload URLs (hash path) — verified filenames for THESE mountains
DIRECT = {
    "odaesan": "https://upload.wikimedia.org/wikipedia/commons/a/a0/Odaesan_Mountain.jpg",
    "odaesan_alt": "https://upload.wikimedia.org/wikipedia/commons/e/e2/Korea-Gangwondo-Odaesan_National_Park_1663-07.JPG",
    "goryeosan": "https://upload.wikimedia.org/wikipedia/commons/2/22/Azalea_photo4.jpg",
    "bangtaesan": "https://upload.wikimedia.org/wikipedia/commons/4/4c/When_Autumn_Comes_To_Korea_(125962645).jpeg",
    "duryunsan": "https://upload.wikimedia.org/wikipedia/commons/b/bc/11-03956.JPG",
    "manisan": "https://upload.wikimedia.org/wikipedia/commons/0/0f/Mt_mani_2.jpg",
    "baegamsan": "https://upload.wikimedia.org/wikipedia/commons/e/e9/Baekyangsan.JPG",
}


def log(*a):
    print(*a, flush=True)


def md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def is_fb(slug: str) -> bool:
    p = OUT / f"{slug}.jpg"
    return (not p.exists()) or md5(p) == FB


def download(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Accept": "image/*", "Referer": "https://commons.wikimedia.org/"},
    )
    delay = 20.0
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, context=CTX, timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 5:
                w = delay + random.uniform(0, 5)
                log(f"    HTTP {e.code} sleep {w:.1f}s")
                time.sleep(w)
                delay = min(delay * 1.6, 180)
                continue
            raise
    raise RuntimeError("fail")


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
    items = [(s, u) for s, u in DIRECT.items() if not s.endswith("_alt") and is_fb(s)]
    # odaesan alt if still needed
    if is_fb("odaesan"):
        items = [("odaesan", DIRECT["odaesan"])] + [(s, u) for s, u in items if s != "odaesan"]
    log(f"Direct downloads: {len(items)}")
    log("Cooldown 120s...")
    time.sleep(120)
    results = []
    for i, (slug, url) in enumerate(items, 1):
        log(f"[{i}/{len(items)}] {slug}")
        try:
            raw = download(url)
            if len(raw) < 8000:
                # try alt for odaesan
                if slug == "odaesan":
                    log("  retry alt")
                    raw = download(DIRECT["odaesan_alt"])
                else:
                    raise RuntimeError(f"small {len(raw)}")
            n = to_jpeg(raw, OUT / f"{slug}.jpg")
            log(f"  OK {n}")
            results.append({"slug": slug, "ok": True, "url": url})
        except Exception as e:
            log(f"  FAIL: {e}")
            results.append({"slug": slug, "ok": False, "error": str(e)})
        time.sleep(12 + random.uniform(2, 6))
    LOG.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    # final tally
    places = json.loads((ROOT / "tool" / "_mountain_slugs.json").read_text(encoding="utf-8"))
    unique = [p["slug"] for p in places if not is_fb(p["slug"])]
    remain = [p["slug"] for p in places if is_fb(p["slug"])]
    log(f"\nDONE unique={len(unique)} remain={len(remain)}")
    log("REMAIN: " + ", ".join(remain))


if __name__ == "__main__":
    main()
