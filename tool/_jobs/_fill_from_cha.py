# -*- coding: utf-8 -*-
"""Fill leftover place photos from Korea Heritage Service Open API.

Only keeps items whose official heritage name contains the query, then
downloads the agency photo. No web-search first hits.
"""
from __future__ import annotations

import importlib.util
import re
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "fill_ph", ROOT / "tool" / "_fill_placeholder_photos.py"
)
fill = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fill)

LIST_URL = "http://www.khs.go.kr/cha/SearchKindOpenapiList.do"
IMG_URL = "http://www.khs.go.kr/cha/SearchImageOpenapi.do"
SLEEP = 1.6

SKIP_SLUGS = {
    "nohyeong-supermarket",  # café; no verified exterior
    "arte-museum-jeju",  # indoor art; copyright
    "seonbichon",  # no verified village photo (false friends)
    "yeotju-seonbichon",
    "chwigajeot",  # CHA photo is people on the porch
    "gwatju-chwigajeot",
    "hamcheon-salgahyatgyo",  # CHA image was a different hyanggyo
    "yeotju-geundaeyeoksamunhwageori",  # CHA image is a map
    "yeotju-yeotju-geundaeyeoksamunhwageori",
}

# slug -> unique heritage search strings. First match wins.
QUERIES: dict[str, list[str]] = {
    "isathwa-gotaek": ["이상화생가", "이상화 고택"],
    "seosatdon-gotaek": ["서상돈생가", "서상돈 고택"],
    "yuksinsa": ["육신사"],
    "ilsil-saseondae": ["임실 사선대"],
    "wolbotseowon": ["광주 월봉서원"],
    "hamcheon-hwatmaesanseot": ["황매산성"],
    "daegueumseot-yujeok": ["대구읍성"],
    "oryundae-hanguksungyojabakmulgwan": ["한국순교자박물관"],
    "gotju-jemincheon-yeoksamunhwageori": ["제민천"],
    "andotminsokchon": ["안동민속촌"],
    "andot-andotminsokchon": ["안동민속촌"],
    "daegokbakmulgwan": ["대곡박물관"],
    "daejeongeunhyeondaesajeonsigwan": ["대전근현대사전시관"],
    "yeotju-geundaeyeoksamunhwageori": ["영주 근대역사문화거리"],
    "gangcheonsan": ["강천산"],
    "paryeongsan": ["팔영산"],
    "hwangaksan": ["황악산"],
    "gubyeongsan": ["구병산"],
    "unjangsan": ["운장산"],
    "deokhangsan": ["덕항산"],
    "namdeogyusan": ["남덕유산"],
    "bangjangsan": ["방장산"],
    "gyebangsan": ["계방산"],
    "dalseong-wetland": ["달성습지"],
    "yeojaman": ["여자만"],
    "junam-reservoir": ["주남저수지"],
    "jangseong-lake": ["장성댐"],
    "eunpa-lake-park": ["은파호수공원"],
    "boryeong-lake": ["보령댐"],
    "goesan-lake": ["괴산댐"],
    "sapgyo-lake": ["삽교호"],
    "naejang-lake": ["내장호"],
    "damyang-lake": ["담양댐"],
    "homyeong-lake": ["호명호수"],
    "geumgwang-lake": ["금광호수"],
    "seolbong-lake": ["설봉호"],
    "jinha-beach": ["진하해수욕장"],
    "chunjangdae-beach": ["춘장대해수욕장"],
    "goraebul-beach": ["고래불해수욕장"],
    "myeongsasipri-beach": ["명사십리해수욕장"],
    "yulpo-pine-beach": ["율포해수욕장"],
    "gujora-beach": ["구조라해수욕장"],
    "wolpo-beach": ["월포해수욕장"],
    "sipripo-beach": ["십리포해수욕장"],
    "manseongni-black-sand-beach": ["만성리해수욕장"],
    "wahyeon-sand-forest-beach": ["와현모래숲"],
    "namyeol-sunrise-beach": ["남열해돋이"],
    "jukdo-beach-yangyang": ["양양 죽도해수욕장"],
    "bus-terminal-ulsan": ["울산고속버스터미널"],
}

BAD_NAME_PARTS = (
    "고문서",
    "불상",
    "목조",
    "탱화",
    "유물",
    "지정서",
    "초상",
    "괘불",
    "호국사",
)

BAD_DESC = (
    "위치도",
    "안내도",
    "배치도",
    "도면",
    "지도",
    "초상",
    "인물",
    "전신",
    "흉상",
    "로고",
    "지정서",
    "관인",
)

# Heritage name must contain query, but reject these false friends.
REJECT_NAME = {
    "dokrakjeot": ("독락당",),
    "isathwa-gotaek": ("이상화 선수", "스피드"),
    "seonbichon": ("양동", "하회", "선비세상"),
    "museolmaeul": ("서래", "하회", "양동"),
    "gangcheonsan": ("금성산성",),
    "deokhangsan": ("환선굴",),
    "sejotdaewat-yeotreut-gwanryeon-yeoksamunhwagwon": ("효릉", "영녕릉", "선정릉"),
    "jukdo-beach-yangyang": ("죽도정", "울릉"),
    "gitdaebong": ("강천산",),
    "oryundae-hanguksungyojabakmulgwan": ("오륜대교",),
}


def xml_text(el: ET.Element | None) -> str:
    if el is None or el.text is None:
        return ""
    return el.text.strip()


def fetch_xml(url: str) -> ET.Element | None:
    try:
        raw = fill.http_get(url, timeout=40, retries=2)
    except Exception as exc:  # noqa: BLE001
        print(f"  http {exc}", flush=True)
        return None
    text = raw.decode("utf-8", errors="replace")
    if "<result>" not in text:
        print("  not xml", flush=True)
        return None
    try:
        return ET.fromstring(text)
    except ET.ParseError as exc:
        print(f"  xml {exc}", flush=True)
        return None


def search(query: str) -> list[dict]:
    qs = urllib.parse.urlencode(
        {"ccbaMnm1": query, "pageUnit": 12, "pageIndex": 1},
        encoding="utf-8",
    )
    root = fetch_xml(f"{LIST_URL}?{qs}")
    if root is None:
        return []
    items = []
    for item in root.findall("item"):
        items.append(
            {
                "name": xml_text(item.find("ccbaMnm1")),
                "kd": xml_text(item.find("ccbaKdcd")),
                "asno": xml_text(item.find("ccbaAsno")),
                "ct": xml_text(item.find("ccbaCtcd")),
                "cat": xml_text(item.find("ccmaName")),
                "cncl": xml_text(item.find("ccbaCncl")),
            }
        )
    return items


def pick_item(slug: str, query: str, items: list[dict]) -> dict | None:
    qn = fill.norm(query)
    rejects = tuple(fill.norm(x) for x in REJECT_NAME.get(slug, ()))
    good = []
    for it in items:
        name = it["name"]
        nn = fill.norm(name)
        if qn not in nn:
            continue
        if it.get("cncl") == "Y":
            continue
        if any(part in name for part in BAD_NAME_PARTS):
            continue
        if any(r and r in nn for r in rejects):
            continue
        # 담양호 + 국사 같은 거짓 접두 매칭 방지
        idx = nn.find(qn)
        after = nn[idx + len(qn) :]
        if qn.endswith("호") and after.startswith("국"):
            continue
        good.append(it)
    if not good:
        return None
    # Prefer shorter official name (usually the exact site, not a huge district).
    good.sort(key=lambda x: (len(fill.norm(x["name"])), x["name"]))
    return good[0]


def image_list(kd: str, asno: str, ct: str) -> list[dict]:
    qs = urllib.parse.urlencode(
        {"ccbaKdcd": kd, "ccbaAsno": asno, "ccbaCtcd": ct}
    )
    root = fetch_xml(f"{IMG_URL}?{qs}")
    if root is None:
        return []
    out = []
    for item in root.findall("item"):
        url = xml_text(item.find("imageUrl"))
        desc = xml_text(item.find("ccimDesc"))
        nuri = xml_text(item.find("imageNuri"))
        if url:
            out.append({"url": url, "desc": desc, "nuri": nuri})
    return out


def pick_image(slug: str, heritage_name: str, images: list[dict]) -> dict | None:
    ranked = []
    for im in images:
        desc = im["desc"] or ""
        blob = desc + " " + heritage_name
        if any(b in blob for b in BAD_DESC):
            continue
        nuri = (im["nuri"] or "Z")[0]
        # A best, then B/C, then D/E
        order = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4}.get(nuri, 5)
        ranked.append((order, im))
    if not ranked:
        return None
    ranked.sort(key=lambda x: x[0])
    return ranked[0][1]


def copy_group(src: str, hashes: dict, places: list[dict], ko_names: dict) -> None:
    groups = fill.group_places(places, ko_names)
    for g in groups:
        slugs = [p["slug"] for p in g]
        if src not in slugs:
            continue
        for slug in slugs:
            if slug == src:
                continue
            if fill.is_placeholder(slug, hashes):
                fill.copy_to(src, slug)
                print(f"  COPY {src} -> {slug}", flush=True)


def maybe_copy_yeongneung(hashes: dict) -> None:
    src = "sejotdaewatreut"
    dest = "sejotdaewat-yeotreut-gwanryeon-yeoksamunhwagwon"
    if not fill.is_placeholder(dest, hashes):
        return
    if fill.is_placeholder(src, hashes):
        return
    fill.copy_to(src, dest)
    print(f"COPY same-site {src} -> {dest}", flush=True)
    dup = "sejot-sejotdaewat-yeotreut-gwanryeon-yeoksamunhwagwon"
    if fill.is_placeholder(dup, hashes):
        fill.copy_to(src, dup)
        print(f"  COPY {src} -> {dup}", flush=True)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    hashes = fill.type_hashes()
    ko_names = fill.load_ko_names()
    places = fill.parse_places()
    maybe_copy_yeongneung(hashes)
    hashes = fill.type_hashes()

    ok = miss = 0
    done = set()
    for slug, queries in QUERIES.items():
        if slug in SKIP_SLUGS:
            continue
        if not fill.is_placeholder(slug, hashes):
            continue
        if slug in done:
            continue
        print(slug, flush=True)
        saved = False
        for q in queries:
            time.sleep(SLEEP)
            items = search(q)
            picked = pick_item(slug, q, items)
            if not picked:
                print(f"  no name match for {q} (n={len(items)})", flush=True)
                continue
            print(f"  hit {picked['cat']} {picked['name']}", flush=True)
            time.sleep(SLEEP)
            images = image_list(picked["kd"], picked["asno"], picked["ct"])
            im = pick_image(slug, picked["name"], images)
            if not im:
                print(f"  no usable image ({len(images)})", flush=True)
                continue
            url = im["url"].replace("http://", "https://")
            dest = fill.dest_path(slug)
            time.sleep(SLEEP)
            if fill.try_save(url, dest, hashes, f"cha:{picked['name']}"):
                saved = True
                copy_group(slug, hashes, places, ko_names)
                done.add(slug)
                break
        if saved:
            ok += 1
        else:
            miss += 1
            print("  miss", flush=True)

    remain = sum(1 for p in fill.parse_places() if fill.is_placeholder(p["slug"], hashes))
    print(f"DONE ok={ok} miss={miss} remaining={remain}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
