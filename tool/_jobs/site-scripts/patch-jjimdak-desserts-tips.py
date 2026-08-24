# -*- coding: utf-8 -*-
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
I18N = ROOT / "i18n"


def load(lang):
    return json.loads((I18N / f"{lang}.json").read_text(encoding="utf-8"))


def save(lang, data):
    (I18N / f"{lang}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


PATCH = {
    "ko": {
        "dishes": {
            "jjimdak": {
                "title": "찜닭",
                "desc": "매콤달콤한 양념에 닭과 당면을 졸인 요리",
                "about": "찜닭은 닭고기와 감자·당근·당면을 매콤달콤한 간장·고추장 양념에 졸여 낸 한식입니다. 안동찜닭이 유명하며, 여럿이 나눠 먹기 좋습니다.",
            },
            "bingsu": {
                "title": "빙수",
                "desc": "잘게 간 얼음 위에 토핑을 올린 디저트",
                "about": "빙수는 우유 얼음이나 얼음을 곱게 갈아 팥·과일·떡·아이스크림 등을 올린 한국식 디저트입니다. 여름에 특히 인기이며 체인·카페에서 쉽게 만날 수 있습니다.",
            },
            "bread": {
                "title": "빵·베이커리",
                "desc": "한국 베이커리 체인과 인기 빵",
                "about": "한국에는 파리바게뜨·뚜레쥬르 같은 베이커리 체인이 전국에 많습니다. 식사 대용 빵부터 디저트 빵까지 종류가 다양합니다.",
            },
            "sulbing": {
                "title": "설빙",
                "desc": "인절미·과일 등 토핑 빙수 브랜드",
                "about": "설빙은 한국에서 쉽게 찾을 수 있는 빙수 전문 브랜드입니다. 인절미빙수 등 시그니처 메뉴가 유명합니다.",
            },
            "paris-baguette": {
                "title": "파리바게뜨",
                "desc": "전국 어디서나 만나는 베이커리 브랜드",
                "about": "파리바게뜨는 한국에서 가장 흔한 베이커리 체인 중 하나입니다. 식사빵·케이크·커피를 함께 구매할 수 있습니다.",
            },
            "tous-les-jours": {
                "title": "뚜레쥬르",
                "desc": "빵과 케이크가 다양한 베이커리 브랜드",
                "about": "뚜레쥬르는 부드러운 식빵과 디저트 빵으로 잘 알려진 베이커리 브랜드입니다.",
            },
        },
        "dessertsIndex": {
            "intro": "빙수·빵처럼 종류를 고른 뒤, 브랜드(가게)를 확인해 보세요.",
            "title": "디저트",
        },
        "tips": {
            "weekendTitle": "주말·연휴 숙소",
            "weekendMistake": "주말에도 평일과 같은 가격일 거라 생각하는 것",
            "weekendBody": "금·토·일이나 연휴·성수기에는 호텔·게스트하우스 요금이 평일보다 크게 오르는 경우가 많습니다. 가능하면 평일 숙박을 섞거나, 미리 예약·가격 비교(야놀자·여기어때 등)를 하세요. 당일 예약은 더 비쌀 수 있습니다.",
        },
        "restaurants": {
            "sulbing": {
                "name": "설빙",
                "location": "전국 주요 상권·쇼핑몰",
                "menu": "인절미빙수 등 시그니처 빙수",
                "price": "메뉴에 따라 다름 (보통 ₩1만대)",
                "tip": "인절미·망고·초코 등 시즌 메뉴가 자주 바뀝니다. 앱·키오스크 주문이 있는 매장도 있습니다.",
                "about": "설빙의 대표 메뉴는 인절미빙수입니다. 고소한 콩가루와 떡·팥·아이스크림이 어우러집니다.",
            },
            "paris-baguette": {
                "name": "파리바게뜨",
                "location": "전국 편의점·역·상가 인근",
                "menu": "마늘바게트·샌드위치·케이크 등",
                "price": "빵 종류에 따라 다름",
                "tip": "아침·점심 식사 대용으로 샌드위치·김밥형 메뉴도 많습니다. 매장마다 재고가 다릅니다.",
                "about": "여행 중 가볍게 때울 때 유용한 베이커리입니다. 마늘빵·크림치즈 계열 메뉴가 인기입니다.",
            },
            "tous-les-jours": {
                "name": "뚜레쥬르",
                "location": "전국 주요 상권",
                "menu": "식빵·페스츄리·케이크 등",
                "price": "빵 종류에 따라 다름",
                "tip": "부드러운 식빵과 달달한 디저트 빵이 강점입니다. 커피와 함께 포장해 숙소로 가져가기 좋습니다.",
                "about": "뚜레쥬르에서 자주 찾는 대표 빵·페이스트리 구성입니다.",
            },
        },
    },
    "en": {
        "dishes": {
            "jjimdak": {
                "title": "Jjimdak",
                "desc": "Sweet-spicy braised chicken with glass noodles",
                "about": "Jjimdak is chicken braised with potato, carrot, and glass noodles in a sweet-spicy soy/gochujang sauce. Andong jjimdak is the famous style — great for sharing.",
            },
            "bingsu": {
                "title": "Bingsu",
                "desc": "Korean shaved ice with toppings",
                "about": "Bingsu is finely shaved milk ice or ice topped with red beans, fruit, rice cake, and ice cream. Especially popular in summer at dessert cafés and chains.",
            },
            "bread": {
                "title": "Bread · Bakery",
                "desc": "Korean bakery chains and popular breads",
                "about": "Korea has bakery chains like Paris Baguette and Tous Les Jours nationwide — from meal breads to sweet pastries.",
            },
            "sulbing": {
                "title": "Sulbing",
                "desc": "Popular bingsu dessert brand",
                "about": "Sulbing is an easy-to-find Korean bingsu brand known for injeolmi (soybean powder) shaved ice.",
            },
            "paris-baguette": {
                "title": "Paris Baguette",
                "desc": "Nationwide bakery brand",
                "about": "One of Korea’s most common bakery chains — bread, cakes, and coffee in one stop.",
            },
            "tous-les-jours": {
                "title": "Tous Les Jours",
                "desc": "Bakery brand with soft breads and cakes",
                "about": "Tous Les Jours is known for soft milk breads and dessert pastries.",
            },
        },
        "dessertsIndex": {
            "intro": "Pick a type (bingsu or bread), then browse brand shops.",
            "title": "Desserts",
        },
        "tips": {
            "weekendTitle": "Weekend lodging",
            "weekendMistake": "Assuming weekend hotel rates match weekdays",
            "weekendBody": "Friday–Sunday and holidays often cost much more than weekdays. Mix in weekday stays when you can, and compare prices early on booking apps. Same-day bookings can be pricier.",
        },
        "restaurants": {
            "sulbing": {
                "name": "Sulbing",
                "location": "Major shopping areas nationwide",
                "menu": "Injeolmi bingsu and seasonal flavors",
                "price": "Varies (often around ₩10,000+)",
                "tip": "Seasonal menus rotate often. Some shops have kiosk/app ordering.",
                "about": "Sulbing’s signature is injeolmi bingsu with soybean powder, rice cake, red bean, and ice cream.",
            },
            "paris-baguette": {
                "name": "Paris Baguette",
                "location": "Near stations and shopping streets nationwide",
                "menu": "Garlic baguette, sandwiches, cakes, and more",
                "price": "Varies by item",
                "tip": "Handy for quick breakfasts and lunches. Stock differs by store.",
                "about": "A convenient bakery stop while traveling — garlic bread and cream-cheese items are popular.",
            },
            "tous-les-jours": {
                "name": "Tous Les Jours",
                "location": "Major commercial areas nationwide",
                "menu": "Milk bread, pastries, cakes, and more",
                "price": "Varies by item",
                "tip": "Soft breads pair well with coffee to take back to your stay.",
                "about": "Typical Tous Les Jours picks: soft breads and sweet pastries.",
            },
        },
    },
    "ja": {
        "dishes": {
            "jjimdak": {
                "title": "チムタク",
                "desc": "甘辛く煮込んだ鶏肉と春雨",
                "about": "チムタクは鶏肉・じゃがいも・にんじん・春雨を甘辛いヤンニョムで煮た料理です。安東チムタクが有名で、シェア向きです。",
            },
            "bingsu": {
                "title": "ピンス",
                "desc": "かき氷の上にトッピングを載せたデザート",
                "about": "ピンスは牛乳氷などを細かく削り、小豆・フルーツ・餅・アイスなどを載せた韓国式デザートです。夏に特に人気です。",
            },
            "bread": {
                "title": "パン・ベーカリー",
                "desc": "韓国のベーカリーチェーンと人気のパン",
                "about": "韓国にはパリバゲットやトゥレジュールなどのベーカリーチェーンが全国にあります。",
            },
            "sulbing": {
                "title": "ソルビン",
                "desc": "ピンス専門ブランド",
                "about": "ソルビンは韓国で見つけやすいピンスブランドで、インジョルミピンスが有名です。",
            },
            "paris-baguette": {
                "title": "パリバゲット",
                "desc": "全国にあるベーカリーブランド",
                "about": "韓国で最も身近なベーカリーチェーンの一つです。",
            },
            "tous-les-jours": {
                "title": "トゥレジュール",
                "desc": "パンとケーキが豊富なベーカリー",
                "about": "柔らかい食パンやデザートパンで知られるブランドです。",
            },
        },
        "dessertsIndex": {
            "intro": "ピンスやパンなど種類を選んでから、ブランド店を確認してください。",
            "title": "デザート",
        },
        "tips": {
            "weekendTitle": "週末・連休の宿",
            "weekendMistake": "週末も平日と同じ料金だと思い込むこと",
            "weekendBody": "金・土・日や連休・繁忙期はホテルやゲストハウス料金が大きく上がることが多いです。可能なら平日を混ぜ、早めに比較・予約を。当日予約はさらに高いことがあります。",
        },
        "restaurants": {
            "sulbing": {
                "name": "ソルビン",
                "location": "全国の主な繁華街・モール",
                "menu": "インジョルミピンスなど",
                "price": "メニューによる（目安₩1万台）",
                "tip": "季節メニューがよく変わります。キオスク注文の店もあります。",
                "about": "代表はインジョルミピンス。きな粉・餅・小豆・アイスが合わさります。",
            },
            "paris-baguette": {
                "name": "パリバゲット",
                "location": "全国の駅・商店街付近",
                "menu": "にんにくバゲット・サンド・ケーキなど",
                "price": "商品による",
                "tip": "朝食・昼食代わりにも便利。店舗で品揃えが違います。",
                "about": "旅行中の軽食に便利。にんにくパン系が人気です。",
            },
            "tous-les-jours": {
                "name": "トゥレジュール",
                "location": "全国の主な繁華街",
                "menu": "食パン・ペストリー・ケーキなど",
                "price": "商品による",
                "tip": "柔らかいパンはコーヒーと一緒に宿へ持ち帰りやすいです。",
                "about": "トゥレジュールでよく選ばれるパン・ペストリーです。",
            },
        },
    },
}


def deep_merge(base, extra):
    for k, v in extra.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            deep_merge(base[k], v)
        else:
            base[k] = v


for lang, patch in PATCH.items():
    data = load(lang)
    deep_merge(data, patch)
    save(lang, data)
    print("patched", lang)
