# -*- coding: utf-8 -*-
"""Pass5: batch Wikipedia pageimages + thumb downloads for remaining mountains."""
from __future__ import annotations

import hashlib
import io
import json
import random
import ssl
import time
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
SLUGS = json.loads((ROOT / "tool" / "_mountain_slugs.json").read_text(encoding="utf-8"))
UA = "KoreaTravelGuidebook/1.0 (educational static site)"
CTX = ssl._create_unverified_context()


def log(*a):
    print(*a, flush=True)


def is_fb(s: str) -> bool:
    p = OUT / f"{s}.jpg"
    return (not p.exists()) or hashlib.md5(p.read_bytes()).hexdigest() == FB


def batch(lang: str, titles: list[str]) -> dict:
    api = f"https://{lang}.wikipedia.org/w/api.php"
    out: dict = {}
    for i in range(0, len(titles), 20):
        chunk = [t for t in titles[i : i + 20] if t]
        q = urllib.parse.urlencode(
            {
                "action": "query",
                "titles": "|".join(chunk),
                "prop": "pageimages",
                "format": "json",
                "pithumbsize": 1280,
                "pilicense": "any",
                "redirects": 1,
            }
        )
        req = urllib.request.Request(f"{api}?{q}", headers={"User-Agent": UA})
        data = None
        for attempt in range(6):
            try:
                with urllib.request.urlopen(req, context=CTX, timeout=90) as r:
                    data = json.loads(r.read().decode())
                break
            except Exception as e:
                log(f"  batch err {e}")
                time.sleep(20 + attempt * 10)
        if not data:
            continue
        redir = {r["from"]: r["to"] for r in data.get("query", {}).get("redirects", []) or []}
        norm = {n["from"]: n["to"] for n in data.get("query", {}).get("normalized", []) or []}
        pages = {
            p.get("title"): p
            for p in data.get("query", {}).get("pages", {}).values()
            if int(p.get("pageid", -1)) > 0
        }

        def resolve(t: str) -> str:
            t = norm.get(t, t)
            seen = set()
            while t in redir and t not in seen:
                seen.add(t)
                t = redir[t]
            return t

        for orig in chunk:
            page = pages.get(resolve(orig))
            if not page:
                continue
            thumb = page.get("thumbnail") or {}
            src = thumb.get("source")
            if not src:
                continue
            out[orig] = {
                "url": src,
                "pageimage": page.get("pageimage"),
                "resolved": page.get("title"),
            }
        log(f"  {lang} chunk {i // 20 + 1} mapped {len(out)}")
        time.sleep(8)
    return out


def dl(url: str) -> bytes:
    req = urllib.request.Request(
        url.split("?")[0],
        headers={
            "User-Agent": UA,
            "Accept": "image/*",
            "Referer": "https://commons.wikimedia.org/",
        },
    )
    with urllib.request.urlopen(req, context=CTX, timeout=120) as r:
        return r.read()


def to_jpg(data: bytes, dest: Path) -> int:
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
    need = [p for p in SLUGS if is_fb(p["slug"])]
    log(f"need {len(need)}")
    log("Cooldown 30s...")
    time.sleep(30)

    ko_map = batch("ko", [p["ko"] for p in need])
    time.sleep(10)
    en_map = batch("en", [p["en"] for p in need])

    by_slug = {}
    for p in need:
        slug, ko, en = p["slug"], p["ko"], p["en"]
        meta = None
        if ko in ko_map:
            meta = ko_map[ko]
        elif en in en_map:
            meta = en_map[en]
        if not meta:
            continue
        blob = f"{meta.get('pageimage')} {meta.get('resolved')} {meta.get('url')}".lower()
        if any(x in blob for x in ("coral", "county", "disambiguation")):
            continue
        by_slug[slug] = meta

    log(f"candidates {len(by_slug)}: {list(by_slug)}")
    (ROOT / "tool" / "_mountain_pass5_map.json").write_text(
        json.dumps(by_slug, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    ok = fail = 0
    for i, (slug, meta) in enumerate(by_slug.items(), 1):
        log(f"[{i}/{len(by_slug)}] {slug}")
        try:
            raw = dl(meta["url"])
            if len(raw) < 8000:
                raise RuntimeError(f"small {len(raw)}")
            n = to_jpg(raw, OUT / f"{slug}.jpg")
            log(f"  OK {n} <- {meta.get('pageimage')}")
            ok += 1
        except Exception as e:
            log(f"  FAIL {e}")
            fail += 1
        time.sleep(10 + random.uniform(1, 3))

    unique = sum(1 for p in SLUGS if not is_fb(p["slug"]))
    remain = [p["slug"] for p in SLUGS if is_fb(p["slug"])]
    log(f"DONE unique={unique} remain={len(remain)} dl_ok={ok} dl_fail={fail}")
    log("REMAIN: " + ", ".join(remain))


if __name__ == "__main__":
    main()
