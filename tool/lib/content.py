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
    delete_all_shop_images,
    discover_menu_images,
    dish_cover_path,
    dish_media_dir,
    relocate_all_shop_images,
    rel_posix,
    rename_shop_images,
    shop_dir,
    shop_media_dir,
    shop_menu_path,
    shop_photo_path,
)
from .paths import (
    DESSERTS_DIR,
    IMAGES_RESTAURANTS,
    MEALS_DIR,
    ROOT,
)
from .scaffold import (
    dish_card_html,
    dish_dir,
    dish_index_path,
    hub_index_path,
    insert_before_card_grid_close,
    iter_shop_pages,
    legacy_shop_page_path,
    remove_card_referencing,
    render_dish_page,
    render_shop_page,
    resolve_shop_page,
    rewrite_shop_slug_in_html,
    shop_card_html,
    shop_page_path,
    sync_shop_page_body,
    sync_shop_page_menu_gallery,
    sync_shop_page_visual,
)
from .shop_maps import (
    apply_maps_and_preview,
    infer_source_type,
    normalize_place_url,
    normalize_source_type,
    validate_place_for_source,
)
from .shop_body import (
    get_shop_body,
    migrate_shop_body_from_legacy,
    normalize_body,
    rewrite_body_folder_refs,
    rewrite_body_slug_refs,
    write_shop_body,
)
from .translate import BatchStatus, fill_body_blocks, fill_scalar_texts


def rebuild_food_recommend_catalog() -> str:
    """Regenerate data/food/recommend-catalog.js for the food-life quiz.

    Never raises: CRUD callers must not fail after pages/i18n are already written.
    On failure returns a Korean note string so CMS toasts can surface it.
    """
    import importlib.util

    try:
        script = ROOT / "tool" / "build-food-recommend-catalog.py"
        spec = importlib.util.spec_from_file_location(
            "build_food_recommend_catalog", script
        )
        if spec is None or spec.loader is None:
            return "먹거리 추천 카탈로그 갱신 실패: 스크립트 로드 불가"
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        catalog = mod.build_catalog()
        path = mod.write_catalog(catalog)
        return (
            f"먹거리 추천 카탈로그 갱신: {path.relative_to(ROOT).as_posix()} "
            f"({len(catalog)}개)"
        )
    except Exception as exc:  # noqa: BLE001
        return f"먹거리 추천 카탈로그 갱신 실패: {exc}"


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
    "kalguksu",
    "gukbap",
    "gomtang",
    "kongguksu",
    "gopchang",
    "tangsuyuk",
}

# Top-level dessert hubs only (brand shops like paris-baguette / sulbing live under bread / bingsu).
DESSERT_DISH_SLUGS_FALLBACK = {
    "bingsu",
    "bread",
    "butter-bread",
    "cafe",
    "dubai-cookie",
    "tanghulu",
    "yogurt-ice",
    "bungeoppang",
    "nangman-sandwich",
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
    """Require KO title; fill blank non-KO langs from EN (secondary) or KO."""
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
    for lang in i18n_store.LANGS:
        if lang == "ko":
            continue
        for f in DISH_TEXT_FIELDS:
            if not out[lang][f]:
                if lang in ("zh-Hant", "vi", "th", "ru") and out["en"][f]:
                    out[lang][f] = out["en"][f]
                else:
                    out[lang][f] = out["ko"][f]
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
    for lang in i18n_store.LANGS:
        if lang == "ko":
            continue
        for f in SHOP_TEXT_FIELDS:
            if not out[lang][f]:
                if lang in ("zh-Hant", "vi", "th", "ru") and out["en"][f]:
                    out[lang][f] = out["en"][f]
                else:
                    out[lang][f] = out["ko"][f]
    return out, notes


def _dish_old_texts(bundle: dict[str, dict[str, Any]], slug: str) -> dict[str, dict[str, str]]:
    out = _empty_dish_texts()
    for lang in i18n_store.LANGS:
        d = (bundle[lang].get("dishes") or {}).get(slug) or {}
        for f in DISH_TEXT_FIELDS:
            out[lang][f] = str(d.get(f) or "")
    return out


def _shop_old_texts(bundle: dict[str, dict[str, Any]], slug: str) -> dict[str, dict[str, str]]:
    out = _empty_shop_texts()
    for lang in i18n_store.LANGS:
        r = (bundle[lang].get("restaurants") or {}).get(slug) or {}
        for f in SHOP_TEXT_FIELDS:
            out[lang][f] = str(r.get(f) or "")
    return out


def get_dish(kind: str, slug: str) -> dict[str, Any]:
    bundle = i18n_store.load_all()
    texts = _empty_dish_texts()
    for lang in i18n_store.LANGS:
        d = (bundle[lang].get("dishes") or {}).get(slug) or {}
        for f in DISH_TEXT_FIELDS:
            texts[lang][f] = str(d.get(f) or "")
    cover = dish_cover_path(slug, kind)
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
            page = resolve_shop_page(kind, dish_dir_path.name, shop_slug)
            if page:
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
            for slug, page in iter_shop_pages(kind, dish_dir_path.name):
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
    phone = ""
    hours = ""
    maps_url = ""
    place_url = ""
    maps_embed = ""
    maps_provider = ""
    source_type = ""
    preview_title = ""
    preview_image = ""
    for lang in i18n_store.LANGS:
        r = (bundle[lang].get("restaurants") or {}).get(slug) or {}
        for f in SHOP_TEXT_FIELDS:
            texts[lang][f] = str(r.get(f) or "")
        if lang == "ko":
            maps_url = str(r.get("mapsUrl") or "")
            place_url = str(r.get("placeUrl") or "")
            maps_embed = str(r.get("mapsEmbedUrl") or "")
            maps_provider = str(r.get("mapsProvider") or "")
            source_type = infer_source_type(
                source_type=str(r.get("sourceType") or ""),
                place_url=place_url,
                maps_provider=maps_provider,
            )
            preview_title = str(r.get("previewTitle") or "")
            preview_image = str(r.get("previewImage") or "")
            phone = str(r.get("phone") or "")
            hours = str(r.get("hours") or "")
    found = find_shop_page(slug)
    kind = found[0] if found else ""
    dish_slug = found[1] if found else ""
    page = found[2].relative_to(ROOT).as_posix() if found else ""
    kind_eff = kind or "desserts"
    dish_eff = dish_slug or "desserts"
    photo = shop_photo_path(kind_eff, dish_eff, slug)
    menus = discover_menu_images(kind_eff, dish_eff, slug)
    body = get_shop_body(slug, bundle=bundle)
    return {
        "slug": slug,
        "kind": kind,
        "dish_slug": dish_slug,
        "texts": texts,
        "name": texts["ko"]["name"],
        "location": texts["ko"]["location"],
        "phone": phone,
        "hours": hours,
        "placeUrl": place_url,
        "mapsUrl": maps_url,
        "mapsEmbedUrl": maps_embed,
        "mapsProvider": maps_provider,
        "sourceType": source_type,
        "previewTitle": preview_title,
        "previewImage": preview_image,
        "menu": texts["ko"]["menu"],
        "price": texts["ko"]["price"],
        "tip": texts["ko"]["tip"],
        "about": texts["ko"]["about"],
        "body": body,
        "page": page,
        "image_hint": rel_posix(photo),
        "menu_image_hint": menus[0].rel if menus else rel_posix(
            shop_menu_path(kind_eff, dish_eff, slug)
        ),
        "image_exists": photo.is_file(),
        "menu_image_exists": bool(menus),
        "menu_images": [
            {
                "index": m.index,
                "rel": m.rel,
                "legacy": m.legacy,
                "exists": m.path.is_file(),
            }
            for m in menus
        ],
    }


def save_dish_fields(
    kind: str,
    slug: str,
    texts: dict[str, dict[str, str]],
    *,
    force_translate: bool = False,
) -> tuple[list[str], BatchStatus]:
    notes: list[str] = []
    status = BatchStatus()
    bundle = i18n_store.load_all()
    old_texts = _dish_old_texts(bundle, slug)
    texts = fill_scalar_texts(
        texts,
        DISH_TEXT_FIELDS,
        old_texts=old_texts,
        force=force_translate,
        status=status,
    )
    normalized, fill_notes = normalize_dish_texts(texts)
    notes.extend(fill_notes)
    for lang in i18n_store.LANGS:
        dishes = bundle[lang].setdefault("dishes", {})
        entry = dict(dishes.get(slug) or {})
        entry.update(normalized[lang])
        dishes[slug] = entry
    i18n_store.save_all(bundle)
    notes.append("i18n 저장 완료")
    notes.append(i18n_store.build_bundle())
    return notes, status


def create_dish(
    kind: str,
    slug: str,
    texts: dict[str, dict[str, str]],
    emoji: str = "🍽️",
) -> tuple[list[str], BatchStatus]:
    slug = validate_slug(slug)
    if kind not in ("meals", "desserts"):
        raise ValueError("kind는 meals 또는 desserts 여야 합니다.")
    notes: list[str] = []
    status = BatchStatus()
    page = dish_index_path(kind, slug)
    if page.exists():
        raise ValueError(f"이미 페이지가 있습니다: {page.relative_to(ROOT)}")

    texts = fill_scalar_texts(
        texts,
        DISH_TEXT_FIELDS,
        old_texts=None,
        force=True,
        status=status,
    )
    normalized, fill_notes = normalize_dish_texts(texts)
    notes.extend(fill_notes)

    bundle = i18n_store.load_all()
    for lang in i18n_store.LANGS:
        dishes = bundle[lang].setdefault("dishes", {})
        if slug in dishes:
            raise ValueError(f"i18n dishes.{slug} 키가 이미 있습니다 ({lang}).")
        dishes[slug] = dict(normalized[lang])
    i18n_store.save_all(bundle)
    notes.append("i18n 전체 언어(ko/en/ja/zh/zh-Hant/vi/th/ru)에 dishes 항목 추가")

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

    media = dish_media_dir(kind, slug)
    media.mkdir(parents=True, exist_ok=True)
    notes.append(f"대표 이미지 저장 위치: {rel_posix(dish_cover_path(slug, kind))}")
    notes.append(i18n_store.build_bundle())
    notes.append(rebuild_food_recommend_catalog())
    return notes, status


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

    shutil.move(str(old_dir), str(new_dir))
    notes.append(f"폴더 이동: {old_dir.name} → {new_dir.name}")

    # Rewrite i18n / image path references inside the dish folder HTML
    for html_path in new_dir.rglob("*.html"):
        text = html_path.read_text(encoding="utf-8")
        text2 = text.replace(f"dishes.{old_slug}.", f"dishes.{new_slug}.")
        text2 = text2.replace(f"/dishes/{old_slug}.jpg", f"/dishes/{new_slug}.jpg")
        text2 = text2.replace(f"./{old_slug}/", f"./{new_slug}/")
        if kind == "meals":
            text2 = text2.replace(
                f"/restaurants/{old_slug}/",
                f"/restaurants/{new_slug}/",
            )
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

    # Cover lives under the dish folder (moved with rename). Legacy Images/ leftover:
    from .images import legacy_dish_cover_path

    legacy_img = legacy_dish_cover_path(old_slug)
    new_img = dish_cover_path(new_slug, kind)
    if legacy_img.is_file() and not new_img.exists():
        new_img.parent.mkdir(parents=True, exist_ok=True)
        legacy_img.rename(new_img)
        notes.append(f"이미지 이동: {legacy_img.name} → {rel_posix(new_img)}")

    # Legacy restaurants image folder cleanup (pre page-media layout)
    if kind == "meals":
        old_rest = IMAGES_RESTAURANTS / old_slug
        new_rest = IMAGES_RESTAURANTS / new_slug
        if old_rest.is_dir() and not new_rest.exists():
            old_rest.rename(new_rest)
            notes.append(
                f"레거시 가게 이미지 폴더: restaurants/{old_slug} → restaurants/{new_slug}"
            )
        elif old_rest.is_dir() and new_rest.exists():
            for src in old_rest.iterdir():
                dst = new_rest / src.name
                if dst.exists():
                    if src.is_file():
                        src.unlink()
                    continue
                shutil.move(str(src), str(dst))
                notes.append(
                    f"레거시 가게 이미지 병합: {src.name} → restaurants/{new_slug}/"
                )
            try:
                old_rest.rmdir()
            except OSError:
                notes.append(f"경고: restaurants/{old_slug} 비우지 못함")

    notes.append(i18n_store.build_bundle())
    notes.append(rebuild_food_recommend_catalog())
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
        shops = sorted(shops_under_dish(kind, slug))
        if shops:
            raise ValueError(
                "가게 페이지가 남아 있습니다. 먼저 가게를 삭제하세요: "
                + ", ".join(shops)
            )

    bundle = i18n_store.load_all()
    for lang in i18n_store.LANGS:
        i18n_store.del_nested(bundle[lang], ["dishes", slug])
    i18n_store.save_all(bundle)
    notes.append(f"i18n dishes.{slug} 삭제")

    hub = hub_index_path(kind)
    if hub.is_file():
        html = hub.read_text(encoding="utf-8")
        html2 = remove_card_referencing(html, f"./{slug}/")
        if html2 != html:
            hub.write_text(html2, encoding="utf-8", newline="\n")
            notes.append("허브 카드 제거")

    if delete_images and d.is_dir():
        for img in d.rglob("*.jpg"):
            if img.is_file():
                notes.append(f"이미지 삭제: {rel_posix(img)}")
                img.unlink()
        shutil.rmtree(d, ignore_errors=True)
        notes.append(f"폴더 삭제: {d.relative_to(ROOT).as_posix()}")
    else:
        page = dish_index_path(kind, slug)
        if page.is_file():
            page.unlink()
            notes.append(f"삭제: {page.relative_to(ROOT).as_posix()}")
        if d.is_dir():
            try:
                d.rmdir()
                notes.append(f"빈 폴더 삭제: {d.relative_to(ROOT).as_posix()}")
            except OSError:
                notes.append(
                    f"폴더에 다른 파일이 있어 유지: {d.relative_to(ROOT).as_posix()}"
                )

    notes.append(i18n_store.build_bundle())
    notes.append(rebuild_food_recommend_catalog())
    return notes


def save_shop_fields(
    slug: str,
    texts: dict[str, dict[str, str]],
    *,
    regenerate_maps: bool = True,
    body: list[dict[str, Any]] | None = None,
    force_translate: bool = False,
    place_url: str | None = None,
    source_type: str | None = None,
    fetch_preview: bool = True,
    phone: str | None = None,
    hours: str | None = None,
) -> tuple[list[str], BatchStatus]:
    notes: list[str] = []
    status = BatchStatus()
    bundle = i18n_store.load_all()
    old_texts = _shop_old_texts(bundle, slug)
    texts = fill_scalar_texts(
        texts,
        SHOP_TEXT_FIELDS,
        old_texts=old_texts,
        force=force_translate,
        status=status,
    )
    normalized, fill_notes = normalize_shop_texts(texts)
    notes.extend(fill_notes)
    old_ko = (bundle["ko"].get("restaurants") or {}).get(slug) or {}
    ko_loc = normalized["ko"]["location"]
    ko_name = normalized["ko"]["name"]
    if place_url is None:
        place_url = str(old_ko.get("placeUrl") or "")
    place_url = normalize_place_url(place_url)
    st = normalize_source_type(source_type) or infer_source_type(
        source_type=str(old_ko.get("sourceType") or ""),
        place_url=place_url,
        maps_provider=str(old_ko.get("mapsProvider") or ""),
    )
    err = validate_place_for_source(st, place_url)
    if err:
        raise ValueError(err)
    if st == "custom":
        place_url = ""

    map_fields = apply_maps_and_preview(
        dict(old_ko),
        place_url=place_url,
        location=ko_loc,
        name=ko_name,
        source_type=st,
        fetch_preview=bool(fetch_preview and place_url),
        regenerate=regenerate_maps,
    )
    # If no place link and not regenerating, keep prior mapsUrl when present
    if not place_url and not regenerate_maps and st != "custom":
        map_fields["mapsUrl"] = str(
            old_ko.get("mapsUrl") or map_fields.get("mapsUrl") or ""
        )
        map_fields["mapsEmbedUrl"] = str(
            old_ko.get("mapsEmbedUrl") or map_fields.get("mapsEmbedUrl") or ""
        )

    phone_val = (
        str(old_ko.get("phone") or "") if phone is None else str(phone or "").strip()
    )
    hours_val = (
        str(old_ko.get("hours") or "") if hours is None else str(hours or "").strip()
    )

    for lang in i18n_store.LANGS:
        restaurants = bundle[lang].setdefault("restaurants", {})
        entry = dict(restaurants.get(slug) or {})
        entry.update(normalized[lang])
        for key in (
            "placeUrl",
            "mapsUrl",
            "mapsEmbedUrl",
            "mapsProvider",
            "sourceType",
            "previewTitle",
            "previewImage",
        ):
            if key in map_fields:
                entry[key] = map_fields[key]
        entry["phone"] = phone_val
        entry["hours"] = hours_val
        restaurants[slug] = entry

    if body is not None:
        old_body = get_shop_body(slug, bundle=bundle)
        body = fill_body_blocks(
            body, old_blocks=old_body, force=force_translate, status=status
        )
        notes.extend(write_shop_body(slug, body, bundle=bundle, clear_tip=False))
        # Tip is legacy; keep form value but prefer body on site when present.
        # Clear tip when body has text so tip fallback stays unused.
        has_text = any(b.get("type") == "text" for b in normalize_body(body))
        if has_text:
            for lang in i18n_store.LANGS:
                entry = (bundle[lang].get("restaurants") or {}).get(slug) or {}
                entry["tip"] = ""
                bundle[lang].setdefault("restaurants", {})[slug] = entry
            notes.append("본문에 문단이 있어 tip 필드를 비웠습니다 (사이트는 body 사용).")

    i18n_store.save_all(bundle)
    notes.append("i18n 저장 완료")
    notes.append(f"등록 방식: {st}")
    if place_url:
        notes.append("가게 링크로 mapsUrl / mapsEmbedUrl을 갱신했습니다.")
        if map_fields.get("previewTitle") or map_fields.get("previewImage"):
            notes.append("링크 미리보기(OG) 메타를 저장했습니다.")
        elif fetch_preview:
            notes.append("링크 미리보기(OG)는 가져오지 못했습니다 — 임베드·링크는 유지합니다.")
    elif st == "custom":
        notes.append("주소·이름으로 지도 임베드를 저장했습니다." if map_fields.get("mapsEmbedUrl") else "사용자 커스텀 — 제목·본문·사진 중심으로 저장했습니다.")
    elif regenerate_maps:
        notes.append("주소·이름으로 mapsUrl / mapsEmbedUrl을 재생성했습니다.")
    notes.append(i18n_store.build_bundle())
    return notes, status


def set_shop_preview_image(slug: str, image_url: str) -> list[str]:
    """Set previewImage on all langs if missing or empty (does not rebuild bundle)."""
    url = (image_url or "").strip()
    if not url:
        return []
    bundle = i18n_store.load_all()
    changed = False
    for lang in i18n_store.LANGS:
        restaurants = bundle[lang].setdefault("restaurants", {})
        entry = dict(restaurants.get(slug) or {})
        if not entry:
            continue
        if str(entry.get("previewImage") or "").strip():
            continue
        entry["previewImage"] = url
        restaurants[slug] = entry
        changed = True
    if not changed:
        return []
    i18n_store.save_all(bundle)
    return ["미리보기 이미지를 저장했습니다.", i18n_store.build_bundle()]


def create_shop(
    kind: str,
    dish_slug: str,
    shop_slug: str,
    texts: dict[str, dict[str, str]],
    *,
    body: list[dict[str, Any]] | None = None,
    place_url: str = "",
    source_type: str = "",
    fetch_preview: bool = True,
    phone: str = "",
    hours: str = "",
) -> tuple[list[str], BatchStatus]:
    shop_slug = validate_slug(shop_slug)
    dish_slug = validate_slug(dish_slug)
    notes: list[str] = []
    status = BatchStatus()
    parent = dish_dir(kind, dish_slug)
    if not (parent / "index.html").is_file():
        raise ValueError(
            f"부모 음식 페이지가 없습니다: {parent.relative_to(ROOT)}. 먼저 음식을 추가하세요."
        )
    page = shop_page_path(kind, dish_slug, shop_slug)
    if page.exists() or legacy_shop_page_path(kind, dish_slug, shop_slug).exists():
        raise ValueError(f"이미 페이지가 있습니다: {page.relative_to(ROOT)}")

    texts = fill_scalar_texts(
        texts,
        SHOP_TEXT_FIELDS,
        old_texts=None,
        force=True,
        status=status,
    )
    normalized, fill_notes = normalize_shop_texts(texts)
    notes.extend(fill_notes)
    place_url = normalize_place_url(place_url)
    st = normalize_source_type(source_type) or infer_source_type(
        source_type=source_type, place_url=place_url
    )
    err = validate_place_for_source(st, place_url)
    if err:
        raise ValueError(err)
    if st == "custom":
        place_url = ""
    map_fields = apply_maps_and_preview(
        {},
        place_url=place_url,
        location=normalized["ko"]["location"],
        name=normalized["ko"]["name"],
        source_type=st,
        fetch_preview=bool(fetch_preview and place_url),
        regenerate=True,
    )
    body_blocks = fill_body_blocks(
        list(body or []),
        old_blocks=None,
        force=True,
        status=status,
    )
    body_blocks = normalize_body(body_blocks)

    bundle = i18n_store.load_all()
    phone_val = str(phone or "").strip()
    hours_val = str(hours or "").strip()
    for lang in i18n_store.LANGS:
        restaurants = bundle[lang].setdefault("restaurants", {})
        if shop_slug in restaurants:
            raise ValueError(f"restaurants.{shop_slug} 이미 있음 ({lang})")
        entry = dict(normalized[lang])
        for key in (
            "placeUrl",
            "mapsUrl",
            "mapsEmbedUrl",
            "mapsProvider",
            "sourceType",
            "previewTitle",
            "previewImage",
        ):
            if key in map_fields and map_fields[key] != "":
                entry[key] = map_fields[key]
            elif key in ("placeUrl", "mapsUrl", "mapsEmbedUrl", "sourceType"):
                entry[key] = map_fields.get(key) or (
                    "custom" if key == "sourceType" else ""
                )
        entry["phone"] = phone_val
        entry["hours"] = hours_val
        entry["body"] = body_blocks
        if body_blocks:
            entry["tip"] = ""
        restaurants[shop_slug] = entry
    i18n_store.save_all(bundle)
    notes.append("i18n restaurants 추가 (KO/EN/JA)")
    notes.append(f"등록 방식: {st}")
    if body_blocks:
        notes.append(f"본문 body {len(body_blocks)} 블록")
    if place_url:
        notes.append("가게 링크 기반 지도 임베드를 저장했습니다.")
        if map_fields.get("previewTitle") or map_fields.get("previewImage"):
            notes.append("링크 미리보기(OG) 메타를 저장했습니다.")
    elif st == "custom":
        notes.append(
            "주소·이름으로 지도 임베드를 저장했습니다."
            if map_fields.get("mapsEmbedUrl")
            else "사용자 커스텀 가게로 등록했습니다."
        )

    page.parent.mkdir(parents=True, exist_ok=True)
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
    media = shop_media_dir(kind, dish_slug, shop_slug)
    media.mkdir(parents=True, exist_ok=True)
    notes.append(f"상호 이미지 저장 위치: {rel_posix(photo)}")
    notes.append(f"본문 이미지 저장 위치: {rel_posix(media)}/body-1.jpg, body-2.jpg, …")
    notes.append(
        "안내: 공개 페이지는 사진 → 가게 정보 → 지도 순으로 보여 줍니다. "
        "사진이 없으면 링크 미리보기 이미지를 쓰거나 직접 업로드하세요."
    )

    notes.append(i18n_store.build_bundle())
    return notes, status


def migrate_shop_source_types() -> list[str]:
    """Persist inferred sourceType on existing restaurants (idempotent)."""
    notes: list[str] = []
    bundle = i18n_store.load_all()
    restaurants = bundle["ko"].get("restaurants") or {}
    changed = 0
    for slug, entry in restaurants.items():
        st = infer_source_type(
            source_type=str(entry.get("sourceType") or ""),
            place_url=str(entry.get("placeUrl") or ""),
            maps_provider=str(entry.get("mapsProvider") or ""),
        )
        for lang in i18n_store.LANGS:
            r = (bundle[lang].get("restaurants") or {}).get(slug)
            if not isinstance(r, dict):
                continue
            if r.get("sourceType") != st:
                r["sourceType"] = st
                changed += 1
    if changed:
        i18n_store.save_all(bundle)
        notes.append(f"sourceType 마이그레이션: {changed}개 항목 갱신")
        notes.append(i18n_store.build_bundle())
    else:
        notes.append("sourceType 마이그레이션: 변경 없음")
    return notes


def rename_shop(old_slug: str, new_slug: str) -> list[str]:
    new_slug = validate_slug(new_slug)
    if old_slug == new_slug:
        return ["슬러그가 동일합니다."]
    memberships = find_all_shop_pages(old_slug)
    if not memberships:
        raise ValueError(f"가게 페이지를 찾을 수 없습니다: {old_slug}")

    for kind, dish_slug, _old_page in memberships:
        new_page = shop_page_path(kind, dish_slug, new_slug)
        if new_page.exists() or legacy_shop_page_path(kind, dish_slug, new_slug).exists():
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
    body = get_shop_body(new_slug, bundle=bundle)
    if body:
        body = rewrite_body_slug_refs(body, old_slug, new_slug)
        rewritten: list[dict[str, Any]] = []
        for block in body:
            b = dict(block)
            if b.get("type") == "image":
                src = str(b.get("src") or "")
                src = src.replace(f"/{old_slug}/media/", f"/{new_slug}/media/")
                b["src"] = src
            rewritten.append(b)
        write_shop_body(new_slug, rewritten, bundle=bundle, clear_tip=False)
    i18n_store.save_all(bundle)
    notes.append(f"i18n restaurants.{old_slug} → {new_slug} (mapsUrl 유지)")

    for kind, dish_slug, old_page in memberships:
        new_page = shop_page_path(kind, dish_slug, new_slug)
        old_dir = old_page.parent if old_page.name == "index.html" else None
        new_dir = shop_dir(kind, dish_slug, new_slug)

        text = old_page.read_text(encoding="utf-8")
        text = rewrite_shop_slug_in_html(text, old_slug, new_slug)
        # Fix asset depth / back link if migrating flat → folder during rename
        if old_page.name != "index.html":
            text = text.replace('href="./index.html"', 'href="../index.html"')

        if old_dir and old_dir.name == old_slug and old_dir.is_dir():
            if new_dir.exists():
                raise ValueError(f"대상 폴더가 이미 있음: {new_dir.relative_to(ROOT)}")
            # shutil.move is more reliable than Path.rename on Windows
            shutil.move(str(old_dir), str(new_dir))
            (new_dir / "index.html").write_text(text, encoding="utf-8", newline="\n")
            notes.append(
                f"가게 폴더 이름 변경: {old_slug}/ → {new_slug}/"
            )
        else:
            new_page.parent.mkdir(parents=True, exist_ok=True)
            new_page.write_text(text, encoding="utf-8", newline="\n")
            if old_page.is_file():
                old_page.unlink()
            notes.extend(rename_shop_images(kind, dish_slug, old_slug, new_slug))
            notes.append(
                f"페이지 이름 변경: {old_page.name} → {new_page.relative_to(ROOT).as_posix()}"
            )

        notes.extend(sync_shop_page_body(kind, dish_slug, new_slug))

        index = dish_dir(kind, dish_slug) / "index.html"
        if index.is_file():
            html = index.read_text(encoding="utf-8")
            html = html.replace(f"./{old_slug}.html", f"./{new_slug}/index.html")
            html = html.replace(f"./{old_slug}/", f"./{new_slug}/")
            html = rewrite_shop_slug_in_html(html, old_slug, new_slug)
            index.write_text(html, encoding="utf-8", newline="\n")
            notes.append(f"부모 index 카드 갱신: {kind}/{dish_slug}")

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
        shop_folder = page.parent if page.name == "index.html" else None
        if page.is_file():
            page.unlink()
            notes.append(f"삭제: {page.relative_to(ROOT).as_posix()}")
        if shop_folder and shop_folder.name == slug and shop_folder.is_dir():
            if delete_images:
                notes.extend(delete_all_shop_images(mem_kind, mem_dish, slug))
            # Remove leftover media/ or empty dir
            media = shop_folder / "media"
            if media.is_dir():
                for p in list(media.iterdir()):
                    if p.is_file():
                        if delete_images:
                            p.unlink()
                        else:
                            break
                else:
                    try:
                        media.rmdir()
                    except OSError:
                        pass
            try:
                shop_folder.rmdir()
                notes.append(f"폴더 삭제: {shop_folder.relative_to(ROOT).as_posix()}")
            except OSError:
                pass
        index = dish_dir(mem_kind, mem_dish) / "index.html"
        if index.is_file():
            html = index.read_text(encoding="utf-8")
            html2 = remove_card_referencing(html, f"./{slug}.html")
            html2 = remove_card_referencing(html2, f"./{slug}/")
            if html2 != html:
                index.write_text(html2, encoding="utf-8", newline="\n")
                notes.append(f"Places 카드 제거: {mem_kind}/{mem_dish}")

    if delete_images:
        seen: set[str] = set()
        targets = memberships or (
            [(kind, dish_slug, None)] if kind and dish_slug else []
        )
        for mem_kind, mem_dish, _ in targets:
            key = f"{mem_kind}|{mem_dish}|{slug}"
            if key in seen:
                continue
            seen.add(key)
            notes.extend(delete_all_shop_images(mem_kind, mem_dish, slug))

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
    return {slug for slug, _ in iter_shop_pages(kind, dish_slug)}


def find_all_shop_pages(shop_slug: str) -> list[tuple[str, str, Path]]:
    """All (kind, dish_slug, path) for a shop that appears under multiple dishes."""
    found: list[tuple[str, str, Path]] = []
    for kind, base in (("meals", MEALS_DIR), ("desserts", DESSERTS_DIR)):
        if not base.is_dir():
            continue
        for dish_dir_path in base.iterdir():
            if not dish_dir_path.is_dir():
                continue
            page = resolve_shop_page(kind, dish_dir_path.name, shop_slug)
            if page:
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
    dest_photo = rel_posix(shop_photo_path(dest_kind, dest_dish, shop_slug))
    if src_photo != dest_photo:
        text = text.replace(src_photo, dest_photo)
    # Page-local cover stays media/cover.jpg; adjust site-root paths if present
    src_media = rel_posix(shop_media_dir(src_kind, src_dish, shop_slug))
    dest_media = rel_posix(shop_media_dir(dest_kind, dest_dish, shop_slug))
    if src_media != dest_media:
        text = text.replace(src_media + "/", dest_media + "/")
    if src_dish != dest_dish:
        text = text.replace(f"/{src_dish}/{shop_slug}/", f"/{dest_dish}/{shop_slug}/")
    if src_kind == "meals" and dest_kind == "meals" and src_dish != dest_dish:
        text = text.replace(
            f"/restaurants/{src_dish}/",
            f"/restaurants/{dest_dish}/",
        )
    return text


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
            # Prefer moving whole shop folder when already folder-based
            src_folder = (
                src_page.parent
                if src_page.name == "index.html" and src_page.parent.name == shop_slug
                else None
            )
            if src_folder and src_folder.is_dir() and not dest_page.parent.exists():
                shutil.move(str(src_folder), str(dest_page.parent))
                dest_page.write_text(html, encoding="utf-8", newline="\n")
            else:
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

    image_sources = extras if extras else memberships
    if not image_sources and source:
        image_sources = [source]
    for src_kind, src_dish, _ in image_sources:
        notes.extend(
            relocate_all_shop_images(
                src_kind, src_dish, dest_kind, dest_dish, shop_slug
            )
        )
        src_folder = rel_posix(shop_media_dir(src_kind, src_dish, shop_slug))
        dest_folder = rel_posix(shop_media_dir(dest_kind, dest_dish, shop_slug))
        if src_folder != dest_folder:
            bundle = i18n_store.load_all()
            body = get_shop_body(shop_slug, bundle=bundle)
            if body:
                body = rewrite_body_folder_refs(body, src_folder, dest_folder)
                write_shop_body(shop_slug, body, bundle=bundle, clear_tip=False)
                i18n_store.save_all(bundle)
                notes.append("본문 이미지 경로(i18n body) 부모 폴더에 맞춤")
                notes.append(i18n_store.build_bundle())

    for src_kind, src_dish, src_page in extras:
        if src_page.is_file() and src_page.resolve() != dest_page.resolve():
            src_folder = (
                src_page.parent
                if src_page.name == "index.html" and src_page.parent.name == shop_slug
                else None
            )
            src_page.unlink()
            notes.append(f"이전 상세 삭제: {src_page.relative_to(ROOT).as_posix()}")
            if src_folder and src_folder.is_dir():
                shutil.rmtree(src_folder, ignore_errors=True)
        old_index = dish_dir(src_kind, src_dish) / "index.html"
        if old_index.is_file():
            html = old_index.read_text(encoding="utf-8")
            html2 = remove_card_referencing(html, f"./{shop_slug}.html")
            html2 = remove_card_referencing(html2, f"./{shop_slug}/")
            if html2 != html:
                old_index.write_text(html2, encoding="utf-8", newline="\n")
                notes.append(f"이전 Places 카드 제거: {src_kind}/{src_dish}")

    html = dest_index.read_text(encoding="utf-8")
    has_card = (
        f"./{shop_slug}.html" in html or f"./{shop_slug}/" in html
    )
    if not has_card:
        html = insert_before_card_grid_close(
            html, shop_card_html(dest_kind, dest_dish, shop_slug)
        )
        dest_index.write_text(html, encoding="utf-8", newline="\n")
        notes.append(f"Places 카드 추가: {dest_kind}/{dest_dish}")
    else:
        html2 = remove_card_referencing(html, f"./{shop_slug}.html")
        html2 = remove_card_referencing(html2, f"./{shop_slug}/")
        html2 = insert_before_card_grid_close(
            html2, shop_card_html(dest_kind, dest_dish, shop_slug)
        )
        if html2 != html:
            dest_index.write_text(html2, encoding="utf-8", newline="\n")
            notes.append(f"Places 카드 갱신: {dest_kind}/{dest_dish}")

    notes.extend(sync_shop_page_body(dest_kind, dest_dish, shop_slug))

    if extras or not already_here:
        notes.insert(0, f"부모 음식 → {dest_kind}/{dest_dish}")
    return notes


def migrate_all_shop_bodies(*, force: bool = False) -> list[str]:
    """One-time: tip + menu images → restaurants.*.body, then sync HTML mounts."""
    from .scaffold import sync_all_shop_page_bodies

    notes: list[str] = []
    shops = list_shops()
    bundle = i18n_store.load_all()
    migrated = 0
    for shop in shops:
        kind = shop.kind if shop.kind in ("meals", "desserts") else ""
        dish = shop.dish_slug or ""
        if not kind or not dish:
            found = find_shop_page(shop.slug)
            if not found:
                notes.append(f"{shop.slug}: 페이지 없음 — 건너뜀")
                continue
            kind, dish, _ = found
        before = len(notes)
        shop_notes = migrate_shop_body_from_legacy(
            kind, dish, shop.slug, force=force, bundle=bundle, persist=False
        )
        notes.extend(shop_notes)
        if shop_notes and any("→ body" in n for n in shop_notes):
            migrated += 1
    i18n_store.save_all(bundle)
    notes.append(i18n_store.build_bundle())
    notes.extend(sync_all_shop_page_bodies())
    notes.insert(0, f"본문 마이그레이션: {migrated}/{len(shops)}개 가게 body 생성·갱신")
    return notes

