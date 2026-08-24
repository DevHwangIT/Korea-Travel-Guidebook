#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit remaining user-facing vi.json gaps vs en.json."""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
en = json.loads((ROOT / "en.json").read_text(encoding="utf-8"))
vi = json.loads((ROOT / "vi.json").read_text(encoding="utf-8"))
ko = json.loads((ROOT / "ko.json").read_text(encoding="utf-8"))

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
    "previewTitle",
    "placeId",
    "rom",
    "previewImage",
    "image",
    "cover",
    "thumb",
    "media",
}
EMAIL_RE = re.compile(r"^[\w.+-]+@[\w.-]+\.\w+$")
HTTP_RE = re.compile(r"^https?://", re.I)
ONLY_NUM_RE = re.compile(r"^[\d\s\-–—+/₩$.,:]+$")
PLACEHOLDER_RE = re.compile(r"^\{[^}]+\}$")
MEDIA_RE = re.compile(r"^(media/|images/|img/|\.?/?assets/)", re.I)
HANGUL = re.compile(r"[\uac00-\ud7a3]")


def flatten(d, prefix=""):
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            p = f"{prefix}.{k}" if prefix else k
            out.update(flatten(v, p))
    else:
        out[prefix] = d
    return out


en_f = flatten(en)
vi_f = flatten(vi)
ko_f = flatten(ko)


def intentional(key: str, val: str) -> bool:
    leaf = key.split(".")[-1]
    if leaf in SKIP_LEAVES:
        return True
    if key.endswith(".ko") or key.endswith(".rom") or key.endswith(".ja"):
        return True
    if not isinstance(val, str):
        return True
    s = val.strip()
    if not s:
        return False
    if HTTP_RE.match(s) or EMAIL_RE.match(s) or ONLY_NUM_RE.match(s) or PLACEHOLDER_RE.match(s):
        return True
    if MEDIA_RE.match(s) or s.endswith((".jpg", ".png", ".webp", ".svg", ".gif")):
        return True
    hangul_chars = HANGUL.findall(s)
    if hangul_chars and len(hangul_chars) / max(len(s), 1) > 0.3:
        return True
    return False


def looks_like_brand_or_proper(key: str, val: str) -> bool:
    leaf = key.split(".")[-1]
    words = val.split()
    common = {"the", "and", "with", "for", "from", "your", "to", "a", "an", "of", "in", "on"}
    if leaf in ("name", "title", "Name", "Title", "chip") and len(val) < 40:
        if len(words) <= 4 and not any(w.lower() in common for w in words):
            return True
    if len(val) < 20 and " " not in val.strip():
        return True
    return False


print("=== EMPTY (non-intentional) ===")
empty = []
for k, ev in en_f.items():
    if not isinstance(ev, str):
        continue
    lv = vi_f.get(k)
    if lv == "" or lv is None:
        if intentional(k, ev or ""):
            continue
        empty.append((k, ev))
        print(f"  {k}: en={ev[:120]!r} ko={(ko_f.get(k) or '')[:80]!r}")
print(f"empty count: {len(empty)}")

print("\n=== SAME AS EN prose-ish ===")
by = defaultdict(list)
for k, ev in en_f.items():
    if not isinstance(ev, str):
        continue
    lv = vi_f.get(k)
    if lv != ev:
        continue
    if intentional(k, ev):
        continue
    if looks_like_brand_or_proper(k, ev):
        continue
    by[k.split(".")[0]].append((k, ev))

total = sum(len(v) for v in by.values())
print(f"total prose-ish same: {total}")
for sec, items in sorted(by.items(), key=lambda x: -len(x[1])):
    print(f"\n-- {sec} ({len(items)}) --")
    for k, v in items[:15]:
        print(f"  {k}: {v[:110]!r}")


def walk_text_blocks(obj, path=""):
    out = []
    if isinstance(obj, dict):
        if obj.get("type") == "text":
            out.append((path, obj))
        for k, v in obj.items():
            out.extend(walk_text_blocks(v, f"{path}.{k}" if path else k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.extend(walk_text_blocks(v, f"{path}[{i}]"))
    return out


print("\n=== BODY text blocks where vi missing or == en ===")
bysec = defaultdict(int)
samples = []
need = 0
for path, b in walk_text_blocks(vi):
    en_t = str(b.get("en") or "").strip()
    vi_t = str(b.get("vi") or "").strip()
    if not en_t:
        continue
    if not vi_t or vi_t == en_t:
        need += 1
        sec = path.split(".")[0].split("[")[0]
        bysec[sec] += 1
        if len(samples) < 20:
            samples.append((path, en_t[:100]))
print(f"body need: {need}")
for s, n in sorted(bysec.items(), key=lambda x: -x[1]):
    print(f"  {s}: {n}")
for p, t in samples:
    print(f"  {p}: {t!r}")

# Key leaf types for restaurants / places
print("\n=== restaurants hours/category/desc still EN ===")
for leaf in ("hours", "category", "desc", "about", "tip", "how", "body", "lead", "summary"):
    n = 0
    for k, ev in en_f.items():
        if not k.startswith("restaurants.") or not k.endswith("." + leaf):
            continue
        if not isinstance(ev, str) or not ev.strip():
            continue
        lv = vi_f.get(k)
        if lv is None or lv == "" or lv == ev:
            if intentional(k, ev):
                continue
            n += 1
            if n <= 5:
                print(f"  {k}: {ev[:90]!r}")
    print(f"  leaf={leaf} gaps={n}")

print("\n=== places detail fields still EN ===")
for leaf in ("name", "address", "regionLabel", "desc", "how", "tip", "summary", "about"):
    n = 0
    for k, ev in en_f.items():
        if not k.startswith("places.") or not k.endswith("." + leaf):
            continue
        if not isinstance(ev, str) or not ev.strip():
            continue
        lv = vi_f.get(k)
        if lv is None or lv == "" or lv == ev:
            if intentional(k, ev) or looks_like_brand_or_proper(k, ev):
                continue
            n += 1
            if n <= 6:
                print(f"  {k}: {ev[:90]!r}")
    print(f"  leaf={leaf} gaps={n}")
