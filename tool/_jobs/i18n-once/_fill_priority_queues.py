#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fill remaining vi/th/ru/zh-Hant scalar gaps (priorities 3–5).

Skips codes/URLs/numbers/progress templates. Preserves common.langMenu.
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

from deep_translator import GoogleTranslator

ROOT = Path(__file__).resolve().parent
SECONDARY = ("vi", "th", "ru", "zh-Hant")
GMAP = {"vi": "vi", "th": "th", "ru": "ru", "zh-Hant": "zh-TW"}

# Ordered work queues
QUEUES = {
    "p3_places": ("places.",),
    "p2_quiz": ("foodLife.quiz.",),
    "p4_fun_transport_dishes": ("fun.", "transport.", "dishes."),
    "p4_restaurants": ("restaurants.",),
    "p5_rest": (
        "convenience.",
        "souvenir.",
        "korean.",
        "apps.",
        "areas.",
        "restaurantFields.",
        "misc.",
        "cities.",
        "travelUtils.",
        "home.",
        "emergency.",
        "festivals.",
        "beforeTrip.",
        "tips.",
    ),
}

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
    "previewTitle",  # often Korean proper name from CMS
}

# Leaves that are fine to keep romanized / brand-like if short — still translate labels
BRANDISH_LEAVES = {"name"}  # translate when longer descriptive; keep short brands optionally

EMAIL_RE = re.compile(r"^[\w.+-]+@[\w.-]+\.\w+$")
HTTP_RE = re.compile(r"^https?://", re.I)
ONLY_NUM_RE = re.compile(r"^[\d\s\-–—+/₩$.,:]+$")
PLACEHOLDER_RE = re.compile(r"^\{[^}]+\}$")


def log(msg: str) -> None:
    print(msg, flush=True)


def load(lang: str) -> dict:
    return json.loads((ROOT / f"{lang}.json").read_text(encoding="utf-8"))


def save(lang: str, data: dict) -> None:
    (ROOT / f"{lang}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
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


def unflatten_set(data: dict, flat_key: str, value: str) -> None:
    parts = flat_key.split(".")
    cur = data
    for p in parts[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]
    cur[parts[-1]] = value


def should_skip(key: str, en_val: str) -> bool:
    leaf = key.split(".")[-1]
    if leaf in SKIP_LEAVES:
        return True
    if not en_val or not en_val.strip():
        return True
    if HTTP_RE.match(en_val.strip()):
        return True
    if EMAIL_RE.match(en_val.strip()):
        return True
    if ONLY_NUM_RE.match(en_val.strip()):
        return True
    if PLACEHOLDER_RE.match(en_val.strip()):
        return True
    # pure region codes
    if leaf == "region":
        return True
    # keep progress templates with placeholders
    if "{current}" in en_val or "{total}" in en_val:
        return True
    # korean.p.*.rom / *.en / *.ja / *.zh are intentionally multilingual samples
    if key.startswith("korean.p.") and leaf in ("rom", "en", "ja", "zh", "ko"):
        return True
    return False


def batch_translate(texts: list[str], source: str, target: str, chunk: int = 20) -> list[str]:
    if not texts:
        return []
    out: list[str] = [""] * len(texts)
    tr = GoogleTranslator(source=source, target=target)
    for i in range(0, len(texts), chunk):
        batch = texts[i : i + chunk]
        try:
            if hasattr(tr, "translate_batch"):
                res = tr.translate_batch(batch)
            else:
                res = [tr.translate(t) for t in batch]
            if not isinstance(res, list) or len(res) != len(batch):
                raise RuntimeError("bad batch result")
            for j, r in enumerate(res):
                out[i + j] = (r or "").strip() or batch[j]
        except Exception as exc:
            log(f"  batch fail {source}->{target} @{i}: {exc}; fallback single")
            for j, t in enumerate(batch):
                try:
                    out[i + j] = (tr.translate(t) or "").strip() or t
                except Exception:
                    out[i + j] = t
                time.sleep(0.08)
        log(f"  {source}->{target}: {min(i + chunk, len(texts))}/{len(texts)}")
        time.sleep(0.12)
    return out


def collect_jobs(en_flat: dict, loc_flat: dict, prefixes: tuple[str, ...]) -> list[tuple[str, str]]:
    jobs = []
    for key, en_val in en_flat.items():
        if not isinstance(en_val, str):
            continue
        if not any(key.startswith(p) for p in prefixes):
            continue
        if should_skip(key, en_val):
            continue
        loc_val = loc_flat.get(key)
        if loc_val is None or loc_val == "" or loc_val == en_val:
            # zh-Hant: also treat identical-to-zh as needing conversion later; here == en
            jobs.append((key, en_val))
    return jobs


def fill_queue(queue_name: str, prefixes: tuple[str, ...], langs: tuple[str, ...] | None = None) -> None:
    langs = langs or SECONDARY
    log(f"\n===== QUEUE {queue_name} prefixes={prefixes} =====")
    en_flat = flatten(load("en"))
    for lang in langs:
        data = load(lang)
        menu = (data.get("common") or {}).get("langMenu")
        flat = flatten(data)
        jobs = collect_jobs(en_flat, flat, prefixes)
        log(f"{lang}: {len(jobs)} jobs")
        if not jobs:
            continue
        keys = [j[0] for j in jobs]
        srcs = [j[1] for j in jobs]
        outs = batch_translate(srcs, "en", GMAP[lang], chunk=22)
        changed = 0
        for k, v, src in zip(keys, outs, srcs):
            if v and v != src:
                unflatten_set(data, k, v)
                changed += 1
            elif v and v == src:
                # still write if was empty
                if flat.get(k) in (None, ""):
                    unflatten_set(data, k, v)
                    changed += 1
            else:
                unflatten_set(data, k, src)
        if menu is not None:
            data.setdefault("common", {})["langMenu"] = menu
        save(lang, data)
        log(f"saved {lang}.json changed~={changed}")


def polish_zh_hant_from_zh() -> None:
    """Convert remaining zh-identical body/scalars via OpenCC if available."""
    log("\n===== OpenCC zh-Hant polish =====")
    try:
        sys.path.insert(0, str(ROOT))
        from _s2tw_convert import s2tw  # type: ignore
    except Exception as exc:
        log(f"skip OpenCC: {exc}")
        return

    zh = load("zh")
    hant = load("zh-Hant")
    menu = (hant.get("common") or {}).get("langMenu")
    zh_flat = flatten(zh)
    hant_flat = flatten(hant)
    changed = 0
    for key, zh_val in zh_flat.items():
        if not isinstance(zh_val, str) or not zh_val.strip():
            continue
        leaf = key.split(".")[-1]
        if leaf in SKIP_LEAVES:
            continue
        cur = hant_flat.get(key)
        if cur == zh_val or cur is None or cur == "":
            conv = s2tw(zh_val)
            if conv and conv != cur:
                unflatten_set(hant, key, conv)
                changed += 1
    # also walk body text blocks for zh == zh-Hant
    def walk(obj):
        nonlocal changed
        if isinstance(obj, dict):
            if obj.get("type") == "text":
                z = str(obj.get("zh") or "")
                h = str(obj.get("zh-Hant") or "")
                if z and (not h or h == z):
                    conv = s2tw(z)
                    if conv and conv != h:
                        obj["zh-Hant"] = conv
                        changed += 1
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for i in obj:
                walk(i)

    walk(hant)
    if menu is not None:
        hant.setdefault("common", {})["langMenu"] = menu
    save("zh-Hant", hant)
    log(f"OpenCC scalar/body updates: {changed}")


def main() -> None:
    t0 = time.time()
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode == "all":
        for name, prefixes in QUEUES.items():
            fill_queue(name, prefixes)
        polish_zh_hant_from_zh()
    elif mode in QUEUES:
        fill_queue(mode, QUEUES[mode])
    elif mode == "opencc":
        polish_zh_hant_from_zh()
    else:
        log(f"unknown mode {mode}; choose: all|{'|'.join(QUEUES)}|opencc")
        sys.exit(1)
    log(f"\ndone in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
