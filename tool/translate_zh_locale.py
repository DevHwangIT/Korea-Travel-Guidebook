# -*- coding: utf-8 -*-
"""Translate i18n/zh.json string leaves from Korean (deep-translator).

Usage:
  python tool/translate_zh_locale.py           # critical + dishes/apps/home…
  python tool/translate_zh_locale.py --all     # all top-level namespaces
  python tool/translate_zh_locale.py --skip-restaurants
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
import time
from pathlib import Path
from typing import Any

TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from lib import i18n_store  # noqa: E402
from lib.cache_bust import bump_asset_version  # noqa: E402
from lib.translate import BatchStatus, translate_text  # noqa: E402

CRITICAL_TOP = {
    "home",
    "common",
    "apps",
    "misc",
    "foodLife",
    "prepHub",
    "buyHub",
    "restaurantFields",
    "festivals",
    "tips",
    "beforeTrip",
    "emergency",
    "korean",
    "mealsIndex",
    "dessertsIndex",
    "foodsHub",
}

WALK_TOP = CRITICAL_TOP | {
    "dishes",
    "shopping",
    "souvenir",
    "convenience",
    "fun",
    "transport",
    "cities",
    "areas",
    "places",
}


def _looks_korean(text: str) -> bool:
    return any("\uac00" <= ch <= "\ud7a3" for ch in text)


def _translate_leaf(text: str, status: BatchStatus) -> str:
    t = (text or "").strip()
    if not t:
        return t
    if not _looks_korean(t):
        return t
    out = translate_text(t, "zh", status=status)
    time.sleep(0.02)
    return out or t


def walk_translate(
    ko_node: Any,
    zh_node: Any,
    *,
    status: BatchStatus,
    force: bool,
    path: str = "",
) -> Any:
    if isinstance(ko_node, dict):
        # Already multilingual menu name objects — keep as-is (synced from KO)
        if path.endswith(".name") and all(k in ko_node for k in ("ko", "en", "ja")):
            out = dict(ko_node)
            if force or not str(out.get("zh") or "").strip() or _looks_korean(
                str(out.get("zh") or "")
            ):
                if out.get("zh") and not _looks_korean(str(out["zh"])) and not force:
                    return out
                out["zh"] = _translate_leaf(str(out.get("ko") or ""), status)
            return out

        if str(ko_node.get("type") or "") == "text" and "ko" in ko_node:
            out = dict(zh_node) if isinstance(zh_node, dict) else dict(ko_node)
            for lang in ("ko", "en", "ja"):
                if lang in ko_node:
                    out[lang] = ko_node[lang]
            zh_val = str(out.get("zh") or "").strip()
            ko_val = str(ko_node.get("ko") or "").strip()
            if force or not zh_val or zh_val == ko_val or _looks_korean(zh_val):
                out["zh"] = _translate_leaf(ko_val, status) if ko_val else ""
            return out

        out: dict[str, Any] = {}
        zh_dict = zh_node if isinstance(zh_node, dict) else {}
        for key, ko_val in ko_node.items():
            # Skip bulky shared menu/photo arrays under restaurants — already migrated
            if key in ("menuItems", "photos", "previewImage", "mapsEmbedUrl", "placeUrl", "mapsUrl"):
                out[key] = copy.deepcopy(ko_val)
                continue
            child_path = f"{path}.{key}" if path else key
            out[key] = walk_translate(
                ko_val,
                zh_dict.get(key),
                status=status,
                force=force,
                path=child_path,
            )
        for key, zh_val in zh_dict.items():
            if key not in out:
                out[key] = zh_val
        return out

    if isinstance(ko_node, list):
        zh_list = zh_node if isinstance(zh_node, list) else []
        return [
            walk_translate(
                ko_item,
                zh_list[i] if i < len(zh_list) else None,
                status=status,
                force=force,
                path=f"{path}[{i}]",
            )
            for i, ko_item in enumerate(ko_node)
        ]

    if isinstance(ko_node, str):
        zh_str = zh_node if isinstance(zh_node, str) else ""
        if force or not zh_str or zh_str == ko_node or _looks_korean(zh_str):
            return _translate_leaf(ko_node, status)
        return zh_str

    return copy.deepcopy(ko_node)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--skip-restaurants",
        action="store_true",
        default=True,
        help="Skip restaurants namespace (default: true)",
    )
    parser.add_argument(
        "--include-restaurants",
        action="store_true",
        help="Also translate restaurants scalar fields",
    )
    args = parser.parse_args()

    ko = i18n_store.load_lang("ko")
    zh_path = ROOT / "i18n" / "zh.json"
    if zh_path.is_file():
        zh = json.loads(zh_path.read_text(encoding="utf-8"))
    else:
        zh = copy.deepcopy(ko)

    status = BatchStatus()
    if args.all:
        tops = set(ko.keys())
    else:
        tops = (WALK_TOP & set(ko.keys())) | {k for k in CRITICAL_TOP if k in ko}
    if args.include_restaurants:
        tops.add("restaurants")
    elif args.skip_restaurants:
        tops.discard("restaurants")

    for top in sorted(tops):
        print(f"translating namespace: {top}", flush=True)
        zh[top] = walk_translate(
            ko[top], zh.get(top), status=status, force=bool(args.force), path=top
        )

    # Ensure restaurants exist (copy structure from KO, keep prior zh scalars)
    if "restaurants" in ko and "restaurants" not in zh:
        zh["restaurants"] = copy.deepcopy(ko["restaurants"])
    elif "restaurants" in ko:
        # Sync menuItems/photos from KO into zh restaurants
        for slug, entry in (ko.get("restaurants") or {}).items():
            if not isinstance(entry, dict):
                continue
            z = zh.setdefault("restaurants", {}).setdefault(slug, {})
            if not isinstance(z, dict):
                z = {}
                zh["restaurants"][slug] = z
            # Shared / structural fields from KO (previewTitle keeps Korean shop titles)
            for key in (
                "menuItems",
                "photos",
                "placeId",
                "placeUrl",
                "mapsUrl",
                "mapsEmbedUrl",
                "mapsProvider",
                "sourceType",
                "phone",
                "score",
                "previewImage",
                "previewTitle",
            ):
                if key in entry:
                    z[key] = copy.deepcopy(entry[key])
            # hours/category: translate static Korean status/labels when still Hangul
            for f in ("hours", "category"):
                ko_val = str(entry.get(f) or "")
                zh_val = str(z.get(f) or "")
                if ko_val and (
                    f not in z
                    or not zh_val.strip()
                    or zh_val == ko_val
                    or _looks_korean(zh_val)
                ):
                    z[f] = _translate_leaf(ko_val, status) if _looks_korean(ko_val) else ko_val
                elif f in entry and f not in z:
                    z[f] = copy.deepcopy(entry[f])
            for f in ("name", "location", "menu", "price", "tip", "about"):
                if f not in z or not str(z.get(f) or "").strip() or _looks_korean(str(z.get(f) or "")):
                    ko_val = str(entry.get(f) or "")
                    if ko_val and _looks_korean(ko_val):
                        z[f] = _translate_leaf(ko_val, status)
                    else:
                        z[f] = ko_val or z.get(f) or ""

    for top, val in ko.items():
        if top not in zh:
            zh[top] = copy.deepcopy(val)

    i18n_store.save_lang("zh", zh)
    print(i18n_store.build_bundle(), flush=True)
    for line in status.note_lines():
        print(line, flush=True)
    summary = bump_asset_version()
    print(f"cache -> {summary['version']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
