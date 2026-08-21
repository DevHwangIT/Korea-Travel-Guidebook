# -*- coding: utf-8 -*-
"""Apply curated ja/zh/zh-Hant/vi/th/ru translations for EN-copied page keys.

Reads translation maps from tool/i18n_pass_data/*.json (en → {lang: text}).
Updates flat string leaves and nested multilingual blocks in page JSON files.
Does not commit. Rebuild messages.js separately.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "i18n" / "pages"
DATA = Path(__file__).resolve().parent / "i18n_pass_data"
TARGET_LANGS = ("ja", "zh", "zh-Hant", "vi", "th", "ru")
SCOPES = ("festivals", "shopping", "before-trip", "convenience")
SKIP_RE = re.compile(r"(Img|Url|URL|href|src)$", re.I)


def load_map() -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for path in sorted(DATA.glob("*.json")):
        if path.name.startswith("_"):
            continue
        chunk = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(chunk, dict):
            continue
        for en, locs in chunk.items():
            if isinstance(locs, dict):
                out.setdefault(en, {}).update(locs)
    return out


def patch_nested(node, tmap: dict[str, dict[str, str]], counts: dict[str, int]) -> None:
    if isinstance(node, dict):
        if "en" in node and isinstance(node.get("en"), str):
            en = node["en"]
            locs = tmap.get(en)
            if locs:
                for lang in TARGET_LANGS:
                    if lang not in locs:
                        continue
                    cur = node.get(lang)
                    if cur is None or cur == "" or cur == en:
                        node[lang] = locs[lang]
                        counts[lang] = counts.get(lang, 0) + 1
            return
        for v in node.values():
            patch_nested(v, tmap, counts)
    elif isinstance(node, list):
        for v in node:
            patch_nested(v, tmap, counts)


def patch_flat(obj, lang: str, en_flat: dict[str, str], tmap: dict[str, dict[str, str]], counts: dict[str, int], prefix: str = "") -> None:
    if not isinstance(obj, dict):
        return
    for k, v in list(obj.items()):
        path = f"{prefix}.{k}" if prefix else k
        if isinstance(v, str):
            if SKIP_RE.search(k) or v.startswith("http") or v.startswith("Images/"):
                continue
            en_v = en_flat.get(path)
            if en_v is None:
                continue
            if v != en_v and v != "":
                continue
            locs = tmap.get(en_v)
            if not locs or lang not in locs:
                continue
            obj[k] = locs[lang]
            counts[lang] = counts.get(lang, 0) + 1
        elif isinstance(v, dict):
            # skip pure multilingual leaves handled in patch_nested
            if "en" in v and "ko" in v and isinstance(v.get("en"), str):
                continue
            patch_flat(v, lang, en_flat, tmap, counts, path)
        elif isinstance(v, list):
            continue


def flatten_strings(d, prefix: str = "") -> dict[str, str]:
    out: dict[str, str] = {}
    if isinstance(d, dict):
        for k, v in d.items():
            p = f"{prefix}.{k}" if prefix else k
            if isinstance(v, str):
                out[p] = v
            elif isinstance(v, dict) and not (
                "en" in v and "ko" in v and isinstance(v.get("en"), str)
            ):
                out.update(flatten_strings(v, p))
    return out


def main() -> None:
    tmap = load_map()
    print(f"loaded {len(tmap)} EN keys from {DATA}")
    totals: dict[str, int] = {lang: 0 for lang in TARGET_LANGS}
    for scope in SCOPES:
        scope_dir = PAGES / scope
        en_data = json.loads((scope_dir / "en.json").read_text(encoding="utf-8"))
        en_flat = flatten_strings(en_data)
        for lang in list(TARGET_LANGS) + ["ko", "en"]:
            path = scope_dir / f"{lang}.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            counts: dict[str, int] = {}
            # Always sync nested multilingual fields for all target langs
            patch_nested(data, tmap, counts)
            if lang in TARGET_LANGS:
                patch_flat(data, lang, en_flat, tmap, counts)
            path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            for k, n in counts.items():
                totals[k] = totals.get(k, 0) + n
            if counts:
                print(f"  {scope}/{lang}.json: {sum(counts.values())} edits ({counts})")
    print("TOTAL nested+flat edits by locale:", totals)


if __name__ == "__main__":
    main()
