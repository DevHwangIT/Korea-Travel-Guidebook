# -*- coding: utf-8 -*-
"""Pass 3: Wikipedia pageimages + curated Commons FilePath (slow)."""
from __future__ import annotations

import hashlib
import json
import ssl
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "Images" / "places"
TYPE_FALLBACK = IMG / "_types" / "city.jpg"
UA = "KoreaTravelGuidebook/1.0 (city covers pass3; educational)"
CTX = None
SLEEP = 5.0

# Reset these to fallback before retry (wrong subject)
RESET = {
    "busan-x-the-sky",  # Gwangan Bridge
    "coex",  # COEX Aquarium interior only
    "cheongdam",  # may still be fallback
}

# slug -> list of (wiki_lang, wiki_title) and optional exact Commons file titles
JOBS: dict[str, dict] = {
    "seouldal": {
        "wiki": [("en", "Hongdae (area)"), ("ko", "홍대앞"), ("en", "Mapo District")],
        "files": [
            "Hongdae street at night.jpg",
            "Hongik University Street Seoul.jpg",
            "Hongdae Seoul 2014.jpg",
        ],
    },
    "coex": {
        "wiki": [("en", "COEX Convention & Exhibition Center"), ("en", "COEX Mall"), ("ko", "코엑스")],
        "files": [
            "COEX Convention & Exhibition Center 01.jpg",
            "Korea-Seoul-COEX Convention and Exhibition Center-01.jpg",
            "Trade Tower Seoul night.jpg",
            "World Trade Center Seoul.jpg",
        ],
    },
    "apgujeong": {
        "wiki": [("en", "Apgujeong-dong"), ("ko", "압구정동"), ("en", "Galleria Department Store")],
        "files": [
            "Apgujeong Rodeo Stantion Exit 2 2012.JPG",
            "Apgujeong Rodeo Station 6.JPG",
        ],
    },
    "cheongdam": {
        "wiki": [("en", "Cheongdam-dong"), ("ko", "청담동")],
        "files": [],
    },
    "busan-x-the-sky": {
        "wiki": [
            ("en", "Lotte World Tower"),  # Seoul - skip if wrong city in caption later
            ("en", "Haeundae District"),
            ("en", "Marine City"),
            ("ko", "해운대"),
            ("en", "Signiel"),
        ],
        "files": [
            "Marine City from Gwangalli Beach.jpg",
            "Haeundae Marine City from sea.jpg",
            "Busan Marine City skyline.jpg",
            "Haeundae Beach and Marine City.jpg",
            "View of Haeundae from Dalmaji.jpg",
        ],
    },
    "the-bay-101": {
        "wiki": [("en", "Marine City"), ("ko", "마린시티"), ("en", "Haeundae District")],
        "files": [
            "Marine City Busan yacht marina.jpg",
            "Haeundae Marine City waterfront.jpg",
        ],
    },
    "wolmido": {
        "wiki": [("en", "Wolmi Island"), ("ko", "월미도"), ("en", "Incheon Chinatown")],
        "files": [
            "Wolmido Amusement Park.jpg",
            "Incheon Port and Wolmido.jpg",
            "Wolmi Cultural Street.jpg",
        ],
    },
    "inspire-resort": {
        "wiki": [("en", "Inspire Entertainment Resort"), ("ko", "인스파이어 엔터테인먼트 리조트")],
        "files": [],
    },
    "paradise-city": {
        "wiki": [("en", "Paradise City"), ("ko", "파라다이스시티")],
        "files": [],
    },
    "hyundai-premium-outlet-songdo": {
        "wiki": [("en", "Songdo International Business District"), ("ko", "송도국제도시")],
        "files": [
            "Songdo Central Park.jpg",
            "Songdo IBD.jpg",
        ],
    },
    "83-tower": {
        "wiki": [("en", "E-World"), ("ko", "이월드"), ("ko", "83타워")],
        "files": [
            "E WORLD in Daegu on April 5th 2013.jpg",  # park overview may include tower
            "Merry-go-round in E WORLD, Daegu.jpg",
        ],
    },
    "daegu-shinsegae": {
        "wiki": [("en", "Dongdaegu Station"), ("ko", "동대구역"), ("en", "Shinsegae")],
        "files": [
            "Dongdaegu Station 2019.jpg",
            "Dongdaegu Station building.jpg",
            "Korea Daegu Dongdaegu Station.jpg",
        ],
    },
    "yeosu-nangman-pocha": {
        "wiki": [("en", "Yeosu"), ("ko", "여수시"), ("en", "Expo 2012")],
        "files": [
            "Yeosu night view.jpg",
            "Yeosu Harbor.jpg",
            "Yeosu Expo 2012 night.jpg",
            "Odongdo Yeosu.jpg",
        ],
    },
    "arte-museum-jeju": {
        "wiki": [("en", "Aewol-eup"), ("ko", "애월읍")],
        "files": [],
    },
    "nohyeong-supermarket": {
        "wiki": [("en", "Jeju City"), ("ko", "제주시")],
        "files": [],
    },
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


def http_get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx()) as r:
        return r.read()


def http_json(url: str) -> dict:
    return json.loads(http_get(url).decode())


def wiki_lead_image(lang: str, title: str) -> tuple[str | None, str | None]:
    """Return (thumb_url, commons_filename_hint)."""
    api = f"https://{lang}.wikipedia.org/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "query",
            "titles": title,
            "prop": "pageimages|pageprops",
            "piprop": "original|thumbnail|name",
            "pithumbsize": "1280",
            "format": "json",
        }
    )
    try:
        data = http_json(api)
    except Exception as exc:  # noqa: BLE001
        print(f"  wiki err {lang}:{title}: {exc}", flush=True)
        return None, None
    for page in data.get("query", {}).get("pages", {}).values():
        if "missing" in page:
            return None, None
        original = (page.get("original") or {}).get("source")
        thumb = (page.get("thumbnail") or {}).get("source")
        name = page.get("pageimage")
        return (original or thumb), name
    return None, None


def rest_summary_thumb(lang: str, title: str) -> str | None:
    enc = urllib.parse.quote(title.replace(" ", "_"))
    url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{enc}"
    try:
        data = http_json(url)
    except Exception as exc:  # noqa: BLE001
        print(f"  rest err {lang}:{title}: {exc}", flush=True)
        return None
    thumb = (data.get("originalimage") or data.get("thumbnail") or {}).get("source")
    return thumb


def special_filepath(title: str, width: int = 1280) -> str:
    enc = urllib.parse.quote(title.replace(" ", "_"))
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{enc}?width={width}"


def save_image(url: str, dest: Path) -> bool:
    try:
        data = http_get(url, timeout=90)
    except Exception as exc:  # noqa: BLE001
        print(f"  dl err: {exc}", flush=True)
        return False
    if len(data) < 15000:
        print(f"  too small {len(data)}", flush=True)
        return False
    if data[:3] != b"\xff\xd8\xff" and data[:8] != b"\x89PNG\r\n\x1a\n":
        print("  bad magic", flush=True)
        return False
    dest.write_bytes(data)
    return True


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    fb = md5(TYPE_FALLBACK)
    ok, miss = [], []

    for slug in RESET:
        dest = IMG / f"{slug}.jpg"
        if TYPE_FALLBACK.exists():
            dest.write_bytes(TYPE_FALLBACK.read_bytes())
            print(f"RESET {slug}", flush=True)

    for slug, cfg in JOBS.items():
        dest = IMG / f"{slug}.jpg"
        if dest.exists() and md5(dest) != fb and slug not in RESET:
            print(f"KEEP {slug}", flush=True)
            ok.append(slug)
            continue

        candidates_urls: list[tuple[str, str]] = []
        # Wikipedia lead images first (different host; gentler)
        for lang, title in cfg.get("wiki") or []:
            time.sleep(SLEEP)
            url, name = wiki_lead_image(lang, title)
            if url:
                candidates_urls.append((f"wiki:{lang}:{title}", url))
            time.sleep(1.5)
            url2 = rest_summary_thumb(lang, title)
            if url2 and url2 != url:
                candidates_urls.append((f"rest:{lang}:{title}", url2))

        for title in cfg.get("files") or []:
            candidates_urls.append((f"file:{title}", special_filepath(title)))

        success = False
        used = None
        for label, url in candidates_urls:
            print(f"TRY {slug} <- {label}", flush=True)
            time.sleep(SLEEP)
            if save_image(url, dest) and md5(dest) != fb:
                print(f"  OK {dest.stat().st_size}", flush=True)
                success = True
                used = label
                break
            time.sleep(1.0)

        if success:
            ok.append(slug)
            print(f"OK {slug} <- {used}", flush=True)
        else:
            miss.append(slug)
            print(f"MISS {slug}", flush=True)
        time.sleep(3.0)

    still = [s for s in JOBS if not (IMG / f"{s}.jpg").exists() or md5(IMG / f"{s}.jpg") == fb]
    print(f"\nPASS3 ok={len(ok)} miss={len(miss)} still={len(still)}", flush=True)
    if still:
        print("STILL:", ", ".join(still), flush=True)
    (ROOT / "tool" / "_city_image_pass3_log.json").write_text(
        json.dumps({"ok": ok, "miss": miss, "still": still}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
