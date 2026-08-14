#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fast batch fill of vi/th/ru/zh-Hant for body blocks + priority scalars."""
from __future__ import annotations

import json
import sys
import time
from copy import deepcopy
from pathlib import Path

from deep_translator import GoogleTranslator

ROOT = Path(__file__).resolve().parent
LANG_FILES = ("ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru")
SECONDARY = ("vi", "th", "ru", "zh-Hant")
GMAP = {"vi": "vi", "th": "th", "ru": "ru", "zh-Hant": "zh-TW"}

# Priority scalar prefixes (ordered)
SCALAR_PREFIXES = (
    "foodLife.quiz.",
    "places.",
    "fun.",
    "dishes.",
    "transport.",
    "restaurants.",
    "areas.",
    "restaurantFields.",
    "convenience.",
    "souvenir.",
    "korean.",
    "apps.",
    "misc.",
    "cities.",
    "home.",
    "beforeTrip.",
    "tips.",
    "emergency.",
    "festivals.",
    "travelUtils.",
)
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
}


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


def body_fingerprint(blocks: list) -> str:
    parts = []
    for b in blocks:
        if not isinstance(b, dict):
            continue
        t = b.get("type")
        if t == "text":
            parts.append("T:" + (b.get("ko") or b.get("en") or "")[:120])
        elif t == "image":
            parts.append("I:" + str(b.get("src") or ""))
        elif t == "youtube":
            parts.append("Y:" + str(b.get("url") or ""))
    return "||".join(parts)


def collect_bodies(obj, out=None):
    if out is None:
        out = []
    if isinstance(obj, dict):
        for v in obj.values():
            collect_bodies(v, out)
    elif isinstance(obj, list):
        if obj and isinstance(obj[0], dict) and any(
            isinstance(b, dict) and b.get("type") == "text" for b in obj
        ):
            out.append(obj)
        else:
            for v in obj:
                collect_bodies(v, out)
    return out


def walk_set_bodies(obj, filled_map: dict) -> int:
    n = 0
    if isinstance(obj, dict):
        for k, v in list(obj.items()):
            if isinstance(v, list) and v and isinstance(v[0], dict) and any(
                isinstance(b, dict) and b.get("type") == "text" for b in v
            ):
                key = body_fingerprint(v)
                if key in filled_map:
                    obj[k] = deepcopy(filled_map[key])
                    n += 1
                else:
                    n += walk_set_bodies(v, filled_map)
            else:
                n += walk_set_bodies(v, filled_map)
    elif isinstance(obj, list):
        for item in obj:
            n += walk_set_bodies(item, filled_map)
    return n


def needs_secondary(block: dict, lang: str) -> bool:
    en = str(block.get("en") or "").strip()
    ko = str(block.get("ko") or "").strip()
    cur = str(block.get(lang) or "").strip()
    if not cur:
        return True
    if cur == en or cur == ko:
        return True
    if lang == "zh-Hant":
        zh = str(block.get("zh") or "").strip()
        if zh and cur == zh:
            return True
    return False


def batch_translate(texts: list[str], source: str, target: str, chunk: int = 20) -> list[str]:
    """Translate list; on failure fall back one-by-one then to original."""
    if not texts:
        return []
    out: list[str] = [""] * len(texts)
    tr = GoogleTranslator(source=source, target=target)
    for i in range(0, len(texts), chunk):
        batch = texts[i : i + chunk]
        try:
            # translate_batch may not exist on all versions — try both
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
                time.sleep(0.05)
        log(f"  {source}->{target}: {min(i + chunk, len(texts))}/{len(texts)}")
        time.sleep(0.15)
    return out


def fill_bodies() -> None:
    log("=== Body blocks (batch) ===")
    src = load("ko")
    bodies = collect_bodies(src)
    log(f"body arrays: {len(bodies)}")

    # Unique text blocks by KO (or EN)
    unique: dict[str, dict] = {}
    for blocks in bodies:
        for b in blocks:
            if not isinstance(b, dict) or b.get("type") != "text":
                continue
            key = (b.get("ko") or b.get("en") or "")[:240]
            if key and key not in unique:
                unique[key] = dict(b)
    log(f"unique text blocks: {len(unique)}")

    # Build source list (prefer KO, else EN)
    keys = list(unique.keys())
    ko_srcs = []
    en_srcs = []
    for k in keys:
        b = unique[k]
        ko = str(b.get("ko") or "").strip()
        en = str(b.get("en") or "").strip()
        ko_srcs.append(ko if ko else en)
        en_srcs.append(en if en else ko)

    for lang in SECONDARY:
        need_idx = [i for i, k in enumerate(keys) if needs_secondary(unique[k], lang)]
        log(f"{lang}: need {len(need_idx)}")
        if not need_idx:
            continue
        # Translate from EN for reliability on secondary langs (Google KO→vi/th/ru ok too;
        # EN tends to be cleaner for long travel copy already reviewed)
        srcs = [en_srcs[i] for i in need_idx]
        # Prefer KO when available and lang supports it well
        use_src = "en"
        translated = batch_translate(srcs, use_src, GMAP[lang])
        for j, i in enumerate(need_idx):
            unique[keys[i]][lang] = translated[j]

    filled_map = {}
    for blocks in bodies:
        new_blocks = []
        for b in blocks:
            if isinstance(b, dict) and b.get("type") == "text":
                key = (b.get("ko") or b.get("en") or "")[:240]
                new_blocks.append(deepcopy(unique.get(key) or b))
            else:
                new_blocks.append(dict(b) if isinstance(b, dict) else b)
        filled_map[body_fingerprint(blocks)] = new_blocks

    for lang in LANG_FILES:
        data = load(lang)
        menu = (data.get("common") or {}).get("langMenu")
        n = walk_set_bodies(data, filled_map)
        if menu is not None:
            data.setdefault("common", {})["langMenu"] = menu
        save(lang, data)
        log(f"wrote {lang}.json bodies n={n}")


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


def should_translate_scalar(key: str, en_val, loc_val) -> bool:
    if not isinstance(en_val, str) or not isinstance(loc_val, str):
        return False
    if not en_val.strip() or loc_val != en_val:
        return False
    leaf = key.split(".")[-1]
    if leaf in SKIP_LEAVES:
        return False
    if en_val.startswith("http"):
        return False
    return any(key.startswith(p) for p in SCALAR_PREFIXES)


def fill_scalars(priority_only: bool = False) -> None:
    log("=== Scalars (batch) ===")
    prefixes = (
        (
            "foodLife.quiz.",
            "places.",
            "fun.",
            "dishes.",
            "transport.",
            "beforeTrip.",
            "tips.",
            "home.",
            "emergency.",
            "festivals.",
        )
        if priority_only
        else SCALAR_PREFIXES
    )
    en = flatten(load("en"))
    for lang in SECONDARY:
        data = load(lang)
        menu = (data.get("common") or {}).get("langMenu")
        flat = flatten(data)
        jobs = []
        for key, en_val in en.items():
            if not any(key.startswith(p) for p in prefixes):
                continue
            loc_val = flat.get(key)
            if loc_val is None:
                unflatten_set(data, key, en_val)
                loc_val = en_val
                flat[key] = en_val
            if should_translate_scalar(key, en_val, loc_val):
                jobs.append((key, en_val))
        log(f"{lang}: {len(jobs)} scalars")
        if not jobs:
            if menu is not None:
                data.setdefault("common", {})["langMenu"] = menu
            save(lang, data)
            continue
        keys = [j[0] for j in jobs]
        srcs = [j[1] for j in jobs]
        outs = batch_translate(srcs, "en", GMAP[lang], chunk=25)
        for k, v in zip(keys, outs):
            unflatten_set(data, k, v)
        if menu is not None:
            data.setdefault("common", {})["langMenu"] = menu
        save(lang, data)
        log(f"saved {lang}.json")


def polish_opencc() -> None:
    log("=== OpenCC zh-Hant body polish ===")
    try:
        sys.path.insert(0, str(ROOT))
        from _s2tw_convert import s2tw  # type: ignore
    except Exception as exc:
        log(f"skip OpenCC: {exc}")
        return
    changed = 0
    for lang in LANG_FILES:
        data = load(lang)
        menu = (data.get("common") or {}).get("langMenu")

        def walk(obj):
            nonlocal changed
            if isinstance(obj, dict):
                if obj.get("type") == "text":
                    zh = str(obj.get("zh") or "")
                    hant = str(obj.get("zh-Hant") or "")
                    if zh and (not hant or hant == zh):
                        conv = s2tw(zh)
                        if conv and conv != hant:
                            obj["zh-Hant"] = conv
                            changed += 1
                for v in obj.values():
                    walk(v)
            elif isinstance(obj, list):
                for i in obj:
                    walk(i)

        walk(data)
        if menu is not None:
            data.setdefault("common", {})["langMenu"] = menu
        save(lang, data)
    log(f"OpenCC updates: {changed}")


def main() -> None:
    t0 = time.time()
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("all", "bodies"):
        fill_bodies()
        polish_opencc()
    if mode in ("all", "scalars", "priority"):
        fill_scalars(priority_only=(mode == "priority"))
    if mode == "scalars-rest":
        # heavier leftovers
        global SCALAR_PREFIXES
        SCALAR_PREFIXES = (
            "restaurants.",
            "areas.",
            "restaurantFields.",
            "convenience.",
            "souvenir.",
            "korean.",
            "apps.",
            "misc.",
            "cities.",
            "travelUtils.",
        )
        fill_scalars(priority_only=False)
    log(f"done in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
