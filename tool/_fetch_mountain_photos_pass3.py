# -*- coding: utf-8 -*-
"""Pass3: fill remaining mountain fallbacks — one mountain, few API calls, long sleeps."""
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
FB_PATH = OUT / "_types" / "mountain.jpg"
FB = hashlib.md5(FB_PATH.read_bytes()).hexdigest()
SLUGS = json.loads((ROOT / "tool" / "_mountain_slugs.json").read_text(encoding="utf-8"))
LOG = ROOT / "tool" / "_mountain-photo-pass3-log.json"
UA = "KoreaTravelGuidebook/1.0 (educational static site; offline asset mirror)"
CTX = ssl._create_unverified_context()
API = "https://commons.wikimedia.org/w/api.php"

# Extra Commons category titles when Category:{En} is empty/missing
CAT_OVERRIDES = {
    "baegamsan": ["Category:Baegamsan, Jeolla-do", "Category:Landscapes of Baegamsan"],
    "baegunsan": ["Category:Baegunsan", "Category:Baegunsan (Gwangyang)"],
    "byeonsan": ["Category:Byeonsanbando"],
    "geumsan": ["Category:Geumsan (mountain)", "Category:Geumsan, Namhae"],
    "manisan": ["Category:Manisan", "Category:Mani-san"],
    "seonginbong": ["Category:Seonginbong", "Category:Ulleungdo"],
    "gitdaebong": ["Category:Gitdaebong", "Category:Hongdo"],
    "jeombongsan": ["Category:Jeombongsan", "Category:Seoraksan"],
}

BAD = re.compile(r"map|logo|diagram|chart|flag|stamp|icon|coral reef|county", re.I)


def log(*a):
    print(*a, flush=True)


def md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def is_fb(slug: str) -> bool:
    p = OUT / f"{slug}.jpg"
    return (not p.exists()) or md5(p) == FB


def api(params: dict) -> dict:
    q = urllib.parse.urlencode({**params, "format": "json"})
    req = urllib.request.Request(f"{API}?{q}", headers={"User-Agent": UA})
    delay = 12.0
    for attempt in range(8):
        try:
            with urllib.request.urlopen(req, context=CTX, timeout=90) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 7:
                w = delay + random.uniform(0, 4)
                log(f"    API {e.code} sleep {w:.1f}s")
                time.sleep(w)
                delay = min(delay * 1.5, 120)
                continue
            raise
    raise RuntimeError("api fail")


def download(url: str) -> bytes:
    clean = url.split("?")[0]
    req = urllib.request.Request(
        clean,
        headers={"User-Agent": UA, "Accept": "image/*", "Referer": "https://commons.wikimedia.org/"},
    )
    delay = 10.0
    for attempt in range(7):
        try:
            with urllib.request.urlopen(req, context=CTX, timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 6:
                w = delay + random.uniform(0, 3)
                log(f"    DL {e.code} sleep {w:.1f}s")
                time.sleep(w)
                delay = min(delay * 1.6, 100)
                continue
            raise
    raise RuntimeError("dl fail")


def to_jpeg(data: bytes, dest: Path) -> int:
    if data[:3] == b"\xff\xd8\xff":
        dest.write_bytes(data)
        return len(data)
    if Image is None:
        raise RuntimeError("need PIL")
    im = Image.open(io.BytesIO(data)).convert("RGB")
    im.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=88, optimize=True)
    raw = buf.getvalue()
    dest.write_bytes(raw)
    return len(raw)


def match(en: str, ko: str, title: str) -> bool:
    if BAD.search(title):
        return False
    low = title.lower()
    en_l = en.lower()
    stem = re.sub(r"san$", "", en_l)
    if en_l in low:
        return True
    if stem and len(stem) >= 4 and stem in low:
        return True
    if ko and ko in title:
        return True
    # baegamsan files named Baekyangsan
    if en_l == "baegamsan" and "baekyang" in low:
        return True
    if en_l == "gitdaebong" and ("hongdo" in low or "gitdae" in low):
        return True
    return False


def category_files(cat: str) -> list[str]:
    data = api(
        {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": cat,
            "cmnamespace": 6,
            "cmlimit": 12,
            "cmtype": "file",
        }
    )
    return [m["title"] for m in data.get("query", {}).get("categorymembers", [])]


def search_files(query: str) -> list[str]:
    data = api(
        {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srnamespace": 6,
            "srlimit": 10,
        }
    )
    return [h["title"] for h in data.get("query", {}).get("search", [])]


def best_url(titles: list[str], en: str, ko: str) -> tuple[str, str] | None:
    titles = [t for t in titles if match(en, ko, t)]
    if not titles:
        return None
    data = api(
        {
            "action": "query",
            "titles": "|".join(titles[:5]),
            "prop": "imageinfo",
            "iiprop": "url|size|mime",
            "iiurlwidth": 1280,
        }
    )
    best = None
    score = -1
    for page in data.get("query", {}).get("pages", {}).values():
        ii = (page.get("imageinfo") or [None])[0]
        if not ii or ii.get("mime") not in ("image/jpeg", "image/png", "image/webp"):
            continue
        w = int(ii.get("thumbwidth") or ii.get("width") or 0)
        h = int(ii.get("thumbheight") or ii.get("height") or 0)
        if w < 400 or h < 220:
            continue
        url = ii.get("thumburl") or ii.get("url")
        sc = w + (50 if ii.get("mime") == "image/jpeg" else 0)
        if url and sc > score:
            score = sc
            best = (page.get("title") or "", url)
    return best


def find(en: str, ko: str, slug: str) -> tuple[str, str] | None:
    cats = CAT_OVERRIDES.get(slug, []) + [f"Category:{en}", f"Category:{en} National Park"]
    titles: list[str] = []
    for cat in cats:
        try:
            titles.extend(category_files(cat))
        except Exception as e:
            log(f"    cat fail {cat}: {e}")
        time.sleep(2.5)
        hit = best_url(titles, en, ko)
        if hit:
            return hit
    for q in (f'"{en}"', f"{en} Korea mountain", ko):
        if not q:
            continue
        try:
            titles.extend(search_files(q))
        except Exception as e:
            log(f"    search fail: {e}")
        time.sleep(2.5)
        hit = best_url(titles, en, ko)
        if hit:
            return hit
    return None


def main():
    need = [p for p in SLUGS if is_fb(p["slug"])]
    log(f"Need {len(need)}")
    log("Cooldown 60s...")
    time.sleep(60)
    results = []
    for i, p in enumerate(need, 1):
        slug, en, ko = p["slug"], p["en"], p["ko"]
        log(f"[{i}/{len(need)}] {slug}")
        if not is_fb(slug):
            results.append({"slug": slug, "ok": True, "kept": True})
            continue
        try:
            hit = find(en, ko, slug)
            if not hit:
                raise RuntimeError("no candidate")
            title, url = hit
            raw = download(url)
            if len(raw) < 10000:
                raise RuntimeError(f"small {len(raw)}")
            n = to_jpeg(raw, OUT / f"{slug}.jpg")
            if md5(OUT / f"{slug}.jpg") == FB:
                raise RuntimeError("still fallback")
            log(f"  OK {n} <- {title}")
            results.append({"slug": slug, "ok": True, "title": title, "url": url})
        except Exception as e:
            log(f"  FAIL: {e}")
            results.append({"slug": slug, "ok": False, "error": str(e)})
        LOG.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        time.sleep(5.0 + random.uniform(0.5, 2.0))

    unique = [p["slug"] for p in SLUGS if not is_fb(p["slug"])]
    remain = [p["slug"] for p in SLUGS if is_fb(p["slug"])]
    failed = [r["slug"] for r in results if not r.get("ok")]
    log(f"\nDONE unique={len(unique)} remain={len(remain)} failed={len(failed)}")
    log("REMAIN: " + ", ".join(remain))
    log("FAILED: " + ", ".join(failed))


if __name__ == "__main__":
    main()
