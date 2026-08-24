# -*- coding: utf-8 -*-
"""Add biyott, desserts, meals; dual shop images (storefront + menu)."""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
I18N = ROOT / "i18n"

# --- i18n content ---

COMMON_FIELDS = {
    "ko": {"menuPhoto": "대표 메뉴 사진"},
    "en": {"menuPhoto": "Signature menu photo"},
    "ja": {"menuPhoto": "看板メニュー写真"},
}

DISHES = {
    "malatang": {
        "ko": {
            "title": "마라탕",
            "desc": "취향대로 재료를 골라 끓여 먹는 매콤한 탕",
            "about": "마라탕은 중국식에서 온 매콤한 탕 요리로, 한국에서도 젊은층·관광객에게 인기입니다. 채소·면·고기·두부 등 재료를 고른 뒤 맵기 단계와 국물을 선택해 끓여 먹습니다.",
        },
        "en": {
            "title": "Malatang",
            "desc": "Build-your-own spicy hot pot soup",
            "about": "Malatang is a spicy hot-pot-style soup popular with young locals and travelers. Pick ingredients (veggies, noodles, meat, tofu), choose a spice level and broth, then simmer and eat.",
        },
        "ja": {
            "title": "マーラータン",
            "desc": "好みの具材を選んで煮込む辛いスープ",
            "about": "マーラータンは中国発の辛いスープ料理で、韓国でも若者や観光客に人気です。野菜・麺・肉・豆腐などを選び、辛さやスープを決めて煮込んで食べます。",
        },
    },
    "tteokbokki": {
        "ko": {
            "title": "떡볶이",
            "desc": "매콤달콤한 고추장 양념의 떡 요리",
            "about": "떡볶이는 가래떡을 고추장·고춧가루 양념에 볶아 먹는 한국의 대표 분식입니다. 길거리·분식집·편의점에서도 쉽게 만날 수 있고, 치즈·로제·국물떡볶이 등 변형이 많습니다.",
        },
        "en": {
            "title": "Tteokbokki",
            "desc": "Chewy rice cakes in sweet-spicy sauce",
            "about": "Tteokbokki is Korea’s classic street snack: chewy rice cakes simmered in a gochujang sauce. You’ll find it at street stalls, snack shops, and convenience stores — plus cheese, rose, and soup styles.",
        },
        "ja": {
            "title": "トッポッキ",
            "desc": "甘辛ソースの餅炒め",
            "about": "トッポッキは韓国の代表的な粉食。餅をコチュジャン系の甘辛ソースで煮込みます。屋台や粉食店、コンビニでも見つけやすく、チーズ・ロゼ・スープ型など種類も豊富です。",
        },
    },
    "nangman-sandwich": {
        "ko": {
            "title": "낭만 샌드",
            "desc": "두툼한 속재료가 보이는 디저트·브런치 샌드위치",
            "about": "낭만 샌드(낭만 샌드위치)는 SNS에서 유행한 두툼한 샌드위치 트렌드입니다. 계란·햄·채소·소스 등이 층층이 쌓여 단면이 예쁘고, 카페·베이커리에서 한 끼·디저트처럼 즐깁니다.",
        },
        "en": {
            "title": "Nangman sandwich",
            "desc": "Thick, photogenic dessert/brunch sandwiches",
            "about": "“Nangman sandwich” (romantic sandwich) is a viral thick-sandwich trend. Layers of egg, ham, veggies, and sauce make a photogenic cross-section — popular at cafés and bakeries as a meal or sweet-savory treat.",
        },
        "ja": {
            "title": "낭만サンド",
            "desc": "具がたっぷりの映えサンドウィッチ",
            "about": "낭만サンドはSNSで話題の厚みのあるサンドウィッチ。卵・ハム・野菜・ソースが層になり断面がきれいで、カフェやベーカリーで食事にもデザート感覚でも楽しめます。",
        },
    },
    "dubai-cookie": {
        "ko": {
            "title": "두바이 쫀득쿠키",
            "desc": "피스타치오·카다이프가 들어간 쫀득한 초코 쿠키",
            "about": "두바이 초콜릿 열풍에서 파생된 디저트로, 피스타치오 크림과 바삭한 카다이프(실 과자)를 넣은 쫀득한 쿠키·초코 과자류입니다. 베이커리·카페·디저트 전문점에서 시즌·한정으로 자주 나옵니다.",
        },
        "en": {
            "title": "Dubai chewy cookie",
            "desc": "Chewy chocolate cookie with pistachio & kadaif",
            "about": "Inspired by viral Dubai-style chocolate, these chewy cookies or chocolate treats layer pistachio cream and crunchy kadaif (shredded pastry). Often sold as seasonal specials at bakeries and dessert shops.",
        },
        "ja": {
            "title": "ドバイもちもちクッキー",
            "desc": "ピスタチオとカダイフ入りのもちもちチョコクッキー",
            "about": "ドバイチョコ人気から生まれたデザート。ピスタチオクリームとカリッとしたカダイフを入れたもちもちクッキー／チョコ菓子です。ベーカリーやカフェの季節限定でよく見かけます。",
        },
    },
    "butter-bread": {
        "ko": {
            "title": "버터빵",
            "desc": "버터를 듬뿍 바른 고소한 인기 베이커리 빵",
            "about": "버터빵은 부드러운 빵 안에 버터(또는 버터 크림)를 듬뿍 넣어 굽거나 바른 한국 베이커리 인기 메뉴입니다. 따뜻할 때 먹으면 버터가 녹아 고소하고, 유명 빵집·프랜차이즈 시그니처로도 많습니다.",
        },
        "en": {
            "title": "Butter bread",
            "desc": "Rich bakery bread loaded with butter",
            "about": "Butter bread is a Korean bakery favorite: soft bread filled or topped with generous butter (or butter cream). Best warm when the butter melts — a signature at many famous bakeries and chains.",
        },
        "ja": {
            "title": "バターパン",
            "desc": "バターたっぷりの人気ベーカリーパン",
            "about": "バターパンは柔らかいパンにバター（やバタークリーム）をたっぷり入れた韓国ベーカリーの定番。温かいとバターが溶けて香ばしく、有名店やチェーンの看板メニューにも多いです。",
        },
    },
    "tanghulu": {
        "ko": {
            "title": "탕후루",
            "desc": "과일에 설탕 코팅을 입힌 달콤바삭 간식",
            "about": "탕후루는 과일(딸기·샤인머스캣 등)에 설탕을 입혀 바삭하게 만든 중국식 길거리 간식으로, 한국에서도 디저트·길거리 음식으로 유행했습니다. 당분이 높으니 한두 꼬치만 즐기기 좋습니다.",
        },
        "en": {
            "title": "Tanghulu",
            "desc": "Fruit skewers with a crunchy sugar shell",
            "about": "Tanghulu is candied fruit on a stick (strawberry, shine muscat, etc.) with a crunchy sugar coating. It became a trendy street dessert in Korea too — quite sweet, so one or two skewers is usually enough.",
        },
        "ja": {
            "title": "タンフル",
            "desc": "果物に砂糖をまとった甘くてサクサクのおやつ",
            "about": "タンフルはイチゴやシャインマスカットなどに砂糖衣をまとった中国発の屋台スイーツで、韓国でも人気になりました。糖分が高いので1〜2本を楽しむのがおすすめです。",
        },
    },
    "yogurt-ice": {
        "ko": {
            "title": "요거트 아이스크림",
            "desc": "상큼한 요거트 아이스크림·소프트 전문점",
            "about": "요거트 아이스크림은 상큼한 맛과 가벼운 식감으로 디저트 카페에서 인기입니다. 토핑·과일·시리얼을 올려 먹고, 체인 브랜드를 중심으로 관광지에서도 쉽게 찾을 수 있습니다.",
        },
        "en": {
            "title": "Yogurt ice cream",
            "desc": "Tangy soft-serve yogurt dessert shops",
            "about": "Yogurt ice cream (soft serve) is popular for its tangy, lighter taste. Add fruit, cereal, or toppings — easy to find at chain dessert shops near tourist areas.",
        },
        "ja": {
            "title": "ヨーグルトアイス",
            "desc": "さっぱりヨーグルトソフトの専門店",
            "about": "ヨーグルトアイスは酸味と軽い食感が人気のデザート。フルーツやシリアルなどのトッピングで楽しみ、観光地でもチェーン店を見つけやすいです。",
        },
    },
    "bungeoppang": {
        "ko": {
            "title": "붕어빵",
            "desc": "붕어 모양 틀에 구운 길거리 겨울 간식",
            "about": "붕어빵은 붕어 모양 틀에 밀가루 반죽과 팥(또는 슈크림·피자 등)을 넣어 구운 한국의 대표 길거리 간식입니다. 겨울철 포장마차에서 특히 유명하고, 따뜻할 때 먹는 맛이 핵심입니다.",
        },
        "en": {
            "title": "Bungeoppang",
            "desc": "Fish-shaped street pastry, often filled with red bean",
            "about": "Bungeoppang is a fish-shaped pastry cooked in a mold, usually filled with sweet red bean (also cream or savory versions). A classic winter street snack — best eaten hot from the stall.",
        },
        "ja": {
            "title": "붕어パン（たい焼き風）",
            "desc": "魚型で焼く韓国の屋台おやつ",
            "about": "붕어パンは魚型の型で焼く韓国の屋台スイーツ。あんこが定番で、シュークリームやピザ味などもあります。冬の屋台で特に人気で、焼きたてが一番おいしいです。",
        },
    },
}

YOAJEONG = {
    "ko": {
        "name": "요아정 (Yoajeong)",
        "location": "전국 주요 상권·대학가",
        "menu": "요거트 아이스크림, 시즌 토핑",
        "price": "토핑·사이즈에 따라 다름 (보통 ₩4,000–8,000대)",
        "tip": "토핑을 너무 많이 올리면 양이 많아집니다. 줄이 길면 테이크아웃을 이용하세요.",
        "about": "요아정은 요거트 아이스크림으로 유명한 디저트 브랜드입니다. 상큼한 소프트와 다양한 토핑 조합이 인기입니다.",
    },
    "en": {
        "name": "Yoajeong",
        "location": "Major shopping areas & campuses nationwide",
        "menu": "Yogurt soft serve, seasonal toppings",
        "price": "Varies by size/toppings (often ₩4,000–8,000)",
        "tip": "Too many toppings can get heavy. Use takeout if the line is long.",
        "about": "Yoajeong is a popular yogurt soft-serve brand. People love the tangy base plus creative topping mixes.",
    },
    "ja": {
        "name": "ヨアジョン",
        "location": "全国の主要繁華街・大学街",
        "menu": "ヨーグルトソフト、季節トッピング",
        "price": "サイズ・トッピングによる（目安₩4,000–8,000）",
        "tip": "トッピングを盛りすぎると量が増えます。行列が長いときはテイクアウトも。",
        "about": "ヨアジョンはヨーグルトソフトで人気のデザートブランド。さっぱりしたベースとトッピングの組み合わせが人気です。",
    },
}

BIYOTT = {
    "ko": {
        "Title": "비요뜨",
        "Desc": "편의점 인기 요거트 디저트 (떠먹는 타입)",
        "pageTitle": "비요뜨 — 편의점 인기 요거트",
        "lead": "비요뜨는 한국 편의점에서 쉽게 사는 떠먹는 요거트 디저트입니다. 상큼달콤한 맛과 다양한 맛 라인업으로 외국인 관광객에게도 인기 있는 ‘편의점 디저트’입니다.",
        "whatTitle": "어떤 제품인가요?",
        "what": "냉장 코너의 컵 요거트입니다. 플레인·딸기·복숭아 등 맛이 있고, 뚜껑을 열어 스푼으로 바로 먹습니다. 브랜드·시리즈명은 편의점마다 비슷하게 진열됩니다.",
        "whyTitle": "왜 인기인가요?",
        "why": "가볍고 달콤해서 식사 후 디저트·간식으로 부담이 적습니다. 가격도 비교적 저렴하고, 숙소·이동 중에도 먹기 쉬워 여행 중 ‘한 입 디저트’로 자주 고릅니다.",
        "tipTitle": "구매·섭취 팁",
        "tip": "냉장 진열인지 확인하고 유통기한을 보세요. 더운 날엔 빨리 드시거나 아이스팩과 함께 이동하세요. 당이 있는 제품이 많으니 한 번에 여러 개는 부담될 수 있습니다.",
    },
    "en": {
        "Title": "Biyott",
        "Desc": "Popular cup yogurt dessert at convenience stores",
        "pageTitle": "Biyott — popular convenience-store yogurt",
        "lead": "Biyott is an easy-to-find cup yogurt dessert in Korean convenience stores. Tangy-sweet flavors and many varieties make it a tourist-friendly grab-and-go dessert.",
        "whatTitle": "What is it?",
        "what": "A refrigerated cup yogurt you eat with a spoon. Flavors include plain, strawberry, peach, and more. Similar products sit together in the dairy/dessert fridge.",
        "whyTitle": "Why tourists like it",
        "why": "It’s light, sweet, inexpensive, and easy to eat while traveling — a simple post-meal dessert without hunting for a café.",
        "tipTitle": "Tips",
        "tip": "Check the fridge section and expiration date. On hot days, eat soon or carry an ice pack. Many flavors are quite sweet — one cup is usually enough.",
    },
    "ja": {
        "Title": "ビヨット",
        "Desc": "コンビニ人気のカップヨーグルトデザート",
        "pageTitle": "ビヨット — コンビニ人気ヨーグルト",
        "lead": "ビヨットは韓国コンビニで手軽に買えるカップヨーグルトデザート。さっぱり甘く、味の種類も多く、旅行者にも人気のコンビニデザートです。",
        "whatTitle": "どんな商品？",
        "what": "冷蔵コーナーのカップヨーグルト。プレーン・イチゴ・ピーチなどがあり、フタを開けてスプーンで食べます。似た商品が並んでいることが多いです。",
        "whyTitle": "なぜ人気？",
        "why": "軽くて甘く、価格も手頃。食後のデザートや移動中のおやつに向き、カフェを探さなくても楽しめるのが魅力です。",
        "tipTitle": "購入・食べるときのヒント",
        "tip": "冷蔵陳列と賞味期限を確認を。暑い日は早めに食べるか保冷剤を。甘いものが多いので一度に何個もは重いこともあります。",
    },
}

DESSERT_SLUGS = [
    ("nangman-sandwich", "🥪"),
    ("dubai-cookie", "🍪"),
    ("butter-bread", "🧈"),
    ("tanghulu", "🍬"),
    ("yogurt-ice", "🍦"),
    ("bungeoppang", "🐟"),
]

MEAL_SLUGS = [
    ("malatang", "🌶️"),
    ("tteokbokki", "🔥"),
]

KIMBAP_SHOPS = [
    "wonjo-nude-cheese",
    "oto",
    "hanipsoban",
    "horangi",
    "sua-dang",
    "food2900",
    "bapdoduk",
    "seoho",
]

CAFE_BRANDS = [
    "mega-coffee",
    "starbucks",
    "compose-coffee",
    "ediya",
    "twosome-place",
    "paiks-coffee",
]


def update_i18n():
    for lang in ("ko", "en", "ja"):
        path = I18N / f"{lang}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data.setdefault("restaurantFields", {}).update(COMMON_FIELDS[lang])
        for slug, langs in DISHES.items():
            data.setdefault("dishes", {})[slug] = langs[lang]
        data.setdefault("restaurants", {})["yoajeong"] = YOAJEONG[lang]
        b = BIYOTT[lang]
        c = data.setdefault("convenience", {})
        c["productTitle"] = {"ko": "인기 제품", "en": "Popular products", "ja": "人気商品"}[lang]
        c["biyottTitle"] = b["Title"]
        c["biyottDesc"] = b["Desc"]
        for key in (
            "pageTitle",
            "lead",
            "whatTitle",
            "what",
            "whyTitle",
            "why",
            "tipTitle",
            "tip",
        ):
            c[f"biyott_{key}"] = b[key]
        intro = {
            "ko": "빙수·빵·카페부터 길거리·트렌드 디저트까지, 종류를 고른 뒤 브랜드(가게)를 확인해 보세요.",
            "en": "From bingsu, bread, and cafés to street and trend desserts — pick a type, then browse shops.",
            "ja": "ピンス・パン・カフェから屋台・トレンドデザートまで。種類を選んでからブランド店を確認してください。",
        }
        data.setdefault("dessertsIndex", {})["intro"] = intro[lang]
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("updated", path)


def meal_page(slug: str, emoji: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ko" data-i18n-title="dishes.{slug}.title">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{slug} | Korea Travel Guide</title>
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
      <a href="../index.html" data-i18n="misc.backFoods">← Back</a>
    </p>
    <h1>{emoji} <span data-i18n="dishes.{slug}.title">{slug}</span></h1>
    <img src="../../../../Images/foods/dishes/{slug}.jpg" width="100%" alt="{slug}" data-i18n-attr="alt:dishes.{slug}.title">
    <section class="intro">
      <h2 data-i18n="common.about">About</h2>
      <p data-i18n="dishes.{slug}.about"></p>
    </section>
    <h2 data-i18n="common.places">Places</h2>
    <p class="tabs-help" data-i18n="common.shopsComing"></p>
    <p data-i18n="common.emptyPlaces">등록된 곳이 아직 없습니다.</p>
  </main>
  <footer class="site-footer">
    <hr>
    <img src="../../../../Images/cover/footer-korea.png" width="100%" alt="Korea Travel">
    <p class="footer-note" data-i18n="common.footer">© Korea Travel Guide</p>
  </footer>
  <script src="../../../../i18n/messages.js"></script>
  <script src="../../../../js/i18n.js"></script>
</body>
</html>
"""


def dessert_dish_page(slug: str, emoji: str, places_html: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ko" data-i18n-title="dishes.{slug}.title">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{slug} | Korea Travel Guide</title>
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
      <a href="../index.html" data-i18n="misc.backDesserts">← Back</a>
    </p>
    <h1>{emoji} <span data-i18n="dishes.{slug}.title">{slug}</span></h1>
    <img src="../../../../Images/foods/dishes/{slug}.jpg" width="100%" alt="{slug}" data-i18n-attr="alt:dishes.{slug}.title">
    <section class="intro">
      <h2 data-i18n="common.about">About</h2>
      <p data-i18n="dishes.{slug}.about"></p>
    </section>
{places_html}
  </main>
  <footer class="site-footer">
    <hr>
    <img src="../../../../Images/cover/footer-korea.png" width="100%" alt="Korea Travel">
    <p class="footer-note" data-i18n="common.footer">© Korea Travel Guide</p>
  </footer>
  <script src="../../../../i18n/messages.js"></script>
  <script src="../../../../js/i18n.js"></script>
</body>
</html>
"""


EMPTY_PLACES = """    <h2 data-i18n="common.places">Places</h2>
    <p class="tabs-help" data-i18n="common.shopsComing"></p>
    <p data-i18n="common.emptyPlaces"></p>"""

YOAJEONG_PLACES = """    <h2 data-i18n="common.places">Places</h2>
    <div class="card-grid">
      <article class="card">
        <a href="./yoajeong.html">
          <img src="../../../../Images/foods/restaurants/desserts/yoajeong-menu.jpg" width="100%" alt="" data-i18n-attr="alt:restaurants.yoajeong.name">
        </a>
        <h2><span data-i18n="restaurants.yoajeong.name"></span></h2>
        <p data-i18n="restaurants.yoajeong.menu"></p>
        <p><a href="./yoajeong.html" data-i18n="common.viewMore">View more →</a></p>
      </article>
    </div>"""


def shop_detail(
    slug: str,
    back_dish_key: str,
    shop_img: str,
    menu_img: str,
    depth: str = "../../../../",
    include_region: bool = False,
    city: str | None = None,
    area: str | None = None,
) -> str:
    region = ""
    city_area_rows = ""
    if include_region and city and area:
        region = f'    <p class="region-badge"><span data-i18n="cities.{city}"></span> · <span data-i18n="areas.{area}"></span></p>\n'
        city_area_rows = f"""      <tr><th data-i18n="restaurantFields.city">City</th><td data-i18n="cities.{city}"></td></tr>
      <tr><th data-i18n="restaurantFields.area">Area</th><td data-i18n="areas.{area}"></td></tr>
"""
    return f"""<!DOCTYPE html>
<html lang="ko" data-i18n-title="restaurants.{slug}.name">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{slug}</title>
  <link rel="stylesheet" href="{depth}styles.css">
</head>
<body>
  <nav class="lang-switch" aria-label="Language">
    <button type="button" data-set-lang="ko">KR</button>
    <button type="button" data-set-lang="en">EN</button>
    <button type="button" data-set-lang="ja">JP</button>
  </nav>
  <header class="site-header">
    <a href="{depth}index.html" class="site-brand" data-i18n="common.brand">Korea Travel Guide</a>
  </header>
  <main class="page">
    <p class="back-link">
      <a href="./index.html">← <span data-i18n="{back_dish_key}"></span></a>
    </p>
    <h1 data-i18n="restaurants.{slug}.name"></h1>
{region}    <img class="shop-photo" src="{depth}{shop_img}" width="100%" alt="" data-i18n-attr="alt:restaurants.{slug}.name">
    <p data-i18n="restaurants.{slug}.about"></p>
    <table class="content-table">
      <tr><th data-i18n="restaurantFields.name"></th><td data-i18n="restaurants.{slug}.name"></td></tr>
{city_area_rows}      <tr><th data-i18n="restaurantFields.location"></th><td data-i18n="restaurants.{slug}.location"></td></tr>
      <tr><th data-i18n="restaurantFields.menu"></th><td data-i18n="restaurants.{slug}.menu"></td></tr>
      <tr><th data-i18n="restaurantFields.price"></th><td data-i18n="restaurants.{slug}.price"></td></tr>
    </table>
    <figure class="menu-photo">
      <figcaption data-i18n="restaurantFields.menuPhoto"></figcaption>
      <img src="{depth}{menu_img}" width="100%" alt="" data-i18n-attr="alt:restaurants.{slug}.menu">
    </figure>
    <div class="tip">
      <h3 data-i18n="common.tip">TIP</h3>
      <p data-i18n="restaurants.{slug}.tip"></p>
    </div>
  </main>
  <footer class="site-footer">
    <hr>
    <img src="{depth}Images/cover/footer-korea.png" width="100%" alt="Korea Travel">
    <p class="footer-note" data-i18n="common.footer"></p>
  </footer>
  <script src="{depth}i18n/messages.js"></script>
  <script src="{depth}js/i18n.js"></script>
</body>
</html>
"""


def biyott_page() -> str:
    return """<!DOCTYPE html>
<html lang="ko" data-i18n-title="convenience.biyott_pageTitle">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>biyott</title>
  <link rel="stylesheet" href="../../../styles.css">
</head>
<body>
  <nav class="lang-switch" aria-label="Language">
    <button type="button" data-set-lang="ko">KR</button>
    <button type="button" data-set-lang="en">EN</button>
    <button type="button" data-set-lang="ja">JP</button>
  </nav>
  <header class="site-header">
    <a href="../../../index.html" class="site-brand" data-i18n="common.brand">Korea Travel Guide</a>
  </header>
  <main class="page article-page">
    <p class="back-link"><a href="../index.html" data-i18n="convenience.backCombos"></a></p>
    <article class="combo-article">
      <img class="combo-article-hero" src="../../../Images/convenience/biyott.jpg" alt="" data-i18n-attr="alt:convenience.biyott_pageTitle">
      <h1 data-i18n="convenience.biyott_pageTitle"></h1>
      <p class="article-lead" data-i18n="convenience.biyott_lead"></p>
      <h2 data-i18n="convenience.biyott_whatTitle"></h2>
      <p data-i18n="convenience.biyott_what"></p>
      <h2 data-i18n="convenience.biyott_whyTitle"></h2>
      <p data-i18n="convenience.biyott_why"></p>
      <div class="tip">
        <h3 data-i18n="convenience.biyott_tipTitle"></h3>
        <p data-i18n="convenience.biyott_tip"></p>
      </div>
    </article>
  </main>
  <footer class="site-footer">
    <hr>
    <img src="../../../Images/cover/footer-korea.png" width="100%" alt="Korea Travel">
    <p class="footer-note" data-i18n="common.footer"></p>
  </footer>
  <script src="../../../i18n/messages.js"></script>
  <script src="../../../js/i18n.js"></script>
</body>
</html>
"""


def patch_convenience_index(html: str) -> str:
    if "biyott" in html:
        return html
    section = """
    <h2 class="section-heading" data-i18n="convenience.productTitle">인기 제품</h2>
    <div class="combo-grid">
      <a class="combo-card" href="./biyott/index.html">
        <img src="../../Images/convenience/biyott.jpg" alt="" data-i18n-attr="alt:convenience.biyottTitle">
        <div class="combo-body">
          <h3 data-i18n="convenience.biyottTitle"></h3>
          <p data-i18n="convenience.biyottDesc"></p>
          <span class="combo-more" data-i18n="convenience.readMore"></span>
        </div>
      </a>
    </div>

"""
    return html.replace(
        '<h2 class="section-heading" data-i18n="convenience.comboTitle">유행 꿀조합</h2>',
        section + '    <h2 class="section-heading" data-i18n="convenience.comboTitle">유행 꿀조합</h2>',
    )


def dessert_card(slug: str, emoji: str) -> str:
    return f"""      <article class="card">
        <a href="./{slug}/index.html">
          <img src="../../../Images/foods/dishes/{slug}.jpg" width="100%" alt="" data-i18n-attr="alt:dishes.{slug}.title">
        </a>
        <h2>{emoji} <span data-i18n="dishes.{slug}.title"></span></h2>
        <p data-i18n="dishes.{slug}.desc"></p>
        <p><a href="./{slug}/index.html" data-i18n="common.viewMore">View more →</a></p>
      </article>
"""


def meal_card(slug: str, emoji: str) -> str:
    return f"""      <article class="card">
        <a href="./{slug}/index.html">
          <img src="../../../Images/foods/dishes/{slug}.jpg" width="100%" alt="" data-i18n-attr="alt:dishes.{slug}.title">
        </a>
        <h2>{emoji} <span data-i18n="dishes.{slug}.title"></span></h2>
        <p data-i18n="dishes.{slug}.desc"></p>
        <p><a href="./{slug}/index.html" data-i18n="common.viewMore">View more →</a></p>
      </article>
"""


def patch_desserts_index(html: str) -> str:
    if "nangman-sandwich" in html:
        return html
    cards = "".join(dessert_card(s, e) for s, e in DESSERT_SLUGS)
    return html.replace("    </div>\n  </main>", cards + "    </div>\n  </main>")


def patch_meals_index(html: str) -> str:
    if "malatang" in html:
        return html
    cards = "".join(meal_card(s, e) for s, e in MEAL_SLUGS)
    return html.replace("    </div>\n  </main>", cards + "    </div>\n  </main>")


KIMBAP_META = {
    "wonjo-nude-cheese": ("서울", "종로"),
    "oto": ("서울", "용산·이태원"),
    "hanipsoban": ("서울", "용산·이태원"),
    "horangi": ("서울", "성북"),
    "sua-dang": ("서울", "성북"),
    "food2900": ("서울", "강남·압구정"),
    "bapdoduk": ("서울", "관악"),
    "seoho": ("서울", "서초·방배"),
}


def ensure_kimbap_menu_copies():
    base = ROOT / "Images" / "foods" / "restaurants" / "kimbap"
    for slug in KIMBAP_SHOPS:
        src = base / f"{slug}.jpg"
        dst = base / f"{slug}-menu.jpg"
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)
            print("copied menu placeholder", dst.name)


def rewrite_shop_pages():
    # Kimbap
    for slug in KIMBAP_SHOPS:
        city, area = KIMBAP_META[slug]
        html = shop_detail(
            slug,
            "dishes.kimbap.title",
            f"Images/foods/restaurants/kimbap/{slug}.jpg",
            f"Images/foods/restaurants/kimbap/{slug}-menu.jpg",
            include_region=True,
            city=city,
            area=area,
        )
        path = ROOT / "pages" / "foods" / "meals" / "kimbap" / f"{slug}.html"
        path.write_text(html, encoding="utf-8")
        print("rewrote", path)

    # Sulbing
    (ROOT / "pages" / "foods" / "desserts" / "bingsu" / "sulbing.html").write_text(
        shop_detail(
            "sulbing",
            "dishes.bingsu.title",
            "Images/foods/brands/sulbing.jpg",
            "Images/foods/restaurants/desserts/sulbing-menu.jpg",
        ),
        encoding="utf-8",
    )
    # Bread brands
    for slug in ("paris-baguette", "tous-les-jours"):
        (ROOT / "pages" / "foods" / "desserts" / "bread" / f"{slug}.html").write_text(
            shop_detail(
                slug,
                "dishes.bread.title",
                f"Images/foods/brands/{slug}.jpg",
                f"Images/foods/restaurants/desserts/{slug}-menu.jpg",
            ),
            encoding="utf-8",
        )
        print("rewrote bread", slug)

    # Cafe brands — storefront brand image + menu
    for slug in CAFE_BRANDS:
        brand = ROOT / "Images" / "foods" / "brands" / f"{slug}.jpg"
        menu = ROOT / "Images" / "foods" / "restaurants" / "desserts" / f"{slug}-menu.jpg"
        if not brand.exists() and menu.exists():
            shutil.copy2(menu, brand)
        (ROOT / "pages" / "foods" / "desserts" / "cafe" / f"{slug}.html").write_text(
            shop_detail(
                slug,
                "dishes.cafe.title",
                f"Images/foods/brands/{slug}.jpg",
                f"Images/foods/restaurants/desserts/{slug}-menu.jpg",
            ),
            encoding="utf-8",
        )
        print("rewrote cafe", slug)

    # Yoajeong
    ypath = ROOT / "pages" / "foods" / "desserts" / "yogurt-ice" / "yoajeong.html"
    ypath.parent.mkdir(parents=True, exist_ok=True)
    ypath.write_text(
        shop_detail(
            "yoajeong",
            "dishes.yogurt-ice.title",
            "Images/foods/brands/yoajeong.jpg",
            "Images/foods/restaurants/desserts/yoajeong-menu.jpg",
        ),
        encoding="utf-8",
    )
    print("wrote", ypath)


def patch_css():
    css_path = ROOT / "styles.css"
    css = css_path.read_text(encoding="utf-8")
    if ".menu-photo" in css:
        return
    block = """
.shop-photo {
  display: block;
  margin: 12px 0 20px;
}

.menu-photo {
  margin: 24px 0 16px;
  padding: 0;
}

.menu-photo figcaption {
  font-weight: 600;
  margin: 0 0 8px;
  font-size: 0.95rem;
}

.menu-photo img {
  display: block;
  border-radius: 8px;
}
"""
    css_path.write_text(css + block, encoding="utf-8")
    print("patched styles.css")


def main():
    update_i18n()
    patch_css()
    ensure_kimbap_menu_copies()

    # Biyott
    bdir = ROOT / "pages" / "convenience-store" / "biyott"
    bdir.mkdir(parents=True, exist_ok=True)
    (bdir / "index.html").write_text(biyott_page(), encoding="utf-8")
    conv = ROOT / "pages" / "convenience-store" / "index.html"
    conv.write_text(patch_convenience_index(conv.read_text(encoding="utf-8")), encoding="utf-8")
    print("updated convenience index + biyott")

    # Meals
    for slug, emoji in MEAL_SLUGS:
        d = ROOT / "pages" / "foods" / "meals" / slug
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(meal_page(slug, emoji), encoding="utf-8")
        print("wrote meal", slug)
    meals_idx = ROOT / "pages" / "foods" / "meals" / "index.html"
    meals_idx.write_text(patch_meals_index(meals_idx.read_text(encoding="utf-8")), encoding="utf-8")

    # Desserts
    for slug, emoji in DESSERT_SLUGS:
        d = ROOT / "pages" / "foods" / "desserts" / slug
        d.mkdir(parents=True, exist_ok=True)
        places = YOAJEONG_PLACES if slug == "yogurt-ice" else EMPTY_PLACES
        (d / "index.html").write_text(dessert_dish_page(slug, emoji, places), encoding="utf-8")
        print("wrote dessert", slug)
    desserts_idx = ROOT / "pages" / "foods" / "desserts" / "index.html"
    desserts_idx.write_text(patch_desserts_index(desserts_idx.read_text(encoding="utf-8")), encoding="utf-8")

    rewrite_shop_pages()
    print("done")


if __name__ == "__main__":
    main()
