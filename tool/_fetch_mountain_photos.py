# -*- coding: utf-8 -*-
"""Download already-mapped mountain images; validate titles; reset bad uniques."""
from __future__ import annotations

import hashlib
import io
import json
import random
import re
import shutil
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
FALLBACK = ROOT / "Images" / "places" / "_types" / "mountain.jpg"
FALLBACK_MD5 = hashlib.md5(FALLBACK.read_bytes()).hexdigest()
SLUGS = json.loads((ROOT / "tool" / "_mountain_slugs.json").read_text(encoding="utf-8"))
MAP = json.loads((ROOT / "tool" / "_mountain-pageimage-map.json").read_text(encoding="utf-8"))
LOG = ROOT / "tool" / "_mountain-photo-fetch-log.json"
UA = "KoreaTravelGuidebook/1.0 (educational static site; offline asset mirror)"
CTX = ssl._create_unverified_context()

# Definitely wrong lead images
REJECT_SLUGS = {"geumsan", "jeombongsan"}
REJECT_SUBSTRINGS = re.compile(
    r"coral|county|귀암사|geumsan_county|sunrise_of_coral",
    re.I,
)


def log(*a):
    print(*a, flush=True)


def md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def is_fallback(slug: str) -> bool:
    p = OUT / f"{slug}.jpg"
    return (not p.exists()) or md5(p) == FALLBACK_MD5


def meta_ok(slug: str, en: str, ko: str, meta: dict) -> bool:
    if slug in REJECT_SLUGS:
        return False
    pageimage = str(meta.get("pageimage") or "")
    resolved = str(meta.get("resolved") or "")
    url = str(meta.get("url") or "")
    blob = f"{pageimage} {resolved} {url}"
    if REJECT_SUBSTRINGS.search(blob):
        return False
    en_l = en.lower()
    stem = re.sub(r"san$", "", en_l)
    low = blob.lower()
    if en_l and en_l in low:
        return True
    if stem and len(stem) >= 4 and stem in low:
        return True
    if ko and (ko in pageimage or ko in resolved):
        return True
    # romanized pieces in filename like Yumyeong_Mountain
    if stem and len(stem) >= 4 and stem[:4] in low:
        return True
    return False


def download(url: str) -> bytes:
    # strip tracking query for cleaner fetch
    clean = url.split("?")[0]
    req = urllib.request.Request(
        clean,
        headers={"User-Agent": UA, "Accept": "image/*,*/*", "Referer": "https://commons.wikimedia.org/"},
    )
    delay = 6.0
    for attempt in range(8):
        try:
            with urllib.request.urlopen(req, context=CTX, timeout=120) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 7:
                wait = delay + random.uniform(0, 2)
                log(f"    HTTP {e.code}, sleep {wait:.1f}s")
                time.sleep(wait)
                delay = min(delay * 1.7, 80)
                continue
            raise
    raise RuntimeError("download failed")


def to_jpeg(data: bytes, dest: Path) -> int:
    if data[:3] == b"\xff\xd8\xff":
        dest.write_bytes(data)
        return len(data)
    if Image is None:
        raise RuntimeError("PIL required")
    im = Image.open(io.BytesIO(data)).convert("RGB")
    im.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=88, optimize=True)
    raw = buf.getvalue()
    dest.write_bytes(raw)
    return len(raw)


def reset_bad_uniques():
    by_slug = {p["slug"]: p for p in SLUGS}
    # reset REJECT uniques + baegamsan (known Baekyangsan mismatch)
    for slug in list(REJECT_SLUGS) + ["baegamsan"]:
        dest = OUT / f"{slug}.jpg"
        if dest.exists() and md5(dest) != FALLBACK_MD5:
            shutil.copy2(FALLBACK, dest)
            log(f"RESET {slug} -> fallback")


def main():
    reset_bad_uniques()
    results = []
    to_fetch = []
    for p in SLUGS:
        slug, en, ko = p["slug"], p["en"], p["ko"]
        if not is_fallback(slug):
            results.append({"slug": slug, "ok": True, "kept": True})
            continue
        meta = MAP.get(slug)
        if meta and meta_ok(slug, en, ko, meta):
            to_fetch.append((p, meta))
        else:
            results.append({"slug": slug, "ok": False, "kept": False, "error": "no validated map"})

    log(f"Validated map downloads: {len(to_fetch)}")
    log("Cooldown 45s...")
    time.sleep(45)

    for i, (p, meta) in enumerate(to_fetch, 1):
        slug = p["slug"]
        dest = OUT / f"{slug}.jpg"
        log(f"[{i}/{len(to_fetch)}] {slug} <- {meta.get('pageimage')}")
        try:
            raw = download(meta["url"])
            if len(raw) < 10000:
                raise RuntimeError(f"too small {len(raw)}")
            n = to_jpeg(raw, dest)
            if md5(dest) == FALLBACK_MD5:
                raise RuntimeError("still fallback")
            log(f"  OK {n}")
            # update result entry
            results = [r for r in results if r["slug"] != slug]
            results.append(
                {
                    "slug": slug,
                    "ok": True,
                    "kept": False,
                    "title": meta.get("pageimage"),
                    "url": meta.get("url"),
                    "error": None,
                }
            )
        except Exception as e:
            log(f"  FAIL: {e}")
            results = [r for r in results if r["slug"] != slug]
            results.append({"slug": slug, "ok": False, "kept": False, "error": str(e)})
        LOG.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        time.sleep(3.0 + random.uniform(0.5, 1.5))

    unique = [p["slug"] for p in SLUGS if not is_fallback(p["slug"])]
    remain = [p["slug"] for p in SLUGS if is_fallback(p["slug"])]
    log(f"\nDONE unique={len(unique)} fallback_remain={len(remain)}")
    log("REMAIN: " + ", ".join(remain))


if __name__ == "__main__":
    main()
