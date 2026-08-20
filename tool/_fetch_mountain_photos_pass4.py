# -*- coding: utf-8 -*-
"""Pass4: curated FilePath + slow Wikipedia pageimages for remainders."""
from __future__ import annotations

import hashlib
import io
import json
import random
import re
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
SLUGS = {p["slug"]: p for p in json.loads((ROOT / "tool" / "_mountain_slugs.json").read_text(encoding="utf-8"))}
REMAIN = json.loads((ROOT / "tool" / "_mountain_remain.json").read_text(encoding="utf-8"))
LOG = ROOT / "tool" / "_mountain-photo-pass4-log.json"
UA = "KoreaTravelGuidebook/1.0 (educational static site; offline asset mirror)"
CTX = ssl._create_unverified_context()

# Direct Commons filenames (validated via prior search / category pages)
CURATED = {
    "baegamsan": "Baekyangsan.JPG",
    "odaesan": "Odaesan_Mountain.jpg",
    "bangtaesan": "When_Autumn_Comes_To_Korea_(125962645).jpeg",
    "duryunsan": "11-03956.JPG",  # Daeheungsa on Duryunsan slopes (landscape)
    "goryeosan": "Azalea_photo4.jpg",  # Goryeosan famous azalea landscape (ko wiki lead)
    "manisan": "Mt_mani_2.jpg",
    "jirisan": "Korea-Mountain-Jirisan-15.jpg",
}

# More curated from known Commons patterns / prior map
CURATED.update(
    {
        "seonginbong": "Ulleung_island_from_above.jpg",
    }
)


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
    delay = 12.0
    for attempt in range(8):
        try:
            with urllib.request.urlopen(req, context=CTX, timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 7:
                w = delay + random.uniform(0, 3)
                log(f"    DL {e.code} sleep {w:.1f}s")
                time.sleep(w)
                delay = min(delay * 1.5, 120)
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


def filepath_url(filename: str) -> str:
    # Special:FilePath redirects to upload URL
    return "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(filename)


def wiki_pageimage(lang: str, title: str) -> str | None:
    api = f"https://{lang}.wikipedia.org/w/api.php"
    q = urllib.parse.urlencode(
        {
            "action": "query",
            "titles": title,
            "prop": "pageimages",
            "format": "json",
            "pithumbsize": 1280,
            "pilicense": "any",
            "redirects": 1,
        }
    )
    req = urllib.request.Request(f"{api}?{q}", headers={"User-Agent": UA})
    delay = 15.0
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, context=CTX, timeout=90) as r:
                data = json.loads(r.read().decode())
            break
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 5:
                w = delay + random.uniform(0, 4)
                log(f"    wiki {e.code} sleep {w:.1f}s")
                time.sleep(w)
                delay = min(delay * 1.5, 120)
                continue
            raise
    else:
        return None
    for page in data.get("query", {}).get("pages", {}).values():
        if int(page.get("pageid", -1)) < 0:
            continue
        thumb = page.get("thumbnail") or {}
        src = thumb.get("source")
        if not src:
            continue
        pname = str(page.get("pageimage") or "")
        resolved = str(page.get("title") or "")
        # reject obvious wrong pages
        if re.search(r"county|coral|disambiguation", f"{pname} {resolved}", re.I):
            continue
        if " (disambiguation)" in resolved.lower():
            continue
        return src
    return None


def save_from_url(slug: str, url: str, note: str) -> bool:
    dest = OUT / f"{slug}.jpg"
    raw = download(url)
    if len(raw) < 8000:
        raise RuntimeError(f"small {len(raw)}")
    n = to_jpeg(raw, dest)
    if md5(dest) == FB:
        raise RuntimeError("fallback")
    log(f"  OK {n} [{note}]")
    return True


def main():
    # refresh remain
    need = [p for p in REMAIN if is_fb(p["slug"])]
    # also any current fallbacks not in remain
    for p in SLUGS.values():
        if is_fb(p["slug"]) and p["slug"] not in {x["slug"] for x in need}:
            need.append(p)
    log(f"Need {len(need)}")
    log("Cooldown 90s...")
    time.sleep(90)

    results = []
    for i, p in enumerate(need, 1):
        slug, en, ko = p["slug"], p["en"], p["ko"]
        log(f"[{i}/{len(need)}] {slug}")
        if not is_fb(slug):
            results.append({"slug": slug, "ok": True, "kept": True})
            continue
        try:
            if slug in CURATED:
                url = filepath_url(CURATED[slug])
                save_from_url(slug, url, f"curated:{CURATED[slug]}")
                results.append({"slug": slug, "ok": True, "via": "curated", "file": CURATED[slug]})
            else:
                # try ko then en pageimage only (1-2 calls)
                src = None
                if ko:
                    src = wiki_pageimage("ko", ko)
                    time.sleep(8)
                if not src:
                    src = wiki_pageimage("en", en)
                    time.sleep(8)
                if not src:
                    src = wiki_pageimage("en", f"{en} (mountain)")
                    time.sleep(8)
                if not src:
                    raise RuntimeError("no wiki image")
                save_from_url(slug, src, "wiki")
                results.append({"slug": slug, "ok": True, "via": "wiki", "url": src})
        except Exception as e:
            log(f"  FAIL: {e}")
            results.append({"slug": slug, "ok": False, "error": str(e)})
        LOG.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        time.sleep(6 + random.uniform(1, 3))

    unique = [s for s in SLUGS if not is_fb(s)]
    remain = [s for s in SLUGS if is_fb(s)]
    failed = [r["slug"] for r in results if not r.get("ok")]
    log(f"\nDONE unique={len(unique)} remain={len(remain)} failed={len(failed)}")
    log("REMAIN: " + ", ".join(remain))


if __name__ == "__main__":
    main()
