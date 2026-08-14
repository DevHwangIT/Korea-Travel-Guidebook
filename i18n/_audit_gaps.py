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
            if isinstance(v, dict):
                out.update(flatten(v, p))
            elif isinstance(v, list):
                # skip body arrays at top; mark specially
                out[p] = v
            else:
                out[p] = v
    return out


def top_prefix(key):
    parts = key.split(".")
    if parts[0] in (
        "beforeTrip",
        "tips",
        "foodLife",
        "places",
        "fun",
        "transport",
        "transportation",
        "dishes",
        "restaurants",
    ):
        return ".".join(parts[:2]) if len(parts) > 1 else parts[0]
    return parts[0]


en_f = flatten(en)
print("en keys:", len(en_f))

for lang in ["vi", "th", "ru", "zh-Hant"]:
    f = flatten(json.loads((ROOT / f"{lang}.json").read_text(encoding="utf-8")))
    by = defaultdict(lambda: {"same": 0, "empty": 0, "ok": 0, "chars": 0})
    for k, v in en_f.items():
        if isinstance(v, list):
            continue
        pref = top_prefix(k)
        lv = f.get(k)
        if lv is None or lv == "":
            by[pref]["empty"] += 1
        elif isinstance(v, str) and lv == v:
            by[pref]["same"] += 1
            by[pref]["chars"] += len(v)
        else:
            by[pref]["ok"] += 1
    print("===", lang, "===")
    items = sorted(by.items(), key=lambda x: -(x[1]["same"] + x[1]["empty"]))
    for pref, st in items[:30]:
        if st["same"] + st["empty"] == 0:
            continue
        print(
            f"  {pref}: same={st['same']} empty={st['empty']} ok={st['ok']} en_chars={st['chars']}"
        )


# Body block audit in beforeTrip / tips
def collect_bodies(obj, path="", out=None):
    if out is None:
        out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else k
            collect_bodies(v, p, out)
    elif isinstance(obj, list):
        if obj and isinstance(obj[0], dict) and any(
            isinstance(b, dict) and b.get("type") == "text" for b in obj
        ):
            out.append((path, obj))
        else:
            for i, v in enumerate(obj):
                collect_bodies(v, f"{path}[{i}]", out)
    return out


print("\n=== BODY BLOCKS beforeTrip/tips ===")
for section in ["beforeTrip", "tips"]:
    bodies = collect_bodies(en.get(section, {}), section)
    print(f"{section}: {len(bodies)} body arrays")
    for lang in ["vi", "th", "ru", "zh-Hant"]:
        need = 0
        text_need = 0
        for path, blocks in bodies:
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
                if bad and en_t:
                    text_need += 1
                    need = 1
        print(f"  {lang}: bodies_needing_fill~={need} text_blocks_need={text_need}")

# Also check foodLife.quiz
quiz = en.get("foodLife", {}).get("quiz", {})
print("\n=== foodLife.quiz keys ===")
qf = flatten(quiz, "foodLife.quiz")
for lang in ["vi", "th", "ru", "zh-Hant"]:
    lf = flatten(json.loads((ROOT / f"{lang}.json").read_text(encoding="utf-8")))
    same = sum(
        1
        for k, v in qf.items()
        if isinstance(v, str) and lf.get(k) == v and v
    )
    print(f"  {lang}: quiz same_as_en={same}/{len(qf)}")
