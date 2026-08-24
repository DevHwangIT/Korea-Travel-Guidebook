# -*- coding: utf-8 -*-
"""English-label Wikidata P18 pass for leftover placeholders."""
from __future__ import annotations

import importlib.util
import re
import sys
import time
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


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    hashes = fill.type_hashes()
    places = fill.parse_places()
    need = [p for p in places if fill.is_placeholder(p["slug"], hashes)]
    notes = []
    for p in need:
        bare = re.sub(r"\s*\([^)]*\)\s*", " ", p["note"]).strip()
        notes.append(bare)
    print(f"need={len(need)} notes={len(set(notes))}", flush=True)
    en_map = wd.lookup_map(notes, "en")
    ok = 0
    for p in need:
        if not fill.is_placeholder(p["slug"], hashes):
            continue
        bare = re.sub(r"\s*\([^)]*\)\s*", " ", p["note"]).strip()
        image = en_map.get(bare) or ""
        print(f"{p['slug']} <- {bare}", flush=True)
        if not image:
            print("  no P18", flush=True)
            continue
        url = wd.file_path_url(image)
        time.sleep(2.4)
        if fill.try_save(url, fill.dest_path(p["slug"]), hashes, f"en:{bare}"):
            ok += 1
            for other in need:
                if other["note"] == p["note"] and other["slug"] != p["slug"]:
                    if fill.is_placeholder(other["slug"], hashes):
                        fill.copy_to(p["slug"], other["slug"])
                        print(f"  COPY -> {other['slug']}", flush=True)
        else:
            print("  dl fail", flush=True)
    remain = sum(1 for x in fill.parse_places() if fill.is_placeholder(x["slug"], hashes))
    print(f"DONE ok={ok} remaining={remain}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
