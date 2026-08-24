# -*- coding: utf-8 -*-
"""Festivals card-deck UX + shopping souvenir panel updates."""
from __future__ import annotations

import io
import json
import re
import shutil
import ssl
import tempfile
import time
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CTX = ssl._create_unverified_context()
UA = "Mozilla/5.0 (compatible; KoreaTravelGuidebook/1.0)"
COVER = (1536, 1024)
LANGS = ["ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru"]
ASSET_V = "20260821183833"


def write_retry(path: Path, text: str, attempts: int = 12) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    last: Exception | None = None
    for i in range(attempts):
        tmp = None
        try:
            fd, tmp = tempfile.mkstemp(prefix=f".{path.stem}-", suffix=".tmp", dir=str(path.parent))
            with open(fd, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            Path(tmp).replace(path)
            return
        except OSError as e:
            last = e
            time.sleep(0.35 + i * 0.25)
            if tmp:
                try:
                    Path(tmp).unlink(missing_ok=True)
                except OSError:
                    pass
    raise last  # type: ignore[misc]


def http_get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "image/*,*/*"})
    with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
        return r.read()


def save_cover(dest: Path, data: bytes) -> None:
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
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "JPEG", quality=88, optimize=True)


def fetch_cover(dest: Path, urls: list[str], fallback: Path | None = None) -> None:
    if dest.is_file() and dest.stat().st_size > 4000:
        return
    for url in urls:
        for _ in range(2):
            try:
                data = http_get(url)
                if len(data) < 1500:
                    raise RuntimeError("small")
                save_cover(dest, data)
                print("cover", dest.relative_to(ROOT))
                return
            except Exception as e:  # noqa: BLE001
                print("cover fail", url[:70], e)
                time.sleep(1)
    if fallback and fallback.is_file():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(fallback, dest)
        print("cover copy", dest.relative_to(ROOT))
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", COVER, (232, 228, 220)).save(dest, "JPEG", quality=80)
        print("cover placeholder", dest.relative_to(ROOT))


ARTICLE = """<!DOCTYPE html>
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


def body_blocks(ko1: str, en1: str, ko2: str, en2: str) -> list:
    def blk(ko: str, en: str) -> dict:
        return {
            "type": "text",
            "ko": ko,
            "en": en,
            "ja": en,
            "zh": en,
            "zh-Hant": en,
            "vi": en,
            "th": en,
            "ru": en,
        }

    return [blk(ko1, en1), blk(ko2, en2)]


def put_i18n(key: str, ko: dict, en: dict) -> None:
    for lang in LANGS:
        path = ROOT / "i18n" / "pages" / "shopping" / f"{lang}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        souv = data.setdefault("souvenir", {})
        src = ko if lang == "ko" else en
        for field in ("Title", "Desc", "Body1", "Body2", "Tip"):
            souv[f"{key}{field}"] = src[field]
        souv[f"{key}Body"] = body_blocks(ko["Body1"], en["Body1"], ko["Body2"], en["Body2"])
        write_retry(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def make_item(slug: str, key: str, ko: dict, en: dict, urls: list[str], fallback: Path | None) -> None:
    page = ROOT / "pages" / "souvenir" / slug
    page.mkdir(parents=True, exist_ok=True)
    write_retry((page / "index.html"), ARTICLE.format(key=key, ver=ASSET_V))
    fetch_cover(page / "media" / "cover.jpg", urls, fallback)
    put_i18n(key, ko, en)
    print("item", slug)


def replace_panel(panel: str, cards_html: str) -> None:
    buy = ROOT / "pages" / "buy" / "index.html"
    html = buy.read_text(encoding="utf-8")
    pat = re.compile(
        rf'(<div class="tab-panel" role="tabpanel" data-buy-panel="{panel}"[^>]*>\s*<div class="souvenir-grid">)(.*?)(</div>\s*</div>)',
        re.S,
    )
    m = pat.search(html)
    if not m:
        raise SystemExit(f"panel {panel} missing")
    html = pat.sub(m.group(1) + "\n" + cards_html + "\n            " + m.group(3), html, count=1)
    write_retry(buy, html)
    print("panel", panel)


def patch_festivals() -> None:
    # HTML: replace official link cards with compact buttons
    fest = ROOT / "pages" / "festivals" / "index.html"
    html = fest.read_text(encoding="utf-8")
    new_links = """    <section class="festivals-links" aria-labelledby="festivals-links-heading">
      <h2 id="festivals-links-heading" data-i18n="festivals.linksTitle">공식 안내</h2>
      <p class="festivals-links__help" data-i18n="festivals.linksHelp">더 많은 지역 축제는 아래 공식 사이트에서 검색해 보세요.</p>
      <div class="festivals-link-buttons" role="list">
        <a class="festivals-link-btn" role="listitem" href="https://korean.visitkorea.or.kr/kfes" target="_blank" rel="noopener noreferrer" data-i18n="festivals.linkVisitKoreaTitle">한국관광공사 축제·행사</a>
        <a class="festivals-link-btn" role="listitem" href="https://korean.visitkorea.or.kr/kfes/list/wntyFstvlList.do" target="_blank" rel="noopener noreferrer" data-i18n="festivals.linkNationwideTitle">전국 축제 검색</a>
        <a class="festivals-link-btn" role="listitem" href="https://korean.visitkorea.or.kr/" target="_blank" rel="noopener noreferrer" data-i18n="festivals.linkKoreanVisitTitle">대한민국 구석구석</a>
        <a class="festivals-link-btn" role="listitem" href="https://english.visitkorea.or.kr/" target="_blank" rel="noopener noreferrer" data-i18n="festivals.linkVisitKoreaEnTitle">VisitKorea (English)</a>
      </div>
    </section>"""
    html = re.sub(
        r'<section class="festivals-links".*?</section>',
        new_links,
        html,
        count=1,
        flags=re.S,
    )
    # Add deck class on slider
    html = html.replace('class="festivals-slider"', 'class="festivals-slider festivals-slider--deck"', 1)
    html = html.replace('class="festivals-event-card"', 'class="festivals-event-card festivals-event-card--deck"')
    write_retry(fest, html)

    # CSS append/replace deck + button styles
    css_path = ROOT / "styles.css"
    css = css_path.read_text(encoding="utf-8")
    marker = "/* festivals-deck-v2 */"
    block = f"""
{marker}
.festivals-slider--deck {{
  perspective: 1200px;
}}
.festivals-slider--deck .festivals-slider__track {{
  gap: 18px;
  padding: 18px 8px 28px;
  scroll-padding-inline: 12px;
}}
.festivals-event-card--deck {{
  flex: 0 0 min(82vw, 300px);
  border-radius: 20px;
  border: 1px solid rgba(31, 58, 50, 0.12);
  box-shadow:
    0 1px 0 rgba(255,255,255,0.7) inset,
    0 14px 34px rgba(20, 40, 32, 0.14),
    0 4px 10px rgba(20, 40, 32, 0.06);
  transform: translateZ(0) rotateY(-1.5deg);
  background:
    linear-gradient(180deg, #ffffff 0%, #f7faf8 100%);
}}
.festivals-event-card--deck:hover {{
  transform: translateY(-6px) rotateY(0deg);
  box-shadow:
    0 1px 0 rgba(255,255,255,0.8) inset,
    0 22px 40px rgba(20, 40, 32, 0.18);
}}
.festivals-event-card--deck img {{
  aspect-ratio: 4 / 3;
}}
.festivals-event-card--deck .festivals-event-card__body {{
  min-height: 132px;
  padding: 16px 16px 18px;
}}
.festivals-link-buttons {{
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 0 0 12px;
}}
.festivals-link-btn {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 34px;
  padding: 6px 12px;
  border: 1px solid #c9d6d0;
  border-radius: 999px;
  background: #f4f8f6;
  color: #1f2a26;
  font-size: 0.82rem;
  font-weight: 600;
  line-height: 1.2;
  text-decoration: none;
}}
.festivals-link-btn:hover {{
  border-color: #7f9b8e;
  background: #eaf2ee;
}}
@media (min-width: 640px) {{
  .festivals-event-card--deck {{
    flex-basis: 280px;
  }}
}}
"""
    if marker in css:
        # replace from marker to next festivals-attribution or end of previous block
        css = re.sub(
            rf"{re.escape(marker)}.*?(?=\n\.festivals-attribution|\n/\*|\\Z)",
            block.strip() + "\n\n",
            css,
            count=1,
            flags=re.S,
        )
    else:
        # insert before .festivals-attribution
        css = css.replace(".festivals-attribution {", block + "\n.festivals-attribution {", 1)
    # Hide old large link-row if still referenced
    if ".festivals-link-row {" in css and "festivals-link-row{display:none" not in css.replace(" ", ""):
        css = css.replace(
            ".festivals-link-row {",
            ".festivals-link-row { display: none !important; /* replaced by .festivals-link-buttons */\n",
            1,
        )
    write_retry(css_path, css)
    print("festivals UI patched")


def main() -> None:
    patch_festivals()

    # --- Daily ---
    # Restore unified KF94 mask page
    make_item(
        "mask",
        "mask",
        {
            "Title": "KF94 마스크",
            "Desc": "약국·편의점·올리브영에서 사는 미세먼지 마스크",
            "Body1": "여행용으로 많이 사는 KF94(또는 KF80) 마스크입니다. 작심·블루닷·아에르 등 브랜드가 편의점·다이소·올리브영·약국에 소량 팩으로 많습니다.",
            "Body2": "캐리어에 넣기 쉬운 5~10매 팩이 실용적입니다. ‘KF94’ 표기와 포장 날짜를 확인하세요.",
            "Tip": "대량 구매는 시중 약국 묶음이 무난한 경우가 많습니다.",
        },
        {
            "Title": "KF94 masks",
            "Desc": "Dust masks from pharmacies, convenience stores, and Olive Young",
            "Body1": "KF94 (or KF80) masks are a common travel buy. Brands like Jaksim, Bluedot, and Aer come in small packs at convenience stores, Daiso, Olive Young, and pharmacies.",
            "Body2": "5–10 packs travel well. Check the KF grade and pack date.",
            "Tip": "For bulk, local pharmacy multipacks are often fine.",
        },
        [],
        ROOT / "pages/souvenir/jaksim-mask/media/cover.jpg",
    )

    # Kakao character goods (reuse stationery folder slug)
    put_i18n(
        "kakaoFriendsStationery",
        {
            "Title": "카카오 캐릭터 굿즈",
            "Desc": "카카오프렌즈 인형·문구·잡화 기념품",
            "Body1": "카카오 캐릭터 굿즈는 인형·키링·텀블러·문구·파우치 등 가벼운 기념품으로 인기입니다. 플래그십·아트박스·다이소·편의점 캐릭터 코너에서 찾을 수 있습니다.",
            "Body2": "한정 콜라보는 플래그십·팝업이 재고가 나은 편입니다. 부피가 큰 인형은 캐리어 공간을 먼저 확인하세요.",
            "Tip": "작은 키링·메모·스티커가 선물용으로 부담이 적습니다.",
        },
        {
            "Title": "Kakao character goods",
            "Desc": "Kakao Friends plush, stationery, and small gifts",
            "Body1": "Kakao character goods—plush, keyrings, tumblers, stationery, pouches—are popular light souvenirs. Find them at flagships, Artbox, Daiso, and convenience-store character corners.",
            "Body2": "Limited collabs are easier at flagships/pop-ups. Check suitcase space for large plush.",
            "Tip": "Small keyrings, memos, and stickers make easy gifts.",
        },
    )
    # rename page title file still uses same key - update article is fine via i18n

    make_item(
        "starbucks-tumbler",
        "starbucksTumbler",
        {
            "Title": "스타벅스 텀블러",
            "Desc": "한국 한정·시즌 텀블러·머그",
            "Body1": "스타벅스 한국 매장·리저브에서는 시즌·도시 한정 텀블러·머그가 자주 나옵니다. 여행 기념·선물로 많이 고릅니다.",
            "Body2": "명동·강남·공항 인근 매장은 품절이 빠를 수 있어 여유 있게 방문하세요. 액체 제한 때문에 출국 전에는 비워 휴대하세요.",
            "Tip": "시즌 신상은 출시 직후·주말에 빨리 소진됩니다.",
        },
        {
            "Title": "Starbucks tumbler",
            "Desc": "Korea-only and seasonal tumblers/mugs",
            "Body1": "Korean Starbucks and Reserve stores often carry seasonal or city-limited tumblers and mugs that travelers buy as souvenirs.",
            "Body2": "Busy tourist stores sell out fast. Empty bottles before flying to meet liquids rules.",
            "Tip": "New seasonal drops go quickly on launch weekends.",
        },
        [
            "https://images.unsplash.com/photo-1514228742587-6b1558fcc036?auto=format&fit=crop&w=1600&q=80",
            "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=1600&q=80",
        ],
        None,
    )

    daily_cards = "".join(
        [
            CARD.format(slug="mask", key="mask"),
            CARD.format(slug="kakao-friends-stationery", key="kakaoFriendsStationery"),
            CARD.format(slug="starbucks-tumbler", key="starbucksTumbler"),
            CARD.format(slug="kpop", key="kpop"),
        ]
    )
    replace_panel("daily", daily_cards)

    # Redirect removed daily pages
    for old, new in [
        ("jaksim-mask", "mask"),
        ("bluedot-mask", "mask"),
        ("aer-mask", "mask"),
        ("monami", "kakao-friends-stationery"),
        ("iconic", "kakao-friends-stationery"),
    ]:
        p = ROOT / "pages" / "souvenir" / old / "index.html"
        if p.parent.is_dir():
            write_retry(
                p,
                f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="UTF-8"><meta http-equiv="refresh" content="0;url=../{new}/index.html"><script>location.replace("../{new}/index.html");</script><title>Redirect</title></head>
<body><p><a href="../{new}/index.html">Continue</a></p></body></html>
""",
            )

    # --- Daiso: cica bubble ---
    make_item(
        "vt-cica-bubble-mask",
        "vtCicaBubbleMask",
        {
            "Title": "VT 시카 버블 스파클링 마스크",
            "Desc": "다이소 VT 시카 버블 부스터 — 휴대용 개별 포장",
            "Body1": "다이소에서 파는 VT 시카 버블 스파클링 부스터(마스크/부스터 팩)입니다. 크림 머드가 버블로 바뀌며 노폐물 흡착·진정 수분 케어용으로 여행객에게도 인기입니다.",
            "Body2": "개별 포장이라 위생적이고 캐리어에 넣기 쉽습니다. 다이소몰·매장 재고를 확인하고, 피부 자극이 있으면 사용을 중단하세요.",
            "Tip": "다이소몰 상품번호·매장 키오스크에서 ‘시카 버블’로 검색해 보세요.",
        },
        {
            "Title": "VT Cica Bubble Sparkling Mask",
            "Desc": "Daiso VT cica bubble booster — travel-friendly packets",
            "Body1": "VT Cica Bubble Sparkling Booster packs are a Daiso favorite. Cream-mud texture turns into bubbles for a quick clarifying/calming facial boost.",
            "Body2": "Individually wrapped and easy to pack. Check store/online stock and stop if irritation occurs.",
            "Tip": "Search “시카 버블 / Cica Bubble” on Daiso mall or in-store kiosks.",
        },
        [
            "https://images.unsplash.com/photo-1556228578-8c89e6adf883?auto=format&fit=crop&w=1600&q=80",
            "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?auto=format&fit=crop&w=1600&q=80",
        ],
        ROOT / "pages/souvenir/daiso/media/cover.jpg",
    )
    # Append to daiso panel - read existing and append
    buy = (ROOT / "pages" / "buy" / "index.html").read_text(encoding="utf-8")
    if "vt-cica-bubble-mask" not in buy:
        buy = buy.replace(
            'href="../souvenir/daiso/index.html"',
            'href="../souvenir/daiso/index.html"',
            1,
        )
        # insert after daiso card block end: find mommycare and insert before it, or after last daiso child
        insert_card = CARD.format(slug="vt-cica-bubble-mask", key="vtCicaBubbleMask")
        buy = buy.replace(
            '<a class="souvenir-card" href="../souvenir/mommycare-sea-grape-skin-pack/index.html">',
            insert_card + '\n              <a class="souvenir-card" href="../souvenir/mommycare-sea-grape-skin-pack/index.html">',
            1,
        )
        write_retry(ROOT / "pages" / "buy" / "index.html", buy)
        print("daiso card inserted")

    # --- Snacks ---
    make_item(
        "honey-butter-almond",
        "honeyButterAlmond",
        {
            "Title": "허니버터 아몬드",
            "Desc": "HBAF(바프) 허니버터 아몬드 — 외국인 필수 기념 스낵",
            "Body1": "HBAF(바프) 허니버터 아몬드는 꿀·버터 시즈닝을 입힌 아몬드 스낵으로, 외국인 관광객이 한국에서 꼭 사 가는 간식으로 유명합니다. 편의점·마트·명동 바프 매장에서 살 수 있습니다.",
            "Body2": "지퍼백·소포장 구성이 많아 선물·기내용으로 편합니다. 유사 브랜드가 있으니 패키지의 HBAF/바프 표기를 확인하세요.",
            "Tip": "명동 바프 스토어는 다양한 맛 샘플러도 함께 고르기 좋습니다.",
        },
        {
            "Title": "Honey Butter Almond",
            "Desc": "HBAF honey-butter almonds — a traveler staple snack",
            "Body1": "HBAF Honey Butter Almonds are honey-and-butter seasoned almonds that many visitors treat as a must-buy Korean snack. Find them at convenience stores, markets, and HBAF stores in Myeongdong.",
            "Body2": "Zip bags and gift packs travel well. Check the HBAF branding to avoid lookalikes.",
            "Tip": "Myeongdong HBAF stores are great for tasting multiple flavors.",
        },
        [
            "https://images.unsplash.com/photo-1508747703725-719777637510?auto=format&fit=crop&w=1600&q=80",
            "https://images.unsplash.com/photo-1604329760661-e7fb410d3ab9?auto=format&fit=crop&w=1600&q=80",
        ],
        ROOT / "pages/souvenir/honey-butter-chips/media/cover.jpg",
    )
    make_item(
        "americano-cooling-candy",
        "americanoCoolingCandy",
        {
            "Title": "아메리카노 쿨링캔디",
            "Desc": "커피 향 + 청량감 틴케이스 캔디 (편의점 인기)",
            "Body1": "아메리카노 쿨링캔디는 아메리카노 풍미와 쿨링감을 담은 틴케이스 캔디입니다. 무설탕(자일리톨) 표기 제품이 많아 휴대용·기념 간식으로 편의점에서 화제가 됐습니다.",
            "Body2": "당류 0g이어도 칼로리가 있을 수 있고, 자일리톨은 한꺼번에 많이 먹으면 배가 아플 수 있습니다. 라벨의 함량·주의사항을 확인하세요.",
            "Tip": "편의점 캔디·덴탈케어 코너에서 ‘아메리카노 쿨링’·틴케이스를 찾아보세요.",
        },
        {
            "Title": "Americano cooling candy",
            "Desc": "Coffee-flavored cooling candy in a tin (convenience-store hit)",
            "Body1": "Americano cooling candy packs coffee flavor with a cooling finish in a pocket tin. Sugar-free xylitol versions became a convenience-store trend.",
            "Body2": "Sugar-free is not calorie-free. High xylitol can upset the stomach if you eat too much—read the label.",
            "Tip": "Look for “Americano cooling” tins in the candy aisle.",
        },
        [
            "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=1600&q=80",
            "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=1600&q=80",
        ],
        None,
    )
    buy = (ROOT / "pages" / "buy" / "index.html").read_text(encoding="utf-8")
    for slug, key in [
        ("honey-butter-almond", "honeyButterAlmond"),
        ("americano-cooling-candy", "americanoCoolingCandy"),
    ]:
        if slug in buy:
            continue
        card = CARD.format(slug=slug, key=key)
        buy = buy.replace(
            '<a class="souvenir-card" href="../souvenir/pepero/index.html">',
            card + '\n              <a class="souvenir-card" href="../souvenir/pepero/index.html">',
            1,
        )
    write_retry(ROOT / "pages" / "buy" / "index.html", buy)

    # --- Food: bangatgan sesame oil ---
    make_item(
        "bangatgan-sesame-oil",
        "bangatganSesameOil",
        {
            "Title": "방앗간 참기름",
            "Desc": "방앗간·전통 참기름 — 선물용 국산 조미유",
            "Body1": "방앗간 참기름은 참깨를 짜낸 고소한 참기름으로, 한국 집에서 나물·비빔밥·고기 양념에 쓰는 기본 조미유입니다. 선물 세트·소용량 병이 마트·한식 코너·온라인에 많습니다.",
            "Body2": "직사광선을 피해 서늘한 곳에 두고, 개봉 후엔 가급적 빨리 드세요. 항공 액체 제한(기내 100ml)을 확인해 위탁 수하물로 보내는 편이 안전합니다.",
            "Tip": "‘방앗간’·참깨 함량·제조일을 라벨에서 확인하세요.",
        },
        {
            "Title": "Mill sesame oil (bangatgan)",
            "Desc": "Traditional sesame oil — a classic Korean pantry gift",
            "Body1": "Bangatgan (mill) sesame oil is pressed sesame oil used in namul, bibimbap, and marinades. Gift sets and small bottles are easy to find in markets and Korean grocery aisles.",
            "Body2": "Store cool and away from light; use soon after opening. For flights, check liquids rules—checked baggage is safer than cabin for larger bottles.",
            "Tip": "Check “방앗간”, sesame content, and pack date on the label.",
        },
        [
            "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=1600&q=80",
            "https://images.unsplash.com/photo-1606923829579-0cb981a83e2e?auto=format&fit=crop&w=1600&q=80",
        ],
        None,
    )
    buy = (ROOT / "pages" / "buy" / "index.html").read_text(encoding="utf-8")
    if "bangatgan-sesame-oil" not in buy:
        card = CARD.format(slug="bangatgan-sesame-oil", key="bangatganSesameOil")
        buy = buy.replace(
            '<a class="souvenir-card" href="../souvenir/buldak-bokkeum-myeon/index.html">',
            card + '\n              <a class="souvenir-card" href="../souvenir/buldak-bokkeum-myeon/index.html">',
            1,
        )
        write_retry(ROOT / "pages" / "buy" / "index.html", buy)

    # --- Beauty: olive young only ---
    # Restore olive page as Olive Young guide
    make_item(
        "olive",
        "olive",
        {
            "Title": "올리브영",
            "Desc": "올영픽·세일·택스프리 — 한국 뷰티 쇼핑 허브",
            "Body1": "올리브영은 외국인이 가장 많이 찾는 드럭스토어입니다. ‘올영픽’·세일 코너에서 시트마스크·선크림·틴트·스킨케어를 고르기 쉽고, 앱 쿠폰·증정 조합을 직원에게 물어보면 좋습니다.",
            "Body2": "명동·홍대·강남 대형점이 재고가 많고, 공항점은 품절이 잦을 수 있습니다. 택스프리 가능 매장인지 계산 전 확인하세요.",
            "Tip": "인기 제품은 아침에 서거나 온라인 픽업을 활용해 보세요.",
        },
        {
            "Title": "Olive Young",
            "Desc": "Picks, sales, tax-free — Korea’s beauty shopping hub",
            "Body1": "Olive Young is the drugstore travelers visit most. Start with Olive Young Picks and sale shelves for masks, sunscreen, tints, and skincare; ask staff about app coupons and GWP.",
            "Body2": "Large Myeongdong/Hongdae/Gangnam stores stock more; airport shops sell out faster. Confirm tax-free before checkout.",
            "Tip": "For hyped items, go early or use pickup options.",
        },
        [
            "https://images.unsplash.com/photo-1596462502278-27bfdc403348?auto=format&fit=crop&w=1600&q=80",
        ],
        ROOT / "pages/souvenir/mediheal/media/cover.jpg",
    )
    replace_panel("beauty", CARD.format(slug="olive", key="olive"))

    # --- Bakery: gyeongju sipwon bread ---
    make_item(
        "gyeongju-sipwon-bread",
        "gyeongjuSipwonBread",
        {
            "Title": "경주 십원빵",
            "Desc": "경주 기념 십원 모양 빵 — 여행 디저트",
            "Body1": "경주 십원빵은 십원 주화 문양을 올린 기념 빵·디저트로, 경주 시내 베이커리·관광 안내 포인트에서 많이 삽니다. 사진 찍기 좋은 비주얼 간식입니다.",
            "Body2": "당일 생산·유통기한이 짧은 편이니 당일 드시는 게 좋습니다. 경주 외 지역에서는 구하기 어려울 수 있습니다.",
            "Tip": "황남빵·찰보리빵과 함께 비교해 기념으로 골라 보세요.",
        },
        {
            "Title": "Gyeongju 10-won bread",
            "Desc": "Coin-stamped souvenir bread from Gyeongju",
            "Body1": "Gyeongju sipwon (10-won) bread is a souvenir bake stamped like the 10-won coin—popular around downtown Gyeongju bakeries and tourist spots.",
            "Body2": "Often same-day fresh with a short shelf life—eat soon. Harder to find outside Gyeongju.",
            "Tip": "Compare with Hwangnam bread and barley bread for a local pastry set.",
        },
        [
            "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=1600&q=80",
            "https://images.unsplash.com/photo-1549931319-a545dcf3bc73?auto=format&fit=crop&w=1600&q=80",
        ],
        ROOT / "pages/souvenir/nangman-sandwich/media/cover.jpg",
    )
    buy = (ROOT / "pages" / "buy" / "index.html").read_text(encoding="utf-8")
    if "gyeongju-sipwon-bread" not in buy:
        card = CARD.format(slug="gyeongju-sipwon-bread", key="gyeongjuSipwonBread")
        buy = buy.replace(
            '<div class="tab-panel" role="tabpanel" data-buy-panel="bakery" hidden>\n            <div class="souvenir-grid">',
            '<div class="tab-panel" role="tabpanel" data-buy-panel="bakery" hidden>\n            <div class="souvenir-grid">\n'
            + card,
            1,
        )
        write_retry(ROOT / "pages" / "buy" / "index.html", buy)

    # festivals i18n tiny help tweak
    for lang in LANGS:
        path = ROOT / "i18n" / "pages" / "festivals" / f"{lang}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        fest = data.setdefault("festivals", {})
        if lang == "ko":
            fest["featuredHelp"] = "카드를 좌우로 밀어 넘기듯 둘러보세요."
            fest["linksHelp"] = "더 많은 축제는 아래 공식 안내 버튼에서 확인하세요."
        elif lang == "ja":
            fest["featuredHelp"] = "カードを左右にスライドして見てください。"
            fest["linksHelp"] = "その他の祭りは下の公式ボタンから。"
        else:
            fest["featuredHelp"] = "Swipe the cards sideways like a deck."
            fest["linksHelp"] = "More festivals via the official buttons below."
        write_retry(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")

    import sys

    sys.path.insert(0, str(ROOT / "tool"))
    from lib.i18n_store import build_bundle, load_lang, save_lang

    for lang in LANGS:
        save_lang(lang, load_lang(lang))
    print(build_bundle())
    print("DONE")


if __name__ == "__main__":
    main()
