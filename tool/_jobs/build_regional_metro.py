# -*- coding: utf-8 -*-
"""Fetch Busan / Daegu / Gwangju / Daejeon metro lines + named stations (OSM Overpass).

Writes:
  data/metro/line-{id}.geojson
  merges stations into data/metro/stations.geojson (+ stations-data.js)
  rebuilds metro-data.js / lines.geojson via build_metro_lines.rebuild_pack
"""
from __future__ import annotations

import json
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "metro"
CACHE_DIR = ROOT / "tool" / "_tmp" / "overpass-regional-metro"
UA = "KoreaTravelGuidebook/1.0 (regional-metro)"

# Import Seoul line pack helper
sys.path.insert(0, str(ROOT / "tool"))
from build_metro_lines import (  # noqa: E402
    ENDPOINTS,
    LINES as SEOUL_LINES,
    dedupe_features,
    overpass as _seoul_overpass,
    rebuild_pack,
    relation_features,
    write_line,
)


def _ssl_ctx() -> ssl.SSLContext:
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl._create_unverified_context()


def overpass(query_body: str) -> dict:
    # Keep full tags on recursive child nodes (stops need name:*).
    q = f"[out:json][timeout:180];\n({query_body}\n);\nout body;\n>;\nout body qt;"
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


# Ensure relation_features / fetch paths using imported overpass also get tagged nodes
import build_metro_lines as _bml  # noqa: E402

_bml.overpass = overpass

REGIONAL_LINES: dict[str, dict] = {
    "busan-1": {
        "color": "#F06A00",
        "name": "부산1호선",
        "region": "busan",
        "query": (
            r'relation["type"="route"]["route"~"subway|light_rail"]'
            r'["name"~"부산.*1호선|Busan Metro Line 1|부산도시철도 1"](34.9,128.7,35.45,129.35);'
        ),
    },
    "busan-2": {
        "color": "#3CB44A",
        "name": "부산2호선",
        "region": "busan",
        "query": (
            r'relation["type"="route"]["route"~"subway|light_rail"]'
            r'["name"~"부산.*2호선|Busan Metro Line 2|부산도시철도 2"](34.9,128.7,35.45,129.35);'
        ),
    },
    "busan-3": {
        "color": "#BB8C00",
        "name": "부산3호선",
        "region": "busan",
        "query": (
            r'relation["type"="route"]["route"~"subway|light_rail"]'
            r'["name"~"부산.*3호선|Busan Metro Line 3|부산도시철도 3"](34.9,128.7,35.45,129.35);'
        ),
    },
    "busan-4": {
        "color": "#2178C4",
        "name": "부산4호선",
        "region": "busan",
        "query": (
            r'relation["type"="route"]["route"~"subway|light_rail|monorail"]'
            r'["name"~"부산.*4|Busan.*Line 4|도시철도 4|안평"](35.05,128.95,35.3,129.2);'
        ),
    },
    "busan-gimhae": {
        "color": "#8FC31F",
        "name": "부산김해경전철",
        "region": "busan",
        "query": (
            r'relation["type"="route"]["route"~"light_rail|subway"]'
            r'["name"~"김해경전철|Busan–Gimhae|Busan-Gimhae|부산김해"](35.0,128.7,35.35,129.15);'
        ),
    },
    "daegu-1": {
        "color": "#D93F0C",
        "name": "대구1호선",
        "region": "daegu",
        "query": (
            r'relation["type"="route"]["route"="subway"]'
            r'["name"~"대구.*1호선|Daegu Metro Line 1|대구도시철도 1"](35.7,128.4,36.05,128.85);'
        ),
    },
    "daegu-2": {
        "color": "#00AA80",
        "name": "대구2호선",
        "region": "daegu",
        "query": (
            r'relation["type"="route"]["route"="subway"]'
            r'["name"~"대구.*2호선|Daegu Metro Line 2|대구도시철도 2"](35.7,128.4,36.05,128.85);'
        ),
    },
    "daegu-3": {
        "color": "#FFB100",
        "name": "대구3호선",
        "region": "daegu",
        "query": (
            r'relation["type"="route"]["route"~"subway|light_rail|monorail"]'
            r'["name"~"대구.*3|Daegu.*Line 3|도시철도 3|모노레일"](35.75,128.45,36.0,128.8);'
        ),
    },
    "gwangju-1": {
        "color": "#009088",
        "name": "광주1호선",
        "region": "gwangju",
        "query": (
            r'relation["type"="route"]["route"="subway"]'
            r'["name"~"광주.*1호선|Gwangju Metro|광주도시철도"](35.05,126.7,35.25,127.05);'
        ),
    },
    "daejeon-1": {
        "color": "#007448",
        "name": "대전1호선",
        "region": "daejeon",
        "query": (
            r'relation["type"="route"]["route"="subway"]'
            r'["name"~"대전.*1호선|Daejeon Metro|대전도시철도"](36.2,127.25,36.45,127.55);'
        ),
    },
}

# Station bbox queries (railway=station with subway/light_rail tags)
STATION_QUERIES: dict[str, str] = {
    "busan": (
        r'node["railway"="station"]["name"](35.0,128.75,35.35,129.28);'
        r'node["railway"="halt"]["name"]["subway"="yes"](35.0,128.75,35.35,129.28);'
    ),
    "daegu": (
        r'node["railway"="station"]["name"](35.75,128.45,36.0,128.8);'
        r'node["railway"="halt"]["name"]["subway"="yes"](35.75,128.45,36.0,128.8);'
    ),
    "gwangju": (
        r'node["railway"="station"]["name"](35.1,126.75,35.22,126.98);'
        r'node["railway"="halt"]["name"]["subway"="yes"](35.1,126.75,35.22,126.98);'
    ),
    "daejeon": (
        r'node["railway"="station"]["name"](36.28,127.3,36.42,127.5);'
        r'node["railway"="halt"]["name"]["subway"="yes"](36.28,127.3,36.42,127.5);'
    ),
}

# Heuristic: map OSM station → line ids by known line name fragments on tags
# or by network/ref. Fallback: assign from nearby line region all lines if subway=yes.
REGION_LINE_IDS = {
    "busan": ["busan-1", "busan-2", "busan-3", "busan-4", "busan-gimhae"],
    "daegu": ["daegu-1", "daegu-2", "daegu-3"],
    "gwangju": ["gwangju-1"],
    "daejeon": ["daejeon-1"],
}


def fetch_cached(key: str, query_body: str, force: bool = False) -> dict:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache = CACHE_DIR / f"{key}.json"
    if cache.exists() and cache.stat().st_size > 500 and not force:
        print(f"[{key}] cache hit ({cache.stat().st_size} bytes)")
        return json.loads(cache.read_text(encoding="utf-8"))
    print(f"[{key}] fetching…")
    payload = overpass(query_body)
    cache.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    time.sleep(1.5)
    return payload


def infer_lines_from_tags(tags: dict, region: str) -> list[str]:
    name = (tags.get("name") or "") + " " + (tags.get("network") or "")
    ref = str(tags.get("ref") or "")
    line = str(tags.get("line") or "")
    blob = f"{name} {ref} {line}".lower()
    found: list[str] = []

    def add(lid: str) -> None:
        if lid not in found:
            found.append(lid)

    if region == "busan":
        if "김해" in name or "gimhae" in blob:
            add("busan-gimhae")
        if "4호선" in name or ref == "4" or "line 4" in blob:
            add("busan-4")
        if "3호선" in name or ref == "3" or "line 3" in blob:
            add("busan-3")
        if "2호선" in name or ref == "2" or "line 2" in blob:
            add("busan-2")
        if "1호선" in name or ref == "1" or "line 1" in blob:
            add("busan-1")
    elif region == "daegu":
        if "3호선" in name or ref == "3":
            add("daegu-3")
        if "2호선" in name or ref == "2":
            add("daegu-2")
        if "1호선" in name or ref == "1":
            add("daegu-1")
    elif region == "gwangju":
        add("gwangju-1")
    elif region == "daejeon":
        add("daejeon-1")

    # subway=yes stations without line tags: keep if we can match later via stop members
    return found


def stations_from_relation_stops(payload: dict, line_id: str) -> dict[str, dict]:
    """name -> {lon, lat, name_en, lines} from route relation stop/platform nodes."""
    nodes: dict[int, dict] = {}
    for el in payload.get("elements") or []:
        if el.get("type") == "node":
            nodes[el["id"]] = el
    out: dict[str, dict] = {}
    for el in payload.get("elements") or []:
        if el.get("type") != "relation":
            continue
        for mem in el.get("members") or []:
            if mem.get("type") != "node":
                continue
            role = (mem.get("role") or "").lower()
            if role and role not in (
                "stop",
                "stop_entry_only",
                "stop_exit_only",
                "platform",
                "station",
                "",
            ):
                continue
            node = nodes.get(mem.get("ref"))
            if not node or "lat" not in node or "lon" not in node:
                continue
            tags = node.get("tags") or {}
            name = tags.get("name") or tags.get("name:ko")
            if not name:
                continue
            # Route stop/platform members are authoritative for this line_id.
            en = tags.get("name:en") or tags.get("name:ko-Latn") or ""
            prev = out.get(name)
            if prev:
                lines = set(prev["lines"].split(",")) if prev.get("lines") else set()
                lines.add(line_id)
                prev["lines"] = ",".join(sorted(lines))
            else:
                out[name] = {
                    "lon": float(node["lon"]),
                    "lat": float(node["lat"]),
                    "name_en": en,
                    "lines": line_id,
                    "tags": tags,
                }
    return out


def is_likely_metro_station(tags: dict, region: str) -> bool:
    railway = tags.get("railway") or ""
    station = tags.get("station") or ""
    subway = tags.get("subway") or ""
    network = (tags.get("network") or "") + (tags.get("operator") or "")
    name = tags.get("name") or ""
    if subway == "yes" or station in ("subway", "light_rail"):
        return True
    if any(
        x in network
        for x in ("도시철도", "지하철", "Metro", "경전철", "교통공사", "모노레일")
    ):
        return True
    if region == "busan" and any(
        x in network for x in ("부산교통공사", "김해경전철", "부산김해")
    ):
        return True
    if region == "daegu" and "대구" in network:
        return True
    if region == "gwangju" and "광주" in network:
        return True
    if region == "daejeon" and "대전" in network:
        return True
    if station == "train" or "KTX" in name:
        return False
    if railway == "station" and not subway and station not in ("subway", "light_rail"):
        return any(
            x in network for x in ("도시철도", "지하철", "경전철", "Metro", "Light", "모노레일")
        )
    # Named railway=station inside metro bbox often is metro even without tags
    if railway == "station" and name:
        return True
    return False


def merge_stations(new_features: list[dict]) -> tuple[int, int]:
    geo_path = OUT / "stations.geojson"
    existing = json.loads(geo_path.read_text(encoding="utf-8"))
    by_name: dict[str, dict] = {}
    for f in existing.get("features") or []:
        props = f.get("properties") or {}
        n = props.get("name")
        if n:
            by_name[n] = f

    added = 0
    updated = 0
    for f in new_features:
        props = f.get("properties") or {}
        name = props.get("name")
        if not name:
            continue
        if name in by_name:
            old = by_name[name]
            old_props = old.get("properties") or {}
            old_lines = set(
                x.strip()
                for x in str(old_props.get("lines") or "").split(",")
                if x.strip()
            )
            new_lines = set(
                x.strip()
                for x in str(props.get("lines") or "").split(",")
                if x.strip()
            )
            merged = sorted(old_lines | new_lines)
            # Prefer regional line ids when this is a regional-only name conflict
            # (Seoul names can collide — only merge lines if coords are close)
            old_coords = (old.get("geometry") or {}).get("coordinates") or [0, 0]
            new_coords = (f.get("geometry") or {}).get("coordinates") or [0, 0]
            dist2 = (old_coords[0] - new_coords[0]) ** 2 + (
                old_coords[1] - new_coords[1]
            ) ** 2
            if dist2 > 0.01:  # ~ ~10km — different cities, keep separate via rename
                alt = f"{name}·{props.get('region') or 'r'}"
                props = dict(props)
                props["name"] = name  # keep Hangul; use unique key via coords
                # Store as separate feature keyed by name+region in list later
                key = f"{name}@@{round(new_coords[0], 3)},{round(new_coords[1], 3)}"
                by_name[key] = f
                added += 1
                continue
            old_props["lines"] = ",".join(merged)
            if not old_props.get("name_en") and props.get("name_en"):
                old_props["name_en"] = props["name_en"]
            old["properties"] = old_props
            updated += 1
        else:
            by_name[name] = f
            added += 1

    features = list(by_name.values())
    fc = {
        "type": "FeatureCollection",
        "properties": {
            **(existing.get("properties") or {}),
            "source": "KoreaMetroData+OSM regional",
        },
        "features": features,
    }
    geo_path.write_text(
        json.dumps(fc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    js_path = OUT / "stations-data.js"
    js_path.write_text(
        "window.METRO_STATION_DATA="
        + json.dumps(fc, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    return added, updated


def feature_from_stop(name: str, data: dict, region: str) -> dict:
    tags = data.get("tags") or {}
    return {
        "type": "Feature",
        "properties": {
            "name": name,
            "name_en": data.get("name_en") or tags.get("name:en") or "",
            "name_han": tags.get("name:zh-Hant") or tags.get("name:zh") or "",
            "name_zh": tags.get("name:zh") or "",
            "name_ja": tags.get("name:ja") or "",
            "name_vi": "",
            "name_th": "",
            "name_ru": "",
            "lines": data.get("lines") or "",
            "source": "osm-regional",
            "region": region,
            "major": False,
        },
        "geometry": {
            "type": "Point",
            "coordinates": [
                round(float(data["lon"]), 6),
                round(float(data["lat"]), 6),
            ],
        },
    }


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--stations-only", action="store_true")
    ap.add_argument("--lines-only", action="store_true")
    args = ap.parse_args()

    # Patch SEOUL_LINES rebuild to include regional files already on disk
    targets = args.only or list(REGIONAL_LINES.keys())
    stop_accum: dict[str, dict] = {}  # name@@region -> data

    if not args.stations_only:
        for line_id in targets:
            meta = REGIONAL_LINES.get(line_id)
            if not meta:
                print(f"skip unknown {line_id}")
                continue
            try:
                payload = fetch_cached(f"line-{line_id}", meta["query"], force=args.force)
                features = dedupe_features(
                    relation_features(payload, line_id, meta["color"], meta["name"])
                )
                write_line(line_id, features)
                pts = sum(len(f["geometry"]["coordinates"]) for f in features)
                print(f"[{line_id}] features={len(features)} points={pts}")
                # Collect stop nodes from same payload
                stops = stations_from_relation_stops(payload, line_id)
                for name, data in stops.items():
                    key = f"{name}@@{meta['region']}"
                    if key in stop_accum:
                        lines = set(stop_accum[key]["lines"].split(","))
                        lines.update(data["lines"].split(","))
                        stop_accum[key]["lines"] = ",".join(sorted(x for x in lines if x))
                        if not stop_accum[key].get("name_en") and data.get("name_en"):
                            stop_accum[key]["name_en"] = data["name_en"]
                    else:
                        stop_accum[key] = {
                            **data,
                            "region": meta["region"],
                        }
            except Exception as exc:  # noqa: BLE001
                print(f"[{line_id}] ERROR: {exc}")

    if not args.lines_only:
        # Extra station nodes by region bbox (fills gaps)
        for region, qbody in STATION_QUERIES.items():
            if args.only and not any(
                REGIONAL_LINES.get(x, {}).get("region") == region for x in (args.only or [])
            ):
                # If --only specified and none for this region, skip
                if args.only:
                    continue
            try:
                payload = fetch_cached(f"stations-{region}", qbody, force=args.force)
                for el in payload.get("elements") or []:
                    if el.get("type") != "node":
                        continue
                    tags = el.get("tags") or {}
                    name = tags.get("name")
                    if not name or "lat" not in el:
                        continue
                    if not is_likely_metro_station(tags, region):
                        continue
                    lines = infer_lines_from_tags(tags, region)
                    if not lines:
                        # Single-line systems: safe default
                        if len(REGION_LINE_IDS.get(region) or []) == 1:
                            lines = list(REGION_LINE_IDS[region])
                        elif tags.get("subway") == "yes" or tags.get("station") in (
                            "subway",
                            "light_rail",
                        ):
                            # Multi-line city without ref — leave for relation stops
                            continue
                        else:
                            continue
                    key = f"{name}@@{region}"
                    line_str = ",".join(lines)
                    if key in stop_accum:
                        old = set(stop_accum[key]["lines"].split(","))
                        old.update(lines)
                        stop_accum[key]["lines"] = ",".join(sorted(old))
                    else:
                        stop_accum[key] = {
                            "lon": float(el["lon"]),
                            "lat": float(el["lat"]),
                            "name_en": tags.get("name:en") or "",
                            "lines": line_str,
                            "tags": tags,
                            "region": region,
                        }
            except Exception as exc:  # noqa: BLE001
                print(f"[stations-{region}] ERROR: {exc}")

        # Filter: keep stops that have at least one regional line id
        regional_ids = set(REGIONAL_LINES.keys())
        features: list[dict] = []
        for key, data in stop_accum.items():
            name = key.split("@@", 1)[0]
            lines = [
                x.strip()
                for x in str(data.get("lines") or "").split(",")
                if x.strip() in regional_ids
            ]
            if not lines:
                continue
            data = dict(data)
            data["lines"] = ",".join(sorted(set(lines)))
            # Drop likely non-metro if tags look like mainline and only weak lines
            tags = data.get("tags") or {}
            if tags and not is_likely_metro_station(tags, data.get("region") or ""):
                # Still keep if we got it from route relation stop members
                if data.get("source") != "relation":
                    # relation stops don't set source; keep all stop_accum from relations
                    pass
            features.append(feature_from_stop(name, data, data.get("region") or ""))

        added, updated = merge_stations(features)
        print(f"stations merge: added={added} updated={updated} total_new_feats={len(features)}")

    # Ensure rebuild_pack sees regional line files: temporarily extend LINES
    SEOUL_LINES.update(
        {k: {"color": v["color"], "name": v["name"], "query": v["query"]} for k, v in REGIONAL_LINES.items()}
    )
    p = rebuild_pack()
    print(f"Wrote pack {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
