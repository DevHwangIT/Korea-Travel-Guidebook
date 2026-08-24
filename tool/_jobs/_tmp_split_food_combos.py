# -*- coding: utf-8 -*-
"""Remove ramen/tea/honey combo cards; add 정관장, 약과·한과 세트, 불닭볶음면."""
from __future__ import annotations

import io
import json
import re
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CTX = ssl._create_unverified_context()
UA = "KoreaTravelGuidebook/1.0 (souvenir-covers; educational)"
COVER_SIZE = (1536, 1024)
ASSET_V = "20260821002336"

SHOP_LANGS = ["ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru"]


def http_get(url: str, timeout: int = 90) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.read()


def commons_file_url(filename: str, width: int = 1600) -> str:
    enc = urllib.parse.quote(filename.replace(" ", "_"))
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{enc}?width={width}"


def save_cover(dest: Path, data: bytes) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(io.BytesIO(data)).convert("RGB")
    tw, th = COVER_SIZE
    src_w, src_h = im.size
    target_ratio = tw / th
    src_ratio = src_w / src_h
    if src_ratio > target_ratio:
        new_w = int(src_h * target_ratio)
        left = (src_w - new_w) // 2
        im = im.crop((left, 0, left + new_w, src_h))
    else:
        new_h = int(src_w / target_ratio)
        top = (src_h - new_h) // 2
        im = im.crop((0, top, src_w, top + new_h))
    im = im.resize(COVER_SIZE, Image.Resampling.LANCZOS)
    im.save(dest, "JPEG", quality=88, optimize=True)
    print(f"  cover -> {dest.relative_to(ROOT)} ({dest.stat().st_size} bytes)")


def fetch_cover(slug: str, commons_name: str) -> None:
    dest = ROOT / "pages" / "souvenir" / slug / "media" / "cover.jpg"
    url = commons_file_url(commons_name)
    print(f"fetch {slug}: {commons_name}")
    for attempt in range(4):
        try:
            data = http_get(url)
            if len(data) < 2000:
                raise RuntimeError(f"too small {len(data)}")
            save_cover(dest, data)
            return
        except Exception as exc:  # noqa: BLE001
            print(f"  retry {attempt+1}: {exc}")
            time.sleep(2 + attempt * 2)
    raise RuntimeError(f"failed cover for {slug}")


ARTICLE_TMPL = """<!DOCTYPE html>
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
    <p class="back-link"><a href="../../buy/index.html" data-i18n="buyHub.back">← 쇼핑 & 놀거리</a></p>
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

REDIRECT = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0;url=../../buy/index.html#shopping">
  <title>Redirect</title>
  <link rel="canonical" href="../../buy/index.html">
  <script>location.replace("../../buy/index.html#shopping");</script>
</head>
<body>
  <p><a href="../../buy/index.html#shopping">쇼핑 & 놀거리</a></p>
</body>
</html>
"""

CARD_CKJ = """              <a class="souvenir-card" href="../souvenir/cheong-kwan-jang/index.html">
                <img src="../souvenir/cheong-kwan-jang/media/cover.jpg" alt="" data-i18n-attr="alt:souvenir.cheongKwanJangTitle">
                <div class="souvenir-card-body">
                  <h3 data-i18n="souvenir.cheongKwanJangTitle"></h3>
                  <p data-i18n="souvenir.cheongKwanJangDesc"></p>
                  <span class="souvenir-more" data-i18n="souvenir.readMore">자세히 보기 →</span>
                </div>
              </a>
"""

CARD_YAKGWA = """              <a class="souvenir-card" href="../souvenir/yakgwa-hangwa-set/index.html">
                <img src="../souvenir/yakgwa-hangwa-set/media/cover.jpg" alt="" data-i18n-attr="alt:souvenir.yakgwaHangwaSetTitle">
                <div class="souvenir-card-body">
                  <h3 data-i18n="souvenir.yakgwaHangwaSetTitle"></h3>
                  <p data-i18n="souvenir.yakgwaHangwaSetDesc"></p>
                  <span class="souvenir-more" data-i18n="souvenir.readMore">자세히 보기 →</span>
                </div>
              </a>
"""

CARD_BULDAK = """              <a class="souvenir-card" href="../souvenir/buldak-bokkeum-myeon/index.html">
                <img src="../souvenir/buldak-bokkeum-myeon/media/cover.jpg" alt="" data-i18n-attr="alt:souvenir.buldakBokkeumMyeonTitle">
                <div class="souvenir-card-body">
                  <h3 data-i18n="souvenir.buldakBokkeumMyeonTitle"></h3>
                  <p data-i18n="souvenir.buldakBokkeumMyeonDesc"></p>
                  <span class="souvenir-more" data-i18n="souvenir.readMore">자세히 보기 →</span>
                </div>
              </a>
"""

NEW_KEYS_FULL = {
    "cheongKwanJangTitle": {
        "ko": "정관장",
        "en": "Cheong Kwan Jang",
        "ja": "正官庄",
        "zh": "正官庄",
        "zh-Hant": "正官莊",
        "vi": "Cheong Kwan Jang",
        "th": "ชองกวานจัง",
        "ru": "Cheong Kwan Jang",
    },
    "cheongKwanJangDesc": {
        "ko": "한국인삼공사 정관장 — 홍삼 스틱·선물세트 대표 브랜드.",
        "en": "KGC Cheong Kwan Jang — Korea’s flagship red-ginseng sticks and gift sets.",
        "ja": "韓国人参公社の正官庄。紅参スティック・ギフトセットの定番。",
        "zh": "韩国人参公社正官庄 — 红参条与礼盒代表品牌。",
        "zh-Hant": "韓國人參公社正官莊 — 紅參條與禮盒代表品牌。",
        "vi": "KGC Cheong Kwan Jang — thương hiệu hồng sâm stick & set quà nổi tiếng.",
        "th": "KGC ชองกวานจัง — แบรนด์โสมแดงสติกและชุดของขวัญชั้นนำ",
        "ru": "KGC Cheong Kwan Jang — флагманские стики красного женьшеня и подарочные наборы.",
    },
    "cheongKwanJangBody1": {
        "ko": "정관장(Cheong Kwan Jang)은 한국인삼공사(KGC)의 홍삼 브랜드로, 에브리타임 스틱·농축액·선물세트가 백화점 식품관·면세·공항에서 잘 팔립니다. 여행 선물·건강 기념품으로 자주 고릅니다.",
        "en": "Cheong Kwan Jang is KGC’s red-ginseng brand — Everytime sticks, extracts, and gift sets sell well in department food halls, duty-free, and airports. A common health souvenir.",
        "ja": "正官庄は韓国人参公社の紅参ブランド。エブリタイムスティック・濃縮液・ギフトが百貨店・免税・空港で人気です。",
        "zh": "正官庄是韩国人参公社的红参品牌。Everytime条、浓缩液和礼盒在百货食品区、免税和机场很常见。",
        "zh-Hant": "正官莊是韓國人參公社的紅參品牌。Everytime條、濃縮液和禮盒在百貨食品區、免稅和機場很常見。",
        "vi": "Cheong Kwan Jang là thương hiệu hồng sâm của KGC — stick Everytime, cao và set quà dễ mua ở siêu thị cao cấp, duty-free, sân bay.",
        "th": "ชองกวานจังคือแบรนด์โสมแดงของ KGC — สติก Everytime สารสกัด และชุดของขวัญหาซื้อได้ตามห้าง ดิวตี้ฟรี สนามบิน",
        "ru": "Cheong Kwan Jang — бренд красного женьшеня KGC: стики Everytime, экстракты и подарочные наборы в универмагах, duty-free и аэропортах.",
    },
    "cheongKwanJangBody2": {
        "ko": "위조 방지를 위해 공식·대형 매장 구매를 권합니다. 액체 스틱은 기내 액체 제한에 걸리니 위탁 수하물이나 분말·정제형을 고려하세요.",
        "en": "Buy from official/large retailers to avoid counterfeits. Liquid sticks count as cabin liquids — use checked bags or powder/tablet formats.",
        "ja": "偽造防止のため公式・大型店で。液体スティックは機内制限対象なので預け入れか粉末・錠剤を。",
        "zh": "为防假货请在官方或大型店购买。液体条受机上液体限制，可托运或选粉剂/片剂。",
        "zh-Hant": "為防假貨請在官方或大型店購買。液體條受機上液體限制，可託運或選粉劑/片劑。",
        "vi": "Mua ở cửa hàng chính thức/lớn để tránh hàng giả. Stick lỏng tính vào hạn chế chất lỏng — gửi ký gửi hoặc chọn bột/viên.",
        "th": "ซื้อจากร้านทางการ/ห้างใหญ่กันของปลอม สติกเหลวติดข้อจำกัดของเหลวบนเครื่อง — ใส่กระเป๋าโหลดหรือเลือกแบบผง/เม็ด",
        "ru": "Покупайте в официальных/крупных магазинах. Жидкие стики — ограничение ручной клади; сдавайте багаж или берите порошок/таблетки.",
    },
    "cheongKwanJangTip": {
        "ko": "구매 팁\n\n정관장 공식·백화점·공항 면세 구성을 비교하고, 유통기한·정품 스티커를 확인하세요.",
        "en": "Buying tip\n\nCompare official, department-store, and airport sets; check expiry and authenticity seals.",
        "ja": "買い方\n\n公式・百貨店・空港セットを比較し、期限・正規シールを確認。",
        "zh": "购买提示\n\n比较官方、百货与机场套装，核对保质期与正品标识。",
        "zh-Hant": "購買提示\n\n比較官方、百貨與機場套裝，核對保質期與正品標識。",
        "vi": "Mẹo mua\n\nSo set chính hãng, department store và sân bay; kiểm tra HSD và tem chính hãng.",
        "th": "เคล็ดลับ\n\nเทียบชุดทางการ ห้าง และสนามบิน ตรวจวันหมดอายุและซีลของแท้",
        "ru": "Совет\n\nСравните официальные, универмаг и аэропортные наборы; проверяйте срок и пломбы.",
    },
    "yakgwaHangwaSetTitle": {
        "ko": "약과·한과 세트",
        "en": "Yakgwa & hangwa set",
        "ja": "薬菓・韓菓セット",
        "zh": "药果·韩果套装",
        "zh-Hant": "藥果·韓菓套裝",
        "vi": "Set yakgwa & hangwa",
        "th": "ชุดยักฮวาและฮังวา",
        "ru": "Набор якгва и хангва",
    },
    "yakgwaHangwaSetDesc": {
        "ko": "전통 약과와 한과 선물세트 — 인사동·백화점·공항 스테디.",
        "en": "Traditional yakgwa and hangwa gift sets — Insadong, department stores, airports.",
        "ja": "伝統の薬菓・韓菓ギフト。仁寺洞・百貨店・空港の定番。",
        "zh": "传统药果与韩果礼盒 — 仁寺洞、百货、机场常备。",
        "zh-Hant": "傳統藥果與韓菓禮盒 — 仁寺洞、百貨、機場常備。",
        "vi": "Set quà yakgwa & hangwa truyền thống — Insadong, department store, sân bay.",
        "th": "ชุดของขวัญยักฮวาและฮังวาแบบดั้งเดิม — อินซาดง ห้าง สนามบิน",
        "ru": "Подарочные наборы якгва и хангва — Инсадон, универмаги, аэропорты.",
    },
    "yakgwaHangwaSetBody1": {
        "ko": "약과는 밀가루·꿀·참기름 반죽을 튀겨 조청에 재운 전통 한과이고, 한과 세트는 유과·강정·다식 등과 함께 선물 박스로 많이 나갑니다. 명절·답례 선물로 인사동·백화점·공항에서 구하기 쉽습니다.",
        "en": "Yakgwa is deep-fried wheat dough soaked in syrup — a classic hangwa. Gift boxes often mix yakgwa with yugwa, gangjeong, and dasik. Easy to find in Insadong, department stores, and airports.",
        "ja": "薬菓は小麦粉・蜂蜜・ごま油の生地を揚げて飴に漬けた伝統菓子。韓菓セットは油菓・姜精・茶食などと一緒のギフトが多いです。",
        "zh": "药果是油炸面团再浸糖浆的传统韩果；礼盒常搭配油果、姜精、茶食。仁寺洞、百货、机场易购。",
        "zh-Hant": "藥果是油炸麵團再浸糖漿的傳統韓菓；禮盒常搭配油果、薑精、茶食。仁寺洞、百貨、機場易購。",
        "vi": "Yakgwa là bánh chiên ngâm mật — hangwa cổ điển. Hộp quà thường kèm yugwa, gangjeong, dasik. Dễ mua ở Insadong, department store, sân bay.",
        "th": "ยักฮวาคือขนมทอดชุบน้ำเชื่อมแบบดั้งเดิม ชุดฮังวามักรวมยูควา แกงจอง ดาซิก หาได้ที่อินซาดง ห้าง สนามบิน",
        "ru": "Якгва — жареное тесто в сиропе, классическая хангва. В наборах часто югва, ганджон, дасик. Легко купить в Инсадоне, универмагах и аэропортах.",
    },
    "yakgwaHangwaSetBody2": {
        "ko": "깨지기 쉬우니 완충 포장·개별 포장 제품을 고르세요. 여름에는 녹거나 변형될 수 있어 시원한 보관·출국 직전 구매가 안전합니다.",
        "en": "They crush easily — pick padded or individually wrapped boxes. In summer they can soften; keep cool and buy near departure.",
        "ja": "割れやすいので緩衝・個包装を。夏は溶けやすいので涼しい保管・出発直前購入を。",
        "zh": "易碎，选缓冲或独立包装。夏天易软化，宜阴凉存放、临出发购买。",
        "zh-Hant": "易碎，選緩衝或獨立包裝。夏天易軟化，宜陰涼存放、臨出發購買。",
        "vi": "Dễ vỡ — chọn hộp đệm/gói riêng. Mùa hè dễ mềm — giữ mát, mua sát giờ bay.",
        "th": "แตกง่าย เลือกกล่องกันกระแทก/ห่อเดี่ยว ฤดูร้อนละลายง่าย เก็บเย็น ซื้อใกล้ขึ้นเครื่อง",
        "ru": "Ломкие — берите с амортизацией/индивидуальной упаковкой. Летом размягчаются — храните в прохладе, покупайте ближе к вылету.",
    },
    "yakgwaHangwaSetTip": {
        "ko": "구매 팁\n\n시장 벌크보다 밀봉·유통기한이 있는 선물세트가 검역·선물용으로 무난합니다.",
        "en": "Buying tip\n\nSealed gift sets with expiry dates beat open market bulk for gifts and customs.",
        "ja": "買い方\n\n市場の量り売りより期限付き密封ギフトが安心。",
        "zh": "购买提示\n\n有密封与保质期的礼盒比散装更适合送礼和通关。",
        "zh-Hant": "購買提示\n\n有密封與保質期的禮盒比散裝更適合送禮和通關。",
        "vi": "Mẹo mua\n\nHộp quà niêm phong có HSD an toàn hơn hàng rời ở chợ.",
        "th": "เคล็ดลับ\n\nชุดของขวัญซีลมีวันหมดอายุดีกว่าซื้อยกกองในตลาด",
        "ru": "Совет\n\nЗапечатанные наборы со сроком годности лучше рыночного развеса для подарков и таможни.",
    },
    "buldakBokkeumMyeonTitle": {
        "ko": "불닭볶음면",
        "en": "Buldak bokkeum myeon",
        "ja": "ブルダック炒め麺",
        "zh": "火鸡面（不鸡炒面）",
        "zh-Hant": "火雞麵（不雞炒麵）",
        "vi": "Mì xào cay Buldak",
        "th": "บูลดัคบกกึมมยอน",
        "ru": "Пульдак поккым мён",
    },
    "buldakBokkeumMyeonDesc": {
        "ko": "삼양 불닭볶음면 — 매운맛 K-라면 아이콘, 멀티팩 기념품.",
        "en": "Samyang Buldak — iconic spicy Korean ramen, popular multipack souvenir.",
        "ja": "三養ブルダック炒め麺。辛口Kラーメンの定番、マルチパック土産。",
        "zh": "三养火鸡面 — 韩式辣面代表，多包装伴手礼。",
        "zh-Hant": "三養火雞麵 — 韓式辣麵代表，多包裝伴手禮。",
        "vi": "Samyang Buldak — mì cay biểu tượng Hàn, gói nhiều làm quà.",
        "th": "ซัมยังบูลดัค — ราเม็งเผ็ดไอคอนเกาหลี แพ็กหลายชิ้นเป็นของฝาก",
        "ru": "Samyang Buldak — культовая острая рамён, популярный мультипак-сувенир.",
    },
    "buldakBokkeumMyeonBody1": {
        "ko": "삼양 불닭볶음면은 오리지널·카르보나라·치즈 등 맛 변형이 많은 매운 볶음 라면입니다. 마트·편의점·다이소에서 봉지 멀티팩(5개입)으로 기념품처럼 사 가는 외국인이 많습니다.",
        "en": "Samyang Buldak is a spicy stir-fry ramen with many flavors (original, carbonara, cheese). Visitors often buy 5-pack bags at marts, convenience stores, and Daiso as edible souvenirs.",
        "ja": "三養ブルダックはオリジナル・カルボ・チーズなど味が多い辛炒め麺。マート・コンビニ・ダイソーの5個パックが土産人気です。",
        "zh": "三养火鸡面有原味、奶油、芝士等多种口味。游客常在超市、便利店、Daiso买五连包当伴手礼。",
        "zh-Hant": "三養火雞麵有原味、奶油、起司等多種口味。遊客常在超市、便利店、Daiso買五連包當伴手禮。",
        "vi": "Samyang Buldak có nhiều vị (gốc, carbonara, phô mai). Du khách hay mua túi 5 gói ở siêu thị, cửa hàng tiện lợi, Daiso làm quà.",
        "th": "ซัมยังบูลดัคมีหลายรส (ดั้งเดิม คาร์โบนารา ชีส) นักท่องเที่ยวมักซื้อแพ็ก 5 ที่ห้าง ร้านสะดวกซื้อ ไดโซ",
        "ru": "Samyang Buldak — острая жареная лапша (оригинал, карбонара, сыр). Часто берут 5-паки в маркетах, магазинах и Daiso.",
    },
    "buldakBokkeumMyeonBody2": {
        "ko": "조리 시 물을 버리고 소스를 비비는 타입입니다. 액상 소스는 압력으로 터질 수 있어 지퍼백에 한 번 더 넣으세요. 매운맛에 약하면 카르보·치즈부터 추천합니다.",
        "en": "Drain then mix the sauce. Double-bag liquid packets. If spice-sensitive, start with carbonara or cheese.",
        "ja": "湯切りしてソースを絡めます。液状ソースはジップ袋に。辛さに弱ければカルボ・チーズから。",
        "zh": "沥水后拌酱。液态酱包再套拉链袋。怕辣可先试奶油或芝士味。",
        "zh-Hant": "瀝水後拌醬。液態醬包再套拉鍊袋。怕辣可先試奶油或起司味。",
        "vi": "Chắt nước rồi trộn sốt. Bọc thêm túi zip cho gói sốt. Nếu sợ cay, bắt đầu với carbonara hoặc phô mai.",
        "th": "เทน้ำทิ้งแล้วคลุกซอส ใส่ถุงซิปซ้ำ ถ้าเผ็ดไม่ไหวเริ่มคาร์โบนาราหรือชีส",
        "ru": "Слейте воду и смешайте с соусом. Пакетики — в zip. Если остро — начните с карбонары или сыра.",
    },
    "buldakBokkeumMyeonTip": {
        "ko": "구매 팁\n\n이마트·홈플러스 라면 특가가 편의점보다 저렴한 경우가 많습니다. ‘삼양 불닭’ 표기를 확인하세요.",
        "en": "Buying tip\n\nHypermarket ramen deals often beat convenience stores. Look for the Samyang Buldak label.",
        "ja": "買い方\n\n大型マート特価がお得なことが多い。三養ブルダック表示を確認。",
        "zh": "购买提示\n\n大型超市特价往往比便利店便宜。认准三养火鸡面包装。",
        "zh-Hant": "購買提示\n\n大型超市特價往往比便利店便宜。認準三養火雞麵包裝。",
        "vi": "Mẹo mua\n\nSiêu thị thường rẻ hơn cửa hàng tiện lợi. Nhìn nhãn Samyang Buldak.",
        "th": "เคล็ดลับ\n\nห้างใหญ่มักถูกกว่าร้านสะดวกซื้อ ดูฉลากซัมยังบูลดัค",
        "ru": "Совет\n\nГипермаркеты часто дешевле магазинов у дома. Ищите этикетку Samyang Buldak.",
    },
}


def make_body(key_base: str) -> list:
    b1 = NEW_KEYS_FULL[f"{key_base}Body1"]
    b2 = NEW_KEYS_FULL[f"{key_base}Body2"]
    tip = NEW_KEYS_FULL[f"{key_base}Tip"]
    return [
        {"type": "text", **b1},
        {"type": "text", **b2},
        {"type": "callout", **{k: tip[k] for k in tip}},
    ]


def remove_card(text: str, slug: str) -> tuple[str, bool]:
    pattern = (
        rf'\s*<a class="souvenir-card" href="\.\./souvenir/{re.escape(slug)}/index\.html">.*?</a>\s*'
    )
    text2, n = re.subn(pattern, "\n", text, count=1, flags=re.S)
    return text2, n > 0


def patch_buy_index() -> None:
    path = ROOT / "pages" / "buy" / "index.html"
    text = path.read_text(encoding="utf-8")

    for slug in ("ramen", "tea", "honey"):
        text, ok = remove_card(text, slug)
        print(f"{'removed' if ok else 'WARN missing'} combo card: {slug}")

    # Insert new cards into food panel (before closing souvenir-grid of food)
    # Prefer after yangban if present, else at start of food grid after opening div
    if "souvenir/buldak-bokkeum-myeon/" not in text:
        # Insert buldak + yakgwa near top of food grid; CKJ into health
        m = re.search(
            r'(<div class="tab-panel" role="tabpanel" data-buy-panel="food"[^>]*>\s*<div class="souvenir-grid">)',
            text,
        )
        if not m:
            raise RuntimeError("food panel not found")
        insert = m.group(1) + "\n" + CARD_BULDAK + CARD_YAKGWA
        text = text[: m.start()] + insert + text[m.end() :]
        print("added buldak + yakgwa-hangwa cards to food tab")
    else:
        print("buldak card already present")

    if "souvenir/cheong-kwan-jang/" not in text:
        m = re.search(
            r'(<div class="tab-panel" role="tabpanel" data-buy-panel="health"[^>]*>\s*<div class="souvenir-grid">)',
            text,
        )
        if not m:
            raise RuntimeError("health panel not found")
        insert = m.group(1) + "\n" + CARD_CKJ
        text = text[: m.start()] + insert + text[m.end() :]
        print("added cheong-kwan-jang card to health tab")
    else:
        print("cheong-kwan-jang card already present")

    path.write_text(text, encoding="utf-8", newline="\n")


def write_pages() -> None:
    for slug, key in [
        ("cheong-kwan-jang", "cheongKwanJang"),
        ("yakgwa-hangwa-set", "yakgwaHangwaSet"),
        ("buldak-bokkeum-myeon", "buldakBokkeumMyeon"),
    ]:
        idx = ROOT / "pages" / "souvenir" / slug / "index.html"
        idx.parent.mkdir(parents=True, exist_ok=True)
        (idx.parent / "media").mkdir(exist_ok=True)
        idx.write_text(
            ARTICLE_TMPL.format(key=key, ver=ASSET_V),
            encoding="utf-8",
            newline="\n",
        )
        print(f"wrote {idx.relative_to(ROOT)}")

    for slug in ("ramen", "tea", "honey"):
        path = ROOT / "pages" / "souvenir" / slug / "index.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(REDIRECT, encoding="utf-8", newline="\n")
        print(f"{slug}/index.html -> redirect to buy#shopping")


def patch_i18n() -> None:
    for lang in SHOP_LANGS:
        path = ROOT / "i18n" / "pages" / "shopping" / f"{lang}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        souv = data.setdefault("souvenir", {})

        for key_base in ("cheongKwanJang", "yakgwaHangwaSet", "buldakBokkeumMyeon"):
            for suffix in ("Title", "Desc", "Body1", "Body2", "Tip"):
                full = f"{key_base}{suffix}"
                souv[full] = NEW_KEYS_FULL[full][lang]
            souv[f"{key_base}Body"] = make_body(key_base)

        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"i18n patched {path.relative_to(ROOT)}")


COVERS = {
    "buldak-bokkeum-myeon": "Buldak Ramen 20210114 003.jpg",
    "yakgwa-hangwa-set": "Korean hangwa-Yakgwa-Yugwa-Tea-01.jpg",
    "cheong-kwan-jang": "Korean ginseng-Hongsam-01.jpg",
}

ALTS = {
    "buldak-bokkeum-myeon": [
        "Buldak Ramen 20210114 001.jpg",
        "Buldak Ramen 20210114 002.jpg",
        "SAMYANG INSTANT NOODLES HOT CHICKEN CHEESE FLAVOUR.jpg",
    ],
    "yakgwa-hangwa-set": [
        "Yakgwa 1.jpg",
        "Korean.food-Yakgwa-01.jpg",
        "KOCIS yakgwa, honey cookies (4646996556).jpg",
    ],
    "cheong-kwan-jang": [
        "Korean red ginseng.jpg",
        "Red ginseng slices (20240124).jpg",
        "HK SW CMMA 香港中藥聯商會 Chinese Medicine Merchants Association - 高麗紅參 Korean Red Ginseng Jan-2014.JPG",
    ],
}


def main() -> None:
    write_pages()
    patch_buy_index()
    patch_i18n()

    for slug, name in list(COVERS.items()):
        ok = False
        try:
            fetch_cover(slug, name)
            ok = True
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL {slug} primary: {exc}")
            for alt in ALTS.get(slug, []):
                try:
                    fetch_cover(slug, alt)
                    ok = True
                    break
                except Exception as e2:  # noqa: BLE001
                    print(f"  alt fail {alt}: {e2}")
        if not ok:
            print(f"WARN: no new cover for {slug}")
        time.sleep(1.2)

    print("DONE structural + covers — run i18n/build-bundle.py next")


if __name__ == "__main__":
    main()
