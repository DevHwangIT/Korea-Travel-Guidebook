# -*- coding: utf-8 -*-
"""Add convenience items + split merged souvenir cards (fashion/beauty/daily)."""
from __future__ import annotations

import io
import json
import re
import shutil
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def write_text_retry(path: Path, text: str, attempts: int = 10) -> None:
    last: Exception | None = None
    for i in range(attempts):
        try:
            path.write_text(text, encoding="utf-8")
            return
        except OSError as e:  # Windows file lock / Errno 22
            last = e
            time.sleep(0.4 + i * 0.3)
    raise last  # type: ignore[misc]
CTX = ssl._create_unverified_context()
UA = "KoreaTravelGuidebook/1.0 (educational; cover fetch)"
COVER = (1536, 1024)
ASSET_V = "20260821181902"
LANGS = ["ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru"]


def http_get(url: str, timeout: int = 90) -> bytes:
    req = urllib.request.Request(
        url, headers={"User-Agent": UA, "Accept": "image/*,*/*"}
    )
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.read()


def save_cover(dest: Path, data: bytes) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(io.BytesIO(data)).convert("RGB")
    tw, th = COVER
    sw, sh = im.size
    tr, sr = tw / th, sw / sh
    if sr > tr:
        nw = int(sh * tr)
        left = (sw - nw) // 2
        im = im.crop((left, 0, left + nw, sh))
    else:
        nh = int(sw / tr)
        top = (sh - nh) // 2
        im = im.crop((0, top, sw, top + nh))
    im = im.resize(COVER, Image.Resampling.LANCZOS)
    im.save(dest, "JPEG", quality=88, optimize=True)


def fetch_or_copy(dest: Path, urls: list[str], fallback: Path | None) -> None:
    if dest.is_file() and dest.stat().st_size > 3000:
        print(f"  keep existing {dest.relative_to(ROOT)}")
        return
    for url in urls:
        for attempt in range(3):
            try:
                print(f"  GET {url[:90]}…")
                data = http_get(url)
                if len(data) < 2000:
                    raise RuntimeError("small")
                save_cover(dest, data)
                print(f"  ok {dest.relative_to(ROOT)}")
                return
            except Exception as e:  # noqa: BLE001
                print(f"  fail {attempt+1}: {e}")
                time.sleep(1.5 + attempt)
    if fallback and fallback.is_file():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(fallback, dest)
        print(f"  copied fallback -> {dest.relative_to(ROOT)}")
    else:
        # solid soft placeholder
        dest.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", COVER, (240, 236, 230)).save(dest, "JPEG", quality=80)
        print(f"  placeholder {dest.relative_to(ROOT)}")


def commons(name: str, width: int = 1600) -> str:
    enc = urllib.parse.quote(name.replace(" ", "_"))
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{enc}?width={width}"


CONV_ARTICLE = """<!DOCTYPE html>
<html lang="ko" data-i18n-title="convenience.{slug}_pageTitle">
<head>
  <!-- asset-v: {ver} -->
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{slug}</title>
  <link rel="stylesheet" href="../../../styles.css?v={ver}">
</head>
<body>
  <nav class="lang-switch" aria-label="Language"></nav>
  <header class="site-header">
    <a href="../../../index.html" class="site-brand" data-i18n="common.brand">Korea Travel Guide</a>
  </header>
  <main class="page article-page">
    <p class="back-link"><a href="../index.html" data-i18n="convenience.backProducts"></a></p>
    <article class="combo-article">
      <img class="combo-article-hero" src="media/cover.jpg" alt="" data-i18n-attr="alt:convenience.{slug}_pageTitle">
      <h1 data-i18n="convenience.{slug}_pageTitle"></h1>
      <p class="article-lead" data-i18n="convenience.{slug}_lead"></p>
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
  <script src="../../../i18n/messages.js?v={ver}"></script>
  <script src="../../../js/i18n.js?v={ver}"></script>
  <script src="../../../js/analytics.js?v={ver}"></script>
</body>
</html>
"""

SOUV_ARTICLE = """<!DOCTYPE html>
<html lang="ko" data-i18n-title="souvenir.{key}Title">
<head>
  <!-- asset-v: {ver} -->
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Souvenir</title>
  <link rel="stylesheet" href="../../../styles.css?v={ver}">
</head>
<body>
  <nav class="lang-switch" aria-label="Language"></nav>
  <header class="site-header">
    <a href="../../../index.html" class="site-brand" data-i18n="common.brand">Korea Travel Guide</a>
  </header>
  <main class="page article-page">
    <p class="back-link"><a href="../../buy/index.html" data-i18n="buyHub.back">← 쇼핑 및 놀거리</a></p>
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
  <script src="../../../i18n/messages.js?v={ver}"></script>
  <script src="../../../js/i18n.js?v={ver}"></script>
  <script src="../../../js/analytics.js?v={ver}"></script>
  <script src="../../../js/content-body.js?v={ver}"></script>
</body>
</html>
"""

CARD = """              <a class="souvenir-card" href="../souvenir/{slug}/index.html">
                <img src="../souvenir/{slug}/media/cover.jpg" alt="" data-i18n-attr="alt:souvenir.{key}Title">
                <div class="souvenir-card-body">
                  <h3 data-i18n="souvenir.{key}Title"></h3>
                  <p data-i18n="souvenir.{key}Desc"></p>
                  <span class="souvenir-more" data-i18n="souvenir.readMore">자세히 보기 →</span>
                </div>
              </a>
"""

CONV_CARD = """      <a class="combo-card" data-brand="{brand}" data-section="product" href="./{slug}/index.html">
        <img src="./{slug}/media/cover.jpg" alt="" data-i18n-attr="alt:convenience.{slug}Title">
        <div class="combo-body">
          <h3 data-i18n="convenience.{slug}Title"></h3>
          <p data-i18n="convenience.{slug}Desc"></p>
          <span class="combo-more" data-i18n="convenience.readMore"></span>
        </div>
      </a>
"""


def slug_to_key(slug: str) -> str:
    parts = slug.split("-")
    return parts[0] + "".join(p.title() for p in parts[1:])


def body_blocks(ko: str, en: str) -> list:
    return [
        {"type": "text", "ko": ko, "en": en, "ja": en, "zh": en, "zh-Hant": en, "vi": en, "th": en, "ru": en}
    ]


# --- Convenience products ---
CONV_ITEMS = [
    {
        "slug": "kim-hyeja-dosirak",
        "brand": "gs",
        "cover_urls": [
            commons("Dosirak.jpg"),
            commons("Korean_lunch_box.jpg"),
            "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Bento_box.jpg/1280px-Bento_box.jpg",
        ],
        "ko": {
            "Title": "김혜자 도시락",
            "Desc": "GS25 대표 도시락 — 김혜자 브랜드",
            "_pageTitle": "GS25 김혜자 도시락",
            "_lead": "김혜자 도시락은 GS25에서 파는 대표 편의점 도시락 브랜드입니다. 밥·반찬 구성이 든든해 한 끼 식사로 많이 고릅니다.",
            "_tipTitle": "팁",
            "_tip": "GS25 매장에서 찾을 수 있습니다. 전자레인지로 데워 드시고, 유통기한을 확인하세요.",
        },
        "en": {
            "Title": "Kim Hye-ja Dosirak",
            "Desc": "GS25 signature lunch box — Kim Hye-ja brand",
            "_pageTitle": "GS25 Kim Hye-ja Dosirak",
            "_lead": "Kim Hye-ja Dosirak is a well-known GS25 convenience-store lunch-box line — rice and side dishes for a quick full meal.",
            "_tipTitle": "Tip",
            "_tip": "Sold at GS25. Microwave before eating and check the date.",
        },
        "ja": {
            "Title": "キム・ヘジャ弁当",
            "Desc": "GS25の代表弁当ブランド",
            "_pageTitle": "GS25 キム・ヘジャ弁当",
            "_lead": "キム・ヘジャ弁当はGS25で売られる人気のコンビニ弁当ブランドです。ご飯とおかずでしっかり一食になります。",
            "_tipTitle": "ヒント",
            "_tip": "GS25で購入。レンジで温めて、賞味期限を確認してください。",
        },
    },
    {
        "slug": "cheese-bokki-ramen",
        "brand": "common",
        "cover_urls": [
            commons("Ramyeon.jpg"),
            commons("Instant_noodles.jpg"),
            "https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Shin_Ramyun.jpg/1280px-Shin_Ramyun.jpg",
        ],
        "ko": {
            "Title": "치즈볶이 라면",
            "Desc": "치즈맛 떡볶이 풍 컵라면 — 편의점 인기",
            "_pageTitle": "치즈볶이 라면",
            "_lead": "치즈볶이 라면은 떡볶이 양념에 치즈 풍미를 더한 편의점 인기 컵라면입니다. 매콤달콤한 맛으로 한 끼·야식으로 많이 찾습니다.",
            "_tipTitle": "팁",
            "_tip": "컵라면 코너에서 ‘치즈볶이’ 표기를 확인하세요. 취향에 따라 물을 조금 적게 잡고 저어 드세요.",
        },
        "en": {
            "Title": "Cheese Bokki Ramen",
            "Desc": "Cheesy tteokbokki-style cup ramen",
            "_pageTitle": "Cheese Bokki Ramen",
            "_lead": "Cheese Bokki ramen is a popular convenience-store cup noodle with cheesy tteokbokki-style seasoning — sweet-spicy and filling.",
            "_tipTitle": "Tip",
            "_tip": "Look for “치즈볶이 / Cheese Bokki” on the cup. Use a little less water if you like it thicker.",
        },
        "ja": {
            "Title": "チーズトッポギラーメン",
            "Desc": "チーズ風味のトッポギ系カップ麺",
            "_pageTitle": "チーズトッポギラーメン",
            "_lead": "チーズトッポギ風味の人気カップ麺。甘辛くてご飯代わりにもなります。",
            "_tipTitle": "ヒント",
            "_tip": "カップ麺コーナーで「チーズ볶이」表記を確認。濃いめが好きならお湯を少し控えめに。",
        },
    },
]

# --- Souvenir splits ---
# Each: slug, key (camel), panel, covers, rewrite_existing?, i18n per lang subset
SOUV_NEW = [
    # Fashion
    {
        "slug": "uniqlo",
        "key": "uniqlo",
        "panel": "fashion",
        "reuse": True,
        "covers": [commons("Uniqlo_logo.svg"), commons("Uniqlo.jpg")],
        "fallback": ROOT / "pages/souvenir/uniqlo/media/cover.jpg",
        "ko": {
            "Title": "유니클로",
            "Desc": "한국 매장 한정 컬러·캐릭터 콜라보 티셔츠",
            "Body1": "유니클로 한국 매장에는 한정 컬러·그래픽·캐릭터 콜라보가 따로 나오는 경우가 많습니다. 여행 기념 티셔츠로 많이 고릅니다.",
            "Body2": "시즌 세일 때 가격 경쟁력이 좋고, 택스프리도 비교적 익숙합니다. 피팅룸에서 cm 사이즈를 확인하세요.",
            "Tip": "명동·타임스퀘어·코엑스 대형 매장 재고가 넉넉합니다.",
        },
        "en": {
            "Title": "Uniqlo",
            "Desc": "Korea-only colors and character collab tees",
            "Body1": "Korean Uniqlo stores often carry exclusive colors, graphics, and character collabs that travelers buy as souvenirs.",
            "Body2": "Sales are competitive and tax-free procedures are familiar. Check cm sizes in the fitting room.",
            "Tip": "Large stores in Myeongdong, Times Square, and COEX usually have better stock.",
        },
    },
    {
        "slug": "spa",
        "key": "spa",
        "panel": "fashion",
        "reuse": True,
        "covers": [],
        "fallback": ROOT / "pages/souvenir/spa/media/cover.jpg",
        "ko": {
            "Title": "스파오",
            "Desc": "캐릭터 콜라보·가성비 SPA 패션",
            "Body1": "스파오(SPAO)는 티셔츠·잠옷·캐릭터 콜라보로 유명한 한국 SPA 브랜드입니다. 시즌마다 애니·캐릭터 라인업이 나옵니다.",
            "Body2": "사이즈는 한국 기준으로 타이트할 수 있어 한 치수 여유를 두고, 영수증을 보관하세요.",
            "Tip": "명동·홍대·강남 로드샵을 비교하고 세일 시즌을 노리면 좋습니다.",
        },
        "en": {
            "Title": "SPAO",
            "Desc": "Character collabs and affordable SPA fashion",
            "Body1": "SPAO is a Korean SPA brand known for tees, sleepwear, and character collaborations that change by season.",
            "Body2": "Korean sizes can run small — size up if unsure, and keep the receipt.",
            "Tip": "Compare Myeongdong, Hongdae, and Gangnam street shops; hunt sales.",
        },
    },
    {
        "slug": "eight-seconds",
        "key": "eightSeconds",
        "panel": "fashion",
        "reuse": False,
        "covers": [
            commons("Fashion.jpg"),
            "https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=1600&q=80",
        ],
        "fallback": ROOT / "pages/souvenir/spa/media/cover.jpg",
        "ko": {
            "Title": "에잇세컨즈",
            "Desc": "트렌디한 한국 SPA — 티·아우터·액세서리",
            "Body1": "에잇세컨즈(8Seconds)는 시즌 트렌드를 빠르게 반영하는 한국 SPA입니다. 티셔츠·아우터·가방 등 여행 중 입기 좋은 아이템이 많습니다.",
            "Body2": "명동·대형 쇼핑몰 매장이 찾기 쉽고, 세일 코너를 먼저 보면 실패가 적습니다.",
            "Tip": "사이즈는 cm 표기를 기준으로 고르세요.",
        },
        "en": {
            "Title": "8Seconds",
            "Desc": "Trendy Korean SPA — tees, outerwear, accessories",
            "Body1": "8Seconds is a Korean SPA brand that quickly reflects seasonal trends — good for tees, light outerwear, and accessories.",
            "Body2": "Myeongdong and mall stores are easy to find; start with the sale racks.",
            "Tip": "Use the cm size labels as your guide.",
        },
    },
    {
        "slug": "basic",
        "key": "basic",
        "panel": "fashion",
        "reuse": False,
        "covers": [
            "https://images.unsplash.com/photo-1489987707025-afc232f7ea62?auto=format&fit=crop&w=1600&q=80",
        ],
        "fallback": ROOT / "pages/souvenir/spa/media/cover.jpg",
        "ko": {
            "Title": "베이직",
            "Desc": "심플·데일리 가성비 패션",
            "Body1": "베이직은 심플한 티·니트·데일리웨어 위주의 가성비 패션으로, 여행 중 ‘입을 옷’을 보충할 때 자주 고릅니다.",
            "Body2": "화려한 기념품보다 실용 아이템을 원할 때 어울립니다. 매장·온라인 구성은 시즌마다 달라집니다.",
            "Tip": "기본 컬러 티·양말 세트가 캐리어에 넣기 좋습니다.",
        },
        "en": {
            "Title": "Basic",
            "Desc": "Simple, affordable everyday fashion",
            "Body1": "Basic focuses on simple tees, knits, and daily wear — handy when you need practical clothes while traveling.",
            "Body2": "Better for useful pieces than flashy souvenirs. Assortments change by season.",
            "Tip": "Basics and sock packs pack easily in a suitcase.",
        },
    },
    {
        "slug": "shoopen",
        "key": "shoopen",
        "panel": "fashion",
        "reuse": False,
        "covers": [
            "https://images.unsplash.com/photo-1586350977771-b3b0abd50cbe?auto=format&fit=crop&w=1600&q=80",
        ],
        "fallback": ROOT / "pages/souvenir/socks/media/cover.jpg",
        "ko": {
            "Title": "슈펜",
            "Desc": "양말·신발·액세서리 가성비 브랜드",
            "Body1": "슈펜(Shoopen)은 양말·스타킹·슬리퍼·간단한 슈즈를 저렴하게 살 수 있는 브랜드입니다. 여행용 여분 양말로 인기입니다.",
            "Body2": "3·5족 묶음이 낱개보다 낫고, 한국 사이즈(230–280)를 확인하세요.",
            "Tip": "출국 초반에 여분을 사 두면 편리합니다.",
        },
        "en": {
            "Title": "Shoopen",
            "Desc": "Affordable socks, shoes, and accessories",
            "Body1": "Shoopen is a budget brand for socks, tights, slippers, and simple shoes — popular for spare travel socks.",
            "Body2": "Multi-packs beat singles; check Korean sizes (230–280).",
            "Tip": "Buy a spare pack early in the trip.",
        },
    },
    {
        "slug": "socks",
        "key": "socks",
        "panel": "fashion",
        "reuse": True,
        "covers": [],
        "fallback": ROOT / "pages/souvenir/socks/media/cover.jpg",
        "ko": {
            "Title": "양말·스타킹 세트",
            "Desc": "다이소·스파오 등 묶음 양말",
            "Body1": "다이소·스파오·유니클로 등에서 파는 3·5족 양말·스타킹 묶음은 가성비가 좋고 선물용으로도 무난합니다.",
            "Body2": "개별 포장 세트가 위생적이고 캐리어 틈에 잘 들어갑니다.",
            "Tip": "묶음팩이 낱개보다 저렴한 경우가 많습니다.",
        },
        "en": {
            "Title": "Sock & tights packs",
            "Desc": "Multi-packs from Daiso, SPAO, and more",
            "Body1": "3–5 pair sock and tights packs from Daiso, SPAO, Uniqlo, and similar stores are good value and easy gifts.",
            "Body2": "Individually wrapped packs travel well in suitcase gaps.",
            "Tip": "Multi-packs are usually cheaper than singles.",
        },
    },
    # Beauty
    {
        "slug": "round-lab",
        "key": "roundLab",
        "panel": "beauty",
        "reuse": False,
        "covers": [
            "https://images.unsplash.com/photo-1556228578-0d85b1a4d571?auto=format&fit=crop&w=1600&q=80",
        ],
        "fallback": ROOT / "pages/souvenir/olive/media/cover.jpg",
        "ko": {
            "Title": "라운드랩",
            "Desc": "독도 토너·자작나무 선크림 등 올영 베스트",
            "Body1": "라운드랩은 독도 토너·크림, 자작나무 수분 선크림 등으로 올리브영 외국인 장바구니에 자주 들어갑니다.",
            "Body2": "저자극·수분 라인을 찾는 여행객에게 추천됩니다. ‘올영픽’ 진열을 먼저 보세요.",
            "Tip": "명동·홍대·강남 대형점이 재고가 많습니다.",
        },
        "en": {
            "Title": "Round Lab",
            "Desc": "Dokdo toner, birch sunscreen — Olive Young favorites",
            "Body1": "Round Lab’s Dokdo toner/cream and birch moisture sunscreen are frequent Olive Young picks for visitors.",
            "Body2": "Good for gentle, hydrating routines. Start with Olive Young Picks shelves.",
            "Tip": "Large stores in Myeongdong, Hongdae, and Gangnam stock more.",
        },
    },
    {
        "slug": "anua",
        "key": "anua",
        "panel": "beauty",
        "reuse": False,
        "covers": [
            "https://images.unsplash.com/photo-1571875257727-256c39da42af?auto=format&fit=crop&w=1600&q=80",
        ],
        "fallback": ROOT / "pages/souvenir/olive/media/cover.jpg",
        "ko": {
            "Title": "아누아",
            "Desc": "어성초 77 토너·세럼",
            "Body1": "아누아 어성초 77 토너·세럼은 올리브영에서 가장 잘 팔리는 진정 케어 중 하나입니다.",
            "Body2": "민감·트러블 케어를 찾는 여행객 선물로도 인기입니다. 택스프리 매장인지 계산 전 확인하세요.",
            "Tip": "앱 쿠폰·증정 조합을 직원에게 물어보세요.",
        },
        "en": {
            "Title": "Anua",
            "Desc": "Heartleaf 77 toner and serum",
            "Body1": "Anua Heartleaf 77 toner and serum are among Olive Young’s best-selling calming skincare lines.",
            "Body2": "Popular gifts for sensitive or troubled skin. Ask about tax-free before checkout.",
            "Tip": "Ask staff about app coupons and gift-with-purchase.",
        },
    },
    {
        "slug": "mediheal",
        "key": "mediheal",
        "panel": "beauty",
        "reuse": False,
        "covers": [
            "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?auto=format&fit=crop&w=1600&q=80",
        ],
        "fallback": ROOT / "pages/souvenir/sheet/media/cover.jpg",
        "ko": {
            "Title": "메디힐",
            "Desc": "N.M.F 아쿠아링 등 시트마스크",
            "Body1": "메디힐은 N.M.F 아쿠아링 등 시트마스크로 유명한 브랜드입니다. 박스 세트(10매)가 선물용으로 보기 좋습니다.",
            "Body2": "올리브영·면세에서 구성이 명확한 세트를 고르세요. 유통기한·영문 표기가 있는 수출용도 있습니다.",
            "Tip": "민감 피부는 저자극·센텔라 표기를 확인하세요.",
        },
        "en": {
            "Title": "Mediheal",
            "Desc": "N.M.F Aquaring and other sheet masks",
            "Body1": "Mediheal is known for sheet masks like N.M.F Aquaring. 10-pack boxes make tidy gifts.",
            "Body2": "Olive Young and duty-free have clear set options; check expiry and English labeling.",
            "Tip": "Sensitive skin: look for gentle / centella labels.",
        },
    },
    {
        "slug": "numbuzin",
        "key": "numbuzin",
        "panel": "beauty",
        "reuse": False,
        "covers": [
            "https://images.unsplash.com/photo-1620916565916-6a1c5a0f5f5f?auto=format&fit=crop&w=1600&q=80",
            "https://images.unsplash.com/photo-1612817288484-6f916006741a?auto=format&fit=crop&w=1600&q=80",
        ],
        "fallback": ROOT / "pages/souvenir/sheet/media/cover.jpg",
        "ko": {
            "Title": "넘버즈인",
            "Desc": "1·3·5번 등 번호별 스킨케어·마스크",
            "Body1": "넘버즈인(numbuzin)은 번호별 라인(1·3·5번 등)으로 유명한 스킨케어·마스크 브랜드입니다.",
            "Body2": "올리브영에서 피부 고민별 추천을 받기 쉽고, 미니·본품 조합 선물이 많습니다.",
            "Tip": "본인 피부 타입을 직원에게 말하고 골라 보세요.",
        },
        "en": {
            "Title": "numbuzin",
            "Desc": "Numbered skincare and masks (No.1 / 3 / 5…)",
            "Body1": "numbuzin is known for numbered lines (No.1, 3, 5, etc.) of skincare and masks.",
            "Body2": "Easy to get skin-concern advice at Olive Young; mini + full-size gift sets are common.",
            "Tip": "Tell staff your skin type before choosing.",
        },
    },
    {
        "slug": "tirtir",
        "key": "tirtir",
        "panel": "beauty",
        "reuse": False,
        "covers": [
            "https://images.unsplash.com/photo-1522335789203-aabd92dbc271?auto=format&fit=crop&w=1600&q=80",
        ],
        "fallback": ROOT / "pages/souvenir/sheet/media/cover.jpg",
        "ko": {
            "Title": "티르티르",
            "Desc": "마스크·쿠션 미니 등",
            "Body1": "티르티르(TIRTIR)는 마스크팩과 쿠션 미니로 여행·선물용으로 자주 추천됩니다.",
            "Body2": "면세·올리브영 세트가 구성이 분명하고, 색조는 매장 테스터로 확인하세요.",
            "Tip": "쿠션은 호수·커버력을 테스터로 맞추세요.",
        },
        "en": {
            "Title": "TIRTIR",
            "Desc": "Masks and mini cushions",
            "Body1": "TIRTIR masks and mini cushions are popular travel and gift picks.",
            "Body2": "Duty-free and Olive Young sets are clear; shade-match makeup with testers.",
            "Tip": "Test cushion shade and coverage in store.",
        },
    },
    {
        "slug": "tocobo",
        "key": "tocobo",
        "panel": "beauty",
        "reuse": False,
        "covers": [
            "https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=1600&q=80",
        ],
        "fallback": ROOT / "pages/souvenir/sunscreen/media/cover.jpg",
        "ko": {
            "Title": "토코보",
            "Desc": "코튼소프트 선크림·선스틱",
            "Body1": "토코보(Tocobo)는 코튼소프트 선크림·선스틱 등 백탁 적은 선케어로 인기입니다.",
            "Body2": "항공 액체 제한 때문에 스틱·50ml 이하를 고르면 기내 반입이 수월합니다.",
            "Tip": "올리브영 선케어 ‘올영픽’을 먼저 보세요.",
        },
        "en": {
            "Title": "Tocobo",
            "Desc": "Cotton Soft sunscreen and sun sticks",
            "Body1": "Tocobo’s Cotton Soft sunscreen and sun sticks are popular low-white-cast options.",
            "Body2": "Sticks and ≤50ml sizes are easier for cabin liquids limits.",
            "Tip": "Start with Olive Young sunscreen picks.",
        },
    },
    {
        "slug": "green-finger",
        "key": "greenFinger",
        "panel": "beauty",
        "reuse": False,
        "covers": [
            "https://images.unsplash.com/photo-1556229010-6c3f2c9ca5f8?auto=format&fit=crop&w=1600&q=80",
            "https://images.unsplash.com/photo-1608248543807-ac7c7c6e3c0f?auto=format&fit=crop&w=1600&q=80",
        ],
        "fallback": ROOT / "pages/souvenir/sunscreen/media/cover.jpg",
        "ko": {
            "Title": "그린핑거",
            "Desc": "키즈·패밀리 선케어",
            "Body1": "그린핑거는 키즈·패밀리용 선크림으로 잘 알려진 브랜드입니다. 아이와 함께 여행할 때 자주 고릅니다.",
            "Body2": "얼굴·바디용을 나누고, 무기자차/유기자차 표기를 확인하세요.",
            "Tip": "약국·올리브영·대형마트에서 쉽게 찾을 수 있습니다.",
        },
        "en": {
            "Title": "Green Finger",
            "Desc": "Kids and family sun care",
            "Body1": "Green Finger is known for kids/family sunscreens — handy for trips with children.",
            "Body2": "Separate face/body products and check mineral vs chemical filters.",
            "Tip": "Easy to find at pharmacies, Olive Young, and hypermarkets.",
        },
    },
    {
        "slug": "romand",
        "key": "romand",
        "panel": "beauty",
        "reuse": False,
        "covers": [
            "https://images.unsplash.com/photo-1586495777744-4413f21062fa?auto=format&fit=crop&w=1600&q=80",
        ],
        "fallback": ROOT / "pages/souvenir/lipstick/media/cover.jpg",
        "ko": {
            "Title": "롬앤",
            "Desc": "쥬시 라스팅 틴트·글래스팅 글로스",
            "Body1": "롬앤(rom&nd) 쥬시 라스팅 틴트·글래스팅 글로스는 올리브영 고정 베스트 립입니다.",
            "Body2": "색번호는 매장 테스터로 확인하세요. 단품+미니 조합이 세트보다 나을 때도 있습니다.",
            "Tip": "피부톤(웜/뮤트)을 직원에게 말해 보세요.",
        },
        "en": {
            "Title": "rom&nd",
            "Desc": "Juicy Lasting Tint and Glasting Gloss",
            "Body1": "rom&nd Juicy Lasting Tint and Glasting Gloss are Olive Young lipstick staples.",
            "Body2": "Shade-match with testers; singles + minis can beat gift sets.",
            "Tip": "Tell staff if you prefer warm or muted tones.",
        },
    },
    {
        "slug": "peripera",
        "key": "peripera",
        "panel": "beauty",
        "reuse": False,
        "covers": [
            "https://images.unsplash.com/photo-1631214524020-7e18db9a8f92?auto=format&fit=crop&w=1600&q=80",
        ],
        "fallback": ROOT / "pages/souvenir/lipstick/media/cover.jpg",
        "ko": {
            "Title": "페리페라",
            "Desc": "잉크 벨벳 등 틴트",
            "Body1": "페리페라 잉크 벨벳 등 틴트는 가성비 좋은 한국 메이크업으로 선물·기념품으로 많이 삽니다.",
            "Body2": "발색이 진한 편이니 테스터로 확인하고, 위생에 주의하세요.",
            "Tip": "올리브영 메이크업 코너에서 호수를 비교하세요.",
        },
        "en": {
            "Title": "Peripera",
            "Desc": "Ink Velvet and other tints",
            "Body1": "Peripera Ink Velvet tints are affordable Korean makeup favorites for gifts and souvenirs.",
            "Body2": "Pigment can be strong — test shades and mind tester hygiene.",
            "Tip": "Compare shade numbers in the Olive Young makeup aisle.",
        },
    },
    {
        "slug": "clio",
        "key": "clio",
        "panel": "beauty",
        "reuse": False,
        "covers": [
            "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?auto=format&fit=crop&w=1600&q=80",
        ],
        "fallback": ROOT / "pages/souvenir/lipstick/media/cover.jpg",
        "ko": {
            "Title": "클리오",
            "Desc": "킬커버 파운데이션·쿠션",
            "Body1": "클리오 킬커버는 커버력 좋은 파운데이션·쿠션으로 올리브영에서 자주 추천됩니다.",
            "Body2": "호수·피부타입 상담을 받고, 미니 쿠션은 여행용으로 좋습니다.",
            "Tip": "면세 한정 세트보다 시중 단품이 나을 수 있습니다.",
        },
        "en": {
            "Title": "CLIO",
            "Desc": "Kill Cover foundation and cushions",
            "Body1": "CLIO Kill Cover foundations and cushions are Olive Young staples for fuller coverage.",
            "Body2": "Ask for shade matching; mini cushions are great for travel.",
            "Tip": "Regular singles can beat duty-free sets on value.",
        },
    },
    # Daily
    {
        "slug": "jaksim-mask",
        "key": "jaksimMask",
        "panel": "daily",
        "reuse": False,
        "covers": [
            "https://images.unsplash.com/photo-1584017911766-d451b3d0e843?auto=format&fit=crop&w=1600&q=80",
        ],
        "fallback": ROOT / "pages/souvenir/mask/media/cover.jpg",
        "ko": {
            "Title": "작심 KF94 마스크",
            "Desc": "약국·편의점에서 사는 대표 KF94",
            "Body1": "작심(Jaksim) KF94는 외국인이 기념·실사용으로 많이 사는 마스크입니다. 소량 팩이 캐리어에 넣기 좋습니다.",
            "Body2": "편의점·다이소·올리브영·약국에 있습니다. ‘KF94’ 표기와 포장 날짜를 확인하세요.",
            "Tip": "대량은 시중 약국 묶음이 무난한 경우가 많습니다.",
        },
        "en": {
            "Title": "Jaksim KF94 masks",
            "Desc": "A common KF94 sold at pharmacies and convenience stores",
            "Body1": "Jaksim KF94 masks are popular for both souvenirs and daily use. Small packs pack well.",
            "Body2": "Find them at convenience stores, Daiso, Olive Young, and pharmacies. Check KF94 labeling and pack date.",
            "Tip": "For bulk, local pharmacy multipacks are often fine.",
        },
    },
    {
        "slug": "bluedot-mask",
        "key": "bluedotMask",
        "panel": "daily",
        "reuse": False,
        "covers": [],
        "fallback": ROOT / "pages/souvenir/mask/media/cover.jpg",
        "ko": {
            "Title": "블루닷 마스크",
            "Desc": "KF94/KF80 — 편의점·약국 스테디",
            "Body1": "블루닷(Bluedot) 마스크는 편의점·약국에서 쉽게 보이는 KF94/KF80 라인입니다.",
            "Body2": "황사·미세먼지 시즌에 재고가 빨리 줄어들 수 있어 동네 약국을 함께 보세요.",
            "Tip": "5~10매 소량 팩이 여행용으로 적당합니다.",
        },
        "en": {
            "Title": "Bluedot masks",
            "Desc": "KF94/KF80 — convenience-store and pharmacy staple",
            "Body1": "Bluedot masks are easy-to-find KF94/KF80 options at convenience stores and pharmacies.",
            "Body2": "Stock can run low in dust season — try neighborhood pharmacies too.",
            "Tip": "5–10 pack sizes are ideal for travel.",
        },
    },
    {
        "slug": "aer-mask",
        "key": "aerMask",
        "panel": "daily",
        "reuse": False,
        "covers": [],
        "fallback": ROOT / "pages/souvenir/mask/media/cover.jpg",
        "ko": {
            "Title": "아에르 마스크",
            "Desc": "KF94 — 약국·올리브영에서",
            "Body1": "아에르(Aer) KF94는 약국·올리브영에서 자주 보이는 마스크 브랜드입니다.",
            "Body2": "착용감·사이즈(S/M/L)를 확인하고, 귀국용 대량은 무게를 계산하세요.",
            "Tip": "포장에 KF 등급과 제조일을 확인하세요.",
        },
        "en": {
            "Title": "Aer masks",
            "Desc": "KF94 — pharmacies and Olive Young",
            "Body1": "Aer KF94 masks are commonly stocked at pharmacies and Olive Young.",
            "Body2": "Check fit sizes (S/M/L) and suitcase weight for bulk buys.",
            "Tip": "Confirm KF grade and manufacture date on the pack.",
        },
    },
    {
        "slug": "monami",
        "key": "monami",
        "panel": "daily",
        "reuse": False,
        "covers": [
            commons("Ballpoint_pen.jpg"),
            "https://images.unsplash.com/photo-1455390582262-044cdead277a?auto=format&fit=crop&w=1600&q=80",
        ],
        "fallback": ROOT / "pages/souvenir/stationery/media/cover.jpg",
        "ko": {
            "Title": "모나미",
            "Desc": "153 볼펜 등 한국 문구 아이콘",
            "Body1": "모나미 153 볼펜 세트는 한국 문구 기념품의 대표입니다. 다이소·문구점·아트박스에서 세트를 고르기 쉽습니다.",
            "Body2": "선물용 케이스 세트, 본인용 리필·단품으로 나누어 사면 합리적입니다.",
            "Tip": "색상 세트·리미티드 패키지를 찾아보세요.",
        },
        "en": {
            "Title": "Monami",
            "Desc": "153 ballpoint — a Korean stationery icon",
            "Body1": "Monami 153 pen sets are classic Korean stationery souvenirs. Easy to find at Daiso, stationery shops, and Artbox.",
            "Body2": "Gift case sets for others; refills/singles for yourself.",
            "Tip": "Look for color sets and limited packages.",
        },
    },
    {
        "slug": "iconic",
        "key": "iconic",
        "panel": "daily",
        "reuse": False,
        "covers": [
            "https://images.unsplash.com/photo-1517842645767-c639042777db?auto=format&fit=crop&w=1600&q=80",
        ],
        "fallback": ROOT / "pages/souvenir/stationery/media/cover.jpg",
        "ko": {
            "Title": "아이코닉",
            "Desc": "다이어리·스티커·플래너",
            "Body1": "아이코닉은 다이어리·스티커·플래너로 인기인 문구 브랜드입니다. 가벼운 기념품으로 좋습니다.",
            "Body2": "아트박스·아이코닉 매장·일부 올리브영·백화점 문구 코너에서 찾을 수 있습니다.",
            "Tip": "스티커·메모는 항공 무게 부담이 적습니다.",
        },
        "en": {
            "Title": "Iconic",
            "Desc": "Diaries, stickers, and planners",
            "Body1": "Iconic is popular for diaries, stickers, and planners — light souvenir stationery.",
            "Body2": "Find it at Artbox, Iconic shops, and some Olive Young/department stationery corners.",
            "Tip": "Stickers and memo pads barely add luggage weight.",
        },
    },
    {
        "slug": "kakao-friends-stationery",
        "key": "kakaoFriendsStationery",
        "panel": "daily",
        "reuse": False,
        "covers": [
            "https://images.unsplash.com/photo-1452860606245-08befc0ff44b?auto=format&fit=crop&w=1600&q=80",
        ],
        "fallback": ROOT / "pages/souvenir/stationery/media/cover.jpg",
        "ko": {
            "Title": "카카오프렌즈 문구",
            "Desc": "메모지·마스킹테이프·캐릭터 문구",
            "Body1": "카카오프렌즈 메모·마스킹테이프·볼펜은 가벼운 캐릭터 기념품으로 인기입니다.",
            "Body2": "플래그십·아트박스·다이소·편의점 캐릭터 코너에서도 소품을 찾을 수 있습니다.",
            "Tip": "한정 콜라보는 플래그십이 재고가 나은 편입니다.",
        },
        "en": {
            "Title": "Kakao Friends stationery",
            "Desc": "Memo pads, washi tape, character pens",
            "Body1": "Kakao Friends memo pads, washi tape, and pens are popular light character souvenirs.",
            "Body2": "Also find small goods at flagships, Artbox, Daiso, and convenience-store character corners.",
            "Tip": "Limited collabs are easier at flagship stores.",
        },
    },
]


def fill_lang(base_ko: dict, base_en: dict, lang: str) -> dict:
    if lang == "ko":
        return dict(base_ko)
    if lang == "ja" and "ja" in base_en:  # unused
        return dict(base_en)
    # default: EN for other langs (site often falls back / translate later)
    src = base_en
    return dict(src)


def write_souv_i18n(item: dict) -> None:
    key = item["key"]
    for lang in LANGS:
        path = ROOT / "i18n" / "pages" / "shopping" / f"{lang}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        souv = data.setdefault("souvenir", {})
        if lang == "ko":
            t = item["ko"]
        elif lang == "ja" and "ja" in item:
            t = item["ja"]
        else:
            t = item.get("en", item["ko"])
        souv[f"{key}Title"] = t["Title"]
        souv[f"{key}Desc"] = t["Desc"]
        souv[f"{key}Body1"] = t["Body1"]
        souv[f"{key}Body2"] = t["Body2"]
        souv[f"{key}Tip"] = t["Tip"]
        souv[f"{key}Body"] = body_blocks(item["ko"]["Body1"], item["en"]["Body1"]) + body_blocks(
            item["ko"]["Body2"], item["en"]["Body2"]
        )
        write_text_retry(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def write_conv_i18n(item: dict) -> None:
    slug = item["slug"]
    for lang in LANGS:
        path = ROOT / "i18n" / "pages" / "convenience" / f"{lang}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        conv = data.setdefault("convenience", {})
        if lang == "ko":
            t = item["ko"]
        elif lang == "ja":
            t = item["ja"]
        else:
            t = item["en"]
        for k, v in t.items():
            if k.startswith("_"):
                conv[f"{slug}{k}"] = v
            else:
                conv[f"{slug}{k}"] = v
        write_text_retry(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def ensure_conv_pages() -> None:
    hub = ROOT / "pages" / "convenience-store" / "index.html"
    brands_path = ROOT / "data" / "convenience" / "product-brands.json"
    brands = json.loads(brands_path.read_text(encoding="utf-8"))

    for item in CONV_ITEMS:
        slug = item["slug"]
        page_dir = ROOT / "pages" / "convenience-store" / slug
        page_dir.mkdir(parents=True, exist_ok=True)
        write_text_retry(page_dir / "index.html", CONV_ARTICLE.format(slug=slug, ver=ASSET_V))
        fetch_or_copy(
            page_dir / "media" / "cover.jpg",
            item["cover_urls"],
            ROOT / "pages/convenience-store/store-kimbap/media/cover.jpg",
        )
        brands[slug] = item["brand"]
        write_conv_i18n(item)

    html = hub.read_text(encoding="utf-8")
    for item in CONV_ITEMS:
        slug = item["slug"]
        card = CONV_CARD.format(slug=slug, brand=item["brand"])
        if f'href="./{slug}/index.html"' in html:
            continue
        needle = 'href="./chalddeok-ice/index.html"'
        idx = html.find(needle)
        if idx == -1:
            raise SystemExit("chalddeok card not found")
        end = html.find("</a>", idx) + len("</a>")
        html = html[:end] + "\n" + card + html[end:]

    write_text_retry(hub, html)
    write_text_retry(brands_path, json.dumps(brands, ensure_ascii=False, indent=2) + "\n")
    print("convenience hub + brands updated")


def replace_panel_cards(panel: str, slugs_keys: list[tuple[str, str]]) -> None:
    buy = ROOT / "pages" / "buy" / "index.html"
    html = buy.read_text(encoding="utf-8")
    pat = re.compile(
        rf'(<div class="tab-panel" role="tabpanel" data-buy-panel="{panel}"[^>]*>\s*<div class="souvenir-grid">)(.*?)(</div>\s*</div>)',
        re.S,
    )
    m = pat.search(html)
    if not m:
        raise SystemExit(f"panel {panel} not found")
    keep = ""
    if panel == "fashion":
        for keep_slug, keep_key in [
            ("hanbok", "hanbok"),
            ("dr-reju-all", "drRejuAll"),
            ("korean-traditional-accessories", "koreanTraditionalAccessories"),
        ]:
            keep += CARD.format(slug=keep_slug, key=keep_key)
    if panel == "daily":
        keep += CARD.format(slug="kpop", key="kpop")

    cards = "".join(CARD.format(slug=s, key=k) for s, k in slugs_keys) + keep
    html = pat.sub(m.group(1) + "\n" + cards + "\n            " + m.group(3), html, count=1)
    write_text_retry(buy, html)
    print(f"buy panel {panel} updated ({len(slugs_keys)} + keep)")


def ensure_souv_pages() -> None:
    for item in SOUV_NEW:
        slug, key = item["slug"], item["key"]
        page_dir = ROOT / "pages" / "souvenir" / slug
        page_dir.mkdir(parents=True, exist_ok=True)
        write_text_retry(page_dir / "index.html", SOUV_ARTICLE.format(key=key, ver=ASSET_V))
        fetch_or_copy(
            page_dir / "media" / "cover.jpg",
            item.get("covers") or [],
            item.get("fallback"),
        )
        write_souv_i18n(item)
        print(f"souvenir {slug} ok")

    redirects = {
        "olive": "round-lab",
        "sheet": "mediheal",
        "sunscreen": "round-lab",
        "lipstick": "romand",
        "mask": "jaksim-mask",
        "stationery": "monami",
    }
    for old, new in redirects.items():
        p = ROOT / "pages" / "souvenir" / old / "index.html"
        if not p.parent.is_dir():
            continue
        write_text_retry(
            p,
            f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0;url=../{new}/index.html">
  <link rel="canonical" href="../{new}/index.html">
  <script>location.replace("../{new}/index.html");</script>
  <title>Redirect</title>
</head>
<body>
  <p><a href="../{new}/index.html">Continue</a></p>
</body>
</html>
""",
        )
        print(f"redirect {old} -> {new}")


def main() -> None:
    ensure_conv_pages()
    ensure_souv_pages()
    replace_panel_cards(
        "fashion",
        [
            ("uniqlo", "uniqlo"),
            ("spa", "spa"),
            ("eight-seconds", "eightSeconds"),
            ("basic", "basic"),
            ("shoopen", "shoopen"),
            ("socks", "socks"),
        ],
    )
    replace_panel_cards(
        "beauty",
        [
            ("round-lab", "roundLab"),
            ("anua", "anua"),
            ("mediheal", "mediheal"),
            ("numbuzin", "numbuzin"),
            ("tirtir", "tirtir"),
            ("tocobo", "tocobo"),
            ("green-finger", "greenFinger"),
            ("romand", "romand"),
            ("peripera", "peripera"),
            ("clio", "clio"),
        ],
    )
    replace_panel_cards(
        "daily",
        [
            ("jaksim-mask", "jaksimMask"),
            ("bluedot-mask", "bluedotMask"),
            ("aer-mask", "aerMask"),
            ("monami", "monami"),
            ("iconic", "iconic"),
            ("kakao-friends-stationery", "kakaoFriendsStationery"),
        ],
    )

    import sys

    sys.path.insert(0, str(ROOT / "tool"))
    from lib.i18n_store import build_bundle, load_lang, save_lang

    for lang in LANGS:
        save_lang(lang, load_lang(lang))
    print(build_bundle())
    print("DONE")


if __name__ == "__main__":
    main()
