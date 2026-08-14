#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from pathlib import Path
from collections import defaultdict

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


en_f = {k: v for k, v in flatten(en).items() if isinstance(v, str)}

FOCUS = (
    "beforeTrip.",
    "tips.",
    "foodLife.quiz.",
    "places.",
    "fun.",
    "transport.",
    "dishes.",
    "restaurants.",
    "home.",
    "emergency.",
    "festivals.",
    "convenience.",
    "souvenir.",
    "korean.",
    "apps.",
    "areas.",
    "restaurantFields.",
    "travelUtils.",
    "misc.",
    "cities.",
)

for lang in ["vi", "th", "ru", "zh-Hant"]:
    f = flatten(json.loads((ROOT / f"{lang}.json").read_text(encoding="utf-8")))
    by = defaultdict(int)
    samples = defaultdict(list)
    for k, v in en_f.items():
        if not any(k.startswith(p) for p in FOCUS):
            continue
        lv = f.get(k)
        if lv is None or lv == "" or lv == v:
            pref = next(p.rstrip(".") for p in FOCUS if k.startswith(p))
            by[pref] += 1
            if len(samples[pref]) < 3 and v and not v.startswith("http"):
                samples[pref].append((k, v[:80]))
    print("===", lang, "===")
    for pref, n in sorted(by.items(), key=lambda x: -x[1]):
        print(f"  {pref}: {n}")
        for k, s in samples[pref]:
            print(f"    - {k}: {s!r}")
