# -*- coding: utf-8 -*-
"""Rewrite convenience combos + shopping + places i18n; build bundle."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
I18N = ROOT / "i18n"


def load(lang):
    return json.loads((I18N / f"{lang}.json").read_text(encoding="utf-8"))


def save(lang, data):
    (I18N / f"{lang}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


COMBOS = [
    ("gongganchun", "combo-gongganchun.jpg"),
    ("markjeongsik", "combo-markjeongsik.jpg"),
    ("carbonara", "combo-carbonara-risotto.jpg"),
    ("eolbaksa", "combo-eolbaksa.jpg"),
    ("jikgguri", "combo-jikgguri.jpg"),
    ("melona", "combo-melona-coffee.jpg"),
]

KO_C = {
    "intro": "한국 편의점 꿀조합은 SNS·방송에서 유행한 레시피가 많습니다. 전자레인지만으로도 만들 수 있는 대표 조합을 모았습니다.",
    "comboTitle": "유행 꿀조합",
    "tapHint": "카드를 누르면 재료·만드는 법을 볼 수 있습니다.",
    "readMore": "자세히 보기 →",
    "backCombos": "← 꿀조합 목록",
    "gongganchunTitle": "공간춘",
    "gongganchunDesc": "공화춘 짜장 + 간짬뽕을 섞어 먹는 매운 짜장 라면",
    "markjeongsikTitle": "마크정식",
    "markjeongsikDesc": "컵떡볶이 + 스파게티 라면 + 소시지 + 치즈",
    "carbonaraTitle": "까르보불닭리조또",
    "carbonaraDesc": "까르보불닭볶음면 + 참치마요 삼각김밥",
    "eolbaksaTitle": "얼박사",
    "eolbaksaDesc": "얼음컵 + 박카스 + 사이다",
    "jikgguriTitle": "직꾸리",
    "jikgguriDesc": "카구리 + 직화구이 닭 + 치즈",
    "melonaTitle": "메로나 + 아이스커피",
    "melonaDesc": "메로나를 커피에 찍어 먹는 디저트 조합",
}

EN_C = {
    "intro": "Korean convenience-store ‘honey combos’ went viral on SNS and TV. Most need only a microwave.",
    "comboTitle": "Viral combos",
    "tapHint": "Tap a card for ingredients and steps.",
    "readMore": "Read more →",
    "backCombos": "← Combo list",
    "gongganchunTitle": "Gongganchun",
    "gongganchunDesc": "Mix Chapagetti jjajang cup + spicy jjamppong cup",
    "markjeongsikTitle": "Mark’s set",
    "markjeongsikDesc": "Cup tteokbokki + spaghetti ramyeon + sausage + cheese",
    "carbonaraTitle": "Carbonara Buldak risotto",
    "carbonaraDesc": "Carbonara Buldak noodles + tuna-mayo triangle kimbap",
    "eolbaksaTitle": "Eolbaksa",
    "eolbaksaDesc": "Ice cup + Bacchus + cider soda",
    "jikgguriTitle": "Jikgguri",
    "jikgguriDesc": "Kaguri curry udon + grilled chicken + cheese",
    "melonaTitle": "Melona + iced coffee",
    "melonaDesc": "Dip Melona ice cream in iced coffee",
}

JA_C = {
    "intro": "韓国コンビニの神組み合わせはSNSや放送で話題です。電子レンジだけで作れる定番を集めました。",
    "comboTitle": "話題の組み合わせ",
    "tapHint": "カードを押すと材料と作り方が見られます。",
    "readMore": "詳しく見る →",
    "backCombos": "← 組み合わせ一覧",
    "gongganchunTitle": "ゴンガンチュン",
    "gongganchunDesc": "チャパゲティ＋海鮮チャンポン杯を混ぜる辛いジャージャー麺",
    "markjeongsikTitle": "マーク定食",
    "markjeongsikDesc": "カップトッポギ＋スパゲティ麺＋ソーセージ＋チーズ",
    "carbonaraTitle": "カルボブルダックリゾット",
    "carbonaraDesc": "カルボブルダック＋ツナマヨ三角キンパ",
    "eolbaksaTitle": "オルバクサ",
    "eolbaksaDesc": "氷カップ＋バッカス＋サイダー",
    "jikgguriTitle": "ジッククリ",
    "jikgguriDesc": "カグリ＋直火チキン＋チーズ",
    "melonaTitle": "メ로나＋アイスコーヒー",
    "melonaDesc": "メ로나をコーヒーに浸けて食べるデザート",
}

DETAIL_KO = {
    "gongganchun": {
        "pageTitle": "공간춘 만드는 법",
        "lead": "공화춘(짜장)과 간짬뽕을 한 그릇에 섞어, 짜장 고소함과 짬뽕 매콤함을 동시에 즐기는 조합입니다.",
        "productsTitle": "살 것",
        "products": "공화춘 컵라면(또는 짜장 컵) 1개, 간짬뽕(또는 해물짬뽕) 컵라면 1개. 취향에 따라 슬라이스 치즈·계란 추가.",
        "stepsTitle": "만드는 법",
        "s1": "두 컵라면의 면과 스프를 준비합니다. 물은 한 컵 분량만 끓이거나, 전자레인지용 큰 용기에 모읍니다.",
        "s2": "면을 익힌 뒤 짜장 스프와 짬뽕 스프를 원하는 비율(보통 1:1)로 넣고 비빕니다.",
        "s3": "너무 짜면 물을 조금 더하고, 더 맵게 하려면 짬뽕 스프를 늘리세요. 치즈를 올리면 부드러워집니다.",
        "tipTitle": "팁",
        "tip": "브랜드명은 편의점마다 다를 수 있어요. ‘짜장 컵 + 짬뽕 컵’이면 같은 컨셉입니다.",
    },
    "markjeongsik": {
        "pageTitle": "마크정식 만드는 법",
        "lead": "GOT7 마크 팬덤에서 유명해진 레시피. 컵떡볶이에 스파게티 라면·소시지·치즈를 올려 전자레인지로 완성합니다.",
        "productsTitle": "살 것",
        "products": "컵떡볶이 1개, 스파게티 컵라면(또는 스파게티맛 라면) 1개, 소시지(프랑크·핫바) , 슬라이스 치즈 1–2장.",
        "stepsTitle": "만드는 법",
        "s1": "컵떡볶이를 설명대로 데웁니다. 스파게티 라면도 익혀 물기를 적당히 남깁니다.",
        "s2": "떡볶이 용기에 스파게티 면을 넣고, 데운 소시지를 올리고 치즈를 얹습니다.",
        "s3": "전자레인지에 20–40초 더 돌려 치즈를 녹인 뒤 비벼 먹습니다.",
        "tipTitle": "팁",
        "tip": "체다 치즈를 한 장 더 올리면 풍미가 좋아집니다. 매운맛은 떡볶이 소스 양으로 조절하세요.",
    },
    "carbonara": {
        "pageTitle": "까르보불닭리조또 만드는 법",
        "lead": "까르보불닭의 크림 소스에 참치마요 삼각김밥 밥을 섞어 리조또처럼 먹는 조합입니다.",
        "productsTitle": "살 것",
        "products": "까르보불닭볶음면 1개, 참치마요 삼각김밥 1개. (선택) 슬라이스 치즈, 우유 조금.",
        "stepsTitle": "만드는 법",
        "s1": "까르보불닭을 패키지 설명대로 조리해 크림 소스를 만듭니다.",
        "s2": "삼각김밥 포장을 벗겨 밥을 면 그릇에 풀어 넣습니다.",
        "s3": "면·소스·밥을 잘 섞어 리조또처럼 먹습니다. 질면 치즈나 우유를 조금 더하세요.",
        "tipTitle": "팁",
        "tip": "매운맛이 강하면 밥을 더 넣거나 까르보 스프만 먼저 덜어 조절하세요.",
    },
    "eolbaksa": {
        "pageTitle": "얼박사 만드는 법",
        "lead": "얼음컵에 박카스와 사이다를 섞어 마시는 상쾌한 피로회복 음료 조합입니다.",
        "productsTitle": "살 것",
        "products": "얼음컵(빙수·아이스커피용) 1개, 박카스(또는 유사 드링크) 1병, 사이다(또는 스프라이트류) 1캔.",
        "stepsTitle": "만드는 법",
        "s1": "얼음컵에 얼음이 충분한지 확인합니다.",
        "s2": "박카스를 먼저 붓고, 사이다를 천천히 채워 섞습니다.",
        "s3": "빨대로 저어 바로 마십니다. 너무 달면 탄산수 비율을 높이세요.",
        "tipTitle": "팁",
        "tip": "카페인·당이 있으니 저녁 늦게는 양을 줄이세요. 편의점에 따라 얼음컵 종류가 다릅니다.",
    },
    "jikgguri": {
        "pageTitle": "직꾸리 만드는 법",
        "lead": "카레 우동 라면(카구리) 위에 직화 닭구이를 올리고 치즈를 녹인 조합입니다.",
        "productsTitle": "살 것",
        "products": "카구리(카레우동) 1개, 직화구이 닭(또는 유사 닭구이 간편식) 1팩, 슬라이스 치즈 1장.",
        "stepsTitle": "만드는 법",
        "s1": "카구리를 설명대로 조리합니다.",
        "s2": "직화 닭을 데워 면 위에 올립니다.",
        "s3": "치즈를 올리고 전자레인지에 약 30초 더 돌려 녹인 뒤 먹습니다.",
        "tipTitle": "팁",
        "tip": "삼각김밥을 곁들이면 더 든든합니다. 닭 제품명은 편의점 PB마다 다를 수 있습니다.",
    },
    "melona": {
        "pageTitle": "메로나 + 커피",
        "lead": "메로나를 아이스커피에 찍어 먹거나 함께 즐기는 간단한 디저트 조합입니다.",
        "productsTitle": "살 것",
        "products": "메로나(또는 유사 아이스바) 1개, 아이스 아메리카노 1잔.",
        "stepsTitle": "만드는 법",
        "s1": "아이스커피를 준비합니다.",
        "s2": "메로나를 커피에 살짝 찍어 먹거나, 컵에 조각을 넣어 녹여 마십니다.",
        "s3": "너무 달면 아메리카노 비율을 높이세요.",
        "tipTitle": "팁",
        "tip": "여름 산책·사진용으로 인기 있는 가벼운 조합입니다.",
    },
}

# EN/JA shortened details for bundle size - mirror KO structure
def translate_detail(slug, lang):
    ko = DETAIL_KO[slug]
    if lang == "ko":
        return ko
    # Use English/Japanese parallel short versions
    table = {
        "gongganchun": {
            "en": {
                "pageTitle": "How to make Gongganchun",
                "lead": "Mix jjajang cup noodles with spicy jjamppong cup noodles for savory-spicy flavor.",
                "productsTitle": "Buy",
                "products": "1 Chapagetti/jjajang cup, 1 spicy seafood jjamppong cup. Optional cheese/egg.",
                "stepsTitle": "Steps",
                "s1": "Cook both noodles (use about one cup of water total in a larger bowl if needed).",
                "s2": "Mix sauces about 1:1 and toss.",
                "s3": "Add water if too salty; more jjamppong powder if you want more heat.",
                "tipTitle": "Tip",
                "tip": "Brand names vary — any jjajang cup + jjamppong cup works.",
            },
            "ja": {
                "pageTitle": "ゴンガンチュンの作り方",
                "lead": "ジャージャー麺カップと辛いチャンポンカップを混ぜる定番アレンジです。",
                "productsTitle": "買うもの",
                "products": "チャパゲティ等ジャージャー1、海鮮チャンポン1。任意でチーズ・卵。",
                "stepsTitle": "作り方",
                "s1": "両方の麺を茹でます（大きめ容器にまとめてもOK）。",
                "s2": "スープをだいたい1:1で入れて混ぜます。",
                "s3": "塩辛ければ水を足し、辛さはチャンポン側で調節。",
                "tipTitle": "ヒント",
                "tip": "ブランド名は店により違います。ジャージャー＋チャンポンならOK。",
            },
        },
        "markjeongsik": {
            "en": {
                "pageTitle": "How to make Mark’s set",
                "lead": "Viral fan recipe: cup tteokbokki with spaghetti ramyeon, sausage, and cheese.",
                "productsTitle": "Buy",
                "products": "Cup tteokbokki, spaghetti-style cup noodles, sausage, 1–2 cheese slices.",
                "stepsTitle": "Steps",
                "s1": "Heat tteokbokki and cook spaghetti noodles.",
                "s2": "Combine noodles in the tteokbokki cup; add sausage and cheese.",
                "s3": "Microwave 20–40s to melt cheese, then mix.",
                "tipTitle": "Tip",
                "tip": "Extra cheddar boosts flavor. Control spice with tteokbokki sauce.",
            },
            "ja": {
                "pageTitle": "マーク定食の作り方",
                "lead": "カップトッポギにスパゲティ麺・ソーセージ・チーズを合わせる人気レシピです。",
                "productsTitle": "買うもの",
                "products": "カップトッポギ、スパゲティ風カップ麺、ソーセージ、チーズ1–2枚。",
                "stepsTitle": "作り方",
                "s1": "トッポギと麺をそれぞれ加熱します。",
                "s2": "トッポギ容器に麺・ソーセージ・チーズを入れます。",
                "s3": "20–40秒追加加熱してチーズを溶かし混ぜます。",
                "tipTitle": "ヒント",
                "tip": "チェダーを足すと風味アップ。辛さはトッポギソースで調節。",
            },
        },
        "carbonara": {
            "en": {
                "pageTitle": "Carbonara Buldak risotto",
                "lead": "Mix Carbonara Buldak with tuna-mayo kimbap rice for a creamy ‘risotto’.",
                "productsTitle": "Buy",
                "products": "Carbonara Buldak noodles, tuna-mayo triangle kimbap. Optional cheese/milk.",
                "stepsTitle": "Steps",
                "s1": "Cook Carbonara Buldak as directed.",
                "s2": "Unwrap kimbap and add the rice to the noodles.",
                "s3": "Mix into a risotto texture; add cheese/milk if dry.",
                "tipTitle": "Tip",
                "tip": "Too spicy? Add more rice or use less chili powder.",
            },
            "ja": {
                "pageTitle": "カルボブルダックリゾット",
                "lead": "カルボブルダックにツナマヨキンパのご飯を混ぜてリゾット風に。",
                "productsTitle": "買うもの",
                "products": "カルボブルダック、ツナマヨ三角キンパ。任意でチーズ・牛乳。",
                "stepsTitle": "作り方",
                "s1": "カルボブルダックを表示通り調理。",
                "s2": "キンパのご飯をほぐして入れます。",
                "s3": "よく混ぜてリゾット状に。固ければチーズや牛乳を。",
                "tipTitle": "ヒント",
                "tip": "辛ければご飯を増やすか粉を控えめに。",
            },
        },
        "eolbaksa": {
            "en": {
                "pageTitle": "How to make Eolbaksa",
                "lead": "Ice cup + Bacchus energy drink + lemon-lime soda — a refreshing pick-me-up.",
                "productsTitle": "Buy",
                "products": "Ice cup, Bacchus (or similar), cider/Sprite-style soda.",
                "stepsTitle": "Steps",
                "s1": "Start with a cup of ice.",
                "s2": "Pour Bacchus, then top with soda.",
                "s3": "Stir and drink. Use more soda if too sweet.",
                "tipTitle": "Tip",
                "tip": "Has caffeine and sugar — go easy at night.",
            },
            "ja": {
                "pageTitle": "オルバクサの作り方",
                "lead": "氷カップにバッカスとサイダーを混ぜる爽快ドリンクです。",
                "productsTitle": "買うもの",
                "products": "氷カップ、バッカス、サイダー類。",
                "stepsTitle": "作り方",
                "s1": "氷を用意します。",
                "s2": "バッカスを入れ、サイダーを注ぎます。",
                "s3": "混ぜてすぐ飲みます。甘ければ炭酸を多めに。",
                "tipTitle": "ヒント",
                "tip": "カフェイン・糖分があるので夜は控えめに。",
            },
        },
        "jikgguri": {
            "en": {
                "pageTitle": "How to make Jikgguri",
                "lead": "Kaguri curry-udon topped with grilled chicken and melted cheese.",
                "productsTitle": "Buy",
                "products": "Kaguri (curry udon), grilled chicken pack, cheese slice.",
                "stepsTitle": "Steps",
                "s1": "Cook Kaguri.",
                "s2": "Heat chicken and place on noodles.",
                "s3": "Add cheese; microwave ~30s to melt.",
                "tipTitle": "Tip",
                "tip": "Pair with triangle kimbap. Chicken brand names vary by store.",
            },
            "ja": {
                "pageTitle": "ジッククリの作り方",
                "lead": "カグリ（カレーうどん）に直火チキンとチーズを乗せます。",
                "productsTitle": "買うもの",
                "products": "カグリ、直火チキン、チーズ1枚。",
                "stepsTitle": "作り方",
                "s1": "カグリを調理。",
                "s2": "チキンを温めてのせます。",
                "s3": "チーズを乗せ約30秒加熱して溶かす。",
                "tipTitle": "ヒント",
                "tip": "三角キンパを添えると満腹感アップ。",
            },
        },
        "melona": {
            "en": {
                "pageTitle": "Melona + coffee",
                "lead": "Dip Melona in iced coffee or melt pieces into the cup.",
                "productsTitle": "Buy",
                "products": "Melona ice bar, iced Americano.",
                "stepsTitle": "Steps",
                "s1": "Get iced coffee.",
                "s2": "Dip Melona or drop pieces into the cup.",
                "s3": "Adjust sweetness with more Americano.",
                "tipTitle": "Tip",
                "tip": "A light summer dessert combo.",
            },
            "ja": {
                "pageTitle": "メ로나＋コーヒー",
                "lead": "メ로나をアイスコーヒーに浸けて食べる簡単デザート。",
                "productsTitle": "買うもの",
                "products": "メ로나、アイスアメリカーノ。",
                "stepsTitle": "作り方",
                "s1": "コーヒーを用意。",
                "s2": "メロナを浸けるか、欠片を入れて溶かす。",
                "s3": "甘ければアメリカーノを多めに。",
                "tipTitle": "ヒント",
                "tip": "夏の軽いデザート組み合わせです。",
            },
        },
    }
    return table[slug][lang]


def write_combo_pages():
    for slug, img in COMBOS:
        folder = ROOT / "pages/convenience-store" / slug
        folder.mkdir(parents=True, exist_ok=True)
        html = f"""<!DOCTYPE html>
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
        (folder / "index.html").write_text(html, encoding="utf-8")
        print("combo page", slug)


def patch_convenience_i18n():
    for lang, meta in (("ko", KO_C), ("en", EN_C), ("ja", JA_C)):
        data = load(lang)
        c = data.setdefault("convenience", {})
        c.update(meta)
        # map short titles used on cards
        mapping = {
            "gongganchun": ("gongganchunTitle", "gongganchunDesc"),
            "markjeongsik": ("markjeongsikTitle", "markjeongsikDesc"),
            "carbonara": ("carbonaraTitle", "carbonaraDesc"),
            "eolbaksa": ("eolbaksaTitle", "eolbaksaDesc"),
            "jikgguri": ("jikgguriTitle", "jikgguriDesc"),
            "melona": ("melonaTitle", "melonaDesc"),
        }
        for i, (slug, _) in enumerate(COMBOS, start=1):
            tkey, dkey = mapping[slug]
            c[f"c{i}Title"] = meta[tkey]
            c[f"c{i}Desc"] = meta[dkey]
        for slug, _ in COMBOS:
            detail = translate_detail(slug, lang)
            for k, v in detail.items():
                c[f"{slug}_{k}"] = v
        save(lang, data)
        print("convenience i18n", lang)


PLACES_KO = {
    "tabPlaces": "대표 명소 소개",
    "placesIntro": "지역을 고른 뒤, 여행객이 많이 찾는 명소를 확인하세요. 가는 방법 힌트도 함께 적었습니다.",
    "regionSeoul": "서울",
    "regionGyeonggi": "경기",
    "regionBusan": "부산",
    "howLabel": "가는 방법",
    "place_myeongdong_name": "명동",
    "place_myeongdong_desc": "쇼핑·길거리 음식·면세점이 밀집한 서울의 대표 관광·쇼핑 거리입니다.",
    "place_myeongdong_how": "지하철 4호선 명동역. 쇼핑가는 1·6–8번 출구가 가깝습니다.",
    "place_gyeongbok_name": "경복궁",
    "place_gyeongbok_desc": "조선의 법궁. 한복 대여·근정전·국립고궁박물관과 함께 방문하기 좋습니다.",
    "place_gyeongbok_how": "3호선 경복궁역 5번 출구. 광화문·안국역에서도 도보 가능.",
    "place_gangnam_name": "강남",
    "place_gangnam_desc": "쇼핑·카페·나이트라이프. 강남역·신논현·가로수길·압구정 일대를 포함해 부르는 경우가 많습니다.",
    "place_gangnam_how": "2호선·신분당 강남역. 번화가는 11·12번 출구 방면.",
    "place_hongdae_name": "홍대",
    "place_hongdae_desc": "젊음·버스킹·카페·클럽. 저녁~밤 분위기가 특히 유명합니다.",
    "place_hongdae_how": "2호선·공항철도·경의중앙 홍대입구역. 9·1번 출구가 번화가와 가깝습니다.",
    "place_itaewon_name": "이태원",
    "place_itaewon_desc": "세계 음식·바가 모인 거리. 해방촌·경리단길과도 이어집니다.",
    "place_itaewon_how": "6호선 이태원역 1–4번 출구.",
    "place_suwon_name": "수원 화성",
    "place_suwon_desc": "유네스코 세계유산 수원화성. 성곽 산책과 행궁이 볼거리입니다.",
    "place_suwon_how": "1호선 수원역 후 버스·택시, 또는 수인분당·도보 코스를 지도 앱으로 확인.",
    "place_goyang_name": "일산 호수공원",
    "place_goyang_desc": "넓은 공원·자전거·야경. 가족·피크닉 코스로 인기입니다.",
    "place_goyang_how": "3호선 마두·정발산역 인근. 호수공원 출구를 지도에서 확인하세요.",
    "place_gapyeong_name": "가평·남이섬",
    "place_gapyeong_desc": "남이섬·자른·쁘띠프랑스 등 경기 동북부 당일 여행 명소.",
    "place_gapyeong_how": "경춘선 가평·남이섬(경강)역. ITX·청춘 열차도 이용합니다.",
    "place_haeundae_name": "해운대",
    "place_haeundae_desc": "부산의 대표 해변. 동백섬·달맞이·마린시티와 함께 즐깁니다.",
    "place_haeundae_how": "부산도시철도 2호선 해운대역. 해변은 도보 또는 짧은 버스.",
    "place_nampo_name": "남포·자갈치",
    "place_nampo_desc": "자갈치시장·국제시장·비프광장. 해산물과 부산 먹거리가 풍부합니다.",
    "place_nampo_how": "1호선 자갈치·남포역.",
    "place_seomyeon_name": "서면",
    "place_seomyeon_desc": "부산의 중심 번화가. 쇼핑·음식·교통 환승의 허브입니다.",
    "place_seomyeon_how": "1·2호선 서면역.",
}

PLACES_EN = {
    "tabPlaces": "Popular sights",
    "placesIntro": "Pick a region, then browse popular places with short how-to-get tips.",
    "regionSeoul": "Seoul",
    "regionGyeonggi": "Gyeonggi",
    "regionBusan": "Busan",
    "howLabel": "How to get there",
    "place_myeongdong_name": "Myeongdong",
    "place_myeongdong_desc": "Seoul’s classic shopping and street-food district with duty-free stores.",
    "place_myeongdong_how": "Line 4 Myeongdong Station. Exits 1 and 6–8 are closest to the main street.",
    "place_gyeongbok_name": "Gyeongbokgung",
    "place_gyeongbok_desc": "Joseon’s main palace — pair with hanbok rental and the palace museum.",
    "place_gyeongbok_how": "Line 3 Gyeongbokgung Station exit 5. Also walkable from Gwanghwamun/Anguk.",
    "place_gangnam_name": "Gangnam",
    "place_gangnam_desc": "Shopping, cafés, nightlife — often includes Gangnam Station, Sinnonhyeon, Garosu-gil, Apgujeong.",
    "place_gangnam_how": "Line 2 / Shinbundang Gangnam Station; exits 11–12 for the busy side.",
    "place_hongdae_name": "Hongdae",
    "place_hongdae_desc": "Youth culture, busking, cafés, clubs — especially lively at night.",
    "place_hongdae_how": "Line 2 / AREX / Gyeongui–Jungang Hongik Univ. Station; exits 9 and 1.",
    "place_itaewon_name": "Itaewon",
    "place_itaewon_desc": "International food and bars; connects toward Haebangchon and Gyeongnidan.",
    "place_itaewon_how": "Line 6 Itaewon Station exits 1–4.",
    "place_suwon_name": "Suwon Hwaseong",
    "place_suwon_desc": "UNESCO fortress walls and Hwaseong Haenggung palace.",
    "place_suwon_how": "Line 1 Suwon Station then bus/taxi, or check Suin–Bundang walking routes.",
    "place_goyang_name": "Ilsan Lake Park",
    "place_goyang_desc": "Large park for cycling, picnics, and evening lights.",
    "place_goyang_how": "Line 3 Madu / Jeongbalsan area — check lake-park exits on the map.",
    "place_gapyeong_name": "Gapyeong · Nami Island",
    "place_gapyeong_desc": "Nami Island and nearby day-trip spots in northeast Gyeonggi.",
    "place_gapyeong_how": "Gyeongchun Line Gapyeong / Nami Island (Gyeonggang) Station; ITX also runs.",
    "place_haeundae_name": "Haeundae",
    "place_haeundae_desc": "Busan’s famous beach with Dongbaek Island and Marine City nearby.",
    "place_haeundae_how": "Busan Metro Line 2 Haeundae Station; short walk or bus to the sand.",
    "place_nampo_name": "Nampo · Jagalchi",
    "place_nampo_desc": "Jagalchi fish market, Gukje Market, and BIFF Square eats.",
    "place_nampo_how": "Line 1 Jagalchi / Nampo Stations.",
    "place_seomyeon_name": "Seomyeon",
    "place_seomyeon_desc": "Busan’s central shopping and transfer hub.",
    "place_seomyeon_how": "Lines 1 & 2 Seomyeon Station.",
}

PLACES_JA = {
    "tabPlaces": "代表名所案内",
    "placesIntro": "地域を選んでから、旅行者に人気の名所とアクセスのヒントを確認してください。",
    "regionSeoul": "ソウル",
    "regionGyeonggi": "京畿",
    "regionBusan": "釜山",
    "howLabel": "行き方",
    "place_myeongdong_name": "明洞",
    "place_myeongdong_desc": "ショッピングと屋台、免税店が集まるソウルの定番エリア。",
    "place_myeongdong_how": "4号線明洞駅。1・6–8番出口が近いです。",
    "place_gyeongbok_name": "景福宮",
    "place_gyeongbok_desc": "朝鮮の法宮。韓服レンタルや博物館と合わせて。",
    "place_gyeongbok_how": "3号線景福宮駅5番出口。光化門・安国からも徒歩可。",
    "place_gangnam_name": "江南",
    "place_gangnam_desc": "ショッピング・カフェ・ナイトライフ。駅周辺や狎鴎亭も含めて呼ばれます。",
    "place_gangnam_how": "2号線・新盆唐江南駅。11・12番出口方面がにぎやか。",
    "place_hongdae_name": "弘大",
    "place_hongdae_desc": "若者文化・バスキング・カフェ・クラブ。夜が特に有名。",
    "place_hongdae_how": "2号線・空港鉄道・京義中央弘大入口駅。9・1番出口。",
    "place_itaewon_name": "梨泰院",
    "place_itaewon_desc": "多国籍フードとバー。解放村・京里达にもつながります。",
    "place_itaewon_how": "6号線梨泰院駅1–4番出口。",
    "place_suwon_name": "水原華城",
    "place_suwon_desc": "ユネスコ世界遺産の城郭。行宮と散歩がおすすめ。",
    "place_suwon_how": "1号線水原駅からバス・タクシー等。地図で確認を。",
    "place_goyang_name": "一山湖水公園",
    "place_goyang_desc": "広い公園でサイクリングや夜景が人気。",
    "place_goyang_how": "3号線馬頭・鼎鉢山周辺。出口は地図で確認。",
    "place_gapyeong_name": "加平・南怡島",
    "place_gapyeong_desc": "南怡島など京畿東北部の日帰りスポット。",
    "place_gapyeong_how": "京春線加平・南怡島（京江）駅。ITXも利用可。",
    "place_haeundae_name": "海雲台",
    "place_haeundae_desc": "釜山を代表するビーチ。冬柏島やマリンシティも。",
    "place_haeundae_how": "釜山都市鉄道2号線海雲台駅。",
    "place_nampo_name": "南浦・札嘎致",
    "place_nampo_desc": "札嘎致市場・国際市場・BIFF広場の食べ歩き。",
    "place_nampo_how": "1号線札嘎致・南浦駅。",
    "place_seomyeon_name": "西面",
    "place_seomyeon_desc": "釜山の中心繁華街・乗換ハブ。",
    "place_seomyeon_how": "1・2号線西面駅。",
}

SHOP_KO = {
    "intro": "올리브영·다이소부터 면세·시장까지, 외국인이 자주 묻는 쇼핑 팁을 모았습니다.",
    "catBeauty": "뷰티·올리브영",
    "catDaily": "다이소·생활",
    "catDuty": "면세·환급",
    "catMarket": "시장·번화가",
    "oliveTitle": "올리브영 팁",
    "olive1": "인기 제품은 ‘올영픽’·세일 코너를 먼저 보세요. 시트마스크·선크림·틴트는 선물용으로 많이 삽니다.",
    "olive2": "멤버십/앱 쿠폰이 있으면 할인폭이 커질 수 있습니다. 직원에게 세일 중인 유사 제품을 물어보세요.",
    "olive3": "공항·명동 매장은 관광객용 세트 구성이 많고, 동네 매장은 재고·가격이 다를 수 있습니다.",
    "daisoTitle": "다이소 팁",
    "daiso1": "균일가 생활용품·문구·여행용 소품이 강점입니다. 캐리어에 넣기 쉬운 작은 아이템을 고르세요.",
    "daiso2": "층별로 카테고리가 나뉩니다. 필요한 키워드(예: 여행, 수납)로 매장 안내판을 확인하세요.",
    "dutyTitle": "면세·택스프리",
    "duty1": "시내면세점·공항 면세는 여권·항공권이 필요할 수 있습니다. 구매 한도와 수령 방식을 미리 확인하세요.",
    "duty2": "일반 가게 택스프리는 최소 금액·여권 제시·출국 시 환급 절차가 있습니다. ‘TAX FREE’ 스티커가 있는 가게인지 확인하세요.",
    "marketTitle": "시장·번화가",
    "market1": "광장시장·남대문·동대문은 현금이 편한 곳이 있습니다. 카드 가능 여부를 먼저 물어보세요.",
    "market2": "명동·홍대·강남은 브랜드 매장과 길거리 음식이 많습니다. 주말 저녁은 매우 붐빕니다.",
}

SHOP_EN = {
    "intro": "From Olive Young and Daiso to duty-free and markets — shopping tips visitors ask about most.",
    "catBeauty": "Beauty · Olive Young",
    "catDaily": "Daiso · Daily",
    "catDuty": "Duty-free · Refund",
    "catMarket": "Markets · Districts",
    "oliveTitle": "Olive Young tips",
    "olive1": "Start with ‘Olive Young Picks’ and sale shelves. Sheet masks, sunscreen, and tints are popular gifts.",
    "olive2": "App/membership coupons can add discounts — ask staff about similar items on sale.",
    "olive3": "Airport/Myeongdong stores stock tourist sets; neighborhood stores may differ in stock and price.",
    "daisoTitle": "Daiso tips",
    "daiso1": "Great for fixed-price household goods, stationery, and travel bits that fit a suitcase.",
    "daiso2": "Floors are categorized — follow in-store signs for travel/storage keywords.",
    "dutyTitle": "Duty-free & tax free",
    "duty1": "Downtown/airport duty-free may need passport and flight info — check pickup rules.",
    "duty2": "Shop tax-free needs a minimum spend, passport, and airport refund steps. Look for TAX FREE signs.",
    "marketTitle": "Markets & streets",
    "market1": "Gwangjang, Namdaemun, and Dongdaemun sometimes prefer cash — ask if cards work.",
    "market2": "Myeongdong, Hongdae, and Gangnam mix brands and street food; weekends get crowded.",
}

SHOP_JA = {
    "intro": "オリーブヤングやダイソーから免税・市場まで、旅行者がよく聞くショッピングのヒントです。",
    "catBeauty": "美容·オリーブヤング",
    "catDaily": "ダイソー·生活",
    "catDuty": "免税·還付",
    "catMarket": "市場·繁華街",
    "oliveTitle": "オリーブヤングのヒント",
    "olive1": "まずは『オリヤンピック』やセールコーナーへ。シートマスク・日焼け止め・ティントが人気お土産です。",
    "olive2": "アプリ／会員クーポンで割引が広がることがあります。",
    "olive3": "空港・明洞店は観光向けセットが多く、街の店と在庫・価格が違うことがあります。",
    "daisoTitle": "ダイソーのヒント",
    "daiso1": "均一価格の生活雑貨・文具が強み。スーツケースに入る小さめを選びましょう。",
    "daiso2": "フロア案内でカテゴリーを確認してください。",
    "dutyTitle": "免税・TAX FREE",
    "duty1": "市内・空港免税はパスポートや航空券が必要な場合があります。",
    "duty2": "一般店のTAX FREEは最低金額・パスポート・出国時還付の手続きがあります。",
    "marketTitle": "市場・繁華街",
    "market1": "広蔵・南大門・東大門は現金が楽な店もあります。カード可否を確認。",
    "market2": "明洞・弘大・江南は週末夜に混みます。",
}


def patch_places_shop():
    for lang, places, shop in (
        ("ko", PLACES_KO, SHOP_KO),
        ("en", PLACES_EN, SHOP_EN),
        ("ja", PLACES_JA, SHOP_JA),
    ):
        data = load(lang)
        t = data.setdefault("transport", {})
        t["tabRoutes"] = places["tabPlaces"]
        t.update(places)
        data.setdefault("shopping", {}).update(shop)
        if lang == "ko":
            data.setdefault("misc", {})["shoppingTitle"] = "쇼핑 가이드"
            data["misc"]["shoppingIntro"] = shop["intro"]
        elif lang == "en":
            data.setdefault("misc", {})["shoppingTitle"] = "Shopping guide"
            data["misc"]["shoppingIntro"] = shop["intro"]
        else:
            data.setdefault("misc", {})["shoppingTitle"] = "ショッピングガイド"
            data["misc"]["shoppingIntro"] = shop["intro"]
        save(lang, data)
        print("places+shop", lang)


def main():
    write_combo_pages()
    patch_convenience_i18n()
    patch_places_shop()


if __name__ == "__main__":
    main()
