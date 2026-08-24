# -*- coding: utf-8 -*-
"""Fill remaining place placeholders from Wikidata P18 (representative image).

Batches SPARQL lookups, then downloads Commons files via Special:FilePath.
"""
from __future__ import annotations

import importlib.util
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "fill_ph", ROOT / "tool" / "_fill_placeholder_photos.py"
)
fill = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(fill)

UA = (
    "KoreaTravelGuidebook/1.0 (wikidata P18 place covers; "
    "educational offline mirror; rate-limited)"
)
SPARQL_URL = "https://query.wikidata.org/sparql"
SLEEP_DL = 2.2
SLEEP_Q = 20.0
BATCH = 40
LOG = ROOT / "tool" / "_wikidata_p18_log.json"
CACHE = ROOT / "tool" / "_wd_p18_cache.json"


def http_get(url: str, timeout: int = 60, accept: str | None = None) -> bytes:
    headers = {"User-Agent": UA}
    if accept:
        headers["Accept"] = accept
    req = urllib.request.Request(url, headers=headers)
    ctx = fill.ssl_ctx()
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.read()


def sparql(values_clause: str) -> list[dict]:
    query = f"""
SELECT ?label ?image WHERE {{
  VALUES ?label {{ {values_clause} }}
  ?item rdfs:label ?label.
  ?item wdt:P18 ?image.
}}
"""
    url = SPARQL_URL + "?" + urllib.parse.urlencode(
        {"query": query, "format": "json"}
    )
    data = json.loads(http_get(url, accept="application/sparql-results+json").decode())
    rows = []
    for b in data.get("results", {}).get("bindings", []):
        label = (b.get("label") or {}).get("value") or ""
        image = (b.get("image") or {}).get("value") or ""
        if label and image:
            rows.append({"label": label, "image": image})
    return rows


def file_path_url(image: str, width: int = 800) -> str:
    # http://commons.wikimedia.org/wiki/Special:FilePath/Name.jpg
    parsed = urllib.parse.urlparse(image)
    name = urllib.parse.unquote(parsed.path.split("/Special:FilePath/")[-1])
    return (
        "https://commons.wikimedia.org/wiki/Special:FilePath/"
        + urllib.parse.quote(name)
        + f"?width={width}"
    )


def chunks(items: list, n: int):
    for i in range(0, len(items), n):
        yield items[i : i + n]


def lookup_map(names: list[str], lang: str) -> dict[str, str]:
    cache: dict[str, str] = {}
    if CACHE.exists():
        try:
            cache = json.loads(CACHE.read_text(encoding="utf-8"))
        except Exception:
            cache = {}
    out: dict[str, str] = dict(cache)
    unique = []
    seen = set()
    for n in names:
        n = n.strip()
        if n and n not in seen:
            seen.add(n)
            unique.append(n)
    pending = [n for n in unique if n not in out]
    print(f"  cache hit={len(unique)-len(pending)} pending={len(pending)}", flush=True)
    for batch in chunks(pending, BATCH):
        parts = " ".join(f'"{n.replace(chr(34), "")}"@{lang}' for n in batch)
        print(f"  SPARQL {lang} n={len(batch)}", flush=True)
        try:
            rows = sparql(parts)
        except urllib.error.HTTPError as exc:
            print(f"  SPARQL HTTP {exc.code}, wait 70s", flush=True)
            time.sleep(70)
            try:
                rows = sparql(parts)
            except Exception as exc2:  # noqa: BLE001
                print(f"  SPARQL retry err: {exc2}", flush=True)
                time.sleep(8)
                continue
        except Exception as exc:  # noqa: BLE001
            print(f"  SPARQL err: {exc}", flush=True)
            time.sleep(8)
            continue
        for row in rows:
            lab = row["label"]
            if lab not in out:
                out[lab] = row["image"]
        for n in batch:
            out.setdefault(n, "")
        CACHE.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"    hits {len(rows)}", flush=True)
        time.sleep(SLEEP_Q)
    return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    hashes = fill.type_hashes()
    ko_names = fill.load_ko_names()
    places = fill.parse_places()
    need = [p for p in places if fill.is_placeholder(p["slug"], hashes)]
    print(f"placeholder={len(need)}", flush=True)

    groups = fill.group_places(need + [p for p in places if not fill.is_placeholder(p["slug"], hashes)], ko_names)
    todo: list[list[dict]] = []
    for g in groups:
        ph = [p for p in g if fill.is_placeholder(p["slug"], hashes)]
        good = [p for p in g if not fill.is_placeholder(p["slug"], hashes)]
        if not ph:
            continue
        if good:
            src = good[0]["slug"]
            for p in ph:
                fill.copy_to(src, p["slug"])
                print(f"COPY {src} -> {p['slug']}", flush=True)
            continue
        todo.append(ph)
    print(f"groups={len(todo)}", flush=True)

    ko_list = []
    en_list = []
    for g in todo:
        p = g[0]
        ko = ko_names.get(p["slug"], "")
        ko = re.sub(r"\s*\([^)]*\)\s*", " ", ko).strip()
        if ko:
            ko_list.append(ko)
        en = re.sub(r"\s*\([^)]*\)\s*", " ", p["note"]).strip()
        if en:
            en_list.append(en)

    ko_map = lookup_map(ko_list, "ko")
    en_map: dict[str, str] = {}

    ok = miss = 0
    missed = []
    for i, g in enumerate(todo, 1):
        primary = g[0]
        slug = primary["slug"]
        ko = re.sub(r"\s*\([^)]*\)\s*", " ", ko_names.get(slug, "")).strip()
        en = re.sub(r"\s*\([^)]*\)\s*", " ", primary["note"]).strip()
        image = ko_map.get(ko) or en_map.get(en)
        print(f"[{i}/{len(todo)}] {slug} {ko or en}", flush=True)
        if not image:
            miss += 1
            missed.append({"slug": slug, "ko": ko, "en": en})
            print("  no P18", flush=True)
            continue
        url = file_path_url(image)
        dest = fill.dest_path(slug)
        time.sleep(SLEEP_DL)
        if fill.try_save(url, dest, hashes, f"wd:{image.split('/')[-1]}"):
            ok += 1
            for p in g[1:]:
                fill.copy_to(slug, p["slug"])
                print(f"  COPY -> {p['slug']}", flush=True)
        else:
            miss += 1
            missed.append({"slug": slug, "ko": ko, "en": en, "image": image})
            print("  dl fail", flush=True)

    remain = sum(1 for p in fill.parse_places() if fill.is_placeholder(p["slug"], hashes))
    LOG.write_text(
        json.dumps(
            {"ok": ok, "miss": miss, "remaining": remain, "missed": missed},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nDONE ok={ok} miss={miss} remaining={remain}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
