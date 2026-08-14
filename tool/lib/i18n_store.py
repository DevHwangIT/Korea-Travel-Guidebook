# -*- coding: utf-8 -*-
"""Load / save locale JSON files and rebuild messages.js."""
from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

from .paths import I18N_DIR, ROOT

# Editorial primary locales. Runtime also ships zh-Hant / vi / th / ru via build-bundle.
LANGS = ("ko", "en", "ja", "zh")
BUNDLE_LANGS = ("ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru")


def load_lang(lang: str) -> dict[str, Any]:
    path = I18N_DIR / f"{lang}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_all() -> dict[str, dict[str, Any]]:
    return {lang: load_lang(lang) for lang in LANGS}


def save_lang(lang: str, data: dict[str, Any]) -> None:
    path = I18N_DIR / f"{lang}.json"
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def save_all(bundle: dict[str, dict[str, Any]]) -> None:
    for lang in LANGS:
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
