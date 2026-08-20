# -*- coding: utf-8 -*-
"""Safely re-geocode place markers: region-biased Nominatim + jump guard."""
from __future__ import annotations

import argparse
import json
import math
import re
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COORDS = ROOT / "data" / "places" / "places-coords.js"
KO_I18N = ROOT / "i18n" / "pages" / "transport" / "ko.json"
UA = "KoreaTravelGuidebook/1.0 (safe coord fix; local)"

TYPES = {"city", "nature", "mountain", "beach", "market"}

# Reject Nominatim hits farther than this from current coords (km)
MAX_JUMP_KM = 25.0
# Apply only if move is at least this far (m)
MIN_MOVE_M = 80.0

REGION_KO = {
    "seoul": "서울",
    "busan": "부산",
    "incheon": "인천",
    "daegu": "대구",
    "daejeon": "대전",
    "gwangju": "광주",
    "ulsan": "울산",
    "sejong": "세종",
    "gyeonggi": "경기",
    "gangwon": "강원",
    "chungbuk": "충북",
    "chungnam": "충남",
    "chungcheong": "충청",
    "jeonbuk": "전북",
    "jeonnam": "전남",
    "jeolla": "전라",
    "gyeongbuk": "경북",
    "gyeongnam": "경남",
    "gyeongsang": "경상",
    "jeju": "제주",
}

# Authoritative coords for ambiguous / famous places
OVERRIDES: dict[str, tuple[float, float]] = {
    "gyeongbok": (37.5796, 126.9770),
    "myeongdong": (37.5636, 126.9869),
    "gangnam": (37.4979, 127.0276),
    "hongdae": (37.5563, 126.9236),
    "itaewon": (37.5345, 126.9946),
    "namsan": (37.5512, 126.9882),
    "dongdaemun": (37.5668, 127.0094),
    "lotte-tower": (37.5126, 127.1025),
    "cheonggyecheon": (37.5695, 126.9788),
    "seoul-forest": (37.5445, 127.0376),
    "seongsu-dong": (37.5445, 127.0557),
    "apgujeong": (37.5272, 127.0286),
    "cheongdam": (37.5245, 127.0470),
    "coex": (37.5115, 127.0590),
    "byeolmadang-library": (37.5112, 127.0594),
    "hangang-yeouido": (37.5285, 126.9340),
    "hangang-banpo": (37.5105, 126.9960),
    "noryangjin-cupbap": (37.5135, 126.9405),
    "noryangjin-fish-market": (37.5148, 126.9408),
    "gwangjang-market": (37.5700, 126.9996),
    "namdaemun-market": (37.5595, 126.9775),
    "tongin-market": (37.5808, 126.9700),
    "mangwon-market": (37.5566, 126.9061),
    "dongdaemun-market": (37.5705, 127.0095),
    "goyang": (37.6580, 126.7695),  # Ilsan Lake Park
    "gapyeong": (37.7915, 127.5258),
    "everland": (37.2940, 127.2023),
    "songdo": (37.3928, 126.6388),
    "haeundae": (35.1587, 129.1604),
    "nampo": (35.0969, 129.0306),
    "seomyeon": (35.1575, 129.0595),
    "jagalchi-market": (35.0969, 129.0306),
    "gukje-market": (35.1012, 129.0282),
    "biff-square": (35.0989, 129.0291),
    "dongseong-ro": (35.8695, 128.5955),  # Daegu
    "83-tower": (35.8535, 128.5663),
    "eworld": (35.8538, 128.5660),
    "seomun-market": (35.8694, 128.5807),
    "chilseong-market": (35.8761, 128.6051),
    "jeonju": (35.8150, 127.1530),
    "jeonju-nambu-market": (35.8120, 127.1290),
    "jeonju-jungang-market": (35.8165, 127.1485),
    "tongyeong": (34.8544, 128.4330),
    "tongyeong-jungang-market": (34.8452, 128.4245),
    "ulsan-daewangam": (35.4925, 129.4405),
    "boseong": (34.7140, 127.0810),
    "suncheon-bay": (34.8852, 127.5103),
    "hallasan": (33.3617, 126.5292),
    "seongsan": (33.4581, 126.9425),
    "jungmun": (33.2427, 126.4127),
    "jeju-dongmun-market": (33.5115, 126.5290),
    "seogwipo-maeil-olle-market": (33.2502, 126.5636),
    "seoraksan": (38.1195, 128.4654),
    "bulguksa": (35.7900, 129.3320),
    "donggung": (35.8347, 129.2268),
}


def ssl_ctx() -> ssl.SSLContext:
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl._create_unverified_context()


def haversine_km(a_lat: float, a_lng: float, b_lat: float, b_lng: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(a_lat), math.radians(b_lat)
    dphi = math.radians(b_lat - a_lat)
    dl = math.radians(b_lng - a_lng)
    x = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(min(1.0, math.sqrt(x)))


def load_names() -> dict[str, str]:
    data = json.loads(KO_I18N.read_text(encoding="utf-8"))
    places = data.get("places") or {}
    out: dict[str, str] = {}
    for slug, meta in places.items():
        if isinstance(meta, dict) and meta.get("name"):
            out[slug] = str(meta["name"])
    return out


def nominatim_search(
    query: str,
    *,
    near: tuple[float, float] | None = None,
    limit: int = 5,
) -> list[tuple[float, float, str]]:
    params: dict[str, str] = {
        "q": query,
        "format": "json",
        "limit": str(limit),
        "countrycodes": "kr",
        "addressdetails": "0",
    }
    if near:
        lat, lng = near
        # ~0.35 deg ~ 30–40km box
        delta = 0.35
        params["viewbox"] = f"{lng - delta},{lat + delta},{lng + delta},{lat - delta}"
        params["bounded"] = "1"
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=25, context=ssl_ctx()) as r:
            rows = json.loads(r.read().decode())
    except Exception as exc:  # noqa: BLE001
        print(f"  nominatim err: {exc}", flush=True)
        return []
    out: list[tuple[float, float, str]] = []
    for row in rows or []:
        try:
            out.append(
                (
                    float(row["lat"]),
                    float(row["lon"]),
                    str(row.get("display_name") or "")[:80],
                )
            )
        except (KeyError, TypeError, ValueError):
            continue
    return out


def pick_hit(
    candidates: list[tuple[float, float, str]],
    old_lat: float,
    old_lng: float,
) -> tuple[float, float, str] | None:
    if not candidates:
        return None
    best = None
    best_d = 1e18
    for lat, lng, label in candidates:
        d = haversine_km(old_lat, old_lng, lat, lng)
        if d < best_d:
            best_d = d
            best = (lat, lng, label)
    if best is None or best_d > MAX_JUMP_KM:
        return None
    return best


def region_label(region: str) -> str:
    return REGION_KO.get(region.strip().lower(), "") if region else ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Write places-coords.js")
    ap.add_argument(
        "--types",
        default=",".join(sorted(TYPES)),
        help="Comma-separated types",
    )
    args = ap.parse_args()
    types = {t.strip() for t in args.types.split(",") if t.strip()}

    names = load_names()
    text = COORDS.read_text(encoding="utf-8")
    pat = re.compile(
        r'\{ slug: "([^"]+)", lat: ([-\d.]+), lng: ([-\d.]+), region: "([^"]*)", type: "([^"]+)"([^}]*)\}',
        re.M,
    )

    updated = 0
    checked = 0
    failed = 0
    rejected = 0
    overrides_n = 0
    changes: list[tuple[str, float, float, float, float]] = []

    def repl(m: re.Match) -> str:
        nonlocal updated, checked, failed, rejected, overrides_n
        slug, lat_s, lng_s, region, typ, rest = m.groups()
        if typ not in types:
            return m.group(0)
        checked += 1
        old_lat, old_lng = float(lat_s), float(lng_s)

        if slug in OVERRIDES:
            lat, lng = OVERRIDES[slug]
            overrides_n += 1
            d_km = haversine_km(old_lat, old_lng, lat, lng)
            if d_km * 1000 < MIN_MOVE_M:
                return m.group(0)
            updated += 1
            changes.append((slug, old_lat, old_lng, lat, lng))
            print(
                f"  OVERRIDE {slug}: ({old_lat},{old_lng}) -> ({lat:.5f},{lng:.5f}) "
                f"[{d_km:.2f}km]",
                flush=True,
            )
            return (
                f'{{ slug: "{slug}", lat: {round(lat, 5)}, lng: {round(lng, 5)}, '
                f'region: "{region}", type: "{typ}"{rest}}}'
            )

        name = names.get(slug) or slug.replace("-", " ")
        # Strip decorative separators that confuse Nominatim
        name_clean = re.sub(r"[·•|/].*$", "", name).strip() or name
        rko = region_label(region)
        queries = []
        if rko:
            queries.append(f"{name_clean}, {rko}")
        queries.append(f"{name_clean}, 대한민국")
        if name_clean != name:
            queries.append(name)

        print(f"geocode {slug} <- {name_clean}" + (f" [{rko}]" if rko else ""), flush=True)
        hit = None
        for q in queries:
            time.sleep(1.1)
            cands = nominatim_search(q, near=(old_lat, old_lng), limit=5)
            hit = pick_hit(cands, old_lat, old_lng)
            if hit:
                break
            # Retry without bounded viewbox if empty
            time.sleep(1.1)
            cands = nominatim_search(q, near=None, limit=5)
            hit = pick_hit(cands, old_lat, old_lng)
            if hit:
                break

        if not hit:
            failed += 1
            print(f"  MISS {slug}", flush=True)
            return m.group(0)

        lat, lng, label = hit
        d_km = haversine_km(old_lat, old_lng, lat, lng)
        if d_km > MAX_JUMP_KM:
            rejected += 1
            print(f"  REJECT {slug} jump {d_km:.1f}km -> {label}", flush=True)
            return m.group(0)
        if d_km * 1000 < MIN_MOVE_M:
            return m.group(0)

        updated += 1
        changes.append((slug, old_lat, old_lng, lat, lng))
        print(
            f"  FIX {slug}: ({old_lat},{old_lng}) -> ({lat:.5f},{lng:.5f}) "
            f"[{d_km:.2f}km] {label}",
            flush=True,
        )
        return (
            f'{{ slug: "{slug}", lat: {round(lat, 5)}, lng: {round(lng, 5)}, '
            f'region: "{region}", type: "{typ}"{rest}}}'
        )

    new_text = pat.sub(repl, text)
    print(
        f"\nsummary checked={checked} updated={updated} overrides={overrides_n} "
        f"miss={failed} rejected={rejected} apply={args.apply}",
        flush=True,
    )
    if args.apply and updated:
        COORDS.write_text(new_text, encoding="utf-8", newline="\n")
        print(f"wrote {COORDS}", flush=True)
    elif not args.apply:
        print("dry-run only (pass --apply to write)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
