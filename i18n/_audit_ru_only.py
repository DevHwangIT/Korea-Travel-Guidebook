#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
en = json.loads((ROOT / "en.json").read_text(encoding="utf-8"))
ru = json.loads((ROOT / "ru.json").read_text(encoding="utf-8"))

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
    "naverPlaceId",
    "googlePlaceId",
    "kakaoPlaceId",
}
SKIP_EQ = {
    "naver",
    "google",
    "kakao",
    "Phone",
    "Wi-Fi",
    "Google",
    "Naver",
    "Kakao",
    "Papago",
    "Kakao Map",
    "Naver Map",
    "Kakao T",
    "Tmoney",
    "Yanolja",
    "Yeogi",
    "Baemin",
    "Yogiyo",
    "Coupang",
    "Olive Young",
    "Daiso",
    "Taxi",
    "Tip",
}

FOCUS = (
    "beforeTrip.",
    "tips.",
    "foodLife.",
    "foodsHub.",
    "places.",
    "transport.",
    "fun.",
    "souvenir.",
    "restaurants.",
    "dishes.",
    "convenience.",
    "korean.",
    "apps.",
    "misc.",
    "home.",
    "emergency.",
    "festivals.",
    "areas.",
    "travelUtils.",
)


def flatten(d, prefix=""):
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            p = f"{prefix}.{k}" if prefix else k
            out.update(flatten(v, p))
    else:
        out[prefix] = d
    return out


en_f = {k: v for k, v in flatten(en).items() if isinstance(v, str)}
ru_f = flatten(ru)

by = defaultdict(lambda: defaultdict(int))
samples = defaultdict(list)

for k, v in en_f.items():
    if not any(k.startswith(p) for p in FOCUS):
        continue
    leaf = k.split(".")[-1]
    if leaf in SKIP_LEAVES:
        continue
    if not v or not v.strip():
        continue
    if v.strip() in SKIP_EQ:
        continue
    if re.match(r"^https?://", v):
        continue
    if re.match(r"^[\d\s\-–—+/₩$.,:]+$", v):
        continue
    if re.match(r"^[\w.+-]+@[\w.-]+\.\w+$", v):
        continue
    lv = ru_f.get(k)
    gap = lv is None or lv == "" or lv == v
    if gap:
        pref = next(p.rstrip(".") for p in FOCUS if k.startswith(p))
        by[pref]["scalar"] += 1
        if len(samples[pref]) < 3:
            samples[pref].append(("scalar", k, v[:100]))


def walk(obj, path=""):
    if isinstance(obj, dict):
        if obj.get("type") in ("text", "callout") and "en" in obj:
            en_t = str(obj.get("en") or "").strip()
            ru_t = str(obj.get("ru") or "").strip()
            ko_t = str(obj.get("ko") or "").strip()
            if en_t and (not ru_t or ru_t == en_t or ru_t == ko_t):
                pref = path.split(".")[0] if path else "root"
                by[pref]["body"] += 1
                if len(samples[pref]) < 5:
                    samples[pref].append((obj.get("type"), path, en_t[:100]))
        for k, v in obj.items():
            walk(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            walk(item, f"{path}[{i}]")


walk(ru)
print("=== RU GAPS (content) ===")
for pref in sorted(by.keys(), key=lambda x: -(by[x]["scalar"] + by[x]["body"])):
    print(f"{pref}: scalar={by[pref]['scalar']} body={by[pref]['body']}")
    for t, k, s in samples[pref]:
        print(f"  [{t}] {k}: {s!r}")
print("TOTAL scalars:", sum(by[p]["scalar"] for p in by))
print("TOTAL bodies:", sum(by[p]["body"] for p in by))
