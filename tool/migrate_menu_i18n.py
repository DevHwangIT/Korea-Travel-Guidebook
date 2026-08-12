# -*- coding: utf-8 -*-
"""Migrate restaurant menuItems.name → multilingual {ko,en,ja,zh} and sync langs."""
from __future__ import annotations

import sys
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from pathlib import Path
from typing import Any

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from lib import i18n_store  # noqa: E402
from lib.cache_bust import bump_asset_version  # noqa: E402
from lib.translate import BatchStatus, TARGET_LANGS, translate_text  # noqa: E402

NAME_CACHE: dict[str, dict[str, str]] = {}


def _ko_name(item: dict[str, Any]) -> str:
    name = item.get("name")
    if isinstance(name, dict):
        return str(name.get("ko") or name.get("en") or "").strip()
    return str(name or item.get("nameKo") or "").strip()


def _translate_one(ko: str, lang: str) -> str:
    st = BatchStatus()
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            fut = pool.submit(translate_text, ko, lang, status=st)
            return fut.result(timeout=20) or ko
    except FuturesTimeout:
        return ko
    except Exception:  # noqa: BLE001
        return ko


def localize_name(ko: str, status: BatchStatus) -> dict[str, str]:
    if not ko:
        return {lang: "" for lang in ("ko",) + TARGET_LANGS}
    if ko in NAME_CACHE:
        status.reused += 1
        return dict(NAME_CACHE[ko])
    out = {"ko": ko}
    for lang in TARGET_LANGS:
        out[lang] = _translate_one(ko, lang)
        if out[lang] and out[lang] != ko:
            status.translated += 1
        else:
            status.copied += 1
        time.sleep(0.02)
    NAME_CACHE[ko] = dict(out)
    return out


def migrate_menu_items(
    items: list[Any], status: BatchStatus
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for raw in items:
        if not isinstance(raw, dict):
            continue
        item = dict(raw)
        ko = _ko_name(item)
        if not ko:
            continue
        name = item.get("name")
        if isinstance(name, dict) and name.get("ko") and all(
            str(name.get(lang) or "").strip() for lang in TARGET_LANGS
        ):
            item["name"] = {
                "ko": str(name["ko"]).strip(),
                **{lang: str(name[lang]).strip() for lang in TARGET_LANGS},
            }
            status.reused += 1
        else:
            item["name"] = localize_name(ko, status)
        item.pop("nameKo", None)
        item.pop("nameEn", None)
        item.pop("nameJa", None)
        item.pop("nameZh", None)
        out.append(item)
    return out


def main() -> int:
    bundle = i18n_store.load_all()
    ko_restaurants = bundle["ko"].setdefault("restaurants", {})
    status = BatchStatus()
    changed_shops = 0
    slugs = [
        s
        for s, e in sorted(ko_restaurants.items())
        if isinstance(e, dict)
        and isinstance(e.get("menuItems"), list)
        and e.get("menuItems")
    ]
    print(f"shops with menus: {len(slugs)}")

    for idx, slug in enumerate(slugs, start=1):
        entry = ko_restaurants[slug]
        items = entry.get("menuItems") or []
        print(f"[{idx}/{len(slugs)}] {slug} ({len(items)} items)…", flush=True)
        migrated = migrate_menu_items(list(items), status)
        if not migrated:
            continue
        entry["menuItems"] = migrated
        sig = next((m for m in migrated if m.get("recommend")), migrated[0])
        sig_name = sig.get("name") if isinstance(sig.get("name"), dict) else {}
        if isinstance(sig_name, dict) and sig_name.get("ko"):
            entry["menu"] = sig_name["ko"]

        for lang in i18n_store.LANGS:
            restaurants = bundle[lang].setdefault("restaurants", {})
            other = dict(restaurants.get(slug) or {})
            other["menuItems"] = migrated
            if lang != "ko" and isinstance(sig_name, dict) and sig_name.get(lang):
                other["menu"] = sig_name[lang]
            elif lang == "ko" and isinstance(sig_name, dict):
                other["menu"] = sig_name.get("ko") or other.get("menu") or ""
            restaurants[slug] = other
        changed_shops += 1

        # Checkpoint every 5 shops so progress is not lost
        if idx % 5 == 0:
            i18n_store.save_all(bundle)
            print(f"  checkpoint saved ({idx})", flush=True)

    i18n_store.save_all(bundle)
    print(i18n_store.build_bundle())
    for line in status.note_lines():
        print(line)
    summary = bump_asset_version()
    print(f"shops with menus: {changed_shops}")
    print(f"unique names cached: {len(NAME_CACHE)}")
    print(f"cache → {summary['version']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
