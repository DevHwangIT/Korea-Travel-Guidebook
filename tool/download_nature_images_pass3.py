# -*- coding: utf-8 -*-
"""Pass 3: remaining nature fallbacks — verified Commons titles, direct URLs only."""
from __future__ import annotations

import hashlib
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "Images" / "places"
TYPE_FALLBACK = IMG / "_types" / "nature.jpg"
COORDS = ROOT / "data" / "places" / "places-coords.js"
UA = "KoreaTravelGuidebook/1.0 (nature covers; educational)"
CTX = None

# Exact File: titles confirmed via Commons category / file pages.
TITLES: dict[str, list[str]] = {
    "dadaepo-nature": [
        "Dadaepo Beach, Busan, Korea.jpg",
        "Sunset at Daedapo Beach.jpg",
        "대한민국 부산 다대포 해변 Dadaepo beach.Busan.South korea 1.jpg",
    ],
    "yeongjong-do": [
        "Yeongjongdo of west sea of South Korea.jpg",
    ],
    "baengnyeong-do": [
        "KOCIS Korea Island Baengnyeongdo01 (9265013277).jpg",
        "Sand Beach at Sagot Cape on Baengnyeongdo Island.jpg",
        "Kongdol Pebble Beach in Nampo-ri, Baengnyeongdo Island.jpg",
        "Encykorea-옹진 백령도 두무진 기암.jpg",
    ],
    "udo": [
        "Udo, Jeju Province, South Korea 01.jpg",
        "Udo Bong Scenery.jpg",
        "우도 풍경.jpg",
        "제주 우도 Jeju Udo.jpg",
    ],
    "jusangjeolli": [
        "Daepo Jusangjeolli Cliff 01.jpg",
        "Daepo Jusangjeolli Cliff 20160616 083106.jpg",
    ],
    "bijarim": [
        "Bijarim nutmeg forest jeju korea 6.jpg",
    ],
    "gotjawal": [
        "Gotjawal Forest.jpg",
    ],
    "seopjikoji": [
        "Seopjikoji.jpg",
        "Seopjiokji Coastline.jpg",
    ],
    "sangumburi": [
        "Silver Grass, Sangumburi, Jeju (억새, 제주 산굼부리) - panoramio.jpg",
        "Silver Grass, Sangumburi, Jeju (억새, 제주 산굼부리) - panoramio (1).jpg",
    ],
    "jeongbang-falls": [
        "Jeongbang Falls.jpg",
        "Jeongbang 1 Jeju Island 제주도.jpg",
        "정방폭포 (1).jpg",
    ],
    "yongmeori-coast": [
        "Yongmeori Coast.jpg",
    ],
    "manjanggul": [
        "Jeju Manjanggul.jpg",
        "Manjanggul in Jeju.jpg",
        "Jeju LavaTube.JPG",
        "Manjanggul lava column, largest in the world.jpg",
    ],
    # Best-effort extras (may stay fallback if no Commons hit)
    "saryeoni-forest": [
        "Saryeoni Forest Path.jpg",
        "사려니숲길.jpg",
        "Saryoni Forest Trail.jpg",
    ],
    "soesoggak": [
        "Soesokkak.jpg",
        "쇠소깍.jpg",
        "Soesokkak estuary.jpg",
    ],
    "dalseong-wetland": [
        "달성습지.jpg",
        "Dalseong Wetland Ecological Park.jpg",
    ],
    "geumodo": [
        "Geumo Island Yeosu.jpg",
        "금오도.jpg",
        "Geumodo Yeosu.jpg",
    ],
    "geomundo": [
        "Geomundo Island.jpg",
        "거문도.jpg",
        "Geomun Island Yeosu.jpg",
    ],
    "baekdo": [
        "Yeosu Baekdo islets.jpg",
        "백도 여수.jpg",
    ],
    "yeojaman": [
        "Yeoja Bay Yeosu.jpg",
        "여자만.jpg",
    ],
    "yeosu-jangdo": [
        "Yeosu Jangdo.jpg",
        "장도 여수.jpg",
    ],
}


def ssl_ctx() -> ssl.SSLContext:
    global CTX
    if CTX is None:
        try:
            import certifi

            CTX = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            CTX = ssl._create_unverified_context()
    return CTX


def md5_file(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def http_get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=70, context=ssl_ctx()) as r:
        return r.read()


def urls_for(title: str, width: int = 1280) -> list[str]:
    name = title.replace(" ", "_")
    d = hashlib.md5(name.encode("utf-8")).hexdigest()
    q = urllib.parse.quote(name, safe="()-_,.'!")
    return [
        f"https://upload.wikimedia.org/wikipedia/commons/thumb/{d[0]}/{d[:2]}/{q}/{width}px-{q}",
        f"https://upload.wikimedia.org/wikipedia/commons/{d[0]}/{d[:2]}/{q}",
    ]


def fetch(url: str, dest: Path) -> str | None:
    try:
        data = http_get(url)
    except urllib.error.HTTPError as e:
        return f"http:{e.code}"
    except Exception as e:  # noqa: BLE001
        return f"err:{e}"
    if len(data) < 12000:
        return "small"
    if data[:4] == b"%PDF" or data[:1] == b"<":
        return "bad"
    if not (data[:3] == b"\xff\xd8\xff" or data[:8] == b"\x89PNG\r\n\x1a\n"):
        return "fmt"
    dest.write_bytes(data)
    return None


def remaining(fb: str) -> list[str]:
    out = []
    for line in COORDS.read_text(encoding="utf-8").splitlines():
        if 'type: "nature"' not in line:
            continue
        m = re.search(r'slug:\s*"([^"]+)"', line)
        if not m:
            continue
        slug = m.group(1)
        p = IMG / f"{slug}.jpg"
        if (not p.exists()) or md5_file(p) == fb:
            out.append(slug)
    return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    fb = md5_file(TYPE_FALLBACK)
    targets = remaining(fb)
    print(f"Pass3 remaining: {len(targets)}", flush=True)
    print("Cooldown 120s before start…", flush=True)
    time.sleep(120)

    replaced: list[str] = []
    still: list[str] = []
    used: set[str] = set()
    rate_hits = 0

    for i, slug in enumerate(targets):
        dest = IMG / f"{slug}.jpg"
        titles = TITLES.get(slug, [])
        print(f"\n[{i+1}/{len(targets)}] {slug}", flush=True)
        ok = False
        for title in titles:
            print(f"  TRY {title}", flush=True)
            time.sleep(5.0)
            for url in urls_for(title):
                err = fetch(url, dest)
                if err == "http:404":
                    continue
                if err == "http:429":
                    rate_hits += 1
                    wait = min(300, 120 + rate_hits * 30)
                    print(f"  429 — global pause {wait}s", flush=True)
                    time.sleep(wait)
                    err = fetch(url, dest)
                if err:
                    print(f"  {err}", flush=True)
                    continue
                h = md5_file(dest)
                if h == fb or h in used:
                    dest.write_bytes(TYPE_FALLBACK.read_bytes())
                    print("  skip hash", flush=True)
                    continue
                used.add(h)
                print(f"  OK {dest.stat().st_size}", flush=True)
                ok = True
                rate_hits = max(0, rate_hits - 1)
                break
            if ok:
                break
        if ok:
            replaced.append(slug)
        else:
            still.append(slug)
            print("  STILL FALLBACK", flush=True)
        time.sleep(6.0)

    print("\n=== PASS3 SUMMARY ===", flush=True)
    print(f"replaced ({len(replaced)}): {', '.join(replaced)}", flush=True)
    print(f"still ({len(still)}): {', '.join(still)}", flush=True)
    (ROOT / "tool" / "_nature_image_report.txt").write_text(
        "pass3_replaced:\n"
        + "\n".join(replaced)
        + "\n\nstill_fallback:\n"
        + "\n".join(still)
        + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
