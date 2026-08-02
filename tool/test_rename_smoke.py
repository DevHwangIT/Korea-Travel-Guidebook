# -*- coding: utf-8 -*-
"""Disposable create → rename → delete smoke test for dish/shop rename.

Does not touch real published slugs. Run:
  python tool/test_rename_smoke.py
"""
from __future__ import annotations

import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from lib import content, i18n_store  # noqa: E402
from lib.images import (  # noqa: E402
    append_menu_uploads,
    discover_menu_images,
    dish_cover_path,
    shop_menu_numbered_path,
    shop_photo_path,
)
from lib.scaffold import dish_index_path, shop_page_path  # noqa: E402


DISH_A = "zz-admin-smoke-dish"
DISH_B = "zz-admin-smoke-dish-renamed"
SHOP_A = "zz-admin-smoke-shop"
SHOP_B = "zz-admin-smoke-shop-renamed"


def _tiny_jpeg() -> bytes:
    # Minimal valid 1x1 JPEG
    return bytes.fromhex(
        "ffd8ffe000104a46494600010100000100010000ffdb004300080606070605080707"
        "070909080a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c20242e2720222c231c"
        "1c2837292c30313434341f27393d38323c2e333432ffdb0043010909090c0b0c180d"
        "0d1832211c2132323232323232323232323232323232323232323232323232323232"
        "323232323232323232323232323232323232323232ffc00011080001000103012200"
        "021101031101ffc4001500010100000000000000000000000000000008ffc4001410"
        "01000000000000000000000000000000ffda000c0301000210031000003f00bf80ffd9"
    )


def cleanup() -> None:
    from lib.paths import IMAGES_DISHES, IMAGES_RESTAURANTS, MEALS_DIR

    for slug in (SHOP_B, SHOP_A):
        try:
            content.delete_shop(slug, delete_images=True)
        except Exception:  # noqa: BLE001
            pass
    for dish in (DISH_B, DISH_A):
        try:
            content.delete_dish("meals", dish, delete_images=True)
        except Exception:  # noqa: BLE001
            pass
        # Hard cleanup leftovers from interrupted runs
        for p in (
            MEALS_DIR / dish,
            IMAGES_RESTAURANTS / dish,
            IMAGES_DISHES / f"{dish}.jpg",
        ):
            if p.is_file():
                p.unlink()
            elif p.is_dir():
                import shutil

                shutil.rmtree(p, ignore_errors=True)


def main() -> int:
    print("cleanup previous leftovers…")
    cleanup()
    jpeg = _tiny_jpeg()
    notes: list[str] = []

    print("1) create dish")
    notes.extend(
        content.create_dish(
            "meals",
            DISH_A,
            {
                "ko": {"title": "스모크음식", "desc": "d", "about": "a"},
                "en": {"title": "Smoke", "desc": "d", "about": "a"},
                "ja": {"title": "スモーク", "desc": "d", "about": "a"},
            },
            "🧪",
        )
    )
    dish_cover_path(DISH_A).write_bytes(jpeg)

    print("2) create shop + 2 menu images")
    notes.extend(
        content.create_shop(
            "meals",
            DISH_A,
            SHOP_A,
            {
                "ko": {
                    "name": "스모크가게",
                    "location": "서울 테스트",
                    "menu": "김밥",
                    "price": "1원",
                    "tip": "팁",
                    "about": "소개",
                },
                "en": {
                    "name": "Smoke Shop",
                    "location": "Seoul",
                    "menu": "Kimbap",
                    "price": "1",
                    "tip": "tip",
                    "about": "about",
                },
                "ja": {
                    "name": "スモーク店",
                    "location": "ソウル",
                    "menu": "キンパ",
                    "price": "1",
                    "tip": "tip",
                    "about": "about",
                },
            },
        )
    )
    shop_photo_path("meals", DISH_A, SHOP_A).write_bytes(jpeg)
    notes.extend(
        append_menu_uploads(
            "meals",
            DISH_A,
            SHOP_A,
            [("a.jpg", jpeg), ("b.jpg", jpeg)],
        )
    )
    menus = discover_menu_images("meals", DISH_A, SHOP_A)
    assert len(menus) == 2, menus
    assert menus[0].path.name == f"{SHOP_A}-menu-1.jpg"
    assert menus[1].path.name == f"{SHOP_A}-menu-2.jpg"

    bundle = i18n_store.load_all()
    maps_before = (bundle["ko"]["restaurants"][SHOP_A]).get("mapsUrl")

    print("3) rename shop")
    notes.extend(content.rename_shop(SHOP_A, SHOP_B))
    assert not shop_page_path("meals", DISH_A, SHOP_A).exists()
    assert shop_page_path("meals", DISH_A, SHOP_B).is_file()
    html = shop_page_path("meals", DISH_A, SHOP_B).read_text(encoding="utf-8")
    assert f"restaurants.{SHOP_B}." in html
    assert f"restaurants.{SHOP_A}." not in html
    assert f"{SHOP_B}-menu-1.jpg" in html
    assert f"{SHOP_B}-menu-2.jpg" in html
    assert shop_photo_path("meals", DISH_A, SHOP_B).is_file()
    assert shop_menu_numbered_path("meals", DISH_A, SHOP_B, 1).is_file()
    assert shop_menu_numbered_path("meals", DISH_A, SHOP_B, 2).is_file()
    bundle = i18n_store.load_all()
    assert SHOP_A not in bundle["ko"]["restaurants"]
    assert SHOP_B in bundle["ko"]["restaurants"]
    assert bundle["en"]["restaurants"][SHOP_B]["name"]
    assert bundle["ja"]["restaurants"][SHOP_B]["name"]
    maps_after = bundle["ko"]["restaurants"][SHOP_B].get("mapsUrl")
    assert maps_after == maps_before, (maps_before, maps_after)
    idx = dish_index_path("meals", DISH_A).read_text(encoding="utf-8")
    assert f"./{SHOP_B}.html" in idx
    assert f"./{SHOP_A}.html" not in idx

    print("4) rename dish (moves restaurant image folder)")
    notes.extend(content.rename_dish("meals", DISH_A, DISH_B))
    assert dish_index_path("meals", DISH_B).is_file()
    assert not dish_index_path("meals", DISH_A).exists()
    assert shop_page_path("meals", DISH_B, SHOP_B).is_file()
    shop_html = shop_page_path("meals", DISH_B, SHOP_B).read_text(encoding="utf-8")
    assert f"dishes.{DISH_B}." in shop_html
    assert f"/restaurants/{DISH_B}/" in shop_html
    assert shop_photo_path("meals", DISH_B, SHOP_B).is_file()
    assert len(discover_menu_images("meals", DISH_B, SHOP_B)) == 2
    hub = (TOOL_DIR.parent / "pages" / "foods" / "meals" / "index.html").read_text(
        encoding="utf-8"
    )
    assert f"./{DISH_B}/" in hub
    assert f"./{DISH_A}/" not in hub

    print("5) cleanup delete")
    notes.extend(content.delete_shop(SHOP_B, delete_images=True))
    notes.extend(content.delete_dish("meals", DISH_B, delete_images=True))
    assert not dish_index_path("meals", DISH_B).exists()

    print("OK - rename smoke passed")
    print("--- notes ---")
    for line in notes[-12:]:
        print(line)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: {exc}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        print("attempting cleanup…", file=sys.stderr)
        try:
            cleanup()
        except Exception:  # noqa: BLE001
            pass
        raise SystemExit(1)
