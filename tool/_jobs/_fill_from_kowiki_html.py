# -*- coding: utf-8 -*-
"""Pull a place photo from Korean Wikipedia HTML (not the REST API).

Uses the article infobox/og image only when the caption or filename
contains the place name, and skips maps/people/icons.
"""
from __future__ import annotations

import importlib.util
import re
import sys
import time
import urllib.parse
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "fill_ph", ROOT / "tool" / "_fill_placeholder_photos.py"
)
fill = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fill)

SKIP = (
    "location_map",
    "locator",
    "map of",
    "위치",
    "대한민국 안",
    "south korea location",
    "question_book",
    "commons-logo",
    "wikimedia-logo",
    "flag of",
    "coat of arms",
    "portrait",
    "headshot",
    "초상",
    "red_triangle",
    "red triangle",
    "green_pog",
    "red_pog",
    "blue_pog",
    ".svg",
    "disambig",
    "ambox",
    "padlock",
    "nuvola",
    "crystal_clear",
)


PAGES: dict[str, list[str]] = {
    "gangcheonsan": ["강천산"],
    "paryeongsan": ["팔영산"],
    "hwangaksan": ["황악산"],
    "gubyeongsan": ["구병산"],
    "unjangsan": ["운장산"],
    "deokhangsan": ["덕항산"],
    "namdeogyusan": ["남덕유산", "덕유산"],
    "bangjangsan": ["방장산"],
    "gyebangsan": ["계방산_(평창군)"],
    "gitdaebong": ["깃대봉"],
    "dalseong-wetland": ["달성습지"],
    "yeojaman": ["여자만"],
    "junam-reservoir": ["주남저수지"],
    "jangseong-lake": ["장성호"],
    "eunpa-lake-park": ["은파호수공원"],
    "goesan-lake": ["괴산호"],
    "sapgyo-lake": ["삽교호"],
    "boryeong-lake": ["보령호"],
    "naejang-lake": ["내장호"],
    "damyang-lake": ["담양호"],
    "homyeong-lake": ["호명호수"],
    "geumgwang-lake": ["금광호"],
    "seolbong-lake": ["설봉호"],
    "sipripo-beach": ["십리포해수욕장"],
    "chunjangdae-beach": ["춘장대해수욕장"],
    "jinha-beach": ["진하해수욕장"],
    "goraebul-beach": ["고래불해수욕장"],
    "wolpo-beach": ["월포해수욕장"],
    "gujora-beach": ["구조라해수욕장"],
    "myeongsasipri-beach": ["명사십리해수욕장"],
    "manseongni-black-sand-beach": ["만성리해수욕장"],
    "andotminsokchon": ["안동민속촌"],
    "seonbichon": ["선비촌_(영주시)", "영주_선비촌"],
    "isathwa-gotaek": ["이상화_고택", "이상화_(시인)"],
    "wolbotseowon": ["월봉서원"],
    "chwigajeot": ["취가정"],
    "bus-terminal-ulsan": ["울산고속버스터미널"],
}


class ImgFinder(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.imgs: list[tuple[str, str]] = []  # src, alt
        self.og = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        d = {k: (v or "") for k, v in attrs}
        if tag == "meta" and d.get("property") == "og:image":
            self.og = d.get("content") or ""
        if tag == "img":
            src = d.get("src") or d.get("data-src") or ""
            alt = d.get("alt") or ""
            if src:
                self.imgs.append((src, alt))


def abs_url(src: str) -> str:
    if src.startswith("//"):
        return "https:" + src
    if src.startswith("http"):
        return src
    return "https://ko.wikipedia.org" + src


def is_map(src: str, alt: str) -> bool:
    blob = (src + " " + alt).lower()
    return any(s.lower() in blob for s in SKIP)


def mentions(place: str, src: str, alt: str) -> bool:
    blob = urllib.parse.unquote(src + " " + alt)
    core = place.split("_")[0].replace("(", "").replace(")", "")
    return core in blob


def best_src(parser: ImgFinder, place: str) -> str | None:
    candidates = []
    if parser.og:
        candidates.append((parser.og, "og"))
    candidates.extend(parser.imgs)
    for src, alt in candidates:
        url = abs_url(src)
        if "upload.wikimedia.org" not in url:
            continue
        if is_map(url, alt):
            continue
        if not mentions(place, url, alt):
            continue
        # bump thumbs to 800
        url = re.sub(r"/\d+px-", "/800px-", url)
        return url
    return None


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    hashes = fill.type_hashes()
    ko = fill.load_ko_names()
    places = fill.parse_places()
    ok = 0
    for slug, titles in PAGES.items():
        if not fill.is_placeholder(slug, hashes):
            continue
        print(slug, flush=True)
        saved = False
        for title in titles:
            url = "https://ko.wikipedia.org/wiki/" + urllib.parse.quote(title)
            time.sleep(1.8)
            try:
                html = fill.http_get(url, timeout=40, retries=2).decode("utf-8", errors="replace")
            except Exception as exc:  # noqa: BLE001
                print(f"  fetch {title}: {exc}", flush=True)
                continue
            if "위키백과" not in html[:2000] and "wikipedia" not in html.lower()[:1500]:
                print(f"  not wiki {title}", flush=True)
                continue
            parser = ImgFinder()
            try:
                parser.feed(html)
            except Exception:
                continue
            src = best_src(parser, title)
            if not src:
                print(f"  no photo {title}", flush=True)
                continue
            print(f"  try {src[:110]}", flush=True)
            time.sleep(1.8)
            if fill.try_save(src, fill.dest_path(slug), hashes, f"kowiki:{title}"):
                saved = True
                for p in places:
                    if p["note"] and p["slug"] != slug and fill.is_placeholder(p["slug"], hashes):
                        if p["note"] == next((x["note"] for x in places if x["slug"] == slug), ""):
                            fill.copy_to(slug, p["slug"])
                            print(f"  COPY {p['slug']}", flush=True)
                break
        if saved:
            ok += 1
        else:
            print("  miss", flush=True)
    remain = sum(1 for p in fill.parse_places() if fill.is_placeholder(p["slug"], hashes))
    print(f"DONE ok={ok} remaining={remain}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
