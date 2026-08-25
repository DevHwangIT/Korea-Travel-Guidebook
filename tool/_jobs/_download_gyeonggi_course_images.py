# -*- coding: utf-8 -*-
"""Download place-specific photos for Gyeonggi curated courses (Wikimedia Commons).

Prefer architecture / landscape of the actual stop. Skip portraits, maps, logos.
"""
from __future__ import annotations

import json
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMG = ROOT / "Images" / "places" / "_courses"
UA = "KoreaTravelGuidebook/1.0 (gyeonggi course covers; educational; rate-limited)"
SLEEP = 1.8

# slug -> preferred Commons File: titles (first usable wins)
FILES: dict[str, list[str]] = {
    "suwon-hwaseong": [
        "Korea-Suwon-Hwaseong Fortress-02.jpg",
        "Korea-Suwon-Hwaseong Fortress-01.jpg",
        "Hwaseong Fortress, Suwon 04.jpg",
        "Suwon Hwaseong Fortress.jpg",
        "Janganmun Gate of Hwaseong Fortress.jpg",
        "Hwaseong Fortress walls.jpg",
        "Paldalmun, Suwon.jpg",
    ],
    "banghwasuryujeong": [
        "Korea-Suwon-Hwaseong Fortress-Banghwasuryujeong-01.jpg",
        "Banghwasuryujeong.jpg",
        "Banghwasuryujeong Pavilion.jpg",
        "방화수류정.jpg",
        "Hwaseong Fortress Banghwasuryujeong.jpg",
    ],
    "haengnidangil": [
        "Haenggung-dong, Suwon.jpg",
        "Haenggung-dong.jpg",
        "행궁동.jpg",
        "Suwon Haenggung-dong street.jpg",
    ],
    "suwon-hwaseong-night": [
        "Hwaseong Fortress night.jpg",
        "Suwon Hwaseong Fortress at night.jpg",
        "Korea-Suwon-Hwaseong Fortress-Night-01.jpg",
        "Hwaseong Fortress illuminated.jpg",
    ],
    "petit-france": [
        "Petite France Gapyeong.jpg",
        "Petite France, Gapyeong.jpg",
        "Gapyeong Petite France.jpg",
        "Petite France (South Korea).jpg",
        "쁘띠프랑스.jpg",
        "Petite France Korea.jpg",
    ],
    "garden-of-morning-calm": [
        "The Garden of Morning Calm.jpg",
        "Garden of Morning Calm.jpg",
        "The Garden of Morning Calm 01.jpg",
        "아침고요수목원.jpg",
        "Garden of Morning Calm Gapyeong.jpg",
    ],
    "heyri": [
        "Heyri Art Valley.jpg",
        "Heyri Art Village.jpg",
        "Paju Heyri.jpg",
        "헤이리 예술마을.jpg",
        "Heyri.jpg",
    ],
    "dmz-dora": [
        "Dora Observatory.jpg",
        "Dora Observatory, Paju.jpg",
        "제3땅굴.jpg",
        "Third Infiltration Tunnel.jpg",
        "Dorasan Station.jpg",
        "Freedom Bridge Imjingak.jpg",
    ],
    "dumulmeori": [
        "Dumulmeori.jpg",
        "두물머리.jpg",
        "Yangpyeong Dumulmeori.jpg",
        "Dumulmeori Yangpyeong.jpg",
        "Two Water Streams Head Yangpyeong.jpg",
    ],
    "semiwon": [
        "Semiwon.jpg",
        "세미원.jpg",
        "Yangpyeong Semiwon.jpg",
        "Semiwon lotus.jpg",
        "Semiwon Garden.jpg",
    ],
    "hangukminsokchon-village": [
        "Korean Folk Village.jpg",
        "Korean Folk Village Yongin.jpg",
        "한국민속촌.jpg",
        "Korean Folk Village 1.jpg",
        "Yongin Korean Folk Village hanok.jpg",
    ],
    "bojeong-cafe": [
        "Bojeong-dong Cafe Street.jpg",
        "보정동 카페거리.jpg",
        "Bojeong-dong.jpg",
        "Jukjeon cafe street.jpg",
    ],
    "namhansanseong-fortress": [
        "Namhansanseong Fortress.jpg",
        "Namhansanseong.jpg",
        "남한산성.jpg",
        "Namhansanseong South Gate.jpg",
        "남한산성 남문.jpg",
        "Namhansanseong fortress wall.jpg",
    ],
    "pocheon-art-valley": [
        "Pocheon Art Valley.jpg",
        "포천아트밸리.jpg",
        "Pocheon Art Valley 01.jpg",
        "Cheonjuho Lake Pocheon.jpg",
        "Pocheon Art Valley granite.jpg",
    ],
    "yeoju-outlet": [
        "Yeoju Premium Outlets.jpg",
        "여주프리미엄아울렛.jpg",
        "Yeoju Premium Outlet.jpg",
        "Simon Premium Outlets Yeoju.jpg",
    ],
    "gwangmyeong-cave": [
        "Gwangmyeong Cave.jpg",
        "광명동굴.jpg",
        "Inside Gwangmyeong Cave.jpg",
        "Gwangmyeong Cave interior.jpg",
        "Gwangmyeong Cave 광명동굴.jpg",
    ],
    "gwangmyeong-market": [
        "Gwangmyeong Traditional Market.jpg",
        "광명전통시장.jpg",
        "Gwangmyeong Market.jpg",
    ],
    "imjingak-peace": [
        "Imjingak Peace Park.jpg",
        "Imjingak.jpg",
        "임진각.jpg",
        "Mangbaedan Altar Imjingak.jpg",
        "Peace Nuri Park Imjingak.jpg",
    ],
    "everland-night": [
        "Everland at night.jpg",
        "Everland night.jpg",
        "Everland illumination.jpg",
        "Everland T Express night.jpg",
    ],
    "namhangang-yangpyeong": [
        "Namhan River Yangpyeong.jpg",
        "남한강 양평.jpg",
        "Namhangang.jpg",
        "Yangpyeong Namhan River.jpg",
    ],
}

SEARCH: dict[str, str] = {
    "suwon-hwaseong": "Hwaseong Fortress Suwon wall gate Janganmun",
    "banghwasuryujeong": "Banghwasuryujeong Hwaseong Suwon pavilion",
    "haengnidangil": "Haenggung-dong Suwon street 행궁동",
    "suwon-hwaseong-night": "Hwaseong Fortress Suwon night illumination",
    "petit-france": "Petite France Gapyeong Korea",
    "garden-of-morning-calm": "Garden of Morning Calm Gapyeong",
    "heyri": "Heyri Art Village Paju",
    "dmz-dora": "Dora Observatory Paju DMZ",
    "dumulmeori": "Dumulmeori Yangpyeong",
    "semiwon": "Semiwon Yangpyeong lotus",
    "hangukminsokchon-village": "Korean Folk Village Yongin hanok",
    "bojeong-cafe": "Bojeong-dong cafe street Yongin",
    "namhansanseong-fortress": "Namhansanseong Fortress wall gate",
    "pocheon-art-valley": "Pocheon Art Valley granite quarry",
    "yeoju-outlet": "Yeoju Premium Outlets exterior",
    "gwangmyeong-cave": "Gwangmyeong Cave interior mine",
    "gwangmyeong-market": "Gwangmyeong Traditional Market",
    "imjingak-peace": "Imjingak Peace Park Paju",
    "everland-night": "Everland Yongin night lights",
    "namhangang-yangpyeong": "Namhan River Yangpyeong",
}

REJECT = (
    "portrait",
    "selfie",
    "people",
    "crowd",
    "tourist",
    "logo",
    "map",
    "svg",
    "diagram",
    "flag",
    "cropped",
    "stamp",
    "coin",
    "document",
    "manuscript",
    "busking",
    "nongak",
    "performance",
    "ceremony",
    "soldier",
    "madonna",
    "shrine",
    "mass",
    "cat",
    "dog",
    "food",
    "dish",
    "meal",
)

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


def http_get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx()) as r:
        return r.read()


def special_filepath(title: str, width: int = 1280) -> str:
    enc = urllib.parse.quote(title.replace(" ", "_"))
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{enc}?width={width}"


def commons_search(query: str, limit: int = 12) -> list[str]:
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


def ok_title(title: str) -> bool:
    if not title:
        return False
    low = title.lower()
    if low.endswith((".pdf", ".svg", ".gif", ".tif", ".tiff", ".djvu", ".webm")):
        return False
    return not any(b in low for b in REJECT)


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
    if head.startswith(b"<") or head.startswith(b"<!DO"):
        print("  rejected html", flush=True)
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


def fetch_one(slug: str, force: bool = False) -> bool:
    dest = IMG / f"{slug}.jpg"
    if not force and dest.exists() and dest.stat().st_size > 20000:
        print(f"= skip existing {slug} ({dest.stat().st_size})", flush=True)
        return True

    titles = list(FILES.get(slug, []))
    for t in commons_search(SEARCH.get(slug, slug), limit=12):
        if t not in titles:
            titles.append(t)

    for title in titles:
        if not ok_title(title):
            print(f"  skip title: {title}", flush=True)
            continue
        url = special_filepath(title)
        print(f"  try {title}", flush=True)
        if save_image(url, dest):
            print(f"+ {slug} <- {title} ({dest.stat().st_size})", flush=True)
            return True
        time.sleep(1.0)
    print(f"! FAIL {slug}", flush=True)
    return False


def main() -> int:
    IMG.mkdir(parents=True, exist_ok=True)
    ok = 0
    fail = 0
    for slug in FILES:
        print(f"\n## {slug}", flush=True)
        if fetch_one(slug):
            ok += 1
        else:
            fail += 1
        time.sleep(SLEEP)
    print(f"\ndone ok={ok} fail={fail}", flush=True)
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
