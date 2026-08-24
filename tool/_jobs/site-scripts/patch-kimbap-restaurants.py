# -*- coding: utf-8 -*-
"""Bulk content updates for guidebook v2 requests."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
I18N = ROOT / "i18n"


def load(lang: str) -> dict:
    return json.loads((I18N / f"{lang}.json").read_text(encoding="utf-8"))


def save(lang: str, data: dict) -> None:
    (I18N / f"{lang}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def deep_set(d: dict, path: str, value):
    keys = path.split(".")
    cur = d
    for k in keys[:-1]:
        cur = cur.setdefault(k, {})
    cur[keys[-1]] = value


KO_RESTAURANTS = {
    "wonjo-nude-cheese": {
        "name": "원조누드치즈김밥 41호",
        "location": "서울 종로구 광장시장",
        "menu": "누드김밥, 잡채김밥",
        "price": "약 ₩5,000–7,000",
        "tip": "광장시장 골목에 있습니다. 누드는 김 없이 밥·속이 바깥으로 보이는 스타일이고, 잡채김밥도 인기입니다. 줄이 길면 포장 후 시장 안에서 드세요.",
        "about": "광장시장의 대표 김밥집. 누드김밥과 잡채를 넣은 김밥으로 유명합니다.",
    },
    "oto": {
        "name": "오토 김밥",
        "location": "서울 용산구 스페이스소마빌딩 1층",
        "menu": "고추냉이 김밥",
        "price": "약 ₩6,000대",
        "tip": "와사비(고추냉이) 향이 선명합니다. 매운맛에 약하면 미리 말해 보세요. 용산 일대 방문 시 들르기 좋습니다.",
        "about": "고추냉이를 포인트로 한 김밥 전문점입니다.",
    },
    "horangi": {
        "name": "호랑이 김밥",
        "location": "서울 성북구 성북동",
        "menu": "꽃등심 불고기 김밥",
        "price": "약 ₩8,000대",
        "tip": "꽃등심 불고기를 넣어 든든합니다. 성북동은 골목이 많아 지도 앱으로 위치를 확인하세요.",
        "about": "꽃등심 불고기를 넣은 프리미엄 김밥으로 알려져 있습니다.",
    },
    "food2900": {
        "name": "FOOD 2900",
        "location": "서울 강남구 압구정로데오",
        "menu": "소세지 김밥",
        "price": "약 ₩2,900–",
        "tip": "가성비 소세지 김밥이 대표입니다. 압구정 로데오 쇼핑·카페 동선에 맞춰 방문하기 좋습니다.",
        "about": "압구정 로데오의 가성비 김밥·간편식 스폿입니다.",
    },
    "sua-dang": {
        "name": "수아당",
        "location": "서울 성북구 동선동",
        "menu": "참치 키토 김밥",
        "price": "약 ₩7,000대",
        "tip": "밥 양을 줄인 키토 스타일 참치김밥입니다. 성신여대·동선동 일대에서 찾기 쉽습니다.",
        "about": "참치를 넣은 키토(저탄수) 스타일 김밥으로 유명한 가게입니다.",
    },
    "bapdoduk": {
        "name": "밥도둑김밥",
        "location": "서울 관악구",
        "menu": "계란폭탄 김밥",
        "price": "약 ₩5,000–7,000",
        "tip": "계란을 듬뿍 넣은 ‘계란폭탄’ 김밥이 대표 메뉴입니다. 관악·서울대 입구 쪽에서 찾기 좋습니다.",
        "about": "계란을 푸짐하게 넣은 김밥으로 입소문이 난 가게입니다.",
    },
    "seoho": {
        "name": "서호김밥",
        "location": "서울 서초구 방배동",
        "menu": "다시마 김밥",
        "price": "약 ₩5,000대",
        "tip": "다시마로 감싼 김밥이라 일반 김과 식감·향이 다릅니다. 방배동 지도에서 상호를 검색하세요.",
        "about": "다시마를 활용한 김밥이 시그니처입니다.",
    },
    "hanipsoban": {
        "name": "한입소반",
        "location": "서울 용산구 숙대입구역 인근",
        "menu": "묵은지 김밥, 삼겹살 김밥",
        "price": "약 ₩6,000–8,000",
        "tip": "묵은지·삼겹살 김밥으로 유명합니다. 숙대입구역에서 도보로 이동할 수 있습니다.",
        "about": "묵은지와 삼겹살을 넣은 김밥으로 잘 알려진 용산 맛집입니다.",
    },
}

EN_RESTAURANTS = {
    "wonjo-nude-cheese": {
        "name": "Wonjo Nude Cheese Kimbap No.41",
        "location": "Gwangjang Market, Jongno-gu, Seoul",
        "menu": "Nude kimbap, japchae kimbap",
        "price": "About ₩5,000–7,000",
        "tip": "Inside Gwangjang Market alleys. Nude style has no outer seaweed wrap; japchae kimbap is also popular.",
        "about": "A Gwangjang Market classic known for nude and japchae kimbap.",
    },
    "oto": {
        "name": "Oto Kimbap",
        "location": "Space Soma Building 1F, Yongsan-gu, Seoul",
        "menu": "Wasabi (hot mustard) kimbap",
        "price": "About ₩6,000",
        "tip": "Clear wasabi kick — ask for milder if needed.",
        "about": "Specialty kimbap with a wasabi accent.",
    },
    "horangi": {
        "name": "Horangi Kimbap",
        "location": "Seongbuk-dong, Seongbuk-gu, Seoul",
        "menu": "Flower sirloin bulgogi kimbap",
        "price": "About ₩8,000",
        "tip": "Hearty premium bulgogi filling. Use a map app in Seongbuk-dong.",
        "about": "Known for flower-sirloin bulgogi kimbap.",
    },
    "food2900": {
        "name": "FOOD 2900",
        "location": "Apgujeong Rodeo, Gangnam-gu, Seoul",
        "menu": "Sausage kimbap",
        "price": "From about ₩2,900",
        "tip": "Budget-friendly sausage kimbap near Apgujeong Rodeo.",
        "about": "Value kimbap spot in Apgujeong Rodeo.",
    },
    "sua-dang": {
        "name": "Sua-dang",
        "location": "Dongseon-dong, Seongbuk-gu, Seoul",
        "menu": "Tuna keto kimbap",
        "price": "About ₩7,000",
        "tip": "Lower-rice keto-style tuna roll near Dongseon-dong / Sungshin area.",
        "about": "Famous for tuna keto-style kimbap.",
    },
    "bapdoduk": {
        "name": "Bapdoduk Kimbap",
        "location": "Gwanak-gu, Seoul",
        "menu": "Egg-bomb kimbap",
        "price": "About ₩5,000–7,000",
        "tip": "Loaded with egg — popular near Gwanak / Seoul National University area.",
        "about": "Known for egg-packed ‘egg bomb’ kimbap.",
    },
    "seoho": {
        "name": "Seoho Kimbap",
        "location": "Bangbae-dong, Seocho-gu, Seoul",
        "menu": "Kelp (dashima) kimbap",
        "price": "About ₩5,000",
        "tip": "Wrapped with kelp instead of regular gim — different aroma and bite.",
        "about": "Signature kelp-wrapped kimbap.",
    },
    "hanipsoban": {
        "name": "Hanip Soban",
        "location": "Near Sookmyung Women’s Univ. Station, Yongsan-gu, Seoul",
        "menu": "Aged kimchi kimbap, pork belly kimbap",
        "price": "About ₩6,000–8,000",
        "tip": "Walkable from Sookmyung Women’s University Station.",
        "about": "Popular for aged-kimchi and samgyeopsal kimbap.",
    },
}

JA_RESTAURANTS = {
    "wonjo-nude-cheese": {
        "name": "元祖ヌードチーズキンパ41号",
        "location": "ソウル鍾路区・広蔵市場",
        "menu": "ヌードキンパ、チャプチェキンパ",
        "price": "約₩5,000–7,000",
        "tip": "広蔵市場の路地にあります。ヌードは海苔なしスタイル。",
        "about": "広蔵市場の定番。ヌードとチャプチェキンパが有名です。",
    },
    "oto": {
        "name": "オトキンパ",
        "location": "ソウル龍山区スペースソマビル1階",
        "menu": "わさびキンパ",
        "price": "約₩6,000台",
        "tip": "わさびの風味がはっきりしています。",
        "about": "わさびをポイントにしたキンパ専門店です。",
    },
    "horangi": {
        "name": "ホランイキンパ",
        "location": "ソウル城北区城北洞",
        "menu": "花灯心プルコギキンパ",
        "price": "約₩8,000台",
        "tip": "ボリュームのあるプルコギ入り。地図アプリで確認を。",
        "about": "花灯心プルコギキンパで知られます。",
    },
    "food2900": {
        "name": "FOOD 2900",
        "location": "ソウル江南区狎鴎亭ロデオ",
        "menu": "ソーセージキンパ",
        "price": "約₩2,900〜",
        "tip": "コスパ良いソーセージキンパが代表です。",
        "about": "狎鴎亭ロデオのコスパキンパスポットです。",
    },
    "sua-dang": {
        "name": "スアダン",
        "location": "ソウル城北区東仙洞",
        "menu": "ツナ・ケトキンパ",
        "price": "約₩7,000台",
        "tip": "ご飯少なめのケトスタイル。東仙洞周辺。",
        "about": "ツナのケトスタイルキンパで有名です。",
    },
    "bapdoduk": {
        "name": "パプドドゥクキンパ",
        "location": "ソウル冠岳区",
        "menu": "卵爆弾キンパ",
        "price": "約₩5,000–7,000",
        "tip": "卵たっぷりの看板メニュー。冠岳周辺。",
        "about": "卵をたっぷり入れたキンパで話題の店です。",
    },
    "seoho": {
        "name": "ソホキンパ",
        "location": "ソウル瑞草区方背洞",
        "menu": "ダシマ（昆布）キンパ",
        "price": "約₩5,000台",
        "tip": "一般の海苔ではなく昆布で巻きます。",
        "about": "ダシマ巻きキンパがシグネチャーです。",
    },
    "hanipsoban": {
        "name": "ハニプソバン",
        "location": "ソウル龍山区・淑大入口駅付近",
        "menu": "熟成キムチキンパ、サムギョプサルキンパ",
        "price": "約₩6,000–8,000",
        "tip": "淑大入口駅から徒歩圏です。",
        "about": "熟成キムチとサムギョプサルキンパで知られます。",
    },
}


def restaurant_html(slug: str, city_area_keys: tuple[str, str]) -> str:
    city, area = city_area_keys
    img = f"../../../../Images/foods/restaurants/kimbap/{slug}.jpg"
    return f"""<!DOCTYPE html>
<html lang="ko" data-i18n-title="restaurants.{slug}.name">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{slug}</title>
  <link rel="stylesheet" href="../../../../styles.css">
</head>
<body>
  <nav class="lang-switch" aria-label="Language">
    <button type="button" data-set-lang="ko">KR</button>
    <button type="button" data-set-lang="en">EN</button>
    <button type="button" data-set-lang="ja">JP</button>
  </nav>
  <header class="site-header">
    <a href="../../../../index.html" class="site-brand" data-i18n="common.brand">Korea Travel Guide</a>
  </header>
  <main class="page">
    <p class="back-link">
      <a href="./index.html">← <span data-i18n="dishes.kimbap.title"></span></a>
    </p>
    <h1 data-i18n="restaurants.{slug}.name"></h1>
    <p class="region-badge"><span data-i18n="cities.{city}"></span> · <span data-i18n="areas.{area}"></span></p>
    <img src="{img}" width="100%" alt="" data-i18n-attr="alt:restaurants.{slug}.name">
    <p data-i18n="restaurants.{slug}.about"></p>
    <table class="content-table">
      <tr><th data-i18n="restaurantFields.name"></th><td data-i18n="restaurants.{slug}.name"></td></tr>
      <tr><th data-i18n="restaurantFields.city"></th><td data-i18n="cities.{city}"></td></tr>
      <tr><th data-i18n="restaurantFields.area"></th><td data-i18n="areas.{area}"></td></tr>
      <tr><th data-i18n="restaurantFields.location"></th><td data-i18n="restaurants.{slug}.location"></td></tr>
      <tr><th data-i18n="restaurantFields.menu"></th><td data-i18n="restaurants.{slug}.menu"></td></tr>
      <tr><th data-i18n="restaurantFields.price"></th><td data-i18n="restaurants.{slug}.price"></td></tr>
    </table>
    <div class="tip">
      <h3 data-i18n="common.tip">TIP</h3>
      <p data-i18n="restaurants.{slug}.tip"></p>
    </div>
  </main>
  <footer class="site-footer">
    <hr>
    <img src="../../../../Images/cover/footer-korea.png" width="100%" alt="Korea Travel">
    <p class="footer-note" data-i18n="common.footer"></p>
  </footer>
  <script src="../../../../i18n/messages.js"></script>
  <script src="../../../../js/i18n.js"></script>
</body>
</html>
"""


NEW_SLUGS = {
    "sua-dang": ("서울", "성북"),
    "bapdoduk": ("서울", "관악"),
    "seoho": ("서울", "서초·방배"),
    "hanipsoban": ("서울", "용산·이태원"),
}


def patch_restaurants():
    for lang, blob in (("ko", KO_RESTAURANTS), ("en", EN_RESTAURANTS), ("ja", JA_RESTAURANTS)):
        data = load(lang)
        data.setdefault("areas", {})
        if lang == "ko":
            data["areas"]["관악"] = "관악"
            data["areas"]["서초·방배"] = "서초·방배"
        elif lang == "en":
            data["areas"]["관악"] = "Gwanak"
            data["areas"]["서초·방배"] = "Seocho · Bangbae"
        else:
            data["areas"]["관악"] = "冠岳"
            data["areas"]["서초·방배"] = "瑞草·方背"
        data.setdefault("restaurants", {})
        for slug, fields in blob.items():
            data["restaurants"].setdefault(slug, {}).update(fields)
        # enrich sundubu about
        if "sundubu-jjigae" in data.get("dishes", {}):
            if lang == "ko":
                data["dishes"]["sundubu-jjigae"]["about"] = (
                    "순두부찌개는 부드러운 순두부를 매콤한 국물에 끓인 찌개입니다. "
                    "계란을 깨 넣어 먹거나, 공기밥·김치와 함께 먹습니다. 외국인에게도 접근하기 쉬운 한식입니다."
                )
                data["dishes"]["sundubu-jjigae"]["desc"] = "부드러운 순두부를 넣은 매콤한 찌개"
            elif lang == "en":
                data["dishes"]["sundubu-jjigae"]["about"] = (
                    "Sundubu-jjigae is a spicy soft-tofu stew. Crack an egg into the bubbling pot and eat with rice and kimchi — an easy Korean classic for visitors."
                )
            else:
                data["dishes"]["sundubu-jjigae"]["about"] = (
                    "スンドゥブチゲは柔らかい純豆腐を辛いスープで煮たチゲです。卵を落としてご飯やキムチと一緒に。外国人にも食べやすい韓国料理です。"
                )
        save(lang, data)
        print("restaurants patched", lang)

    out_dir = ROOT / "pages/foods/meals/kimbap"
    for slug, keys in NEW_SLUGS.items():
        path = out_dir / f"{slug}.html"
        path.write_text(restaurant_html(slug, keys), encoding="utf-8")
        print("wrote", path.name)
        # placeholder image: copy kimbap dish photo if missing
        img = ROOT / f"Images/foods/restaurants/kimbap/{slug}.jpg"
        if not img.exists():
            src = ROOT / "Images/foods/dishes/kimbap.jpg"
            shutil.copy(src, img)
            print("placeholder img", slug)


def main():
    patch_restaurants()


if __name__ == "__main__":
    main()
