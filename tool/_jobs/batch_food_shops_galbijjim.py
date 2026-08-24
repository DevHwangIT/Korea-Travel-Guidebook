# -*- coding: utf-8 -*-
"""Clean shop intros, fix covers, add shops + galbijjim dish (Mar 2026 batch).

No commit/push — run locally then rebuild i18n/catalog/cache.
"""
from __future__ import annotations

import json
import re
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
from lib.images import dish_cover_path, shop_photo_path  # noqa: E402
from lib.place_scrape import (  # noqa: E402
    download_image_to,
    naver_canonical_place_url,
    resolve_naver_search,
    scrape_naver_place,
)
from lib.scaffold import (  # noqa: E402
    dish_dir,
    hub_index_path,
    shop_page_path,
    sync_shop_page_visual,
)
from lib.translate import BatchStatus, fill_scalar_texts  # noqa: E402
from migrate_menu_i18n import migrate_menu_items  # noqa: E402
from migrate_shop_enrich import apply_to_bundle, enrich_one  # noqa: E402

COVER_SIZE = (1400, 933)

# --- shops to add -----------------------------------------------------------
SHOPS: list[dict[str, Any]] = [
    # 부대찌개
    {
        "kind": "meals",
        "dish": "budae-jjigae",
        "slug": "daewoo-budae-jjigae",
        "name": "대우부대찌개",
        "place_id": "11723756",
        "menu_hint": "부대찌개",
        "about": "의정부의 대표 부대찌개 맛집입니다. 햄·소시지·라면사리가 푸짐한 국물을 뚝배기에 내줍니다.",
    },
    {
        "kind": "meals",
        "dish": "budae-jjigae",
        "slug": "dabuzzi",
        "name": "다부찌",
        "place_id": "",
        "search": "다부찌",
        "menu_hint": "부대찌개",
        "about": "홍대 인근의 부대찌개 전문점입니다. 맵기 조절이 가능하고 혼자·소규모로 먹기 좋습니다.",
    },
    {
        "kind": "meals",
        "dish": "budae-jjigae",
        "slug": "bada-sikdang",
        "name": "바다식당",
        "place_id": "11724665",
        "menu_hint": "부대찌개",
        "about": "의정부 부대찌개 골목의 오래 사랑받은 집입니다. 진한 국물과 푸짐한 구성이 특징입니다.",
    },
    {
        "kind": "meals",
        "dish": "budae-jjigae",
        "slug": "deoksujeong",
        "name": "덕수정",
        "place_id": "13006904",
        "menu_hint": "부대찌개",
        "about": "의정부에서 알려진 부대찌개 노포입니다. 국물 맛이 진하고 사이드 메뉴도 함께 주문하기 좋습니다.",
    },
    {
        "kind": "meals",
        "dish": "budae-jjigae",
        "slug": "huijeong-sikdang",
        "name": "희정식당",
        "place_id": "11888725",
        "menu_hint": "부대찌개",
        "about": "의정부 부대찌개 골목의 현지 맛집입니다. 밥·라면사리를 추가해 든든하게 먹기 좋습니다.",
    },
    # 곱창
    {
        "kind": "meals",
        "dish": "gopchang",
        "slug": "pyeonghwa-yeonnam",
        "name": "평화연남",
        "place_id": "1874989869",
        "menu_hint": "곱창",
        "about": "연남동의 곱창·대창 전문점입니다. 불판에 구워 먹는 스타일로 저녁·술안주로 인기입니다.",
    },
    # 감자탕
    {
        "kind": "meals",
        "dish": "gamjatang",
        "slug": "somunnan-seongsu-gamjatang",
        "name": "소문난성수감자탕",
        "place_id": "11721256",
        "menu_hint": "감자탕",
        "about": "성수동의 감자탕 맛집입니다. 뼈에 붙은 고기가 많고 국물이 진해 여럿이 나눠 먹기 좋습니다.",
    },
    # 빵
    {
        "kind": "desserts",
        "dish": "bread",
        "slug": "sowoldang",
        "name": "소월당",
        "place_id": "2047914123",
        "menu_hint": "빵",
        "about": "정성 들인 식빵·페이스트리가 돋보이는 베이커리입니다. 커피와 함께 포장해 가기 좋습니다.",
    },
    {
        "kind": "desserts",
        "dish": "bread",
        "slug": "sungsimdang",
        "name": "성심당 본점",
        "place_id": "11871325",
        "menu_hint": "튀김소보로",
        "about": "대전의 대표 베이커리 성심당 본점입니다. 튀김소보로·부추빵 등 시그니처를 포장해 가세요.",
    },
    # 갈비찜
    {
        "kind": "meals",
        "dish": "galbijjim",
        "slug": "asojeong",
        "name": "아소정",
        "place_id": "11603394",
        "menu_hint": "갈비찜",
        "about": "한정식·갈비찜으로 알려진 집입니다. 부드러운 갈비와 달큰한 양념이 잘 배어 있습니다.",
    },
    {
        "kind": "meals",
        "dish": "galbijjim",
        "slug": "gangnam-myeonok",
        "name": "강남면옥",
        "place_id": "11845608",
        "menu_hint": "갈비찜",
        "about": "갈비찜·냉면으로 유명한 강남 일대 맛집입니다. 양념이 진하고 고기가 부드럽습니다.",
    },
    {
        "kind": "meals",
        "dish": "galbijjim",
        "slug": "seongbukdong-myeonokjip",
        "name": "성북동면옥집",
        "place_id": "37101627",
        "menu_hint": "갈비찜",
        "about": "성북동의 갈비찜·면 요리 집입니다. 가족·단체 식사로도 찾기 좋은 현지 맛집입니다.",
    },
    # 닭갈비
    {
        "kind": "meals",
        "dish": "dakgalbi",
        "slug": "dakuroga-apgujeong",
        "name": "닭으로가 압구정본점",
        "place_id": "11710160",
        "menu_hint": "닭갈비",
        "about": "압구정 본점의 닭갈비 전문점입니다. 매콤한 양념에 볶아 먹는 스타일로 인기가 많습니다.",
    },
    {
        "kind": "meals",
        "dish": "dakgalbi",
        "slug": "ogeunnae-dakgalbi",
        "name": "오근내 닭갈비",
        "place_id": "18168200",
        "menu_hint": "닭갈비",
        "about": "춘천식 닭갈비로 알려진 체인 맛집입니다. 철판에 볶아 먹으며 치즈·라면사리 추가가 흔합니다.",
    },
    {
        "kind": "meals",
        "dish": "dakgalbi",
        "slug": "sanggye-dongsunjip",
        "name": "상계동 원조닭갈비 동순집",
        "place_id": "1218804796",
        "menu_hint": "닭갈비",
        "about": "상계동의 원조 닭갈비로 알려진 집입니다. 양념이 진하고 현지인 단골이 많은 편입니다.",
    },
    {
        "kind": "meals",
        "dish": "dakgalbi",
        "slug": "sindorim-ido-sikdang",
        "name": "신도림 이도식당",
        "place_id": "",
        "search": "신도림 이도식당",
        "menu_hint": "닭갈비",
        "about": "신도림 일대의 닭갈비 맛집입니다. 양념 닭갈비를 철판에 볶아 든든하게 먹기 좋습니다.",
    },
    {
        "kind": "meals",
        "dish": "dakgalbi",
        "slug": "yangju-geosigi-dakgalbi",
        "name": "양주 거시기닭갈비",
        "place_id": "18085815",
        "menu_hint": "닭갈비",
        "about": "양주의 닭갈비 전문점입니다. 푸짐한 양과 매콤달콤한 양념이 특징입니다.",
    },
]

NEW_DISH = {
    "kind": "meals",
    "slug": "galbijjim",
    "emoji": "🥩",
    "title": "갈비찜",
    "desc": "양념에 조린 부드러운 갈비 찜 요리",
    "about": (
        "갈비찜은 소갈비(또는 돼지갈비)를 달큰매콤한 양념에 조려 내는 한국의 대표적인 찜 요리입니다. "
        "고기가 뼈에서 부드럽게 떨어지고, 무·표고·밤 등 고명이 함께 나와 "
        "가족·명절·손님 접대 음식으로도 자주 먹습니다."
    ),
    "cover": "https://commons.wikimedia.org/wiki/Special:FilePath/Korean_ribs-Galbi_jjim-01.jpg",
    "cover_alt": "https://upload.wikimedia.org/wikipedia/commons/8/8a/Galbijjim.jpg",
}

# Fallback Wikimedia / real food covers
DOENJANG_COVER = (
    "https://commons.wikimedia.org/wiki/Special:FilePath/Doenjang_jjigae.jpg"
)
DOENJANG_COVER_ALT = (
    "https://commons.wikimedia.org/wiki/Special:FilePath/Doenjang-jjigae_4.jpg"
)
SEOGIL_FOOD_FALLBACK = (
    "https://commons.wikimedia.org/wiki/Special:FilePath/Ganjang-gejang_3.jpg"
)
SEOGIL_FOOD_ALT = (
    "https://commons.wikimedia.org/wiki/Special:FilePath/Gejang.jpg"
)

RATING_RE = re.compile(
    r"(?:방문자\s*)?평점\s*[0-9]+(?:\.[0-9]+)?(?:\s*\([0-9,]+\s*명\))?",
    re.IGNORECASE,
)
STAR_RE = re.compile(r"[★☆⭐]+(?:\s*[0-9.]+)?")
CONV_RE = re.compile(r"편의\s*[:：]\s*[^\n]+", re.IGNORECASE)
# Common amenity dump tokens if "편의:" prefix was lost
AMENITY_DUMP_RE = re.compile(
    r"(?:^|[\s,，])(?:"
    r"주차|발렛파킹|무선\s*인터넷|와이파이|Wi-?Fi|남/녀\s*화장실\s*구분|"
    r"단체\s*이용\s*가능|대기공간|유아의자|반려동물\s*동반|간편결제|"
    r"방문접수/?출장|예약|포장|배달"
    r")(?=[\s,，]|$)",
    re.IGNORECASE,
)
VISITOR_COUNT_RE = re.compile(r"\([0-9,]+\s*명\)")
PARKING_BLOCK_RE = re.compile(
    r"(?:\*?\s*주차[^\n]*(?:\n|$))+|(?:주차\s*(?:불가|장|은|는)[^\n]*)",
    re.IGNORECASE,
)


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
        return f"cover ok {COVER_SIZE[0]}x{COVER_SIZE[1]}: {path.name}"
    except Exception as exc:  # noqa: BLE001
        return f"cover resize failed: {exc}"


def clean_about_text(text: str) -> str:
    """Strip scraped rating / amenity / parking junk; keep short descriptive prose."""
    raw = (text or "").strip()
    if not raw:
        return ""
    s = raw
    s = RATING_RE.sub(" ", s)
    s = STAR_RE.sub(" ", s)
    s = CONV_RE.sub(" ", s)
    s = VISITOR_COUNT_RE.sub(" ", s)
    # Drop lines that are mostly amenity / parking dumps
    lines_out: list[str] = []
    for line in re.split(r"[\r\n]+", s):
        line = line.strip(" \t·-|")
        if not line:
            continue
        # Entire line is amenity list
        if line.startswith("편의"):
            continue
        if re.fullmatch(
            r"(?:예약|포장|배달|주차|무선\s*인터넷|와이파이|단체\s*이용\s*가능|"
            r"남/녀\s*화장실\s*구분|대기공간|유아의자|반려동물\s*동반|"
            r"간편결제|발렛파킹)(?:\s*[,，]\s*(?:예약|포장|배달|주차|무선\s*인터넷|"
            r"와이파이|단체\s*이용\s*가능|남/녀\s*화장실\s*구분|대기공간|"
            r"유아의자|반려동물\s*동반|간편결제|발렛파킹))+",
            line,
        ):
            continue
        if PARKING_BLOCK_RE.fullmatch(line) or (
            line.startswith("*") and "주차" in line
        ):
            continue
        if re.search(r"방문자\s*평점", line):
            continue
        lines_out.append(line)
    s = "\n".join(lines_out)
    s = re.sub(r"[ \t]{2,}", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    s = s.strip(" \t\n·,，")
    # If leftover is only address-like or too amenity-heavy, treat as empty
    if len(s) < 12:
        return ""
    amenity_hits = len(AMENITY_DUMP_RE.findall(s))
    if amenity_hits >= 3 and len(s) < 80:
        return ""
    # Pure "찾아오는 길" mega-dump without food description → empty
    if len(s) > 280 and (
        s.count("출구") + s.count("주차") + s.count("도보") >= 4
        and not re.search(r"(맛|메뉴|국물|양념|전문|대표|유명)", s)
    ):
        return ""
    return s[:500]


def default_intro(name: str, dish: str, menu: str, category: str) -> str:
    dish_labels = {
        "budae-jjigae": "부대찌개",
        "gopchang": "곱창",
        "gamjatang": "감자탕",
        "bread": "베이커리",
        "galbijjim": "갈비찜",
        "dakgalbi": "닭갈비",
        "ganjang-gejang": "간장게장",
        "kimbap": "김밥",
        "doenjang-jjigae": "된장찌개",
    }
    label = dish_labels.get(dish) or category or menu or "한식"
    focus = menu or label
    return (
        f"{name}은(는) {label}으로 알려진 곳입니다. "
        f"대표 메뉴는 {focus}이며, 현지인·여행객이 함께 찾는 맛집입니다."
    )


def clean_all_shop_abouts(bundle: dict) -> tuple[list[str], list[str]]:
    """Return (notes, cleaned_slugs)."""
    notes: list[str] = []
    ko_rest = bundle["ko"].setdefault("restaurants", {})
    from lib.content import find_shop_page

    dirty_slugs: list[str] = []
    for slug, entry in list(ko_rest.items()):
        if not isinstance(entry, dict):
            continue
        about = str(entry.get("about") or "")
        junk_markers = (
            "평점" in about
            or "편의:" in about
            or "편의：" in about
            or "★" in about
            or "방문자 평점" in about
            or bool(re.search(r"\([0-9,]+\s*명\)", about))
        )
        cleaned_probe = clean_about_text(about)
        if junk_markers or (about.strip() and cleaned_probe != about.strip()):
            dirty_slugs.append(slug)

    dirty_slugs = sorted(set(dirty_slugs))
    rewritten = 0
    changed: list[str] = []
    for slug in dirty_slugs:
        entry = ko_rest[slug]
        old = str(entry.get("about") or "")
        cleaned = clean_about_text(old)
        found = find_shop_page(slug)
        dish = found[1] if found else ""
        if not cleaned:
            cleaned = default_intro(
                str(entry.get("name") or slug),
                dish,
                str(entry.get("menu") or ""),
                str(entry.get("category") or ""),
            )
            rewritten += 1
        if cleaned == old.strip():
            continue
        entry["about"] = cleaned
        changed.append(slug)
        notes.append(f"cleaned about: {slug}")

    notes.append(
        f"about cleaned shops: {len(changed)} "
        f"(candidates {len(dirty_slugs)}, rewrote empty→intro: {rewritten})"
    )
    return notes, changed


def translate_shop_abouts(bundle: dict, slugs: list[str]) -> BatchStatus:
    st = BatchStatus()
    for slug in slugs:
        ko_entry = (bundle["ko"].get("restaurants") or {}).get(slug) or {}
        texts = {
            "ko": {"about": str(ko_entry.get("about") or "")},
            "en": {},
            "ja": {},
            "zh": {},
        }
        filled = fill_scalar_texts(texts, ["about"], force=True, status=st)
        for lang in i18n_store.LANGS:
            restaurants_lang = bundle[lang].setdefault("restaurants", {})
            entry = dict(restaurants_lang.get(slug) or {})
            if lang == "ko":
                entry["about"] = ko_entry.get("about") or ""
            elif filled.get(lang, {}).get("about"):
                entry["about"] = filled[lang]["about"]
            restaurants_lang[slug] = entry
    return st


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
    if not cover.is_file() and d.get("cover"):
        if download_image_to(cover, d["cover"]):
            notes.append(f"dish cover downloaded: {slug}")
        else:
            notes.append(f"WARN: dish cover failed: {slug}")
    if cover.is_file():
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
        cpath.write_text(text, encoding="utf-8", newline="\n")
        notes.append("content.py fallback +galbijjim")

    spath = TOOL_DIR / "lib" / "sections.py"
    stext = spath.read_text(encoding="utf-8")
    if '"galbijjim"' not in stext:
        stext = stext.replace(
            '"doenjang-jjigae": "된장찌개",',
            '"doenjang-jjigae": "된장찌개",\n        "galbijjim": "갈비찜",',
            1,
        )
        spath.write_text(stext, encoding="utf-8", newline="\n")
        notes.append("sections.py +galbijjim")

    tags_path = ROOT / "data" / "food" / "recommend-tags.json"
    data = json.loads(tags_path.read_text(encoding="utf-8"))
    items = data.setdefault("items", {})
    if "galbijjim" not in items:
        items["galbijjim"] = {
            "tags": ["meat", "nosoup", "hearty", "mild", "warm"]
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
            r'(re.compile(r"samgyeopsal|gopchang|tangsuyuk|korean-chinese|bulgogi|bossam|tteokgalbi|jeyuk"), ["meat", "nosoup"]),',
            r'(re.compile(r"samgyeopsal|gopchang|tangsuyuk|korean-chinese|bulgogi|bossam|tteokgalbi|jeyuk|galbijjim"), ["meat", "nosoup"]),',
            1,
        )
        ct = ct.replace(
            r'(re.compile(r"jajang|tangsuyuk|korean-chinese|bulgogi|bossam|tteokgalbi"), ["mild", "nosoup"]),',
            r'(re.compile(r"jajang|tangsuyuk|korean-chinese|bulgogi|bossam|tteokgalbi|galbijjim"), ["mild", "nosoup"]),',
            1,
        )
        cat.write_text(ct, encoding="utf-8", newline="\n")
        notes.append("catalog heuristics +galbijjim")
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
    if page.exists():
        notes.append(f"[skip create] {slug}")
        return notes

    # Partial: i18n exists but HTML page missing (interrupted save)
    bundle = i18n_store.load_all()
    if slug in (bundle["ko"].get("restaurants") or {}):
        from lib.scaffold import (
            insert_before_card_grid_close,
            render_shop_page,
            shop_card_html,
        )

        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(
            render_shop_page(shop["kind"], shop["dish"], slug),
            encoding="utf-8",
            newline="\n",
        )
        index = dish_dir(shop["kind"], shop["dish"]) / "index.html"
        html = index.read_text(encoding="utf-8")
        if f"./{slug}/" not in html:
            html = insert_before_card_grid_close(
                html, shop_card_html(shop["kind"], shop["dish"], slug)
            )
            index.write_text(html, encoding="utf-8", newline="\n")
            notes.append(f"[repaired page+card] {slug}")
        else:
            notes.append(f"[repaired page] {slug}")
        # ensure place id
        for lang in i18n_store.LANGS:
            entry = bundle[lang].setdefault("restaurants", {}).setdefault(slug, {})
            entry["placeId"] = place_id
            entry["placeUrl"] = place_url
            entry["mapsUrl"] = place_url
            entry["sourceType"] = "naver"
            if shop.get("about") and not clean_about_text(str(entry.get("about") or "")):
                entry["about"] = shop["about"]
            elif shop.get("about") and (
                "평점" in str(entry.get("about") or "")
                or "편의:" in str(entry.get("about") or "")
            ):
                entry["about"] = shop["about"]
        for attempt in range(3):
            try:
                i18n_store.save_all(bundle)
                break
            except OSError as exc:
                notes.append(f"save retry {attempt+1}: {exc}")
                time.sleep(1.5)
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
    for attempt in range(3):
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
            notes.append(f"[created] {slug}")
            notes.extend(cnotes)
            notes.extend(status.note_lines())
            return notes
        except OSError as exc:
            notes.append(f"save retry {attempt+1}/3 after OSError: {exc}")
            time.sleep(1.5)
        except ValueError as exc:
            # race / partial
            notes.append(f"create_shop ValueError: {exc}")
            if page.exists() or slug in (
                i18n_store.load_all()["ko"].get("restaurants") or {}
            ):
                notes.append("partial state — will repair on next pass")
                return ensure_shop({**shop, "place_id": place_id})
            raise
    notes.append(f"ERROR: create_shop failed for {slug}")
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


def fix_doenjang_cover() -> list[str]:
    notes: list[str] = []
    cover = dish_cover_path("doenjang-jjigae", "meals")
    cover.parent.mkdir(parents=True, exist_ok=True)
    ok = download_image_to(cover, DOENJANG_COVER) or download_image_to(
        cover, DOENJANG_COVER_ALT
    )
    if ok:
        notes.append("doenjang-jjigae dish cover → real food photo")
        notes.append(_resize_jpeg(cover))
    else:
        notes.append("WARN: doenjang-jjigae cover download failed")
    # meals hub uses same relative cover path — no extra copy needed
    return notes


def fix_seogil_cover() -> list[str]:
    notes: list[str] = []
    cover = shop_photo_path("meals", "ganjang-gejang", "seogil-sikdang")
    cover.parent.mkdir(parents=True, exist_ok=True)
    scraped = scrape_naver_place("17995671", force=True)
    photos = list(scraped.get("photos") or [])
    picked = ""
    # Prefer later gallery shots over smartstore/product hero when possible
    for url in photos[1:] + photos[:1]:
        if not url:
            continue
        # Skip obvious shopping CDN product screenshots if detectable
        low = url.lower()
        if "smartstore" in low or "shopping" in low:
            continue
        if download_image_to(cover, url):
            picked = url
            break
    if not picked:
        if download_image_to(cover, SEOGIL_FOOD_FALLBACK) or download_image_to(
            cover, SEOGIL_FOOD_ALT
        ):
            picked = "wikimedia"
            notes.append("seogil cover: Wikimedia ganjang-gejang food photo")
        else:
            notes.append("WARN: seogil cover download failed")
            return notes
    else:
        notes.append(f"seogil cover from Naver photo: {picked[:80]}…")
    notes.append(_resize_jpeg(cover))
    # Sync previewImage path in i18n
    bundle = i18n_store.load_all()
    for lang in i18n_store.LANGS:
        entry = bundle[lang].setdefault("restaurants", {}).setdefault(
            "seogil-sikdang", {}
        )
        entry["previewImage"] = "media/cover.jpg"
    i18n_store.save_all(bundle)
    return notes


def main() -> int:
    print("=== patch place_scrape already applied separately ===")

    print("=== ensure galbijjim dish ===")
    for n in ensure_galbijjim():
        print(" ", n)
    for n in patch_fallbacks():
        print(" ", n)

    print("=== create shops ===")
    for shop in SHOPS:
        for n in ensure_shop(shop):
            print(" ", n)
        time.sleep(0.35)

    print("=== enrich shops ===")
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
        # Preserve our editorial about through enrich
        editorial = str(shop.get("about") or entry.get("about") or "").strip()
        print(f"[enrich] {slug} placeId={place_id}…")
        updated, notes, st = enrich_one(slug, entry, force=True)
        if editorial:
            updated["about"] = editorial
        else:
            scraped_about = clean_about_text(str(updated.get("about") or ""))
            if scraped_about:
                updated["about"] = scraped_about
            else:
                updated["about"] = default_intro(
                    str(updated.get("name") or shop["name"]),
                    shop["dish"],
                    str(updated.get("menu") or shop.get("menu_hint") or ""),
                    str(updated.get("category") or ""),
                )
        apply_to_bundle(bundle, slug, updated)
        restaurants[slug] = updated
        enrich_stats[slug] = st
        print(f"  status={st}")
        for n in notes[:6]:
            print(" ", n)
        for n in sync_shop_page_visual(shop["kind"], shop["dish"], slug):
            print("  html:", n)
        print(" ", _resize_jpeg(shop_photo_path(shop["kind"], shop["dish"], slug)))
        if i + 1 < len(SHOPS):
            time.sleep(0.8)

    i18n_store.save_all(bundle)

    print("=== clean existing shop about junk ===")
    bundle = i18n_store.load_all()
    clean_notes, cleaned_slugs = clean_all_shop_abouts(bundle)
    for n in clean_notes:
        print(" ", n)
    translate_slugs = sorted(set([s["slug"] for s in SHOPS] + cleaned_slugs))
    print(f"=== translate abouts ({len(translate_slugs)}) ===")
    st = translate_shop_abouts(bundle, translate_slugs)
    for n in st.note_lines():
        print(" ", n)

    print("=== localize new shop scalars ===")
    st2 = localize_scalars(bundle, SHOPS)
    for n in st2.note_lines():
        print(" ", n)

    print("=== menu i18n ===")
    menu_st = BatchStatus()
    for shop in SHOPS:
        slug = shop["slug"]
        ko_restaurants = bundle["ko"].setdefault("restaurants", {})
        entry = ko_restaurants.get(slug) or {}
        items = list(entry.get("menuItems") or [])
        if not items:
            print(f"[menu-i18n skip] {slug}")
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

    i18n_store.save_all(bundle)

    print("=== fix covers ===")
    for n in fix_doenjang_cover():
        print(" ", n)
    for n in fix_seogil_cover():
        print(" ", n)
    # also write short about for seogil if still junk
    bundle = i18n_store.load_all()
    se = bundle["ko"].setdefault("restaurants", {}).setdefault("seogil-sikdang", {})
    se_about = clean_about_text(str(se.get("about") or ""))
    if not se_about or "평점" in str(se.get("about") or ""):
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
        page = shop_page_path(shop["kind"], shop["dish"], slug)
        print(
            f"{slug}: placeId={shop.get('place_id')} "
            f"status={enrich_stats.get(slug)} exists={page.exists()}"
        )
    gal = dish_dir("meals", "galbijjim") / "index.html"
    print(f"galbijjim dish exists={gal.exists()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
