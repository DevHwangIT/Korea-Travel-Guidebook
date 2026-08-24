# -*- coding: utf-8 -*-
"""Fetch remaining Seoul course photos via Wikipedia REST thumbnails (slower, less 429)."""
from __future__ import annotations

import json
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "Images" / "places"
UA = "KoreaTravelGuidebook/1.0 (course thumbs; educational; contact noc if needed)"
SLEEP = 8.0

# slug -> list of (lang, wiki title)
PAGES: dict[str, list[tuple[str, str]]] = {
    "national-museum-korea": [
        ("en", "National Museum of Korea"),
        ("ko", "국립중앙박물관"),
    ],
    "daehangno": [
        ("en", "Daehangno"),
        ("ko", "대학로 (서울)"),
        ("en", "Marronnier Park"),
    ],
    "sebit-seom": [
        ("en", "Some Sevit"),
        ("ko", "세빛섬"),
    ],
    "dosan-park": [
        ("en", "Dosan Park"),
        ("ko", "도산공원"),
    ],
    "euljiro": [
        ("en", "Euljiro"),
        ("ko", "을지로"),
    ],
    "ssamziegil": [
        ("en", "Insadong"),
        ("ko", "쌈지길"),
        ("ko", "인사동"),
    ],
    "seochon": [
        ("en", "Seochon"),
        ("ko", "서촌"),
    ],
    "mangwon-hangang": [
        ("ko", "망원한강공원"),
        ("en", "Hangang Park"),
        ("ko", "한강공원"),
    ],
    "jamsil-skyline": [
        ("en", "Lotte World Tower"),
        ("ko", "롯데월드타워"),
    ],
    "the-hyundai-seoul": [
        ("ko", "더현대 서울"),
        ("en", "Yeouido"),
    ],
    "bukjeong-village": [
        ("ko", "성북동"),
        ("en", "Seongbuk-dong"),
    ],
    "seongbuk-dong": [
        ("ko", "성북동"),
        ("en", "Seongbuk-dong"),
    ],
}

CTX = None


def ssl_ctx():
    global CTX
    if CTX is None:
        try:
            import certifi

            CTX = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            CTX = ssl._create_unverified_context()
    return CTX


def http_get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx()) as r:
        return r.read()


def wiki_thumb(lang: str, title: str) -> str | None:
    api = (
        f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/"
        + urllib.parse.quote(title.replace(" ", "_"))
    )
    try:
        data = json.loads(http_get(api).decode())
    except Exception as exc:  # noqa: BLE001
        print(f"  miss {lang}:{title} ({exc})", flush=True)
        return None
    if data.get("type") == "disambiguation":
        return None
    for key in ("originalimage", "thumbnail"):
        src = (data.get(key) or {}).get("source")
        if src:
            # bump width if thumb
            if "/thumb/" in src and "/" in src.rsplit("/", 1)[-1]:
                # leave as-is; often 320px — try replace px
                import re

                src2 = re.sub(r"/\d+px-", "/1280px-", src)
                return src2
            return src
    return None


def save(url: str, dest: Path) -> bool:
    try:
        data = http_get(url, timeout=90)
    except Exception as exc:  # noqa: BLE001
        print(f"  dl err: {exc}", flush=True)
        return False
    if len(data) < 8000:
        print(f"  small {len(data)}", flush=True)
        return False
    if not (
        data[:3] == b"\xff\xd8\xff"
        or data[:8] == b"\x89PNG\r\n\x1a\n"
        or data[:4] == b"RIFF"
    ):
        print("  bad magic", flush=True)
        return False
    dest.write_bytes(data)
    return True


def main() -> int:
    ok = fail = 0
    for slug, pages in PAGES.items():
        dest = IMG / f"{slug}.jpg"
        if dest.exists() and dest.stat().st_size > 15000:
            print(f"= {slug} exists", flush=True)
            ok += 1
            continue
        print(f"\n## {slug}", flush=True)
        got = False
        for lang, title in pages:
            url = wiki_thumb(lang, title)
            time.sleep(2)
            if not url:
                continue
            print(f"  try {lang}:{title} -> {url[:90]}...", flush=True)
            if save(url, dest):
                print(f"+ {slug} ({dest.stat().st_size})", flush=True)
                got = True
                break
            time.sleep(3)
        if got:
            ok += 1
        else:
            fail += 1
            print(f"! FAIL {slug}", flush=True)
        time.sleep(SLEEP)
    print(f"\ndone ok={ok} fail={fail}", flush=True)
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
