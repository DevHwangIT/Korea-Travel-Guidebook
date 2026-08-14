#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
en = json.loads((ROOT / "en.json").read_text(encoding="utf-8"))


def flatten(d, prefix=""):
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            p = f"{prefix}.{k}" if prefix else k
            out.update(flatten(v, p))
    else:
        out[prefix] = d
    return out


SKIP_LEAVES = {
    "mapsUrl",
    "mapsEmbedUrl",
    "url",
    "href",
    "src",
    "id",
    "slug",
    "region",
    "lat",
    "lng",
    "progress",
    "sourceType",
    "mapsProvider",
    "contactLineId",
    "contactEmail",
    "contactEmailMailto",
    "policeNumber",
    "fireNumber",
    "touristNumber",
}

en_f = {k: v for k, v in flatten(en).items() if isinstance(v, str)}

# places field types
print("=== places field leaf counts (vi same_as_en) ===")
vi = flatten(json.loads((ROOT / "vi.json").read_text(encoding="utf-8")))
leaf_counts = {}
for k, v in en_f.items():
    if not k.startswith("places."):
        continue
    leaf = k.split(".")[-1]
    lv = vi.get(k)
    if lv == v or lv is None or lv == "":
        leaf_counts[leaf] = leaf_counts.get(leaf, 0) + 1
for leaf, n in sorted(leaf_counts.items(), key=lambda x: -x[1]):
    skip = "SKIP" if leaf in SKIP_LEAVES else "TRANSLATE"
    print(f"  {leaf}: {n} [{skip}]")

# sample places desc/intro that need translation
print("\n=== places content samples needing fill (vi) ===")
for k, v in sorted(en_f.items()):
    if not k.startswith("places."):
        continue
    leaf = k.split(".")[-1]
    if leaf in SKIP_LEAVES or v.startswith("http"):
        continue
    lv = vi.get(k)
    if lv == v and len(v) > 20:
        print(f"{k}: {v[:100]}")

print("\n=== foodLife.quiz remaining (vi) ===")
for k, v in sorted(en_f.items()):
    if not k.startswith("foodLife.quiz."):
        continue
    lv = vi.get(k)
    if lv == v or not lv:
        print(f"{k}: {v!r} -> {lv!r}")

# body blocks across ALL sections still needing secondary
print("\n=== ALL body text blocks needing fill ===")


def collect_bodies(obj, path="", out=None):
    if out is None:
        out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            collect_bodies(v, f"{path}.{k}" if path else k, out)
    elif isinstance(obj, list):
        if obj and isinstance(obj[0], dict) and any(
            isinstance(b, dict) and b.get("type") == "text" for b in obj
        ):
            out.append((path, obj))
        else:
            for i, v in enumerate(obj):
                collect_bodies(v, f"{path}[{i}]", out)
    return out


ko = json.loads((ROOT / "ko.json").read_text(encoding="utf-8"))
bodies = collect_bodies(ko)
print(f"total body arrays: {len(bodies)}")
for lang in ["vi", "th", "ru", "zh-Hant"]:
    need = 0
    by_root = {}
    for path, blocks in bodies:
        root = path.split(".")[0]
        for b in blocks:
            if not isinstance(b, dict) or b.get("type") != "text":
                continue
            en_t = str(b.get("en") or "").strip()
            ko_t = str(b.get("ko") or "").strip()
            cur = str(b.get(lang) or "").strip()
            zh = str(b.get("zh") or "").strip()
            bad = (not cur) or cur == en_t or cur == ko_t
            if lang == "zh-Hant" and zh and cur == zh:
                bad = True
            if bad and (en_t or ko_t):
                need += 1
                by_root[root] = by_root.get(root, 0) + 1
    print(f"{lang}: {need} text blocks", dict(sorted(by_root.items(), key=lambda x: -x[1])[:10]))
