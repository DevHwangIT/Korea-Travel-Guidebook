# -*- coding: utf-8 -*-
"""Second pass: fill remaining mountain fallbacks (slow, resume-safe)."""
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
FALLBACK = ROOT / "Images" / "places" / "_types" / "mountain.jpg"
FB = hashlib.md5(FALLBACK.read_bytes()).hexdigest()
SLUGS = json.loads((ROOT / "tool" / "_mountain_slugs.json").read_text(encoding="utf-8"))
MAP = json.loads((ROOT / "tool" / "_mountain-pageimage-map.json").read_text(encoding="utf-8"))
LOG = ROOT / "tool" / "_mountain-photo-pass2-log.json"
UA = "KoreaTravelGuidebook/1.0 (educational static site; offline asset mirror)"
CTX = ssl._create_unverified_context()

REJECT = re.compile(r"coral|county|귀암사|map|logo|diagram|chart|flag|stamp", re.I)


def log(*a):
    print(*a, flush=True)


def md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def is_fb(slug: str) -> bool:
    p = OUT / f"{slug}.jpg"
    return (not p.exists()) or md5(p) == FB


def http_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    delay = 10.0
    for attempt in range(10):
        try:
            with urllib.request.urlopen(req, context=CTX, timeout=90) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 9:
                w = delay + random.uniform(0, 3)
                log(f"    API {e.code}, sleep {w:.1f}s")
                time.sleep(w)
                delay = min(delay * 1.6, 100)
                continue
            raise
    raise RuntimeError("api fail")


def download(url: str) -> bytes:
    clean = url.split("?")[0]
    req = urllib.request.Request(
        clean,
        headers={"User-Agent": UA, "Accept": "image/*", "Referer": "https://commons.wikimedia.org/"},
    )
    delay = 8.0
    for attempt in range(8):
        try:
            with urllib.request.urlopen(req, context=CTX, timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 7:
                w = delay + random.uniform(0, 2)
                log(f"    DL {e.code}, sleep {w:.1f}s")
                time.sleep(w)
                delay = min(delay * 1.7, 90)
                continue
            raise
    raise RuntimeError("dl fail")


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


def name_match(en: str, ko: str, text: str) -> bool:
    if REJECT.search(text):
        return False
    low = text.lower()
    en_l = en.lower()
    stem = re.sub(r"san$", "", en_l)
    if en_l and en_l in low:
        return True
    if stem and len(stem) >= 4 and stem in low:
        return True
    if ko and ko in text:
        return True
    return False


def wiki_thumb(lang: str, title: str) -> dict | None:
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
    data = http_json(f"{api}?{q}")
    for page in data.get("query", {}).get("pages", {}).values():
        if int(page.get("pageid", -1)) < 0:
            continue
        thumb = page.get("thumbnail") or {}
        src = thumb.get("source")
        if not src:
            continue
        pname = str(page.get("pageimage") or "")
        resolved = str(page.get("title") or title)
        if not name_match(title if lang == "en" else "", title if lang == "ko" else "", f"{pname} {resolved} {src}"):
            # for ko title search, match against ko title param separately below
            pass
        return {"url": src, "title": pname or resolved, "via": f"{lang}:{resolved}"}
    return None


def find_image(en: str, ko: str) -> dict | None:
    # 1) reuse map if present
    meta = MAP.get(en)  # wrong key
    return None


def commons_pick(en: str, ko: str) -> dict | None:
    api = "https://commons.wikimedia.org/w/api.php"
    # category first
    for cat in (f"Category:{en}", f"Category:{en} National Park"):
        q = urllib.parse.urlencode(
            {
                "action": "query",
                "list": "categorymembers",
                "cmtitle": cat,
                "cmnamespace": 6,
                "cmlimit": 10,
                "cmtype": "file",
                "format": "json",
            }
        )
        try:
            data = http_json(f"{api}?{q}")
        except Exception:
            data = {"query": {"categorymembers": []}}
        titles = [m["title"] for m in data.get("query", {}).get("categorymembers", [])]
        time.sleep(2)
        titles = [t for t in titles if name_match(en, ko, t)]
        if titles:
            return imageinfo_best(titles[:6], en, ko)

    # search
    for query in (f'"{en}" Korea', f"{en} mountain", ko):
        if not query:
            continue
        q = urllib.parse.urlencode(
            {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srnamespace": 6,
                "srlimit": 10,
                "format": "json",
            }
        )
        data = http_json(f"{api}?{q}")
        titles = [h["title"] for h in data.get("query", {}).get("search", [])]
        time.sleep(2)
        titles = [t for t in titles if name_match(en, ko, t)]
        if titles:
            return imageinfo_best(titles[:6], en, ko)
    return None


def imageinfo_best(titles: list[str], en: str, ko: str) -> dict | None:
    api = "https://commons.wikimedia.org/w/api.php"
    q = urllib.parse.urlencode(
        {
            "action": "query",
            "titles": "|".join(titles),
            "prop": "imageinfo",
            "iiprop": "url|size|mime",
            "iiurlwidth": 1280,
            "format": "json",
        }
    )
    data = http_json(f"{api}?{q}")
    time.sleep(1.5)
    best = None
    best_score = -1
    for page in data.get("query", {}).get("pages", {}).values():
        ii = (page.get("imageinfo") or [None])[0]
        if not ii:
            continue
        if ii.get("mime") not in ("image/jpeg", "image/png", "image/webp"):
            continue
        title = page.get("title") or ""
        if not name_match(en, ko, title):
            continue
        w = int(ii.get("thumbwidth") or ii.get("width") or 0)
        h = int(ii.get("thumbheight") or ii.get("height") or 0)
        if w < 400 or h < 250:
            continue
        url = ii.get("thumburl") or ii.get("url")
        score = w
        if ii.get("mime") == "image/jpeg":
            score += 100
        if score > best_score and url:
            best_score = score
            best = {"url": url, "title": title, "via": "commons"}
    return best


def pick(en: str, ko: str, slug: str) -> dict | None:
    # retry saved map
    if slug in MAP:
        m = MAP[slug]
        blob = f"{m.get('pageimage')} {m.get('resolved')} {m.get('url')}"
        if name_match(en, ko, blob) or (ko and ko in str(m.get("resolved") or "")):
            if not REJECT.search(blob):
                return {"url": m["url"], "title": m.get("pageimage"), "via": "map"}

    # wiki ko / en
    for lang, title in (("ko", ko), ("en", en), ("en", f"{en} (mountain)"), ("en", f"{en} National Park")):
        if not title:
            continue
        try:
            data_url = None
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
            data = http_json(f"{api}?{q}")
            time.sleep(2.5)
            for page in data.get("query", {}).get("pages", {}).values():
                if int(page.get("pageid", -1)) < 0:
                    continue
                thumb = page.get("thumbnail") or {}
                src = thumb.get("source")
                if not src:
                    continue
                pname = str(page.get("pageimage") or "")
                resolved = str(page.get("title") or "")
                blob = f"{pname} {resolved} {src}"
                if REJECT.search(blob):
                    continue
                # accept if resolved equals requested mountain page
                if ko and resolved == ko:
                    return {"url": src, "title": pname, "via": f"wiki-{lang}"}
                if en and resolved.lower().startswith(en.lower()):
                    return {"url": src, "title": pname, "via": f"wiki-{lang}"}
                if name_match(en, ko, blob):
                    return {"url": src, "title": pname, "via": f"wiki-{lang}"}
        except Exception as e:
            log(f"    wiki err: {e}")
            continue

    return commons_pick(en, ko)


def main():
    need = [p for p in SLUGS if is_fb(p["slug"])]
    log(f"Remaining fallbacks: {len(need)}")
    log("Cooldown 120s...")
    time.sleep(120)

    results = []
    for i, p in enumerate(need, 1):
        slug, en, ko = p["slug"], p["en"], p["ko"]
        dest = OUT / f"{slug}.jpg"
        log(f"[{i}/{len(need)}] {slug} ({en}/{ko})")
        if not is_fb(slug):
            log("  already filled")
            results.append({"slug": slug, "ok": True, "kept": True})
            continue
        try:
            picked = pick(en, ko, slug)
            if not picked:
                raise RuntimeError("no candidate")
            raw = download(picked["url"])
            if len(raw) < 10000:
                raise RuntimeError(f"small {len(raw)}")
            n = to_jpeg(raw, dest)
            if md5(dest) == FB:
                raise RuntimeError("fallback")
            log(f"  OK {n} <- {picked.get('title')} [{picked.get('via')}]")
            results.append({"slug": slug, "ok": True, "kept": False, **picked})
        except Exception as e:
            log(f"  FAIL: {e}")
            results.append({"slug": slug, "ok": False, "error": str(e)})
        LOG.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        time.sleep(4.0 + random.uniform(0.5, 2.0))

    unique = sum(1 for p in SLUGS if not is_fb(p["slug"]))
    remain = [p["slug"] for p in SLUGS if is_fb(p["slug"])]
    failed = [r["slug"] for r in results if not r.get("ok")]
    replaced = [r["slug"] for r in results if r.get("ok") and not r.get("kept")]
    log(f"\nDONE unique={unique} remain={len(remain)} replaced={len(replaced)} failed={len(failed)}")
    log("REMAIN: " + ", ".join(remain))
    log("FAILED: " + ", ".join(failed))


if __name__ == "__main__":
    main()
