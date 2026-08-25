# -*- coding: utf-8 -*-
"""Resume list2: write foods JSON only, scaffold missing shops, enrich, one bundle."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

JOBS_DIR = Path(__file__).resolve().parent
TOOL_DIR = JOBS_DIR.parent
ROOT = TOOL_DIR.parent
sys.path.insert(0, str(TOOL_DIR))
sys.path.insert(0, str(JOBS_DIR))

from add_food_batch_aug26_list2 import (  # noqa: E402
    COVER_SIZE,
    NEW_DISHES,
    SHOPS,
    _resize_jpeg,
    copy_dish_covers,
)
from lib.content import _write_text_retry  # noqa: E402
from lib.images import shop_media_dir  # noqa: E402
from lib.place_scrape import naver_canonical_place_url, resolve_naver_search  # noqa: E402
from lib.scaffold import (  # noqa: E402
    dish_dir,
    insert_before_card_grid_close,
    render_shop_page,
    shop_card_html,
    shop_page_path,
    sync_shop_page_visual,
)
from migrate_shop_enrich import apply_to_bundle, enrich_one  # noqa: E402

FOODS_DIR = ROOT / "i18n" / "pages" / "foods"
LANGS = ("ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru")

KNOWN_IDS = {
    "seumugogae-haeundae": "1390003666",
    "hongojip-myeongdong": "1873302607",
    "cheongwadae-sogeumgui": "2080937308",
    "manmanjeong-seomyeon": "1038172900",
    "gayang-kalguksu": "11624237",
    "byeolyangjip": "19872940",
    "dongdong-gomguk": "1752138250",
}


def load_foods() -> dict[str, dict]:
    out = {}
    for lang in LANGS:
        path = FOODS_DIR / f"{lang}.json"
        out[lang] = json.loads(path.read_text(encoding="utf-8"))
    return out


def save_foods(foods: dict[str, dict]) -> None:
    for lang in LANGS:
        path = FOODS_DIR / f"{lang}.json"
        _write_text_retry(
            path,
            json.dumps(foods[lang], ensure_ascii=False, indent=2) + "\n",
        )
        print(f"saved foods/{lang}.json", flush=True)


def ensure_dish_i18n(foods: dict) -> None:
    for d in NEW_DISHES:
        slug = d["slug"]
        ko = d["texts"]["ko"]
        en = d["texts"].get("en") or ko
        for lang in LANGS:
            dishes = foods[lang].setdefault("dishes", {})
            if slug in dishes and dishes[slug].get("title"):
                continue
            src = ko if lang == "ko" else (en if lang == "en" else ko)
            if lang == "ja":
                src = en
            dishes[slug] = {
                "title": src.get("title") or ko["title"],
                "desc": src.get("desc") or ko["desc"],
                "about": src.get("about") or ko["about"],
            }
        print(f"dish i18n {slug}", flush=True)


def stub_entry(shop: dict) -> dict:
    pid = str(shop.get("place_id") or "").strip()
    url = naver_canonical_place_url(pid) if pid else ""
    return {
        "name": shop["name"],
        "location": shop["name"],
        "menu": shop["name"],
        "price": "",
        "tip": "",
        "about": shop["name"],
        "placeUrl": url,
        "mapsUrl": url,
        "mapsEmbedUrl": "",
        "mapsProvider": "naver",
        "sourceType": "naver",
        "previewImage": "media/cover.jpg",
        "phone": "",
        "hours": "",
        "body": [],
        "placeId": pid,
        "previewTitle": shop["name"],
    }


def ensure_shop_page(shop: dict) -> str:
    page = shop_page_path(shop["kind"], shop["dish"], shop["slug"])
    if page.is_file():
        return f"[page ok] {shop['slug']}"
    parent = dish_dir(shop["kind"], shop["dish"])
    if not (parent / "index.html").is_file():
        return f"[FAIL] no dish page for {shop['dish']}"
    page.parent.mkdir(parents=True, exist_ok=True)
    shop_media_dir(shop["kind"], shop["dish"], shop["slug"]).mkdir(parents=True, exist_ok=True)
    _write_text_retry(page, render_shop_page(shop["kind"], shop["dish"], shop["slug"]))
    index = parent / "index.html"
    html = index.read_text(encoding="utf-8")
    if f"./{shop['slug']}/index.html" not in html:
        html = insert_before_card_grid_close(
            html,
            shop_card_html(
                shop["kind"], shop["dish"], shop["slug"], region_group="sudo"
            ),
        )
        _write_text_retry(index, html)
    return f"[page created] {shop['slug']}"


def resolve_ids() -> None:
    for shop in SHOPS:
        slug = shop["slug"]
        if shop.get("place_id"):
            continue
        if slug in KNOWN_IDS:
            shop["place_id"] = KNOWN_IDS[slug]
            print(f"known id {slug}={shop['place_id']}", flush=True)
            continue
        if shop.get("search"):
            hit = resolve_naver_search(str(shop["search"]), force=True)
            pid = str(hit.get("placeId") or "").strip()
            shop["place_id"] = pid
            print(
                f"resolved {shop['search']!r} → {pid} {hit.get('name')!r}",
                flush=True,
            )
            time.sleep(0.4)


def main() -> int:
    print("=== resolve ids ===", flush=True)
    resolve_ids()

    print("=== load foods json ===", flush=True)
    foods = load_foods()
    existing_ids = {}
    for slug, entry in (foods["ko"].get("restaurants") or {}).items():
        if isinstance(entry, dict) and entry.get("placeId"):
            existing_ids[str(entry["placeId"])] = slug

    ensure_dish_i18n(foods)

    targets = []
    for shop in SHOPS:
        pid = str(shop.get("place_id") or "").strip()
        if not pid:
            print(f"[FAIL] {shop['slug']}: no place id", flush=True)
            continue
        other = existing_ids.get(pid)
        if other and other != shop["slug"]:
            print(f"[skip dup] {shop['slug']} == {other} ({pid})", flush=True)
            continue
        shop["place_url"] = naver_canonical_place_url(pid)
        print(ensure_shop_page(shop), flush=True)
        for lang in LANGS:
            restaurants = foods[lang].setdefault("restaurants", {})
            if shop["slug"] not in restaurants:
                restaurants[shop["slug"]] = stub_entry(shop)
            else:
                restaurants[shop["slug"]].setdefault("placeId", pid)
                restaurants[shop["slug"]].setdefault("name", shop["name"])
        existing_ids[pid] = shop["slug"]
        targets.append(shop)

    print("=== save i18n stubs ===", flush=True)
    save_foods(foods)

    print(f"=== enrich ({len(targets)}) ===", flush=True)
    for i, shop in enumerate(targets):
        slug = shop["slug"]
        pid = shop["place_id"]
        entry = foods["ko"]["restaurants"].get(slug) or stub_entry(shop)
        entry["placeUrl"] = naver_canonical_place_url(pid)
        entry["placeId"] = pid
        entry["sourceType"] = "naver"
        print(f"[enrich] {slug} {pid}", flush=True)
        try:
            updated, enotes, st = enrich_one(slug, entry, force=True)
            apply_to_bundle(foods, slug, updated)
            foods["ko"]["restaurants"][slug] = updated
            print(f"  {st}", flush=True)
            for n in enotes[:6]:
                print(" ", n, flush=True)
            for n in sync_shop_page_visual(shop["kind"], shop["dish"], slug):
                print("  html:", n, flush=True)
            print(" ", _resize_jpeg(
                ROOT / "pages" / "foods" / shop["kind"] / shop["dish"] / slug / "media" / "cover.jpg"
            ), flush=True)
        except Exception as exc:  # noqa: BLE001
            print(f"[enrich fail] {slug}: {exc}", flush=True)
        if i % 5 == 4:
            save_foods(foods)
            print("  checkpoint", flush=True)
        if i + 1 < len(targets):
            time.sleep(0.6)

    print("=== dish covers ===", flush=True)
    for n in copy_dish_covers(targets):
        print(n, flush=True)

    print("=== save foods ===", flush=True)
    save_foods(foods)

    print("=== build-bundle ===", flush=True)
    subprocess.check_call(
        [sys.executable, str(ROOT / "i18n" / "build-bundle.py")],
        cwd=str(ROOT),
    )
    from lib import content
    from lib.cache_bust import bump_asset_version

    try:
        print(content.rebuild_food_recommend_catalog(), flush=True)
    except OSError as exc:
        print("catalog deferred", exc, flush=True)
    try:
        print(bump_asset_version(), flush=True)
    except OSError as exc:
        print("bump deferred", exc, flush=True)
    print(f"done targets={len(targets)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
