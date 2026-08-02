# -*- coding: utf-8 -*-
"""CRUD helpers for meal/dessert dishes and restaurant shops."""
from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import i18n_store
from .images import (
    dish_cover_path,
    rel_posix,
    shop_menu_path,
    shop_photo_path,
)
from .paths import (
    DESSERTS_DIR,
    MEALS_DIR,
    ROOT,
)
from .scaffold import (
    dish_card_html,
    dish_dir,
    dish_index_path,
    hub_index_path,
    insert_before_card_grid_close,
    maps_url_from_location,
    remove_card_referencing,
    render_dish_page,
    render_shop_page,
    shop_card_html,
    shop_page_path,
)

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# Known dish folders that are hubs (have index) under meals / desserts
MEAL_DISH_SLUGS_FALLBACK = {
    "kimbap",
    "naengmyeon",
    "jeon",
    "jajangmyeon",
    "dakhanmari",
    "samgyeopsal",
    "budae-jjigae",
    "dakgalbi",
    "samgyetang",
    "bibimbap",
    "ganjang-gejang",
    "yangnyeom-chicken",
    "sundubu-jjigae",
    "jjimdak",
    "malatang",
    "tteokbokki",
}

DESSERT_DISH_SLUGS_FALLBACK = {
    "bingsu",
    "bread",
    "cafe",
    "nangman-sandwich",
    "dubai-cookie",
    "butter-bread",
    "tanghulu",
    "yogurt-ice",
    "bungeoppang",
    "sulbing",
    "paris-baguette",
    "tous-les-jours",
}


@dataclass
class DishItem:
    kind: str  # meals | desserts
    slug: str
    title: str
    desc: str
    about: str
    page_exists: bool


@dataclass
class ShopItem:
    slug: str
    name: str
    dish_slug: str
    kind: str
    location: str
    page_path: str | None


def validate_slug(slug: str) -> str:
    slug = slug.strip().lower()
    if not SLUG_RE.match(slug):
        raise ValueError(
            "슬러그는 영문 소문자·숫자·하이픈만 가능합니다. 예: my-dish-name"
        )
    return slug


def list_dish_folders(kind: str) -> list[str]:
    base = MEALS_DIR if kind == "meals" else DESSERTS_DIR
    if not base.is_dir():
        return []
    slugs = []
    for p in sorted(base.iterdir()):
        if p.is_dir() and (p / "index.html").is_file():
            slugs.append(p.name)
    return slugs


def classify_dish_kind(slug: str) -> str | None:
    if slug in list_dish_folders("meals") or slug in MEAL_DISH_SLUGS_FALLBACK:
        if slug in list_dish_folders("meals"):
            return "meals"
    if slug in list_dish_folders("desserts") or slug in DESSERT_DISH_SLUGS_FALLBACK:
        if slug in list_dish_folders("desserts"):
            return "desserts"
    # Prefer folder existence
    if (MEALS_DIR / slug / "index.html").is_file():
        return "meals"
    if (DESSERTS_DIR / slug / "index.html").is_file():
        return "desserts"
    if slug in MEAL_DISH_SLUGS_FALLBACK:
        return "meals"
    if slug in DESSERT_DISH_SLUGS_FALLBACK:
        return "desserts"
    return None


def list_dishes(kind: str) -> list[DishItem]:
    ko = i18n_store.load_lang("ko")
    dishes = ko.get("dishes") or {}
    folder_slugs = set(list_dish_folders(kind))
    # Include i18n keys that clearly belong to this kind
    for slug in dishes:
        ck = classify_dish_kind(slug)
        if ck == kind:
            folder_slugs.add(slug)
    # Brand-only dessert keys that are also restaurants (sulbing etc.) may appear
    # as dishes in i18n but live under desserts as shop pages — still list if folder exists.
    items: list[DishItem] = []
    for slug in sorted(folder_slugs):
        d = dishes.get(slug) or {}
        items.append(
            DishItem(
                kind=kind,
                slug=slug,
                title=str(d.get("title") or slug),
                desc=str(d.get("desc") or ""),
                about=str(d.get("about") or ""),
                page_exists=dish_index_path(kind, slug).is_file(),
            )
        )
    return items


DISH_TEXT_FIELDS = ("title", "desc", "about")
SHOP_TEXT_FIELDS = ("name", "location", "menu", "price", "tip", "about")


def _empty_dish_texts() -> dict[str, dict[str, str]]:
    return {lang: {f: "" for f in DISH_TEXT_FIELDS} for lang in i18n_store.LANGS}


def _empty_shop_texts() -> dict[str, dict[str, str]]:
    return {lang: {f: "" for f in SHOP_TEXT_FIELDS} for lang in i18n_store.LANGS}


def normalize_dish_texts(
    texts: dict[str, dict[str, str]],
) -> tuple[dict[str, dict[str, str]], list[str]]:
    """Require KO title; fill blank EN/JA from KO. Returns (normalized, notes)."""
    notes: list[str] = []
    out = _empty_dish_texts()
    for lang in i18n_store.LANGS:
        src = texts.get(lang) or {}
        for f in DISH_TEXT_FIELDS:
            out[lang][f] = (src.get(f) or "").strip()
    if not out["ko"]["title"]:
        raise ValueError("한국어 이름(title)은 필수입니다.")
    if not out["ko"]["desc"]:
        out["ko"]["desc"] = out["ko"]["title"]
    if not out["ko"]["about"]:
        out["ko"]["about"] = out["ko"]["desc"]
    filled: list[str] = []
    for lang in ("en", "ja"):
        for f in DISH_TEXT_FIELDS:
            if not out[lang][f]:
                out[lang][f] = out["ko"][f]
                filled.append(f"{lang}.{f}")
    if filled:
        notes.append(
            "비어 있던 EN/JA 항목은 한국어와 동일하게 저장했습니다: "
            + ", ".join(filled)
        )
    return out, notes


def normalize_shop_texts(
    texts: dict[str, dict[str, str]],
) -> tuple[dict[str, dict[str, str]], list[str]]:
    notes: list[str] = []
    out = _empty_shop_texts()
    for lang in i18n_store.LANGS:
        src = texts.get(lang) or {}
        for f in SHOP_TEXT_FIELDS:
            out[lang][f] = (src.get(f) or "").strip()
    if not out["ko"]["name"]:
        raise ValueError("한국어 가게명(name)은 필수입니다.")
    if not out["ko"]["location"]:
        out["ko"]["location"] = out["ko"]["name"]
    if not out["ko"]["menu"]:
        out["ko"]["menu"] = out["ko"]["name"]
    if not out["ko"]["about"]:
        out["ko"]["about"] = out["ko"]["name"]
    filled: list[str] = []
    for lang in ("en", "ja"):
        for f in SHOP_TEXT_FIELDS:
            if not out[lang][f]:
                out[lang][f] = out["ko"][f]
                filled.append(f"{lang}.{f}")
    if filled:
        notes.append(
            "비어 있던 EN/JA 항목은 한국어와 동일하게 저장했습니다: "
            + ", ".join(filled)
        )
    return out, notes


def get_dish(kind: str, slug: str) -> dict[str, Any]:
    bundle = i18n_store.load_all()
    texts = _empty_dish_texts()
    for lang in i18n_store.LANGS:
        d = (bundle[lang].get("dishes") or {}).get(slug) or {}
        for f in DISH_TEXT_FIELDS:
            texts[lang][f] = str(d.get(f) or "")
    cover = dish_cover_path(slug)
    return {
        "kind": kind,
        "slug": slug,
        "texts": texts,
        # convenience for list-style KO display
        "title": texts["ko"]["title"],
        "desc": texts["ko"]["desc"],
        "about": texts["ko"]["about"],
        "page": str(dish_index_path(kind, slug).relative_to(ROOT).as_posix())
        if dish_index_path(kind, slug).is_file()
        else "",
        "image_hint": rel_posix(cover),
        "image_exists": cover.is_file(),
    }


def find_shop_page(shop_slug: str) -> tuple[str, str, Path] | None:
    """Return (kind, dish_slug, path) for a shop HTML page."""
    for kind, base in (("meals", MEALS_DIR), ("desserts", DESSERTS_DIR)):
        if not base.is_dir():
            continue
        for dish_dir_path in base.iterdir():
            if not dish_dir_path.is_dir():
                continue
            page = dish_dir_path / f"{shop_slug}.html"
            if page.is_file():
                return kind, dish_dir_path.name, page
    return None


def list_shops() -> list[ShopItem]:
    ko = i18n_store.load_lang("ko")
    restaurants = ko.get("restaurants") or {}
    items: list[ShopItem] = []
    seen: set[str] = set()

    for kind, base in (("meals", MEALS_DIR), ("desserts", DESSERTS_DIR)):
        if not base.is_dir():
            continue
        for dish_dir_path in sorted(base.iterdir()):
            if not dish_dir_path.is_dir():
                continue
            for page in sorted(dish_dir_path.glob("*.html")):
                if page.name == "index.html":
                    continue
                slug = page.stem
                seen.add(slug)
                r = restaurants.get(slug) or {}
                items.append(
                    ShopItem(
                        slug=slug,
                        name=str(r.get("name") or slug),
                        dish_slug=dish_dir_path.name,
                        kind=kind,
                        location=str(r.get("location") or ""),
                        page_path=page.relative_to(ROOT).as_posix(),
                    )
                )

    # i18n-only restaurants without pages
    for slug, r in restaurants.items():
        if slug in seen:
            continue
        found = find_shop_page(slug)
        kind = found[0] if found else ""
        dish = found[1] if found else ""
        items.append(
            ShopItem(
                slug=slug,
                name=str(r.get("name") or slug),
                dish_slug=dish,
                kind=kind or "?",
                location=str(r.get("location") or ""),
                page_path=None,
            )
        )

    items.sort(key=lambda x: (x.kind, x.dish_slug, x.slug))
    return items


def get_shop(slug: str) -> dict[str, Any]:
    bundle = i18n_store.load_all()
    texts = _empty_shop_texts()
    maps_url = ""
    for lang in i18n_store.LANGS:
        r = (bundle[lang].get("restaurants") or {}).get(slug) or {}
        for f in SHOP_TEXT_FIELDS:
            texts[lang][f] = str(r.get(f) or "")
        if lang == "ko":
            maps_url = str(r.get("mapsUrl") or "")
    found = find_shop_page(slug)
    kind = found[0] if found else ""
    dish_slug = found[1] if found else ""
    page = found[2].relative_to(ROOT).as_posix() if found else ""
    kind_eff = kind or "desserts"
    dish_eff = dish_slug or "desserts"
    photo = shop_photo_path(kind_eff, dish_eff, slug)
    menu = shop_menu_path(kind_eff, dish_eff, slug)
    return {
        "slug": slug,
        "kind": kind,
        "dish_slug": dish_slug,
        "texts": texts,
        "name": texts["ko"]["name"],
        "location": texts["ko"]["location"],
        "mapsUrl": maps_url,
        "menu": texts["ko"]["menu"],
        "price": texts["ko"]["price"],
        "tip": texts["ko"]["tip"],
        "about": texts["ko"]["about"],
        "page": page,
        "image_hint": rel_posix(photo),
        "menu_image_hint": rel_posix(menu),
        "image_exists": photo.is_file(),
        "menu_image_exists": menu.is_file(),
    }


def save_dish_fields(
    kind: str,
    slug: str,
    texts: dict[str, dict[str, str]],
) -> list[str]:
    notes: list[str] = []
    normalized, fill_notes = normalize_dish_texts(texts)
    notes.extend(fill_notes)
    bundle = i18n_store.load_all()
    for lang in i18n_store.LANGS:
        dishes = bundle[lang].setdefault("dishes", {})
        entry = dict(dishes.get(slug) or {})
        entry.update(normalized[lang])
        dishes[slug] = entry
    i18n_store.save_all(bundle)
    notes.append("번역(KO/EN/JA) 저장 완료")
    notes.append(i18n_store.build_bundle())
    return notes


def create_dish(
    kind: str,
    slug: str,
    texts: dict[str, dict[str, str]],
    emoji: str = "🍽️",
) -> list[str]:
    slug = validate_slug(slug)
    if kind not in ("meals", "desserts"):
        raise ValueError("kind는 meals 또는 desserts 여야 합니다.")
    notes: list[str] = []
    page = dish_index_path(kind, slug)
    if page.exists():
        raise ValueError(f"이미 페이지가 있습니다: {page.relative_to(ROOT)}")

    normalized, fill_notes = normalize_dish_texts(texts)
    notes.extend(fill_notes)

    bundle = i18n_store.load_all()
    for lang in i18n_store.LANGS:
        dishes = bundle[lang].setdefault("dishes", {})
        if slug in dishes:
            raise ValueError(f"i18n dishes.{slug} 키가 이미 있습니다 ({lang}).")
        dishes[slug] = dict(normalized[lang])
    i18n_store.save_all(bundle)
    notes.append("i18n ko/en/ja에 dishes 항목 추가")

    page.parent.mkdir(parents=True, exist_ok=True)
    default_emoji = emoji or ("🍽️" if kind == "meals" else "🍰")
    page.write_text(
        render_dish_page(kind, slug, default_emoji),
        encoding="utf-8",
        newline="\n",
    )
    notes.append(f"페이지 생성: {page.relative_to(ROOT).as_posix()}")

    hub = hub_index_path(kind)
    if hub.is_file():
        html = hub.read_text(encoding="utf-8")
        html = insert_before_card_grid_close(
            html, dish_card_html(kind, slug, default_emoji)
        )
        hub.write_text(html, encoding="utf-8", newline="\n")
        notes.append(f"허브 카드 추가: {hub.relative_to(ROOT).as_posix()}")

    notes.append(f"대표 이미지 저장 위치: {rel_posix(dish_cover_path(slug))}")
    notes.append(i18n_store.build_bundle())
    return notes


def rename_dish(kind: str, old_slug: str, new_slug: str) -> list[str]:
    new_slug = validate_slug(new_slug)
    if old_slug == new_slug:
        return ["슬러그가 동일합니다."]
    notes: list[str] = []
    old_dir = dish_dir(kind, old_slug)
    new_dir = dish_dir(kind, new_slug)
    if not old_dir.is_dir():
        raise ValueError(f"폴더 없음: {old_dir.relative_to(ROOT)}")
    if new_dir.exists():
        raise ValueError(f"대상 폴더가 이미 있음: {new_dir.relative_to(ROOT)}")

    bundle = i18n_store.load_all()
    for lang in i18n_store.LANGS:
        dishes = bundle[lang].setdefault("dishes", {})
        if old_slug not in dishes:
            raise ValueError(f"dishes.{old_slug} 없음 ({lang})")
        if new_slug in dishes:
            raise ValueError(f"dishes.{new_slug} 이미 있음 ({lang})")
        dishes[new_slug] = dishes.pop(old_slug)
    i18n_store.save_all(bundle)
    notes.append(f"i18n dishes.{old_slug} → dishes.{new_slug}")

    old_dir.rename(new_dir)
    notes.append(f"폴더 이동: {old_dir.name} → {new_dir.name}")

    # Rewrite i18n key references inside the dish folder HTML
    for html_path in new_dir.rglob("*.html"):
        text = html_path.read_text(encoding="utf-8")
        text2 = text.replace(f"dishes.{old_slug}.", f"dishes.{new_slug}.")
        text2 = text2.replace(f"/dishes/{old_slug}.jpg", f"/dishes/{new_slug}.jpg")
        text2 = text2.replace(f"./{old_slug}/", f"./{new_slug}/")
        if text2 != text:
            html_path.write_text(text2, encoding="utf-8", newline="\n")

    hub = hub_index_path(kind)
    if hub.is_file():
        html = hub.read_text(encoding="utf-8")
        html = html.replace(f"./{old_slug}/", f"./{new_slug}/")
        html = html.replace(f"dishes.{old_slug}.", f"dishes.{new_slug}.")
        html = html.replace(f"/dishes/{old_slug}.jpg", f"/dishes/{new_slug}.jpg")
        hub.write_text(html, encoding="utf-8", newline="\n")
        notes.append("허브 index 링크 갱신")

    old_img = dish_cover_path(old_slug)
    new_img = dish_cover_path(new_slug)
    if old_img.is_file() and not new_img.exists():
        old_img.rename(new_img)
        notes.append(f"이미지 이름 변경: {old_img.name} → {new_img.name}")

    notes.append(i18n_store.build_bundle())
    return notes


def delete_dish(
    kind: str,
    slug: str,
    *,
    delete_images: bool = False,
) -> list[str]:
    notes: list[str] = []
    # Block if shops still exist under dish
    d = dish_dir(kind, slug)
    if d.is_dir():
        shops = [p for p in d.glob("*.html") if p.name != "index.html"]
        if shops:
            raise ValueError(
                "가게 페이지가 남아 있습니다. 먼저 가게를 삭제하세요: "
                + ", ".join(p.stem for p in shops)
            )

    bundle = i18n_store.load_all()
    for lang in i18n_store.LANGS:
        i18n_store.del_nested(bundle[lang], ["dishes", slug])
    i18n_store.save_all(bundle)
    notes.append(f"i18n dishes.{slug} 삭제")

    page = dish_index_path(kind, slug)
    if page.is_file():
        page.unlink()
        notes.append(f"삭제: {page.relative_to(ROOT).as_posix()}")
    if d.is_dir():
        try:
            d.rmdir()
            notes.append(f"빈 폴더 삭제: {d.relative_to(ROOT).as_posix()}")
        except OSError:
            notes.append(f"폴더에 다른 파일이 있어 유지: {d.relative_to(ROOT).as_posix()}")

    hub = hub_index_path(kind)
    if hub.is_file():
        html = hub.read_text(encoding="utf-8")
        html2 = remove_card_referencing(html, f"./{slug}/")
        if html2 != html:
            hub.write_text(html2, encoding="utf-8", newline="\n")
            notes.append("허브 카드 제거")

    if delete_images:
        img = dish_cover_path(slug)
        if img.is_file():
            img.unlink()
            notes.append(f"이미지 삭제: {rel_posix(img)}")

    notes.append(i18n_store.build_bundle())
    return notes


def save_shop_fields(
    slug: str,
    texts: dict[str, dict[str, str]],
    *,
    regenerate_maps: bool = True,
) -> list[str]:
    notes: list[str] = []
    normalized, fill_notes = normalize_shop_texts(texts)
    notes.extend(fill_notes)
    bundle = i18n_store.load_all()
    old_ko = (bundle["ko"].get("restaurants") or {}).get(slug) or {}
    ko_loc = normalized["ko"]["location"]
    maps = (
        maps_url_from_location(ko_loc)
        if regenerate_maps and ko_loc
        else (old_ko.get("mapsUrl") or maps_url_from_location(ko_loc or normalized["ko"]["name"]))
    )

    for lang in i18n_store.LANGS:
        restaurants = bundle[lang].setdefault("restaurants", {})
        entry = dict(restaurants.get(slug) or {})
        entry.update(normalized[lang])
        entry["mapsUrl"] = maps
        restaurants[slug] = entry

    i18n_store.save_all(bundle)
    notes.append("번역(KO/EN/JA) 저장 완료")
    if regenerate_maps:
        notes.append("mapsUrl을 한국어 location 기준으로 재생성했습니다.")
    notes.append(i18n_store.build_bundle())
    return notes


def create_shop(
    kind: str,
    dish_slug: str,
    shop_slug: str,
    texts: dict[str, dict[str, str]],
) -> list[str]:
    shop_slug = validate_slug(shop_slug)
    dish_slug = validate_slug(dish_slug)
    notes: list[str] = []
    parent = dish_dir(kind, dish_slug)
    if not (parent / "index.html").is_file():
        raise ValueError(
            f"부모 음식 페이지가 없습니다: {parent.relative_to(ROOT)}. 먼저 음식을 추가하세요."
        )
    page = shop_page_path(kind, dish_slug, shop_slug)
    if page.exists():
        raise ValueError(f"이미 페이지가 있습니다: {page.relative_to(ROOT)}")

    normalized, fill_notes = normalize_shop_texts(texts)
    notes.extend(fill_notes)
    maps = maps_url_from_location(
        normalized["ko"]["location"] or normalized["ko"]["name"]
    )

    bundle = i18n_store.load_all()
    for lang in i18n_store.LANGS:
        restaurants = bundle[lang].setdefault("restaurants", {})
        if shop_slug in restaurants:
            raise ValueError(f"restaurants.{shop_slug} 이미 있음 ({lang})")
        entry = dict(normalized[lang])
        entry["mapsUrl"] = maps
        restaurants[shop_slug] = entry
    i18n_store.save_all(bundle)
    notes.append("i18n restaurants 추가 (KO/EN/JA)")

    page.write_text(
        render_shop_page(kind, dish_slug, shop_slug),
        encoding="utf-8",
        newline="\n",
    )
    notes.append(f"페이지 생성: {page.relative_to(ROOT).as_posix()}")

    index = parent / "index.html"
    html = index.read_text(encoding="utf-8")
    html = insert_before_card_grid_close(
        html, shop_card_html(kind, dish_slug, shop_slug)
    )
    index.write_text(html, encoding="utf-8", newline="\n")
    notes.append("음식 Places 카드 추가")

    photo = shop_photo_path(kind, dish_slug, shop_slug)
    menu_img = shop_menu_path(kind, dish_slug, shop_slug)
    photo.parent.mkdir(parents=True, exist_ok=True)
    menu_img.parent.mkdir(parents=True, exist_ok=True)
    notes.append(f"상호 이미지 저장 위치: {rel_posix(photo)}")
    notes.append(f"메뉴 이미지 저장 위치: {rel_posix(menu_img)}")

    notes.append(i18n_store.build_bundle())
    return notes


def rename_shop(old_slug: str, new_slug: str) -> list[str]:
    new_slug = validate_slug(new_slug)
    if old_slug == new_slug:
        return ["슬러그가 동일합니다."]
    found = find_shop_page(old_slug)
    if not found:
        raise ValueError(f"가게 페이지를 찾을 수 없습니다: {old_slug}")
    kind, dish_slug, old_page = found
    new_page = shop_page_path(kind, dish_slug, new_slug)
    if new_page.exists():
        raise ValueError(f"대상 페이지가 이미 있음: {new_page.relative_to(ROOT)}")

    notes: list[str] = []
    bundle = i18n_store.load_all()
    for lang in i18n_store.LANGS:
        restaurants = bundle[lang].setdefault("restaurants", {})
        if old_slug not in restaurants:
            raise ValueError(f"restaurants.{old_slug} 없음 ({lang})")
        if new_slug in restaurants:
            raise ValueError(f"restaurants.{new_slug} 이미 있음 ({lang})")
        restaurants[new_slug] = restaurants.pop(old_slug)
    i18n_store.save_all(bundle)
    notes.append(f"i18n restaurants.{old_slug} → {new_slug}")

    text = old_page.read_text(encoding="utf-8")
    text = text.replace(f"restaurants.{old_slug}.", f"restaurants.{new_slug}.")
    text = text.replace(f"/{old_slug}.jpg", f"/{new_slug}.jpg")
    text = text.replace(f"/{old_slug}-menu.jpg", f"/{new_slug}-menu.jpg")
    new_page.write_text(text, encoding="utf-8", newline="\n")
    old_page.unlink()
    notes.append(f"페이지 이름 변경: {old_page.name} → {new_page.name}")

    index = dish_dir(kind, dish_slug) / "index.html"
    if index.is_file():
        html = index.read_text(encoding="utf-8")
        html = html.replace(f"./{old_slug}.html", f"./{new_slug}.html")
        html = html.replace(f"restaurants.{old_slug}.", f"restaurants.{new_slug}.")
        html = html.replace(f"/{old_slug}.jpg", f"/{new_slug}.jpg")
        index.write_text(html, encoding="utf-8", newline="\n")
        notes.append("부모 index 카드 링크 갱신")

    # Best-effort image rename along canonical paths
    pairs = [
        (
            shop_photo_path(kind, dish_slug, old_slug),
            shop_photo_path(kind, dish_slug, new_slug),
        ),
        (
            shop_menu_path(kind, dish_slug, old_slug),
            shop_menu_path(kind, dish_slug, new_slug),
        ),
    ]
    for old_img, new_img in pairs:
        if old_img.is_file() and not new_img.exists():
            new_img.parent.mkdir(parents=True, exist_ok=True)
            old_img.rename(new_img)
            notes.append(f"이미지: {old_img.name} → {new_img.name}")

    notes.append(i18n_store.build_bundle())
    return notes


def delete_shop(slug: str, *, delete_images: bool = False) -> list[str]:
    notes: list[str] = []
    memberships = find_all_shop_pages(slug)
    primary = memberships[0] if memberships else None
    kind = primary[0] if primary else ""
    dish_slug = primary[1] if primary else ""

    bundle = i18n_store.load_all()
    for lang in i18n_store.LANGS:
        i18n_store.del_nested(bundle[lang], ["restaurants", slug])
    i18n_store.save_all(bundle)
    notes.append(f"i18n restaurants.{slug} 삭제")

    for mem_kind, mem_dish, page in memberships:
        if page.is_file():
            page.unlink()
            notes.append(f"삭제: {page.relative_to(ROOT).as_posix()}")
        index = dish_dir(mem_kind, mem_dish) / "index.html"
        if index.is_file():
            html = index.read_text(encoding="utf-8")
            html2 = remove_card_referencing(html, f"./{slug}.html")
            if html2 != html:
                index.write_text(html2, encoding="utf-8", newline="\n")
                notes.append(f"Places 카드 제거: {mem_kind}/{mem_dish}")

    if delete_images and kind and dish_slug:
        for p in (
            shop_photo_path(kind, dish_slug, slug),
            shop_menu_path(kind, dish_slug, slug),
        ):
            if p.is_file():
                p.unlink()
                notes.append(f"이미지 삭제: {rel_posix(p)}")

    notes.append(i18n_store.build_bundle())
    return notes


def dish_options_for_select() -> list[tuple[str, str, str]]:
    """(kind, slug, label) for shop create form."""
    out: list[tuple[str, str, str]] = []
    for kind in ("meals", "desserts"):
        for d in list_dishes(kind):
            out.append((kind, d.slug, f"[{kind}] {d.slug} — {d.title}"))
    return out


def shops_under_dish(kind: str, dish_slug: str) -> set[str]:
    d = dish_dir(kind, dish_slug)
    if not d.is_dir():
        return set()
    return {p.stem for p in d.glob("*.html") if p.name != "index.html"}


def find_all_shop_pages(shop_slug: str) -> list[tuple[str, str, Path]]:
    """All (kind, dish_slug, path) for a shop that appears under multiple dishes."""
    found: list[tuple[str, str, Path]] = []
    for kind, base in (("meals", MEALS_DIR), ("desserts", DESSERTS_DIR)):
        if not base.is_dir():
            continue
        for dish_dir_path in base.iterdir():
            if not dish_dir_path.is_dir():
                continue
            page = dish_dir_path / f"{shop_slug}.html"
            if page.is_file():
                found.append((kind, dish_dir_path.name, page))
    return found


def list_child_shops(kind: str, dish_slug: str) -> list[tuple[str, str]]:
    """Read-only child shops under a dish: (slug, display_name)."""
    ko = i18n_store.load_lang("ko")
    restaurants = ko.get("restaurants") or {}
    out: list[tuple[str, str]] = []
    for slug in sorted(shops_under_dish(kind, dish_slug)):
        r = restaurants.get(slug) or {}
        out.append((slug, str(r.get("name") or slug)))
    return out


def _rewrite_shop_html_for_dish(
    html: str,
    *,
    src_kind: str,
    src_dish: str,
    dest_kind: str,
    dest_dish: str,
    shop_slug: str,
) -> str:
    text = html
    if src_dish != dest_dish:
        text = text.replace(f"dishes.{src_dish}.", f"dishes.{dest_dish}.")
    src_photo = rel_posix(shop_photo_path(src_kind, src_dish, shop_slug))
    src_menu = rel_posix(shop_menu_path(src_kind, src_dish, shop_slug))
    dest_photo = rel_posix(shop_photo_path(dest_kind, dest_dish, shop_slug))
    dest_menu = rel_posix(shop_menu_path(dest_kind, dest_dish, shop_slug))
    if src_photo != dest_photo:
        text = text.replace(src_photo, dest_photo)
    if src_menu != dest_menu:
        text = text.replace(src_menu, dest_menu)
    if src_kind == "meals" and dest_kind == "meals" and src_dish != dest_dish:
        text = text.replace(
            f"/restaurants/{src_dish}/",
            f"/restaurants/{dest_dish}/",
        )
    return text


def _relocate_shop_image(src: Path, dst: Path, notes: list[str]) -> None:
    if src.resolve() == dst.resolve():
        return
    if not src.is_file():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        src.unlink()
        notes.append(f"이미지 정리(대상 유지): {rel_posix(src)}")
        return
    shutil.move(str(src), str(dst))
    notes.append(f"이미지 이동: {rel_posix(src)} → {rel_posix(dst)}")


def set_shop_parent(shop_slug: str, dest_kind: str, dest_dish: str) -> list[str]:
    """Place/move a shop under exactly one parent dish (HTML, index card, images)."""
    if dest_kind not in ("meals", "desserts"):
        raise ValueError("kind는 meals 또는 desserts 여야 합니다.")
    shop_slug = validate_slug(shop_slug)
    dest_dish = validate_slug(dest_dish)
    notes: list[str] = []

    dest_index = dish_index_path(dest_kind, dest_dish)
    if not dest_index.is_file():
        raise ValueError(
            f"부모 음식 페이지가 없습니다: {dest_index.relative_to(ROOT)}. "
            "먼저 음식을 추가하세요."
        )

    ko = i18n_store.load_lang("ko")
    if shop_slug not in (ko.get("restaurants") or {}):
        raise ValueError(f"restaurants.{shop_slug} 이(가) 없습니다.")

    memberships = find_all_shop_pages(shop_slug)
    already_here = [
        (k, d, p) for k, d, p in memberships if k == dest_kind and d == dest_dish
    ]
    extras = [
        (k, d, p) for k, d, p in memberships if not (k == dest_kind and d == dest_dish)
    ]

    if already_here and not extras:
        return ["부모 음식 변경 없음"]

    dest_page = shop_page_path(dest_kind, dest_dish, shop_slug)
    source = extras[0] if extras else (already_here[0] if already_here else None)

    if not dest_page.is_file():
        dest_page.parent.mkdir(parents=True, exist_ok=True)
        if source:
            src_kind, src_dish, src_page = source
            html = src_page.read_text(encoding="utf-8")
            html = _rewrite_shop_html_for_dish(
                html,
                src_kind=src_kind,
                src_dish=src_dish,
                dest_kind=dest_kind,
                dest_dish=dest_dish,
                shop_slug=shop_slug,
            )
            dest_page.write_text(html, encoding="utf-8", newline="\n")
            notes.append(
                f"상세 페이지 이동: {src_page.relative_to(ROOT).as_posix()} → "
                f"{dest_page.relative_to(ROOT).as_posix()}"
            )
        else:
            dest_page.write_text(
                render_shop_page(dest_kind, dest_dish, shop_slug),
                encoding="utf-8",
                newline="\n",
            )
            notes.append(f"상세 페이지 생성: {dest_page.relative_to(ROOT).as_posix()}")
    elif source:
        # Refresh paths if page already existed under dest but came from elsewhere earlier
        src_kind, src_dish, _src_page = source
        html = dest_page.read_text(encoding="utf-8")
        html = _rewrite_shop_html_for_dish(
            html,
            src_kind=src_kind,
            src_dish=src_dish,
            dest_kind=dest_kind,
            dest_dish=dest_dish,
            shop_slug=shop_slug,
        )
        dest_page.write_text(html, encoding="utf-8", newline="\n")

    # Move images from each previous parent into dest convention
    image_sources = extras if extras else memberships
    if not image_sources and source:
        image_sources = [source]
    for src_kind, src_dish, _ in image_sources:
        _relocate_shop_image(
            shop_photo_path(src_kind, src_dish, shop_slug),
            shop_photo_path(dest_kind, dest_dish, shop_slug),
            notes,
        )
        _relocate_shop_image(
            shop_menu_path(src_kind, src_dish, shop_slug),
            shop_menu_path(dest_kind, dest_dish, shop_slug),
            notes,
        )

    for src_kind, src_dish, src_page in extras:
        if src_page.is_file() and src_page.resolve() != dest_page.resolve():
            src_page.unlink()
            notes.append(f"이전 상세 삭제: {src_page.relative_to(ROOT).as_posix()}")
        old_index = dish_dir(src_kind, src_dish) / "index.html"
        if old_index.is_file():
            html = old_index.read_text(encoding="utf-8")
            html2 = remove_card_referencing(html, f"./{shop_slug}.html")
            if html2 != html:
                old_index.write_text(html2, encoding="utf-8", newline="\n")
                notes.append(f"이전 Places 카드 제거: {src_kind}/{src_dish}")

    html = dest_index.read_text(encoding="utf-8")
    if f"./{shop_slug}.html" not in html:
        html = insert_before_card_grid_close(
            html, shop_card_html(dest_kind, dest_dish, shop_slug)
        )
        dest_index.write_text(html, encoding="utf-8", newline="\n")
        notes.append(f"Places 카드 추가: {dest_kind}/{dest_dish}")
    else:
        # Refresh card image path after parent/kind change
        html2 = remove_card_referencing(html, f"./{shop_slug}.html")
        html2 = insert_before_card_grid_close(
            html2, shop_card_html(dest_kind, dest_dish, shop_slug)
        )
        if html2 != html:
            dest_index.write_text(html2, encoding="utf-8", newline="\n")
            notes.append(f"Places 카드 갱신: {dest_kind}/{dest_dish}")

    if extras or not already_here:
        notes.insert(0, f"부모 음식 → {dest_kind}/{dest_dish}")
    return notes

