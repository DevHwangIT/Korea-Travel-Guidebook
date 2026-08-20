#!/usr/bin/env python3
"""Survey image note + korean catStore + shopping specialty (Aug 20 batch 2)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANGS = ("ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru")
KOREAN_DIR = ROOT / "i18n" / "pages" / "korean"
SHOPPING_DIR = ROOT / "i18n" / "pages" / "shopping"
TIPS_DIR = ROOT / "i18n" / "pages" / "travel-tips"

CAT_STORE = {
    "ko": "편의점·다이소",
    "en": "Convenience & Daiso",
    "ja": "コンビニ・ダイソー",
    "zh": "便利店·大创",
    "zh-Hant": "便利商店·大創",
    "vi": "Tiện lợi & Daiso",
    "th": "ร้านสะดวกซื้อ·ไดโซะ",
    "ru": "Магазины и Daiso",
}

SPECIALTY = {
    "ko": {
        "tabSpecialty": "지역 특산품",
        "catShoppingIntro": "올리브영·다이소·면세·시장·지역 특산품 팁을 이 안에서 바로 확인하세요. (별도 페이지 이동 없음)",
        "specialtyTitle": "지역 특산품",
        "specialtyLead": "여행지마다 유명한 먹거리·특산품이 다릅니다",
        "specialty1": "서울·경기 — 김·한과·인사동 공예 / 부산·경남 — 어묵·굴비·돼지국밥 국물팩 / 제주 — 감귤·흑돼지·한라봉 / 전라 — 떡·전·고추장 / 강원 — 감자·오징어 / 충청 — 인삼·약과 등 지역마다 대표 특산품이 있습니다.",
        "specialty2": "공항·기차역·전통시장·관광지 매장에는 ‘○○ 특산품’ 코너가 있는 경우가 많습니다. 먹거리는 유통기한과 기내 반입 규정을 확인한 뒤, 지역 정보를 참고해 쇼핑을 즐겨 보세요.",
        "specialtyBodyText": "한국은 지역마다 대표 먹거리와 특산품이 뚜렷합니다. 서울·경기(김·한과), 부산·경남(어묵·굴비), 제주(감귤·흑돼지), 전라(떡·고추장), 강원(감자·오징어), 충청(인삼·약과)처럼 여행지별로 유명한 것이 다릅니다.\n\n공항·기차역·시장·관광지 매장의 ‘지역 특산품’ 코너를 찾아보세요. 식품은 유통기한·보관 방법·기내 반입 규정을 꼭 확인하세요.",
    },
    "en": {
        "tabSpecialty": "Regional specialties",
        "catShoppingIntro": "Olive Young, Daiso, duty-free, markets, and regional specialties — all in one place.",
        "specialtyTitle": "Regional specialties",
        "specialtyLead": "Each region has famous foods and local products",
        "specialty1": "Seoul/Gyeonggi — seaweed, hangwa sweets / Busan/Gyeongnam — fish cake, dried croaker, gukbap broth packs / Jeju — citrus, black pork / Jeolla — rice cakes, gochujang / Gangwon — potatoes, squid / Chungcheong — ginseng, yakgwa, etc.",
        "specialty2": "Airports, train stations, markets, and tourist shops often have a ‘local specialty’ corner. Check expiry dates and carry-on rules for food, then shop with regional guides in mind.",
        "specialtyBodyText": "Korea has distinct specialties by region — seaweed and hangwa around Seoul, fish cake and croaker in Busan, citrus on Jeju, rice cakes and gochujang in Jeolla, and more.\n\nLook for ‘regional specialty’ corners at airports, stations, and markets. For food, check expiry, storage, and carry-on rules before you buy.",
    },
    "ja": {
        "tabSpecialty": "地域特産品",
        "catShoppingIntro": "オリーブヤング・ダイソー・免税・市場・地域特産のヒントをここで確認。",
        "specialtyTitle": "地域特産品",
        "specialtyLead": "旅行先ごとに名物・特産品が違います",
        "specialty1": "ソウル・京畿 — 海苔・韓菓 / 釜山・慶南 — おでん・干しコロダイ・スープパック / 済州 — みかん・黒豚 / 全羅 — 餅・コチュジャン / 江原 — じゃがいも・イカ / 忠清 — 人参・薬菓 など。",
        "specialty2": "空港・駅・市場・観光地店舗には「○○特産」コーナーがあることが多いです。食品は賞味期限と機内持ち込みを確認して、地域情報を参考に買い物を楽しみましょう。",
        "specialtyBodyText": "韓国は地域ごとに名物・特産品がはっきりしています。ソウル（海苔・韓菓）、釜山（おでん・干物）、済州（みかん・黒豚）、全羅（餅・コチュジャン）など。\n\n空港・駅・市場の「地域特産」コーナーを探してみてください。食品は期限・保存・機内持ち込みを確認を。",
    },
    "zh": {
        "tabSpecialty": "地区特产",
        "catShoppingIntro": "在此查看 Olive Young、大创、免税、市场与地区特产提示。",
        "specialtyTitle": "地区特产",
        "specialtyLead": "每个旅行目的地都有不同的名产",
        "specialty1": "首尔·京畿 — 海苔·韩果 / 釜山·庆南 — 鱼糕·干黄花鱼·汤饭料包 / 济州 — 柑橘·黑猪 / 全罗 — 年糕·辣椒酱 / 江原 — 土豆·鱿鱼 / 忠清 — 人参·药果 等。",
        "specialty2": "机场、火车站、传统市场和景区商店常有“○○特产”专区。食品请注意保质期和登机规定，参考地区信息享受购物。",
        "specialtyBodyText": "韩国各地区代表特产不同：首尔（海苔·韩果）、釜山（鱼糕·干鱼）、济州（柑橘·黑猪）、全罗（年糕·辣椒酱）等。\n\n可在机场、车站、市场寻找“地区特产”专区。购买食品前请确认保质期、保存方式与登机规定。",
    },
    "zh-Hant": {
        "tabSpecialty": "地區特產",
        "catShoppingIntro": "在此查看 Olive Young、大創、免稅、市場與地區特產提示。",
        "specialtyTitle": "地區特產",
        "specialtyLead": "每個旅行目的地都有不同的名產",
        "specialty1": "首爾·京畿 — 海苔·韓果 / 釜山·慶南 — 魚糕·干黃花魚·湯飯料包 / 濟州 — 柑橘·黑豬 / 全羅 — 年糕·辣椒醬 / 江原 — 馬鈴薯·魷魚 / 忠清 — 人參·藥果 等。",
        "specialty2": "機場、火車站、傳統市場和景區商店常有「○○特產」專區。食品請注意保存期限和登機規定，參考地區資訊享受購物。",
        "specialtyBodyText": "韓國各地區代表特產不同：首爾（海苔·韓果）、釜山（魚糕·乾魚）、濟州（柑橘·黑豬）、全羅（年糕·辣椒醬）等。\n\n可在機場、車站、市場尋找「地區特產」專區。購買食品前請確認保存期限、保存方式與登機規定。",
    },
    "vi": {
        "tabSpecialty": "Đặc sản vùng",
        "catShoppingIntro": "Olive Young, Daiso, miễn thuế, chợ và đặc sản vùng — xem ngay tại đây.",
        "specialtyTitle": "Đặc sản vùng",
        "specialtyLead": "Mỗi vùng có món ăn và sản phẩm đặc trưng riêng",
        "specialty1": "Seoul/Gyeonggi — rong biển, bánh hangwa / Busan/Gyeongnam — chả cá, cá khô, gói nước canh / Jeju — quýt, heo đen / Jeolla — bánh gạo, gochujang / Gangwon — khoai tây, mực / Chungcheong — nhân sâm, yakgwa…",
        "specialty2": "Sân bay, ga tàu, chợ và cửa hàng du lịch thường có góc ‘đặc sản địa phương’. Kiểm tra hạn dùng và quy định mang lên máy bay trước khi mua.",
        "specialtyBodyText": "Hàn Quốc có đặc sản khác nhau theo vùng — rong biển ở Seoul, chả cá ở Busan, quýt ở Jeju, bánh gạo ở Jeolla…\n\nTìm góc ‘đặc sản vùng’ ở sân bay, ga và chợ. Với thực phẩm, kiểm tra hạn dùng và quy định mang lên máy bay.",
    },
    "th": {
        "tabSpecialty": "ของฝากประจำภูมิภาค",
        "catShoppingIntro": "Olive Young, ไดโซะ,  duty-free, ตลาด และของฝากประจำภูมิภาค — ดูได้ที่นี่",
        "specialtyTitle": "ของฝากประจำภูมิภาค",
        "specialtyLead": "แต่ละพื้นที่มีอาหารและของฝากที่โด่งดังต่างกัน",
        "specialty1": "โซล/คยองกี — สาหร่าย ขนมเกาหลี / ปusan/คยองนam — ลูกชิ้นปลา ปลาแห้ง ซุปสำเร็จรูป / เชju — ส้ม หมูดำ / จอlla — เค้กข้าว โกชูจัง / กangwon — มันฝรั่ง ปลาหมึก / ชungcheong — โสม ยakgwa ฯลฯ",
        "specialty2": "สนามบิน สถานีรถไฟ ตลาด และร้านท่องเที่ยวมักมีมุม ‘ของฝากท้องถิ่น’ ตรวจวันหมดอายุและกฎนำขึ้นเครื่องก่อนซื้อ",
        "specialtyBodyText": "เกาหลีมีของฝากเด่นตามภูมิภาค — สาหร่ายที่โซล ลูกชิ้นปลาที่ปusan ส้มที่เชju เค้กข้าวที่จeolla ฯลฯ\n\nมองหามุม ‘ของฝากประจำภูมิภาค’ ที่สนามบิน สถานี และตลาด สำหรับอาหาร ตรวจวันหมดอายุและกฎนำขึ้นเครื่อง",
    },
    "ru": {
        "tabSpecialty": "Региональные деликатесы",
        "catShoppingIntro": "Olive Young, Daiso, duty-free, рынки и региональные деликатесы — всё здесь.",
        "specialtyTitle": "Региональные деликатесы",
        "specialtyLead": "В каждом регионе свои знаменитые продукты",
        "specialty1": "Сеул/Кёнги — водоросли, hangwa / Пusan/Кёнnam — рыбные котлеты, сушёная рыба / Чеджу — мандарины, чёрная свинина / Чолла — рисовые пирожки, gochujang / Канwon — картофель, кальмар / Чунчхон — женьшень, yakgwa и т. д.",
        "specialty2": "В аэропортах, на вокзалах, рынках и в туристических магазинах часто есть уголок «местные деликатесы». Проверяйте срок годности и правила провоза еды.",
        "specialtyBodyText": "В Корее у каждого региона свои деликатесы — водоросли в Сеуле, рыбные котлеты в Пusanе, мандарины на Чеджу, рисовые пирожки в Чолла…\n\nИщите уголки «региональных деликатесов» в аэропортах, на вокзалах и рынках. Для еды проверяйте срок годности и правила провоза.",
    },
}

BODY_LANGS = ("ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru")
MAP_SRC = "Images/shopping/regional-specialty-map.jpg"


def specialty_body_block() -> list:
    text_block: dict = {"type": "text"}
    for lang in BODY_LANGS:
        text_block[lang] = SPECIALTY[lang]["specialtyBodyText"]
    return [
        {"type": "image", "src": MAP_SRC},
        text_block,
        {
            "type": "text",
            "ko": SPECIALTY["ko"]["specialty2"],
            "en": SPECIALTY["en"]["specialty2"],
            "ja": SPECIALTY["ja"]["specialty2"],
            "zh": SPECIALTY["zh"]["specialty2"],
            "zh-Hant": SPECIALTY["zh-Hant"]["specialty2"],
            "vi": SPECIALTY["vi"]["specialty2"],
            "th": SPECIALTY["th"]["specialty2"],
            "ru": SPECIALTY["ru"]["specialty2"],
        },
    ]


def patch_korean() -> None:
    for lang in LANGS:
        path = KOREAN_DIR / f"{lang}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["korean"]["catStore"] = CAT_STORE[lang]
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("korean", lang)


def patch_shopping() -> None:
    body = specialty_body_block()
    for lang in LANGS:
        path = SHOPPING_DIR / f"{lang}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        s = data["shopping"]
        p = SPECIALTY[lang]
        s["specialtyTitle"] = p["specialtyTitle"]
        s["specialtyLead"] = p["specialtyLead"]
        s["specialty1"] = p["specialty1"]
        s["specialty2"] = p["specialty2"]
        s["specialtyBody"] = body
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("shopping", lang)


def patch_travel_tips() -> None:
    for lang in LANGS:
        path = TIPS_DIR / f"{lang}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        tips = data["tips"]
        p = SPECIALTY[lang]
        tips["tabSpecialty"] = p["tabSpecialty"]
        tips["catShoppingIntro"] = p["catShoppingIntro"]
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("tips", lang)


def main() -> None:
    patch_korean()
    patch_shopping()
    patch_travel_tips()
    print("done")


if __name__ == "__main__":
    main()
