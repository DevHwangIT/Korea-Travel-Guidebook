# -*- coding: utf-8 -*-
"""Download unique nature/outdoor place covers from Wikimedia Commons.

Uses direct upload.wikimedia.org URLs (MD5 path) first to avoid API 429s.
Falls back to MediaWiki API search with exponential backoff when needed.
"""
from __future__ import annotations

import hashlib
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
IMG = ROOT / "Images" / "places"
TYPE_FALLBACK = IMG / "_types" / "nature.jpg"
COORDS = ROOT / "data" / "places" / "places-coords.js"
UA = "KoreaTravelGuidebook/1.0 (nature covers; educational; contact: local guidebook)"
CTX = None

# Curated Commons File titles — verified / high-probability real photos.
NATURE_FILES: dict[str, list[str]] = {
    "seoul-forest": [
        "Seoul Forest seen from Dongho Bridge.jpg",
        "Seoul Forest 서울숲.jpg",
        "Seoul Forest in May 2022 (1).jpg",
        "Seoulforest path01.jpg",
        "Seoulforest lake01.jpg",
    ],
    "bukseoul-kkumui-forest": [
        "North Seoul dream forest.jpg",
        "북서울꿈의숲 아트센터, 전망대.JPG",
        "Dream Forest Park.jpg",
    ],
    "cheonggyecheon": [
        "Cheonggyecheon Seoul 1.jpg",
        "20240413 Cheonggyecheon.jpg",
        "Cheonggyecheon stream at sunrise with trees in Seoul.jpg",
        "Cheonggyecheon stream with flowers and bridge at sunrise near Cheonggye Plaza in Seoul.jpg",
        "Seoul-Cheonggyecheon-01.jpg",
        "KOCIS Korea Cheonggyecheon 2013 01 (10988752943).jpg",
    ],
    "naksan-park": [
        "Naksan Park, Seoul, South Korea 15.jpg",
        "Naksan Park, Seoul, South Korea 12.jpg",
        "Naksan Park, Seoul, South Korea 02.jpg",
    ],
    "seoul-botanic-park": [
        "서울식물원.jpg",
        "Seoul Botanic Park.jpg",
        "Seoul Botanical Garden Magok.jpg",
    ],
    "olympic-park": [
        "World Peace Gate.jpg",
        "Seoul Olympic Park World Peace Gate.jpg",
        "Olympic Park Seoul.jpg",
        "Korea-Seoul-Olympic Park-01.jpg",
    ],
    "taejongdae": [
        "Taejongdae.jpg",
        "Taejongdae Busan South Korea.jpg",
        "Busan Taejongdae Park.jpg",
        "태종대.jpg",
    ],
    "oryukdo": [
        "Oryukdo islands.jpg",
        "Oryuk-do.jpg",
        "오륙도.jpg",
        "Oryukdo Busan.jpg",
    ],
    "igidae-coastal-trail": [
        "Igidae.jpg",
        "Igidae Park.jpg",
        "이기대.jpg",
        "Busan Igidae.jpg",
    ],
    "eulsukdo": [
        "Eulsukdo.jpg",
        "을숙도.jpg",
        "Eulsuk Island.jpg",
    ],
    "dadaepo-nature": [
        "Dadaepo Beach.jpg",
        "Dadaepo Sunset Festival.jpg",
        "다대포.jpg",
        "Dadaepo Beach Busan.jpg",
    ],
    "sorae-wetland": [
        "20250830 Sorae Photowalk Jjw 015.jpg",
        "20250830 Sorae Photowalk Jjw 016.jpg",
        "소래습지생태공원.jpg",
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
        "Paddy in Ganghwa Island 1.jpg",
    ],
    "baengnyeong-do": [
        "Baengnyeongdo.jpg",
        "백령도.jpg",
        "Baengnyeong Island.jpg",
    ],
    "suseong-mot": [
        "Suseongmot.jpg",
        "Suseong Lake.jpg",
        "수성못.jpg",
    ],
    "dalseong-wetland": [
        "달성습지.jpg",
        "Dalseong Wetland.jpg",
    ],
    "duryu-park": [
        "Duryu Park.jpg",
        "두류공원.jpg",
    ],
    "odongdo": [
        "Odongdo.jpg",
        "오동도.jpg",
        "Odongdo Island Yeosu.jpg",
    ],
    "dolsando": [
        "Dolsan Bridge.jpg",
        "Dolsan Bridge Yeosu.jpg",
        "돌산대교.jpg",
    ],
    "geumodo": [
        "Geumodo.jpg",
        "금오도.jpg",
    ],
    "geomundo": [
        "Geomundo.jpg",
        "거문도.jpg",
    ],
    "baekdo": [
        "Baekdo.jpg",
        "여수백도.jpg",
    ],
    "yeojaman": [
        "Yeoja Bay.jpg",
        "여자만.jpg",
    ],
    "yeosu-jangdo": [
        "Jangdo Yeosu.jpg",
        "여수장도.jpg",
    ],
    "udo": [
        "Udo Island Jeju.jpg",
        "Udo (Jeju).jpg",
        "우도 제주.jpg",
        "Udo Island.jpg",
    ],
    "jusangjeolli": [
        "Jusangjeollidae.jpg",
        "주상절리대.jpg",
        "Columnar Joints Jeju.jpg",
        "Jungmun Jusangjeolli.jpg",
    ],
    "bijarim": [
        "Bijarim Forest.jpg",
        "비자림.jpg",
        "Bijarim.jpg",
    ],
    "saryeoni-forest": [
        "Saryeoni Forest Path.jpg",
        "사려니숲길.jpg",
        "Saryeoni Forest.jpg",
    ],
    "gotjawal": [
        "Gotjawal.jpg",
        "곶자왈.jpg",
        "Gotjawal Forest.jpg",
    ],
    "seopjikoji": [
        "Seopjikoji.jpg",
        "섭지코지.jpg",
        "Seopjikoji Jeju.jpg",
    ],
    "sangumburi": [
        "Sangumburi.jpg",
        "산굼부리.jpg",
    ],
    "jeongbang-falls": [
        "Jeongbang Falls.jpg",
        "정방폭포.jpg",
        "Jeongbang Waterfall.jpg",
    ],
    "soesoggak": [
        "Soesokkak.jpg",
        "쇠소깍.jpg",
    ],
    "yongmeori-coast": [
        "Yongmeori Coast.jpg",
        "용머리해안.jpg",
        "Yongmeori.jpg",
    ],
    "manjanggul": [
        "Manjanggul.jpg",
        "만장굴.jpg",
        "Manjanggul Cave.jpg",
    ],
}

SEARCH_QUERIES: dict[str, str] = {
    "seoul-forest": "Seoul Forest park filetype:bitmap",
    "bukseoul-kkumui-forest": "North Seoul Dream Forest OR 북서울꿈의숲",
    "cheonggyecheon": "Cheonggyecheon stream",
    "naksan-park": "Naksan Park Seoul",
    "seoul-botanic-park": "서울식물원 OR Seoul Botanic Park Magok",
    "olympic-park": "Olympic Park Seoul Peace Gate",
    "taejongdae": "Taejongdae Busan",
    "oryukdo": "Oryukdo Busan",
    "igidae-coastal-trail": "Igidae Busan",
    "eulsukdo": "Eulsukdo",
    "dadaepo-nature": "Dadaepo Busan sunset",
    "sorae-wetland": "Sorae Wetland OR 소래습지",
    "incheon-grand-park": "인천대공원",
    "muui-do": "Muuido Island",
    "yeongjong-do": "Yeongjongdo sea",
    "ganghwa-do": "Ganghwa Island scenery",
    "baengnyeong-do": "Baengnyeongdo OR 백령도",
    "suseong-mot": "Suseongmot OR 수성못",
    "dalseong-wetland": "달성습지 OR Dalseong wetland",
    "duryu-park": "Duryu Park Daegu OR 두류공원",
    "odongdo": "Odongdo Yeosu OR 오동도",
    "dolsando": "Dolsan Bridge Yeosu",
    "geumodo": "Geumodo OR 금오도",
    "geomundo": "Geomundo OR 거문도",
    "baekdo": "Yeosu Baekdo OR 백도",
    "yeojaman": "Yeoja Bay OR 여자만",
    "yeosu-jangdo": "Jangdo Yeosu",
    "udo": "Udo Island Jeju",
    "jusangjeolli": "Jusangjeolli OR 주상절리",
    "bijarim": "Bijarim Forest",
    "saryeoni-forest": "Saryeoni Forest",
    "gotjawal": "Gotjawal",
    "seopjikoji": "Seopjikoji",
    "sangumburi": "Sangumburi",
    "jeongbang-falls": "Jeongbang Falls",
    "soesoggak": "Soesokkak",
    "yongmeori-coast": "Yongmeori Coast OR 용머리해안",
    "manjanggul": "Manjanggul Cave",
}

BAD_TITLE = re.compile(
    r"(?i)(\.svg\b|\.pdf\b|\.djvu\b|location|locator|\bmap\b|diagram|"
    r"banner|coat of arms|flag of|logo|icon|woodblock|"
    r"namecard|station exterior|station name|wikidata)"
)


def ssl_ctx() -> ssl.SSLContext:
    global CTX
    if CTX is None:
        try:
            import certifi

            CTX = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            CTX = ssl._create_unverified_context()
    return CTX


def md5_bytes(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def md5_file(path: Path) -> str:
    return md5_bytes(path.read_bytes())


def http_get(url: str, timeout: int = 60, retries: int = 5) -> bytes:
    last: Exception | None = None
    for attempt in range(retries):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx()) as r:
                return r.read()
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code == 404:
                raise
            if exc.code == 429:
                wait = min(180, 20 * (2**attempt))
                print(f"  429 backoff {wait}s", flush=True)
                time.sleep(wait)
                continue
            if attempt + 1 < retries:
                time.sleep(4 + attempt * 2)
                continue
            raise
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(3 + attempt)
    assert last is not None
    raise last


def commons_direct_urls(title: str, width: int = 1280) -> list[str]:
    """Build likely upload.wikimedia.org URLs for a File title (no API)."""
    name = title.replace(" ", "_")
    digest = hashlib.md5(name.encode("utf-8")).hexdigest()
    a, ab = digest[0], digest[:2]
    quoted = urllib.parse.quote(name, safe="/()")
    # thumb first (smaller), then original
    return [
        f"https://upload.wikimedia.org/wikipedia/commons/thumb/{a}/{ab}/{quoted}/{width}px-{quoted}",
        f"https://upload.wikimedia.org/wikipedia/commons/{a}/{ab}/{quoted}",
    ]


def imageinfo_url(title: str, width: int = 1280) -> str | None:
    api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "query",
            "titles": f"File:{title}",
            "prop": "imageinfo",
            "iiprop": "url|mime",
            "iiurlwidth": str(width),
            "format": "json",
        }
    )
    data = json.loads(http_get(api).decode())
    for page in data.get("query", {}).get("pages", {}).values():
        if "missing" in page:
            return None
        infos = page.get("imageinfo") or []
        if not infos:
            return None
        info = infos[0]
        mime = (info.get("mime") or "").lower()
        if not mime.startswith("image/") or "svg" in mime:
            return None
        return info.get("thumburl") or info.get("url")
    return None


def commons_search(query: str, limit: int = 8) -> list[str]:
    api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srnamespace": "6",
            "srlimit": str(limit),
            "format": "json",
        }
    )
    try:
        data = json.loads(http_get(api).decode())
    except Exception as exc:  # noqa: BLE001
        print(f"  search err: {exc}", flush=True)
        return []
    out: list[str] = []
    for item in data.get("query", {}).get("search", []):
        t = item.get("title", "")
        if t.startswith("File:"):
            out.append(t[5:])
    return out


def save_image(url: str, dest: Path) -> str | None:
    try:
        data = http_get(url, timeout=70, retries=3)
    except urllib.error.HTTPError as exc:
        return f"http:{exc.code}"
    except Exception as exc:  # noqa: BLE001
        return f"dl:{exc}"
    if len(data) < 12000:
        return "too_small"
    if data[:4] == b"%PDF":
        return "pdf"
    if data[:32].lstrip().startswith(b"<") or data[:5] == b"<!DOC":
        return "html"
    if not (data[:3] == b"\xff\xd8\xff" or data[:8] == b"\x89PNG\r\n\x1a\n"):
        return "not_raster"
    dest.write_bytes(data)
    return None


def nature_slugs_from_coords() -> list[str]:
    text = COORDS.read_text(encoding="utf-8")
    slugs = []
    for line in text.splitlines():
        if 'type: "nature"' not in line:
            continue
        m = re.search(r'slug:\s*"([^"]+)"', line)
        if m:
            slugs.append(m.group(1))
    return slugs


def title_ok(title: str) -> bool:
    if BAD_TITLE.search(title):
        return False
    low = title.lower()
    return not low.endswith((".svg", ".pdf", ".djvu", ".gif"))


def download_title(title: str, dest: Path, fb_hash: str, used_hashes: set[str]) -> bool:
    """Try direct URLs then API resolve."""
    print(f"  TRY {title}", flush=True)
    urls = commons_direct_urls(title)
    # API resolve as last resort (rate limited)
    for url in urls:
        time.sleep(0.8)
        err = save_image(url, dest)
        if err:
            if err.startswith("http:404"):
                continue
            print(f"  direct fail ({err})", flush=True)
            continue
        h = md5_file(dest)
        if h == fb_hash:
            continue
        if h in used_hashes:
            dest.write_bytes(TYPE_FALLBACK.read_bytes())
            print("  skip duplicate content", flush=True)
            return False
        used_hashes.add(h)
        print(f"  OK direct {dest.stat().st_size} bytes", flush=True)
        return True

    time.sleep(2.0)
    try:
        url = imageinfo_url(title)
    except Exception as exc:  # noqa: BLE001
        print(f"  api fail ({exc})", flush=True)
        return False
    if not url:
        print("  missing", flush=True)
        return False
    err = save_image(url, dest)
    if err:
        print(f"  bad ({err})", flush=True)
        return False
    h = md5_file(dest)
    if h == fb_hash or h in used_hashes:
        dest.write_bytes(TYPE_FALLBACK.read_bytes())
        print("  skip hash", flush=True)
        return False
    used_hashes.add(h)
    print(f"  OK api {dest.stat().st_size} bytes", flush=True)
    return True


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    IMG.mkdir(parents=True, exist_ok=True)
    fb_hash = md5_file(TYPE_FALLBACK)

    targets = [
        s
        for s in nature_slugs_from_coords()
        if (not (IMG / f"{s}.jpg").exists()) or md5_file(IMG / f"{s}.jpg") == fb_hash
    ]
    print(f"Fallback nature targets: {len(targets)}", flush=True)

    replaced: list[str] = []
    still: list[str] = []
    failed: list[str] = []
    used_hashes: set[str] = set()

    for i, slug in enumerate(targets):
        dest = IMG / f"{slug}.jpg"
        print(f"\n[{i+1}/{len(targets)}] {slug}", flush=True)
        success = False

        curated = [t for t in NATURE_FILES.get(slug, []) if title_ok(t)]
        for title in curated:
            if download_title(title, dest, fb_hash, used_hashes):
                success = True
                break
            time.sleep(1.0)

        if not success:
            q = SEARCH_QUERIES.get(slug, slug)
            time.sleep(4.0)
            for title in commons_search(q):
                if not title_ok(title) or title in curated:
                    continue
                if download_title(title, dest, fb_hash, used_hashes):
                    success = True
                    break
                time.sleep(1.5)

        if success:
            replaced.append(slug)
        elif dest.exists() and md5_file(dest) == fb_hash:
            still.append(slug)
            print("  STILL FALLBACK", flush=True)
        else:
            failed.append(slug)
            print("  FAILED", flush=True)
        time.sleep(1.2)

    print("\n=== SUMMARY ===", flush=True)
    print(f"replaced ({len(replaced)}): {', '.join(replaced)}", flush=True)
    print(f"still_fallback ({len(still)}): {', '.join(still)}", flush=True)
    print(f"failed ({len(failed)}): {', '.join(failed)}", flush=True)
    (ROOT / "tool" / "_nature_image_report.txt").write_text(
        "replaced:\n"
        + "\n".join(replaced)
        + "\n\nstill_fallback:\n"
        + "\n".join(still)
        + "\n\nfailed:\n"
        + "\n".join(failed)
        + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
