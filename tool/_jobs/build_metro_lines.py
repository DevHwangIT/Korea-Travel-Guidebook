# -*- coding: utf-8 -*-
"""Fetch Seoul metro route geometries from Overpass → data/metro/line-*.geojson.

Also rebuilds metro-data.js (embedded fallback pack for places-map / metro-map).
"""
from __future__ import annotations

import json
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "metro"
CACHE_DIR = ROOT / "tool" / "_tmp" / "overpass-metro"
UA = "KoreaTravelGuidebook/1.0 (metro-lines rebuild)"

# id → official-ish color + Overpass relation matchers
LINES: dict[str, dict] = {
    "1": {
        "color": "#0052A4",
        "name": "1호선",
        "query": r'relation["type"="route"]["route"~"subway|train"]["name"~"1호선|Line 1"](36.5,126.0,38.2,128.2);',
    },
    "2": {
        "color": "#00A84D",
        "name": "2호선",
        "query": r'relation["type"="route"]["route"="subway"]["ref"="2"](36.8,126.5,37.8,127.4);',
    },
    "3": {
        "color": "#EF7C1C",
        "name": "3호선",
        "query": r'relation["type"="route"]["route"="subway"]["ref"="3"](36.8,126.5,37.8,127.4);',
    },
    "4": {
        "color": "#00A5E3",
        "name": "4호선",
        "query": r'relation["type"="route"]["route"~"subway|train"]["name"~"4호선|Line 4"](36.8,126.5,37.9,127.5);',
    },
    "5": {
        "color": "#996CAC",
        "name": "5호선",
        "query": r'relation["type"="route"]["route"="subway"]["ref"="5"](36.8,126.5,37.8,127.4);',
    },
    "6": {
        "color": "#CD7C2F",
        "name": "6호선",
        "query": r'relation["type"="route"]["route"="subway"]["ref"="6"](36.8,126.5,37.8,127.4);',
    },
    "7": {
        "color": "#747F00",
        "name": "7호선",
        "query": r'relation["type"="route"]["route"="subway"]["ref"="7"](36.8,126.4,37.8,127.4);',
    },
    "8": {
        "color": "#E35D4D",
        "name": "8호선",
        "query": r'relation["type"="route"]["route"="subway"]["ref"="8"](36.8,126.8,37.7,127.4);',
    },
    "9": {
        "color": "#B7A45C",
        "name": "9호선",
        "query": r'relation["type"="route"]["route"="subway"]["ref"="9"](36.8,126.5,37.7,127.3);',
    },
    "arex": {
        "color": "#0090D2",
        "name": "공항철도",
        "query": (
            r'relation["type"="route"]["route"~"subway|train|light_rail"]'
            r'["name"~"공항철도|AREX|Airport Railroad"](37.3,126.3,37.7,127.1);'
        ),
    },
    "gyeongui": {
        "color": "#77C4A3",
        "name": "경의중앙선",
        # OSM uses middle-dot name: 경의·중앙선
        "query": (
            r'relation["type"="route"]["route"="train"]'
            r'["name"~"경의"](36.8,126.4,38.0,127.6);'
        ),
    },
    "suin-bundang": {
        "color": "#F5A200",
        "name": "수인분당선",
        # OSM: 수인·분당선 (middle dot). Exclude 신분당 via name filter below.
        "query": (
            r'relation["type"="route"]["route"="train"]'
            r'["name"~"수인|분당"](36.9,126.5,37.7,127.5);'
        ),
    },
    "shinbundang": {
        "color": "#D31145",
        "name": "신분당선",
        "query": (
            r'relation["type"="route"]["route"~"subway|light_rail|train"]'
            r'["name"~"신분당|Shinbundang"](37.0,126.9,37.6,127.3);'
        ),
    },
    "sillim": {
        "color": "#6789CA",
        "name": "신림선",
        "query": (
            r'relation["type"="route"]["route"~"light_rail|subway"]'
            r'["name"~"신림선|Sillim Line"](37.4,126.9,37.55,127.05);'
        ),
    },
    # Regional metros (OSM). Prefer tool/build_regional_metro.py for fetch.
    "busan-1": {
        "color": "#F06A00",
        "name": "부산1호선",
        "query": (
            r'relation["type"="route"]["route"~"subway|light_rail"]'
            r'["name"~"부산.*1호선|Busan Metro Line 1|부산도시철도 1"](34.9,128.7,35.45,129.35);'
        ),
    },
    "busan-2": {
        "color": "#3CB44A",
        "name": "부산2호선",
        "query": (
            r'relation["type"="route"]["route"~"subway|light_rail"]'
            r'["name"~"부산.*2호선|Busan Metro Line 2|부산도시철도 2"](34.9,128.7,35.45,129.35);'
        ),
    },
    "busan-3": {
        "color": "#BB8C00",
        "name": "부산3호선",
        "query": (
            r'relation["type"="route"]["route"~"subway|light_rail"]'
            r'["name"~"부산.*3호선|Busan Metro Line 3|부산도시철도 3"](34.9,128.7,35.45,129.35);'
        ),
    },
    "busan-4": {
        "color": "#2178C4",
        "name": "부산4호선",
        "query": (
            r'relation["type"="route"]["route"~"subway|light_rail|monorail"]'
            r'["name"~"부산.*4|Busan.*Line 4|도시철도 4|안평"](35.05,128.95,35.3,129.2);'
        ),
    },
    "busan-gimhae": {
        "color": "#8FC31F",
        "name": "부산김해경전철",
        "query": (
            r'relation["type"="route"]["route"~"light_rail|subway"]'
            r'["name"~"김해경전철|Busan–Gimhae|Busan-Gimhae|부산김해"](35.0,128.7,35.35,129.15);'
        ),
    },
    "daegu-1": {
        "color": "#D93F0C",
        "name": "대구1호선",
        "query": (
            r'relation["type"="route"]["route"="subway"]'
            r'["name"~"대구.*1호선|Daegu Metro Line 1|대구도시철도 1"](35.7,128.4,36.05,128.85);'
        ),
    },
    "daegu-2": {
        "color": "#00AA80",
        "name": "대구2호선",
        "query": (
            r'relation["type"="route"]["route"="subway"]'
            r'["name"~"대구.*2호선|Daegu Metro Line 2|대구도시철도 2"](35.7,128.4,36.05,128.85);'
        ),
    },
    "daegu-3": {
        "color": "#FFB100",
        "name": "대구3호선",
        "query": (
            r'relation["type"="route"]["route"~"subway|light_rail|monorail"]'
            r'["name"~"대구.*3|Daegu.*Line 3|도시철도 3|모노레일"](35.75,128.45,36.0,128.8);'
        ),
    },
    "gwangju-1": {
        "color": "#009088",
        "name": "광주1호선",
        "query": (
            r'relation["type"="route"]["route"="subway"]'
            r'["name"~"광주.*1호선|Gwangju Metro|광주도시철도"](35.05,126.7,35.25,127.05);'
        ),
    },
    "daejeon-1": {
        "color": "#007448",
        "name": "대전1호선",
        "query": (
            r'relation["type"="route"]["route"="subway"]'
            r'["name"~"대전.*1호선|Daejeon Metro|대전도시철도"](36.2,127.25,36.45,127.55);'
        ),
    },
}

ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]


def _ssl_ctx() -> ssl.SSLContext:
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl._create_unverified_context()


def overpass(query_body: str) -> dict:
    q = f"[out:json][timeout:180];\n({query_body}\n);\nout body;\n>;\nout skel qt;"
    data = urllib.parse.urlencode({"data": q}).encode()
    last_err: Exception | None = None
    for ep in ENDPOINTS:
        req = urllib.request.Request(
            ep, data=data, headers={"User-Agent": UA, "Content-Type": "application/x-www-form-urlencoded"}
        )
        try:
            with urllib.request.urlopen(req, timeout=200, context=_ssl_ctx()) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            time.sleep(2)
    raise RuntimeError(f"Overpass failed: {last_err}")


def elements_to_ways(payload: dict) -> tuple[dict[int, dict], dict[int, tuple[float, float]]]:
    nodes: dict[int, tuple[float, float]] = {}
    ways: dict[int, dict] = {}
    for el in payload.get("elements") or []:
        t = el.get("type")
        if t == "node":
            nodes[el["id"]] = (el["lon"], el["lat"])
        elif t == "way":
            ways[el["id"]] = el
    return ways, nodes


def way_to_coords(way: dict, nodes: dict[int, tuple[float, float]]) -> list[list[float]]:
    coords: list[list[float]] = []
    for nid in way.get("nodes") or []:
        pt = nodes.get(nid)
        if pt:
            coords.append([round(pt[0], 6), round(pt[1], 6)])
    return coords if len(coords) >= 2 else []


def relation_features(
    payload: dict, line_id: str, color: str, fallback_name: str
) -> list[dict]:
    ways, nodes = elements_to_ways(payload)
    features: list[dict] = []
    for el in payload.get("elements") or []:
        if el.get("type") != "relation":
            continue
        tags = el.get("tags") or {}
        name = tags.get("name") or tags.get("name:ko") or fallback_name
        ref = tags.get("ref") or line_id
        # Skip obvious non-passenger / freight / shuttle noise when possible
        lower = (name or "").lower()
        if any(x in lower for x in ("freight", "화물", "shuttle bus", "bus ")):
            continue
        # Suin-Bundang query also matches Shinbundang — drop those here.
        if line_id == "suin-bundang" and ("신분당" in name or "shinbundang" in lower):
            continue
        # Gyeongui query is broad ("경의") — keep Jungang / Gyeongui passenger routes.
        if line_id == "gyeongui":
            if "중앙" not in name and "jungang" not in lower and "gyeongui" not in lower:
                if "경의" not in name:
                    continue
        for mem in el.get("members") or []:
            if mem.get("type") != "way":
                continue
            # Prefer outer rail geometry; keep empty roles too (common on subway routes)
            role = (mem.get("role") or "").strip()
            if role and role not in ("", "forward", "backward", "route", "rail"):
                continue
            way = ways.get(mem.get("ref"))
            if not way:
                continue
            coords = way_to_coords(way, nodes)
            if not coords:
                continue
            features.append(
                {
                    "type": "Feature",
                    "properties": {
                        "line": line_id,
                        "ref": str(ref),
                        "name": name,
                        "color": color,
                    },
                    "geometry": {"type": "LineString", "coordinates": coords},
                }
            )
    return features


def dedupe_features(features: list[dict], max_features: int = 900) -> list[dict]:
    seen: set[tuple] = set()
    out: list[dict] = []
    for f in features:
        coords = tuple(
            (round(c[0], 5), round(c[1], 5))
            for c in (f.get("geometry") or {}).get("coordinates") or []
        )
        if len(coords) < 2 or coords in seen:
            continue
        seen.add(coords)
        out.append(f)
        if len(out) >= max_features:
            break
    return out


def write_line(line_id: str, features: list[dict]) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"line-{line_id}.geojson"
    fc = {"type": "FeatureCollection", "features": features}
    path.write_text(json.dumps(fc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return path


def rebuild_pack() -> Path:
    pack: dict[str, dict] = {}
    for line_id in LINES:
        path = OUT / f"line-{line_id}.geojson"
        if not path.exists():
            continue
        pack[line_id] = json.loads(path.read_text(encoding="utf-8"))
    # Combined lines.geojson
    all_features: list[dict] = []
    for line_id, fc in pack.items():
        all_features.extend(fc.get("features") or [])
    (OUT / "lines.geojson").write_text(
        json.dumps(
            {"type": "FeatureCollection", "features": all_features},
            ensure_ascii=False,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    js_path = OUT / "metro-data.js"
    js_path.write_text(
        "window.METRO_LINE_DATA=" + json.dumps(pack, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    return js_path


def fetch_line(line_id: str, meta: dict, force: bool = False) -> int:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache = CACHE_DIR / f"{line_id}.json"
    if cache.exists() and cache.stat().st_size > 2000 and not force:
        payload = json.loads(cache.read_text(encoding="utf-8"))
        print(f"[{line_id}] cache hit ({cache.stat().st_size} bytes)")
    else:
        print(f"[{line_id}] fetching…")
        payload = overpass(meta["query"])
        cache.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        time.sleep(1.2)
    features = dedupe_features(
        relation_features(payload, line_id, meta["color"], meta["name"])
    )
    write_line(line_id, features)
    pts = sum(len(f["geometry"]["coordinates"]) for f in features)
    print(f"[{line_id}] features={len(features)} points={pts}")
    return len(features)


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", help="Fetch only these line ids")
    ap.add_argument("--force", action="store_true", help="Ignore Overpass cache")
    ap.add_argument("--pack-only", action="store_true", help="Only rebuild metro-data.js")
    args = ap.parse_args()

    if args.pack_only:
        p = rebuild_pack()
        print(f"Wrote {p}")
        return 0

    targets = args.only or list(LINES.keys())
    # Prefer fixing sparse lines first when fetching all
    priority = ["4", "arex", "sillim", "gyeongui", "suin-bundang", "shinbundang", "8"]
    ordered = [x for x in priority if x in targets] + [
        x for x in targets if x not in priority
    ]

    results: dict[str, int] = {}
    for line_id in ordered:
        if line_id not in LINES:
            print(f"skip unknown {line_id}")
            continue
        try:
            results[line_id] = fetch_line(line_id, LINES[line_id], force=args.force)
        except Exception as exc:  # noqa: BLE001
            print(f"[{line_id}] ERROR: {exc}")
            results[line_id] = -1
            # Keep existing file if present

    rebuild_pack()
    print("done:", results)
    weak = [k for k, v in results.items() if 0 <= v < 5]
    if weak:
        print("WARNING weak geometries:", weak)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
