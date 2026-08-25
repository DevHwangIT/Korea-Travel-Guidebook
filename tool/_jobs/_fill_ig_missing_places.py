# -*- coding: utf-8 -*-
"""Fetch Wikimedia/Wikipedia photos for remaining Incheon/Gyeonggi course stops."""
from __future__ import annotations

import json
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "Images" / "places" / "_courses"
UA = "KoreaTravelGuidebook/1.1 (course stop photos; educational)"

TARGETS = {
    "paradise-city-resort": {
        "wiki": [
            ("ko.wikipedia.org", "파라다이스시티"),
            ("en.wikipedia.org", "Paradise City (Incheon)"),
            ("en.wikipedia.org", "Paradise Group"),
        ],
        "files": [
            "Paradise City Incheon.jpg",
            "Paradise City (Incheon).jpg",
            "파라다이스시티.jpg",
            "Paradise City Hotel Incheon.jpg",
        ],
        "search": "Paradise City Incheon hotel",
    },
    "paradise-city-arts": {
        "wiki": [
            ("ko.wikipedia.org", "파라다이스시티"),
            ("en.wikipedia.org", "Paradise City (Incheon)"),
        ],
        "files": [
            "Paradise City Art Space.jpg",
            "Paradise City plaza.jpg",
        ],
        "search": "Paradise City Incheon plaza",
    },
    "songdo-outlet": {
        "wiki": [
            ("ko.wikipedia.org", "현대 프리미엄 아울렛"),
            ("ko.wikipedia.org", "송도국제도시"),
        ],
        "files": [
            "Hyundai Premium Outlet Songdo.jpg",
            "송도 현대프리미엄아울렛.jpg",
            "Hyundai Premium Outlet.jpg",
        ],
        "search": "Hyundai Premium Outlet Songdo",
    },
    "ganghwa-peace-obs": {
        "wiki": [
            ("ko.wikipedia.org", "강화평화전망대"),
            ("ko.wikipedia.org", "교동도"),
            ("en.wikipedia.org", "Ganghwa Island"),
        ],
        "files": [
            "강화평화전망대.jpg",
            "Ganghwa Peace Observatory.jpg",
            "Ganghwado Peace Observatory.jpg",
        ],
        "search": "강화평화전망대",
    },
    "everland-safari": {
        "wiki": [
            ("ko.wikipedia.org", "에버랜드"),
            ("en.wikipedia.org", "Everland"),
        ],
        "files": [
            "Everland Safari World.jpg",
            "Everland safari.jpg",
            "Safari World Everland.jpg",
        ],
        "search": "Everland Safari World lion",
    },
    "everland-night": {
        "wiki": [
            ("ko.wikipedia.org", "에버랜드"),
            ("en.wikipedia.org", "Everland"),
        ],
        "files": [
            "Everland night.jpg",
            "Everland illumination.jpg",
            "에버랜드 야간.jpg",
        ],
        "search": "Everland night illumination",
    },
    "minsokchon-gate": {
        "wiki": [
            ("ko.wikipedia.org", "한국민속촌"),
            ("en.wikipedia.org", "Korean Folk Village"),
        ],
        "files": [
            "Korean Folk Village Yongin.jpg",
            "한국민속촌.jpg",
            "Korean Folk Village entrance.jpg",
        ],
        "search": "Korean Folk Village Yongin thatched",
    },
    "gwangmyeong-market": {
        "wiki": [
            ("ko.wikipedia.org", "광명전통시장"),
            ("ko.wikipedia.org", "광명시"),
        ],
        "files": [
            "광명전통시장.jpg",
            "Gwangmyeong Traditional Market.jpg",
        ],
        "search": "광명전통시장",
    },
    "yeoju-outlet": {
        "wiki": [
            ("ko.wikipedia.org", "여주프리미엄아울렛"),
            ("en.wikipedia.org", "Premium Outlets"),
            ("ko.wikipedia.org", "여주시"),
        ],
        "files": [
            "Yeoju Premium Outlets.jpg",
            "여주프리미엄아울렛.jpg",
            "Premium Outlets Yeoju.jpg",
        ],
        "search": "Yeoju Premium Outlets",
    },
    "haengnidangil": {
        "wiki": [
            ("ko.wikipedia.org", "행궁동"),
            ("ko.wikipedia.org", "수원화성"),
        ],
        "files": [
            "행리단길.jpg",
            "행궁동.jpg",
            "Suwon Haenggung-dong.jpg",
        ],
        "search": "수원 행궁동 카페",
    },
    "gopchang-food": {
        "wiki": [
            ("ko.wikipedia.org", "곱창"),
            ("en.wikipedia.org", "Gopchang"),
        ],
        "files": [
            "Gopchang.jpg",
            "Korean gopchang.jpg",
            "곱창구이.jpg",
            "Makchang.jpg",
        ],
        "search": "gopchang grilled Korea",
    },
}

CTX = ssl._create_unverified_context()


def http_get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45, context=CTX) as r:
        return r.read()


def save_ok(data: bytes, dest: Path) -> bool:
    if len(data) < 18000:
        print(f"  too small {len(data)}", flush=True)
        return False
    if data[:32].lstrip()[:1] == b"<":
        print("  html", flush=True)
        return False
    if not (data[:3] == b"\xff\xd8\xff" or data[:8] == b"\x89PNG\r\n\x1a\n"):
        print("  magic", data[:8], flush=True)
        return False
    dest.write_bytes(data)
    print(f"  saved {dest.name} ({dest.stat().st_size})", flush=True)
    return True


def commons_file(title: str) -> str:
    enc = urllib.parse.quote(title.replace(" ", "_"))
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{enc}?width=1400"


def pageimage(host: str, title: str) -> str | None:
    api = f"https://{host}/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "query",
            "titles": title,
            "prop": "pageimages",
            "pithumbsize": 1400,
            "format": "json",
        }
    )
    data = json.loads(http_get(api).decode())
    for page in data.get("query", {}).get("pages", {}).values():
        src = (page.get("thumbnail") or {}).get("source")
        if src:
            return src
    return None


def commons_search(q: str, limit: int = 8) -> list[str]:
    api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "query",
            "list": "search",
            "srsearch": q,
            "srnamespace": 6,
            "srlimit": limit,
            "format": "json",
        }
    )
    data = json.loads(http_get(api).decode())
    out = []
    for hit in data.get("query", {}).get("search", []):
        t = hit.get("title", "")
        if t.startswith("File:"):
            out.append(t[5:])
    return out


def try_url(url: str, dest: Path) -> bool:
    try:
        print(f"  get {url[:110]}", flush=True)
        return save_ok(http_get(url), dest)
    except Exception as exc:
        print(f"  err {exc}", flush=True)
        return False


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for slug, spec in TARGETS.items():
        dest = OUT / f"{slug}.jpg"
        print(f"\n## {slug}", flush=True)
        got = False
        for fname in spec.get("files") or []:
            if try_url(commons_file(fname), dest):
                got = True
                break
            time.sleep(0.8)
        if not got:
            for host, title in spec.get("wiki") or []:
                print(f"  wiki {host} {title}", flush=True)
                try:
                    url = pageimage(host, title)
                    if url and try_url(url, dest):
                        got = True
                        break
                except Exception as exc:
                    print(f"  wiki err {exc}", flush=True)
                time.sleep(1.0)
        if not got:
            try:
                for fname in commons_search(spec.get("search") or slug):
                    print(f"  search hit {fname}", flush=True)
                    if try_url(commons_file(fname), dest):
                        got = True
                        break
                    time.sleep(0.8)
            except Exception as exc:
                print(f"  search err {exc}", flush=True)
        if not got:
            print(f"! FAIL {slug}", flush=True)
            if dest.exists():
                dest.unlink()
        time.sleep(1.2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
