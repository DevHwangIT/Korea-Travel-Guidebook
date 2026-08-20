# -*- coding: utf-8 -*-
"""Second-pass city photo fetch for misses / rejected images."""
from __future__ import annotations

import hashlib
import json
import re
import ssl
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "Images" / "places"
TYPE_FALLBACK = IMG / "_types" / "city.jpg"
UA = "KoreaTravelGuidebook/1.0 (city covers pass2; educational)"
CTX = None
SLEEP = 3.2

# Force re-download even if currently a non-fallback file
FORCE = {
    "busan-x-the-sky",  # construction site — reject
    "wolmido",  # ondol kitchen — wrong subject
    "cheongdam",  # generic boulevard — weak match
}

TARGETS: dict[str, dict] = {
    "seouldal": {
        "files": [],
        "search": [
            "서울달 Hongdae",
            "giant moon sculpture Seoul Hongdae",
            "Hongdae night street Seoul",
        ],
    },
    "coex": {
        "files": [
            "COEX Mall and Trade Tower.jpg",
            "COEX Aquarium.jpg",
            "Samsungdong COEX.jpg",
            "Korea-Seoul-Trade Tower-01.jpg",
            "Trade Tower Seoul.jpg",
            "Bongeunsa and COEX.jpg",
        ],
        "search": [
            "COEX Seoul Trade Tower",
            "코엑스 무역센터",
            "COEX Convention Center Seoul exterior",
        ],
    },
    "apgujeong": {
        "files": [
            "Apgujeong Rodeo Stantion Exit 2 2012.JPG",
            "Galleria Department Store Apgujeong.jpg",
            "Apgujeong Gallery.jpg",
        ],
        "search": [
            "Apgujeong Rodeo Street",
            "압구정로데오",
            "Galleria Apgujeong Seoul",
        ],
    },
    "cheongdam": {
        "files": [],
        "search": [
            "Cheongdam-dong Seoul street",
            "청담동 거리",
            "Cheongdam fashion street",
        ],
    },
    "busan-x-the-sky": {
        "files": [
            "Haeundae Marine City and beach.jpg",
            "Marine City Haeundae night.jpg",
            "Haeundae skyline.jpg",
            "Busan Haeundae highrise.jpg",
        ],
        "search": [
            "Signiel Busan tower",
            "Lotte World Tower Busan Haeundae",
            "Haeundae Marine City skyscraper",
            "부산 해운대 마린시티 야경",
        ],
        "reject": re.compile(r"(?i)construction|공사|building site|excavation"),
    },
    "lotte-world-adventure-busan": {
        "files": [],
        "search": [
            "Lotte World Adventure Busan",
            "Osiria Busan theme park",
            "롯데월드 부산 기장",
            "Busan Osiria amusement",
        ],
    },
    "the-bay-101": {
        "files": [],
        "search": [
            "The Bay 101 Busan",
            "더베이101",
            "Marine City Busan yacht",
            "Haeundae Marine City waterfront",
        ],
    },
    "wolmido": {
        "files": [
            "Wolmido Playground.jpg",
            "Wolmi Park Incheon.jpg",
            "Incheon Wolmido.jpg",
            "월미도.jpg",
        ],
        "search": [
            "Wolmido amusement park Incheon",
            "월미도 놀이공원",
            "Wolmi Island Incheon waterfront",
            "Wolmido ferry Incheon",
        ],
        "reject": re.compile(r"(?i)ondol|stove|kitchen|agungi|가마솥"),
    },
    "inspire-resort": {
        "files": [],
        "search": [
            "Inspire Entertainment Resort Incheon",
            "인스파이어 리조트",
            "Inspire Arena Yeongjong",
        ],
    },
    "paradise-city": {
        "files": [],
        "search": [
            "Paradise City Incheon resort",
            "파라다이스시티 인천",
            "Paradise City Yeongjong Island",
            "Incheon casino resort Paradise",
        ],
    },
    "hyundai-premium-outlet-songdo": {
        "files": [],
        "search": [
            "Hyundai Premium Outlet Songdo",
            "현대프리미엄아울렛 송도",
            "Songdo outlet mall Incheon",
            "Songdo shopping mall exterior",
        ],
    },
    "83-tower": {
        "files": [
            "83 Tower Daegu at night.jpg",
            "E-World 83 Tower.jpg",
            "Daegu E-World Tower night.jpg",
        ],
        "search": [
            "E-World Daegu tower night",
            "83타워 대구",
            "우방타워 대구",
            "Duryu Park Tower Daegu",
            "E WORLD Daegu observation tower",
        ],
        "reject": re.compile(r"(?i)eiffel|paris|lightning"),
    },
    "daegu-shinsegae": {
        "files": [
            "Dongdaegu Station.jpg",
            "Dongdaegu Station exterior.jpg",
            "Korea-Daegu-Dongdaegu Station-01.jpg",
        ],
        "search": [
            "Dongdaegu Station Shinsegae",
            "동대구역 신세계",
            "Dongdaegu Station exterior",
            "Daegu Shinsegae department store",
        ],
    },
    "aquaplanet-yeosu": {
        "files": [],
        "search": [
            "Aqua Planet Yeosu exterior",
            "아쿠아플라넷 여수",
            "Yeosu aquarium Odongdo",
            "Yeosu Expo aquarium",
        ],
    },
    "yeosu-nangman-pocha": {
        "files": [],
        "search": [
            "Yeosu night harbor street food",
            "여수 낭만포차",
            "Yeosu waterfront night market",
            "Yeosu Jungang-dong night",
            "Yeosu Expo night view",
        ],
    },
    "arte-museum-jeju": {
        "files": [],
        "search": [
            "Arte Museum Jeju",
            "ARTE Museum Jeju Aewol",
            "아르떼뮤지엄 제주",
            "Jeju immersive media art museum",
        ],
    },
    "981-park": {
        "files": [],
        "search": [
            "9.81 Park Jeju",
            "981파크 제주",
            "Gravity Race Jeju 9.81",
            "Jeju Aewol theme park 9.81",
        ],
    },
    "nohyeong-supermarket": {
        "files": [],
        "search": [
            "Nohyeong Supermarket Jeju",
            "노형슈퍼마켓",
            "Nohyeong cafe Jeju museum",
            "Jeju Nohyeong shopping street",
        ],
    },
}

REJECT_TITLE = re.compile(
    r"(?i)\b(map|logo|icon|flag|svg|diagram|chart|poster|stamp|pdf|scan|"
    r"coat of arms|emblem|qr|infobox|location map|construction site)\b"
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


def http_get(url: str, timeout: int = 50) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx()) as r:
        return r.read()


def imageinfo(title: str, width: int = 1280) -> dict | None:
    api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "query",
            "titles": f"File:{title}",
            "prop": "imageinfo",
            "iiprop": "url|mime|size",
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
        return infos[0] if infos else None
    return None


def commons_search(query: str, limit: int = 10) -> list[str]:
    api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "query",
            "list": "search",
            "srsearch": f"{query} filetype:bitmap",
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


def usable(title: str, extra_reject: re.Pattern | None = None) -> bool:
    if not title:
        return False
    low = title.lower()
    if low.endswith((".pdf", ".svg", ".gif", ".tif", ".tiff", ".djvu")):
        return False
    if REJECT_TITLE.search(title):
        return False
    if extra_reject and extra_reject.search(title):
        return False
    return True


def save_image(url: str, dest: Path) -> bool:
    try:
        data = http_get(url, timeout=90)
    except Exception as exc:  # noqa: BLE001
        print(f"  dl err: {exc}", flush=True)
        return False
    if len(data) < 15000:
        print(f"  too small ({len(data)})", flush=True)
        return False
    head = data[:32].lstrip()
    if head.startswith(b"<") or head.startswith(b"%PDF"):
        print("  rejected non-image", flush=True)
        return False
    if not (
        data[:3] == b"\xff\xd8\xff"
        or data[:8] == b"\x89PNG\r\n\x1a\n"
        or data[:4] == b"RIFF"
    ):
        print("  bad magic", flush=True)
        return False
    dest.write_bytes(data)
    return True


def try_one(slug: str, title: str, dest: Path, fb: str, rej) -> bool:
    if not usable(title, rej):
        print(f"  skip {title}", flush=True)
        return False
    print(f"TRY {slug} <- {title}", flush=True)
    time.sleep(SLEEP)
    info = imageinfo(title)
    url = None
    if info:
        mime = (info.get("mime") or "").lower()
        if mime and not mime.startswith("image/"):
            print(f"  mime {mime}", flush=True)
            return False
        url = info.get("thumburl") or info.get("url")
    if not url:
        time.sleep(1.0)
        url = special_filepath(title)
    time.sleep(0.8)
    if not save_image(url, dest):
        return False
    if fb and md5(dest) == fb:
        return False
    print(f"  OK {dest.stat().st_size}", flush=True)
    return True


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    fb = md5(TYPE_FALLBACK) if TYPE_FALLBACK.exists() else ""
    ok, miss = [], []
    log = {}

    for slug, cfg in TARGETS.items():
        dest = IMG / f"{slug}.jpg"
        if dest.exists() and fb and md5(dest) != fb and slug not in FORCE:
            print(f"KEEP {slug}", flush=True)
            ok.append(slug)
            continue

        # Restore fallback before retry for forced rejects
        if slug in FORCE and TYPE_FALLBACK.exists():
            dest.write_bytes(TYPE_FALLBACK.read_bytes())

        candidates: list[str] = list(cfg.get("files") or [])
        for q in cfg.get("search") or []:
            time.sleep(SLEEP)
            for t in commons_search(q):
                if t not in candidates:
                    candidates.append(t)

        rej = cfg.get("reject")
        success = False
        used = None
        for title in candidates:
            if try_one(slug, title, dest, fb, rej):
                success = True
                used = title
                break
            time.sleep(0.8)

        if success:
            ok.append(slug)
            log[slug] = {"status": "ok", "file": used}
            print(f"OK {slug} <- {used}", flush=True)
        else:
            miss.append(slug)
            log[slug] = {"status": "miss"}
            print(f"MISS {slug}", flush=True)
        time.sleep(2.0)

    still = []
    for slug in TARGETS:
        p = IMG / f"{slug}.jpg"
        if not p.exists() or (fb and md5(p) == fb):
            still.append(slug)

    summary = {
        "ok": ok,
        "miss": miss,
        "still_fallback": still,
        "log": log,
    }
    (ROOT / "tool" / "_city_image_pass2_log.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nPASS2 ok={len(ok)} miss={len(miss)} still={len(still)}", flush=True)
    if still:
        print("STILL:", ", ".join(still), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
