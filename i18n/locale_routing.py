# -*- coding: utf-8 -*-
"""Shared locale routing: common/ + pages/ ownership and deep-merge helpers.

Keep KEY_OWNERS in sync with i18n/README-locales.md.
Runtime contract is unchanged: build-bundle.py still emits window.__I18N_MESSAGES__.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

LANGS = ("ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru")

I18N_DIR = Path(__file__).resolve().parent

# Top-level key → owner directory under i18n/
# "common" → i18n/common/{lang}.json
# "pages/foo" → i18n/pages/foo/{lang}.json
KEY_OWNERS: dict[str, str] = {
    # shared / site-wide
    "common": "common",
    "cities": "common",
    "areas": "common",
    "restaurantFields": "common",
    "misc": "common",
    # page groups
    "home": "pages/home",
    "beforeTrip": "pages/before-trip",
    "prepTips": "pages/before-trip",
    "tips": "pages/travel-tips",
    "travelCourses": "pages/travel-courses",
    "apps": "pages/apps",
    "dishes": "pages/foods",
    "restaurants": "pages/foods",
    "foodLife": "pages/foods",
    "foodsHub": "pages/foods",
    "mealsIndex": "pages/foods",
    "dessertsIndex": "pages/foods",
    "prepHub": "pages/prep",
    "transport": "pages/transport",
    "places": "pages/transport",
    "fun": "pages/fun",
    "shopping": "pages/shopping",
    "souvenir": "pages/shopping",
    "buyHub": "pages/shopping",
    "convenience": "pages/convenience",
    "emergency": "pages/emergency",
    "festivals": "pages/festivals",
    "korean": "pages/korean",
    "privacy": "pages/misc",
    "welcome": "pages/misc",
    "travelUtils": "pages/misc",
}

DEFAULT_OWNER = "pages/_other"


def owner_for_key(key: str) -> str:
    return KEY_OWNERS.get(key, DEFAULT_OWNER)


def owner_dir(owner: str) -> Path:
    return I18N_DIR / owner


def owner_lang_path(owner: str, lang: str) -> Path:
    return owner_dir(owner) / f"{lang}.json"


def residual_path(lang: str) -> Path:
    return I18N_DIR / f"{lang}.json"


def deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    """In-place deep merge of overlay into base; returns base."""
    for key, value in overlay.items():
        if (
            key in base
            and isinstance(base[key], dict)
            and isinstance(value, dict)
        ):
            deep_merge(base[key], value)
        else:
            base[key] = value
    return base


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return {}
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError(f"Expected object in {path}")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    """Write JSON with retries; use atomic replace to avoid Windows file locks."""
    import os
    import tempfile

    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    last_exc: Exception | None = None
    for attempt in range(8):
        tmp_name = None
        try:
            fd, tmp_name = tempfile.mkstemp(
                prefix=f".{path.stem}-",
                suffix=".json.tmp",
                dir=str(path.parent),
            )
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
                f.write(payload)
            os.replace(tmp_name, path)
            tmp_name = None
            return
        except OSError as exc:
            last_exc = exc
            time.sleep(0.4 * (attempt + 1))
        finally:
            if tmp_name and os.path.exists(tmp_name):
                try:
                    os.unlink(tmp_name)
                except OSError:
                    pass
    assert last_exc is not None
    raise last_exc


def iter_page_lang_files(lang: str) -> list[Path]:
    pages_root = I18N_DIR / "pages"
    if not pages_root.is_dir():
        return []
    return sorted(pages_root.glob(f"**/{lang}.json"))


def load_merged_lang(lang: str) -> dict[str, Any]:
    """Merge residual (fallback) → common → pages/** into one dict."""
    result: dict[str, Any] = {}

    residual = _read_json(residual_path(lang))
    if residual:
        deep_merge(result, residual)

    common = _read_json(owner_lang_path("common", lang))
    if common:
        deep_merge(result, common)

    for path in iter_page_lang_files(lang):
        page_data = _read_json(path)
        if page_data:
            deep_merge(result, page_data)

    return result


def split_by_owner(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Group top-level keys into owner → partial locale dict."""
    buckets: dict[str, dict[str, Any]] = {}
    for key, value in data.items():
        owner = owner_for_key(key)
        buckets.setdefault(owner, {})[key] = value
    return buckets


def _existing_owners_for_lang(lang: str) -> set[str]:
    """Owners that already have a source file for this language."""
    owners: set[str] = set()
    if owner_lang_path("common", lang).is_file():
        owners.add("common")
    pages_root = I18N_DIR / "pages"
    if pages_root.is_dir():
        for path in pages_root.glob(f"**/{lang}.json"):
            owners.add(path.relative_to(I18N_DIR).parent.as_posix())
    return owners


def write_sources_for_lang(lang: str, data: dict[str, Any]) -> list[Path]:
    """Write split source files for one language; return paths written.

    Rewrites existing owner files even when empty so removed top-level keys
    do not linger and get re-merged from stale page/common JSON.
    """
    written: list[Path] = []
    buckets = split_by_owner(data)
    owners = set(buckets.keys()) | _existing_owners_for_lang(lang)
    for owner in sorted(owners):
        partial = buckets.get(owner, {})
        path = owner_lang_path(owner, lang)
        write_json(path, partial)
        written.append(path)
    return written


def write_assembled_lang(lang: str, data: dict[str, Any] | None = None) -> Path:
    """Write canonical assembled i18n/{lang}.json (CMS / git mirror)."""
    merged = data if data is not None else load_merged_lang(lang)
    path = residual_path(lang)
    write_json(path, merged)
    return path


def count_leaf_keys(obj: Any) -> int:
    if isinstance(obj, dict):
        return sum(count_leaf_keys(v) for v in obj.values())
    if isinstance(obj, list):
        return sum(count_leaf_keys(v) for v in obj)
    return 1
