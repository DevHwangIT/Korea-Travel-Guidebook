# -*- coding: utf-8 -*-
"""Fill missing Incheon/Gyeonggi course photos and uniquify reused food shots."""
from __future__ import annotations

import json
import shutil
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMG = ROOT / "Images" / "places" / "_courses"
FOOD = ROOT / "Images" / "places"
UA = "KoreaTravelGuidebook/1.0 (course photo fill; educational; rate-limited)"

FOOD_COPIES = [
    ("pages/foods/meals/korean-pasta/media/cover.jpg", FOOD / "food-pasta-songdo.jpg"),
    ("pages/foods/meals/samgyeopsal/gukbo-garden/media/cover.jpg", FOOD / "food-samgyeopsal-songdo.jpg"),
    ("pages/foods/meals/gukbap/yeongchunok/media/cover.jpg", FOOD / "food-gukbap-masian.jpg"),
    ("pages/foods/desserts/cafe/beton-seongsu/media/cover.jpg", FOOD / "food-cafe-masian.jpg"),
    ("pages/foods/meals/bulgogi/media/cover.jpg", FOOD / "food-bulgogi-paradise.jpg"),
    ("pages/foods/desserts/toast/eggdrop-gangnam/media/cover.jpg", FOOD / "food-toast-masian.jpg"),
    ("pages/foods/meals/budae-jjigae/daewoo-budae-jjigae/media/cover.jpg", FOOD / "food-budae-masian.jpg"),
    ("pages/foods/meals/dolsotbap/solsot-myeongdong/media/cover.jpg", FOOD / "food-dolsotbap-ganghwa.jpg"),
    ("pages/foods/desserts/cafe/paul-bassett-gwanghwamun/media/cover.jpg", FOOD / "food-cafe-ganghwa.jpg"),
    ("pages/foods/meals/baekban/sunchunga/media/cover.jpg", FOOD / "food-baekban-ganghwa.jpg"),
    ("pages/foods/meals/kimbap/hawaii-kimbap/media/cover.jpg", FOOD / "food-kimbap-haenggung.jpg"),
    ("pages/foods/meals/gopchang/michin-makchang/media/cover.jpg", FOOD / "food-gopchang-nami.jpg"),
    ("pages/foods/meals/jeon/bakgane-bindaetteok/media/cover.jpg", FOOD / "food-bindaetteok-imjingak.jpg"),
    ("pages/foods/desserts/cafe/dotori-garden/media/cover.jpg", FOOD / "food-cafe-heyri.jpg"),
    ("pages/foods/meals/dakgangjeong/manseok-dakgangjeong-anmok/media/cover.jpg", FOOD / "food-chicken-everland.jpg"),
    ("pages/foods/meals/dakhanmari/hyodam-myeongdong/media/cover.jpg", FOOD / "food-dakhanmari-everland.jpg"),
    ("pages/foods/meals/galbijjim/seongbukdong-myeonokjip/media/cover.jpg", FOOD / "food-galbijjim-minsok.jpg"),
    ("pages/foods/meals/samgyeopsal/kimchiok-magok/media/cover.jpg", FOOD / "food-samgyeopsal-jukjeon.jpg"),
    ("pages/foods/meals/baekban/yangji-sikdang/media/cover.jpg", FOOD / "food-baekban-yangpyeong.jpg"),
    ("pages/foods/desserts/cafe/miruku-coffee-gwangalli/media/cover.jpg", FOOD / "food-cafe-yangpyeong.jpg"),
    ("pages/foods/meals/gukbap/daeseongjip/media/cover.jpg", FOOD / "food-gukbap-gwangmyeong.jpg"),
    ("pages/foods/meals/sundubu-jjigae/bukchangdong-sundubu/media/cover.jpg", FOOD / "food-sundubu-namhansan.jpg"),
    ("pages/foods/desserts/bingsu/ikseondang/media/cover.jpg", FOOD / "food-bingsu-namhansan.jpg"),
    ("pages/foods/meals/yangnyeom-chicken/kyochon-yongmun/media/cover.jpg", FOOD / "food-chicken-pocheon.jpg"),
    ("pages/foods/meals/dolsotbap/yeonjune-dolsotbap/media/cover.jpg", FOOD / "food-dolsotbap-yeoju.jpg"),
    ("pages/foods/desserts/hotteok/media/cover.jpg", FOOD / "food-hotteok-cafe.jpg"),
    ("pages/foods/desserts/toast/isaac-toast-gwanghwamun/media/cover.jpg", FOOD / "food-toast-heyri.jpg"),
]

JOBS = [
    {
        "dest": IMG / "paradise-city-resort.jpg",
        "titles": [
            "Paradise City Incheon.jpg",
            "Paradise City Hotel Incheon.jpg",
            "Paradise City Yeongjongdo.jpg",
            "Incheon Paradise City.jpg",
        ],
        "search": "Paradise City Incheon hotel building",
    },
    {
        "dest": IMG / "paradise-city-arts.jpg",
        "titles": [
            "Paradise City Artmosphere.jpg",
            "Paradise City Incheon lobby.jpg",
            "Wonderbox Paradise City.jpg",
        ],
        "search": "Paradise City Incheon art sculpture",
    },
    {
        "dest": IMG / "songdo-outlet.jpg",
        "titles": [
            "Hyundai Premium Outlet Songdo.jpg",
            "Songdo Hyundai Premium Outlet.jpg",
            "현대프리미엄아울렛 송도.jpg",
        ],
        "search": "Hyundai Premium Outlet Songdo Incheon",
    },
    {
        "dest": IMG / "eulwangni-sunset.jpg",
        "titles": [
            "Eulwangri Beach sunset.jpg",
            "Eurwangni sunset.jpg",
            "을왕리 일몰.jpg",
            "Yeongjongdo sunset.jpg",
        ],
        "search": "Eulwangri Beach sunset Incheon",
    },
    {
        "dest": IMG / "ganghwa-peace.jpg",
        "titles": [
            "Ganghwa Peace Observatory.jpg",
            "강화평화전망대.jpg",
            "Ganghwa Peace Observatory 2014.jpg",
        ],
        "search": "Ganghwa Peace Observatory viewpoint",
    },
    {
        "dest": IMG / "dongmak-beach.jpg",
        "titles": [
            "Dongmak Beach.jpg",
            "동막해수욕장.jpg",
            "Dongmak Beach Ganghwa.jpg",
            "Ganghwa Dongmak Beach.jpg",
        ],
        "search": "Dongmak Beach Ganghwa mudflat",
    },
    {
        "dest": IMG / "dongmak-sunset.jpg",
        "titles": [
            "Dongmak Beach sunset.jpg",
            "Ganghwa sunset beach.jpg",
            "동막해변 일몰.jpg",
        ],
        "search": "Dongmak Beach Ganghwa sunset",
    },
    {
        "dest": IMG / "jeondeungsa-hall.jpg",
        "titles": [
            "Jeondeungsa.jpg",
            "전등사.jpg",
            "Jeondeungsa Temple Ganghwa.jpg",
            "Daeungjeon Jeondeungsa.jpg",
        ],
        "search": "Jeondeungsa Temple Ganghwa hall",
    },
    {
        "dest": IMG / "haengnidangil.jpg",
        "titles": [
            "Haenggung-dong Suwon.jpg",
            "Haenggungdong.jpg",
            "행궁동.jpg",
            "Suwon Hwaseong village.jpg",
        ],
        "search": "Haenggung-dong Suwon cafe street",
    },
    {
        "dest": IMG / "everland-safari.jpg",
        "titles": [
            "Everland Safari World.jpg",
            "Everland lion safari.jpg",
            "에버랜드 사파리.jpg",
        ],
        "search": "Everland Safari World Yongin",
    },
    {
        "dest": IMG / "everland-night.jpg",
        "titles": [
            "Everland night parade.jpg",
            "Everland night.jpg",
            "에버랜드 야경.jpg",
            "Everland illumination.jpg",
        ],
        "search": "Everland night lights Yongin",
    },
    {
        "dest": IMG / "gwangmyeong-market.jpg",
        "titles": [
            "Gwangmyeong Traditional Market.jpg",
            "광명전통시장.jpg",
            "Gwangmyeong market street.jpg",
        ],
        "search": "Gwangmyeong Traditional Market street",
    },
    {
        "dest": IMG / "namhansanseong-wall.jpg",
        "titles": [
            "Namhansanseong wall.jpg",
            "Namhansanseong fortress wall.jpg",
            "남한산성 성곽.jpg",
        ],
        "search": "Namhansanseong fortress wall trail",
    },
    {
        "dest": IMG / "namhansanseong-seomun.jpg",
        "titles": [
            "Namhansanseong Seomun.jpg",
            "남한산성 서문.jpg",
            "West Gate Namhansanseong.jpg",
        ],
        "search": "Namhansanseong west gate",
    },
    {
        "dest": IMG / "yeoju-outlet.jpg",
        "titles": [
            "Yeoju Premium Outlets.jpg",
            "여주프리미엄아울렛.jpg",
            "Premium Outlets Yeoju.jpg",
        ],
        "search": "Yeoju Premium Outlets building",
    },
    {
        "dest": IMG / "minsokchon-houses.jpg",
        "titles": [
            "Korean Folk Village thatched.jpg",
            "Hanguk Minsokchon.jpg",
            "한국민속촌 가옥.jpg",
            "Yongin Folk Village.jpg",
        ],
        "search": "Korean Folk Village Yongin thatched house",
    },
    {
        "dest": IMG / "hanagae-wide.jpg",
        "titles": [
            "Hanagae Beach.jpg",
            "하나개해수욕장.jpg",
            "Muuido Hanagae.jpg",
            "Hanagae Beach Muuido.jpg",
        ],
        "search": "Hanagae Beach Muuido Incheon",
    },
]

CTX = None
REJECT = ("portrait", "selfie", "map", "logo", "svg", "diagram", "stamp")


def ssl_ctx():
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


def special_filepath(title: str, width: int = 1280) -> str:
    enc = urllib.parse.quote(title.replace(" ", "_"))
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{enc}?width={width}"


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
    except Exception as exc:
        print(f"  search err: {exc}", flush=True)
        return []
    out = []
    for item in data.get("query", {}).get("search", []):
        t = item.get("title", "")
        if t.startswith("File:"):
            out.append(t[5:])
    return out


def ok_title(title: str) -> bool:
    low = title.lower()
    if low.endswith((".pdf", ".svg", ".gif", ".tif", ".tiff", ".djvu", ".webm")):
        return False
    return not any(b in low for b in REJECT)


def save_image(url: str, dest: Path) -> bool:
    try:
        data = http_get(url)
    except Exception as exc:
        print(f"  dl err: {exc}", flush=True)
        return False
    if len(data) < 12000:
        print(f"  too small ({len(data)})", flush=True)
        return False
    head = data[:32].lstrip()
    if head.startswith(b"<") or head.startswith(b"<!DO"):
        print("  rejected html", flush=True)
        return False
    if not (data[:3] == b"\xff\xd8\xff" or data[:8] == b"\x89PNG\r\n\x1a\n" or data[:4] == b"RIFF"):
        print("  bad magic", flush=True)
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return True


def copy_foods() -> None:
    for src_rel, dest in FOOD_COPIES:
        src = ROOT / src_rel
        if not src.exists():
            print(f"! missing source {src_rel}", flush=True)
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        print(f"+ copy {dest.name} <- {src_rel} ({dest.stat().st_size})", flush=True)


def fetch_one(job: dict) -> bool:
    dest = job["dest"]
    if dest.exists() and dest.stat().st_size > 20000:
        print(f"= skip existing {dest.name}", flush=True)
        return True
    titles = list(job.get("titles") or [])
    for t in commons_search(job.get("search") or dest.stem, limit=6):
        if t not in titles:
            titles.append(t)
    for title in titles:
        if not ok_title(title):
            continue
        print(f"  try {title}", flush=True)
        if save_image(special_filepath(title), dest):
            print(f"+ {dest.name} <- {title} ({dest.stat().st_size})", flush=True)
            return True
        time.sleep(0.8)
    print(f"! FAIL {dest.name}", flush=True)
    return False


def main() -> int:
    print("## copy unique food photos", flush=True)
    copy_foods()
    ok = fail = 0
    for job in JOBS:
        print(f"\n## {job['dest'].name}", flush=True)
        if fetch_one(job):
            ok += 1
        else:
            fail += 1
        time.sleep(1.4)
    print(f"\ndone fetch ok={ok} fail={fail}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
