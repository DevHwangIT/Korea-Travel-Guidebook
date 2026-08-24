# -*- coding: utf-8 -*-
"""Slow SPARQL (1/min) sitelink+label P18 fill for leftovers."""
from __future__ import annotations

import importlib.util
import json
import re
import sys
import time
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "fill_ph", ROOT / "tool" / "_fill_placeholder_photos.py"
)
fill = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fill)
wd_spec = importlib.util.spec_from_file_location(
    "wd", ROOT / "tool" / "_fill_from_wikidata.py"
)
wd = importlib.util.module_from_spec(wd_spec)
wd_spec.loader.exec_module(wd)

BATCH = 30
SLEEP_Q = 70
SLEEP_DL = 2.8


def sitelink_sparql(names: list[str]) -> dict[str, str]:
    parts = " ".join(f'"{n.replace(chr(34), "")}"@ko' for n in names if n)
    q = f"""
SELECT ?name ?image WHERE {{
  VALUES ?name {{ {parts} }}
  {{
    ?item rdfs:label ?name .
    ?item wdt:P18 ?image .
  }} UNION {{
    ?sitelink schema:about ?item ;
              schema:isPartOf <https://ko.wikipedia.org/> ;
              schema:name ?name .
    ?item wdt:P18 ?image .
  }}
}}
"""
    url = wd.SPARQL_URL + "?" + urllib.parse.urlencode({"query": q, "format": "json"})
    data = json.loads(wd.http_get(url, accept="application/sparql-results+json").decode())
    out: dict[str, str] = {}
    for b in data.get("results", {}).get("bindings", []):
        label = (b.get("name") or {}).get("value") or ""
        image = (b.get("image") or {}).get("value") or ""
        if label and image and label not in out:
            out[label] = image
    return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    hashes = fill.type_hashes()
    ko_names = fill.load_ko_names()
    places = fill.parse_places()
    need = [p for p in places if fill.is_placeholder(p["slug"], hashes)]
    groups = fill.group_places(need, ko_names)
    print(f"need={len(need)} groups={len(groups)}", flush=True)

    labels = []
    seen = set()
    for g in groups:
        slug = g[0]["slug"]
        ko = re.sub(r"\s*\([^)]*\)\s*", " ", ko_names.get(slug, "")).strip()
        if ko and ko not in seen:
            seen.add(ko)
            labels.append(ko)

    mapping: dict[str, str] = {}
    for i in range(0, len(labels), BATCH):
        batch = labels[i : i + BATCH]
        print(f"SPARQL {i//BATCH+1} n={len(batch)}", flush=True)
        try:
            mapping.update(sitelink_sparql(batch))
            print(f"  hits {len(mapping)}", flush=True)
        except Exception as exc:
            print(f"  SPARQL err {exc}", flush=True)
            time.sleep(SLEEP_Q)
            try:
                mapping.update(sitelink_sparql(batch))
                print(f"  hits {len(mapping)}", flush=True)
            except Exception as exc2:
                print(f"  retry fail {exc2}", flush=True)
        time.sleep(SLEEP_Q)

    ok = miss = 0
    for i, g in enumerate(groups, 1):
        p = g[0]
        slug = p["slug"]
        ko = re.sub(r"\s*\([^)]*\)\s*", " ", ko_names.get(slug, "")).strip()
        image = mapping.get(ko)
        print(f"[{i}/{len(groups)}] {slug} {ko}", flush=True)
        if not image:
            miss += 1
            print("  no P18", flush=True)
            continue
        time.sleep(SLEEP_DL)
        dest = fill.dest_path(slug)
        if fill.try_save(wd.file_path_url(image), dest, hashes, f"wd:{ko}"):
            ok += 1
            for other in g[1:]:
                fill.copy_to(slug, other["slug"])
                print(f"  COPY -> {other['slug']}", flush=True)
        else:
            miss += 1
            print("  dl fail", flush=True)

    remain = sum(1 for x in fill.parse_places() if fill.is_placeholder(x["slug"], hashes))
    print(f"DONE ok={ok} miss={miss} remaining={remain}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
