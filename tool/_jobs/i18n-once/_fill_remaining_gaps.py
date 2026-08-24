#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fill remaining vi/th/ru/zh-Hant gaps: body blocks, quiz, places, fun, dishes, transport.

Uses tool/lib/translate.py (deep-translator). Idempotent: skips strings that already
differ from English (and body keys that already have native text ≠ en/ko copy).
Preserves common.langMenu.
"""
from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
sys.path.insert(0, str(REPO / "tool"))

from lib.translate import (  # noqa: E402
    BatchStatus,
    SECONDARY_TARGET_LANGS,
    translate_text,
)

LANG_FILES = ("ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru")
SECONDARY = ("vi", "th", "ru", "zh-Hant")

# Priority scalar path prefixes (flat keys) to translate when locale == en
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

# Skip translating these leaf keys (URLs, ids, codes)
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
    "progress",  # "{current} / {total}"
}


def load(lang: str) -> dict:
    return json.loads((ROOT / f"{lang}.json").read_text(encoding="utf-8"))


def save(lang: str, data: dict) -> None:
    (ROOT / f"{lang}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def walk_set_bodies(obj, filled_by_path: dict[str, list], path: str = "") -> int:
    """Replace body arrays at known paths with filled versions; return count replaced."""
    n = 0
    if isinstance(obj, dict):
        for k, v in list(obj.items()):
            p = f"{path}.{k}" if path else k
            if isinstance(v, list) and v and isinstance(v[0], dict) and any(
                isinstance(b, dict) and b.get("type") == "text" for b in v
            ):
                # Match by collecting text en fingerprints
                key = body_fingerprint(v)
                if key in filled_by_path:
                    obj[k] = deepcopy(filled_by_path[key])
                    n += 1
                else:
                    n += walk_set_bodies(v, filled_by_path, p)
            else:
                n += walk_set_bodies(v, filled_by_path, p)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            n += walk_set_bodies(v, filled_by_path, f"{path}[{i}]")
    return n


def body_fingerprint(blocks: list) -> str:
    parts = []
    for b in blocks:
        if not isinstance(b, dict):
            continue
        if b.get("type") == "text":
            parts.append("T:" + (b.get("ko") or b.get("en") or "")[:120])
        elif b.get("type") == "image":
            parts.append("I:" + str(b.get("src") or ""))
        elif b.get("type") == "youtube":
            parts.append("Y:" + str(b.get("url") or ""))
    return "||".join(parts)


def collect_bodies(obj, out: list | None = None) -> list:
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


def needs_secondary(block: dict, lang: str) -> bool:
    en = str(block.get("en") or "").strip()
    ko = str(block.get("ko") or "").strip()
    cur = str(block.get(lang) or "").strip()
    if not cur:
        return True
    if cur == en or cur == ko:
        return True
    # zh-Hant that is still simplified copy of zh
    if lang == "zh-Hant":
        zh = str(block.get("zh") or "").strip()
        if zh and cur == zh:
            return True
    return False


def fill_text_block_secondary(block: dict, status: BatchStatus) -> dict:
    """Add vi/th/ru/zh-Hant on a text block without re-translating en/ja/zh."""
    nb = dict(block)
    if str(nb.get("type") or "") != "text":
        return nb
    ko = str(nb.get("ko") or "").strip()
    en = str(nb.get("en") or "").strip() or ko
    if not ko and not en:
        return nb

    langs_needed = [lang for lang in SECONDARY if needs_secondary(nb, lang)]
    if not langs_needed:
        return nb

    def one_lang(lang: str) -> tuple[str, str, BatchStatus]:
        local = BatchStatus()
        src = ko or en
        out = ""
        if ko:
            out = translate_text(ko, lang, status=local)
        if not out or out.strip() == src.strip():
            try:
                from deep_translator import GoogleTranslator

                gmap = {"zh-Hant": "zh-TW", "vi": "vi", "th": "th", "ru": "ru"}
                out = (
                    GoogleTranslator(source="en", target=gmap[lang]).translate(en) or ""
                ).strip() or en
                local.translated += 1
            except Exception as exc:  # noqa: BLE001
                local.errors.append(str(exc))
                local.copied += 1
                out = en
        return lang, out, local

    with ThreadPoolExecutor(max_workers=4) as pool:
        for lang, out, local in pool.map(one_lang, langs_needed):
            nb[lang] = out
            status.translated += local.translated
            status.copied += local.copied
            status.errors.extend(local.errors)
            if not status.provider and local.provider:
                status.provider = local.provider
    return nb


def fill_all_bodies() -> BatchStatus:
    print("=== Body blocks ===")
    src = load("ko")
    bodies = collect_bodies(src)
    print(f"found {len(bodies)} body arrays")

    status = BatchStatus()
    text_jobs: list[dict] = []
    for blocks in bodies:
        for b in blocks:
            if str(b.get("type") or "") == "text" and any(
                needs_secondary(b, lang) for lang in SECONDARY
            ):
                text_jobs.append(b)

    print(f"text blocks needing secondary: {len(text_jobs)}")

    def block_key(b: dict) -> str:
        return (b.get("ko") or b.get("en") or "")[:200]

    unique_results: dict[str, dict] = {}
    translated_blocks = 0
    for b in text_jobs:
        bk = block_key(b)
        if bk in unique_results:
            continue
        unique_results[bk] = fill_text_block_secondary(b, status)
        translated_blocks += 1
        if translated_blocks % 15 == 0:
            print(
                f"  text {translated_blocks} unique | "
                f"tr={status.translated} copy={status.copied}"
            )

    filled_map: dict[str, list] = {}
    for blocks in bodies:
        new_blocks = []
        for b in blocks:
            if str(b.get("type") or "") == "text":
                new_blocks.append(deepcopy(unique_results.get(block_key(b)) or b))
            else:
                new_blocks.append(dict(b))
        filled_map[body_fingerprint(blocks)] = new_blocks

    print(f"body translate done: {status.note_lines()}")

    for lang in LANG_FILES:
        data = load(lang)
        lang_menu = (data.get("common") or {}).get("langMenu")
        n = walk_set_bodies(data, filled_map)
        if lang_menu is not None:
            data.setdefault("common", {})["langMenu"] = lang_menu
        save(lang, data)
        print(f"  wrote bodies into {lang}.json ({n} arrays)")
    return status

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
    if not en_val.strip():
        return False
    leaf = key.split(".")[-1]
    if leaf in SKIP_LEAVES:
        return False
    if key.startswith("http") or en_val.startswith("http"):
        return False
    # brand-ish short identical tokens often stay
    if loc_val != en_val:
        return False
    if not any(key.startswith(p) for p in SCALAR_PREFIXES):
        return False
    return True


def translate_scalars(langs: tuple[str, ...] = SECONDARY, max_per_lang: int | None = None) -> None:
    print("=== Scalar strings ===")
    en = flatten(load("en"))
    ko = flatten(load("ko"))

    for lang in langs:
        data = load(lang)
        lang_menu = (data.get("common") or {}).get("langMenu")
        flat = flatten(data)
        jobs = []
        for key, en_val in en.items():
            loc_val = flat.get(key, en_val if key in flat else None)
            if loc_val is None:
                # missing key — fill from en then translate
                loc_val = en_val
                unflatten_set(data, key, en_val)
                flat[key] = en_val
            if should_translate_scalar(key, en_val, loc_val):
                ko_val = ko.get(key) or en_val
                jobs.append((key, ko_val if isinstance(ko_val, str) else en_val))
        if max_per_lang:
            jobs = jobs[:max_per_lang]
        print(f"{lang}: {len(jobs)} scalars to translate")

        status = BatchStatus()
        # Parallel but limited
        results: dict[str, str] = {}

        def one(item):
            key, src = item
            # Prefer KO source; translate_text expects KO
            out = translate_text(src, lang, status=status)
            # If engine returned KO unchanged for secondary, fall back to translating EN
            if out.strip() == src.strip() and lang in SECONDARY_TARGET_LANGS:
                en_src = en.get(key) or src
                if en_src != src:
                    # translate from EN via deep-translator by temporarily using EN as KO
                    # Better: use GoogleTranslator source=en
                    try:
                        from deep_translator import GoogleTranslator

                        gmap = {
                            "zh-Hant": "zh-TW",
                            "vi": "vi",
                            "th": "th",
                            "ru": "ru",
                        }
                        gt = GoogleTranslator(source="en", target=gmap[lang])
                        out2 = (gt.translate(en_src) or "").strip()
                        if out2:
                            out = out2
                    except Exception:
                        out = en_src
                else:
                    out = en_src
            return key, out

        workers = 6
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futs = [pool.submit(one, j) for j in jobs]
            done = 0
            for fut in as_completed(futs):
                key, val = fut.result()
                results[key] = val
                done += 1
                if done % 50 == 0:
                    print(f"  {lang} {done}/{len(jobs)}")

        for key, val in results.items():
            unflatten_set(data, key, val)

        if lang_menu is not None:
            data.setdefault("common", {})["langMenu"] = lang_menu
        save(lang, data)
        print(f"  saved {lang}.json ({len(results)} updated) {status.note_lines()}")


def polish_zh_hant_bodies_opencc() -> None:
    """Convert zh-Hant body text that still equals simplified zh via OpenCC dicts."""
    print("=== zh-Hant OpenCC body polish ===")
    sys.path.insert(0, str(ROOT))
    try:
        from _s2tw_convert import s2tw  # type: ignore
    except Exception as exc:
        print("OpenCC helper unavailable:", exc)
        return

    changed = 0
    for lang in LANG_FILES:
        data = load(lang)
        lang_menu = (data.get("common") or {}).get("langMenu")

        def walk(obj):
            nonlocal changed
            if isinstance(obj, dict):
                if obj.get("type") == "text":
                    zh = str(obj.get("zh") or "")
                    hant = str(obj.get("zh-Hant") or "")
                    if zh and (not hant or hant == zh):
                        converted = s2tw(zh)
                        if converted and converted != hant:
                            obj["zh-Hant"] = converted
                            changed += 1
                    elif hant and hant == zh:
                        converted = s2tw(hant)
                        if converted != hant:
                            obj["zh-Hant"] = converted
                            changed += 1
                for v in obj.values():
                    walk(v)
            elif isinstance(obj, list):
                for i in obj:
                    walk(i)

        walk(data)
        if lang_menu is not None:
            data.setdefault("common", {})["langMenu"] = lang_menu
        save(lang, data)
    print(f"OpenCC body updates: {changed}")


def main() -> None:
    t0 = time.time()
    mode = (sys.argv[1] if len(sys.argv) > 1 else "all").strip()
    if mode in ("all", "bodies"):
        fill_all_bodies()
        polish_zh_hant_bodies_opencc()
    if mode in ("all", "scalars"):
        # Priority first via prefixes order already in SCALAR_PREFIXES
        translate_scalars()
    print(f"done in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
