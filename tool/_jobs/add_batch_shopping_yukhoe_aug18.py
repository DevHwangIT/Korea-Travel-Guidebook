# -*- coding: utf-8 -*-
"""Aug 18 batch: shopping tips (convenience + 2+1), yukhoe/toast dishes+shops, cover fixes.

No git commit — run build-bundle, catalog, cache bump at end.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from lib import content, i18n_store  # noqa: E402
from lib.cache_bust import bump_asset_version  # noqa: E402
from lib.content_body import _text_block_from_langs  # noqa: E402
from lib.images import dish_cover_path, shop_photo_path  # noqa: E402
from lib.place_scrape import (  # noqa: E402
    download_image_to,
    naver_canonical_place_url,
    scrape_naver_place,
)
from lib.scaffold import sync_shop_page_visual  # noqa: E402
from lib.translate import BatchStatus, fill_scalar_texts, translate_text  # noqa: E402
from migrate_menu_i18n import migrate_menu_items  # noqa: E402
from migrate_shop_enrich import apply_to_bundle, enrich_one  # noqa: E402

COVER_SIZE = (1400, 933)

# Wikimedia direct upload URLs
COVER_URLS = {
    "jokbal": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Korean_cuisine-Jokbal-02.jpg",
    "milmyeon": "https://upload.wikimedia.org/wikipedia/commons/4/4a/Busan_Milmyeon_20200522_001.jpg",
    "yukhoe": "https://upload.wikimedia.org/wikipedia/commons/8/8e/Yukhoe_in_Gwangjang_Market%2C_Seoul.jpg",
}

# Naver place for nakgopsae dish cover (용호동낙지 북창점 — 낙곱새)
NAKGOPSAE_COVER_PLACE = "1346592242"

SHOPPING_IMAGES = {
    "convenience": "https://upload.wikimedia.org/wikipedia/commons/8/8a/Expo_2012_Convenience_Store_GS25.JPG",
    "promo": "https://upload.wikimedia.org/wikipedia/commons/9/9e/%EC%83%88%EC%9A%B0%EA%B9%A1_%EB%B8%94%EB%9E%99%2C_%EC%98%A4%EB%A6%AC%EC%A7%80%EB%84%90_%EC%83%88%EC%9A%B0%EA%B9%A1.jpg",
}

SHOPPING_KO = {
    "convenienceTitle": "편의점 쇼핑",
    "convenienceLead": "간식만 사러 가면 손해 — 식사·생활용품·우산까지",
    "convenience1": "CU·GS25·세븐일레븐 등이 골목마다 있습니다. 도시락·삼각김밥·컵라면·음료는 숙소·관광 중 간단히 해결할 때 유용해요.",
    "convenience2": "우산·세면도구·충전기·밴드·파스 같은 생활용품도 24시간 살 수 있습니다. 약이 필요하면 약국을, 처방·전문 상담이 필요한 약은 반드시 약사에게 물어보세요.",
    "convenience3": "인기 조합·시즌 메뉴는 사이트의 편의점 가이드(pages/convenience-store/)에서 더 자세히 볼 수 있어요. 여기서는 쇼핑 관점의 핵심만 정리합니다.",
    "promoTitle": "2+1·1+1 행사, 현명하게 쓰기",
    "promoLead": "세 개 사서 두 개 값 — 여행 중엔 ‘필요한 만큼만’이 포인트",
    "promo1": "2+1(1+1)은 같은 상품 3개(2개)를 담으면 2개(1개) 가격만 내는 행사입니다. 음료·과자·아이스크림·컵라면 등에 자주 붙어요. ‘2+1’·‘1+1’·‘N+1’ 스티커를 먼저 확인하세요.",
    "promo2": "여행자에게 잘 맞는 경우: 같은 날 마실 음료, 숙소에서 나눠 먹을 간식, 다음날 아침 도시락·우유 등 ‘곧 소비할 것’. 반대로 유통기한이 짧거나 냉장 보관이 필요한데 숙소 냉장고가 없으면 손해일 수 있어요.",
    "promo3": "맛·브랜드를 모를 때는 행사품을 무리하게 세 개 담기보다, 하나만 사서 맛본 뒤 다시 오는 편이 낫습니다. 짐·기내 반입 규정도 생각해 두세요.",
    "promo4": "편의점마다 행사 품목이 다릅니다. 계산대 앞 ‘행사 코너’·진열대 노란 스티커·앱(포인트/쿠폰)을 함께 보면 놓치기 어렵습니다.",
}

TIPS_TAB_KO = {
    "tabConvenienceShop": "편의점",
    "tabPromo": "2+1·행사",
}

DISHES = [
    {
        "kind": "meals",
        "slug": "yukhoe",
        "emoji": "🥩",
        "texts": {
            "ko": {
                "title": "육회",
                "desc": "간장·참기름·배와 함께 즐기는 신선한 쇠고기 회",
                "about": "육회는 신선한 쇠고기(주로 우육)를 가늘게 썰어 간장·설탕·참기름·마늘 등으로 양념한 한식입니다. 배·계란 노른자·잣을 곁들이면 달콤하고 고소한 맛이 살아납니다. 술안주·비빔밥 토핑으로도 사랑받아요.",
            },
        },
        "shops": [
            {
                "slug": "buchon-yukhoe",
                "name": "부촌육회",
                "place_id": "36428555",
                "menu_hint": "육회",
            },
            {
                "slug": "yukhoe-jamaejip",
                "name": "육회자매집",
                "place_id": "12795594",
                "menu_hint": "육회",
            },
        ],
    },
    {
        "kind": "desserts",
        "slug": "toast",
        "emoji": "🍞",
        "texts": {
            "ko": {
                "title": "토스트",
                "desc": "길거리 토스트·에그드랍·이삭토스트 스타일",
                "about": "한국식 토스트(길거리 토스트)는 달콤한 소스와 계란·양배추·햄·치즈를 넣어 철판에 구운 빵 샌드위치입니다. 에그드랍·이삭토스트 같은 체인은 관광객에게도 아침·간식으로 인기예요.",
            },
        },
        "shops": [
            {
                "slug": "eggdrop-gangnam",
                "name": "에그드랍 강남본점",
                "place_id": "1023881187",
                "menu_hint": "에그 샌드",
            },
            {
                "slug": "isaac-toast-gwanghwamun",
                "name": "이삭토스트 광화문점",
                "place_id": "1448519199",
                "menu_hint": "토스트",
            },
        ],
    },
]


def _resize_jpeg(path: Path) -> str:
    if not path.is_file():
        return f"cover missing: {path}"
    try:
        from PIL import Image

        with Image.open(path) as im:
            im = im.convert("RGB")
            if im.size != COVER_SIZE:
                im = im.resize(COVER_SIZE, Image.Resampling.LANCZOS)
            im.save(path, "JPEG", quality=88, optimize=True)
        return f"cover resized: {path.name}"
    except Exception as exc:  # noqa: BLE001
        return f"cover resize failed: {exc}"


def _download_cover(path: Path, url: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if download_image_to(path, url):
        print(" ", _resize_jpeg(path))
        return True
    return False


def _translate_all(ko: str, status: BatchStatus) -> dict[str, str]:
    out = {"ko": ko}
    for lang in i18n_store.LANGS:
        if lang == "ko":
            continue
        out[lang] = translate_text(ko, lang, status=status)
        time.sleep(0.05)
    return out


def _body_blocks(ko_paragraphs: list[str], status: BatchStatus, image_src: str) -> list[dict]:
    blocks: list[dict] = [{"type": "image", "src": image_src}]
    for para in ko_paragraphs:
        langs = _translate_all(para, status)
        blk = _text_block_from_langs(langs)
        if blk:
            blocks.append(blk)
    return blocks


def patch_shopping_i18n() -> None:
    status = BatchStatus()

    def tr(ko: str, lang: str) -> str:
        if lang == "ko":
            return ko
        return translate_text(ko, lang, status=status)

    # Build KO bodies first
    convenience_body = _body_blocks(
        [
            SHOPPING_KO["convenience1"],
            SHOPPING_KO["convenience2"],
            SHOPPING_KO["convenience3"],
        ],
        status,
        "Images/shopping/convenience.jpg",
    )
    promo_body = _body_blocks(
        [
            SHOPPING_KO["promo1"],
            SHOPPING_KO["promo2"],
            SHOPPING_KO["promo3"],
            SHOPPING_KO["promo4"],
        ],
        status,
        "Images/shopping/promo.jpg",
    )

    for lang in i18n_store.LANGS:
        path = ROOT / "i18n" / "pages" / "shopping" / f"{lang}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        shopping = data.setdefault("shopping", {})
        for key, ko_val in SHOPPING_KO.items():
            if key.endswith("Body"):
                continue
            shopping[key] = tr(ko_val, lang)

        if lang == "ko":
            shopping["convenienceBody"] = convenience_body
            shopping["promoBody"] = promo_body
        else:
            def translate_body(ko_blocks: list[dict]) -> list[dict]:
                out: list[dict] = []
                for blk in ko_blocks:
                    if blk.get("type") == "image":
                        out.append(dict(blk))
                        continue
                    src = (blk.get("ko") or "").strip()
                    out.append(_text_block_from_langs(_translate_all(src, status)))
                return out

            shopping["convenienceBody"] = translate_body(convenience_body)
            shopping["promoBody"] = translate_body(promo_body)

        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    for key, ko_val in TIPS_TAB_KO.items():
        for lang in i18n_store.LANGS:
            path = ROOT / "i18n" / "pages" / "travel-tips" / f"{lang}.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            tips = data.setdefault("tips", {})
            tips[key] = tr(ko_val, lang)
            if lang == "ko":
                tips["catShoppingIntro"] = (
                    "편의점·2+1 행사·올리브영·다이소·면세·시장 팁을 이 안에서 바로 확인하세요. (별도 페이지 이동 없음)"
                )
            else:
                tips["catShoppingIntro"] = tr(
                    "편의점·2+1 행사·올리브영·다이소·면세·시장 팁을 이 안에서 바로 확인하세요. (별도 페이지 이동 없음)",
                    lang,
                )
            path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
    print("shopping + travel-tips i18n patched")


def patch_shopping_images() -> None:
    img_dir = ROOT / "Images" / "shopping"
    img_dir.mkdir(parents=True, exist_ok=True)
    for name, url in SHOPPING_IMAGES.items():
        dest = img_dir / f"{name}.jpg"
        if _download_cover(dest, url):
            print(f"  shopping image: {name}.jpg")
        else:
            print(f"  WARN: {name}.jpg download failed")


def patch_before_trip_html() -> None:
    path = ROOT / "pages" / "before-trip" / "index.html"
    html = path.read_text(encoding="utf-8")
    if 'data-prep-go="shopping/convenience"' in html:
        print("before-trip HTML already has shopping/convenience")
        return

    toc_insert = """                  <li><button type="button" class="prep-map__child" data-prep-go="shopping/convenience"><span data-i18n="tips.tabConvenienceShop">편의점</span></button></li>
                  <li><button type="button" class="prep-map__child" data-prep-go="shopping/promo"><span data-i18n="tips.tabPromo">2+1·행사</span></button></li>
"""
    html = html.replace(
        '                  <li><button type="button" class="prep-map__child" data-prep-go="shopping/olive"',
        toc_insert
        + '                  <li><button type="button" class="prep-map__child" data-prep-go="shopping/olive"',
    )

    articles = """
              <article class="prep-map__sub" data-prep-sub="convenience" hidden>
                <div class="prep-map__sub-inner guide-article tip-article">
                  <h2 data-i18n="shopping.convenienceTitle">편의점 쇼핑</h2>
                  <p class="tip-mistake" data-i18n="shopping.convenienceLead"></p>
                  <div class="content-body" data-content-body data-body-path="shopping.convenienceBody"></div>
                  <div data-content-body-fallback>
                    <p data-i18n="shopping.convenience1"></p>
                    <p data-i18n="shopping.convenience2"></p>
                    <p data-i18n="shopping.convenience3"></p>
                  </div>
                </div>
              </article>
              <article class="prep-map__sub" data-prep-sub="promo" hidden>
                <div class="prep-map__sub-inner guide-article tip-article">
                  <h2 data-i18n="shopping.promoTitle">2+1·1+1 행사</h2>
                  <p class="tip-mistake" data-i18n="shopping.promoLead"></p>
                  <div class="content-body" data-content-body data-body-path="shopping.promoBody"></div>
                  <div data-content-body-fallback>
                    <p data-i18n="shopping.promo1"></p>
                    <p data-i18n="shopping.promo2"></p>
                    <p data-i18n="shopping.promo3"></p>
                    <p data-i18n="shopping.promo4"></p>
                  </div>
                </div>
              </article>
"""
    html = html.replace(
        '              <article class="prep-map__sub" data-prep-sub="olive" hidden>',
        articles + '              <article class="prep-map__sub" data-prep-sub="olive" hidden>',
    )
    path.write_text(html, encoding="utf-8", newline="\n")
    print("before-trip HTML patched")


def patch_content_body_slots() -> None:
    path = ROOT / "tool" / "lib" / "content_body.py"
    text = path.read_text(encoding="utf-8")
    if "convenienceBody" in text and '"promoBody"' in text:
        return
    old = """SHOPPING_SLOTS: list[BodySlot] = [
    BodySlot("oliveBody", "뷰티·올리브영", "shopping", "olive", group="olive"),
"""
    new = """SHOPPING_SLOTS: list[BodySlot] = [
    BodySlot("convenienceBody", "편의점", "shopping", "convenience", group="convenience"),
    BodySlot("promoBody", "2+1·행사", "shopping", "promo", group="promo"),
    BodySlot("oliveBody", "뷰티·올리브영", "shopping", "olive", group="olive"),
"""
    if old in text:
        path.write_text(text.replace(old, new), encoding="utf-8", newline="\n")
        print("content_body SHOPPING_SLOTS updated")


def fix_meal_covers() -> None:
    for slug, url in COVER_URLS.items():
        cover = dish_cover_path(slug, "meals")
        if _download_cover(cover, url):
            print(f"  cover meals/{slug}")

    # nakgopsae: try Naver scrape
    cover = dish_cover_path("nakgopsae", "meals")
    cover.parent.mkdir(parents=True, exist_ok=True)
    scraped = scrape_naver_place(NAKGOPSAE_COVER_PLACE)
    img_url = (scraped or {}).get("imageUrl") or ""
    if not img_url:
        photos = (scraped or {}).get("photos") or []
        if photos and isinstance(photos[0], str):
            img_url = photos[0]
    if img_url and download_image_to(cover, img_url):
        print(f"  cover nakgopsae from Naver place {NAKGOPSAE_COVER_PLACE}")
        print(" ", _resize_jpeg(cover))
    else:
        print("  WARN: nakgopsae cover scrape failed — try manual")


def ensure_dish(dish: dict) -> None:
    slug = dish["slug"]
    page = ROOT / "pages" / "foods" / dish["kind"] / slug / "index.html"
    if page.exists():
        print(f"[skip dish] {slug}")
        return
    texts = dict(dish["texts"])
    for lang in ("en", "ja", "zh", "zh-Hant", "vi", "th", "ru"):
        texts.setdefault(lang, {})
    notes, st = content.create_dish(
        dish["kind"], slug, texts, emoji=dish["emoji"]
    )
    for n in notes:
        print(" ", n)
    for n in st.note_lines():
        print(" ", n)


def ensure_shop(shop: dict) -> None:
    from lib.scaffold import shop_page_path

    slug = shop["slug"]
    page = shop_page_path(shop["kind"], shop["dish"], slug)
    if page.exists():
        print(f"[skip shop] {slug}")
        return
    place_url = naver_canonical_place_url(shop["place_id"])
    texts = {
        "ko": {
            "name": shop["name"],
            "location": "",
            "menu": shop.get("menu_hint") or "",
            "price": "",
            "tip": "",
            "about": "",
        },
        "en": {},
        "ja": {},
        "zh": {},
    }
    notes, status = content.create_shop(
        shop["kind"],
        shop["dish"],
        slug,
        texts,
        place_url=place_url,
        source_type="naver",
        fetch_preview=True,
    )
    print(f"[created shop] {slug}")
    for n in notes[:8]:
        print(" ", n)


def enrich_and_translate_shops(dish: dict) -> None:
    bundle = i18n_store.load_all()
    for shop in dish.get("shops") or []:
        slug = shop["slug"]
        place_id = str(shop["place_id"])
        restaurants = bundle["ko"].setdefault("restaurants", {})
        entry = restaurants.get(slug) or {
            "name": shop["name"],
            "placeId": place_id,
            "placeUrl": naver_canonical_place_url(place_id),
            "sourceType": "naver",
        }
        entry["placeId"] = place_id
        entry["placeUrl"] = naver_canonical_place_url(place_id)
        entry["sourceType"] = "naver"
        updated, notes, st = enrich_one(slug, entry, force=True)
        apply_to_bundle(bundle, slug, updated)
        restaurants[slug] = updated
        print(f"[enrich] {slug} placeId={place_id}")
        sync_shop_page_visual(dish["kind"], dish["slug"], slug)
        print(" ", _resize_jpeg(shop_photo_path(dish["kind"], dish["slug"], slug)))
        time.sleep(0.8)

    st = BatchStatus()
    for shop in dish.get("shops") or []:
        slug = shop["slug"]
        ko_entry = (bundle["ko"].get("restaurants") or {}).get(slug) or {}
        texts = {
            "ko": {f: str(ko_entry.get(f) or "") for f in content.SHOP_TEXT_FIELDS},
            "en": {},
            "ja": {},
            "zh": {},
        }
        filled = fill_scalar_texts(
            texts, content.SHOP_TEXT_FIELDS, force=True, status=st
        )
        for lang in i18n_store.LANGS:
            restaurants_lang = bundle[lang].setdefault("restaurants", {})
            entry = dict(restaurants_lang.get(slug) or {})
            if lang != "ko":
                for f in content.SHOP_TEXT_FIELDS:
                    if filled.get(lang, {}).get(f):
                        entry[f] = filled[lang][f]
            ko = (bundle["ko"].get("restaurants") or {}).get(slug) or {}
            for key in (
                "placeUrl",
                "mapsUrl",
                "mapsEmbedUrl",
                "mapsProvider",
                "sourceType",
                "previewTitle",
                "previewImage",
                "phone",
                "hours",
                "placeId",
                "menuItems",
                "category",
                "score",
                "lat",
                "lng",
                "region",
            ):
                if key in ko:
                    entry[key] = ko[key]
            entry.pop("photos", None)
            entry.pop("gallery", None)
            items = entry.get("menuItems")
            if isinstance(items, list):
                for it in items:
                    if isinstance(it, dict):
                        it.pop("image", None)
            restaurants_lang[slug] = entry

        menu_st = BatchStatus()
        items = list(ko_entry.get("menuItems") or [])
        if items:
            migrated = migrate_menu_items(items, menu_st)
            ko_entry["menuItems"] = migrated
            sig = next((m for m in migrated if m.get("recommend")), migrated[0])
            sig_name = sig.get("name") if isinstance(sig.get("name"), dict) else {}
            if isinstance(sig_name, dict) and sig_name.get("ko"):
                ko_entry["menu"] = sig_name["ko"]
            for lang in i18n_store.LANGS:
                other = dict(
                    (bundle[lang].get("restaurants") or {}).get(slug) or {}
                )
                other["menuItems"] = migrated
                if lang != "ko" and isinstance(sig_name, dict) and sig_name.get(lang):
                    other["menu"] = sig_name[lang]
                bundle[lang].setdefault("restaurants", {})[slug] = {
                    **(bundle[lang].get("restaurants") or {}).get(slug, {}),
                    **other,
                }

    i18n_store.save_all(bundle)


def patch_dish_hub_cards(dish: dict) -> None:
    """Replace emptyPlaces with shopsHelp on dish hub after shops exist."""
    hub = ROOT / "pages" / "foods" / dish["kind"] / dish["slug"] / "index.html"
    if not hub.is_file():
        return
    html = hub.read_text(encoding="utf-8")
    if "common.emptyPlaces" in html and "card-grid" in html:
        html = html.replace(
            '<p class="tabs-help" data-i18n="common.shopsComing"></p>\n'
            '    <p data-i18n="common.emptyPlaces">등록된 곳이 아직 없습니다.</p>',
            '<p class="tabs-help" data-i18n="common.shopsHelp"></p>',
        )
        hub.write_text(html, encoding="utf-8", newline="\n")
        print(f"  hub {dish['slug']}: emptyPlaces → shopsHelp")


def download_dish_cover(dish: dict) -> None:
    slug = dish["slug"]
    if slug == "toast":
        # Prefer shop cover from egg drop
        cover = dish_cover_path(slug, dish["kind"])
        shop_cover = shop_photo_path(
            dish["kind"], dish["slug"], dish["shops"][0]["slug"]
        )
        if shop_cover.is_file():
            cover.parent.mkdir(parents=True, exist_ok=True)
            cover.write_bytes(shop_cover.read_bytes())
            print(" ", _resize_jpeg(cover))
        return
    if slug == "yukhoe":
        cover = dish_cover_path(slug, dish["kind"])
        _download_cover(cover, COVER_URLS["yukhoe"])


def main() -> int:
    print("=== shopping images ===")
    patch_shopping_images()
    print("=== shopping i18n ===")
    patch_shopping_i18n()
    print("=== before-trip HTML ===")
    patch_before_trip_html()
    patch_content_body_slots()

    print("=== meal cover fixes ===")
    fix_meal_covers()

    print("=== create dishes ===")
    for dish in DISHES:
        ensure_dish(dish)

    print("=== create shops ===")
    for dish in DISHES:
        for shop in dish.get("shops") or []:
            shop["kind"] = dish["kind"]
            shop["dish"] = dish["slug"]
            ensure_shop(shop)
            time.sleep(0.3)

    print("=== enrich shops ===")
    for dish in DISHES:
        enrich_and_translate_shops(dish)
        patch_dish_hub_cards(dish)
        download_dish_cover(dish)

    print(i18n_store.build_bundle())
    print(content.rebuild_food_recommend_catalog())
    summary = bump_asset_version()
    print(f"cache → {summary['version']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
