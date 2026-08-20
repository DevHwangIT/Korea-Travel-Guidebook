# -*- coding: utf-8 -*-
"""Download unique city-type cover photos from Wikimedia Commons."""
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
COORDS = ROOT / "data" / "places" / "places-coords.js"
TYPE_FALLBACK = IMG / "_types" / "city.jpg"
UA = "KoreaTravelGuidebook/1.0 (city covers; educational; contact via github)"
CTX = None
SLEEP = 1.8

# Curated Commons File: titles (prefer exterior / landmark matching the place).
CITY_FILES: dict[str, list[str]] = {
    "seouldal": [
        # Rare on Commons; search may find Hongdae moon / nearby street.
    ],
    "seongsu-dong": [
        "Snowy shopping street in Seongsu-dong.jpg",
        "Industrial buildings in Seongsu-dong.jpg",
        "Snowy street and sidewalk in Seongsu-dong.jpg",
    ],
    "coex": [
        "COEX Convention & Exhibition Center 01.jpg",
        "COEX Convention and Exhibition Center.jpg",
        "Korea-Seoul-COEX-01.jpg",
        "COEX Mall Seoul.jpg",
        "Trade Tower and COEX.jpg",
    ],
    "byeolmadang-library": [
        "Starfield Library COEX 20240218.jpg",
        "Books in Byeolmadang Library (254828841).jpg",
        "Starfield library 4.jpg",
    ],
    "apgujeong": [
        "Apgujeong Rodeo Street.jpg",
        "Apgujeong.jpg",
        "Korea-Seoul-Apgujeong-01.jpg",
        "Apgujeong Rodeo Station Exit 2 2012.JPG",
    ],
    "cheongdam": [
        "Cheongdam-dong.jpg",
        "Cheongdam.jpg",
        "Cheongdam Fashion Street.jpg",
        "Korea-Seoul-Cheongdam-01.jpg",
    ],
    "lotte-world": [
        "Lotte World.jpg",
        "Lotte World Adventure.jpg",
        "Korea-Seoul-Lotte World-01.jpg",
        "Lotte World Magic Island.jpg",
        "Lotteworld.jpg",
    ],
    "namsan-cable-car": [
        "Namsan cable car.jpg",
        "Namsan Cable Car (2015).jpg",
        "N Seoul Tower cable car.jpg",
        "Namsan Cablecar.jpg",
        "Korea-Seoul-Namsan Cable Car-01.jpg",
    ],
    "busan-x-the-sky": [
        "Lotte Tower Busan.jpg",
        "Signiel Busan.jpg",
        "Lotte World Tower Busan.jpg",
        "Haeundae Lotte Tower.jpg",
        "Busan Lotte Tower.jpg",
    ],
    "haeundae-blueline-park": [
        "Sky Capsule train at Haeundae Blueline Park, Busan.jpg",
    ],
    "lotte-world-adventure-busan": [
        "Lotte World Adventure Busan.jpg",
        "Osiria Theme Park.jpg",
    ],
    "shinsegae-centum-city": [
        "Shinsegae Centum City.jpg",
        "Centum City Shinsegae.jpg",
        "Centum City.jpg",
        "Shinsegae Department Store Centum City.jpg",
    ],
    "the-bay-101": [
        "The Bay 101.jpg",
        "The Bay 101 Busan.jpg",
        "Marine City Busan night.jpg",
        "Marine City Busan.jpg",
        "Haeundae Marine City.jpg",
    ],
    "busan-cinema-center": [
        "Busan Cinema Center.jpg",
        "Busan Cinema Center at night.jpg",
        "Busan Cinema Center BIFF.jpg",
        "영화의전당.jpg",
    ],
    "wolmido": [
        "Ondol Incheon Wolmido Park 1.JPG",
        "Ondol Incheon Wolmido Park 2.JPG",
        "Wolmido amusement park.jpg",
        "Wolmido Incheon.jpg",
    ],
    "inspire-resort": [
        "Inspire Entertainment Resort.jpg",
        "Inspire Resort Incheon.jpg",
    ],
    "paradise-city": [
        "Paradise City Incheon.jpg",
        "Paradise City Yeongjong.jpg",
        "Paradise City.jpg",
        "Incheon Paradise City.jpg",
    ],
    "incheon-chinatown": [
        "Incheon Chinatown South Korea 2013 02.jpg",
        "Chinatown, incheon 20230430 002.jpg",
        "Chinatown, incheon 20230430 010.jpg",
    ],
    "hyundai-premium-outlet-songdo": [
        "Hyundai Premium Outlet Songdo.jpg",
        "Songdo Hyundai Premium Outlet.jpg",
    ],
    "dongseong-ro": [
        "Dongseongno.jpg",
        "Dongseong-ro Daegu.jpg",
        "Daegu Dongseongro.jpg",
        "동성로.jpg",
    ],
    "83-tower": [
        "E-World Tower.jpg",
        "Daegu 83 Tower.jpg",
        "우방타워.jpg",
        "두류타워.jpg",
        "E WORLD Tower Daegu.jpg",
    ],
    "eworld": [
        "E WORLD in Daegu on April 5th 2013.jpg",
        "Merry-go-round in E WORLD, Daegu.jpg",
    ],
    "daegu-shinsegae": [
        "Shinsegae Daegu.jpg",
        "Daegu Shinsegae.jpg",
        "Dongdaegu Station Shinsegae.jpg",
    ],
    "aquaplanet-yeosu": [
        "Aqua Planet Yeosu.jpg",
        "Aquaplanet Yeosu.jpg",
        "아쿠아플라넷 여수.jpg",
    ],
    "yeosu-nangman-pocha": [
        "Yeosu night market.jpg",
        "Yeosu Harbor at night.jpg",
        "Yeosu waterfront night.jpg",
        "Yeosu Expo night.jpg",
        "Yeosu night.jpg",
    ],
    "arte-museum-jeju": [
        "Arte Museum Jeju.jpg",
        "ARTE Museum Jeju.jpg",
        "아르떼뮤지엄 제주.jpg",
    ],
    "981-park": [
        "9.81 Park Jeju.jpg",
        "981 Park Jeju.jpg",
        "9.81파크.jpg",
    ],
    "nohyeong-supermarket": [
        "Nohyeong Supermarket.jpg",
        "노형슈퍼마켓.jpg",
        "Nohyeong Jeju.jpg",
    ],
}

SEARCH_FALLBACK: dict[str, str] = {
    "seouldal": 'Seouldal OR "Seoul Moon" Hongdae OR 서울달',
    "seongsu-dong": "Seongsu-dong Seoul street OR 성수동",
    "coex": "COEX Seoul Convention OR 코엑스 서울",
    "byeolmadang-library": "Starfield Library COEX OR Byeolmadang",
    "apgujeong": "Apgujeong Rodeo Street Seoul OR 압구정로데오",
    "cheongdam": "Cheongdam-dong Seoul OR 청담동",
    "lotte-world": "Lotte World Seoul amusement OR 롯데월드 잠실",
    "namsan-cable-car": "Namsan cable car Seoul OR 남산케이블카",
    "busan-x-the-sky": "Lotte Tower Busan OR Signiel Busan Haeundae",
    "haeundae-blueline-park": "Haeundae Blueline Park Sky Capsule",
    "lotte-world-adventure-busan": "Lotte World Adventure Busan OR Osiria",
    "shinsegae-centum-city": "Shinsegae Centum City Busan",
    "the-bay-101": "The Bay 101 Busan OR Marine City Busan waterfront",
    "busan-cinema-center": "Busan Cinema Center OR 영화의전당",
    "wolmido": "Wolmido Incheon amusement OR 월미도",
    "inspire-resort": "Inspire Entertainment Resort Incheon Yeongjong",
    "paradise-city": "Paradise City Incheon Yeongjong resort",
    "incheon-chinatown": "Incheon Chinatown OR 인천 차이나타운",
    "hyundai-premium-outlet-songdo": "Hyundai Premium Outlet Songdo OR 송도 아울렛",
    "dongseong-ro": "Dongseongno Daegu OR 동성로 대구",
    "83-tower": 'E-World Tower Daegu OR "83 Tower" Daegu OR 우방타워 OR 두류공원 타워',
    "eworld": "E-World Daegu OR E WORLD Daegu amusement",
    "daegu-shinsegae": "Shinsegae Daegu Dongdaegu OR 대구 신세계",
    "aquaplanet-yeosu": "Aqua Planet Yeosu OR Aquaplanet Yeosu",
    "yeosu-nangman-pocha": "Yeosu night street harbor OR 여수 야경 항구",
    "arte-museum-jeju": "Arte Museum Jeju OR ARTE Museum Jeju",
    "981-park": "9.81 Park Jeju OR Gravity Race Jeju",
    "nohyeong-supermarket": "Nohyeong Supermarket Jeju OR 노형슈퍼마켓",
}

REJECT_TITLE = re.compile(
    r"(?i)\b(map|logo|icon|flag|svg|diagram|chart|poster|stamp|pdf|scan|"
    r"coat of arms|emblem|qr|infobox|location map)\b"
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


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def http_get(url: str, timeout: int = 45) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx()) as r:
        return r.read()


def imageinfo(title: str, width: int = 1280) -> dict | None:
    api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "query",
            "titles": f"File:{title}",
            "prop": "imageinfo",
            "iiprop": "url|mime|size|dimensions",
            "iiurlwidth": str(width),
            "format": "json",
        }
    )
    try:
        data = json.loads(http_get(api).decode())
    except Exception as exc:  # noqa: BLE001
        print(f"  api err: {exc}", flush=True)
        return None
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        if "missing" in page:
            return None
        infos = page.get("imageinfo") or []
        if not infos:
            return None
        return infos[0]
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
    out = []
    for item in data.get("query", {}).get("search", []):
        t = item.get("title", "")
        if t.startswith("File:"):
            out.append(t[5:])
    return out


def special_filepath(title: str, width: int = 1280) -> str:
    enc = urllib.parse.quote(title.replace(" ", "_"))
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{enc}?width={width}"


def is_usable_title(title: str) -> bool:
    if not title:
        return False
    low = title.lower()
    if low.endswith((".pdf", ".svg", ".gif", ".tif", ".tiff", ".djvu")):
        return False
    if REJECT_TITLE.search(title):
        return False
    return True


def save_image(url: str, dest: Path) -> bool:
    try:
        data = http_get(url, timeout=90)
    except Exception as exc:  # noqa: BLE001
        print(f"  dl err: {exc}", flush=True)
        return False
    if len(data) < 12000:
        print(f"  too small ({len(data)})", flush=True)
        return False
    head = data[:32].lstrip()
    if head.startswith(b"<") or head.startswith(b"<!DO") or head.startswith(b"%PDF"):
        print("  rejected non-image payload", flush=True)
        return False
    # JPEG / PNG / WEBP magic
    if not (
        data[:3] == b"\xff\xd8\xff"
        or data[:8] == b"\x89PNG\r\n\x1a\n"
        or data[:4] == b"RIFF"
    ):
        print("  rejected unknown magic", flush=True)
        return False
    dest.write_bytes(data)
    return True


def city_slugs_needing_photos(fallback_hash: str) -> list[str]:
    text = COORDS.read_text(encoding="utf-8")
    slugs: list[str] = []
    for m in re.finditer(
        r'\{\s*slug:\s*"([^"]+)".*?type:\s*"city"',
        text,
        flags=re.S,
    ):
        slug = m.group(1)
        dest = IMG / f"{slug}.jpg"
        if not dest.exists():
            slugs.append(slug)
            continue
        if fallback_hash and md5(dest) == fallback_hash:
            slugs.append(slug)
    # Prefer newly-added curated list order when present
    order = list(CITY_FILES.keys())
    ordered = [s for s in order if s in slugs]
    rest = [s for s in slugs if s not in ordered]
    return ordered + rest


def try_download(slug: str, title: str, dest: Path, fallback_hash: str) -> bool:
    if not is_usable_title(title):
        print(f"  skip title: {title}", flush=True)
        return False
    print(f"TRY {slug} <- {title}", flush=True)
    time.sleep(SLEEP)
    info = imageinfo(title)
    url = None
    if info:
        mime = (info.get("mime") or "").lower()
        if mime and not mime.startswith("image/"):
            print(f"  bad mime: {mime}", flush=True)
            return False
        if mime in ("image/svg+xml", "application/pdf"):
            print(f"  reject mime: {mime}", flush=True)
            return False
        url = info.get("thumburl") or info.get("url")
    if not url:
        # Direct FilePath fallback (still a real Commons photo if title exists)
        time.sleep(0.5)
        url = special_filepath(title)
    time.sleep(0.6)
    if not save_image(url, dest):
        return False
    if fallback_hash and md5(dest) == fallback_hash:
        print("  still fallback hash", flush=True)
        return False
    print(f"  OK {dest.stat().st_size} bytes", flush=True)
    return True


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    IMG.mkdir(parents=True, exist_ok=True)
    fallback_hash = md5(TYPE_FALLBACK) if TYPE_FALLBACK.exists() else ""
    targets = city_slugs_needing_photos(fallback_hash)
    print(f"Targets needing real photos: {len(targets)}", flush=True)

    ok: list[str] = []
    miss: list[str] = []
    log: dict[str, dict] = {}

    for slug in targets:
        dest = IMG / f"{slug}.jpg"
        candidates = list(CITY_FILES.get(slug, []))
        q = SEARCH_FALLBACK.get(slug)
        if q:
            time.sleep(SLEEP)
            for t in commons_search(q):
                if t not in candidates:
                    candidates.append(t)

        success = False
        used = None
        for title in candidates:
            if try_download(slug, title, dest, fallback_hash):
                success = True
                used = title
                break
            time.sleep(0.5)

        if success:
            ok.append(slug)
            log[slug] = {"status": "ok", "file": used, "bytes": dest.stat().st_size}
        else:
            miss.append(slug)
            log[slug] = {"status": "miss"}
            print(f"MISS {slug}", flush=True)
        time.sleep(1.0)

    # Final recount vs fallback
    still = []
    for slug in targets:
        p = IMG / f"{slug}.jpg"
        if not p.exists() or (fallback_hash and md5(p) == fallback_hash):
            still.append(slug)

    summary = {
        "replaced": ok,
        "still_fallback": still,
        "missed": miss,
        "replaced_count": len(ok),
        "still_fallback_count": len(still),
        "miss_count": len(miss),
        "details": log,
    }
    out = ROOT / "tool" / "_city_image_download_log.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"\nDONE replaced={len(ok)} still_fallback={len(still)} miss={len(miss)}",
        flush=True,
    )
    if still:
        print("STILL:", ", ".join(still), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
