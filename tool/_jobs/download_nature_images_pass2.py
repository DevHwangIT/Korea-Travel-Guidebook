# -*- coding: utf-8 -*-
"""Fill remaining nature fallbacks using direct Commons upload URLs only.

No MediaWiki API in the happy path (avoids 429). Verified File titles only.
"""
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

# Only titles confirmed or highly likely on Commons (category / search results).
VERIFIED: dict[str, list[str]] = {
    "igidae-coastal-trail": [
        "View of Haeundae from Igidae Coastal Trail.jpg",
    ],
    "oryukdo": [
        "Oryukdo, Busan, South Korea 01.jpg",
        "Oryukdo Skywalk in Busan, South Korea.jpg",
        "Oryukdo, Busan, South Korea 02.jpg",
    ],
    "taejongdae": [
        "Taejongdae in Busan, South Korea.jpg",
        "Cliffs of Taejongdae 1.jpg",
        "Korea-Busan-Taejongdae-01.jpg",
        "Taejongdae.jpg",
    ],
    "eulsukdo": [
        "Eulsukdo.jpg",
        "을숙도.jpg",
        "Nakdonggang Estuary.jpg",
        "Nakdong River estuary.jpg",
    ],
    "dadaepo-nature": [
        "Dadaepo Beach.jpg",
        "다대포해수욕장.jpg",
        "Dadaepo Beach Busan.jpg",
        "Sunset at Dadaepo Beach.jpg",
    ],
    "sorae-wetland": [
        "20250830 Sorae Photowalk Jjw 015.jpg",
        "20250830 Sorae Photowalk Jjw 016.jpg",
    ],
    "incheon-grand-park": [
        "인천대공원.JPG",
        "인천대공원 2.JPG",
    ],
    "muui-do": [
        "Muuido Island from Ferry Dock.jpg",
        "Cabana at Hanagae Beach, Muuido.jpg",
    ],
    "yeongjong-do": [
        "Yeongjongdo of west sea of South Korea.jpg",
    ],
    "ganghwa-do": [
        "Natural Scenery in Ganghwa Island 6.jpg",
        "Natural Scenery in Ganghwa Island 1.jpg",
        "Ganghwa1.jpg",
    ],
    "baengnyeong-do": [
        "Baengnyeongdo.jpg",
        "백령도.jpg",
        "Baengnyeong Island.jpg",
        "Baengnyeongdo Island.jpg",
    ],
    "suseong-mot": [
        "Suseongmot.jpg",
        "수성못.jpg",
        "Suseong Lake.jpg",
        "Suseongmot Lake.jpg",
    ],
    "dalseong-wetland": [
        "달성습지.jpg",
        "Dalseong Wetland.jpg",
        "Dalseong wetland ecological park.jpg",
    ],
    "duryu-park": [
        "Duryu Park.jpg",
        "두류공원.jpg",
        "Duryusan.jpg",
    ],
    "odongdo": [
        "Dongbaek Habitat of Odongdo in 2017.jpg",
        "Baramgol of Odongdo in 2017.jpg",
        "Odongdo.jpg",
        "오동도.jpg",
    ],
    "dolsando": [
        "Dolsan Bridge.jpg",
        "Dolsan Bridge at night.jpg",
        "돌산대교.jpg",
        "Yeosu Dolsan Bridge.jpg",
    ],
    "geumodo": [
        "Geumodo.jpg",
        "금오도.jpg",
        "Geumo-do.jpg",
    ],
    "geomundo": [
        "Geomundo.jpg",
        "거문도.jpg",
        "Geomun-do.jpg",
    ],
    "baekdo": [
        "Baekdo.jpg",
        "백도.jpg",
        "Yeosu Baekdo.jpg",
    ],
    "yeojaman": [
        "Yeoja Bay.jpg",
        "여자만.jpg",
        "Suncheonman Bay.jpg",
    ],
    "yeosu-jangdo": [
        "Jangdo Yeosu.jpg",
        "장도.jpg",
        "Yeosu Jangdo.jpg",
    ],
    "udo": [
        "Udo Island.jpg",
        "Udo (Jeju).jpg",
        "우도.jpg",
        "Udo Jeju.jpg",
        "Jeju Udo Island.jpg",
    ],
    "jusangjeolli": [
        "Daepo Jusangjeolli Cliff 01.jpg",
        "Daepo Jusangjeolli Cliff 20160616 083106.jpg",
        "주상절리대.jpg",
    ],
    "bijarim": [
        "Bijarim Forest.jpg",
        "비자림.jpg",
        "Bijarim.jpg",
        "Bija Forest.jpg",
    ],
    "saryeoni-forest": [
        "Saryeoni Forest Path.jpg",
        "사려니숲길.jpg",
        "Saryeoni Forest.jpg",
        "Saryeoni Forest Trail.jpg",
    ],
    "gotjawal": [
        "Gotjawal.jpg",
        "곶자왈.jpg",
        "Gotjawal Forest.jpg",
        "Jeju Gotjawal Forest.jpg",
    ],
    "seopjikoji": [
        "Seopjikoji.jpg",
        "섭지코지.jpg",
        "Seopjiokji Coastline.jpg",
    ],
    "sangumburi": [
        "Sangumburi.jpg",
        "산굼부리.jpg",
        "Sangumburi Crater.jpg",
    ],
    "jeongbang-falls": [
        "Jeongbang Falls.jpg",
        "정방폭포.jpg",
        "Jeongbang Waterfall.jpg",
        "Jeongbangpokpo.jpg",
    ],
    "soesoggak": [
        "Soesokkak.jpg",
        "쇠소깍.jpg",
        "Soesokkak Jeju.jpg",
    ],
    "yongmeori-coast": [
        "Yongmeori Coast.jpg",
        "용머리해안.jpg",
        "Yongmeori.jpg",
        "Yongduam.jpg",
    ],
    "manjanggul": [
        "Jeju Manjanggul.jpg",
        "Manjanggul in Jeju.jpg",
        "Jeju LavaTube.JPG",
        "Manjanggul lava column, largest in the world.jpg",
        "만장굴.jpg",
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


def http_get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx()) as r:
        return r.read()


def direct_urls(title: str, width: int = 1280) -> list[str]:
    name = title.replace(" ", "_")
    digest = hashlib.md5(name.encode("utf-8")).hexdigest()
    a, ab = digest[0], digest[:2]
    q = urllib.parse.quote(name, safe="()-_,.'!")
    return [
        f"https://upload.wikimedia.org/wikipedia/commons/thumb/{a}/{ab}/{q}/{width}px-{q}",
        f"https://upload.wikimedia.org/wikipedia/commons/{a}/{ab}/{q}",
    ]


def try_save(url: str, dest: Path) -> str | None:
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


def fallback_slugs(fb_hash: str) -> list[str]:
    out = []
    for line in COORDS.read_text(encoding="utf-8").splitlines():
        if 'type: "nature"' not in line:
            continue
        m = re.search(r'slug:\s*"([^"]+)"', line)
        if not m:
            continue
        slug = m.group(1)
        p = IMG / f"{slug}.jpg"
        if (not p.exists()) or md5_file(p) == fb_hash:
            out.append(slug)
    return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    fb_hash = md5_file(TYPE_FALLBACK)
    targets = fallback_slugs(fb_hash)
    print(f"Remaining fallbacks: {len(targets)}", flush=True)

    replaced: list[str] = []
    still: list[str] = []
    used: set[str] = set()

    for i, slug in enumerate(targets):
        dest = IMG / f"{slug}.jpg"
        titles = VERIFIED.get(slug, [])
        print(f"\n[{i+1}/{len(targets)}] {slug} ({len(titles)} titles)", flush=True)
        ok = False
        for title in titles:
            print(f"  TRY {title}", flush=True)
            time.sleep(3.5)  # rate limit
            for url in direct_urls(title):
                err = try_save(url, dest)
                if err == "http:404":
                    continue
                if err == "http:429":
                    print("  429 — sleep 90s", flush=True)
                    time.sleep(90)
                    err = try_save(url, dest)
                if err:
                    print(f"  {err}", flush=True)
                    continue
                h = md5_file(dest)
                if h == fb_hash or h in used:
                    dest.write_bytes(TYPE_FALLBACK.read_bytes())
                    print("  dup/fallback hash", flush=True)
                    continue
                used.add(h)
                print(f"  OK {dest.stat().st_size}", flush=True)
                ok = True
                break
            if ok:
                break
            time.sleep(2.0)
        if ok:
            replaced.append(slug)
        else:
            still.append(slug)
            print("  STILL FALLBACK", flush=True)
        time.sleep(4.0)

    print("\n=== PASS SUMMARY ===", flush=True)
    print(f"replaced ({len(replaced)}): {', '.join(replaced)}", flush=True)
    print(f"still ({len(still)}): {', '.join(still)}", flush=True)
    (ROOT / "tool" / "_nature_image_report.txt").write_text(
        "replaced_this_pass:\n"
        + "\n".join(replaced)
        + "\n\nstill_fallback:\n"
        + "\n".join(still)
        + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
