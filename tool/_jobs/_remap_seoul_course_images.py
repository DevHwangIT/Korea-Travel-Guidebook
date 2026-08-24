# -*- coding: utf-8 -*-
"""Download cafe/street/store images and remap Seoul course stops."""
from __future__ import annotations

import json
import re
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "Images" / "places"
DATA = ROOT / "data" / "courses" / "seoul-curated.js"
UA = "KoreaTravelGuidebook/1.0 (course photos; educational; rate-limited)"
SLEEP = 8.0

FILES: dict[str, list[str]] = {
    "songridan-gil": [
        "Seokchon Lake and Lotte World Tower.jpg",
        "Lotte World Tower and Seokchon Lake.jpg",
        "Seokchon Lake Seoul.jpg",
    ],
    "seongsu-cafe": [
        "Snowy shopping street in Seongsu-dong.jpg",
        "Industrial buildings in Seongsu-dong.jpg",
    ],
    "seongsu-popup": [
        "Industrial buildings in Seongsu-dong.jpg",
        "Snowy street and sidewalk in Seongsu-dong.jpg",
    ],
    "gyeongnidan-gil": [
        "Itaewon Gyeongnidan-gil.JPG",
    ],
    "garosu-gil": [
        "Garosu-gil in Sinsa-dong, Seoul.jpg",
        "Sinsa-dong Garosu-gil Seoul.jpg",
    ],
    "yeonnam-cafe": [
        "연남동 (20240803) 1.jpg",
        "Covered car in an alley in Yeonnam-dong, Mapo-gu, Seoul.jpg",
    ],
    "hongdae-street": [
        "Hongdae Playground street merchants.JPG",
        "Hongdae, Seoul- Part II - Hongdae2237.jpg",
    ],
    "seochon-cafe": [
        "Seochon Cafe.jpg",
        "Seochon scene.jpg",
    ],
    "yongridan-gil": [
        "Yongsan Yongsan-ro 53-gil.jpg",
        "Yongsan-ro 53-gil.jpg",
    ],
    "itaewon-street": [
        "Itaewon Seoul.jpg",
        "Itaewon 01.jpg",
    ],
    "konkuk-food-street": [
        "Konkuk University Station.jpg",
        "Konkuk University, Seoul.jpg",
    ],
    "cheongdam-fashion": [
        "Cheongdam Fashion Street.jpg",
        "Cheongdam-dong.jpg",
    ],
}

# course_id -> list of image slug per stop (must match stop count)
STOP_IMAGES: dict[str, list[str]] = {
    "c01": [
        "gyeongbok",
        "bukchon",
        "insadong",
        "ssamziegil",
        "ikseon-dong",
        "gwangjang-market",
        "cheonggyecheon",
    ],
    "c02": [
        "myeongdong",
        "myeongdong",
        "namsan",
        "n-seoul-tower",
        "namdaemun-market",
        "seoullo-7017",
        "euljiro",
    ],
    "c03": [
        "seoul-forest",
        "seongsu-cafe",
        "seongsu-dong",
        "seongsu-popup",
        "ttukseom-hangang",
        "konkuk-food-street",
        "konkuk-university",
    ],
    "c04": [
        "yeonnam-cafe",
        "yeonnam-cafe",
        "hongdae-street",
        "hongdae",
        "mangwon-market",
        "mangwon-hangang",
        "hongdae-street",
    ],
    "c05": [
        "coex",
        "byeolmadang-library",
        "garosu-gil",
        "boteunsa",
        "seokchon-lake",
        "seokchon-lake",
        "lotte-world",
        "lotte-tower",
    ],
    "c06": [
        "naksan-park",
        "ihwa-mural-village",
        "daehangno",
        "dongdaemun",
        "ddp",
        "dongdaemun-market",
        "gwangjang-market",
        "cheonggyecheon",
    ],
    "c07": [
        "the-hyundai-seoul",
        "yeouido",
        "hangang-yeouido",
        "hangang-yeouido",
        "hangang-yeouido",
        "yeouido",
        "hangang-yeouido",
    ],
    "c08": [
        "gyeongbok",
        "seochon",
        "tongin-market",
        "seochon-cafe",
        "gwathwamun",
        "cheonggyecheon",
        "euljiro",
        "euljiro",
    ],
    "c09": [
        "hannam-dong",
        "hannam-dong",
        "itaewon-street",
        "itaewon",
        "gyeongnidan-gil",
        "haebangchon",
        "namsan",
    ],
    "c10": [
        "namdaemun-market",
        "namdaemun-market",
        "myeongdong",
        "gwangjang-market",
        "ikseon-dong",
        "bosingak",
        "cheonggyecheon",
    ],
    "c11": [
        "lotte-world",
        "seokchon-lake",
        "seokchon-lake",
        "songridan-gil",
        "lotte-tower",
        "jamsil-skyline",
    ],
    "c12": [
        "bus-terminal-seoul-express",
        "hangang-banpo",
        "sebit-seom",
        "hangang-banpo",
        "hangang-banpo",
        "hangang-banpo",
    ],
    "c13": [
        "national-museum-korea",
        "itaewon",
        "yongridan-gil",
        "itaewon-street",
        "ichon-hangang",
        "itaewon",
    ],
    "c14": [
        "naksan-park",
        "seongbuk-dong",
        "seongbuk-dong",
        "gilsatsa",
        "bukjeong-village",
        "daehangno",
        "marronnier-park",
    ],
    "c15": [
        "seoul-forest",
        "seongsu-dong",
        "seongsu-cafe",
        "cheongdam-fashion",
        "dosan-park",
        "apgujeong",
    ],
}

CTX = None


def ssl_ctx() -> ssl.SSLContext:
    global CTX
    if CTX is None:
        try:
            import certifi

            CTX = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            CTX = ssl._create_unverified_context()
    return CTX


def http_get(url: str, timeout: int = 90) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx()) as r:
        return r.read()


def thumb_url(title: str, width: int = 960) -> str | None:
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
    try:
        data = json.loads(http_get(api).decode())
    except Exception as exc:  # noqa: BLE001
        print(f"  api err: {exc}", flush=True)
        return None
    for page in data.get("query", {}).get("pages", {}).values():
        if "missing" in page:
            return None
        infos = page.get("imageinfo") or []
        if not infos:
            return None
        return infos[0].get("thumburl") or infos[0].get("url")
    return None


def save_thumb(title: str, dest: Path) -> bool:
    url = thumb_url(title)
    if not url:
        return False
    try:
        data = http_get(url)
    except Exception as exc:  # noqa: BLE001
        print(f"  dl err: {exc}", flush=True)
        return False
    if len(data) < 8000:
        return False
    if not (
        data[:3] == b"\xff\xd8\xff"
        or data[:8] == b"\x89PNG\r\n\x1a\n"
        or data[:4] == b"RIFF"
    ):
        return False
    dest.write_bytes(data)
    return True


def fetch_slug(slug: str) -> bool:
    dest = IMG / f"{slug}.jpg"
    if dest.exists() and dest.stat().st_size > 15000:
        print(f"= skip {slug}", flush=True)
        return True
    print(f"## {slug}", flush=True)
    for title in FILES.get(slug, []):
        print(f"  try {title}", flush=True)
        if save_thumb(title, dest):
            print(f"+ {slug} ({dest.stat().st_size}) <- {title}", flush=True)
            return True
        time.sleep(2)
    print(f"! FAIL {slug}", flush=True)
    return False


def fallback_slug(slug: str) -> str:
    fb = {
        "songridan-gil": "seokchon-lake",
        "seongsu-cafe": "seongsu-dong",
        "seongsu-popup": "seongsu-dong",
        "gyeongnidan-gil": "itaewon",
        "garosu-gil": "gangnam",
        "yeonnam-cafe": "yeonnam-dong",
        "hongdae-street": "hongdae",
        "seochon-cafe": "seochon",
        "yongridan-gil": "itaewon",
        "itaewon-street": "itaewon",
        "konkuk-food-street": "konkuk-university",
        "cheongdam-fashion": "cheongdam",
    }
    return fb.get(slug, slug)


def resolve_image(slug: str) -> str:
    p = IMG / f"{slug}.jpg"
    if p.exists() and p.stat().st_size > 8000:
        return slug
    fb = fallback_slug(slug)
    print(f"  fallback {slug} -> {fb}", flush=True)
    return fb


def write_courses() -> None:
    text = DATA.read_text(encoding="utf-8")
    m = re.search(r"window\.SEOUL_CURATED_COURSES\s*=\s*(\[.*\]);?\s*$", text, re.S)
    courses = json.loads(m.group(1))
    by_id = {c["id"]: c for c in courses}

    out = []
    for cid, slugs in STOP_IMAGES.items():
        c = by_id[cid]
        stops = []
        assert len(slugs) == len(c["stops"]), (cid, len(slugs), len(c["stops"]))
        for i, (stop, slug) in enumerate(zip(c["stops"], slugs)):
            resolved = resolve_image(slug)
            stops.append(
                {
                    "time": stop["time"],
                    "image": f"../../Images/places/{resolved}.jpg",
                }
            )
        cover_slug = resolve_image(slugs[0])
        out.append({"id": cid, "cover": f"../../Images/places/{cover_slug}.jpg", "stops": stops})

    header = "/** Seoul curated day courses — structure only; copy in i18n travelCourses.seoulCurated */\n"
    body = "window.SEOUL_CURATED_COURSES = " + json.dumps(out, ensure_ascii=False, indent=2) + ";\n"
    tmp = DATA.with_suffix(".js.tmp")
    tmp.write_text(header + body, encoding="utf-8")
    tmp.replace(DATA)
    print("wrote courses", flush=True)


def main() -> None:
    import sys

    write_only = "--write-only" in sys.argv
    IMG.mkdir(parents=True, exist_ok=True)
    if not write_only:
        for slug in FILES:
            fetch_slug(slug)
            time.sleep(SLEEP)
    write_courses()


if __name__ == "__main__":
    main()
