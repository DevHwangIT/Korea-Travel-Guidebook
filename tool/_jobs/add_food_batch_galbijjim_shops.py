# -*- coding: utf-8 -*-
"""Food batch: clean intros, fix covers, add shops, new galbijjim dish.

- Clean restaurant about (rating/amenity scrapes) across GUIDE_LANGS
- Replace seogil-sikdang + doenjang-jjigae covers
- Add budae / gopchang / gamjatang / bread / dakgalbi shops
- New meals dish galbijjim + 3 shops
- Enrich, translate, recommend catalog, cache bump

Usage:
  python tool/add_food_batch_galbijjim_shops.py
"""
from __future__ import annotations

import json
import ssl
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen

TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from clean_shop_intros import clean_bundle, editorial_about, clean_about_text  # noqa: E402
from lib import content, i18n_store  # noqa: E402
from lib.images import dish_cover_path, shop_photo_path  # noqa: E402
from lib.place_scrape import (  # noqa: E402
    download_image_to,
    naver_canonical_place_url,
    resolve_naver_search,
    scrape_naver_place,
)
from lib.scaffold import (  # noqa: E402
    dish_dir,
    insert_before_card_grid_close,
    render_shop_page,
    shop_card_html,
    shop_page_path,
    sync_shop_page_visual,
)
from lib.translate import BatchStatus, fill_scalar_texts  # noqa: E402
from migrate_menu_i18n import migrate_menu_items  # noqa: E402
from migrate_shop_enrich import apply_to_bundle, enrich_one  # noqa: E402

COVER_SIZE = (1400, 933)
_SSL_CTX = ssl._create_unverified_context()
_UA = "Mozilla/5.0 (compatible; KoreaTravelGuide/1.0; +https://korea-guidebook.cloud)"

NEW_DISH = {
    "kind": "meals",
    "slug": "galbijjim",
    "emoji": "🍖",
    "title": "갈비찜",
    "desc": "소갈비를 달콤짭짤하게 조린 한식 찜 요리",
    "about": (
        "갈비찜은 소갈비를 간장·설탕·마늘 양념으로 부드럽게 조린 "
        "한국의 대표 찜 요리입니다. 가족 모임·명절 상에도 자주 오르며, "
        "밥과 함께 든든한 한 끼로 즐기기 좋습니다."
    ),
    "cover": "https://commons.wikimedia.org/wiki/Special:FilePath/Galbi-jjim_1.jpg",
}

COVER_FIXES = [
    {
        "label": "doenjang-jjigae dish",
        "path": dish_cover_path("doenjang-jjigae", "meals"),
        "url": "https://commons.wikimedia.org/wiki/Special:FilePath/Doenjang-jjigae_4.jpg",
    },
    {
        "label": "seogil-sikdang cover",
        "path": shop_photo_path("meals", "ganjang-gejang", "seogil-sikdang"),
        # Prefer Commons food photo — Naver OG/photos often return Smart Store shots
        "url": "https://commons.wikimedia.org/wiki/Special:FilePath/Korean_seafood-Ganjang_gejang-01.jpg",
        "force_commons": True,
    },
]

SHOPS = [
    # —— 부대찌개 ——
    {
        "kind": "meals",
        "dish": "budae-jjigae",
        "slug": "daewoo-budae-jjigae",
        "name": "대우부대찌개",
        "place_id": "11723756",
        "menu_hint": "부대찌개",
        "about": "대우부대찌개는 푸짐한 햄·소시지 부대찌개로 알려진 현지 맛집입니다.",
    },
    {
        "kind": "meals",
        "dish": "budae-jjigae",
        "slug": "dabuzzi",
        "name": "다부찌",
        "place_id": "37406362",  # resolved via Naver search
        "search": "다부찌 부대찌개",
        "menu_hint": "부대찌개",
        "about": "다부찌는 서울대·대학동 고시촌에서 가성비 부대찌개로 유명한 곳입니다.",
    },
    {
        "kind": "meals",
        "dish": "budae-jjigae",
        "slug": "bada-sikdang",
        "name": "바다식당",
        "place_id": "11724665",
        "menu_hint": "부대찌개",
        "about": "바다식당은 김치와 햄이 잘 어우러진 부대찌개로 알려진 식당입니다.",
    },
    {
        "kind": "meals",
        "dish": "budae-jjigae",
        "slug": "deoksujeong",
        "name": "덕수정",
        "place_id": "13006904",
        "menu_hint": "부대찌개",
        "about": "덕수정은 진한 국물의 부대찌개로 사랑받는 오래된 맛집입니다.",
    },
    {
        "kind": "meals",
        "dish": "budae-jjigae",
        "slug": "huijeong-sikdang",
        "name": "희정식당",
        "place_id": "11888725",
        "menu_hint": "부대찌개",
        "about": "희정식당은 푸짐한 사리와 함께 즐기는 부대찌개 집으로 유명합니다.",
    },
    # —— 곱창 ——
    {
        "kind": "meals",
        "dish": "gopchang",
        "slug": "pyeonghwa-yeonnam",
        "name": "평화연남",
        "place_id": "1874989869",
        "menu_hint": "곱창",
        "about": "평화연남은 연남동에서 곱창·막창을 즐기는 분위기의 고깃집입니다.",
    },
    # —— 감자탕 ——
    {
        "kind": "meals",
        "dish": "gamjatang",
        "slug": "somunnan-seongsu-gamjatang",
        "name": "소문난성수감자탕",
        "place_id": "11721256",
        "menu_hint": "감자탕",
        "about": "소문난성수감자탕은 뼈에 붙은 고기가 푸짐한 성수 감자탕 맛집입니다.",
    },
    # —— 빵·베이커리 ——
    {
        "kind": "desserts",
        "dish": "bread",
        "slug": "sowoldang",
        "name": "소월당",
        "place_id": "2047914123",
        "menu_hint": "빵",
        "about": "소월당은 정성스럽게 구운 빵과 디저트로 알려진 베이커리입니다.",
    },
    {
        "kind": "desserts",
        "dish": "bread",
        "slug": "sungsimdang",
        "name": "성심당",
        "place_id": "11871325",
        "menu_hint": "튀김소보로",
        "about": (
            "성심당은 대전의 대표 베이커리로, 튀김소보로 등 "
            "시그니처 빵을 사려는 줄이 길게 이어지는 곳입니다."
        ),
    },
    # —— 갈비찜 ——
    {
        "kind": "meals",
        "dish": "galbijjim",
        "slug": "asojeong",
        "name": "아소정",
        "place_id": "11603394",
        "menu_hint": "갈비찜",
        "about": "아소정은 부드러운 소갈비찜으로 알려진 한식당입니다.",
    },
    {
        "kind": "meals",
        "dish": "galbijjim",
        "slug": "gangnam-myeonok",
        "name": "강남면옥",
        "place_id": "11845608",
        "menu_hint": "갈비찜",
        "about": "강남면옥은 갈비찜·냉면 등 한식을 함께 즐길 수 있는 식당입니다.",
    },
    {
        "kind": "meals",
        "dish": "galbijjim",
        "slug": "seongbukdong-myeonokjip",
        "name": "성북동면옥집",
        "place_id": "37101627",
        "menu_hint": "갈비찜",
        "about": "성북동면옥집은 성북동에서 갈비찜과 면 요리를 내는 맛집입니다.",
    },
    # —— 닭갈비 ——
    {
        "kind": "meals",
        "dish": "dakgalbi",
        "slug": "dakeuroga-apgujeong",
        "name": "닭으로가 압구정본점",
        "place_id": "11710160",
        "menu_hint": "닭갈비",
        "about": "닭으로가 압구정본점은 양념 닭갈비로 유명한 압구정 맛집입니다.",
    },
    {
        "kind": "meals",
        "dish": "dakgalbi",
        "slug": "ogeunnae-dakgalbi",
        "name": "오근내 닭갈비",
        "place_id": "18168200",
        "menu_hint": "닭갈비",
        "about": "오근내 닭갈비는 춘천식 양념 닭갈비로 잘 알려진 체인·맛집입니다.",
    },
    {
        "kind": "meals",
        "dish": "dakgalbi",
        "slug": "sanggyedong-wonjo-dongsunjip",
        "name": "상계동 원조닭갈비 동순집",
        "place_id": "1218804796",
        "menu_hint": "닭갈비",
        "about": "동순집은 상계동에서 원조 닭갈비로 오랜 단골을 둔 식당입니다.",
    },
    {
        "kind": "meals",
        "dish": "dakgalbi",
        "slug": "sindorim-ido-sikdang",
        "name": "신도림 이도식당",
        "place_id": "75209465",  # resolved via Naver search
        "search": "신도림 이도식당",
        "menu_hint": "닭갈비",
        "about": (
            "신도림 이도식당은 철판 닭갈비·눈꽃치즈 닭갈비로 "
            "신도림역 인근에서 줄 서는 맛집입니다."
        ),
    },
    {
        "kind": "meals",
        "dish": "dakgalbi",
        "slug": "yangju-geosigi-dakgalbi",
        "name": "양주 거시기닭갈비",
        "place_id": "18085815",
        "menu_hint": "닭갈비",
        "about": "양주 거시기닭갈비는 푸짐한 철판 닭갈비로 알려진 경기 북부 맛집입니다.",
    },
]


def _safe_print(*args: object) -> None:
    try:
        print(*args)
    except UnicodeEncodeError:
        print(*(str(a).encode("utf-8", "replace").decode("utf-8") for a in args))


def download_commons(dest: Path, url: str) -> bool:
    """Download image; retry with unverified SSL for Wikimedia."""
    if download_image_to(dest, url):
        return True
    try:
        req = Request(url, headers={"User-Agent": _UA}, method="GET")
        with urlopen(req, context=_SSL_CTX, timeout=30) as resp:
            data = resp.read(12_000_000)
        if not data or len(data) < 1000:
            return False
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return True
    except Exception as exc:  # noqa: BLE001
        _safe_print(f"  commons download fail: {exc}")
        return False


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
        return f"cover resized {COVER_SIZE[0]}x{COVER_SIZE[1]}: {path.name}"
    except Exception as exc:  # noqa: BLE001
        return f"cover resize failed: {exc}"


def _looks_like_product_shot(path: Path) -> bool:
    """Heuristic: very small or Smart-Store-ish screenshots are bad covers."""
    if not path.is_file():
        return True
    # Force replace for known bad seogil cover regardless of size
    return path.stat().st_size < 40_000


def fix_covers() -> list[str]:
    notes: list[str] = []
    for item in COVER_FIXES:
        path: Path = item["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        used = ""
        if not item.get("force_commons") and item.get("prefer_naver_food") and item.get(
            "naver_place_id"
        ):
            scraped = scrape_naver_place(str(item["naver_place_id"]), force=True)
            photos = list(scraped.get("photos") or [])
            image = str(scraped.get("imageUrl") or "")
            candidates = photos[:6] + ([image] if image else [])
            for url in candidates:
                if not url:
                    continue
                low = url.lower()
                if "smartstore" in low or "shopping" in low:
                    continue
                if download_image_to(path, url) or download_commons(path, url):
                    # Reject tiny / UI-screenshot-like files
                    if path.is_file() and path.stat().st_size > 80_000:
                        used = url
                        notes.append(f"{item['label']}: naver photo → {path}")
                        break
                    path.unlink(missing_ok=True)
        if not used:
            # Try primary + fallback commons names for gejang
            urls = [item["url"]]
            if "gejang" in item["label"] or "seogil" in item["label"]:
                urls.extend(
                    [
                        "https://commons.wikimedia.org/wiki/Special:FilePath/Ganjang-gejang.jpg",
                        "https://commons.wikimedia.org/wiki/Special:FilePath/Korean.cuisine-Ganjang_gejang-01.jpg",
                    ]
                )
            for url in urls:
                if download_commons(path, url):
                    used = url
                    notes.append(f"{item['label']}: commons → {path.name} ({url.split('/')[-1]})")
                    break
            if not used:
                notes.append(f"WARN: cover failed {item['label']}")
                continue
        notes.append(_resize_jpeg(path))
    return notes


def ensure_galbijjim() -> list[str]:
    notes: list[str] = []
    d = NEW_DISH
    slug = d["slug"]
    page = dish_dir(d["kind"], slug) / "index.html"
    if page.exists():
        notes.append(f"[skip dish] {slug} exists")
    else:
        texts = {
            "ko": {"title": d["title"], "desc": d["desc"], "about": d["about"]},
            "en": {},
            "ja": {},
            "zh": {},
        }
        cnotes, st = content.create_dish(d["kind"], slug, texts, emoji=d["emoji"])
        notes.append(f"[created dish] {slug}")
        notes.extend(cnotes)
        notes.extend(st.note_lines())

    cover = dish_cover_path(slug, d["kind"])
    if not cover.is_file() or cover.stat().st_size < 20_000:
        if download_commons(cover, d["cover"]):
            notes.append(f"dish cover downloaded: {slug}")
            notes.append(_resize_jpeg(cover))
        else:
            notes.append(f"WARN: dish cover failed: {slug}")
    else:
        notes.append(_resize_jpeg(cover))
    return notes


def patch_fallbacks() -> list[str]:
    notes: list[str] = []
    cpath = TOOL_DIR / "lib" / "content.py"
    text = cpath.read_text(encoding="utf-8")
    if '"galbijjim"' not in text:
        text = text.replace(
            '"dakgangjeong",\n',
            '"dakgangjeong",\n    "galbijjim",\n',
            1,
        )
        # gamjatang may already be folder-only; ensure fallback if missing
        if '"gamjatang"' not in text:
            text = text.replace(
                '"gopchang",\n',
                '"gopchang",\n    "gamjatang",\n',
                1,
            )
        cpath.write_text(text, encoding="utf-8", newline="\n")
        notes.append("content.py fallback +galbijjim")

    spath = TOOL_DIR / "lib" / "sections.py"
    stext = spath.read_text(encoding="utf-8")
    if '"galbijjim"' not in stext:
        stext = stext.replace(
            '"doenjang-jjigae": "된장찌개",\n',
            '"doenjang-jjigae": "된장찌개",\n        "galbijjim": "갈비찜",\n',
            1,
        )
        spath.write_text(stext, encoding="utf-8", newline="\n")
        notes.append("sections.py +galbijjim")

    tags_path = ROOT / "data" / "food" / "recommend-tags.json"
    data = json.loads(tags_path.read_text(encoding="utf-8"))
    items = data.setdefault("items", {})
    if "galbijjim" not in items:
        items["galbijjim"] = {
            "tags": ["meat", "warm", "hearty", "mild", "nonspicy"]
        }
        tags_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        notes.append("recommend-tags +galbijjim")

    cat = TOOL_DIR / "build-food-recommend-catalog.py"
    ct = cat.read_text(encoding="utf-8")
    if "galbijjim" not in ct:
        ct = ct.replace(
            r'(re.compile(r"doenjang"), ["soup", "warm", "mild"]),',
            r'(re.compile(r"doenjang"), ["soup", "warm", "mild"]),\n'
            r'    (re.compile(r"galbijjim|galbi-jjim"), ["meat", "warm", "hearty"]),',
            1,
        )
        cat.write_text(ct, encoding="utf-8", newline="\n")
        notes.append("catalog heuristics +galbijjim")
    return notes


def _ensure_page_for_existing_i18n(shop: dict, place_url: str) -> list[str]:
    """Create HTML + hub card when restaurants.{slug} already exists."""
    notes: list[str] = []
    kind, dish, slug = shop["kind"], shop["dish"], shop["slug"]
    page = shop_page_path(kind, dish, slug)
    if page.exists():
        return [f"[skip create] {slug}"]
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(
        render_shop_page(kind, dish, slug),
        encoding="utf-8",
        newline="\n",
    )
    notes.append(f"[page from i18n] {page.relative_to(ROOT).as_posix()}")
    index = dish_dir(kind, dish) / "index.html"
    if index.is_file():
        html = index.read_text(encoding="utf-8")
        if f"./{slug}/" not in html and f"restaurants.{slug}." not in html:
            html = insert_before_card_grid_close(
                html, shop_card_html(kind, dish, slug)
            )
            index.write_text(html, encoding="utf-8", newline="\n")
            notes.append(f"hub card +{slug}")
    bundle = i18n_store.load_all()
    for lang in i18n_store.LANGS:
        restaurants = bundle[lang].setdefault("restaurants", {})
        entry = dict(restaurants.get(slug) or {})
        if place_url and not str(entry.get("placeUrl") or "").strip():
            entry["placeUrl"] = place_url
            entry["mapsUrl"] = place_url
            entry["sourceType"] = "naver"
        if shop.get("place_id"):
            entry["placeId"] = str(shop["place_id"])
        if lang == "ko":
            if shop.get("about") and not clean_about_text(
                str(entry.get("about") or "")
            ):
                entry["about"] = shop["about"]
            if shop.get("name") and not entry.get("name"):
                entry["name"] = shop["name"]
            if shop.get("menu_hint") and not entry.get("menu"):
                entry["menu"] = shop["menu_hint"]
        restaurants[slug] = entry
    i18n_store.save_all(bundle)
    return notes


def ensure_shop(shop: dict) -> list[str]:
    notes: list[str] = []
    slug = shop["slug"]
    place_id = str(shop.get("place_id") or "").strip()
    if not place_id and shop.get("search"):
        hit = resolve_naver_search(str(shop["search"]), force=True)
        place_id = str(hit.get("placeId") or "").strip()
        shop["place_id"] = place_id
        notes.append(
            f"resolved {shop['search']!r} → placeId={place_id} "
            f"name={hit.get('name')!r}"
        )
    if not place_id:
        notes.append(f"ERROR: no place id for {slug}")
        return notes

    place_url = naver_canonical_place_url(place_id)
    shop["place_url"] = place_url
    page = shop_page_path(shop["kind"], shop["dish"], slug)

    bundle = i18n_store.load_all()
    exists_i18n = slug in (bundle["ko"].get("restaurants") or {})

    if page.exists():
        notes.append(f"[skip create] {slug}")
        # Place id / URL stamped during enrich — avoid mid-loop save_all races
        return notes

    if exists_i18n:
        notes.extend(_ensure_page_for_existing_i18n(shop, place_url))
        return notes

    texts = {
        "ko": {
            "name": shop["name"],
            "location": "",
            "menu": shop.get("menu_hint") or "",
            "price": "",
            "tip": "",
            "about": shop.get("about") or "",
        },
        "en": {},
        "ja": {},
        "zh": {},
    }
    try:
        cnotes, status = content.create_shop(
            shop["kind"],
            shop["dish"],
            slug,
            texts,
            place_url=place_url,
            source_type="naver",
            fetch_preview=True,
        )
    except ValueError as exc:
        msg = str(exc)
        if "이미 있음" in msg or "already" in msg.lower():
            notes.append(f"[race] {slug}: {msg}")
            notes.extend(_ensure_page_for_existing_i18n(shop, place_url))
            return notes
        raise
    notes.append(f"[created] {slug}")
    notes.extend(cnotes)
    notes.extend(status.note_lines())
    return notes


def localize_scalars(bundle: dict, shops: list[dict]) -> BatchStatus:
    st = BatchStatus()
    for shop in shops:
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
    return st


def ensure_editorial_after_enrich(bundle: dict, shops: list[dict]) -> None:
    restaurants = bundle["ko"].setdefault("restaurants", {})
    for shop in shops:
        slug = shop["slug"]
        entry = restaurants.get(slug)
        if not isinstance(entry, dict):
            continue
        about = clean_about_text(str(entry.get("about") or ""))
        if not about:
            about = shop.get("about") or editorial_about(entry)
        entry["about"] = about


def main() -> int:
    # Drop accidental duplicate 다부찌 slug from earlier partial run
    try:
        for n in content.delete_shop("dabucci", delete_images=True):
            _safe_print("cleanup dabucci:", n)
    except Exception as exc:  # noqa: BLE001
        _safe_print(f"cleanup dabucci skip: {exc}")

    _safe_print("=== fix covers ===")
    for n in fix_covers():
        _safe_print(" ", n)

    _safe_print("=== ensure galbijjim dish ===")
    for n in ensure_galbijjim():
        _safe_print(" ", n)

    _safe_print("=== patch fallbacks / tags ===")
    for n in patch_fallbacks():
        _safe_print(" ", n)

    _safe_print("=== create shops ===")
    for shop in SHOPS:
        for n in ensure_shop(shop):
            _safe_print(" ", n)
        time.sleep(0.35)

    _safe_print("=== enrich ===")
    bundle = i18n_store.load_all()
    restaurants = bundle["ko"].setdefault("restaurants", {})
    enrich_stats: dict[str, str] = {}
    for i, shop in enumerate(SHOPS):
        slug = shop["slug"]
        place_id = str(shop.get("place_id") or "").strip()
        place_url = str(shop.get("place_url") or naver_canonical_place_url(place_id))
        entry = restaurants.get(slug) or {
            "name": shop["name"],
            "placeUrl": place_url,
            "sourceType": "naver",
            "placeId": place_id,
        }
        entry["placeUrl"] = place_url
        entry["placeId"] = place_id
        entry["sourceType"] = "naver"
        # Seed editorial so enrich won't leave empty about
        if shop.get("about") and not clean_about_text(str(entry.get("about") or "")):
            entry["about"] = shop["about"]
        _safe_print(f"[enrich] {slug} placeId={place_id}…")
        updated, notes, st = enrich_one(slug, entry, force=True)
        # Prefer our editorial if enrich about is empty/junk
        cleaned = clean_about_text(str(updated.get("about") or ""))
        if not cleaned:
            updated["about"] = shop.get("about") or editorial_about(updated)
        else:
            updated["about"] = cleaned
        apply_to_bundle(bundle, slug, updated)
        restaurants[slug] = updated
        enrich_stats[slug] = st
        _safe_print(f"  status={st}")
        for n in notes[:6]:
            _safe_print(" ", n)
        for n in sync_shop_page_visual(shop["kind"], shop["dish"], slug):
            _safe_print("  html:", n)
        cover = shop_photo_path(shop["kind"], shop["dish"], slug)
        _safe_print(" ", _resize_jpeg(cover))
        if i + 1 < len(SHOPS):
            time.sleep(0.9)

    ensure_editorial_after_enrich(bundle, SHOPS)
    i18n_store.save_all(bundle)
    bundle = i18n_store.load_all()

    _safe_print("=== clean ALL shop intros ===")
    stats = clean_bundle(bundle, slugs=None)
    i18n_store.save_all(bundle)
    _safe_print(
        f"  cleaned={stats['cleaned']} emptied={stats['emptied']} "
        f"editorial={stats['editorial']}"
    )

    bundle = i18n_store.load_all()
    _safe_print("=== translate new shop scalars ===")
    st = localize_scalars(bundle, SHOPS)
    for n in st.note_lines()[:20]:
        _safe_print(" ", n)

    _safe_print("=== menu i18n ===")
    menu_st = BatchStatus()
    for shop in SHOPS:
        slug = shop["slug"]
        ko_restaurants = bundle["ko"].setdefault("restaurants", {})
        entry = ko_restaurants.get(slug) or {}
        items = list(entry.get("menuItems") or [])
        if not items:
            _safe_print(f"[menu-i18n skip] {slug}")
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
        _safe_print(f"[menu-i18n] {slug}: {len(migrated)} items")

    i18n_store.save_all(bundle)
    _safe_print(i18n_store.build_bundle())
    _safe_print(content.rebuild_food_recommend_catalog())
    for n in menu_st.note_lines()[:10]:
        _safe_print(n)

    # Explicit rebuilds requested by user
    import subprocess

    for cmd in (
        [sys.executable, str(ROOT / "i18n" / "build-bundle.py")],
        [sys.executable, str(TOOL_DIR / "build-food-recommend-catalog.py")],
        [sys.executable, str(TOOL_DIR / "update-version.py")],
    ):
        _safe_print("run:", " ".join(cmd))
        subprocess.check_call(cmd, cwd=str(ROOT))

    from lib.cache_bust import read_version

    _safe_print(f"cache → {read_version()}")

    _safe_print("\n=== SUMMARY ===")
    for shop in SHOPS:
        slug = shop["slug"]
        page = shop_page_path(shop["kind"], shop["dish"], slug)
        _safe_print(
            f"{slug}: placeId={shop.get('place_id')} "
            f"status={enrich_stats.get(slug)} exists={page.exists()}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
