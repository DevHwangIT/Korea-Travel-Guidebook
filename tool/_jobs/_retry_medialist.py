# -*- coding: utf-8 -*-
"""Slow media-list + FilePath fill. 18s between Wikipedia REST calls."""
from __future__ import annotations

import importlib.util
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "fill_ph", ROOT / "tool" / "_fill_placeholder_photos.py"
)
fill = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fill)

SLEEP = 18.0
UA = "KoreaTravelGuidebook/1.0 (place covers; educational; slow media-list)"

KNOWN = {
    "gatjin-dasanchodat": "Dasanchodang_(茶山草堂)_-_panoramio.jpg",
    "jeonnal-gatjin-dasanchodat": "Dasanchodang_(茶山草堂)_-_panoramio.jpg",
    "gukrimasiamunhwajeondat": "ACC 하늘마당.jpg",
    "gwatju-gukrimasiamunhwajeondat": "ACC 하늘마당.jpg",
}


def filepath(name: str) -> str:
    return (
        "https://commons.wikimedia.org/wiki/Special:FilePath/"
        + urllib.parse.quote(name)
        + "?width=800"
    )


def media_list(title: str) -> list[str]:
    url = "https://ko.wikipedia.org/api/rest_v1/page/media-list/" + urllib.parse.quote(
        title
    )
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=40, context=fill.ssl_ctx()) as r:
            data = json.loads(r.read().decode())
    except urllib.error.HTTPError as exc:
        if exc.code in (429, 503):
            print(f"  REST {exc.code}, wait 45s", flush=True)
            time.sleep(45)
            return []
        if exc.code == 404:
            return []
        print(f"  REST err {exc}", flush=True)
        return []
    except Exception as exc:  # noqa: BLE001
        print(f"  REST err {exc}", flush=True)
        return []
    out = []
    for it in data.get("items") or []:
        if it.get("type") != "image":
            continue
        t = fill.strip_file_prefix(it.get("title") or "")
        if not t or fill.bad_filename(t) or fill.is_generic_file(t):
            continue
        low = t.lower()
        if not any(low.endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".webp")):
            continue
        out.append(t)
    return out


def titles_for(place: dict, ko_names: dict[str, str]) -> list[str]:
    ko = ko_names.get(place["slug"], "")
    stripped = re.sub(r"\s*\([^)]*\)\s*", " ", ko).strip() if ko else ""
    out = []
    for t in (stripped, ko):
        if t and t not in out:
            out.append(t)
    return out[:2]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    hashes = fill.type_hashes()
    ko_names = fill.load_ko_names()
    places = fill.parse_places()

    # Known files first (no Wikipedia REST)
    for slug, fname in KNOWN.items():
        if fill.is_placeholder(slug, hashes) or slug.startswith("gukrim"):
            print(f"known {slug} {fname}", flush=True)
            time.sleep(2.5)
            fill.try_save(
                filepath(fname), fill.dest_path(slug), hashes, f"known:{fname}"
            )

    need = [p for p in places if fill.is_placeholder(p["slug"], hashes)]
    groups = fill.group_places(need, ko_names)
    print(f"need={len(need)} groups={len(groups)}", flush=True)

    ok = miss = 0
    for i, g in enumerate(groups, 1):
        p = g[0]
        slug = p["slug"]
        dest = fill.dest_path(slug)
        print(f"\n[{i}/{len(groups)}] {slug} {ko_names.get(slug, p['note'])}", flush=True)
        saved = False
        for title in titles_for(p, ko_names):
            print(f"  media-list {title}", flush=True)
            time.sleep(SLEEP)
            files = media_list(title)
            for fname in files[:2]:
                print(f"  file {fname}", flush=True)
                time.sleep(2.5)
                if fill.try_save(filepath(fname), dest, hashes, f"ml:{fname}"):
                    saved = True
                    break
            if saved:
                break
        if saved:
            ok += 1
            for other in g[1:]:
                fill.copy_to(slug, other["slug"])
                print(f"  COPY -> {other['slug']}", flush=True)
        else:
            miss += 1
            print("  MISS", flush=True)

    remain = sum(1 for x in fill.parse_places() if fill.is_placeholder(x["slug"], hashes))
    print(f"\nDONE ok={ok} miss={miss} remaining={remain}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
