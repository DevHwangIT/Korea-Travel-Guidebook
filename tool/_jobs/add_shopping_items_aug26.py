# -*- coding: utf-8 -*-
"""Add shopping souvenir items with downloaded product photos."""
from __future__ import annotations

import io
import json
import ssl
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

from PIL import Image

JOBS = Path(__file__).resolve().parent
TOOL = JOBS.parent
ROOT = TOOL.parent
sys.path.insert(0, str(TOOL))

from lib.cache_bust import VERSION_FILE, iter_html_files, process_html  # noqa: E402
from lib.content import _write_text_retry  # noqa: E402

SHOPPING = ROOT / "i18n" / "pages" / "shopping"
BUY = ROOT / "pages" / "buy" / "index.html"
SOUVENIR = ROOT / "pages" / "souvenir"
LANGS = ("ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru")
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)

CTX = ssl.create_default_context()

PAGE_TMPL = """<!DOCTYPE html>
<html lang="ko" data-i18n-title="souvenir.{key}Title">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Souvenir</title>
  <link rel="stylesheet" href="../../../styles.css">
</head>
<body>
  <nav class="lang-switch" aria-label="Language"></nav>
  <header class="site-header">
    <a href="../../../index.html" class="site-brand" data-i18n="common.brand">Korea Travel Guide</a>
  </header>
  <main class="page article-page">
    <p class="back-link"><a href="../../buy/index.html#shopping" data-i18n="souvenir.backList">← 쇼핑 & 놀거리</a></p>
    <article class="souvenir-article">
      <img class="combo-article-hero" src="media/cover.jpg" alt="" data-i18n-attr="alt:souvenir.{key}Title">
      <h1 data-i18n="souvenir.{key}Title"></h1>
      <p class="article-lead" data-i18n="souvenir.{key}Desc"></p>
      <div class="content-body" data-content-body data-body-path="souvenir.{key}Body"></div>
      <div data-content-body-fallback>
      <p data-i18n="souvenir.{key}Body1"></p>
      <p data-i18n="souvenir.{key}Body2"></p>
      <div class="tip">
        <h3 data-i18n="souvenir.tipTitle">사는 팁</h3>
        <p data-i18n="souvenir.{key}Tip"></p>
      </div>
      </div>
    </article>
  </main>
  <footer class="site-footer">
    <hr>
    <img src="../../../Images/cover/footer-korea.png" width="100%" alt="Korea Travel">
    <p class="footer-note" data-i18n="common.footer">© Korea Travel Guide</p>
  </footer>
  <script src="../../../i18n/messages.js"></script>
  <script src="../../../js/i18n.js"></script>
  <script src="../../../js/analytics.js"></script>
  <script src="../../../js/content-body.js"></script>
</body>
</html>
"""


def card_html(slug: str, key: str) -> str:
    return (
        f'              <a class="souvenir-card" href="../souvenir/{slug}/index.html">\n'
        f'                <img src="../souvenir/{slug}/media/cover.jpg" alt="" data-i18n-attr="alt:souvenir.{key}Title">\n'
        f'                <div class="souvenir-card-body">\n'
        f'                  <h3 data-i18n="souvenir.{key}Title"></h3>\n'
        f'                  <p data-i18n="souvenir.{key}Desc"></p>\n'
        f'                  <span class="souvenir-more" data-i18n="souvenir.readMore">자세히 보기 →</span>\n'
        f"                </div>\n"
        f"              </a>\n"
    )


def mx(ko: str, en: str, ja: str = "", zh: str = "", zht: str = "") -> dict:
    ja = ja or en
    zh = zh or en
    zht = zht or zh
    return {
        "ko": ko,
        "en": en,
        "ja": ja,
        "zh": zh,
        "zh-Hant": zht,
        "vi": en,
        "th": en,
        "ru": en,
    }


def body_arr(b1: dict, b2: dict, tip: dict) -> list:
    return [
        {"type": "text", **b1},
        {"type": "text", **b2},
        {"type": "callout", **tip},
    ]


# tab: food | snacks | daiso | health | beauty
# existing=True → update cover only (and still refresh i18n if provided)
ITEMS = [
    {
        "slug": "gwangcheon-kim",
        "key": "gwangcheonKim",
        "tab": "food",
        "url": "https://sitem.ssgcdn.com/62/52/40/item/1000034405262_i1_750.jpg",
        "title": mx("광천김", "Gwangcheon Gim (seaweed)", "広川海苔", "广川海苔", "廣川海苔"),
        "desc": mx(
            "충남 광천 특산 김 — 조미김·돌김 선물 세트.",
            "Chungnam Gwangcheon seaweed — seasoned gim gift packs.",
            "忠南広川の海苔。味付け海苔・ギフトセット。",
            "忠南广川海苔，调味紫菜礼盒。",
            "忠南廣川海苔，調味紫菜禮盒。",
        ),
        "b1": mx(
            "광천김은 충남 홍성 광천 일대에서 나는 김으로, 마트·전통시장·공항에서 한국 음식으로 많이 사 가는 기념품입니다. 조미김은 밥반찬·간식으로 바로 먹을 수 있습니다.",
            "Gwangcheon gim is seaweed from Hongseong, Chungnam. Travelers often buy seasoned sheets as a light Korean food souvenir at marts, markets, and airports.",
        ),
        "b2": mx(
            "습기와 눌림에 약하니 지퍼백에 넣고 캐리어 중앙에 두세요. 기름·소금이 있는 조미김은 개봉 후 빨리 먹는 편이 좋습니다.",
            "Keep packs dry and uncrushed in the middle of your suitcase. Eat seasoned gim soon after opening.",
        ),
        "tip": mx(
            "구매 팁\n\n대형마트 묶음이 관광지보다 저렴한 경우가 많고, 선물용은 개별 포장 세트를 고르세요.",
            "Buying tip\n\nHypermarket multipacks are usually cheaper than tourist shops; pick individually wrapped gift sets to share.",
        ),
    },
    {
        "slug": "nongshim-jangkalguksu",
        "key": "nongshimJangkalguksu",
        "tab": "food",
        "url": "https://image.nongshim.com/non/pro/1708563291563.jpg",
        "title": mx("농심 얼큰 장칼국수", "Nongshim Spicy Jangkalguksu", "農心 ピリ辛 ジャンカルグクス", "农心辣酱刀削面", "農心辣醬刀削麵"),
        "desc": mx(
            "농심 얼큰 장칼국수 — 칼칼한 장칼국수 라면.",
            "Nongshim spicy jang-kalguksu instant noodles.",
            "農心のピリ辛ジャンカルグクス袋麺。",
            "农心辣味酱刀削面袋装面。",
            "農心辣味醬刀削麵袋裝麵。",
        ),
        "b1": mx(
            "농심 얼큰 장칼국수는 된장소스 칼국수 맛을 매콤하게 낸 봉지라면입니다. 불닭·짜왕과 함께 마트 라면 코너에서 사 가기 좋은 한국 음식 기념품입니다.",
            "Nongshim spicy jang-kalguksu is bag ramen with a spicy soybean-paste noodle taste. A easy Korean food souvenir next to Buldak and Jjawang in mart ramen aisles.",
        ),
        "b2": mx(
            "스프·액상 소스는 지퍼백에 한 번 더 넣어 주세요. 이마트·홈플러스 특가가 편의점보다 저렴한 경우가 많습니다.",
            "Double-bag soup and sauce packets. Hypermarket deals usually beat convenience-store prices.",
        ),
        "tip": mx(
            "구매 팁\n\n멀티팩으로 사고, 조리법은 봉지 뒷면을 확인하세요.",
            "Buying tip\n\nBuy a multipack and check the cooking steps on the back of the bag.",
        ),
    },
    {
        "slug": "ottogi-chamkkae-noodle",
        "key": "ottogiChamkkaeNoodle",
        "tab": "food",
        "url": "https://lottemartzetta.com/images-v3/932dcbc7-fca8-4d43-bcde-f73d1ce3cc7d/657258e2-075d-4086-901b-62087ee6eba3/500x500.jpg",
        "title": mx("오뚜기 참깨누들", "Ottogi Sesame Noodles", "オットギ ごまヌードル", "不倒翁芝麻面", "不倒翁芝麻麵"),
        "desc": mx(
            "오뚜기 참깨누들 — 고소한 참깨 소스 면.",
            "Ottogi sesame noodles — nutty sesame sauce ramen.",
            "オットギのごまソース麺。",
            "不倒翁芝麻酱拌面。",
            "不倒翁芝麻醬拌麵。",
        ),
        "b1": mx(
            "오뚜기 참깨누들은 참깨 소스를 비벼 먹는 라면입니다. 매운 라면보다 덜 맵고 고소해서, 매운 음식을 부담스러워하는 여행객 선물로도 무난합니다.",
            "Ottogi Chamkkae Noodle is mixed with a sesame sauce. Milder and nuttier than spicy ramyeon, so it works as a gift for travelers who skip heat.",
        ),
        "b2": mx(
            "물을 버리고 소스를 비비는 타입이 많습니다. 액상 소스는 캐리어에서 새지 않게 지퍼백에 넣으세요.",
            "Many versions drain the water then mix sauce. Bag liquid packets so they do not leak in luggage.",
        ),
        "tip": mx(
            "구매 팁\n\n대형마트 라면 코너·온라인 묶음이 찾기 쉽습니다.",
            "Buying tip\n\nLook in hypermarket ramen aisles or online multipacks.",
        ),
    },
    {
        "slug": "ahri-cup-ramen",
        "key": "ahriCupRamen",
        "tab": "food",
        "url": "https://prs.ohousecdn.com/apne2/any/uploads/productions/v1-515119579951232.jpg?w=480&h=480&c=c",
        "title": mx("AHRI 컵라면", "AHRI Cup Ramen", "AHRI カップ麺", "AHRI 杯面", "AHRI 杯麵"),
        "desc": mx(
            "AHRI 컵라면 — 캐릭터 콜라보 컵라면 기념품.",
            "AHRI cup ramen — character-collab instant cup noodles.",
            "AHRIコラボのカップ麺。お土産向き。",
            "AHRI 联名杯面，适合当纪念品。",
            "AHRI 聯名杯麵，適合作紀念品。",
        ),
        "b1": mx(
            "AHRI 컵라면은 게임 캐릭터 콜라보 컵라면으로, 맛과 패키지 모두 기념품처럼 사 가는 경우가 많습니다. 편의점·온라인·팝업에서 재고가 들쭉날쭉합니다.",
            "AHRI cup ramen is a character-collaboration cup noodle. People buy it as much for the package as the taste. Stock jumps around at convenience stores, online, and pop-ups.",
        ),
        "b2": mx(
            "컵라면은 부피가 크니 캐리어 공간을 확인하고, 액상 스프는 지퍼백에 넣어 주세요. 한정판은 정가·중고가를 비교하세요.",
            "Cups take space in a suitcase. Bag sauce packets. For limited editions, compare official and resale prices.",
        ),
        "tip": mx(
            "구매 팁\n\n공식 판매처·대형마트 재고를 먼저 보고, 관광지 프리미엄은 피하세요.",
            "Buying tip\n\nCheck official or hypermarket stock first and skip tourist-markup prices.",
        ),
    },
    {
        "slug": "chaltteok-dameun-pie",
        "key": "chaltteokDameunPie",
        "tab": "snacks",
        "url": "https://sitem.ssgcdn.com/45/34/23/item/1000632233445_i1_750.jpg",
        "title": mx("찰떡 담은파이", "Chaltteok-Dameun Pie", "餅入りパイ", "糯米派", "糯米派"),
        "desc": mx(
            "SPC 빚은 찰떡 담은파이 — 냉장 디저트 파이.",
            "SPC Bizeun chaltteok-filled pie — a chilled dessert pie.",
            "SPCビジュンの冷蔵・餅入りパイ。",
            "SPC 빚은 冷藏糯米派。",
            "SPC 빚은 冷藏糯米派。",
        ),
        "b1": mx(
            "찰떡 담은파이는 SPC 빚은에서 파는 냉장 파이로, 속에 찰떡이 들어간 디저트입니다. 편의점 상온 ‘찰떡파이’(롯데)와는 다른 제품이니 포장을 확인하세요.",
            "Chaltteok-Dameun Pie is a chilled SPC Bizeun dessert pie with sticky-rice cake inside. It is not Lotte’s room-temperature Chaltteok Pie — check the label.",
        ),
        "b2": mx(
            "냉장 상품이라 당일·다음날 먹는 용도나 아이스팩이 있을 때만 가져가세요. 편의점·슈퍼 디저트 코너에서 구합니다.",
            "It is refrigerated, so eat it the same day or pack ice. Find it in convenience-store and supermarket dessert cases.",
        ),
        "tip": mx(
            "구매 팁\n\n장거리 비행 기념품보다는 숙소·당일 간식으로 사는 편이 안전합니다.",
            "Buying tip\n\nBetter as a same-day snack than a long-haul souvenir unless you have a cooler.",
        ),
    },
    {
        "slug": "yegam-cheese-gratin",
        "key": "yegamCheeseGratin",
        "tab": "snacks",
        "url": "https://crcf.cookatmarket.com/singong/images/2025/06/dasi_1749606207_7747.png",
        "title": mx("예감 치즈그라탕맛", "Yegam Cheese Gratin", "イェガム チーズグラタン味", "预感芝士焗味", "預感起司焗味"),
        "desc": mx(
            "오리온 예감 치즈그라탕맛 — 고구마 스낵 시즌 맛.",
            "Orion Yegam cheese-gratin flavor — a sweet-potato snack.",
            "オリオン・イェガムのチーズグラタン味。",
            "好丽友预感芝士焗味红薯零食。",
            "好麗友預感起司焗味地瓜零食。",
        ),
        "b1": mx(
            "예감은 오리온의 고구마 스낵이고, 치즈그라탕맛은 고소하고 짭짤한 시즌·한정 맛입니다. 편의점·마트 과자 코너에서 찾기 좋습니다.",
            "Yegam is Orion’s sweet-potato snack; cheese-gratin is a savory limited flavor. Easy to find in convenience-store and mart snack aisles.",
        ),
        "b2": mx(
            "봉지가 부풀어 잘 찢어지니 캐리어에 세게 누르지 마세요. 시즌 맛은 재고가 빨리 떨어질 수 있습니다.",
            "Bags puff and tear easily — do not crush them in luggage. Limited flavors can sell out.",
        ),
        "tip": mx(
            "구매 팁\n\n편의점보다 대형마트 묶음이 저렴한 경우가 많습니다.",
            "Buying tip\n\nHypermarket multipacks are often cheaper than convenience stores.",
        ),
    },
    {
        "slug": "mallang-cow",
        "key": "mallangCow",
        "tab": "snacks",
        "url": "https://i.namu.wiki/i/FviBLeUs75lDikXyg9BsYOLdHGXkWkgBtpe25Bvpi4GIqrM5GuuP-LfUJ7erh-FDY9GE4hv1r_VscS72tnwiGg.webp",
        "title": mx("말랑카우", "Mallang Cow", "マランカウ", "软牛糖", "軟牛糖"),
        "desc": mx(
            "크라운 말랑카우 — 말랑한 캐러멜 캔디.",
            "Crown Mallang Cow — a soft caramel chewy candy.",
            "クラウンの柔らかいキャラメルキャンディ。",
            "可瑞安软牛糖，软糯焦糖糖。",
            "可瑞安軟牛糖，軟糯焦糖糖。",
        ),
        "b1": mx(
            "말랑카우는 크라운의 말랑한 캐러멜 캔디입니다. 작아서 가방에 넣기 쉽고, 한국 과자 선물 묶음에 자주 들어갑니다.",
            "Mallang Cow is Crown’s soft caramel candy. Small and easy to pack, it often shows up in Korean snack gift piles.",
        ),
        "b2": mx(
            "더운 날에는 녹을 수 있으니 기내 반입·그늘 보관을 권합니다. 편의점·마트에서 쉽게 삽니다.",
            "It can melt in heat — keep it in the cabin or shade. Easy to buy at convenience stores and marts.",
        ),
        "tip": mx(
            "구매 팁\n\n낱개 봉지가 나눠 주기 좋고, 유통기한을 확인하세요.",
            "Buying tip\n\nSmall packs are easy to share; check the expiry date.",
        ),
    },
    {
        "slug": "ace-cracker",
        "key": "aceCracker",
        "tab": "snacks",
        "url": "https://i.namu.wiki/i/VPHrXsk7tWQ5Dx8J_7BvPEQOCW9xwyhZ7r2_3WaPa6lVN3Rmc8yWTVw-C8bnyD7fMr8woYFLUAe1g33BeOJoWA.webp",
        "title": mx("에이스", "Haitai Ace", "ヘテ エース", "海太Ace饼干", "海太Ace餅乾"),
        "desc": mx(
            "해태 에이스 — 담백한 발효 크래커.",
            "Haitai Ace — a light fermented cracker.",
            "ヘテのプレーンな発酵クラッカー。",
            "海太Ace，清淡发酵饼干。",
            "海太Ace，清淡發酵餅乾。",
        ),
        "b1": mx(
            "에이스는 해태의 담백한 크래커로, 한국에서 오래 사랑받은 과자입니다. 너무 달지 않아 차·커피와 같이 기념품으로 사기 좋습니다.",
            "Ace is Haitai’s light cracker and a long-time Korean staple. Not too sweet, so it pairs well with tea or coffee as a souvenir.",
        ),
        "b2": mx(
            "박스 포장이라 깨지지 않게 옷 사이에 넣으세요. 대형마트 대용량이 공항보다 저렴합니다.",
            "Boxes can crush — pack between clothes. Large mart packs beat airport prices.",
        ),
        "tip": mx(
            "구매 팁\n\n이마트·홈플러스 과자 코너에서 묶음을 고르세요.",
            "Buying tip\n\nPick a multipack in the hypermarket snack aisle.",
        ),
    },
    {
        "slug": "gosomi",
        "key": "gosomi",
        "tab": "snacks",
        "url": "https://lottemartzetta.com/images-v3/932dcbc7-fca8-4d43-bcde-f73d1ce3cc7d/d5576994-f2f4-4b3b-aee9-acd4f1c5e032/500x500.jpg",
        "title": mx("고소미", "Gosomi", "ゴソミ", "高笑美", "高笑美"),
        "desc": mx(
            "롯데 고소미 — 참깨 고소한 크래커.",
            "Lotte Gosomi — a sesame-savory cracker.",
            "ロッテ・ゴソミ。ごま風味クラッカー。",
            "乐天高笑美，芝麻香饼干。",
            "樂天高笑美，芝麻香餅乾。",
        ),
        "b1": mx(
            "고소미는 롯데의 참깨 풍미 크래커입니다. 에이스·예감과 함께 한국 과자 세트로 사 가기 좋은 스테디셀러입니다.",
            "Gosomi is Lotte’s sesame-flavored cracker. A steady seller to pack with Ace and Yegam in a Korean snack set.",
        ),
        "b2": mx(
            "봉지가 쉽게 구겨지니 상자나 옷 사이에 넣어 주세요. 편의점·마트에서 구합니다.",
            "Bags crease easily — pack in a box or between clothes. Sold at convenience stores and marts.",
        ),
        "tip": mx(
            "구매 팁\n\n대용량·묶음이 낱개보다 가성비가 좋습니다.",
            "Buying tip\n\nFamily or multipacks are better value than singles.",
        ),
    },
    {
        "slug": "jocheong-yugwa",
        "key": "jocheongYugwa",
        "tab": "snacks",
        "url": "https://image.nongshim.com/non/pro/1495610654553.jpg",
        "title": mx("조청유과", "Jocheong Yugwa", "チョチョンユグァ", "造清油果", "造清油果"),
        "desc": mx(
            "농심 조청유과 — 조청 바른 전통 유과 스낵.",
            "Nongshim jocheong yugwa — puffed rice snacks with grain syrup.",
            "農心のチョチョンユグァ。伝統菓子スナック。",
            "农心造清油果，麦芽糖传统米果。",
            "農心造清油果，麥芽糖傳統米果。",
        ),
        "b1": mx(
            "조청유과는 농심이 만든 유과 스낵으로, 조청의 달콤함과 바삭한 식감이 특징입니다. 한과를 부담 없이 맛보고 싶을 때 마트에서 사기 좋습니다.",
            "Nongshim Jocheong Yugwa is a puffed traditional sweet with grain-syrup flavor. An easy mart way to try hangwa-style snacks.",
        ),
        "b2": mx(
            "바삭해서 잘 부서지므로 캐리어 위쪽보다 옷 사이에 넣으세요. 단맛이 있어 차와 잘 맞습니다.",
            "It crushes easily — pack between clothes, not on top. The sweetness pairs well with tea.",
        ),
        "tip": mx(
            "구매 팁\n\n농심 과자 코너·대형마트에서 구하세요.",
            "Buying tip\n\nFind it in the Nongshim snack section at hypermarkets.",
        ),
    },
    {
        "slug": "choco-chip",
        "key": "chocoChip",
        "tab": "snacks",
        "url": "https://i.namu.wiki/i/g5s2KN7CW2sLas8b9vkIqMGs8PXDpjEZbFS_oA9zk2Go3OqIRSKTZRAYZiuanGypd2VMrPE-viZh_n6c2WF7UA.webp",
        "title": mx("초코칩", "Choco Chip", "チョコチップ", "巧克力豆饼干", "巧克力豆餅乾"),
        "desc": mx(
            "오리온 초코칩 — 초코칩 쿠키 과자.",
            "Orion Choco Chip — chocolate-chip cookies.",
            "オリオンのチョコチップクッキー。",
            "好丽友巧克力豆饼干。",
            "好麗友巧克力豆餅乾。",
        ),
        "b1": mx(
            "초코칩은 오리온의 초코칩 쿠키로, 한국 편의점·마트에서 흔히 보는 과자입니다. 달콤해서 아이·친구 선물용 묶음에 넣기 좋습니다.",
            "Orion Choco Chip is a common convenience-store cookie. Sweet enough to drop into a snack pile for kids or friends.",
        ),
        "b2": mx(
            "초콜릿은 더운 날 녹을 수 있으니 기내 반입을 권합니다. 낱개 포장 멀티팩이 나눠 주기 쉽습니다.",
            "Chocolate can melt in heat — keep it in the cabin. Individually wrapped multipacks are easy to share.",
        ),
        "tip": mx(
            "구매 팁\n\n대형마트 묶음이 공항 가격보다 저렴합니다.",
            "Buying tip\n\nHypermarket packs beat airport prices.",
        ),
    },
    {
        "slug": "dr-cpu-mulgwang-ampoule",
        "key": "drCpuMulgwangAmpoule",
        "tab": "daiso",
        "url": "https://cdn.daisomall.co.kr/file/resize/PD/20250403/thumbnail/850/fzK1IFvyEpmvaVhksrnL1062710_00_04fzK1IFvyEpmvaVhksrnL.png",
        "title": mx("닥터CPU 물광앰플샷", "Dr.CPU Water-Glow Ampoule Shot", "Dr.CPU 水光アンプルショット", "Dr.CPU 水光安瓶精华", "Dr.CPU 水光安瓶精華"),
        "desc": mx(
            "다이소 닥터CPU 물광앰플샷 — 휴대용 수분 앰플.",
            "Daiso Dr.CPU water-glow ampoule shot — a travel-size hydrating ampoule.",
            "ダイソーのDr.CPU水光アンプル。携帯しやすい。",
            "Daiso Dr.CPU 水光安瓶，便于携带。",
            "Daiso Dr.CPU 水光安瓶，便於攜帶。",
        ),
        "b1": mx(
            "닥터CPU 물광앰플샷은 다이소에서 파는 소용량 수분 앰플입니다. 균일가라 여러 개 담기 좋고, 여행·선물용 스킨케어로 자주 집습니다.",
            "Dr.CPU water-glow ampoule shots are small hydrating ampoules at Daiso. The fixed price makes it easy to grab several for travel or gifts.",
        ),
        "b2": mx(
            "액체류라 기내 수하물 100ml 제한을 확인하고, 파우치에 넣어 새지 않게 하세요. 피부 자극이 있으면 사용을 중단하세요.",
            "Liquids count toward the 100ml cabin limit — pouch them against leaks. Stop if your skin reacts.",
        ),
        "tip": mx(
            "구매 팁\n\n다이소몰·매장 키오스크에서 ‘물광앰플’로 검색해 보세요.",
            "Buying tip\n\nSearch “물광앰플” on Daiso Mall or in-store kiosks.",
        ),
    },
    {
        "slug": "yuja-tea",
        "key": "yujaTea",
        "tab": "health",
        "url": "https://img.dongwonmall.com/dwmall/static_root/product_img/main/0036623/003662315_1_a.jpg?f=webp&q=80",
        "title": mx("유자차", "Yuja Tea", "柚子茶", "柚子茶", "柚子茶"),
        "desc": mx(
            "유자차 — 유자청을 물에 타 마시는 한국 차.",
            "Yuja tea — citron marmalade tea to stir into water.",
            "柚子茶。柚子糖漬を湯に溶かす韓国のお茶。",
            "柚子茶，用柚子酱冲泡的韩国茶。",
            "柚子茶，用柚子醬沖泡的韓國茶。",
        ),
        "b1": mx(
            "유자차는 유자청을 따뜻한 물에 풀어 마시는 한국 차입니다. 마트·백화점·공항에서 병·선물세트로 많이 팔리고, 감기 기운·겨울 선물로도 고릅니다.",
            "Yuja tea is Korean citron marmalade stirred into hot water. Sold in jars and gift sets at marts, department stores, and airports — a common winter or feel-better gift.",
        ),
        "b2": mx(
            "유리병은 무겁고 깨지니 완충재를 요청하세요. 당도가 높아 보관은 개봉 후 냉장하는 제품이 많습니다.",
            "Glass jars are heavy and breakable — ask for padding. Many are high-sugar; refrigerate after opening.",
        ),
        "tip": mx(
            "구매 팁\n\n플라스틱·파우치형이 비행기에 더 안전하고, 선물용은 백화점 세트가 포장이 깔끔합니다.",
            "Buying tip\n\nPlastic or pouches travel safer than glass; department-store sets look nicer as gifts.",
        ),
    },
    {
        "slug": "rejuran-skin-protection-mask",
        "key": "rejuranSkinProtectionMask",
        "tab": "beauty",
        "url": "https://image.oliveyoung.co.kr/cfimages/cf-goods/uploads/images/thumbnails/10/0000/0016/A00000016951228ko.jpg?l=ko",
        "title": mx(
            "REJURAN 스킨 프로텍션 마스크",
            "REJURAN Skin Protection Mask",
            "REJURAN スキンプロテクションマスク",
            "REJURAN 肌肤防护面膜",
            "REJURAN 肌膚防護面膜",
        ),
        "desc": mx(
            "리쥬란 스킨 프로텍션 마스크 — 올리브영에서 사는 시트 마스크.",
            "REJURAN Skin Protection Mask — a sheet mask from Olive Young.",
            "オリーブヤングで買えるリジュランのシートマスク。",
            "可在 Olive Young 购买的 REJURAN 面膜。",
            "可在 Olive Young 購買的 REJURAN 面膜。",
        ),
        "b1": mx(
            "REJURAN 스킨 프로텍션 마스크는 올리브영에서 찾기 쉬운 리쥬란 시트 마스크입니다. 한국 화장품 기념품으로 낱장·박스 모두 인기입니다.",
            "REJURAN Skin Protection Mask is a sheet mask easy to find at Olive Young. Popular as a K-beauty souvenir in singles or boxes.",
        ),
        "b2": mx(
            "박스 포장은 구겨지지 않게 캐리어 중앙에 넣으세요. 피부 타입·성분표를 확인하고, 행사 기간 묶음이 저렴합니다.",
            "Keep boxes uncrushed in the middle of your bag. Check your skin type and INCI list; sale bundles are cheaper.",
        ),
        "tip": mx(
            "구매 팁\n\n올리브영 앱·매장 재고를 확인하고, 공항 면세보다 시내 행사를 먼저 보세요.",
            "Buying tip\n\nCheck Olive Young app/store stock; downtown sales often beat airport duty-free.",
        ),
    },
]


EXISTING_PHOTO = [
    {
        "slug": "dr-reju-all",
        "url": "https://drrejuall.com/cdn/shop/files/PDRN_30145e54-718d-4dd4-9388-64d29963d61c.jpg?v=1786083538&width=1500",
    }
]


def download(url: str) -> bytes:
    import subprocess

    headers = {
        "User-Agent": UA,
        "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
        "Referer": url.split("/", 3)[0] + "//" + url.split("/")[2] + "/",
    }
    if "namu.wiki" in url:
        headers["Referer"] = "https://namu.wiki/"
    if "oliveyoung.co.kr" in url:
        headers["Referer"] = "https://www.oliveyoung.co.kr/"
    if "daisomall.co.kr" in url:
        headers["Referer"] = "https://www.daisomall.co.kr/"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=40, context=CTX) as resp:
            return resp.read()
    except Exception:
        cmd = [
            "curl",
            "-fsSL",
            "--tlsv1.2",
            "-A",
            UA,
            "-e",
            headers["Referer"],
            url,
        ]
        raw = subprocess.check_output(cmd, timeout=40)
        if not raw:
            raise RuntimeError("empty curl body")
        return raw


def save_cover(raw: bytes, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(io.BytesIO(raw))
    if im.mode in ("RGBA", "P"):
        bg = Image.new("RGB", im.size, (255, 255, 255))
        im = im.convert("RGBA")
        bg.paste(im, mask=im.split()[-1])
        im = bg
    else:
        im = im.convert("RGB")
    w, h = im.size
    max_side = 1400
    if max(w, h) > max_side:
        scale = max_side / max(w, h)
        im = im.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
    im.save(dest, "JPEG", quality=88, optimize=True)


def souvenir_keys(item: dict) -> dict:
    key = item["key"]
    out = {
        f"{key}Title": item["title"],
        f"{key}Desc": item["desc"],
        f"{key}Body1": item["b1"],
        f"{key}Body2": item["b2"],
        f"{key}Tip": item["tip"],
        f"{key}Body": body_arr(item["b1"], item["b2"], item["tip"]),
    }
    return out


def apply_i18n() -> None:
    per_lang_keys = {}
    for item in ITEMS:
        packed = souvenir_keys(item)
        for field, val in packed.items():
            per_lang_keys[field] = val
    for lang in LANGS:
        path = SHOPPING / f"{lang}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        souvenir = data.setdefault("souvenir", {})
        for field, val in per_lang_keys.items():
            if field.endswith("Body") and not field.endswith("Body1") and not field.endswith("Body2"):
                souvenir[field] = val
            else:
                souvenir[field] = val[lang] if isinstance(val, dict) else val
        _write_text_retry(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        print("i18n", lang, flush=True)


def insert_after(html: str, marker: str, extra: str) -> str:
    idx = html.find(marker)
    if idx < 0:
        raise SystemExit(f"marker not found: {marker[:80]}")
    end = idx + len(marker)
    if extra in html:
        return html
    return html[:end] + extra + html[end:]


def patch_buy() -> None:
    html = BUY.read_text(encoding="utf-8")
    by_tab: dict[str, str] = {}
    for item in ITEMS:
        by_tab.setdefault(item["tab"], "")
        by_tab[item["tab"]] += "\n" + card_html(item["slug"], item["key"])

    markers = {
        "food": '              <a class="souvenir-card" href="../souvenir/osulloc-jeju-green-tea/index.html">',
        "snacks": '              <a class="souvenir-card" href="../souvenir/bbang-bujang/index.html">',
        "daiso": '              <a class="souvenir-card" href="../souvenir/all-the-better-low-sugar-cacao/index.html">',
        "health": '              <a class="souvenir-card" href="../souvenir/korea-eundan-vitamin-c-1000/index.html">',
        "beauty": '              <a class="souvenir-card" href="../souvenir/olive/index.html">',
    }
    # Insert after the full first matching card block: from marker through next </a>
    for tab, start_token in markers.items():
        extra = by_tab.get(tab, "")
        if not extra:
            continue
        start = html.find(start_token)
        if start < 0:
            raise SystemExit(f"tab marker missing: {tab}")
        close = html.find("</a>", start)
        if close < 0:
            raise SystemExit(f"card close missing: {tab}")
        close += len("</a>")
        if extra.strip() and extra.strip() in html:
            continue
        html = html[:close] + extra + html[close:]

    # Move Dr.Reju-All from fashion to beauty (after olive card + new beauty cards)
    old = (
        '              <a class="souvenir-card" href="../souvenir/dr-reju-all/index.html">\n'
        '                <img src="../souvenir/dr-reju-all/media/cover.jpg" alt="" data-i18n-attr="alt:souvenir.drRejuAllTitle">\n'
        '                <div class="souvenir-card-body">\n'
        '                  <h3 data-i18n="souvenir.drRejuAllTitle"></h3>\n'
        '                  <p data-i18n="souvenir.drRejuAllDesc"></p>\n'
        '                  <span class="souvenir-more" data-i18n="souvenir.readMore">자세히 보기 →</span>\n'
        "                </div>\n"
        "              </a>\n"
    )
    if old in html:
        html = html.replace(old, "", 1)
        beauty_token = '              <a class="souvenir-card" href="../souvenir/olive/index.html">'
        start = html.find(beauty_token)
        close = html.find("</a>", start) + len("</a>")
        # after newly inserted beauty cards the olive close is still the first olive </a>
        html = html[:close] + "\n" + old + html[close:]

    _write_text_retry(BUY, html)
    print("patched buy/index.html", flush=True)


def write_pages() -> None:
    for item in ITEMS:
        dest = SOUVENIR / item["slug"] / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(PAGE_TMPL.format(key=item["key"]), encoding="utf-8")
        print("page", dest.relative_to(ROOT), flush=True)


def bump() -> None:
    ver = datetime.now().strftime("%Y%m%d%H%M%S")
    text = (
        "/* Single source of truth for static asset cache-busting.\n"
        " * Bump SITE_ASSET_VERSION via tool/update-version.py (or edit here),\n"
        " * then HTML ?v= is applied automatically by that tool / apply-cache-bust.\n"
        " */\n"
        f'window.SITE_ASSET_VERSION = "{ver}";\n'
    )
    _write_text_retry(VERSION_FILE, text)
    updated = 0
    skipped = []
    for html_path in iter_html_files(ROOT):
        original = html_path.read_text(encoding="utf-8")
        new_text, n = process_html(original, ver)
        if new_text == original:
            continue
        try:
            _write_text_retry(html_path, new_text)
            updated += 1
        except OSError as exc:
            skipped.append((html_path.name, str(exc)))
    print("bump", ver, "updated", updated, "skipped", skipped, flush=True)


def main() -> int:
    jobs = [(it["slug"], it["url"]) for it in ITEMS] + [
        (it["slug"], it["url"]) for it in EXISTING_PHOTO
    ]
    for slug, url in jobs:
        dest = SOUVENIR / slug / "media" / "cover.jpg"
        print("download", slug, flush=True)
        try:
            raw = download(url)
            save_cover(raw, dest)
            print("  saved", dest.relative_to(ROOT), dest.stat().st_size, flush=True)
        except Exception as exc:  # noqa: BLE001
            print("  FAIL", slug, exc, flush=True)
            return 1
    write_pages()
    apply_i18n()
    patch_buy()
    import subprocess

    subprocess.check_call([sys.executable, str(ROOT / "i18n" / "build-bundle.py")], cwd=str(ROOT))
    bump()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
