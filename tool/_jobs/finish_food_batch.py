# -*- coding: utf-8 -*-
"""Finish remaining steps after interrupted batch_food_shops_galbijjim.py."""
from __future__ import annotations

import sys
import time
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from batch_food_shops_galbijjim import (  # noqa: E402
    SHOPS,
    clean_about_text,
    clean_all_shop_abouts,
    default_intro,
    fix_doenjang_cover,
    fix_seogil_cover,
    localize_scalars,
    translate_shop_abouts,
    _resize_jpeg,
)
from lib import content, i18n_store  # noqa: E402
from lib.cache_bust import bump_asset_version  # noqa: E402
from lib.images import shop_photo_path  # noqa: E402
from lib.place_scrape import naver_canonical_place_url  # noqa: E402
from lib.scaffold import sync_shop_page_visual  # noqa: E402
from lib.translate import BatchStatus  # noqa: E402
from migrate_menu_i18n import migrate_menu_items  # noqa: E402
from migrate_shop_enrich import apply_to_bundle, enrich_one  # noqa: E402


def ensure_editorial_abouts(bundle: dict) -> list[str]:
    notes: list[str] = []
    ko = bundle["ko"].setdefault("restaurants", {})
    need_tr: list[str] = []
    for shop in SHOPS:
        slug = shop["slug"]
        entry = ko.get(slug)
        if not entry:
            notes.append(f"MISSING restaurant entry: {slug}")
            continue
        editorial = str(shop.get("about") or "").strip()
        about = str(entry.get("about") or "")
        cleaned = clean_about_text(about)
        if editorial and (
            not cleaned
            or "평점" in about
            or "편의:" in about
            or about.strip() != editorial
            and ("방문자" in about or len(about) < 20)
        ):
            # Prefer hand-written editorial for new shops
            if not cleaned or "평점" in about or "편의:" in about:
                entry["about"] = editorial
                need_tr.append(slug)
                notes.append(f"set editorial about: {slug}")
            elif cleaned and cleaned != about:
                entry["about"] = cleaned
                need_tr.append(slug)
                notes.append(f"cleaned about: {slug}")
        elif not cleaned:
            entry["about"] = editorial or default_intro(
                str(entry.get("name") or slug),
                shop["dish"],
                str(entry.get("menu") or shop.get("menu_hint") or ""),
                str(entry.get("category") or ""),
            )
            need_tr.append(slug)
            notes.append(f"filled empty about: {slug}")
        # place id
        pid = str(shop.get("place_id") or entry.get("placeId") or "").strip()
        if not pid and shop.get("search"):
            from lib.place_scrape import resolve_naver_search

            hit = resolve_naver_search(str(shop["search"]), force=True)
            pid = str(hit.get("placeId") or "").strip()
            shop["place_id"] = pid
            notes.append(f"resolved {shop['search']} → {pid}")
        if pid:
            for lang in i18n_store.LANGS:
                e = bundle[lang].setdefault("restaurants", {}).setdefault(slug, {})
                e["placeId"] = pid
                e["placeUrl"] = naver_canonical_place_url(pid)
                e["mapsUrl"] = e["placeUrl"]
                e["sourceType"] = "naver"
    return notes, need_tr


def enrich_missing(bundle: dict) -> list[str]:
    notes: list[str] = []
    ko = bundle["ko"].setdefault("restaurants", {})
    for shop in SHOPS:
        slug = shop["slug"]
        entry = ko.get(slug) or {}
        needs = not entry.get("menuItems") or not shop_photo_path(
            shop["kind"], shop["dish"], slug
        ).is_file()
        if not needs:
            continue
        pid = str(shop.get("place_id") or entry.get("placeId") or "").strip()
        if not pid:
            notes.append(f"skip enrich no pid: {slug}")
            continue
        place_url = naver_canonical_place_url(pid)
        entry = dict(entry)
        entry["placeId"] = pid
        entry["placeUrl"] = place_url
        entry["sourceType"] = "naver"
        editorial = str(shop.get("about") or entry.get("about") or "")
        print(f"[enrich missing] {slug}…")
        updated, enotes, st = enrich_one(slug, entry, force=True)
        if editorial:
            updated["about"] = editorial
        apply_to_bundle(bundle, slug, updated)
        ko[slug] = updated
        notes.append(f"enriched {slug} status={st}")
        for n in enotes[:4]:
            notes.append(f"  {n}")
        for n in sync_shop_page_visual(shop["kind"], shop["dish"], slug):
            notes.append(f"  html: {n}")
        notes.append(_resize_jpeg(shop_photo_path(shop["kind"], shop["dish"], slug)))
        time.sleep(0.6)
    return notes


def main() -> int:
    print("=== ensure place ids + editorial abouts ===")
    bundle = i18n_store.load_all()
    notes, need_tr = ensure_editorial_abouts(bundle)
    for n in notes:
        print(" ", n)

    print("=== enrich any missing media/menus ===")
    for n in enrich_missing(bundle):
        print(" ", n)

    print("=== clean remaining junk abouts ===")
    clean_notes, cleaned = clean_all_shop_abouts(bundle)
    for n in clean_notes:
        print(" ", n)

    translate_slugs = sorted(set(need_tr + cleaned + [s["slug"] for s in SHOPS]))
    # Only translate if EN about still looks Korean/junk or empty
    final_tr: list[str] = []
    for slug in translate_slugs:
        ko_about = str(
            (bundle["ko"].get("restaurants") or {}).get(slug, {}).get("about") or ""
        )
        en_about = str(
            (bundle["en"].get("restaurants") or {}).get(slug, {}).get("about") or ""
        )
        if not ko_about:
            continue
        if (
            not en_about
            or en_about == ko_about
            or "평점" in en_about
            or "편의:" in en_about
            or "방문자" in en_about
        ):
            final_tr.append(slug)
    print(f"=== translate abouts needing refresh ({len(final_tr)}) ===")
    if final_tr:
        st = translate_shop_abouts(bundle, final_tr)
        for n in st.note_lines():
            print(" ", n)

    print("=== localize new shop scalars (force about/name/menu) ===")
    st2 = localize_scalars(bundle, SHOPS)
    for n in st2.note_lines():
        print(" ", n)

    print("=== menu i18n for new shops ===")
    menu_st = BatchStatus()
    for shop in SHOPS:
        slug = shop["slug"]
        entry = bundle["ko"].setdefault("restaurants", {}).get(slug) or {}
        items = list(entry.get("menuItems") or [])
        if not items:
            print(f"[menu-i18n skip] {slug}")
            continue
        # Skip if already multilingual
        first = items[0].get("name") if items else None
        if isinstance(first, dict) and first.get("en") and first.get("ja"):
            print(f"[menu-i18n already] {slug}: {len(items)}")
            continue
        migrated = migrate_menu_items(items, menu_st)
        entry["menuItems"] = migrated
        sig = next((m for m in migrated if m.get("recommend")), migrated[0])
        sig_name = sig.get("name") if isinstance(sig.get("name"), dict) else {}
        if isinstance(sig_name, dict) and sig_name.get("ko"):
            entry["menu"] = sig_name["ko"]
        for lang in i18n_store.LANGS:
            restaurants_lang = bundle[lang].setdefault("restaurants", {})
            other = dict(restaurants_lang.get(slug) or {})
            other["menuItems"] = migrated
            if lang != "ko" and isinstance(sig_name, dict) and sig_name.get(lang):
                other["menu"] = sig_name[lang]
            elif lang == "ko" and isinstance(sig_name, dict):
                other["menu"] = sig_name.get("ko") or other.get("menu") or ""
            restaurants_lang[slug] = other
        print(f"[menu-i18n] {slug}: {len(migrated)} items")

    for attempt in range(3):
        try:
            i18n_store.save_all(bundle)
            break
        except OSError as exc:
            print(f"save retry {attempt+1}: {exc}")
            time.sleep(2)

    print("=== fix covers ===")
    for n in fix_doenjang_cover():
        print(" ", n)
    for n in fix_seogil_cover():
        print(" ", n)

    bundle = i18n_store.load_all()
    se = bundle["ko"].setdefault("restaurants", {}).setdefault("seogil-sikdang", {})
    if "평점" in str(se.get("about") or "") or not clean_about_text(
        str(se.get("about") or "")
    ):
        se["about"] = (
            "평택의 간장게장·해물 요리 맛집입니다. "
            "국내산 게로 담근 간장게장과 쭈꾸미 볶음이 대표 메뉴입니다."
        )
        translate_shop_abouts(bundle, ["seogil-sikdang"])
        i18n_store.save_all(bundle)

    print(i18n_store.build_bundle())
    print(content.rebuild_food_recommend_catalog())
    summary = bump_asset_version()
    print(f"cache → {summary['version']}")

    print("\n=== SUMMARY ===")
    for shop in SHOPS:
        slug = shop["slug"]
        entry = (bundle["ko"].get("restaurants") or {}).get(slug) or {}
        print(
            f"{slug}: placeId={entry.get('placeId') or shop.get('place_id')} "
            f"about={str(entry.get('about') or '')[:40]!r} "
            f"menus={len(entry.get('menuItems') or [])}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
