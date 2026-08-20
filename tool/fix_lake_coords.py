# -*- coding: utf-8 -*-
"""Fix lake-type marker coords: curated overrides + region-biased Nominatim."""
from __future__ import annotations

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
UA = "KoreaTravelGuidebook/1.0 (lake coord fix; local)"

MAX_JUMP_KM = 40.0
MIN_MOVE_M = 50.0

REGION_KO = {
    "seoul": "서울",
    "gyeonggi": "경기",
    "gangwon": "강원",
    "chungbuk": "충북",
    "chungnam": "충남",
    "chungcheong": "충청",
    "jeolla": "전라",
    "gyeongsang": "경상",
    "jeju": "제주",
    "": "",
}

# Nominatim-verified (or curated when Nominatim miss/wrong)
OVERRIDES: dict[str, tuple[float, float]] = {
    "goyang": (37.65753, 126.76423),
    "suseong-mot": (35.8290, 128.6175),
    "suncheon-bay": (34.8852, 127.5103),
    "seokchon-lake": (37.51009, 127.10408),
    "sanjeong-lake": (38.07096, 127.32096),
    "baegun-lake": (37.37953, 127.00244),
    "wangsong-lake": (37.31791, 126.94584),
    "homyeong-lake": (37.74888, 127.47557),
    "geumgwang-lake": (37.0535, 127.3125),
    "seolbong-lake": (37.27745, 127.43085),
    "sihwa-lake": (37.29726, 126.66935),
    "gyeongpo-lake": (37.79719, 128.90282),
    "soyang-lake": (37.94484, 127.81384),
    "yeongnang-lake": (38.21740, 128.58051),
    "songji-lake": (38.33541, 128.51132),
    "hongcheon-palbong-lake": (37.69588, 127.69712),
    "paro-lake": (38.14421, 127.90819),
    "soyang-lake-inje": (37.99265, 128.05334),
    "chungju-lake": (36.98041, 128.00564),
    "cheongpung-lake": (37.0035, 128.1715),
    "goesan-lake": (36.74817, 127.84175),
    "daecheong-lake": (36.41862, 127.49711),
    "sapgyo-lake": (36.86206, 126.83619),
    "boryeong-lake": (36.25430, 126.67167),
    "eunpa-lake-park": (35.95095, 126.69608),
    "naejang-lake": (35.4968, 126.8918),
    "yeongsan-lake": (34.77627, 126.45467),
    "damyang-lake": (35.40035, 127.00940),
    "jangseong-lake": (35.38749, 126.83942),
    "junam-reservoir": (35.31824, 128.67528),
    "jinyang-lake": (35.17402, 128.02955),
    "andong-lake": (36.63576, 128.84789),
    "jusanji": (36.36265, 129.19009),
    "bomun-lake": (35.84476, 129.27738),
    "yeongcheon-lake": (36.08381, 129.05053),
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


def nominatim_search(query: str, near: tuple[float, float] | None, limit: int = 5):
    params: dict[str, str] = {
        "q": query,
        "format": "json",
        "limit": str(limit),
        "countrycodes": "kr",
    }
    if near:
        lat, lng = near
        delta = 0.45
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
    out = []
    for row in rows or []:
        try:
            out.append((float(row["lat"]), float(row["lon"]), str(row.get("display_name") or "")[:90]))
        except (KeyError, TypeError, ValueError):
            continue
    return out


def pick_hit(cands, old_lat, old_lng):
    best = None
    best_d = 1e18
    for lat, lng, label in cands:
        d = haversine_km(old_lat, old_lng, lat, lng)
        if d < best_d:
            best_d = d
            best = (lat, lng, label, d)
    if best is None or best[3] > MAX_JUMP_KM:
        return None
    return best


def main() -> int:
    names = load_names()
    text = COORDS.read_text(encoding="utf-8")
    pat = re.compile(
        r'\{ slug: "([^"]+)", lat: ([-\d.]+), lng: ([-\d.]+), region: "([^"]*)", type: "lake"([^}]*)\}',
        re.M,
    )

    updated = 0
    checked = 0
    missed = 0

    def repl(m: re.Match) -> str:
        nonlocal updated, checked, missed
        slug, lat_s, lng_s, region, rest = m.groups()
        checked += 1
        old_lat, old_lng = float(lat_s), float(lng_s)

        if slug in OVERRIDES:
            lat, lng = OVERRIDES[slug]
            d = haversine_km(old_lat, old_lng, lat, lng)
            if d * 1000 < MIN_MOVE_M:
                print(f"  OK {slug} (within {d*1000:.0f}m)", flush=True)
                return m.group(0)
            updated += 1
            print(
                f"  OVERRIDE {slug}: ({old_lat},{old_lng}) -> ({lat:.5f},{lng:.5f}) [{d:.2f}km]",
                flush=True,
            )
            return (
                f'{{ slug: "{slug}", lat: {round(lat, 5)}, lng: {round(lng, 5)}, '
                f'region: "{region}", type: "lake"{rest}}}'
            )

        name = names.get(slug) or slug.replace("-", " ")
        name_clean = re.sub(r"[·•|/].*$", "", name).strip() or name
        rko = REGION_KO.get(region, region)
        queries = []
        if rko:
            queries.append(f"{name_clean}, {rko}")
        queries.append(f"{name_clean}, 대한민국")

        print(f"geocode {slug} <- {name_clean}" + (f" [{rko}]" if rko else ""), flush=True)
        hit = None
        for q in queries:
            time.sleep(1.1)
            hit = pick_hit(nominatim_search(q, (old_lat, old_lng)), old_lat, old_lng)
            if hit:
                break
            time.sleep(1.1)
            hit = pick_hit(nominatim_search(q, None), old_lat, old_lng)
            if hit:
                break

        if not hit:
            missed += 1
            print(f"  MISS {slug}", flush=True)
            return m.group(0)

        lat, lng, label, d = hit
        if d * 1000 < MIN_MOVE_M:
            print(f"  OK {slug}", flush=True)
            return m.group(0)
        updated += 1
        print(
            f"  FIX {slug}: ({old_lat},{old_lng}) -> ({lat:.5f},{lng:.5f}) [{d:.2f}km] {label}",
            flush=True,
        )
        return (
            f'{{ slug: "{slug}", lat: {round(lat, 5)}, lng: {round(lng, 5)}, '
            f'region: "{region}", type: "lake"{rest}}}'
        )

    new_text = pat.sub(repl, text)
    COORDS.write_text(new_text, encoding="utf-8", newline="\n")
    print(f"\ndone checked={checked} updated={updated} miss={missed}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
