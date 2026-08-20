# -*- coding: utf-8 -*-
"""Add missing food categories + shops from Naver place list (2026-08-20)."""
from __future__ import annotations

import sys
import time
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from lib import content, i18n_store  # noqa: E402
from lib.cache_bust import bump_asset_version  # noqa: E402
from lib.place_scrape import naver_canonical_place_url  # noqa: E402
from lib.scaffold import shop_page_path  # noqa: E402
from lib.translate import BatchStatus, fill_scalar_texts  # noqa: E402
from migrate_menu_i18n import migrate_menu_items  # noqa: E402
from migrate_shop_enrich import apply_to_bundle, enrich_one  # noqa: E402

# ---------------------------------------------------------------------------
# New dish categories
# ---------------------------------------------------------------------------
NEW_DISHES = [
    {
        "kind": "meals",
        "slug": "baekban",
        "emoji": "🍚",
        "texts": {
            "ko": {
                "title": "백반",
                "desc": "집밥처럼 반찬이 풍성한 한식 정식",
                "about": "백반은 밥과 국, 여러 반찬이 함께 나오는 한국식 한 상 차림입니다. 여행 중 든든하고 가성비 좋은 식사로 많이 찾습니다.",
            },
            "en": {
                "title": "Baekban (Korean set meal)",
                "desc": "Rice, soup, and many banchan — home-style Korean table",
                "about": "Baekban is a Korean set meal with rice, soup, and assorted side dishes. A filling, good-value lunch or dinner while traveling.",
            },
        },
    },
    {
        "kind": "meals",
        "slug": "guksu",
        "emoji": "🍜",
        "texts": {
            "ko": {
                "title": "국수",
                "desc": "잔치국수·메밀국수 등 담백한 면 요리",
                "about": "국수는 맑은 국물이나 비빔으로 즐기는 한국식 면 요리입니다. 칼국수·냉면과 따로, 지역 특색 국수집을 모았습니다.",
            },
            "en": {
                "title": "Guksu (Korean noodles)",
                "desc": "Light noodle soups and regional specialties",
                "about": "Guksu covers everyday Korean noodle dishes — clear broth or bibim styles — beyond kalguksu and naengmyeon.",
            },
        },
    },
    {
        "kind": "meals",
        "slug": "dolsotbap",
        "emoji": "🍲",
        "texts": {
            "ko": {
                "title": "돌솥밥",
                "desc": "돌솥에 지은 밥과 누룽지",
                "about": "돌솥밥은 뜨겁게 달군 돌솥에 밥을 지어 고슬고슬한 식감과 누룽지를 즐기는 한식입니다.",
            },
            "en": {
                "title": "Dolsotbap (hot-stone pot rice)",
                "desc": "Crispy scorched rice from a hot stone pot",
                "about": "Dolsotbap is rice cooked in a heated stone pot — fluffy grains plus crispy nurungji at the bottom.",
            },
        },
    },
    {
        "kind": "meals",
        "slug": "jangeo-gui",
        "emoji": "🐟",
        "texts": {
            "ko": {
                "title": "장어구이",
                "desc": "양념·소금 장어 구이",
                "about": "장어구이는 민물·바다 장어를 양념이나 소금으로 구워 먹는 보양 요리입니다. 밥·쌈과 함께 푸짐하게 즐깁니다.",
            },
            "en": {
                "title": "Grilled eel (jangeo-gui)",
                "desc": "Soy-glazed or salt-grilled eel",
                "about": "Jangeo-gui is grilled freshwater or sea eel with sweet soy glaze or salt — a classic Korean restorative meal.",
            },
        },
    },
    {
        "kind": "meals",
        "slug": "dakbal",
        "emoji": "🔥",
        "texts": {
            "ko": {
                "title": "닭발",
                "desc": "매콤한 양념 닭발",
                "about": "닭발은 매콤한 양념에 볶거나 구운 안주·야식으로 인기입니다. 소주와 함께 찾는 곳이 많습니다.",
            },
            "en": {
                "title": "Dakbal (spicy chicken feet)",
                "desc": "Spicy braised or grilled chicken feet",
                "about": "Dakbal is chicken feet cooked in a hot-sweet chili sauce — a popular late-night anju with soju.",
            },
        },
    },
    {
        "kind": "meals",
        "slug": "jjuggumi",
        "emoji": "🦑",
        "texts": {
            "ko": {
                "title": "쭈꾸미",
                "desc": "매콤 볶음·불고기 스타일 쭈꾸미",
                "about": "쭈꾸미는 작은 문어류를 매콤하게 볶아 밥·야채와 먹는 요리입니다. 충무로 등 전문 거리가 유명합니다.",
            },
            "en": {
                "title": "Jjuggumi (spicy baby octopus)",
                "desc": "Spicy stir-fried webfoot octopus",
                "about": "Jjuggumi is small octopus stir-fried in chili sauce with rice and veggies — famous around Chungmuro in Seoul.",
            },
        },
    },
]

# Rename yogurt-ice → ice-cream after dishes created
ICE_CREAM_TITLES = {
    "ko": {
        "title": "아이스크림",
        "desc": "젤라토·소프트·요거트 아이스크림",
        "about": "한국에서 즐기는 아이스크림·젤라토·요거트 아이스크림 맛집을 모았습니다. 더운 날 디저트나 산책 코스로 좋습니다.",
    },
    "en": {
        "title": "Ice cream",
        "desc": "Gelato, soft serve, and yogurt ice cream",
        "about": "Ice cream, gelato, and yogurt soft-serve spots popular with travelers in Korea.",
    },
}

# ---------------------------------------------------------------------------
# Shops: (kind, dish, slug, name, place_id_or_none, search_hint)
# place_id preferred; if None, create_shop resolves via name search.
# ---------------------------------------------------------------------------
SHOPS: list[dict] = [
    # 백반
    {"kind": "meals", "dish": "baekban", "slug": "sunchunga", "name": "순천가", "place_id": "38009499"},
    {"kind": "meals", "dish": "baekban", "slug": "yetnaljip", "name": "옛날집", "place_id": "18432817"},
    {"kind": "meals", "dish": "baekban", "slug": "daon", "name": "다온", "place_id": "127943990"},
    {"kind": "meals", "dish": "baekban", "slug": "yangji-sikdang", "name": "양지식당", "place_id": "34582011"},
    {"kind": "meals", "dish": "baekban", "slug": "hansangcharim-bapsang-sinseol", "name": "한상차림밥상 신설동", "place_id": "1727721533"},
    {"kind": "meals", "dish": "baekban", "slug": "cheongdamgol", "name": "청담골", "place_id": "11477316"},
    # 김밥
    {"kind": "meals", "dish": "kimbap", "slug": "haeundae-bada-kimbap", "name": "해운대 바다김밥", "place_id": "2045599810"},
    {"kind": "meals", "dish": "kimbap", "slug": "hawaii-kimbap", "name": "하와이김밥", "place_id": "", "search": "하와이김밥"},
    {"kind": "meals", "dish": "kimbap", "slug": "gawon-kimbap", "name": "가원김밥", "place_id": "1343785420"},
    {"kind": "meals", "dish": "kimbap", "slug": "kimmyeonjang", "name": "김면장", "place_id": "", "search": "김면장"},
    {"kind": "meals", "dish": "kimbap", "slug": "badasoon-kimbap", "name": "바다손김밥", "place_id": "", "search": "바다손김밥"},
    # myeongran-kimbap already exists under kimbap — skip duplicate
    {"kind": "meals", "dish": "kimbap", "slug": "satto-bunsik", "name": "사또분식", "place_id": "", "search": "사또분식"},
    {"kind": "meals", "dish": "kimbap", "slug": "sodami-kimbap", "name": "소다미김밥", "place_id": "", "search": "소다미김밥"},
    # 삼계탕 — tosokchon exists
    # 국수
    {"kind": "meals", "dish": "guksu", "slug": "deuruni-guksu-cheorwon", "name": "드르니 국수 철원 본점", "place_id": "1063302543"},
    # 칼국수
    {"kind": "meals", "dish": "kalguksu", "slug": "hoisik", "name": "호이식", "place_id": "", "search": "호이식"},
    {"kind": "meals", "dish": "kalguksu", "slug": "oneul-neungi-kalguksu", "name": "오늘은능이칼국수", "place_id": "", "search": "오늘은 능이칼국수"},
    {"kind": "meals", "dish": "kalguksu", "slug": "seolidong", "name": "설이동", "place_id": "", "search": "설이동"},
    {"kind": "meals", "dish": "kalguksu", "slug": "hongkal", "name": "홍칼", "place_id": "1714965426"},
    {"kind": "meals", "dish": "kalguksu", "slug": "jojo-kalguksu-seongsu", "name": "조조칼국수 성수점", "place_id": "1057264169"},
    # 국밥
    {"kind": "meals", "dish": "gukbap", "slug": "donmatkkul", "name": "돈맛꿀", "place_id": "", "search": "돈맛꿀"},
    {"kind": "meals", "dish": "gukbap", "slug": "neungdong-minari-seongsu", "name": "능동미나리 성수지점", "place_id": "", "search": "능동미나리 성수지점"},
    {"kind": "meals", "dish": "gukbap", "slug": "sandermi-miseong-dongseongno", "name": "산더미 미성돼지국밥 동성로점", "place_id": "1168203966"},
    {"kind": "meals", "dish": "gukbap", "slug": "haeundae-wonjo-halmae-gukbap", "name": "해운대원조할매국밥", "place_id": "1883663647"},
    {"kind": "meals", "dish": "gukbap", "slug": "dwaeji-gongtang-hau-seongsu", "name": "돼지공탕 하우 성수본점", "place_id": "1559602117"},
    # 고기집
    {"kind": "meals", "dish": "samgyeopsal", "slug": "gabojeong", "name": "가보정", "place_id": "11567981"},
    {"kind": "meals", "dish": "samgyeopsal", "slug": "pulddeumneun-dwaeji", "name": "풀뜯는돼지", "place_id": "", "search": "풀뜯는돼지"},
    {"kind": "meals", "dish": "samgyeopsal", "slug": "baekje-jeongyukjeom", "name": "백제정육점", "place_id": "11728126"},
    {"kind": "meals", "dish": "samgyeopsal", "slug": "dutum", "name": "두툼", "place_id": "37036424"},
    {"kind": "meals", "dish": "samgyeopsal", "slug": "gukbo-garden", "name": "국보가든", "place_id": "", "search": "국보가든"},
    {"kind": "meals", "dish": "samgyeopsal", "slug": "ilpyeon-deungsim-hongdae", "name": "일편등심 홍대본점", "place_id": "34565224"},
    {"kind": "meals", "dish": "samgyeopsal", "slug": "kimchiok-magok", "name": "김치옥 마곡본점", "place_id": "2072413332"},
    # 족발
    {"kind": "meals", "dish": "jokbal", "slug": "yeonnam-jokbal-1987-hongdae", "name": "연남족발1987 홍대점", "place_id": "", "search": "연남족발1987 홍대점"},
    # 곱창 — pyeonghwa-yeonnam exists
    {"kind": "meals", "dish": "gopchang", "slug": "michin-makchang", "name": "미친막창 본점", "place_id": "", "search": "미친막창 본점"},
    # 간장게장
    {"kind": "meals", "dish": "ganjang-gejang", "slug": "pro-ganjang-gejang-paradise", "name": "프로간장게장 인천파라다이스시티점", "place_id": "", "search": "프로간장게장 인천 파라다이스시티"},
    {"kind": "meals", "dish": "ganjang-gejang", "slug": "masan-halmae-ganjang-gejang", "name": "마산할매간장게장", "place_id": "1741697928"},
    {"kind": "meals", "dish": "ganjang-gejang", "slug": "jinbok-sikdang", "name": "진복식당", "place_id": "16862966"},
    {"kind": "meals", "dish": "ganjang-gejang", "slug": "ilmi-ganjang-gejang", "name": "일미간장게장", "place_id": "13182359"},
    # 돌솥밥
    {"kind": "meals", "dish": "dolsotbap", "slug": "yeonjune-dolsotbap", "name": "연주네돌솥밥", "place_id": "", "search": "연주네 돌솥밥"},
    {"kind": "meals", "dish": "dolsotbap", "slug": "bokgil-gyeongju", "name": "복길 경주본점", "place_id": "", "search": "복길 경주본점"},
    {"kind": "meals", "dish": "dolsotbap", "slug": "solsot-myeongdong", "name": "솔솥 명동점", "place_id": "1842122521"},
    # 부침개/전
    {"kind": "meals", "dish": "jeon", "slug": "sinsajeon", "name": "신사전", "place_id": "1346291809"},
    {"kind": "meals", "dish": "jeon", "slug": "gyeongbuk-sikdang", "name": "경북식당", "place_id": "16769712"},
    # 양념치킨
    {"kind": "meals", "dish": "yangnyeom-chicken", "slug": "kyochon-yongmun", "name": "교촌치킨 용문점", "place_id": "11802450"},
    {"kind": "meals", "dish": "yangnyeom-chicken", "slug": "bhc-dongdaemun", "name": "BHC치킨 동대문점", "place_id": "782851237"},
    {"kind": "meals", "dish": "yangnyeom-chicken", "slug": "haebangchon-dak", "name": "해방촌닭 용산 해방촌 본점", "place_id": "1112420992"},
    # 보쌈
    {"kind": "meals", "dish": "bossam", "slug": "wonhalmeoni-bossam-myeongdong", "name": "원할머니보쌈족발 명동점", "place_id": "1865398925"},
    # 감자탕
    {"kind": "meals", "dish": "gamjatang", "slug": "cheongnyeon-gamjatang-gwanggyo", "name": "청년감자탕순대국 광교호수공원점", "place_id": "2011117582"},
    # 냉면
    {"kind": "meals", "dish": "naengmyeon", "slug": "daeyeop", "name": "대엽", "place_id": "2028626899"},
    # 장어
    {"kind": "meals", "dish": "jangeo-gui", "slug": "ilpyeon-jangeo-hongdae", "name": "일편장어 홍대본점", "place_id": "", "search": "일편장어 홍대본점"},
    # 떡갈비
    {"kind": "meals", "dish": "tteokgalbi", "slug": "halmeoni-recipe", "name": "할머니의 레시피", "place_id": "", "search": "할머니의레시피"},
    # 닭발
    {"kind": "meals", "dish": "dakbal", "slug": "paldang-dakbal", "name": "팔당닭발", "place_id": "32602513"},
    # 쭈꾸미
    {"kind": "meals", "dish": "jjuggumi", "slug": "chungmuro-jjuggumi-bulgogi", "name": "충무로 쭈꾸미 불고기", "place_id": "11816541"},
    # 한국식 중국요리
    {"kind": "meals", "dish": "korean-chinese", "slug": "bukmanjang", "name": "북만장", "place_id": "36997196"},
    {"kind": "meals", "dish": "korean-chinese", "slug": "jojo-banjeom", "name": "조조반점", "place_id": "1174702497"},
    # 카페
    {"kind": "desserts", "dish": "cafe", "slug": "dotori-garden", "name": "도토리가든", "place_id": "", "search": "안국 도토리 가든"},
    {"kind": "desserts", "dish": "cafe", "slug": "beton-seongsu", "name": "베통 성수", "place_id": "365858525"},
    {"kind": "desserts", "dish": "cafe", "slug": "paul-bassett-gwanghwamun", "name": "폴바셋 광화문점", "place_id": "35118371"},
    {"kind": "desserts", "dish": "cafe", "slug": "miruku-coffee-gwangalli", "name": "미루꾸커피 부산광안점", "place_id": "", "search": "미루꾸커피 부산광안점"},
    # 빵
    {"kind": "desserts", "dish": "bread", "slug": "1983-hwanggeum-danpatppang", "name": "1983황금단팥빵", "place_id": "2042615942"},
    # 떡
    {"kind": "desserts", "dish": "tteok", "slug": "hanjeongseon", "name": "한정선", "place_id": "1353954221"},
    # 빙수
    {"kind": "desserts", "dish": "bingsu", "slug": "namdaemun-bingsu", "name": "남대문빙수", "place_id": "1796089660"},
    # 아이스크림 (after rename)
    {"kind": "desserts", "dish": "ice-cream", "slug": "benson-creamery-seoul", "name": "벤슨 크리머리 서울", "place_id": "2092510977"},
]


def ensure_dishes() -> list[str]:
    notes: list[str] = []
    for d in NEW_DISHES:
        page = content.dish_index_path(d["kind"], d["slug"]) if hasattr(content, "dish_index_path") else None
        from lib.scaffold import dish_index_path

        page = dish_index_path(d["kind"], d["slug"])
        if page.exists():
            notes.append(f"[skip dish] {d['slug']}")
            continue
        texts = {"ko": d["texts"]["ko"], "en": d["texts"].get("en") or {}, "ja": {}, "zh": {}}
        # fill missing langs via create_dish fill_scalar
        cnotes, st = content.create_dish(d["kind"], d["slug"], texts, emoji=d["emoji"])
        notes.append(f"[dish] {d['slug']}")
        notes.extend(cnotes)
        notes.extend(st.note_lines())
        time.sleep(0.3)
    return notes


def migrate_yogurt_to_ice_cream() -> list[str]:
    notes: list[str] = []
    from lib.scaffold import dish_index_path

    old = dish_index_path("desserts", "yogurt-ice")
    new = dish_index_path("desserts", "ice-cream")
    if new.exists():
        notes.append("[skip rename] ice-cream already exists")
    elif old.exists():
        notes.extend(content.rename_dish("desserts", "yogurt-ice", "ice-cream"))
    else:
        # create fresh
        texts = {"ko": ICE_CREAM_TITLES["ko"], "en": ICE_CREAM_TITLES["en"], "ja": {}, "zh": {}}
        cnotes, st = content.create_dish("desserts", "ice-cream", texts, emoji="🍦")
        notes.append("[dish] ice-cream (new)")
        notes.extend(cnotes)
        notes.extend(st.note_lines())

    # Update dish copy to ice cream wording
    bundle = i18n_store.load_all()
    for lang, block in ICE_CREAM_TITLES.items():
        dishes = bundle[lang].setdefault("dishes", {})
        if "ice-cream" in dishes:
            dishes["ice-cream"].update(block)
    # Fill other langs from EN via fill if empty titles remain as yogurt — force KO/EN
    for lang in i18n_store.LANGS:
        if lang in ICE_CREAM_TITLES:
            continue
        dishes = bundle[lang].setdefault("dishes", {})
        if "ice-cream" not in dishes:
            continue
        # keep existing translated fields if present; else copy EN title keys later by translate
        if not dishes["ice-cream"].get("title") or "요거트" in str(dishes["ice-cream"].get("title") or "") or "Yogurt" in str(dishes["ice-cream"].get("title") or ""):
            dishes["ice-cream"]["title"] = ICE_CREAM_TITLES["en"]["title"]
            dishes["ice-cream"]["desc"] = ICE_CREAM_TITLES["en"]["desc"]
            dishes["ice-cream"]["about"] = ICE_CREAM_TITLES["en"]["about"]
    i18n_store.save_all(bundle)
    notes.append("ice-cream dish titles updated")
    notes.append(i18n_store.build_bundle())
    notes.append(content.rebuild_food_recommend_catalog())
    return notes


def ensure_shop(shop: dict) -> list[str]:
    notes: list[str] = []
    slug = shop["slug"]
    page = shop_page_path(shop["kind"], shop["dish"], slug)
    if page.exists():
        notes.append(f"[skip shop] {slug}")
        return notes

    # Orphan i18n from a failed prior create — drop so create_shop can retry
    bundle = i18n_store.load_all()
    orphan = False
    for lang in i18n_store.LANGS:
        restaurants = bundle[lang].get("restaurants") or {}
        if slug in restaurants:
            del restaurants[slug]
            orphan = True
    if orphan:
        i18n_store.save_all(bundle)
        notes.append(f"[cleared orphan i18n] {slug}")

    pid = str(shop.get("place_id") or "").strip()
    if pid:
        place_url = naver_canonical_place_url(pid)
    else:
        q = shop.get("search") or shop["name"]
        from urllib.parse import quote

        place_url = f"https://map.naver.com/p/search/{quote(q)}"

    texts = {
        "ko": {
            "name": shop["name"],
            "location": "",
            "menu": "",
            "price": "",
            "tip": "",
            "about": "",
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
    except Exception as exc:  # noqa: BLE001
        notes.append(f"[FAIL] {slug}: {exc}")
        return notes
    notes.append(f"[created] {slug}")
    notes.extend(cnotes)
    notes.extend(status.note_lines())
    time.sleep(0.8)
    return notes


def enrich_shops(shops: list[dict]) -> list[str]:
    from lib.scaffold import sync_shop_page_visual  # noqa: WPS433

    notes: list[str] = []
    bundle = i18n_store.load_all()
    for shop in shops:
        slug = shop["slug"]
        page = shop_page_path(shop["kind"], shop["dish"], slug)
        if not page.exists():
            continue
        pid = str(shop.get("place_id") or "").strip()
        restaurants = bundle["ko"].setdefault("restaurants", {})
        entry = dict(restaurants.get(slug) or {"name": shop["name"]})
        if pid:
            entry["placeUrl"] = naver_canonical_place_url(pid)
            entry["placeId"] = pid
            entry["sourceType"] = "naver"
        try:
            updated, enotes, st = enrich_one(slug, entry, force=True)
            apply_to_bundle(bundle, slug, updated)
            restaurants[slug] = updated
            notes.append(f"[enrich] {slug} status={st}")
            notes.extend(enotes[:6])
            for n in sync_shop_page_visual(shop["kind"], shop["dish"], slug):
                notes.append(f"  html: {n}")
        except Exception as exc:  # noqa: BLE001
            notes.append(f"[enrich fail] {slug}: {exc}")
        time.sleep(1.0)
    i18n_store.save_all(bundle)
    try:
        notes.append(i18n_store.build_bundle())
    except Exception as exc:  # noqa: BLE001
        notes.append(f"build_bundle warn: {exc}")
    return notes


def localize_scalars(shops: list[dict]) -> BatchStatus:
    st = BatchStatus()
    bundle = i18n_store.load_all()
    for shop in shops:
        slug = shop["slug"]
        ko_entry = (bundle["ko"].get("restaurants") or {}).get(slug) or {}
        if not ko_entry:
            continue
        texts = {
            "ko": {f: str(ko_entry.get(f) or "") for f in content.SHOP_TEXT_FIELDS},
            "en": {},
            "ja": {},
            "zh": {},
        }
        filled = fill_scalar_texts(texts, content.SHOP_TEXT_FIELDS, force=True, status=st)
        for lang in i18n_store.LANGS:
            restaurants_lang = bundle[lang].setdefault("restaurants", {})
            entry = dict(restaurants_lang.get(slug) or {})
            if lang != "ko":
                for f in content.SHOP_TEXT_FIELDS:
                    if filled.get(lang, {}).get(f):
                        entry[f] = filled[lang][f]
            ko = (bundle["ko"].get("restaurants") or {}).get(slug) or {}
            for key in (
                "placeUrl", "mapsUrl", "mapsEmbedUrl", "mapsProvider", "sourceType",
                "previewTitle", "previewImage", "phone", "hours", "placeId",
                "menuItems", "category", "score", "lat", "lng", "region", "body",
            ):
                if key in ko and ko[key] not in (None, ""):
                    entry[key] = ko[key]
            restaurants_lang[slug] = entry
    i18n_store.save_all(bundle)
    return st


def main() -> int:
    all_notes: list[str] = []
    print("=== dishes ===", flush=True)
    all_notes.extend(ensure_dishes())
    print("=== yogurt-ice → ice-cream ===", flush=True)
    all_notes.extend(migrate_yogurt_to_ice_cream())

    print(f"=== shops ({len(SHOPS)}) ===", flush=True)
    created = []
    for shop in SHOPS:
        notes = ensure_shop(shop)
        all_notes.extend(notes)
        print("\n".join(notes), flush=True)
        if any(n.startswith("[created]") for n in notes):
            created.append(shop)

    print("=== enrich ===", flush=True)
    all_notes.extend(enrich_shops(SHOPS))

    print("=== localize ===", flush=True)
    st = localize_scalars(SHOPS)
    all_notes.extend(st.note_lines())
    try:
        migrate_menu_items()
        all_notes.append("menu items migrated")
    except Exception as exc:  # noqa: BLE001
        all_notes.append(f"menu migrate skip: {exc}")

    all_notes.append(i18n_store.build_bundle())
    all_notes.append(content.rebuild_food_recommend_catalog())
    all_notes.append(bump_asset_version())

    print("\n=== SUMMARY ===", flush=True)
    for n in all_notes:
        print(n, flush=True)
    fails = [n for n in all_notes if n.startswith("[FAIL]")]
    print(f"created~{len(created)} fails={len(fails)}", flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
