# -*- coding: utf-8 -*-
"""Download unique market cover photos from Wikimedia Commons (imageinfo API)."""
from __future__ import annotations

import hashlib
import json
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "Images" / "places"
TYPE_FALLBACK = IMG / "_types" / "market.jpg"
UA = "KoreaTravelGuidebook/1.0 (market covers; educational)"
CTX = None

# Curated Commons file titles known to exist (prefer lively market scenes).
MARKET_FILES: dict[str, list[str]] = {
    "gwangjang-market": [
        "Gwangjang Market, Seoul 01.jpg",
        "Korea-Seoul-Gwangjang Market-01.jpg",
    ],
    "namdaemun-market": [
        "Namdaemun Market Alley.jpg",
        "남대문 시장.jpg",
    ],
    "tongin-market": [
        "Korea Tongin Market 05 (12920990354).jpg",
        "Korea Tongin Market 07 (12920680933).jpg",
    ],
    "mangwon-market": [
        "Mercado Mangwon en Seúl.jpg",
    ],
    "dongdaemun-market": [
        "Korea-Seoul-Dongdaemun Market-01.jpg",
        "Korea-Seoul-Dongdaemun Market-02.jpg",
    ],
    "noryangjin-fish-market": [
        "Noryangjin Fisheries Wholesale Market (4439605879).jpg",
    ],
    "myeongdong-night-market": [
        "Myeongdong night market seoul 1.jpg",
        "Myeongdong night market seoul 4.jpg",
    ],
    "gyeongdong-market": [
        "Korea-Seoul-Gyeongdong Market-02.jpg",
    ],
    "seoul-folk-flea-market": [
        "KOCIS Korea SeoulFolkFleaMarket 14 (8641373889).jpg",
        "Korea SeoulFolkFleaMarket 01 (8641373827).jpg",
    ],
    "jagalchi-market": [
        "Jagalchi Market 01.jpg",
        "Korea-Busan-Jagalchi Fish Market-01.jpg",
    ],
    "gukje-market": [
        "Gukje Market Busan South Korea 01.jpg",
        "Gukje Market area in Busan.jpg",
        "Gukje Market 1.jpg",
    ],
    "bujeon-kkangtong-market": [
        "Bupyeong Kkangtong Night Market.jpg",
        "Night market in Jung-gu, Busan.jpg",
    ],
    "gupo-market": [
        "Gupo Market.jpg",
    ],
    "seomun-market": [
        "Seomun Night Market, Daegu.jpg",
        "Seomun Market Gate.JPG",
        "10경 서문시장.jpg",
    ],
    "chilseong-market": [
        "Chilseong Market.jpg",
    ],
    "jeonju-nambu-market": [
        "Jeonju Nambu Market.jpg",
    ],
    "jeonju-jungang-market": [
        "Jeonju Jungang Market.jpg",
    ],
    "gangneung-jungang-market": [
        "Gangneung Jungang Market.jpg",
    ],
    "jeju-dongmun-market": [
        "Jeju Dongmun Traditional Market 01.jpg",
        "Dongmun Market 01.JPG",
        "Jeju dongmun market 1.JPG",
    ],
    "seogwipo-maeil-olle-market": [
        "Seogwipo Maeil Olle Market.jpg",
        "서귀포매일올레시장.jpg",
    ],
    "sinpo-international-market": [
        "Sinpo International Market.jpg",
        "신포국제시장.jpg",
    ],
    "incheon-complex-fish-market": [
        "Incheon Fish Market.jpg",
        "인천종합어시장.jpg",
    ],
    "suwon-paldalmun-market": [
        "Paldalmun Market.jpg",
        "Suwon Hwaseong Paldalmun.jpg",
    ],
    "sokcho-tourist-fish-market": [
        "Sokcho Jungang Market.jpg",
        "속초관광수산시장.jpg",
    ],
    "chuncheon-folk-market": [
        "Chuncheon Market.jpg",
        "춘천풍물시장.jpg",
    ],
    "yeosu-seo-market": [
        "Yeosu Market.jpg",
        "여수서시장.jpg",
    ],
    "tongyeong-jungang-market": [
        "Tongyeong Jungang Market.jpg",
        "통영중앙시장.jpg",
    ],
    "mokpo-fish-market": [
        "Mokpo Fish Market.jpg",
        "목포종합수산시장.jpg",
    ],
    "gyeongju-jungang-market": [
        "Gyeongju Jungang Market.jpg",
        "경주중앙시장.jpg",
    ],
    "gongju-sanseong-market": [
        "Gongju Sanseong Market.jpg",
        "공주산성시장.jpg",
    ],
    "andong-gu-market": [
        "Korea-Andong-Inside of Andong Market-01.jpg",
        "Korea-Andong-Entrance of Andong Market-01.jpg",
    ],
    "pohang-jukdo-market": [
        "Jukdo Market.jpg",
        "죽도시장.jpg",
    ],
}

SEARCH_FALLBACK: dict[str, str] = {
    "gupo-market": "구포시장 OR Gupo Market Busan",
    "chilseong-market": "칠성시장 OR Chilseong Market Daegu",
    "jeonju-nambu-market": "전주남부시장 OR Jeonju Nambu Market",
    "jeonju-jungang-market": "전주중앙시장 OR Jeonju Jungang Market",
    "gangneung-jungang-market": "강릉중앙시장 OR Gangneung market",
    "seogwipo-maeil-olle-market": "서귀포매일올레 OR Seogwipo Olle Market",
    "sinpo-international-market": "신포국제시장 OR Sinpo Market Incheon",
    "incheon-complex-fish-market": "인천종합어시장 OR Incheon fish market",
    "suwon-paldalmun-market": "팔달문시장 OR Suwon traditional market",
    "sokcho-tourist-fish-market": "속초관광수산시장 OR Sokcho fish market",
    "chuncheon-folk-market": "춘천풍물시장 OR Chuncheon traditional market",
    "yeosu-seo-market": "여수서시장 OR Yeosu market",
    "tongyeong-jungang-market": "통영중앙시장 OR Tongyeong market",
    "mokpo-fish-market": "목포수산시장 OR Mokpo fish market",
    "gyeongju-jungang-market": "경주중앙시장 OR Gyeongju market",
    "gongju-sanseong-market": "공주산성시장 OR Gongju market",
    "pohang-jukdo-market": "죽도시장 OR Jukdo Market Pohang",
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


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def http_get(url: str, timeout: int = 40) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx()) as r:
        return r.read()


def imageinfo_url(title: str, width: int = 1280) -> str | None:
    """Resolve Commons File:title to a thumb URL via MediaWiki API."""
    api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "query",
            "titles": f"File:{title}",
            "prop": "imageinfo",
            "iiprop": "url",
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
        info = infos[0]
        return info.get("thumburl") or info.get("url")
    return None


def commons_search(query: str, limit: int = 6) -> list[str]:
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


def save_image(url: str, dest: Path) -> bool:
    try:
        data = http_get(url, timeout=60)
    except Exception as exc:  # noqa: BLE001
        print(f"  dl err: {exc}", flush=True)
        return False
    if len(data) < 10000:
        return False
    # reject html error pages
    if data[:32].lstrip().startswith(b"<") or data[:4] == b"<!DO":
        return False
    dest.write_bytes(data)
    return True


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    IMG.mkdir(parents=True, exist_ok=True)
    fallback_hash = md5(TYPE_FALLBACK) if TYPE_FALLBACK.exists() else ""
    ok = miss = 0
    missed: list[str] = []

    for slug, titles in MARKET_FILES.items():
        dest = IMG / f"{slug}.jpg"
        if dest.exists() and dest.stat().st_size > 20000:
            if not fallback_hash or md5(dest) != fallback_hash:
                print(f"KEEP {slug}", flush=True)
                ok += 1
                continue

        candidates = list(titles)
        q = SEARCH_FALLBACK.get(slug)
        if q:
            time.sleep(1.5)
            for t in commons_search(q):
                if t not in candidates:
                    candidates.append(t)

        success = False
        for title in candidates:
            print(f"TRY {slug} <- {title}", flush=True)
            time.sleep(1.2)
            url = imageinfo_url(title)
            if not url:
                print("  missing on commons", flush=True)
                continue
            if save_image(url, dest):
                if fallback_hash and md5(dest) == fallback_hash:
                    continue
                print(f"  OK {dest.stat().st_size} bytes", flush=True)
                success = True
                ok += 1
                break
            time.sleep(0.8)

        if not success:
            print(f"MISS {slug}", flush=True)
            miss += 1
            missed.append(slug)
        time.sleep(1.0)

    print(f"\nDONE ok={ok} miss={miss}", flush=True)
    if missed:
        print("MISSED:", ", ".join(missed), flush=True)
        # write list for follow-up AI generation
        (ROOT / "tool" / "_market_image_misses.txt").write_text(
            "\n".join(missed), encoding="utf-8"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
