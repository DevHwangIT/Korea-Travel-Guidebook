# -*- coding: utf-8 -*-
"""Migrate page-owned images into each page's media/ folder.

- Shop HTML: pages/.../{shop}.html → pages/.../{shop}/index.html + media/
- Dish covers: Images/foods/dishes/{slug}.jpg → pages/foods/{kind}/{slug}/media/cover.jpg
- Shop photos/menus: Images/foods/restaurants|brands → shop media/cover.jpg + body-N.jpg
- Souvenir / convenience heroes → detail page media/cover.jpg
- Update HTML img src, parent cards, i18n body image src
- Rebuild i18n/messages.js

Shared Images/menu, Images/cover, Images/transport, Images/foods/hub stay put.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tool"
if str(TOOL) not in sys.path:
    sys.path.insert(0, str(TOOL))

from lib.images import (  # noqa: E402
    dish_cover_path,
    legacy_dish_cover_path,
    legacy_shop_photo_path,
    rel_posix,
    shop_body_numbered_path,
    shop_media_dir,
    shop_photo_path,
)
from lib.paths import DESSERTS_DIR, IMAGES_RESTAURANTS, MEALS_DIR, ROOT as LIB_ROOT  # noqa: E402
from lib.scaffold import shop_page_path  # noqa: E402
from lib import i18n_store  # noqa: E402

assert LIB_ROOT == ROOT

NOTES: list[str] = []


def note(msg: str) -> None:
    NOTES.append(msg)
    print(msg)


def move_file(src: Path, dst: Path, *, copy: bool = False) -> bool:
    if not src.is_file():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        if src.resolve() == dst.resolve():
            return False
        if copy:
            return False
        src.unlink()
        note(f"  skip (exists): {rel_posix(dst)}")
        return False
    if copy:
        shutil.copy2(src, dst)
        note(f"  copy: {rel_posix(src)} → {rel_posix(dst)}")
    else:
        shutil.move(str(src), str(dst))
        note(f"  move: {rel_posix(src)} → {rel_posix(dst)}")
    return True


def rewrite_shop_html_for_folder(html: str, *, deeper: bool) -> str:
    """Adjust asset prefix and local image/back links for shop/index.html."""
    text = html
    if deeper:
        # ../../../../ → ../../../../../ for root assets
        text = re.sub(
            r'(href|src)="(\.\./){4}([^"]*)"',
            r'\1="../../../../../\3"',
            text,
        )
        text = text.replace('href="./index.html"', 'href="../index.html"')
    # Shop photo → page-local media/cover.jpg
    text = re.sub(
        r'(<img[^>]*class="shop-photo"[^>]*src=")[^"]+(")',
        r'\1media/cover.jpg\2',
        text,
        count=1,
        flags=re.IGNORECASE,
    )
    # Also bare shop-photo without relying on class order
    text = re.sub(
        r'src="(?:\.\./)+Images/foods/(?:restaurants|brands)/[^"]+\.jpg"',
        'src="media/cover.jpg"',
        text,
        count=1,
    )
    return text


def migrate_shop(
    kind: str, dish_slug: str, shop_slug: str, flat_page: Path
) -> None:
    dest_page = shop_page_path(kind, dish_slug, shop_slug)
    media = shop_media_dir(kind, dish_slug, shop_slug)
    media.mkdir(parents=True, exist_ok=True)

    html = flat_page.read_text(encoding="utf-8")
    html = rewrite_shop_html_for_folder(html, deeper=True)
    dest_page.parent.mkdir(parents=True, exist_ok=True)
    dest_page.write_text(html, encoding="utf-8", newline="\n")
    flat_page.unlink()
    note(f"shop page: {flat_page.relative_to(ROOT).as_posix()} → {dest_page.relative_to(ROOT).as_posix()}")

    # Cover
    legacy_photo = legacy_shop_photo_path(kind, dish_slug, shop_slug)
    move_file(legacy_photo, shop_photo_path(kind, dish_slug, shop_slug))

    # Body / menu images from restaurants folder
    legacy_dirs = []
    if kind == "meals":
        legacy_dirs.append(IMAGES_RESTAURANTS / dish_slug)
    else:
        legacy_dirs.append(IMAGES_RESTAURANTS / "desserts")
        legacy_dirs.append(legacy_photo.parent)

    body_idx = 1
    for folder in legacy_dirs:
        if not folder.is_dir():
            continue
        candidates: list[Path] = []
        for p in sorted(folder.iterdir()):
            if not p.is_file() or p.suffix.lower() != ".jpg":
                continue
            name = p.name.lower()
            if name == f"{shop_slug}.jpg".lower():
                continue  # cover handled
            if name.startswith(f"{shop_slug.lower()}-menu") or name.startswith(
                f"{shop_slug.lower()}-body"
            ):
                candidates.append(p)
        for p in candidates:
            dest = shop_body_numbered_path(kind, dish_slug, shop_slug, body_idx)
            if move_file(p, dest):
                body_idx += 1


def migrate_all_shops() -> None:
    note("=== shops ===")
    for kind, base in (("meals", MEALS_DIR), ("desserts", DESSERTS_DIR)):
        if not base.is_dir():
            continue
        for dish_dir_path in sorted(base.iterdir()):
            if not dish_dir_path.is_dir():
                continue
            for page in sorted(dish_dir_path.glob("*.html")):
                if page.name == "index.html":
                    continue
                migrate_shop(kind, dish_dir_path.name, page.stem, page)


def patch_dish_index_shop_cards(kind: str, dish_slug: str) -> None:
    index = (MEALS_DIR if kind == "meals" else DESSERTS_DIR) / dish_slug / "index.html"
    if not index.is_file():
        return
    html = index.read_text(encoding="utf-8")
    original = html
    # ./oto.html → ./oto/index.html
    html = re.sub(
        r'href="\./([a-z0-9-]+)\.html"',
        r'href="./\1/index.html"',
        html,
    )
    # Restaurant / brand thumbs → ./slug/media/cover.jpg
    # Prefer shop photo over *-menu.jpg (menu stems would invent fake ./slug-menu/ paths).
    html = re.sub(
        r'src="(?:\.\./)+Images/foods/restaurants/[^"]+/([a-z0-9-]+)-menu\.jpg"',
        r'src="./\1/media/cover.jpg"',
        html,
    )
    html = re.sub(
        r'src="(?:\.\./)+Images/foods/restaurants/[^"]+/([a-z0-9-]+)\.jpg"',
        r'src="./\1/media/cover.jpg"',
        html,
    )
    html = re.sub(
        r'src="(?:\.\./)+Images/foods/brands/([a-z0-9-]+)\.jpg"',
        r'src="./\1/media/cover.jpg"',
        html,
    )
    # Dish cover on dish index
    html = re.sub(
        r'src="(?:\.\./)+Images/foods/dishes/' + re.escape(dish_slug) + r'\.jpg"',
        'src="media/cover.jpg"',
        html,
        count=1,
    )
    if html != original:
        index.write_text(html, encoding="utf-8", newline="\n")
        note(f"patched dish index: {index.relative_to(ROOT).as_posix()}")


def migrate_dish_covers() -> None:
    note("=== dish covers ===")
    for kind, base in (("meals", MEALS_DIR), ("desserts", DESSERTS_DIR)):
        if not base.is_dir():
            continue
        for dish_dir_path in sorted(base.iterdir()):
            if not dish_dir_path.is_dir():
                continue
            if not (dish_dir_path / "index.html").is_file():
                continue
            slug = dish_dir_path.name
            dest = dish_cover_path(slug, kind)
            src = legacy_dish_cover_path(slug)
            move_file(src, dest)
            patch_dish_index_shop_cards(kind, slug)


def patch_hub_indexes() -> None:
    note("=== hub indexes ===")
    for kind, base in (("meals", MEALS_DIR), ("desserts", DESSERTS_DIR)):
        hub = base / "index.html"
        if not hub.is_file():
            continue
        html = hub.read_text(encoding="utf-8")
        original = html
        html = re.sub(
            r'src="(?:\.\./)+Images/foods/dishes/([a-z0-9-]+)\.jpg"',
            r'src="./\1/media/cover.jpg"',
            html,
        )
        if html != original:
            hub.write_text(html, encoding="utf-8", newline="\n")
            note(f"patched hub: {hub.relative_to(ROOT).as_posix()}")


def migrate_souvenir() -> None:
    note("=== souvenir ===")
    base = ROOT / "pages" / "souvenir"
    images = ROOT / "Images" / "souvenir"
    if not base.is_dir():
        return
    # Index thumbs
    index = base / "index.html"
    if index.is_file():
        html = index.read_text(encoding="utf-8")
        html2 = re.sub(
            r'src="(?:\.\./)+Images/souvenir/([a-z0-9-]+)\.jpg"',
            r'src="./\1/media/cover.jpg"',
            html,
        )
        if html2 != html:
            index.write_text(html2, encoding="utf-8", newline="\n")
            note("patched souvenir index")
    for child in sorted(base.iterdir()):
        if not child.is_dir():
            continue
        slug = child.name
        page = child / "index.html"
        media = child / "media"
        media.mkdir(parents=True, exist_ok=True)
        src = images / f"{slug}.jpg"
        move_file(src, media / "cover.jpg")
        if page.is_file():
            html = page.read_text(encoding="utf-8")
            html2 = re.sub(
                r'src="(?:\.\./)+Images/souvenir/[^"]+\.jpg"',
                'src="media/cover.jpg"',
                html,
                count=1,
            )
            if html2 != html:
                page.write_text(html2, encoding="utf-8", newline="\n")
                note(f"patched souvenir page: {slug}")


# convenience: page slug → preferred source filename(s) under Images/convenience
CONVENIENCE_COVERS: dict[str, list[str]] = {
    "biyott": ["biyott.jpg"],
    "gongganchun": ["combo-gongganchun.jpg"],
    "markjeongsik": ["combo-markjeongsik.jpg"],
    "carbonara": ["combo-carbonara-risotto.jpg"],
    "eolbaksa": ["combo-eolbaksa.jpg"],
    "jikgguri": ["combo-jikgguri.jpg"],
    "melona": ["combo-melona-coffee.jpg"],
    "melona-coffee": ["combo-melona-coffee.jpg"],
    "blue-lemonade-milkis": ["combo-blue-lemonade-milkis.jpg"],
    "choco-banana-latte": ["combo-choco-banana-latte.jpg"],
    "banana-americano": ["combo-banana-coffee.jpg"],
    "banana-coffee": ["combo-banana-coffee.jpg"],
    "kimbap-milk": ["combo-kimbap-milk.jpg"],
    "ramyeon-egg": ["combo-ramyeon-egg.jpg"],
    "yakgwa-coffee": ["combo-yakgwa-coffee.jpg"],
    "chicken-beer": ["combo-chicken-beer.jpg"],
}


def migrate_convenience() -> None:
    note("=== convenience ===")
    base = ROOT / "pages" / "convenience-store"
    images = ROOT / "Images" / "convenience"
    if not base.is_dir():
        return
    # Track which source files are shared so we copy instead of move
    src_users: dict[str, list[str]] = {}
    for slug, names in CONVENIENCE_COVERS.items():
        for name in names:
            src_users.setdefault(name, []).append(slug)

    index = base / "index.html"
    if index.is_file():
        html = index.read_text(encoding="utf-8")
        # Map known Images paths to page media
        replacements = {
            "biyott.jpg": "./biyott/media/cover.jpg",
            "combo-gongganchun.jpg": "./gongganchun/media/cover.jpg",
            "combo-markjeongsik.jpg": "./markjeongsik/media/cover.jpg",
            "combo-carbonara-risotto.jpg": "./carbonara/media/cover.jpg",
            "combo-eolbaksa.jpg": "./eolbaksa/media/cover.jpg",
            "combo-jikgguri.jpg": "./jikgguri/media/cover.jpg",
            "combo-melona-coffee.jpg": "./melona/media/cover.jpg",
            "combo-blue-lemonade-milkis.jpg": "./blue-lemonade-milkis/media/cover.jpg",
            "combo-choco-banana-latte.jpg": "./choco-banana-latte/media/cover.jpg",
            "combo-banana-coffee.jpg": "./banana-americano/media/cover.jpg",
            "combo-kimbap-milk.jpg": "./kimbap-milk/media/cover.jpg",
            "combo-ramyeon-egg.jpg": "./ramyeon-egg/media/cover.jpg",
            "combo-yakgwa-coffee.jpg": "./yakgwa-coffee/media/cover.jpg",
            "combo-chicken-beer.jpg": "./chicken-beer/media/cover.jpg",
        }
        html2 = html
        for fname, dest in replacements.items():
            html2 = re.sub(
                rf'src="(?:\.\./)+Images/convenience/{re.escape(fname)}"',
                f'src="{dest}"',
                html2,
            )
        if html2 != html:
            index.write_text(html2, encoding="utf-8", newline="\n")
            note("patched convenience index")

    for child in sorted(base.iterdir()):
        if not child.is_dir():
            continue
        slug = child.name
        page = child / "index.html"
        media = child / "media"
        media.mkdir(parents=True, exist_ok=True)
        names = CONVENIENCE_COVERS.get(slug, [f"{slug}.jpg", f"combo-{slug}.jpg"])
        moved = False
        for name in names:
            src = images / name
            if not src.is_file():
                continue
            shared = len(src_users.get(name, [])) > 1
            # First consumer moves; later ones copy if still present else already moved
            if shared and (media / "cover.jpg").exists():
                break
            if shared:
                # Prefer copy for shared assets; delete source after all copies
                move_file(src, media / "cover.jpg", copy=True)
            else:
                move_file(src, media / "cover.jpg")
            moved = True
            break
        if page.is_file():
            html = page.read_text(encoding="utf-8")
            html2 = re.sub(
                r'src="(?:\.\./)+Images/convenience/[^"]+\.jpg"',
                'src="media/cover.jpg"',
                html,
                count=1,
            )
            if html2 != html:
                page.write_text(html2, encoding="utf-8", newline="\n")
                note(f"patched convenience page: {slug}")

    # Remove shared sources that were only copied
    for name, slugs in src_users.items():
        if len(slugs) <= 1:
            continue
        src = images / name
        if src.is_file():
            # All targets should have cover now
            ok = all(
                (base / s / "media" / "cover.jpg").is_file() for s in slugs if (base / s).is_dir()
            )
            if ok:
                src.unlink()
                note(f"  removed shared source: Images/convenience/{name}")


def update_i18n_body_srcs() -> None:
    note("=== i18n body src ===")
    data = i18n_store.load_all()
    # Build map of legacy menu/body paths → new page media path
    mapping: dict[str, str] = {}

    for kind, base in (("meals", MEALS_DIR), ("desserts", DESSERTS_DIR)):
        if not base.is_dir():
            continue
        for dish_dir_path in sorted(base.iterdir()):
            if not dish_dir_path.is_dir():
                continue
            dish = dish_dir_path.name
            for child in sorted(dish_dir_path.iterdir()):
                if not child.is_dir():
                    continue
                shop = child.name
                media = child / "media"
                if not media.is_dir():
                    continue
                bodies = sorted(
                    p
                    for p in media.iterdir()
                    if p.is_file() and re.match(r"^body-\d+\.jpg$", p.name, re.I)
                )
                # Map common legacy names to body-1, body-2, …
                legacy_names = [
                    f"Images/foods/restaurants/{dish}/{shop}-menu.jpg",
                    f"Images/foods/restaurants/desserts/{shop}-menu.jpg",
                    f"Images/foods/restaurants/{dish}/{shop}-menu-1.jpg",
                    f"Images/foods/restaurants/desserts/{shop}-menu-1.jpg",
                ]
                if bodies:
                    mapping[legacy_names[0]] = rel_posix(bodies[0])
                    mapping[legacy_names[1]] = rel_posix(bodies[0])
                    mapping[legacy_names[2]] = rel_posix(bodies[0])
                    mapping[legacy_names[3]] = rel_posix(bodies[0])
                    # Also page-relative form
                    for i, b in enumerate(bodies, start=1):
                        mapping[
                            f"Images/foods/restaurants/{dish}/{shop}-body-{i}.jpg"
                        ] = rel_posix(b)
                        mapping[
                            f"Images/foods/restaurants/desserts/{shop}-body-{i}.jpg"
                        ] = rel_posix(b)

    changed = 0
    for lang in i18n_store.LANGS:
        restaurants = data[lang].get("restaurants") or {}
        for slug, entry in restaurants.items():
            if not isinstance(entry, dict):
                continue
            body = entry.get("body")
            if not isinstance(body, list):
                continue
            new_body = []
            for block in body:
                if not isinstance(block, dict):
                    new_body.append(block)
                    continue
                b = dict(block)
                if b.get("type") == "image":
                    src = str(b.get("src") or "").replace("\\", "/").lstrip("/")
                    if src in mapping:
                        b["src"] = mapping[src]
                        changed += 1
                    else:
                        # Heuristic: restaurants/.../{slug}-menu.jpg → find shop media
                        m = re.match(
                            r"Images/foods/restaurants/(?:[^/]+)/"
                            r"([a-z0-9-]+)-(?:menu|body)(?:-\d+)?\.jpg$",
                            src,
                            re.I,
                        )
                        if m:
                            shop = m.group(1)
                            # Prefer page-relative media/body-1.jpg when shop page exists
                            for kind, base in (
                                ("meals", MEALS_DIR),
                                ("desserts", DESSERTS_DIR),
                            ):
                                found = None
                                for dish_dir_path in base.iterdir() if base.is_dir() else []:
                                    media = dish_dir_path / shop / "media"
                                    body1 = media / "body-1.jpg"
                                    if body1.is_file():
                                        found = rel_posix(body1)
                                        break
                                if found:
                                    b["src"] = found
                                    changed += 1
                                    break
                new_body.append(b)
            entry["body"] = new_body

    i18n_store.save_all(data)
    note(f"i18n body src updates: {changed}")
    note(i18n_store.build_bundle())


def ensure_section_media_dirs() -> None:
    for rel in ("pages/before-trip/media", "pages/shopping/media"):
        p = ROOT / rel
        p.mkdir(parents=True, exist_ok=True)
        keep = p / ".gitkeep"
        if not keep.exists() and not any(p.iterdir()):
            keep.write_text("", encoding="utf-8")


def main() -> int:
    migrate_all_shops()
    migrate_dish_covers()
    patch_hub_indexes()
    migrate_souvenir()
    migrate_convenience()
    ensure_section_media_dirs()
    update_i18n_body_srcs()
    # Re-patch dish indexes in case shops migrated after covers
    for kind, base in (("meals", MEALS_DIR), ("desserts", DESSERTS_DIR)):
        if not base.is_dir():
            continue
        for dish_dir_path in sorted(base.iterdir()):
            if dish_dir_path.is_dir():
                patch_dish_index_shop_cards(kind, dish_dir_path.name)
    note("DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
