# -*- coding: utf-8 -*-
"""Load / save locale JSON files and rebuild messages.js.

Source layout (see i18n/locale_routing.py + README-locales.md):
  i18n/common/{lang}.json
  i18n/pages/<group>/{lang}.json
  i18n/{lang}.json          — assembled mirror (also residual fallback)

load_* merges sources; save_* routes top-level keys into the correct source
files, then refreshes the assembled mirror. Callers still invoke build_bundle()
to regenerate messages.js.
"""
from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

from .paths import I18N_DIR, ROOT

# Keep in sync with js/i18n.js GUIDE_LANGS and i18n/build-bundle.py LANGS.
BUNDLE_LANGS = ("ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru")
# All locales are first-class for load/save/scaffold (same pipeline as public site).
LANGS = BUNDLE_LANGS

# Display labels for admin / docs
LANG_LABELS = {
    "ko": "한국어",
    "en": "English",
    "ja": "日本語",
    "zh": "简体中文",
    "zh-Hant": "繁體中文",
    "vi": "Tiếng Việt",
    "th": "ภาษาไทย",
    "ru": "Русский",
}


def _routing():
    """Lazy-import i18n/locale_routing.py without requiring package install."""
    import importlib.util

    path = I18N_DIR / "locale_routing.py"
    spec = importlib.util.spec_from_file_location("i18n_locale_routing", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_lang(lang: str) -> dict[str, Any]:
    """Return full merged locale dict (common + pages + residual fallback)."""
    return _routing().load_merged_lang(lang)


def load_all() -> dict[str, dict[str, Any]]:
    return {lang: load_lang(lang) for lang in LANGS}


def save_lang(lang: str, data: dict[str, Any]) -> None:
    """Route top-level keys into source files and refresh assembled mirror."""
    routing = _routing()
    routing.write_sources_for_lang(lang, data)
    routing.write_assembled_lang(lang, data)


def save_all(bundle: dict[str, dict[str, Any]]) -> None:
    for lang in LANGS:
        if lang in bundle:
            save_lang(lang, bundle[lang])


def build_bundle() -> str:
    script = I18N_DIR / "build-bundle.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"build-bundle.py failed:\n{result.stdout}\n{result.stderr}"
        )
    return (result.stdout or "").strip() or "updated messages.js"


def get_nested(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    cur: Any = data
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def set_nested(data: dict[str, Any], keys: list[str], value: Any) -> None:
    cur = data
    for key in keys[:-1]:
        nxt = cur.get(key)
        if not isinstance(nxt, dict):
            nxt = {}
            cur[key] = nxt
        cur = nxt
    cur[keys[-1]] = value


def del_nested(data: dict[str, Any], keys: list[str]) -> bool:
    cur = data
    for key in keys[:-1]:
        if not isinstance(cur, dict) or key not in cur:
            return False
        cur = cur[key]
    if isinstance(cur, dict) and keys[-1] in cur:
        del cur[keys[-1]]
        return True
    return False


def deep_copy_value(value: Any) -> Any:
    return deepcopy(value)
