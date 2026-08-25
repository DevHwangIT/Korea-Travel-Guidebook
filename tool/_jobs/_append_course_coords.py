# -*- coding: utf-8 -*-
"""Append notable new course landmarks to places-coords.js if missing."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COORDS = ROOT / "data/places/places-coords.js"
JS = ROOT / "js/seoul-curated-courses.js"

# sightseeing-ish slugs from new regions (skip generic lunch/dinner/cafe)
KEEP = {
    "gwongeumseong", "sokcho-tourist-fish-market", "oeongchi", "daepohang",
    "gyeongpodae", "gyeongpo-beach", "gangneung-jungang-market", "anmok-coffee",
    "gangmun-beach", "nami-island", "samaksan", "uiamho", "daegwallyeong-sheep",
    "woljeongsa", "naksan-beach", "hajodae", "chuam-candle", "dojjaebigol",
    "mukho-nongol", "hantan-columnar", "goseokjeong", "cheorwon-dmz",
    "gongsanseong", "gongju-sanseong-market", "muryeong-tombs", "gongju-museum",
    "jemincheon", "busosanseong", "gungnamji", "buyeo-museum", "jeongnimsaji",
    "dodamsambong", "mancheonha", "danyang-jando", "danyang-market",
    "daecheon-beach", "anmyeondo", "kkoji-beach", "national-science-museum",
    "hanbit-tower", "sungsimdang", "gyeonggijeon", "jeondong-cathedral",
    "omokdae", "jeonju-nambu-market", "odongdo", "yeosu-cable", "dolsan-park",
    "isunsin-square", "suncheon-garden", "yongsan-observatory", "juknokwon",
    "gwanbangjerim", "metasequoia-damyang", "metaprovence", "yulpo-beach",
    "mokpo-modern", "mokpo-cable", "yudalsan", "gatbawi-mokpo",
    "daereungwon", "cheomseongdae", "gyochon-woljeonggyo", "buyongdae",
    "hahoe-mask", "byeongsanseowon", "woryeonggyo", "tongyeong-cable",
    "dongpirang", "gangguan", "yi-sun-sin-park", "haegeumgang", "oeodo-botania",
    "baramui-eondeok", "sinseondae", "pohang-jukdo-market", "yeongildae-beach",
    "spacewalk", "homigot", "guryongpo-houses", "seomun-market", "daegu-modern",
    "dongseong-ro", "apsan", "taehwa-garden", "ulsan-ilsan-beach",
    "dongbaekseom", "blueline-cheongsapo", "daritdol", "gwangalli", "jagalchi",
    "gukje-market", "yongdusan", "busan-songdo", "huinnyeoul", "haedong",
    "ananti-osiria", "taejongdae", "jeolyeong-trail", "jeonpo-cafe",
    "gwangchigi", "udo", "geommeolle", "osulloc", "hyeopjae-beach",
    "geumneung-beach", "handam", "gwakji-beach", "jeongbang-falls",
    "olle-market", "cheonjiyeon", "saeyeongyo", "jusangjeolli", "yeomiji",
    "yongduam", "yongyeon", "jejumok-gwana", "jeju-dongmun-market", "tapdong",
    "bijarim", "woljeong-beach", "yongnuni-oreum", "sehwa-beach", "sanbangsan",
    "yongmeori-coast", "songaksan", "seopjikoji",
}

REGION_OF = {
    "gwongeumseong": ("gangwon", "heritage"),
    "sokcho-tourist-fish-market": ("gangwon", "market"),
    "oeongchi": ("gangwon", "nature"),
    "daepohang": ("gangwon", "port"),
    "gyeongpodae": ("gangwon", "heritage"),
    "gyeongpo-beach": ("gangwon", "beach"),
    "gangneung-jungang-market": ("gangwon", "market"),
    "anmok-coffee": ("gangwon", "city"),
    "gangmun-beach": ("gangwon", "beach"),
    "nami-island": ("gyeonggi", "nature"),
    "samaksan": ("gangwon", "mountain"),
    "uiamho": ("gangwon", "lake"),
    "daegwallyeong-sheep": ("gangwon", "nature"),
    "woljeongsa": ("gangwon", "heritage"),
    "naksan-beach": ("gangwon", "beach"),
    "hajodae": ("gangwon", "beach"),
    "chuam-candle": ("gangwon", "nature"),
    "dojjaebigol": ("gangwon", "city"),
    "mukho-nongol": ("gangwon", "heritage"),
    "hantan-columnar": ("gangwon", "nature"),
    "goseokjeong": ("gangwon", "nature"),
    "cheorwon-dmz": ("gangwon", "heritage"),
    "gongsanseong": ("chungcheong", "heritage"),
    "gongju-sanseong-market": ("chungcheong", "market"),
    "muryeong-tombs": ("chungcheong", "heritage"),
    "gongju-museum": ("chungcheong", "heritage"),
    "jemincheon": ("chungcheong", "city"),
    "busosanseong": ("chungcheong", "heritage"),
    "gungnamji": ("chungcheong", "heritage"),
    "buyeo-museum": ("chungcheong", "heritage"),
    "jeongnimsaji": ("chungcheong", "heritage"),
    "dodamsambong": ("chungcheong", "nature"),
    "mancheonha": ("chungcheong", "nature"),
    "danyang-jando": ("chungcheong", "nature"),
    "danyang-market": ("chungcheong", "market"),
    "daecheon-beach": ("chungcheong", "beach"),
    "anmyeondo": ("chungcheong", "nature"),
    "kkoji-beach": ("chungcheong", "beach"),
    "national-science-museum": ("chungcheong", "city"),
    "hanbit-tower": ("chungcheong", "city"),
    "sungsimdang": ("chungcheong", "city"),
    "gyeonggijeon": ("jeolla", "heritage"),
    "jeondong-cathedral": ("jeolla", "heritage"),
    "omokdae": ("jeolla", "heritage"),
    "jeonju-nambu-market": ("jeolla", "market"),
    "odongdo": ("jeolla", "nature"),
    "yeosu-cable": ("jeolla", "city"),
    "dolsan-park": ("jeolla", "nature"),
    "isunsin-square": ("jeolla", "city"),
    "suncheon-garden": ("jeolla", "nature"),
    "yongsan-observatory": ("jeolla", "nature"),
    "juknokwon": ("jeolla", "nature"),
    "gwanbangjerim": ("jeolla", "nature"),
    "metasequoia-damyang": ("jeolla", "nature"),
    "metaprovence": ("jeolla", "city"),
    "yulpo-beach": ("jeolla", "beach"),
    "mokpo-modern": ("jeolla", "heritage"),
    "mokpo-cable": ("jeolla", "city"),
    "yudalsan": ("jeolla", "mountain"),
    "gatbawi-mokpo": ("jeolla", "nature"),
    "daereungwon": ("gyeongsang", "heritage"),
    "cheomseongdae": ("gyeongsang", "heritage"),
    "gyochon-woljeonggyo": ("gyeongsang", "heritage"),
    "buyongdae": ("gyeongsang", "heritage"),
    "hahoe-mask": ("gyeongsang", "heritage"),
    "byeongsanseowon": ("gyeongsang", "heritage"),
    "woryeonggyo": ("gyeongsang", "heritage"),
    "tongyeong-cable": ("gyeongsang", "city"),
    "dongpirang": ("gyeongsang", "heritage"),
    "gangguan": ("gyeongsang", "port"),
    "yi-sun-sin-park": ("gyeongsang", "nature"),
    "haegeumgang": ("gyeongsang", "nature"),
    "oeodo-botania": ("gyeongsang", "nature"),
    "baramui-eondeok": ("gyeongsang", "nature"),
    "sinseondae": ("gyeongsang", "nature"),
    "pohang-jukdo-market": ("gyeongsang", "market"),
    "yeongildae-beach": ("gyeongsang", "beach"),
    "spacewalk": ("gyeongsang", "city"),
    "homigot": ("gyeongsang", "nature"),
    "guryongpo-houses": ("gyeongsang", "heritage"),
    "seomun-market": ("gyeongsang", "market"),
    "daegu-modern": ("gyeongsang", "heritage"),
    "dongseong-ro": ("gyeongsang", "city"),
    "apsan": ("gyeongsang", "mountain"),
    "taehwa-garden": ("gyeongsang", "nature"),
    "ulsan-ilsan-beach": ("gyeongsang", "beach"),
    "dongbaekseom": ("busan", "nature"),
    "blueline-cheongsapo": ("busan", "city"),
    "daritdol": ("busan", "nature"),
    "gwangalli": ("busan", "beach"),
    "jagalchi": ("busan", "market"),
    "gukje-market": ("busan", "market"),
    "yongdusan": ("busan", "city"),
    "busan-songdo": ("busan", "beach"),
    "huinnyeoul": ("busan", "heritage"),
    "ananti-osiria": ("busan", "city"),
    "taejongdae": ("busan", "nature"),
    "jeolyeong-trail": ("busan", "nature"),
    "jeonpo-cafe": ("busan", "city"),
    "gwangchigi": ("jeju", "beach"),
    "udo": ("jeju", "nature"),
    "geommeolle": ("jeju", "beach"),
    "osulloc": ("jeju", "nature"),
    "hyeopjae-beach": ("jeju", "beach"),
    "geumneung-beach": ("jeju", "beach"),
    "handam": ("jeju", "nature"),
    "gwakji-beach": ("jeju", "beach"),
    "jeongbang-falls": ("jeju", "nature"),
    "olle-market": ("jeju", "market"),
    "cheonjiyeon": ("jeju", "nature"),
    "saeyeongyo": ("jeju", "city"),
    "jusangjeolli": ("jeju", "nature"),
    "yeomiji": ("jeju", "nature"),
    "yongduam": ("jeju", "nature"),
    "yongyeon": ("jeju", "nature"),
    "jejumok-gwana": ("jeju", "heritage"),
    "jeju-dongmun-market": ("jeju", "market"),
    "tapdong": ("jeju", "city"),
    "bijarim": ("jeju", "nature"),
    "woljeong-beach": ("jeju", "beach"),
    "yongnuni-oreum": ("jeju", "nature"),
    "sehwa-beach": ("jeju", "beach"),
    "sanbangsan": ("jeju", "mountain"),
    "yongmeori-coast": ("jeju", "nature"),
    "songaksan": ("jeju", "mountain"),
    "seopjikoji": ("jeju", "nature"),
}

IMG_FALLBACK = {
    "heritage": "Images/places/_types/heritage.jpg",
    "nature": "Images/places/_types/nature.jpg",
    "beach": "Images/places/_types/beach.jpg",
    "city": "Images/places/_types/city.jpg",
    "mountain": "Images/places/_types/mountain.jpg",
    "market": "Images/places/_types/market.jpg",
    "lake": "Images/places/_types/lake.jpg",
    "port": "Images/places/_types/port.jpg",
}


def slug_coords() -> dict[str, tuple[float, float]]:
    text = JS.read_text(encoding="utf-8")
    m = re.search(r"var SLUG_COORDS = \{([\s\S]*?)\n  \};", text)
    if not m:
        raise SystemExit("SLUG_COORDS not found")
    out = {}
    for slug, lat, lng in re.findall(r'"([^"]+)": \[(-?\d+\.?\d*), (-?\d+\.?\d*)\]', m.group(1)):
        out[slug] = (float(lat), float(lng))
    return out


def existing_slugs(text: str) -> set[str]:
    return set(re.findall(r'slug: "([^"]+)"', text))


def pick_image(slug: str, typ: str) -> str:
    candidates = [
        ROOT / f"Images/places/{typ}/{slug}.jpg",
        ROOT / f"Images/places/_courses/{slug}.jpg",
        ROOT / f"Images/places/heritage/{slug}.jpg",
        ROOT / f"Images/places/nature/{slug}.jpg",
        ROOT / f"Images/places/beach/{slug}.jpg",
        ROOT / f"Images/places/market/{slug}.jpg",
        ROOT / f"Images/places/city/{slug}.jpg",
        ROOT / f"Images/places/mountain/{slug}.jpg",
        ROOT / f"Images/places/lake/{slug}.jpg",
    ]
    for p in candidates:
        if p.exists():
            return str(p.relative_to(ROOT)).replace("\\", "/")
    return IMG_FALLBACK.get(typ, "Images/places/_types/city.jpg")


def main() -> None:
    text = COORDS.read_text(encoding="utf-8")
    have = existing_slugs(text)
    coords = slug_coords()
    lines = []
    for slug in sorted(KEEP):
        if slug in have:
            continue
        if slug not in coords:
            print("no coords", slug)
            continue
        lat, lng = coords[slug]
        region, typ = REGION_OF.get(slug, ("", "nature"))
        img = pick_image(slug, typ)
        note = slug.replace("-", " ").title()
        lines.append(
            f'  {{ slug: "{slug}", lat: {lat}, lng: {lng}, region: "{region}", type: "{typ}", note: "{note}", image: "{img}" }},'
        )
    if not lines:
        print("nothing to add")
        return
    block = "  /* Curated regional day-course landmarks */\n" + "\n".join(lines) + "\n"
    if not text.rstrip().endswith("];"):
        raise SystemExit("unexpected file ending")
    # insert before closing ];
    idx = text.rstrip().rfind("];")
    new = text[:idx].rstrip() + ",\n" + block + "];\n"
    COORDS.write_text(new, encoding="utf-8")
    print("added", len(lines))


if __name__ == "__main__":
    main()
