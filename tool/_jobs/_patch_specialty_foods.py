#!/usr/bin/env python3
"""Update regional specialty shopping tip with city food list."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOPPING_DIR = ROOT / "i18n" / "pages" / "shopping"
LANGS = ("ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru")
MAP_SRC = "Images/shopping/regional-specialty-map.jpg"

CONTENT = {
    "ko": {
        "specialtyLead": "권역·도시마다 유명한 대표 먹거리가 있습니다",
        "specialty1": "한국은 권역·도시마다 대표 먹거리가 뚜렷합니다. 아래 목록을 참고해 해당 지역을 방문할 때 현지에서 맛보거나, 특산품·기념품으로 찾아보세요.",
        "specialty2": "공항·기차역·전통시장·관광지 매장에도 ‘지역 특산품’ 코너가 있습니다. 식품은 유통기한·보관 방법·기내 반입 규정을 확인한 뒤 쇼핑하세요.",
        "listTitle": "지역별 대표 먹거리",
        "listIntro": "해당 지역을 방문할 때 아래 음식을 참고해 보세요.",
        "items": [
            "경인권(인천) — 간장게장",
            "경상권(부산) — 돼지국밥",
            "경인권(인천) — 짜장면",
            "경상권(대구) — 치킨",
            "경인권(수원) — 왕갈비",
            "경상권(안동) — 안동찜닭",
            "경인권(의정부) — 부대찌개",
            "전라권(전주) — 전주비빔밥",
            "강원권(춘천) — 닭갈비",
            "전라권(담양) — 떡갈비",
            "강원권(횡성) — 한우(Korean BBQ)",
            "전라권(광주) — 육전",
            "강원권(강릉) — 초당순두부",
            "제주권(제주) — 흑돼지(Korean BBQ)",
            "충청권(대전) — 칼국수",
        ],
        "listOutro": "현지 식당에서 직접 맛보는 것도 좋고, 간편식·소스·기념품 형태로 사는 것도 여행 기념품으로 인기가 많습니다.",
    },
    "en": {
        "specialtyLead": "Each region and city has famous signature dishes",
        "specialty1": "Korea has clear regional food icons. Use the list below when you visit each area — eat locally or look for specialty products and souvenirs.",
        "specialty2": "Airports, train stations, markets, and tourist shops often have regional specialty corners. Check expiry, storage, and carry-on rules for food.",
        "listTitle": "Regional signature dishes",
        "listIntro": "When you visit these areas, keep these foods in mind:",
        "items": [
            "Gyeongin (Incheon) — ganjang gejang (soy-marinated crab)",
            "Gyeongsang (Busan) — dwaeji gukbap (pork soup rice)",
            "Gyeongin (Incheon) — jajangmyeon (black bean noodles)",
            "Gyeongsang (Daegu) — fried chicken",
            "Gyeongin (Suwon) — wang galbi (king ribs)",
            "Gyeongsang (Andong) — Andong jjimdak (braised chicken)",
            "Gyeongin (Uijeongbu) — budae jjigae (army stew)",
            "Jeolla (Jeonju) — Jeonju bibimbap",
            "Gangwon (Chuncheon) — dakgalbi (spicy stir-fried chicken)",
            "Jeolla (Damyang) — tteokgalbi (grilled rib patty)",
            "Gangwon (Hoengseong) — Hanwoo Korean BBQ",
            "Jeolla (Gwangju) — yukjeon (beef pancake)",
            "Gangwon (Gangneung) — Chodang sundubu (soft tofu)",
            "Jeju (Jeju) — black pork Korean BBQ",
            "Chungcheong (Daejeon) — kalguksu (knife-cut noodles)",
        ],
        "listOutro": "Try them at local restaurants, or pick up ready-to-eat items, sauces, and souvenirs — both are popular with travelers.",
    },
    "ja": {
        "specialtyLead": "地域・都市ごとに有名な代表グルメがあります",
        "specialty1": "韓国は地域・都市ごとに代表料理がはっきりしています。下の一覧を参考に、訪問時に現地で味わうか、特産品・お土産として探してみてください。",
        "specialty2": "空港・駅・市場・観光地店舗にも「地域特産」コーナーがあります。食品は賞味期限・保存方法・機内持ち込みを確認してから買い物を。",
        "listTitle": "地域別 代表グルメ",
        "listIntro": "該当地域を訪れる際は、以下を参考にしてください。",
        "items": [
            "京仁圏（仁川） — カンジャンケジャン（醤油ガニ）",
            "慶尚圏（釜山） — トェジクッパ（豚スープ飯）",
            "京仁圏（仁川） — チャジャンミョン",
            "慶尚圏（大邱） — チキン",
            "京仁圏（水原） — ワンカルビ",
            "慶尚圏（安東） — 安東チムダク",
            "京仁圏（議政府） — プデチゲ",
            "全羅圏（全州） — 全州ビビンバ",
            "江原圏（春川） — タッカルビ",
            "全羅圏（潭陽） — トックカルビ",
            "江原圏（横城） — 韓牛 Korean BBQ",
            "全羅圏（光州） — ユクジョン（牛肉チヂミ）",
            "江原圏（江陵） — 草堂スンドゥブ",
            "済州圏（済州） — 黒豚 Korean BBQ",
            "忠清圏（大田） — カルグクス",
        ],
        "listOutro": "現地の店で食べるのも、レトルト・ソース・お土産として買うのも旅行者に人気です。",
    },
    "zh": {
        "specialtyLead": "各圈、各城市都有著名的代表美食",
        "specialty1": "韩国各圈、各城市都有鲜明的代表美食。参考下列清单，到访当地时可现场品尝，或寻找特产与纪念品。",
        "specialty2": "机场、火车站、传统市场与景区商店也常有“地区特产”专区。购买食品前请确认保质期、保存方式与登机规定。",
        "listTitle": "各地区代表美食",
        "listIntro": "到访下列地区时，可参考这些名物：",
        "items": [
            "京仁圈（仁川） — 酱油蟹",
            "庆尚圈（釜山） — 猪肉汤饭",
            "京仁圈（仁川） — 炸酱面",
            "庆尚圈（大邱） — 炸鸡",
            "京仁圈（水原） — 王排骨",
            "庆尚圈（安东） — 安东炖鸡",
            "京仁圈（议政府） — 部队锅",
            "全罗圈（全州） — 全州拌饭",
            "江原圈（春川） — 辣炒鸡排",
            "全罗圈（潭阳） — 年糕排骨",
            "江原圈（横城） — 韩牛 Korean BBQ",
            "全罗圈（光州） — 肉饼",
            "江原圈（江陵） — 草堂嫩豆腐",
            "济州圈（济州） — 黑猪 Korean BBQ",
            "忠清圈（大田） — 刀切面",
        ],
        "listOutro": "在当地餐厅品尝，或购买即食、酱料、纪念品形式，都是旅行者很喜欢的选择。",
    },
    "zh-Hant": {
        "specialtyLead": "各圈、各城市都有著名的代表美食",
        "specialty1": "韓國各圈、各城市都有鮮明的代表美食。參考下列清單，造訪當地時可現場品嚐，或尋找特產與紀念品。",
        "specialty2": "機場、火車站、傳統市場與景區商店也常有「地區特產」專區。購買食品前請確認保存期限、保存方式與登機規定。",
        "listTitle": "各地區代表美食",
        "listIntro": "造訪下列地區時，可參考這些名物：",
        "items": [
            "京仁圈（仁川） — 醬油蟹",
            "慶尚圈（釜山） — 豬肉湯飯",
            "京仁圈（仁川） — 炸醬麵",
            "慶尚圈（大邱） — 炸雞",
            "京仁圈（水原） — 王排骨",
            "慶尚圈（安東） — 安東燉雞",
            "京仁圈（議政府） — 部隊鍋",
            "全羅圈（全州） — 全州拌飯",
            "江原圈（春川） — 辣炒雞排",
            "全羅圈（潭陽） — 年糕排骨",
            "江原圈（橫城） — 韓牛 Korean BBQ",
            "全羅圈（光州） — 肉餅",
            "江原圈（江陵） — 草堂嫩豆腐",
            "濟州圈（濟州） — 黑豬 Korean BBQ",
            "忠清圈（大田） — 刀切麵",
        ],
        "listOutro": "在當地餐廳品嚐，或購買即食、醬料、紀念品形式，都是旅行者很喜歡的選擇。",
    },
    "vi": {
        "specialtyLead": "Mỗi vùng và thành phố có món ăn đặc trưng nổi tiếng",
        "specialty1": "Hàn Quốc có các món đại diện rõ ràng theo vùng. Tham khảo danh sách dưới đây khi đến từng khu vực — thưởng thức tại chỗ hoặc mua đặc sản, quà lưu niệm.",
        "specialty2": "Sân bay, ga tàu, chợ và cửa hàng du lịch thường có góc đặc sản vùng. Kiểm tra hạn dùng, bảo quản và quy định mang lên máy bay.",
        "listTitle": "Món ăn đặc trưng theo vùng",
        "listIntro": "Khi đến các khu vực sau, hãy tham khảo:",
        "items": [
            "Gyeongin (Incheon) — cua ngâm tương (ganjang gejang)",
            "Gyeongsang (Busan) — cháo thịt heo (dwaeji gukbap)",
            "Gyeongin (Incheon) — mì tương đen (jajangmyeon)",
            "Gyeongsang (Daegu) — gà rán",
            "Gyeongin (Suwon) — sườn vua (wang galbi)",
            "Gyeongsang (Andong) — gà hầm Andong",
            "Gyeongin (Uijeongbu) — lẩu quân đội (budae jjigae)",
            "Jeolla (Jeonju) — bibimbap Jeonju",
            "Gangwon (Chuncheon) — dakgalbi",
            "Jeolla (Damyang) — tteokgalbi",
            "Gangwon (Hoengseong) — thịt bò Hanwoo Korean BBQ",
            "Jeolla (Gwangju) — bánh thịt bò chiên (yukjeon)",
            "Gangwon (Gangneung) — đậu phụ mềm Chodang",
            "Jeju (Jeju) — thịt heo đen Korean BBQ",
            "Chungcheong (Daejeon) — kalguksu",
        ],
        "listOutro": "Ăn tại nhà hàng địa phương hoặc mua dạng ăn liền, nước sốt, quà lưu niệm — đều được du khách yêu thích.",
    },
    "th": {
        "specialtyLead": "แต่ละภูมิภาคและเมืองมีอาหารขึ้นชื่อ",
        "specialty1": "เกาหลีมีอาหารประจำภูมิภาคที่ชัดเจน ใช้รายการด้านล่างเป็นแนวทางเมื่อไปแต่ละพื้นที่ — ชิมที่ร้านท้องถิ่นหรือซื้อของฝาก",
        "specialty2": "สนามบิน สถานีรถไฟ ตลาด และร้านท่องเที่ยวมักมีมุมของฝากประจำภูมิภาค ตรวจวันหมดอายุและกฎนำขึ้นเครื่องก่อนซื้อ",
        "listTitle": "อาหารขึ้นชื่อตามภูมิภาค",
        "listIntro": "เมื่อไปพื้นที่เหล่านี้ ให้อ้างอิงรายการด้านล่าง:",
        "items": [
            "Gyeongin (Incheon) — ปูหมักซีอิ๊ว (ganjang gejang)",
            "Gyeongsang (Busan) — ซุปข้าวหมู (dwaeji gukbap)",
            "Gyeongin (Incheon) — jajangmyeon (บะหมี่ถั่วดำ)",
            "Gyeongsang (Daegu) — ไก่ทอด",
            "Gyeongin (Suwon) — wang galbi (ซี่โครง)",
            "Gyeongsang (Andong) — ไก่ตุม Andong",
            "Gyeongin (Uijeongbu) — budae jjigae (สตูว์ทหาร)",
            "Jeolla (Jeonju) — bibimbap Jeonju",
            "Gangwon (Chuncheon) — dakgalbi",
            "Jeolla (Damyang) — tteokgalbi",
            "Gangwon (Hoengseong) — เนื้อ Hanwoo Korean BBQ",
            "Jeolla (Gwangju) — yukjeon (แพนเค้กเนื้อ)",
            "Gangwon (Gangneung) — เต้าหู้นุ่ม Chodang",
            "Jeju (Jeju) — หมูดำ Korean BBQ",
            "Chungcheong (Daejeon) — kalguksu",
        ],
        "listOutro": "ชิมที่ร้านท้องถิ่นหรือซื้อแบบพร้อมทาน ซอส และของที่ระลึก — นักท่องเที่ยวนิยมทั้งสองแบบ",
    },
    "ru": {
        "specialtyLead": "В каждом регионе и городе есть знаменитые блюда",
        "specialty1": "В Корее у каждого региона и города есть узнаваемые блюда. Используйте список ниже при поездке — попробуйте на месте или ищите деликатесы и сувениры.",
        "specialty2": "В аэропортах, на вокзалах, рынках и в туристических магазинах часто есть уголки региональных деликатесов. Проверяйте срок годности и правила провоза.",
        "listTitle": "Региональные блюда",
        "listIntro": "Посещая эти места, ориентируйтесь на список:",
        "items": [
            "Кёнин (Инчхон) — ganjang gejang (краб в соевом соусе)",
            "Кёнsan (Пusan) — dwaeji gukbap (суп с рисом и свининой)",
            "Кёнин (Инчхон) — jajangmyeon (лапша с чёрной фасолью)",
            "Кёнsan (Тэгу) — жареная курица",
            "Кёнин (Сувон) — van galbi (королевские рёбрышки)",
            "Кёнsan (Андон) — тушёная курица Андон",
            "Кёнин (Ыйджонбу) — budae jjigae (армейское рагу)",
            "Чolla (Чонju) — bibimbap Чонju",
            "Канwon (Чхунчхон) — takgalbi",
            "Чolla (Тamyang) — tteokgalbi",
            "Канwon (Hvanseong) — говядина hanwoo Korean BBQ",
            "Чolla (Kvanju) — yukchon (блинчики с говядиной)",
            "Канwon (Kvanneung) — мягкий тофу Chodang",
            "Чеджу (Чеджу) — чёрная свинина Korean BBQ",
            "Чунчхon (Тэджон) — kalguksu",
        ],
        "listOutro": "Попробуйте в местных ресторанах или купите готовые продукты, соусы и сувениры — оба варианта популярны у путешественников.",
    },
}


def format_list_block(lang: str) -> str:
    c = CONTENT[lang]
    lines = [c["listTitle"], "", c["listIntro"], ""]
    lines.extend("· " + item for item in c["items"])
    lines.extend(["", c["listOutro"]])
    return "\n".join(lines)


def specialty_body(lang: str) -> list:
    c = CONTENT[lang]
    intro = c["specialty1"] + "\n\n" + format_list_block(lang)
    return [
        {"type": "image", "src": MAP_SRC},
        {
            "type": "text",
            **{l: (intro if l == lang else format_list_block(l) if l != lang else intro) for l in LANGS},
        },
        {
            "type": "text",
            **{l: CONTENT[l]["specialty2"] for l in LANGS},
        },
    ]


def build_multilang_list_block() -> dict:
    block: dict = {"type": "text"}
    for lang in LANGS:
        c = CONTENT[lang]
        block[lang] = c["specialty1"] + "\n\n" + format_list_block(lang)
    return block


def main() -> None:
    list_block = build_multilang_list_block()
    for lang in LANGS:
        path = SHOPPING_DIR / f"{lang}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        s = data["shopping"]
        c = CONTENT[lang]
        s["specialtyLead"] = c["specialtyLead"]
        s["specialty1"] = c["specialty1"]
        s["specialty2"] = c["specialty2"]
        s["specialtyBody"] = [
            {"type": "image", "src": MAP_SRC},
            list_block,
            {"type": "text", **{l: CONTENT[l]["specialty2"] for l in LANGS}},
        ]
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("patched", lang)
    print("done")


if __name__ == "__main__":
    main()
