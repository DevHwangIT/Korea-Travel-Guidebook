#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from pathlib import Path

ROOT = Path("i18n")
en = json.loads((ROOT / "en.json").read_text(encoding="utf-8"))
ru = json.loads((ROOT / "ru.json").read_text(encoding="utf-8"))
vi = json.loads((ROOT / "vi.json").read_text(encoding="utf-8"))
th = json.loads((ROOT / "th.json").read_text(encoding="utf-8"))

for slug in ["myeongdong", "gangnam", "haeundae"]:
    print(slug)
    for lang, d in [("en", en), ("vi", vi), ("th", th), ("ru", ru)]:
        p = d["places"][slug]
        print(f"  {lang}: name={p.get('name')!r} regionLabel={p.get('regionLabel')!r}")

r = list(en["restaurants"].keys())[0]
print("\nrestaurant", r)
for k, v in en["restaurants"][r].items():
    if not isinstance(v, str):
        continue
    print(
        f"  {k}: en={v[:70]!r}\n       vi={str(vi['restaurants'][r].get(k,''))[:70]!r}\n       ru={str(ru['restaurants'][r].get(k,''))[:70]!r}"
    )

# count restaurant fields still == en by leaf
from collections import Counter

c = Counter()
for rid, obj in en["restaurants"].items():
    for k, v in obj.items():
        if isinstance(v, str) and vi["restaurants"].get(rid, {}).get(k) == v:
            c[k] += 1
print("\nvi restaurants same_as_en by leaf:")
for k, n in c.most_common():
    print(f"  {k}: {n}")
