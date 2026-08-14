#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge locale overlays into vi/th/ru and polish zh-Hant; then rebuild bundle helpers."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OVER = ROOT / "_overlays"


def deep_merge(base: dict, overlay: dict) -> dict:
    out = deepcopy(base)
    for k, v in overlay.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = deepcopy(v)
    return out


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def add_body_lang_keys(obj, translations: dict[str, dict[str, str]], lang: str):
    """translations: {en_text: translated}. Add lang key on text blocks."""
    if isinstance(obj, dict):
        if obj.get("type") == "text" and "en" in obj:
            en = str(obj.get("en") or "")
            if lang not in obj or not str(obj.get(lang) or "").strip():
                if en in translations:
                    obj[lang] = translations[en]
                elif en:
                    # Prefer EN over leaving missing (public fallback already uses en)
                    obj[lang] = en
            for v in obj.values():
                add_body_lang_keys(v, translations, lang)
        else:
            for v in obj.values():
                add_body_lang_keys(v, translations, lang)
    elif isinstance(obj, list):
        for item in obj:
            add_body_lang_keys(item, translations, lang)


def main() -> None:
    # --- core overlays ---
    for lang in ("vi", "th", "ru"):
        path = ROOT / f"{lang}.json"
        data = load_json(path)
        core = load_json(OVER / f"{lang}_core.json")
        data = deep_merge(data, core)
        # beforeTrip / tips / extra if present
        for name in ("beforeTrip", "tips", "emergency", "apps", "shopping", "fun", "transport"):
            p = OVER / f"{lang}_{name}.json"
            if p.is_file():
                data = deep_merge(data, {name: load_json(p)})
        save_json(path, data)
        print(f"merged overlays → {lang}.json")

    # zh-Hant polish: prefer 出發前 for before-trip chrome (TW style)
    hant = load_json(ROOT / "zh-Hant.json")
    polish = {
        "beforeTrip": {
            "title": "出發前",
            "pageTitle": "出發前 | Korea Travel Guide",
            "backHub": "← 出發前",
        },
        "home": {
            "menuBeforeTrip": "出發前",
            "menuKoreaBasics": "出發前",
        },
        "common": {
            "explore": "探索韓國",
        },
    }
    hant = deep_merge(hant, polish)
    # Ensure body text blocks expose zh-Hant key (copy converted zh field)
    def ensure_hant_body(obj):
        if isinstance(obj, dict):
            if obj.get("type") == "text":
                zh = str(obj.get("zh") or "")
                if zh and not str(obj.get("zh-Hant") or "").strip():
                    obj["zh-Hant"] = zh
            for v in obj.values():
                ensure_hant_body(v)
        elif isinstance(obj, list):
            for i in obj:
                ensure_hant_body(i)

    ensure_hant_body(hant)
    save_json(ROOT / "zh-Hant.json", hant)
    print("polished zh-Hant.json")


if __name__ == "__main__":
    main()
