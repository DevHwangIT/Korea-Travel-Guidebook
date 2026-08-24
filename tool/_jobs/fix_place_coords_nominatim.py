# -*- coding: utf-8 -*-
"""Re-geocode place markers via Nominatim using Korean names from i18n."""
from __future__ import annotations

import json
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COORDS = ROOT / "data" / "places" / "places-coords.js"
KO_I18N = ROOT / "i18n" / "pages" / "transport" / "ko.json"
UA = "KoreaTravelGuidebook/1.0 (coord fix; contact: local)"

# Focus types that were bulk-added with approximate coords
# (heritage is large — run separately if needed)
TYPES = {"city", "nature", "mountain", "beach", "market"}

# Hard overrides for well-known landmarks (authoritative)
OVERRIDES = {
    "gyeongbok": (37.5796, 126.9770),
    "myeongdong": (37.5636, 126.9869),
    "haeundae": (35.1587, 129.1604),
    "hallasan": (33.3617, 126.5292),
    "seongsan": (33.4581, 126.9425),
    "namsan": (37.5512, 126.9882),
    "bulguksa": (35.7900, 129.3320),
    "donggung": (35.8347, 129.2268),
    "jeonju": (35.8150, 127.1530),
    "gwangjang-market": (37.5700, 126.9996),
    "jagalchi-market": (35.0969, 129.0306),
}


def ssl_ctx() -> ssl.SSLContext:
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl._create_unverified_context()


def load_names() -> dict[str, str]:
    data = json.loads(KO_I18N.read_text(encoding="utf-8"))
    places = data.get("places") or {}
    out = {}
    for slug, meta in places.items():
        if isinstance(meta, dict) and meta.get("name"):
            out[slug] = str(meta["name"])
    return out


def nominatim(query: str) -> tuple[float, float] | None:
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {
            "q": query,
            "format": "json",
            "limit": "1",
            "countrycodes": "kr",
        }
    )
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=25, context=ssl_ctx()) as r:
            rows = json.loads(r.read().decode())
    except Exception as exc:  # noqa: BLE001
        print(f"  nominatim err: {exc}")
        return None
    if not rows:
        return None
    try:
        return float(rows[0]["lat"]), float(rows[0]["lon"])
    except (KeyError, TypeError, ValueError):
        return None


def main() -> int:
    names = load_names()
    text = COORDS.read_text(encoding="utf-8")
    # Match place objects
    pat = re.compile(
        r'\{ slug: "([^"]+)", lat: ([-\d.]+), lng: ([-\d.]+), region: "([^"]*)", type: "([^"]+)"([^}]*)\}',
        re.M,
    )
    updated = 0
    checked = 0
    failed = 0

    def repl(m: re.Match) -> str:
        nonlocal updated, checked, failed
        slug, lat_s, lng_s, region, typ, rest = m.groups()
        if typ not in TYPES:
            return m.group(0)
        checked += 1
        old_lat, old_lng = float(lat_s), float(lng_s)
        if slug in OVERRIDES:
            lat, lng = OVERRIDES[slug]
        else:
            name = names.get(slug) or slug.replace("-", " ")
            q = f"{name}, South Korea"
            print(f"geocode {slug} <- {name}", flush=True)
            time.sleep(1.1)
            hit = nominatim(q)
            if not hit:
                # try without South Korea suffix for local names
                time.sleep(1.1)
                hit = nominatim(name)
            if not hit:
                failed += 1
                print(f"  MISS {slug}", flush=True)
                return m.group(0)
            lat, lng = hit
        # Only apply if meaningfully different (> ~80m) or override
        dist = abs(lat - old_lat) + abs(lng - old_lng)
        if slug not in OVERRIDES and dist < 0.0008:
            return m.group(0)
        updated += 1
        print(f"  FIX {slug}: ({old_lat},{old_lng}) -> ({lat:.5f},{lng:.5f})", flush=True)
        return (
            f'{{ slug: "{slug}", lat: {round(lat, 5)}, lng: {round(lng, 5)}, '
            f'region: "{region}", type: "{typ}"{rest}}}'
        )

    new_text = pat.sub(repl, text)
    COORDS.write_text(new_text, encoding="utf-8", newline="\n")
    print(f"\ndone checked={checked} updated={updated} failed={failed}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
