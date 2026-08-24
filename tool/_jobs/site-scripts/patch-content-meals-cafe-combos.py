# -*- coding: utf-8 -*-
"""Update i18n + create convenience combo / cafe dessert pages."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
I18N = ROOT / "i18n"

COMMON_PATCH = {
    "ko": {
        "shopsHelp": "아래 추천 가게(상호)를 눌러 자세히 보세요.",
        "shopsComing": "추천 가게는 앞으로 추가될 예정입니다. 지역 탭 대신 가게 이름으로 안내합니다.",
    },
    "en": {
        "shopsHelp": "Tap a recommended shop below for details.",
        "shopsComing": "Recommended shops will be added soon. We list places by shop name, not by region tabs.",
    },
    "ja": {
        "shopsHelp": "下のおすすめ店（店名）をタップして詳細を見てください。",
        "shopsComing": "おすすめ店は今後追加予定です。地域タブではなく店名で案内します。",
    },
}

DISHES_CAFE = {
    "ko": {
        "title": "카페",
        "desc": "한국에서 자주 찾는 커피 체인",
        "about": "한국에는 합리적인 가격의 테이크아웃 카페부터 디저트·브런치까지 갖춘 카페 체인까지 다양합니다. 관광지·지하철역 근처에서도 쉽게 찾을 수 있어, 여행 중 휴식·충전 장소로 쓰기 좋습니다.",
    },
    "en": {
        "title": "Café",
        "desc": "Popular coffee chains in Korea",
        "about": "Korea has everything from value takeout coffee shops to café chains with desserts and light meals. You’ll find them near tourist spots and subway stations — handy for a break while traveling.",
    },
    "ja": {
        "title": "カフェ",
        "desc": "韓国でよく使うコーヒチェーン",
        "about": "韓国にはコスパ重視のテイクアウトカフェから、デザートや軽食まで揃うチェーンまで多様です。観光地や地下鉄駅の近くでも見つけやすく、旅行中の休憩・充電スポットに便利です。",
    },
}

DESSERTS_INTRO = {
    "ko": "빙수·빵·카페처럼 종류를 고른 뒤, 브랜드(가게)를 확인해 보세요.",
    "en": "Pick a type (bingsu, bread, or café), then browse brand shops.",
    "ja": "ピンス・パン・カフェなど種類を選んでから、ブランド店を確認してください。",
}

RESTAURANTS = {
    "mega-coffee": {
        "ko": {
            "name": "메가커피 (Mega Coffee)",
            "location": "전국 주요 상권·역세권",
            "menu": "아메리카노, 시즌 음료, 디저트",
            "price": "아메리카노 기준 비교적 저렴 (보통 ₩2,000대)",
            "tip": "테이크아웃이 기본인 매장이 많습니다. 앱 쿠폰·사이즈 업 행사를 확인해 보세요.",
            "about": "합리적인 가격으로 유명한 커피 프랜차이즈입니다. 관광지에서도 자주 보이며, 빠르게 커피를 마시고 싶을 때 편리합니다.",
        },
        "en": {
            "name": "Mega Coffee",
            "location": "Major shopping areas & near stations nationwide",
            "menu": "Americano, seasonal drinks, desserts",
            "price": "Often budget-friendly (Americano around ₩2,000s)",
            "tip": "Many shops are takeout-focused. Check app coupons and size-up deals.",
            "about": "A value coffee chain popular across Korea. Easy to find near tourist areas when you want a quick cup.",
        },
        "ja": {
            "name": "メガコーヒー",
            "location": "全国の主要繁華街・駅周辺",
            "menu": "アメリカーノ、季節ドリンク、デザート",
            "price": "比較的リーズナブル（アメリカーノ目安₩2,000台）",
            "tip": "テイクアウト中心の店舗が多いです。アプリクーポンやサイズアップもチェック。",
            "about": "コスパで人気のコーヒーチェーン。観光地でも見つけやすく、すぐにコーヒーが欲しいときに便利です。",
        },
    },
    "starbucks": {
        "ko": {
            "name": "스타벅스 (Starbucks)",
            "location": "전국 (명동·강남·공항 등 관광지 다수)",
            "menu": "시즌 음료, 리저브, 푸드·굿즈",
            "price": "브랜드 평균 이상 (음료 보통 ₩5,000대~)",
            "tip": "와이파이·콘센트가 있는 매장이 많아 잠깐 쉬기 좋습니다. 시즌 굿즈·MD는 인기 매장에서 빨리 품절될 수 있습니다.",
            "about": "한국에서 가장 흔한 글로벌 카페 브랜드 중 하나입니다. 매장 환경이 익숙하고, 외국인 카드·앱 결제도 비교적 수월합니다.",
        },
        "en": {
            "name": "Starbucks",
            "location": "Nationwide (many tourist spots: Myeongdong, Gangnam, airports)",
            "menu": "Seasonal drinks, Reserve, food & merch",
            "price": "Above average (drinks often ₩5,000+)",
            "tip": "Many stores have Wi‑Fi and outlets for a short break. Seasonal merch sells out fast at busy shops.",
            "about": "One of the most common café brands in Korea. Familiar for international travelers, with easy card/app payment.",
        },
        "ja": {
            "name": "スターバックス",
            "location": "全国（明洞・江南・空港など観光地にも多数）",
            "menu": "季節ドリンク、リザーブ、フード・グッズ",
            "price": "やや高め（ドリンク目安₩5,000台〜）",
            "tip": "Wi‑Fiやコンセントのある店が多く休憩に便利。季節グッズは人気店で早く売り切れます。",
            "about": "韓国でも最も身近なグローバルカフェの一つ。外国人にも分かりやすく、カード/アプリ決済もしやすいです。",
        },
    },
    "compose-coffee": {
        "ko": {
            "name": "컴포즈커피 (Compose Coffee)",
            "location": "전국 주요 상권·오피스·역세권",
            "menu": "아메리카노, 라떼, 시즌 음료",
            "price": "가성비형 (아메리카노 보통 ₩1,500–2,500대)",
            "tip": "테이크아웃 위주 매장이 많습니다. ‘원두 변경/샷 추가’ 옵션을 물어보면 취향에 맞출 수 있습니다.",
            "about": "저렴한 가격대 커피로 젊은층·직장인에게 인기인 브랜드입니다. 여행 중 가볍게 커피를 살 때 좋습니다.",
        },
        "en": {
            "name": "Compose Coffee",
            "location": "Major areas, offices & stations nationwide",
            "menu": "Americano, lattes, seasonal drinks",
            "price": "Value pricing (Americano often ₩1,500–2,500)",
            "tip": "Mostly takeout. Ask about bean options or extra shots to adjust the taste.",
            "about": "A budget-friendly coffee brand popular with locals. Great for a quick takeaway while sightseeing.",
        },
        "ja": {
            "name": "コンポーズコーヒー",
            "location": "全国の繁華街・オフィス・駅周辺",
            "menu": "アメリカーノ、ラテ、季節ドリンク",
            "price": "コスパ重視（アメリカーノ目安₩1,500–2,500）",
            "tip": "テイクアウト中心が多いです。豆の変更やショット追加を聞くと好みに合わせやすいです。",
            "about": "リーズナブルな価格で人気のブランド。観光中の気軽なテイクアウトに向いています。",
        },
    },
    "ediya": {
        "ko": {
            "name": "이디야 커피 (Ediya)",
            "location": "전국 (동네·대학가·상권)",
            "menu": "커피, 스무디·에이드, 베이커리",
            "price": "중간 가격대 (음료 보통 ₩3,000–5,000대)",
            "tip": "좌석이 있는 매장이 많아 잠깐 앉아서 쉬기 좋습니다. 디카페인·당도 조절을 요청해 보세요.",
            "about": "한국에서 매장 수가 많은 토종 카페 체인입니다. 커피 외 음료·간단한 빵도 함께 고르기 쉽습니다.",
        },
        "en": {
            "name": "Ediya Coffee",
            "location": "Nationwide (neighborhoods, campuses, shopping streets)",
            "menu": "Coffee, smoothies & ades, bakery items",
            "price": "Mid-range (drinks often ₩3,000–5,000)",
            "tip": "Many shops have seats for a short rest. Ask for decaf or sweetness adjustments.",
            "about": "A large Korean café chain. Easy to grab coffee plus a simple bakery item.",
        },
        "ja": {
            "name": "イーディヤコーヒー",
            "location": "全国（住宅街・大学街・繁華街）",
            "menu": "コーヒー、スムージー・エイド、ベーカリー",
            "price": "中価格帯（ドリンク目安₩3,000–5,000）",
            "tip": "座席のある店が多く小休憩に便利。デカフェや甘さ調整も頼めます。",
            "about": "店舗数が多い韓国発のカフェチェーン。コーヒー以外のドリンクや軽いパンも選びやすいです。",
        },
    },
    "twosome-place": {
        "ko": {
            "name": "투썸플레이스 (A Twosome Place)",
            "location": "전국 주요 상권·쇼핑몰",
            "menu": "케이크·디저트, 커피, 브런치 메뉴",
            "price": "디저트·세트 기준 중상 (케이크 조각 보통 ₩7,000대~)",
            "tip": "케이크와 커피를 같이 시키기 좋습니다. 홀케이크는 미리 예약이 필요할 수 있습니다.",
            "about": "케이크·디저트가 강한 카페 브랜드입니다. 기념일·선물용으로도 자주 찾고, 매장에서 여유 있게 앉기 좋습니다.",
        },
        "en": {
            "name": "A Twosome Place",
            "location": "Major shopping areas & malls nationwide",
            "menu": "Cakes & desserts, coffee, light brunch items",
            "price": "Mid–upper for desserts (cake slices often ₩7,000+)",
            "tip": "Great for cake + coffee. Whole cakes may need advance order.",
            "about": "A dessert-forward café brand. Popular for celebrations and a sit-down coffee break.",
        },
        "ja": {
            "name": "トゥサムプレイス",
            "location": "全国の主要繁華街・ショッピングモール",
            "menu": "ケーキ・デザート、コーヒー、軽食",
            "price": "デザートはやや高め（ケーキ一切れ目安₩7,000台〜）",
            "tip": "ケーキとコーヒーの組み合わせが定番。ホールケーキは予約が必要なことも。",
            "about": "ケーキ・デザートに強いカフェブランド。記念日やギフト、ゆったり休憩したいときにおすすめです。",
        },
    },
    "paiks-coffee": {
        "ko": {
            "name": "빽다방 (Paik’s Coffee)",
            "location": "전국 주요 상권·역세권",
            "menu": "원조커피, 빽스치노, 디저트 음료",
            "price": "가성비형 (기본 커피 보통 ₩2,000–3,000대)",
            "tip": "‘원조커피’는 달달한 스타일입니다. 덜 달게 마시고 싶으면 아메리카노나 당도 조절을 요청하세요.",
            "about": "백종원 이름과 연결된 커피 브랜드로, 달콤한 시그니처 음료와 합리적인 가격이 특징입니다.",
        },
        "en": {
            "name": "Paik’s Coffee",
            "location": "Major areas & stations nationwide",
            "menu": "Original coffee, Paiksccino, dessert drinks",
            "price": "Value pricing (basic coffee often ₩2,000–3,000)",
            "tip": "“Original coffee” is on the sweet side. Choose Americano or ask to reduce sweetness if you prefer less sugar.",
            "about": "A budget coffee brand linked to chef Baek Jong-won, known for sweet signature drinks and affordable prices.",
        },
        "ja": {
            "name": "ペクダバン（Paik’s Coffee）",
            "location": "全国の主要繁華街・駅周辺",
            "menu": "元祖コーヒー、ペクスチノ、デザートドリンク",
            "price": "コスパ重視（基本コーヒー目安₩2,000–3,000）",
            "tip": "「元祖コーヒー」は甘めです。甘さ控えならアメリカーノや甘さ調整を。",
            "about": "ペク・ジョンウォン関連のコーヒーブランド。甘いシグネチャーと手頃な価格が特徴です。",
        },
    },
}

COMBOS = {
    "blue-lemonade-milkis": {
        "ko": {
            "Title": "블루레몬에이드 + 밀키스",
            "Desc": "상큼한 블루레몬에이드에 밀키스를 섞는 청량 조합",
            "pageTitle": "블루레몬에이드 + 밀키스 만드는 법",
            "lead": "편의점 음료끼리 섞어 만드는 SNS 인기 조합입니다. 상큼한 블루레몬에이드에 밀키스의 부드러운 탄산을 더하면 카페 에이드처럼 달콤상큼해집니다.",
            "productsTitle": "살 것",
            "products": "블루레몬에이드(페트·캔) 1개, 밀키스 1캔. (선택) 얼음컵·빨대.",
            "stepsTitle": "만드는 법",
            "s1": "블루레몬에이드와 밀키스를 차갑게 준비합니다. 얼음컵이 있으면 미리 받아 두세요.",
            "s2": "얼음컵(또는 큰 컵)에 블루레몬에이드를 먼저 반쯤 붓고, 밀키스를 천천히 채워 섞습니다. 비율은 1:1이 무난합니다.",
            "s3": "빨대로 가볍게 저어 바로 마십니다. 너무 달면 에이드 비율을, 더 부드럽게 하려면 밀키스 비율을 높이세요.",
            "tipTitle": "팁",
            "tip": "탄산이 세면 컵이 넘칠 수 있으니 천천히 따르세요. 제품명은 편의점마다 ‘블루 레몬’·‘레몬에이드’류로 다를 수 있습니다.",
        },
        "en": {
            "Title": "Blue lemonade + Milkis",
            "Desc": "Mix blue lemonade with creamy Milkis soda",
            "pageTitle": "How to make Blue lemonade + Milkis",
            "lead": "A viral convenience-store drink mix: tangy blue lemonade plus creamy Milkis soda tastes like a café-style ade.",
            "productsTitle": "What to buy",
            "products": "1 blue lemonade (PET/can), 1 Milkis. Optional: ice cup & straw.",
            "stepsTitle": "How to make",
            "s1": "Chill both drinks. Grab an ice cup if available.",
            "s2": "Pour blue lemonade about halfway into a cup, then slowly add Milkis (about 1:1).",
            "s3": "Stir lightly and drink. More lemonade = sharper; more Milkis = creamier.",
            "tipTitle": "Tip",
            "tip": "Pour slowly so the soda doesn’t overflow. Exact product names vary by store.",
        },
        "ja": {
            "Title": "ブルーレモネード＋ミルキス",
            "Desc": "爽やかなブルーレモネードにミルキスを混ぜる清涼コンビ",
            "pageTitle": "ブルーレモネード＋ミルキスの作り方",
            "lead": "コンビニ飲料を混ぜるSNS人気レシピ。酸っぱ甘いブルーレモネードにミルキスのまろやかな炭酸を足すと、カフェのエイド風になります。",
            "productsTitle": "買うもの",
            "products": "ブルーレモネード（ペット/缶）1本、ミルキス1缶。（任意）氷カップ・ストロー。",
            "stepsTitle": "作り方",
            "s1": "両方を冷やします。氷カップがあれば先に用意。",
            "s2": "カップにブルーレモネードを半分ほど入れ、ミルキスをゆっくり注ぎます（目安1:1）。",
            "s3": "軽く混ぜてすぐ飲みます。さっぱりめならレモネード多め、まろやかめならミルキス多め。",
            "tipTitle": "ヒント",
            "tip": "炭酸で溢れやすいのでゆっくり注いでください。商品名は店ごとに違うことがあります。",
        },
    },
    "choco-banana-latte": {
        "ko": {
            "Title": "초코바나나라떼",
            "Desc": "바나나우유에 초코우유를 섞어 만드는 달콤 라떼",
            "pageTitle": "초코바나나라떼 만드는 법",
            "lead": "바나나우유를 먼저 넣고 초코우유를 더해 섞으면, 카페의 초코바나나 음료처럼 달콤해집니다. 별도의 커피 없이도 만들기 쉬운 조합입니다.",
            "productsTitle": "살 것",
            "products": "바나나맛 우유 1개, 초코우유(또는 초코음료) 1개. (선택) 얼음·빨대.",
            "stepsTitle": "만드는 법",
            "s1": "바나나우유를 먼저 컵(또는 병)에 준비합니다. 차갑게 마실수록 맛있습니다.",
            "s2": "초코우유를 조금씩 부어 섞습니다. 처음엔 바나나:초코 = 2:1 정도로 시작해 맛을 보세요.",
            "s3": "잘 흔들거나 저어 색이 고르게 되면 완성입니다. 더 진한 초코 맛을 원하면 초코우유를 추가하세요.",
            "tipTitle": "팁",
            "tip": "당이 꽤 있으니 한 번에 다 섞기보다 조금씩 조절하세요. 더 시원하게 마시려면 얼음컵에 부어 드세요.",
        },
        "en": {
            "Title": "Choco banana latte",
            "Desc": "Mix banana milk first, then chocolate milk",
            "pageTitle": "How to make Choco banana latte",
            "lead": "Start with banana milk, then add chocolate milk for a café-style choco-banana drink — no coffee required.",
            "productsTitle": "What to buy",
            "products": "1 banana milk, 1 chocolate milk. Optional: ice & straw.",
            "stepsTitle": "How to make",
            "s1": "Pour banana milk first into a cup/bottle. Cold tastes best.",
            "s2": "Add chocolate milk little by little. Start around banana:choco = 2:1, then adjust.",
            "s3": "Shake or stir until even. Add more chocolate milk for a richer cocoa taste.",
            "tipTitle": "Tip",
            "tip": "It’s quite sweet — adjust gradually. Use an ice cup for a colder drink.",
        },
        "ja": {
            "Title": "チョコバナナラテ",
            "Desc": "バナナ牛乳にチョコ牛乳を混ぜる甘いラテ風",
            "pageTitle": "チョコバナナラテの作り方",
            "lead": "バナナ牛乳を先に入れ、チョコ牛乳を足して混ぜるとカフェ風のチョコバナナ飲料になります。コーヒーなしでも簡単です。",
            "productsTitle": "買うもの",
            "products": "バナナミルク1本、チョコミルク1本。（任意）氷・ストロー。",
            "stepsTitle": "作り方",
            "s1": "まずバナナミルクを用意します。冷たいほどおいしいです。",
            "s2": "チョコミルクを少しずつ加えて混ぜます。最初はバナナ:チョコ＝2:1くらいで味見。",
            "s3": "よく振って均一にしたら完成。チョコ感を強くしたければチョコを追加。",
            "tipTitle": "ヒント",
            "tip": "かなり甘いので一気に混ぜず調整を。氷カップに注ぐとより冷え冷えです。",
        },
    },
    "banana-americano": {
        "ko": {
            "Title": "바나나우유 아메리카노",
            "Desc": "바나나우유와 아이스 아메리카노를 섞는 정석 조합",
            "pageTitle": "바나나우유 + 아이스 아메리카노 만드는 법",
            "lead": "편의점 음료 꿀조합의 정석입니다. 달콤한 바나나우유와 쓴 커피를 섞으면 디저트 음료처럼 변합니다.",
            "productsTitle": "살 것",
            "products": "빙그레 바나나맛 우유(또는 저지방/고칼슘 바나나우유) · 아이스 아메리카노(컵/캔) · 선택: 빨대",
            "stepsTitle": "만드는 법",
            "s1": "바나나우유와 아이스 아메리카노를 고릅니다. 둘 다 차가운 제품이 더 맛있습니다.",
            "s2": "바나나우유에 커피를 조금씩 부어 섞습니다. 처음엔 커피를 1/3~1/2만 넣고 맛을 본 뒤 조절하세요.",
            "s3": "잘 흔들거나 빨대로 저어 줍니다. 너무 달면 커피를, 쓰다면 우유 비율을 높이세요.",
            "tipTitle": "팁",
            "tip": "커피잔에 바나나우유를 부어도 됩니다. 칼로리가 걱정되면 저지방 바나나우유를 고르세요.",
        },
        "en": {
            "Title": "Banana milk Americano",
            "Desc": "Classic mix of banana milk and iced Americano",
            "pageTitle": "How to make Banana milk + iced Americano",
            "lead": "A classic convenience-store drink hack: sweet banana milk plus bitter coffee becomes a dessert-like latte.",
            "productsTitle": "What to buy",
            "products": "Banana milk · iced Americano (cup/can) · optional straw",
            "stepsTitle": "How to make",
            "s1": "Pick cold banana milk and iced Americano.",
            "s2": "Pour coffee into the banana milk little by little. Start with 1/3–1/2 of the coffee, then taste.",
            "s3": "Shake or stir. Add more coffee if too sweet, or keep more milk if too bitter.",
            "tipTitle": "Tip",
            "tip": "You can also pour banana milk into the coffee cup. Choose low-fat banana milk if you want lighter calories.",
        },
        "ja": {
            "Title": "バナナミルクアメリカーノ",
            "Desc": "バナナミルクとアイスアメリカーノの定番ミックス",
            "pageTitle": "バナナミルク＋アイスアメリカーノの作り方",
            "lead": "コンビニ飲料の定番アレンジ。甘いバナナミルクと苦いコーヒーを混ぜるとデザートドリンク風になります。",
            "productsTitle": "買うもの",
            "products": "バナナミルク · アイスアメリカーノ（カップ/缶） · 任意でストロー",
            "stepsTitle": "作り方",
            "s1": "冷たいバナナミルクとアイスアメリカーノを用意します。",
            "s2": "バナナミルクにコーヒーを少しずつ入れます。最初は1/3〜1/2だけ入れて味見。",
            "s3": "振るか混ぜます。甘すぎればコーヒーを、苦すぎればミルク比率を上げてください。",
            "tipTitle": "ヒント",
            "tip": "コーヒーカップにバナナミルクを注いでもOK。カロリーが気になるなら低脂肪バナナミルクを。",
        },
    },
}

COMBO_IMAGES = {
    "blue-lemonade-milkis": "combo-blue-lemonade-milkis.jpg",
    "choco-banana-latte": "combo-choco-banana-latte.jpg",
    "banana-americano": "combo-banana-coffee.jpg",  # reuse existing
}

CAFE_BRANDS = [
    ("mega-coffee", "mega-coffee-menu.jpg"),
    ("starbucks", "starbucks-menu.jpg"),
    ("compose-coffee", "compose-coffee-menu.jpg"),
    ("ediya", "ediya-menu.jpg"),
    ("twosome-place", "twosome-place-menu.jpg"),
    ("paiks-coffee", "paiks-coffee-menu.jpg"),
]


def combo_page(slug: str) -> str:
    img = COMBO_IMAGES[slug]
    return f"""<!DOCTYPE html>
<html lang="ko" data-i18n-title="convenience.{slug}_pageTitle">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{slug}</title>
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
      <img class="combo-article-hero" src="../../../Images/convenience/{img}" alt="" data-i18n-attr="alt:convenience.{slug}_pageTitle">
      <h1 data-i18n="convenience.{slug}_pageTitle"></h1>
      <p class="article-lead" data-i18n="convenience.{slug}_lead"></p>
      <h2 data-i18n="convenience.{slug}_productsTitle"></h2>
      <p data-i18n="convenience.{slug}_products"></p>
      <h2 data-i18n="convenience.{slug}_stepsTitle"></h2>
      <ol class="route-steps">
        <li data-i18n="convenience.{slug}_s1"></li>
        <li data-i18n="convenience.{slug}_s2"></li>
        <li data-i18n="convenience.{slug}_s3"></li>
      </ol>
      <div class="tip">
        <h3 data-i18n="convenience.{slug}_tipTitle"></h3>
        <p data-i18n="convenience.{slug}_tip"></p>
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


def cafe_index() -> str:
    cards = []
    for slug, img in CAFE_BRANDS:
        cards.append(
            f"""      <article class="card">
        <a href="./{slug}.html">
          <img src="../../../../Images/foods/restaurants/desserts/{img}" width="100%" alt="" data-i18n-attr="alt:restaurants.{slug}.name">
        </a>
        <h2><span data-i18n="restaurants.{slug}.name"></span></h2>
        <p data-i18n="restaurants.{slug}.menu"></p>
        <p><a href="./{slug}.html" data-i18n="common.viewMore">View more →</a></p>
      </article>"""
        )
    return f"""<!DOCTYPE html>
<html lang="ko" data-i18n-title="dishes.cafe.title">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>cafe | Korea Travel Guide</title>
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

    <h1>☕ <span data-i18n="dishes.cafe.title">cafe</span></h1>

    <img src="../../../../Images/foods/dishes/cafe.jpg" width="100%" alt="cafe" data-i18n-attr="alt:dishes.cafe.title">

    <section class="intro">
      <h2 data-i18n="common.about">About</h2>
      <p data-i18n="dishes.cafe.about"></p>
    </section>

    <h2 data-i18n="common.places">Places</h2>
    <div class="card-grid">
{chr(10).join(cards)}
    </div>
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


def cafe_brand_page(slug: str, img: str) -> str:
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
      <a href="./index.html">← <span data-i18n="dishes.cafe.title"></span></a>
    </p>
    <h1 data-i18n="restaurants.{slug}.name"></h1>
    <img src="../../../../Images/foods/restaurants/desserts/{img}" width="100%" alt="" data-i18n-attr="alt:restaurants.{slug}.name">
    <p data-i18n="restaurants.{slug}.about"></p>
    <table class="content-table">
      <tr><th data-i18n="restaurantFields.name"></th><td data-i18n="restaurants.{slug}.name"></td></tr>
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


def patch_desserts_index(html: str) -> str:
    card = """      <article class="card">
        <a href="./cafe/index.html">
          <img src="../../../Images/foods/dishes/cafe.jpg" width="100%" alt="" data-i18n-attr="alt:dishes.cafe.title">
        </a>
        <h2>☕ <span data-i18n="dishes.cafe.title"></span></h2>
        <p data-i18n="dishes.cafe.desc"></p>
        <p><a href="./cafe/index.html" data-i18n="common.viewMore">View more →</a></p>
      </article>
"""
    if "./cafe/index.html" in html:
        return html
    return html.replace(
        """      <article class="card">
        <a href="./bread/index.html">""",
        card
        + """      <article class="card">
        <a href="./bread/index.html">""",
    )


def patch_convenience_index(html: str) -> str:
    extra = """      <a class="combo-card" href="./blue-lemonade-milkis/index.html">
        <img src="../../Images/convenience/combo-blue-lemonade-milkis.jpg" alt="" data-i18n-attr="alt:convenience.blue-lemonade-milkisTitle">
        <div class="combo-body">
          <h3 data-i18n="convenience.blue-lemonade-milkisTitle"></h3>
          <p data-i18n="convenience.blue-lemonade-milkisDesc"></p>
          <span class="combo-more" data-i18n="convenience.readMore"></span>
        </div>
      </a>
      <a class="combo-card" href="./choco-banana-latte/index.html">
        <img src="../../Images/convenience/combo-choco-banana-latte.jpg" alt="" data-i18n-attr="alt:convenience.choco-banana-latteTitle">
        <div class="combo-body">
          <h3 data-i18n="convenience.choco-banana-latteTitle"></h3>
          <p data-i18n="convenience.choco-banana-latteDesc"></p>
          <span class="combo-more" data-i18n="convenience.readMore"></span>
        </div>
      </a>
      <a class="combo-card" href="./banana-americano/index.html">
        <img src="../../Images/convenience/combo-banana-coffee.jpg" alt="" data-i18n-attr="alt:convenience.banana-americanoTitle">
        <div class="combo-body">
          <h3 data-i18n="convenience.banana-americanoTitle"></h3>
          <p data-i18n="convenience.banana-americanoDesc"></p>
          <span class="combo-more" data-i18n="convenience.readMore"></span>
        </div>
      </a>
"""
    if "blue-lemonade-milkis" in html:
        return html
    return html.replace("</div>\n  </main>", extra + "    </div>\n  </main>")


def update_i18n():
    for lang in ("ko", "en", "ja"):
        path = I18N / f"{lang}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["common"].update(COMMON_PATCH[lang])
        data["dishes"]["cafe"] = DISHES_CAFE[lang]
        if "dessertsIndex" in data:
            data["dessertsIndex"]["intro"] = DESSERTS_INTRO[lang]
        for slug, langs in RESTAURANTS.items():
            data.setdefault("restaurants", {})[slug] = langs[lang]
        for slug, langs in COMBOS.items():
            c = langs[lang]
            data["convenience"][f"{slug}Title"] = c["Title"]
            data["convenience"][f"{slug}Desc"] = c["Desc"]
            for key in (
                "pageTitle",
                "lead",
                "productsTitle",
                "products",
                "stepsTitle",
                "s1",
                "s2",
                "s3",
                "tipTitle",
                "tip",
            ):
                data["convenience"][f"{slug}_{key}"] = c[key]
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("updated", path)


def main():
    update_i18n()

    # Convenience pages
    for slug in COMBOS:
        out = ROOT / "pages" / "convenience-store" / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(combo_page(slug), encoding="utf-8")
        print("wrote", out)

    conv_index = ROOT / "pages" / "convenience-store" / "index.html"
    conv_index.write_text(patch_convenience_index(conv_index.read_text(encoding="utf-8")), encoding="utf-8")
    print("updated", conv_index)

    # Cafe pages
    cafe_dir = ROOT / "pages" / "foods" / "desserts" / "cafe"
    cafe_dir.mkdir(parents=True, exist_ok=True)
    (cafe_dir / "index.html").write_text(cafe_index(), encoding="utf-8")
    print("wrote", cafe_dir / "index.html")
    for slug, img in CAFE_BRANDS:
        out = cafe_dir / f"{slug}.html"
        out.write_text(cafe_brand_page(slug, img), encoding="utf-8")
        print("wrote", out)

    desserts_index = ROOT / "pages" / "foods" / "desserts" / "index.html"
    desserts_index.write_text(patch_desserts_index(desserts_index.read_text(encoding="utf-8")), encoding="utf-8")
    print("updated", desserts_index)


if __name__ == "__main__":
    main()
