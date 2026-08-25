# -*- coding: utf-8 -*-
"""Replace Gyeonggi curated-course copy in i18n/pages/travel-courses/{lang}.json"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LANGS = ["ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru"]

CHROME = {
    "ko": {
        "pickLabel": "경기도 추천 코스",
        "intro": "수원·가평·파주부터 에버랜드, 민속촌, 양평, 광명, 남한산성, 포천, 여주까지 경기도를 하루로 도는 코스입니다. 타이틀을 고르면 소개·동선·시간표가 펼쳐집니다.",
        "guideEyebrow": "경기도 코스 안내",
    },
    "en": {
        "pickLabel": "Gyeonggi curated courses",
        "intro": "Day courses around Gyeonggi—Suwon, Gapyeong, Paju, Everland, the Korean Folk Village, Yangpyeong, Gwangmyeong, Namhansanseong, Pocheon, and Yeoju. Pick a title to see the intro, route, and timetable.",
        "guideEyebrow": "Gyeonggi course guide",
    },
    "ja": {
        "pickLabel": "京畿おすすめコース",
        "intro": "水原・加平・坡州からエバーランド、民俗村、楊平、光明、南漢山城、抱川、驪州まで、京畿を一日で回るコースです。タイトルを選ぶと紹介・動線・時間割が開きます。",
        "guideEyebrow": "京畿コース案内",
    },
    "zh": {
        "pickLabel": "京畿推荐路线",
        "intro": "从水原、加平、坡州到爱宝乐园、民俗村、杨平、光明、南汉山城、抱川、骊州，用一天走完京畿。点标题即可看介绍、动线和时刻表。",
        "guideEyebrow": "京畿路线指南",
    },
    "zh-Hant": {
        "pickLabel": "京畿推薦路線",
        "intro": "從水原、加平、坡州到愛寶樂園、民俗村、楊平、光明、南漢山城、抱川、驪州，用一天走完京畿。點標題即可看介紹、動線和時刻表。",
        "guideEyebrow": "京畿路線指南",
    },
    "vi": {
        "pickLabel": "Tour Gyeonggi đề xuất",
        "intro": "Tour một ngày quanh Gyeonggi: Suwon, Gapyeong, Paju, Everland, Làng dân gian, Yangpyeong, Gwangmyeong, Namhansanseong, Pocheon và Yeoju. Chọn tiêu đề để xem giới thiệu, lộ trình và lịch trình.",
        "guideEyebrow": "Hướng dẫn tour Gyeonggi",
    },
    "th": {
        "pickLabel": "เส้นทางแนะนำคยองกี",
        "intro": "เส้นทางวันเดียวรอบคยองกี ซูวอน กาพยอง พาจู เอเวอร์แลนด์ หมู่บ้านพื้นบ้าน ยังพยอง ควางมยอง นัมฮันซานซอง โพชอน และยอจู เลือกชื่อเพื่อดูแนะนำ เส้นทาง และตารางเวลา",
        "guideEyebrow": "คู่มือเส้นทางคยองกี",
    },
    "ru": {
        "pickLabel": "Рекомендуемые маршруты Кёнги",
        "intro": "Дневные маршруты по Кёнги: Сувон, Капхён, Пхаджу, Эверленд, фольклорная деревня, Янпхён, Кванмён, Намхансансон, Пхочхон и Ёджу. Выберите название — откроются описание, маршрут и расписание.",
        "guideEyebrow": "Гид по маршрутам Кёнги",
    },
}

MOBILITY = {
    "ko": {"transit": "대중교통 추천", "car": "자동차 추천", "mix": "대중교통·차량", "transitShort": "대중교통", "carShort": "차량", "mixShort": "혼합"},
    "en": {"transit": "Best by transit", "car": "Best by car", "mix": "Transit or car", "transitShort": "Transit", "carShort": "Car", "mixShort": "Mixed"},
    "ja": {"transit": "公共交通向け", "car": "車での移動向け", "mix": "公共交通・車", "transitShort": "公共交通", "carShort": "車", "mixShort": "併用"},
    "zh": {"transit": "建议公共交通", "car": "建议自驾", "mix": "公交或自驾", "transitShort": "公交", "carShort": "自驾", "mixShort": "均可"},
    "zh-Hant": {"transit": "建議大眾運輸", "car": "建議自駕", "mix": "大眾運輸或自駕", "transitShort": "大眾運輸", "carShort": "自駕", "mixShort": "均可"},
    "vi": {"transit": "Nên đi tàu/xe buýt", "car": "Nên đi ô tô", "mix": "Tàu hoặc ô tô", "transitShort": "Tàu/xe buýt", "carShort": "Ô tô", "mixShort": "Hỗn hợp"},
    "th": {"transit": "แนะนำรถสาธารณะ", "car": "แนะนำรถยนต์", "mix": "รถสาธารณะหรือรถยนต์", "transitShort": "รถสาธารณะ", "carShort": "รถยนต์", "mixShort": "ผสม"},
    "ru": {"transit": "Удобно на транспорте", "car": "Удобнее на машине", "mix": "Транспорт или авто", "transitShort": "Транспорт", "carShort": "Авто", "mixShort": "Смешанно"},
}

NOTICE_LABEL = {
    "ko": "안내", "en": "Good to know", "ja": "案内", "zh": "提示",
    "zh-Hant": "提示", "vi": "Lưu ý", "th": "ข้อควรรู้", "ru": "Важно",
}


def S(*rows):
    return [{"name": n, "desc": d} for n, d in rows]


def _pack(*, titles, summaries, routes, tips, stops, notice=None):
    out = {}
    for lang in LANGS:
        item = {
            "title": titles[lang],
            "summary": summaries[lang],
            "route": routes[lang],
            "tips": tips[lang],
            "stops": stops[lang],
        }
        if notice:
            item["notice"] = notice[lang]
        out[lang] = item
    return out


COURSES = {
    "c01": _pack(
        titles={
            "ko": "수원 화성·행궁동 코스",
            "en": "Suwon Hwaseong · Haenggung-dong",
            "ja": "水原華城・行宮洞コース",
            "zh": "水原华城·行宫洞路线",
            "zh-Hant": "水原華城·行宮洞路線",
            "vi": "Tour Suwon Hwaseong · Haenggung-dong",
            "th": "เส้นทางซูวอนฮวาซอง·แฮงกุงดง",
            "ru": "Сувон Хвасон и Хэнгундон",
        },
        summaries={
            "ko": "유네스코 수원화성과 화성행궁을 보고, 행궁동·행리단길에서 쉬고, 방화수류정과 화성 야경으로 하루를 닫는 대중교통 친화 코스입니다.",
            "en": "UNESCO Hwaseong and Haenggung, lunch and cafés in Haenggung-dong, then Banghwasuryujeong and fortress lights. Easy by subway and bus.",
            "ja": "世界遺産の華城と行宮を見学し、行宮洞で食事とカフェ、訪華随柳亭と夜の城壁で締める公共交通向きコース。",
            "zh": "世界遗产华城与行宫，行宫洞用餐和咖啡，再到访华随柳亭与城墙夜景。地铁公交都方便。",
            "zh-Hant": "世界遺產華城與行宮，行宮洞用餐和咖啡，再到訪華隨柳亭與城牆夜景。捷運公車都方便。",
            "vi": "Di sản Hwaseong và hành cung, ăn và cà phê ở Haenggung-dong, rồi Banghwasuryujeong và đêm thành. Tàu/bus thuận.",
            "th": "ป้อมฮวาซองมรดกโลกและแฮงกุง กินข้าวคาเฟ่ที่แฮงกุงดง แล้วบังฮวาสุรยูจองกับกำแพงยามค่ำ รถสาธารณะสะดวก",
            "ru": "ЮНЕСКО Хвасон и дворец Хэнгун, обед и кафе в Хэнгундоне, павильон Панхвасурюджон и ночные стены. Удобно на метро и автобусе.",
        },
        routes={
            "ko": "수원화성 → 화성행궁 → 행궁동 → 방화수류정",
            "en": "Hwaseong Fortress → Hwaseong Haenggung → Haenggung-dong → Banghwasuryujeong",
            "ja": "水原華城 → 華城行宮 → 行宮洞 → 訪華随柳亭",
            "zh": "水原华城 → 华城行宫 → 行宫洞 → 访华随柳亭",
            "zh-Hant": "水原華城 → 華城行宮 → 行宮洞 → 訪華隨柳亭",
            "vi": "Hwaseong → Hành cung → Haenggung-dong → Banghwasuryujeong",
            "th": "ฮวาซอง → แฮงกุง → แฮงกุงดง → บังฮวาสุรยูจอง",
            "ru": "Хвасон → Хвасон Хэнгун → Хэнгундон → Панхвасурюджон",
        },
        tips={
            "ko": "성곽은 길어 편한 신발이 필수입니다. 수원역·화성행궁 정류장은 지하철·버스로 이동하기 쉽습니다.",
            "en": "The wall walk is long—wear comfortable shoes. Suwon Station and Haenggung are easy by subway and bus.",
            "ja": "城壁は距離があるので歩きやすい靴を。水原駅・行宮は地下鉄やバスで行きやすいです。",
            "zh": "城墙路程较长，请穿舒适鞋。水原站和行宫地铁、公交都方便。",
            "zh-Hant": "城牆路程較長，請穿舒適鞋。水原站和行宮捷運、公車都方便。",
            "vi": "Đi bộ trên thành khá dài — mang giày êm. Ga Suwon và hành cung thuận tiện bằng tàu/bus.",
            "th": "เดินกำแพงค่อนข้างไกล ใส่รองเท้าสบาย สถานีซูวอนและแฮงกุงไปง่ายด้วยรถไฟฟ้า",
            "ru": "Стены длинные — удобная обувь. Станция Сувон и дворец легко доступны на метро и автобусе.",
        },
        stops={
            "ko": S(("수원화성", "장안문·팔달문 일대 성곽을 걸으며 화성 전체를 조망하세요."), ("화성행궁", "정조의 임시 궁궐. 정전·낙남헌을 천천히 둘러보세요."), ("행궁동 점심", "행궁 앞 골목의 한식·분식으로 든든하게 식사합니다."), ("행리단길", "행궁 동쪽 골목의 카페·소품샵에서 쉬어 갑니다."), ("방화수류정", "북동쪽 각루와 용연. 해 질 녘 풍경이 아름답습니다."), ("수원화성 야경", "조명이 켜진 성곽을 따라 천천히 걸으며 마무리합니다.")),
            "en": S(("Suwon Hwaseong", "Walk the walls around Janganmun and Paldalmun for fortress views."), ("Hwaseong Haenggung", "Jeongjo’s temporary palace—tour the main halls at an easy pace."), ("Haenggung-dong lunch", "Korean meals and snacks in the alleys in front of the palace."), ("Haengnidangil", "Cafés and small shops in the lanes east of the palace."), ("Banghwasuryujeong", "Northeast pavilion and Yongyeon pond; beautiful near sunset."), ("Hwaseong night views", "Finish with a slow walk along the lit fortress walls.")),
            "ja": S(("水原華城", "長安門・八達門周辺の城壁を歩き、華城を見渡しましょう。"), ("華城行宮", "正祖の臨時宮殿。正殿と洛南軒をゆっくり見学。"), ("行宮洞で昼食", "行宮前の路地で韓食や軽食を。"), ("ヘンリダンギル", "行宮東側のカフェと雑貨店で休憩。"), ("訪華随柳亭", "北東の角楼と龍淵。日没前後が美しいです。"), ("水原華城の夜景", "ライトアップされた城壁を歩いて締めくくります。")),
            "zh": S(("水原华城", "沿长安门、八达门一带城墙步行，俯瞰华城。"), ("华城行宫", "正祖的临时宫殿，慢慢参观正殿与洛南轩。"), ("行宫洞午餐", "在行宫前巷弄吃韩餐或小吃。"), ("行里团路", "行宫东侧巷弄的咖啡馆和小店歇脚。"), ("访华随柳亭", "东北角楼与龙渊，黄昏景色很好。"), ("水原华城夜景", "沿着亮灯的城墙散步收尾。")),
            "zh-Hant": S(("水原華城", "沿長安門、八達門一帶城牆步行，俯瞰華城。"), ("華城行宮", "正祖的臨時宮殿，慢慢參觀正殿與洛南軒。"), ("行宮洞午餐", "在行宮前巷弄吃韓餐或小吃。"), ("行里團路", "行宮東側巷弄的咖啡館和小店歇腳。"), ("訪華隨柳亭", "東北角樓與龍淵，黃昏景色很好。"), ("水原華城夜景", "沿著亮燈的城牆散步收尾。")),
            "vi": S(("Suwon Hwaseong", "Đi bộ thành quanh Janganmun và Paldalmun."), ("Hwaseong Haenggung", "Cung tạm của vua Jeongjo, tham quan chậm rãi."), ("Ăn trưa Haenggung-dong", "Cơm Hàn và đồ ăn nhẹ trước hành cung."), ("Haengnidangil", "Nghỉ ở quán cà phê phía đông hành cung."), ("Banghwasuryujeong", "Đình góc đông bắc và hồ Yongyeon, đẹp lúc hoàng hôn."), ("Đêm Hwaseong", "Kết thúc bằng thành được thắp đèn.")),
            "th": S(("ซูวอนฮวาซอง", "เดินกำแพงแถวจังอันมุนและพัลดัลมุน"), ("ฮวาซองแฮงกุง", "วังชั่วคราวของพระเจ้าจองโจ"), ("อาหารเที่ยงแฮงกุงดง", "อาหารเกาหลีในตรอกหน้าวัง"), ("แฮงนิดันกิล", "พักที่คาเฟ่ฝั่งตะวันออกของวัง"), ("บังฮวาสุรยูจอง", "มุมป้อมและบึงยงยอน สวยตอนเย็น"), ("ฮวาซองยามค่ำ", "เดินกำแพงที่มีไฟส่องปิดทริป")),
            "ru": S(("Сувон Хвасон", "Прогулка по стенам у Чанганмун и Пхальдальмун."), ("Хвасон Хэнгун", "Временный дворец Чонджо — залы не спеша."), ("Обед в Хэнгундоне", "Корейская еда в переулках перед дворцом."), ("Хаэннидангиль", "Кофейни к востоку от дворца."), ("Панхвасурюджон", "Северо-восточный павильон и пруд Ёнъён на закате."), ("Ночной Хвасон", "Прогулка вдоль подсвеченных стен.")),
        },
    ),
    "c02": _pack(
        titles={"ko": "가평 대표 코스", "en": "Gapyeong highlights", "ja": "加平代表コース", "zh": "加平代表路线", "zh-Hant": "加平代表路線", "vi": "Tour Gapyeong tiêu biểu", "th": "เส้นทางหลักกาพยอง", "ru": "Главный маршрут Капхёна"},
        summaries={
            "ko": "남이섬에서 시작해 쁘띠프랑스·이탈리아마을을 보고, 아침고요수목원으로 하루를 마무리하는 가평 차량 코스입니다.",
            "en": "Nami Island, then Petite France and the Italian Village, finishing at the Garden of Morning Calm. A car (or tour van) makes the hops easy.",
            "ja": "南怡島からプチフランス・イタリア村へ、朝静樹木園で締める加平の車向けコース。",
            "zh": "从南怡岛到小法国、意大利村，再以晨静树木园收尾。站点分散，建议自驾。",
            "zh-Hant": "從南怡島到小法國、義大利村，再以晨靜樹木園收尾。站點分散，建議自駕。",
            "vi": "Đảo Nami, Petite France và làng Ý, kết thúc ở Vườn Bình minh. Nên ô tô.",
            "th": "เกาะนามิ แล้วเปอตีฟร็องส์กับหมู่บ้านอิตาลี จบที่สวนเช้าสงบ แนะนำรถยนต์",
            "ru": "Намисом, Петит-Франс и Итальянская деревня, финал в Саду утреннего спокойствия. Удобнее на машине.",
        },
        routes={
            "ko": "남이섬 → 쁘띠프랑스 → 아침고요수목원",
            "en": "Nami Island → Petite France → Garden of Morning Calm",
            "ja": "南怡島 → プチフランス → 朝静樹木園",
            "zh": "南怡岛 → 小法国 → 晨静树木园",
            "zh-Hant": "南怡島 → 小法國 → 晨靜樹木園",
            "vi": "Nami → Petite France → Vườn Bình minh",
            "th": "นามิ → เปอตีฟร็องส์ → สวนเช้าสงบ",
            "ru": "Намисом → Петит-Франс → Сад утреннего спокойствия",
        },
        tips={
            "ko": "남이섬은 선착장 대기 시간을 보세요. 수목원은 계절·폐장 시간을 미리 확인하세요. 대중교통만으로 세 곳을 잇기는 빠듯합니다.",
            "en": "Allow ferry-queue time at Nami. Check seasonal hours for the garden. Linking all three by transit alone is tight.",
            "ja": "南怡島は船着場の待ち時間を見て。樹木園は季節と閉園時刻を確認。公共交通だけで3か所はタイトです。",
            "zh": "南怡岛请预留码头等候。树木园请查季节开放时间。只靠公交串三站会很赶。",
            "zh-Hant": "南怡島請預留碼頭等候。樹木園請查季節開放時間。只靠大眾運輸串三站會很趕。",
            "vi": "Chừa giờ chờ phà Nami. Kiểm tra giờ đóng cửa vườn. Đi tàu/bus cả ba điểm khá gấp.",
            "th": "เผื่อคิวเรือที่นามิ เช็กเวลาปิดสวน รถสาธารณะครบสามที่ค่อนข้างกระชั้น",
            "ru": "Заложите очередь на паром Нами. Уточните часы сада. Три точки одним транспортом — впритык.",
        },
        stops={
            "ko": S(("남이섬", "메타세쿼이아길·자전거·강변 산책로를 여유 있게 걷습니다."), ("점심", "섬 안이나 가평 선착장 근처에서 식사합니다."), ("쁘띠프랑스·이탈리아마을", "유럽풍 세트와 소품 거리를 둘러봅니다."), ("아침고요수목원", "테마 정원과 산책로. 입장 마감 시각을 확인하세요."), ("종료", "수목원에서 하루를 마무리하고 서울·춘천 방면으로 돌아갑니다.")),
            "en": S(("Nami Island", "Metasequoia lane, bikes, and riverside paths at an easy pace."), ("Lunch", "Eat on the island or near the Gapyeong pier."), ("Petite France · Italian Village", "European-style sets and souvenir lanes."), ("Garden of Morning Calm", "Themed gardens and trails—check last entry."), ("Finish", "End at the garden and head back toward Seoul or Chuncheon.")),
            "ja": S(("南怡島", "メタセコイア並木、自転車、川辺の遊歩道をゆっくり。"), ("昼食", "島内か加平の船着場近くで食事。"), ("プチフランス・イタリア村", "欧州風の街並みと雑貨通り。"), ("朝静樹木園", "テーマ庭園と遊歩道。最終入場を確認。"), ("終了", "樹木園で一日を終え、ソウルや春川方面へ。")),
            "zh": S(("南怡岛", "水杉大道、自行车和江边步道，慢慢走。"), ("午餐", "在岛上或加平码头附近用餐。"), ("小法国·意大利村", "欧式布景和纪念品小街。"), ("晨静树木园", "主题花园和步道，请确认最晚入园。"), ("结束", "在树木园收尾，返回首尔或春川方向。")),
            "zh-Hant": S(("南怡島", "水杉大道、自行車和江邊步道，慢慢走。"), ("午餐", "在島上或加平碼頭附近用餐。"), ("小法國·義大利村", "歐式布景和紀念品小街。"), ("晨靜樹木園", "主題花園和步道，請確認最晚入園。"), ("結束", "在樹木園收尾，返回首爾或春川方向。")),
            "vi": S(("Đảo Nami", "Hàng metasequoia, xe đạp, đường ven sông."), ("Ăn trưa", "Trên đảo hoặc gần bến Gapyeong."), ("Petite France · làng Ý", "Phố kiểu Âu và quà lưu niệm."), ("Vườn Bình minh", "Vườn chủ đề — kiểm tra giờ vào cuối."), ("Kết thúc", "Tan ở vườn, về Seoul hoặc Chuncheon.")),
            "th": S(("เกาะนามิ", "ถนนเมทาซีควอเอีย จักรยาน ทางเดินริมน้ำ"), ("อาหารเที่ยง", "บนเกาะหรือใกล้ท่าเรือกาพยอง"), ("เปอตีฟร็องส์·หมู่บ้านอิตาลี", "ฉากยุโรปและถนนของฝาก"), ("สวนเช้าสงบ", "สวนธีม เช็กเวลาเข้าสุดท้าย"), ("สิ้นสุด", "จบที่สวน กลับโซลหรือชุนชอน")),
            "ru": S(("Намисом", "Аллея метасеквойи, велосипеды и береговые тропы."), ("Обед", "На острове или у причала Капхёна."), ("Петит-Франс и Итальянская деревня", "Европейские декорации и сувениры."), ("Сад утреннего спокойствия", "Тематические сады — уточните последний вход."), ("Финиш", "Завершите в саду и возвращайтесь в Сеул или Чхунчхон.")),
        },
    ),
    "c03": _pack(
        titles={"ko": "파주 DMZ 코스", "en": "Paju DMZ course", "ja": "坡州DMZコース", "zh": "坡州非军事区路线", "zh-Hant": "坡州非軍事區路線", "vi": "Tour DMZ Paju", "th": "เส้นทางดีเอ็มซีพาจู", "ru": "DMZ в Пхаджу"},
        summaries={
            "ko": "임진각 평화누리에서 하루를 열고 DMZ 투어를 한 뒤, 오후는 헤이리 예술마을에서 여유롭게 보내는 차량 코스입니다.",
            "en": "Imjingak Peace Nuri, a DMZ tour, then a slower afternoon in Heyri Art Village. A car or reserved tour is the practical way.",
            "ja": "臨津閣平和ヌリからDMZツアーへ。午後はヘーリ芸術村でゆっくり。車か予約ツアー向き。",
            "zh": "从临津阁和平公园开始，参加非军事区参观，下午在Heyri艺术村放慢节奏。建议自驾或预约团。",
            "zh-Hant": "從臨津閣和平公園開始，參加非軍事區參觀，下午在Heyri藝術村放慢節奏。建議自駕或預約團。",
            "vi": "Imjingak Peace Nuri, tour DMZ, chiều thư thả ở làng nghệ thuật Heyri. Nên ô tô hoặc tour đặt trước.",
            "th": "อิมจินกัก สวนสันติภาพ แล้วทัวร์ดีเอ็มซี บ่ายที่หมู่บ้านศิลปะเฮยรี แนะนำรถยนต์หรือทัวร์จอง",
            "ru": "Имджинкак, тур по DMZ, затем спокойный вечер в художественной деревне Хейри. Удобнее машина или готовый тур.",
        },
        routes={
            "ko": "임진각 → DMZ → 헤이리 예술마을",
            "en": "Imjingak → DMZ → Heyri Art Village",
            "ja": "臨津閣 → DMZ → ヘーリ芸術村",
            "zh": "临津阁 → 非军事区 → Heyri艺术村",
            "zh-Hant": "臨津閣 → 非軍事區 → Heyri藝術村",
            "vi": "Imjingak → DMZ → Làng nghệ thuật Heyri",
            "th": "อิมจินกัก → ดีเอ็มซี → หมู่บ้านศิลปะเฮยรี",
            "ru": "Имджинкак → DMZ → Хейри",
        },
        tips={
            "ko": "DMZ 시설은 여권·신분증과 사전 예약이 보통 필요합니다. 당일 현장 구매는 막힐 수 있어요. 복장은 편한 운동화가 좋습니다.",
            "en": "DMZ sites usually need a passport and advance booking. Walk-up tickets can sell out. Wear comfortable shoes.",
            "ja": "DMZ施設はパスポートと事前予約が基本。当日窓口は満席のことも。歩きやすい靴を。",
            "zh": "非军事区设施通常要护照和预约。当天窗口可能买不到。请穿舒适鞋。",
            "zh-Hant": "非軍事區設施通常要護照和預約。當天窗口可能買不到。請穿舒適鞋。",
            "vi": "Điểm DMZ thường cần hộ chiếu và đặt trước. Vé cửa có thể hết. Mang giày êm.",
            "th": "จุดดีเอ็มซีมักต้องพาสปอร์ตและจองล่วงหน้า ตั๋วหน้างานอาจหมด ใส่รองเท้าสบาย",
            "ru": "Объекты DMZ обычно требуют паспорт и бронь. Билетов на месте может не быть. Удобная обувь.",
        },
        notice={
            "ko": "DMZ 관련 시설은 사전 예약·신분증·출입 조건이 수시로 달라집니다. 방문 전에 경기관광공사와 해당 시설 안내를 확인하세요.",
            "en": "DMZ sites change reservation, ID, and entry rules often. Check Gyeonggi Tourism and the site itself before you go.",
            "ja": "DMZ関連施設は予約・身分証・入場条件が変わります。行く前に京畿観光公社と施設案内を確認してください。",
            "zh": "非军事区相关设施的预约、证件和入场条件经常变动。出发前请核对京畿观光公社及该设施公告。",
            "zh-Hant": "非軍事區相關設施的預約、證件和入場條件經常變動。出發前請核對京畿觀光公社及該設施公告。",
            "vi": "Cơ sở DMZ thường đổi quy định đặt chỗ, giấy tờ và ra vào. Kiểm tra Gyeonggi Tourism và thông báo của điểm trước khi đi.",
            "th": "สถานที่ในดีเอ็มซีเปลี่ยนกฎจอง บัตรประชาชน และเงื่อนไขเข้าบ่อย ตรวจการท่องเที่ยวคยองกีและประกาศของสถานที่ก่อนไป",
            "ru": "Правила брони, документов и входа на объекты DMZ часто меняются. Перед поездкой сверьте Tourism Gyeonggi и объявления площадки.",
        },
        stops={
            "ko": S(("임진각 평화누리", "평화의다리·리본·공원에서 분단과 평화를 먼저 느낍니다."), ("DMZ 투어", "도라전망대·제3땅굴 등 당일 코스. 가이드 투어를 따르는 편이 안전합니다."), ("점심", "임진각 관광지 식당이나 파주 시내에서 식사합니다."), ("헤이리 예술마을", "갤러리·공방·산책로가 이어진 예술 마을을 거닙니다."), ("카페", "헤이리의 카페에서 천천히 쉽니다."), ("종료", "해가 지기 전에 서울 방면으로 돌아갑니다.")),
            "en": S(("Imjingak Peace Nuri", "Freedom Bridge, prayer ribbons, and the park—start with the border story."), ("DMZ tour", "Dora Observatory, the Third Tunnel, and the day’s circuit. A guided tour is the safer option."), ("Lunch", "Eat at Imjingak or in Paju town."), ("Heyri Art Village", "Galleries, studios, and walking paths."), ("Café", "A slow café stop in Heyri."), ("Finish", "Head back toward Seoul before dark.")),
            "ja": S(("臨津閣平和ヌリ", "平和の橋、リボン、公園で分断と平和に触れる。"), ("DMZツアー", "都羅展望台・第3トンネルなど。ガイドツアーが安心。"), ("昼食", "臨津閣か坡州市街で食事。"), ("ヘーリ芸術村", "ギャラリー、工房、遊歩道を歩く。"), ("カフェ", "ヘーリのカフェでゆっくり。"), ("終了", "暗くなる前にソウル方面へ。")),
            "zh": S(("临津阁和平公园", "先在自由之桥、许愿丝带和公园感受边界与和平。"), ("非军事区参观", "都罗展望台、第三地道等当日线路。跟团更稳妥。"), ("午餐", "在临津阁景区或坡州市区用餐。"), ("Heyri艺术村", "走画廊、工坊和步道。"), ("咖啡", "在Heyri的咖啡馆慢慢歇脚。"), ("结束", "天黑前返回首尔方向。")),
            "zh-Hant": S(("臨津閣和平公園", "先在自由之橋、許願絲帶和公園感受邊界與和平。"), ("非軍事區參觀", "都羅展望臺、第三地道等當日路線。跟團更穩妥。"), ("午餐", "在臨津閣景區或坡州市區用餐。"), ("Heyri藝術村", "走畫廊、工坊和步道。"), ("咖啡", "在Heyri的咖啡館慢慢歇腳。"), ("結束", "天黑前返回首爾方向。")),
            "vi": S(("Imjingak Peace Nuri", "Cầu Tự do, ruy băng và công viên — câu chuyện biên giới."), ("Tour DMZ", "Đài Dora, Đường hầm 3. Nên đi tour có hướng dẫn."), ("Ăn trưa", "Ở Imjingak hoặc thị trấn Paju."), ("Làng nghệ thuật Heyri", "Gallery, xưởng, lối đi bộ."), ("Café", "Nghỉ chậm ở quán cà phê Heyri."), ("Kết thúc", "Về phía Seoul trước tối.")),
            "th": S(("อิมจินกัก สวนสันติภาพ", "สะพานเสรีภาพ ริบบิ้น และสวน เริ่มด้วยเรื่องชายแดน"), ("ทัวร์ดีเอ็มซี", "ดาดฟ้าโดรา อุโมงค์ที่ 3 ควรตามทัวร์ไกด์"), ("อาหารเที่ยง", "ที่อิมจินกักหรือตัวเมืองพาจู"), ("หมู่บ้านศิลปะเฮยรี", "แกลเลอรี เวิร์กช็อป ทางเดิน"), ("คาเฟ่", "พักช้าที่คาเฟ่ในเฮยรี"), ("สิ้นสุด", "กลับโซลก่อนมืด")),
            "ru": S(("Имджинкак Peace Nuri", "Мост свободы, ленты и парк — история границы."), ("Тур по DMZ", "Обсерватория Дора, 3-й туннель. Надёжнее с гидом."), ("Обед", "В Имджинкаке или в городе Пхаджу."), ("Художественная деревня Хейри", "Галереи, мастерские, тропы."), ("Кафе", "Медленная остановка в Хейри."), ("Финиш", "Обратно к Сеулу до темноты.")),
        },
    ),
    "c04": _pack(
        titles={"ko": "에버랜드 코스", "en": "Everland day", "ja": "エバーランドコース", "zh": "爱宝乐园路线", "zh-Hant": "愛寶樂園路線", "vi": "Tour Everland", "th": "เส้นทางเอเวอร์แลนด์", "ru": "День в Эверленде"},
        summaries={
            "ko": "에버랜드 하루 집중 코스입니다. 사파리·놀이기구·정원에 이어 저녁과 퍼레이드·야간 콘텐츠까지 공원 안에서 해결합니다.",
            "en": "A full day inside Everland: safari and rides, gardens, dinner, then the parade and night shows—no extra destinations.",
            "ja": "エバーランドに一日集中。サファリと乗り物、庭園、夕食、パレードと夜のコンテンツまで園内で完結。",
            "zh": "爱宝乐园一整天：野生动物世界、游乐设施、花园，晚餐后再看花车与夜间节目。不出园。",
            "zh-Hant": "愛寶樂園一整天：野生動物世界、遊樂設施、花園，晚餐後再看花車與夜間節目。不出園。",
            "vi": "Cả ngày trong Everland: safari, trò chơi, vườn, tối rồi diễu hành và show đêm.",
            "th": "ทั้งวันที่เอเวอร์แลนด์ ซาฟารี เครื่องเล่น สวน อาหารเย็น แล้วขบวนพาเหรดกับโชว์กลางคืน",
            "ru": "Весь день в Эверленде: сафари и аттракционы, сады, ужин, парад и ночные шоу.",
        },
        routes={
            "ko": "에버랜드 하루 집중",
            "en": "Everland — full park day",
            "ja": "エバーランド一日集中",
            "zh": "爱宝乐园一日集中",
            "zh-Hant": "愛寶樂園一日集中",
            "vi": "Cả ngày tại Everland",
            "th": "ทั้งวันที่เอเวอร์แลนด์",
            "ru": "Целый день в Эверленде",
        },
        tips={
            "ko": "주말·성수기는 오픈과 동시에 입장하세요. 퍼레이드 시간은 시즌마다 다릅니다. 용인 에버라인·셔틀·자가용이 모두 가능합니다.",
            "en": "On weekends, arrive at opening. Parade times change by season. Everline, shuttles, or a car all work.",
            "ja": "週末は開園と同時に入場を。パレード時刻は季節で変わります。エバーライン、シャトル、車いずれも可。",
            "zh": "周末请开园即入。花车时间随季节变化。爱宝线、接驳车或自驾都可以。",
            "zh-Hant": "週末請開園即入。花車時間隨季節變化。愛寶線、接駁車或自駕都可以。",
            "vi": "Cuối tuần vào lúc mở cửa. Giờ diễu hành đổi theo mùa. Everline, shuttle hoặc ô tô đều được.",
            "th": "วันหยุดเข้าตอนเปิดสวน เวลาขบวนพาเหรดเปลี่ยนตามฤดู เอเวอร์ไลน์ รถรับส่ง หรือรถยนต์ได้หมด",
            "ru": "В выходные приходите к открытию. Время парада меняется. Подойдут Everline, шаттл или машина.",
        },
        stops={
            "ko": S(("에버랜드 입장", "개장에 맞춰 들어가 동선과 대기 시간을 먼저 확인합니다."), ("점심", "가든 푸드코스나 테마 식당에서 식사합니다."), ("사파리·놀이기구", "사파리월드와 대표 어트랙션을 오후에 몰아 탑니다."), ("정원·어트랙션", "포시즌스 가든과 남은 놀이기구를 둘러봅니다."), ("저녁", "원 안에서 저녁을 먹고 야간 좌석을 잡습니다."), ("퍼레이드·야간 콘텐츠", "시즌 퍼레이드와 조명·쇼로 하루를 닫습니다.")),
            "en": S(("Enter Everland", "Arrive at opening and check wait times and a walking loop."), ("Lunch", "Garden food court or a themed restaurant."), ("Safari & rides", "Safari World and headline attractions in the afternoon."), ("Gardens & more rides", "Four Seasons Garden and anything you skipped."), ("Dinner", "Eat in the park and claim a night-show spot."), ("Parade & night shows", "Seasonal parade, lights, and closing entertainment.")),
            "ja": S(("エバーランド入場", "開園に合わせて入り、待ち時間と動線を確認。"), ("昼食", "ガーデンのフードコートかテーマレストランで。"), ("サファリ・乗り物", "午後にサファリワールドと代表アトラクション。"), ("庭園・アトラクション", "フォーシーズンズガーデンと残りの乗り物。"), ("夕食", "園内で夕食を取り、夜間の場所を確保。"), ("パレード・夜間コンテンツ", "季節のパレードと照明・ショーで締めくくり。")),
            "zh": S(("爱宝乐园入园", "开园入场，先看排队时间和动线。"), ("午餐", "花园美食区或主题餐厅。"), ("野生动物世界·游乐设施", "下午集中玩野生动物世界和热门项目。"), ("花园·其他设施", "四季花园和剩下的游乐项目。"), ("晚餐", "在园内吃晚饭，占好夜间位置。"), ("花车·夜间节目", "看当季花车、灯光和演出收尾。")),
            "zh-Hant": S(("愛寶樂園入園", "開園入場，先看排隊時間和動線。"), ("午餐", "花園美食區或主題餐廳。"), ("野生動物世界·遊樂設施", "下午集中玩野生動物世界和熱門項目。"), ("花園·其他設施", "四季花園和剩下的遊樂項目。"), ("晚餐", "在園內吃晚飯，占好夜間位置。"), ("花車·夜間節目", "看當季花車、燈光和演出收尾。")),
            "vi": S(("Vào Everland", "Vào lúc mở cửa, xem thời gian chờ và lộ trình."), ("Ăn trưa", "Food court vườn hoặc nhà hàng chủ đề."), ("Safari · trò chơi", "Safari World và trò nổi bật buổi chiều."), ("Vườn · attraction", "Four Seasons Garden và trò còn lại."), ("Bữa tối", "Ăn trong công viên, giữ chỗ show đêm."), ("Diễu hành · nội dung đêm", "Parad mùa, đèn và show kết thúc.")),
            "th": S(("เข้าเอเวอร์แลนด์", "เข้าตอนเปิดสวน ดูคิวและเส้นทาง"), ("อาหารเที่ยง", "ฟู้ดคอร์ทสวนหรือร้านธีม"), ("ซาฟารี·เครื่องเล่น", "ซาฟารีเวิลด์และเครื่องเล่นเด่นช่วงบ่าย"), ("สวน·เครื่องเล่นต่อ", "สวนโฟร์ซีซันส์และเครื่องเล่นที่เหลือ"), ("อาหารเย็น", "กินในสวน จองที่โชว์กลางคืน"), ("ขบวนพาเหรด·โชว์กลางคืน", "ขบวนตามฤดู ไฟ และโชว์ปิดวัน")),
            "ru": S(("Вход в Эверленд", "К открытию: очереди и маршрут по парку."), ("Обед", "Фудкорт у садов или тематический ресторан."), ("Сафари и аттракционы", "Safari World и главные горки днём."), ("Сады и ещё аттракционы", "Four Seasons Garden и оставшиеся очереди."), ("Ужин", "Ужин в парке и место на ночное шоу."), ("Парад и ночь", "Сезонный парад, подсветка и финальные шоу.")),
        },
    ),
    "c05": _pack(
        titles={"ko": "한국민속촌 코스", "en": "Korean Folk Village course", "ja": "韓国民俗村コース", "zh": "韩国民俗村路线", "zh-Hant": "韓國民俗村路線", "vi": "Tour Làng dân gian Hàn Quốc", "th": "เส้นทางหมู่บ้านพื้นบ้านเกาหลี", "ru": "Корейская фольклорная деревня"},
        summaries={
            "ko": "한국민속촌에서 전통 가옥·공연·체험을 보고, 해 질 녘 보정동 카페거리에서 쉬는 용인 코스입니다.",
            "en": "Traditional houses, shows, and crafts at the Korean Folk Village, then Bojeong café street in the evening.",
            "ja": "韓国民俗村で伝統家屋・公演・体験のあと、夕方は補正洞カフェ通りで休憩。",
            "zh": "在韩国民俗村看传统房屋、演出和体验，傍晚到校正洞咖啡街歇脚。",
            "zh-Hant": "在韓國民俗村看傳統房屋、演出和體驗，傍晚到校正洞咖啡街歇腳。",
            "vi": "Nhà cổ, biểu diễn và trải nghiệm ở Làng dân gian, tối ở phố cà phê Bojeong.",
            "th": "บ้านโบราณ การแสดง และเวิร์กช็อปที่หมู่บ้านพื้นบ้าน เย็นที่ถนนคาเฟ่โบจอง",
            "ru": "Дома, представления и мастер-классы в фольклорной деревне, вечером кафе-улица Поджондон.",
        },
        routes={
            "ko": "한국민속촌 → 보정동 카페거리",
            "en": "Korean Folk Village → Bojeong café street",
            "ja": "韓国民俗村 → 補正洞カフェ通り",
            "zh": "韩国民俗村 → 校正洞咖啡街",
            "zh-Hant": "韓國民俗村 → 校正洞咖啡街",
            "vi": "Làng dân gian → Phố cà phê Bojeong",
            "th": "หมู่บ้านพื้นบ้าน → ถนนคาเฟ่โบจอง",
            "ru": "Фольклорная деревня → кафе-улица Поджондон",
        },
        tips={
            "ko": "민속촌은 반나절 이상 여유 있게. 공연 시간표를 입구에서 확인하세요. 보정동은 분당선 죽전·보정 역에서 가깝습니다.",
            "en": "Give the village at least half a day. Check the performance board at the gate. Bojeong is near Jukjeon and Bojeong on the Bundang Line.",
            "ja": "民俗村は半日以上。公演時刻は入口で確認。補正洞は盆唐線竹田・補正駅が近いです。",
            "zh": "民俗村至少留半天。在门口看演出时刻表。校正洞靠近盆唐线竹田、校正站。",
            "zh-Hant": "民俗村至少留半天。在門口看演出時刻表。校正洞靠近盆唐線竹田、校正站。",
            "vi": "Dành ít nhất nửa ngày. Xem lịch diễn ở cổng. Bojeong gần ga Jukjeon và Bojeong tuyến Bundang.",
            "th": "เผื่ออย่างน้อยครึ่งวันที่หมู่บ้าน ดูตารางการแสดงที่ทางเข้า โบจองใกล้สถานีจุกจอนและโบจองสายบุนดัง",
            "ru": "Заложите минимум полдня. Расписание шоу — у входа. Поджондон рядом со станциями Чукчон и Поджон линии Пундан.",
        },
        stops={
            "ko": S(("한국민속촌", "조선 시대 마을을 재현한 야외 박물관. 가옥과 장터부터 둘러보세요."), ("점심", "민속촌 안 식당에서 전통 한식으로 식사합니다."), ("전통공연·체험", "농악·줄타기 등 당일 공연과 공방 체험을 고릅니다."), ("민속촌 관람 종료", "해 지기 전에 퇴장해 보정동으로 이동합니다."), ("보정동 카페거리", "죽전 인근 카페골목에서 디저트와 휴식을."), ("저녁", "보정·죽전 일대에서 저녁을 먹고 마무리합니다.")),
            "en": S(("Korean Folk Village", "An open-air Joseon village—start with houses and the market lane."), ("Lunch", "Traditional Korean meals inside the village."), ("Shows & workshops", "Pick the day’s nongak, tightrope, or craft sessions."), ("Leave the village", "Exit before dusk and move to Bojeong."), ("Bojeong café street", "Dessert and downtime near Jukjeon."), ("Dinner", "Casual dinner around Bojeong or Jukjeon.")),
            "ja": S(("韓国民俗村", "朝鮮時代の村を再現した野外博物館。家屋と市場から。"), ("昼食", "村内の食堂で伝統韓食。"), ("伝統公演・体験", "農楽や綱渡りなど当日の公演と工房体験。"), ("民俗村観覧終了", "暗くなる前に出て補正洞へ。"), ("補正洞カフェ通り", "竹田近くのカフェ通りでデザート。"), ("夕食", "補正・竹田一帯で夕食。")),
            "zh": S(("韩国民俗村", "再现朝鲜时代村落的露天博物馆。先看房屋和集市。"), ("午餐", "在村内餐厅吃传统韩餐。"), ("传统演出·体验", "选当天的农乐、走钢丝或工坊体验。"), ("民俗村参观结束", "天黑前出园，前往校正洞。"), ("校正洞咖啡街", "竹田附近的咖啡巷吃甜点歇脚。"), ("晚餐", "在校正、竹田一带吃晚饭。")),
            "zh-Hant": S(("韓國民俗村", "再現朝鮮時代村落的露天博物館。先看房屋和集市。"), ("午餐", "在村內餐廳吃傳統韓餐。"), ("傳統演出·體驗", "選當天的農樂、走鋼絲或工坊體驗。"), ("民俗村參觀結束", "天黑前出園，前往校正洞。"), ("校正洞咖啡街", "竹田附近的咖啡巷吃甜點歇腳。"), ("晚餐", "在校正、竹田一帶吃晚飯。")),
            "vi": S(("Làng dân gian", "Bảo tàng ngoài trời thời Joseon — nhà và chợ."), ("Ăn trưa", "Cơm Hàn trong làng."), ("Biểu diễn · trải nghiệm", "Nongak, đi dây, hoặc xưởng trong ngày."), ("Rời làng", "Ra trước tối, sang Bojeong."), ("Phố cà phê Bojeong", "Tráng miệng gần Jukjeon."), ("Bữa tối", "Ăn tối quanh Bojeong hoặc Jukjeon.")),
            "th": S(("หมู่บ้านพื้นบ้าน", "พิพิธภัณฑ์กลางแจ้งยุคโชซอน บ้านและตลาด"), ("อาหารเที่ยง", "อาหารเกาหลีในหมู่บ้าน"), ("การแสดง·เวิร์กช็อป", "นงอัก เดินไต่เชือก หรืองานฝีมือของวัน"), ("ออกจากหมู่บ้าน", "ออกก่อนมืด ไปโบจอง"), ("ถนนคาเฟ่โบจอง", "ของหวานใกล้จุกจอน"), ("อาหารเย็น", "กินแถวโบจองหรือจุกจอน")),
            "ru": S(("Фольклорная деревня", "Музей под открытым небом эпохи Чосон — дома и рынок."), ("Обед", "Традиционная кухня внутри деревни."), ("Шоу и мастер-классы", "Нонак, канат или ремёсла дня."), ("Выход из деревни", "До сумерек — в Поджондон."), ("Кафе-улица Поджондон", "Десерт у Чукчона."), ("Ужин", "Ужин в Поджондоне или Чукчоне.")),
        },
    ),
    "c06": _pack(
        titles={"ko": "양평 두물머리 코스", "en": "Yangpyeong Dumulmeori course", "ja": "楊平ドゥムルモリコース", "zh": "杨平两水头路线", "zh-Hant": "楊平兩水頭路線", "vi": "Tour Dumulmeori Yangpyeong", "th": "เส้นทางดูมุลเมอรียังพยอง", "ru": "Тумульмори в Янпхёне"},
        summaries={
            "ko": "두물머리와 세미원을 잇고, 강변 카페와 남한강 산책으로 하루를 닫는 양평 차량 코스입니다.",
            "en": "Dumulmeori and Semiwon, then a riverside café and a Namhangang walk. Spread out—easier by car.",
            "ja": "ドゥムルモリと洗美苑を巡り、川辺のカフェと南漢江散歩で締める楊平の車向けコース。",
            "zh": "两水头与洗美苑，再去江边咖啡馆和南汉江散步。点与点有距离，建议自驾。",
            "zh-Hant": "兩水頭與洗美苑，再去江邊咖啡館和南漢江散步。點與點有距離，建議自駕。",
            "vi": "Dumulmeori và Semiwon, rồi café ven sông và đi bộ Namhangang. Nên ô tô.",
            "th": "ดูมุลเมอรีและเซมิวอน แล้วคาเฟ่ริมน้ำกับเดินนัมฮัน แนะนำรถยนต์",
            "ru": "Тумульмори и Семивон, затем кафе у реки и прогулка по Намхангану. Удобнее на машине.",
        },
        routes={
            "ko": "두물머리 → 세미원 → 양평 카페 → 남한강",
            "en": "Dumulmeori → Semiwon → Yangpyeong café → Namhangang",
            "ja": "ドゥムルモリ → 洗美苑 → 楊平カフェ → 南漢江",
            "zh": "两水头 → 洗美苑 → 杨平咖啡 → 南汉江",
            "zh-Hant": "兩水頭 → 洗美苑 → 楊平咖啡 → 南漢江",
            "vi": "Dumulmeori → Semiwon → Café Yangpyeong → Namhangang",
            "th": "ดูมุลเมอรี → เซมิวอน → คาเฟ่ยังพยอง → นัมฮัน",
            "ru": "Тумульмори → Семивон → кафе Янпхёна → Намханган",
        },
        tips={
            "ko": "두물머리는 주말 오전이 붐빕니다. 세미원 연꽃은 여름이 절정입니다. 강변 카페는 주차가 협소한 곳이 많습니다.",
            "en": "Dumulmeori is busy weekend mornings. Semiwon’s lotus peaks in summer. Riverside cafés often have tight parking.",
            "ja": "ドゥムルモリは週末午前が混みます。洗美苑の蓮は夏が見頃。川辺カフェは駐車場が狭いことが多いです。",
            "zh": "两水头周末上午较挤。洗美苑荷花盛于夏季。江边咖啡馆停车位常常很紧。",
            "zh-Hant": "兩水頭週末上午較擠。洗美苑荷花盛於夏季。江邊咖啡館停車位常常很緊。",
            "vi": "Dumulmeori đông sáng cuối tuần. Sen Semiwon đẹp nhất mùa hè. Café ven sông thường thiếu chỗ đỗ.",
            "th": "ดูมุลเมอรีคนเยอะเช้าวันหยุด บัวเซมิวอนสวยสุดฤดูร้อน คาเฟ่ริมน้ำที่จอดแคบ",
            "ru": "Тумульмори люден в выходные утром. Лотос в Семивоне — летом. У речных кафе мало парковки.",
        },
        stops={
            "ko": S(("두물머리", "북한강과 남한강이 만나는 포구. 사진 포인트와 산책로를 걷습니다."), ("세미원", "연꽃·수생 정원과 산책 데크를 둘러봅니다."), ("점심", "두물머리·세미원 인근 한식당에서 식사합니다."), ("강변 카페", "남한강을 보는 카페에서 여유를 갖습니다."), ("남한강 산책", "강변길을 천천히 걷습니다."), ("종료", "해 지기 전에 서울 방면으로 돌아갑니다.")),
            "en": S(("Dumulmeori", "Where the Bukhangang and Namhangang meet—photo spots and paths."), ("Semiwon", "Lotus ponds, water gardens, and boardwalks."), ("Lunch", "Korean restaurants near Dumulmeori or Semiwon."), ("Riverside café", "A slow coffee with a Namhangang view."), ("Namhangang walk", "An easy stroll along the river."), ("Finish", "Head back toward Seoul before dark.")),
            "ja": S(("ドゥムルモリ", "北漢江と南漢江が合流する浦口。写真スポットと遊歩道。"), ("洗美苑", "蓮と水生庭園、デッキを歩く。"), ("昼食", "ドゥムルモリや洗美苑近くの韓食堂で。"), ("川辺カフェ", "南漢江を望むカフェで休憩。"), ("南漢江散歩", "川辺の道をゆっくり歩く。"), ("終了", "暗くなる前にソウル方面へ。")),
            "zh": S(("两水头", "北汉江与南汉江交汇的码头。拍照点和步道。"), ("洗美苑", "荷花、水生花园和栈道。"), ("午餐", "在两水头或洗美苑附近的韩餐馆用餐。"), ("江边咖啡", "看着南汉江慢慢喝一杯。"), ("南汉江散步", "沿江边路慢慢走。"), ("结束", "天黑前返回首尔方向。")),
            "zh-Hant": S(("兩水頭", "北漢江與南漢江交會的碼頭。拍照點和步道。"), ("洗美苑", "荷花、水生花園和棧道。"), ("午餐", "在兩水頭或洗美苑附近的韓餐館用餐。"), ("江邊咖啡", "看著南漢江慢慢喝一杯。"), ("南漢江散步", "沿江邊路慢慢走。"), ("結束", "天黑前返回首爾方向。")),
            "vi": S(("Dumulmeori", "Nơi Bukhangang gặp Namhangang — điểm ảnh và lối đi."), ("Semiwon", "Đầm sen, vườn nước, lối gỗ."), ("Ăn trưa", "Nhà hàng Hàn gần Dumulmeori hoặc Semiwon."), ("Café ven sông", "Cà phê nhìn Namhangang."), ("Đi bộ Namhangang", "Đi chậm dọc sông."), ("Kết thúc", "Về Seoul trước tối.")),
            "th": S(("ดูมุลเมอรี", "จุดบรรจบบุกฮันกับนัมฮัน จุดถ่ายรูปและทางเดิน"), ("เซมิวอน", "บึงบัว สวนน้ำ และทางไม้"), ("อาหารเที่ยง", "ร้านอาหารเกาหลีใกล้ดูมุลเมอรีหรือเซมิวอน"), ("คาเฟ่ริมน้ำ", "กาแฟชมวิวนัมฮัน"), ("เดินนัมฮัน", "เดินช้าตามริมน้ำ"), ("สิ้นสุด", "กลับโซลก่อนมืด")),
            "ru": S(("Тумульмори", "Слияние Пукхангана и Намхангана — фототочки и тропы."), ("Семивон", "Лотос, водные сады и настилы."), ("Обед", "Корейские кафе у Тумульмори или Семивона."), ("Кафе у реки", "Кофе с видом на Намханган."), ("Прогулка по Намхангану", "Неспешный берег."), ("Финиш", "Обратно к Сеулу до темноты.")),
        },
    ),
    "c07": _pack(
        titles={"ko": "광명동굴 코스", "en": "Gwangmyeong Cave course", "ja": "光明洞窟コース", "zh": "光明洞窟路线", "zh-Hant": "光明洞窟路線", "vi": "Tour hang Gwangmyeong", "th": "เส้นทางถ้ำควางมยอง", "ru": "Пещера Кванмён"},
        summaries={
            "ko": "광명동굴을 보고 광명전통시장과 시내 카페로 이어지는 대중교통 코스입니다.",
            "en": "Gwangmyeong Cave, then the traditional market and downtown cafés. Workable by subway and bus.",
            "ja": "光明洞窟のあと光明伝統市場と市街のカフェへ。公共交通向き。",
            "zh": "光明洞窟之后去光明传统市场和市区咖啡馆。地铁公交可完成。",
            "zh-Hant": "光明洞窟之後去光明傳統市場和市區咖啡館。捷運公車可完成。",
            "vi": "Hang Gwangmyeong, rồi chợ truyền thống và café nội thị. Đi tàu/bus được.",
            "th": "ถ้ำควางมยอง แล้วตลาดดั้งเดิมกับคาเฟ่ในเมือง รถสาธารณะได้",
            "ru": "Пещера Кванмён, затем традиционный рынок и кафе в городе. Удобно на метро и автобусе.",
        },
        routes={
            "ko": "광명동굴 → 광명전통시장 → 광명 시내",
            "en": "Gwangmyeong Cave → Gwangmyeong Traditional Market → downtown",
            "ja": "光明洞窟 → 光明伝統市場 → 光明市街",
            "zh": "光明洞窟 → 光明传统市场 → 光明市区",
            "zh-Hant": "光明洞窟 → 光明傳統市場 → 光明市區",
            "vi": "Hang Gwangmyeong → Chợ truyền thống → Nội thị",
            "th": "ถ้ำควางมยอง → ตลาดดั้งเดิม → ตัวเมือง",
            "ru": "Пещера Кванмён → рынок → центр Кванмёна",
        },
        tips={
            "ko": "동굴은 내부가 서늘하고 바닥이 젖을 수 있습니다. 시장은 철산역이 가깝습니다. 동굴~시장은 버스나 택시로 잇습니다.",
            "en": "The cave is cool and floors can be damp. The market sits near Cheolsan Station. Link cave and market by bus or taxi.",
            "ja": "洞窟内は涼しく床が濡れることも。市場は鉄山駅が近い。洞窟と市場はバスかタクシーで。",
            "zh": "洞内偏凉，地面可能潮湿。市场靠近铁山站。洞窟到市场坐公交或出租车。",
            "zh-Hant": "洞內偏涼，地面可能潮溼。市場靠近鐵山站。洞窟到市場坐公車或計程車。",
            "vi": "Hang mát, nền có thể ướt. Chợ gần ga Cheolsan. Hang–chợ đi bus hoặc taxi.",
            "th": "ในถ้ำเย็น พื้นอาจเปียก ตลาดใกล้สถานีชอลซาน ถ้ำถึงตลาดใช้รถเมล์หรือแท็กซี่",
            "ru": "В пещере прохладно, пол может быть влажным. Рынок у станции Чхольсан. Между пещерой и рынком — автобус или такси.",
        },
        stops={
            "ko": S(("광명동굴", "폐광을 테마파크로 바꾼 동굴. 황금폭포·와인동굴 등을 둘러보세요."), ("점심", "동굴 관광지 식당에서 식사합니다."), ("광명전통시장", "철산 일대 시장에서 먹거리와 생활 골목을 구경합니다."), ("카페", "광명 시내 카페에서 쉽니다."), ("종료", "철산역·광명역에서 서울로 돌아갑니다.")),
            "en": S(("Gwangmyeong Cave", "A former mine turned attraction—Golden Waterfall, wine cellar, and light art."), ("Lunch", "Restaurants at the cave complex."), ("Gwangmyeong Traditional Market", "Food and side streets around Cheolsan."), ("Café", "A downtown Gwangmyeong café."), ("Finish", "Back to Seoul from Cheolsan or Gwangmyeong Station.")),
            "ja": S(("光明洞窟", "廃鉱をテーマパークにした洞窟。黄金の滝やワイン洞窟など。"), ("昼食", "洞窟観光地の食堂で。"), ("光明伝統市場", "鉄山一帯の市場で食べ歩き。"), ("カフェ", "光明市街のカフェで休憩。"), ("終了", "鉄山駅か光明駅からソウルへ。")),
            "zh": S(("光明洞窟", "废矿改成的主题洞穴。黄金瀑布、葡萄酒窖和灯光装置。"), ("午餐", "在洞窟景区餐厅用餐。"), ("光明传统市场", "在铁山一带市场吃小吃、逛巷弄。"), ("咖啡", "在光明市区咖啡馆歇脚。"), ("结束", "从铁山站或光明站返回首尔。")),
            "zh-Hant": S(("光明洞窟", "廢礦改成的主題洞穴。黃金瀑布、葡萄酒窖和燈光裝置。"), ("午餐", "在洞窟景區餐廳用餐。"), ("光明傳統市場", "在鐵山一帶市場吃小吃、逛巷弄。"), ("咖啡", "在光明市區咖啡館歇腳。"), ("結束", "從鐵山站或光明站返回首爾。")),
            "vi": S(("Hang Gwangmyeong", "Mỏ cũ thành điểm tham quan — thác Vàng, hầm rượu, đèn."), ("Ăn trưa", "Nhà hàng khu hang."), ("Chợ truyền thống Gwangmyeong", "Ăn vặt và hẻm quanh Cheolsan."), ("Café", "Quán cà phê nội thị Gwangmyeong."), ("Kết thúc", "Về Seoul từ ga Cheolsan hoặc Gwangmyeong.")),
            "th": S(("ถ้ำควางมยอง", "เหมืองเก่าเป็นสวนสนุก น้ำตกทอง ถ้ำไวน์ ไฟ"), ("อาหารเที่ยง", "ร้านในโซนถ้ำ"), ("ตลาดดั้งเดิมควางมยอง", "ของกินและตรอกแถวชอลซาน"), ("คาเฟ่", "คาเฟ่ในตัวเมืองควางมยอง"), ("สิ้นสุด", "กลับโซลจากสถานีชอลซานหรือควางมยอง")),
            "ru": S(("Пещера Кванмён", "Бывшая шахта: Золотой водопад, винный зал, свет."), ("Обед", "Кафе у пещеры."), ("Традиционный рынок Кванмёна", "Еда и переулки у Чхольсана."), ("Кафе", "Кафе в центре Кванмёна."), ("Финиш", "В Сеул со станции Чхольсан или Кванмён.")),
        },
    ),
    "c08": _pack(
        titles={"ko": "남한산성 코스", "en": "Namhansanseong course", "ja": "南漢山城コース", "zh": "南汉山城路线", "zh-Hant": "南漢山城路線", "vi": "Tour Namhansanseong", "th": "เส้นทางนัมฮันซานซอง", "ru": "Намхансансон"},
        summaries={
            "ko": "세계유산 남한산성 성곽과 산성마을을 걷고 카페로 하루를 닫는 대중교통 코스입니다.",
            "en": "UNESCO fortress walls, a village lunch, more ramparts, then a café. Reachable by bus from Seoul.",
            "ja": "世界遺産の南漢山城の城壁と山城の村を歩き、カフェで締める公共交通コース。",
            "zh": "世界遗产南汉山城走城墙和山城村，再以咖啡馆收尾。从首尔坐公交可到。",
            "zh-Hant": "世界遺產南漢山城走城牆和山城村，再以咖啡館收尾。從首爾坐公車可到。",
            "vi": "Thành UNESCO, làng trong thành, rồi café. Có bus từ Seoul.",
            "th": "กำแพงมรดกโลกและหมู่บ้านในป้อม แล้วคาเฟ่ มีรถเมล์จากโซล",
            "ru": "Стены ЮНЕСКО, деревня в крепости, затем кафе. Есть автобус из Сеула.",
        },
        routes={
            "ko": "남한산성 → 산성마을 → 카페",
            "en": "Namhansanseong → fortress village → café",
            "ja": "南漢山城 → 山城の村 → カフェ",
            "zh": "南汉山城 → 山城村 → 咖啡",
            "zh-Hant": "南漢山城 → 山城村 → 咖啡",
            "vi": "Namhansanseong → Làng thành → Café",
            "th": "นัมฮันซานซอง → หมู่บ้านป้อม → คาเฟ่",
            "ru": "Намхансансон → крепостная деревня → кафе",
        },
        tips={
            "ko": "산성까지는 버스가 있습니다. 성곽은 경사가 있어 편한 신발을 신으세요. 날씨가 흐리면 바람이 셉니다.",
            "en": "Buses reach the fortress. Trails are hilly—wear good shoes. It can be windy when the weather turns.",
            "ja": "山城まではバスあり。傾斜があるので歩きやすい靴を。天候が崩れると風が強いです。",
            "zh": "有公交上山。城墙有坡，请穿舒适鞋。阴天风会很大。",
            "zh-Hant": "有公車上山。城牆有坡，請穿舒適鞋。陰天風會很大。",
            "vi": "Có bus lên thành. Dốc — giày êm. Trời xấu thì gió mạnh.",
            "th": "มีรถเมล์ขึ้นป้อม ทางชัน ใส่รองเท้าสบาย ฟ้าครึ้มลมแรง",
            "ru": "До крепости ходит автобус. Склоны — удобная обувь. В пасмурный день бывает ветрено.",
        },
        stops={
            "ko": S(("남한산성", "세계유산 성곽과 남문 일대를 둘러봅니다."), ("성곽길 산책", "성벽을 따라 천천히 걷고 전망을 봅니다."), ("산성마을 점심", "산채비빔밥 등 산성 식당에서 식사합니다."), ("남한산성 추가 관람", "서문·행궁터 등 남은 구간을 더 걷습니다."), ("카페", "산성 안 카페에서 쉽니다."), ("종료", "버스로 내려와 서울로 돌아갑니다.")),
            "en": S(("Namhansanseong", "UNESCO walls around the south gate."), ("Wall walk", "Follow the ramparts for views."), ("Village lunch", "Mountain-vegetable bibimbap and local restaurants."), ("More fortress", "West gate, the temporary palace site, and leftover stretches."), ("Café", "A café inside the fortress village."), ("Finish", "Bus down and back to Seoul.")),
            "ja": S(("南漢山城", "世界遺産の城壁と南門一帯。"), ("城壁散歩", "城壁に沿って歩き、展望を楽しむ。"), ("山城村で昼食", "山菜ビビンバなど。"), ("南漢山城追加観覧", "西門や行宮跡など残りの区間。"), ("カフェ", "山城の中のカフェで休憩。"), ("終了", "バスで下りてソウルへ。")),
            "zh": S(("南汉山城", "世界遗产城墙与南门一带。"), ("城墙散步", "沿城墙慢慢走，看风景。"), ("山城村午餐", "山菜拌饭等山城餐厅。"), ("南汉山城再走一段", "西门、行宫遗址等剩余路段。"), ("咖啡", "在山城村里的咖啡馆歇脚。"), ("结束", "坐公交下山返回首尔。")),
            "zh-Hant": S(("南漢山城", "世界遺產城牆與南門一帶。"), ("城牆散步", "沿城牆慢慢走，看風景。"), ("山城村午餐", "山菜拌飯等山城餐廳。"), ("南漢山城再走一段", "西門、行宮遺址等剩餘路段。"), ("咖啡", "在山城村裡的咖啡館歇腳。"), ("結束", "坐公車下山返回首爾。")),
            "vi": S(("Namhansanseong", "Thành UNESCO quanh cửa Nam."), ("Đi bộ thành", "Theo tường thành ngắm cảnh."), ("Ăn trưa làng", "Bibimbap rau núi."), ("Tham quan thêm", "Cửa Tây, nền hành cung, đoạn còn lại."), ("Café", "Quán cà phê trong làng thành."), ("Kết thúc", "Bus xuống, về Seoul.")),
            "th": S(("นัมฮันซานซอง", "กำแพงมรดกโลกแถวประตูใต้"), ("เดินกำแพง", "เดินตามกำแพงชมวิว"), ("อาหารเที่ยงหมู่บ้าน", "บิบิมบับผักภูเขา"), ("ชมป้อมต่อ", "ประตูตะวันตก ที่ตั้งวังชั่วคราว และช่วงที่เหลือ"), ("คาเฟ่", "คาเฟ่ในหมู่บ้านป้อม"), ("สิ้นสุด", "รถเมล์ลงเขา กลับโซล")),
            "ru": S(("Намхансансон", "Стены ЮНЕСКО у южных ворот."), ("Прогулка по стенам", "Вдоль валов к видамам."), ("Обед в деревне", "Пибимпап с горными овощами."), ("Ещё крепость", "Западные ворота, место дворца и оставшиеся участки."), ("Кафе", "Кафе в крепостной деревне."), ("Финиш", "Автобус вниз и в Сеул.")),
        },
    ),
    "c09": _pack(
        titles={"ko": "포천 자연 코스", "en": "Pocheon nature course", "ja": "抱川自然コース", "zh": "抱川自然路线", "zh-Hant": "抱川自然路線", "vi": "Tour thiên nhiên Pocheon", "th": "เส้นทางธรรมชาติโพชอน", "ru": "Природа Пхочхона"},
        summaries={
            "ko": "포천아트밸리의 채석장 호수와 산정호수를 잇는 차량 코스입니다.",
            "en": "Pocheon Art Valley’s quarry lake, then Sanjeong Lake for a walk and café. You will want a car.",
            "ja": "抱川アートバレーの採石場の湖から山井湖へ。車が便利です。",
            "zh": "抱川艺术谷采石湖再到山井湖散步喝咖啡。建议自驾。",
            "zh-Hant": "抱川藝術谷採石湖再到山井湖散步喝咖啡。建議自駕。",
            "vi": "Hồ mỏ Pocheon Art Valley rồi hồ Sanjeong đi bộ và cà phê. Nên ô tô.",
            "th": "ทะเลสาบเหมืองอาร์ตวัลเลย์โพชอน แล้วทะเลสาบซันจอง แนะนำรถยนต์",
            "ru": "Карьерное озеро Арт-Вэлли, затем озеро Санджон. Удобнее на машине.",
        },
        routes={
            "ko": "포천아트밸리 → 산정호수",
            "en": "Pocheon Art Valley → Sanjeong Lake",
            "ja": "抱川アートバレー → 山井湖",
            "zh": "抱川艺术谷 → 山井湖",
            "zh-Hant": "抱川藝術谷 → 山井湖",
            "vi": "Pocheon Art Valley → Hồ Sanjeong",
            "th": "อาร์ตวัลเลย์โพชอน → ทะเลสาบซันจอง",
            "ru": "Арт-Вэлли Пхочхона → озеро Санджон",
        },
        tips={
            "ko": "아트밸리는 입장료가 있고 주말 주차가 붐빕니다. 산정호수는 호수 한 바퀴가 꽤 깁니다. 두 곳 사이는 버스가 드뭅니다.",
            "en": "Art Valley charges admission and weekend parking fills up. A full loop of Sanjeong Lake is long. Buses between the two are infrequent.",
            "ja": "アートバレーは入場料があり週末駐車場は混みます。山井湖一周は長め。2か所間のバスは少ないです。",
            "zh": "艺术谷需门票，周末停车较满。山井湖一圈不短。两地之间公交很少。",
            "zh-Hant": "藝術谷需門票，週末停車較滿。山井湖一圈不短。兩地之間公車很少。",
            "vi": "Art Valley có vé, cuối tuần đầy chỗ đỗ. Vòng hồ Sanjeong khá dài. Bus giữa hai nơi thưa.",
            "th": "อาร์ตวัลเลย์มีค่าเข้า ที่จอดวันหยุดเต็ม เดินรอบซันจองค่อนข้างไกล รถเมล์ระหว่างสองที่น้อย",
            "ru": "В Арт-Вэлли вход платный, парковка в выходные занята. Круг Санджона длинный. Автобусов между точками мало.",
        },
        stops={
            "ko": S(("포천아트밸리", "화강암 채석장을 호수로 바꾼 전망대와 조각 공원을 봅니다."), ("점심", "아트밸리 인근에서 식사합니다."), ("산정호수", "명성산을 배경으로 호수를 산책합니다."), ("산책·카페", "호숫가 카페에서 쉬거나 짧게 더 걷습니다."), ("종료", "포천에서 서울 방면으로 돌아갑니다.")),
            "en": S(("Pocheon Art Valley", "A granite quarry turned lake, viewpoints, and sculpture park."), ("Lunch", "Eat near Art Valley."), ("Sanjeong Lake", "Walk the shore with Myeongseongsan behind the water."), ("Walk · café", "A lakeside café or a shorter extra stroll."), ("Finish", "Drive back toward Seoul from Pocheon.")),
            "ja": S(("抱川アートバレー", "花崗岩の採石場を湖にした展望台と彫刻公園。"), ("昼食", "アートバレー近くで食事。"), ("山井湖", "明星山を背景に湖畔を歩く。"), ("散歩・カフェ", "湖畔カフェで休むか、短く歩く。"), ("終了", "抱川からソウル方面へ。")),
            "zh": S(("抱川艺术谷", "花岗岩采石场改成的湖、观景台和雕塑园。"), ("午餐", "在艺术谷附近用餐。"), ("山井湖", "以明星山为背景沿湖散步。"), ("散步·咖啡", "在湖边咖啡馆歇脚，或再走一小段。"), ("结束", "从抱川返回首尔方向。")),
            "zh-Hant": S(("抱川藝術谷", "花崗岩採石場改成的湖、觀景臺和雕塑園。"), ("午餐", "在藝術谷附近用餐。"), ("山井湖", "以明星山為背景沿湖散步。"), ("散步·咖啡", "在湖邊咖啡館歇腳，或再走一小段。"), ("結束", "從抱川返回首爾方向。")),
            "vi": S(("Pocheon Art Valley", "Mỏ granite thành hồ, đài nhìn và công viên tượng."), ("Ăn trưa", "Gần Art Valley."), ("Hồ Sanjeong", "Đi bộ bờ hồ với núi Myeongseong."), ("Đi bộ · café", "Café ven hồ hoặc đi thêm đoạn ngắn."), ("Kết thúc", "Về Seoul từ Pocheon.")),
            "th": S(("อาร์ตวัลเลย์โพชอน", "เหมืองหินแกรนิตเป็นทะเลสาบ จุดชมวิว และสวนประติมากรรม"), ("อาหารเที่ยง", "กินใกล้าร์ตวัลเลย์"), ("ทะเลสาบซันจอง", "เดินริมน้ำพื้นหลังภูเขามยองซอง"), ("เดิน·คาเฟ่", "คาเฟ่ริมทะเลสาบหรือเดินต่อสั้น ๆ"), ("สิ้นสุด", "กลับโซลจากโพชอน")),
            "ru": S(("Арт-Вэлли Пхочхона", "Гранитный карьер-озеро, смотровые и парк скульптур."), ("Обед", "Рядом с Арт-Вэлли."), ("Озеро Санджон", "Прогулка по берегу на фоне Мёнсонсана."), ("Прогулка и кафе", "Кафе у воды или короткий доп. круг."), ("Финиш", "Из Пхочхона обратно к Сеулу.")),
        },
    ),
    "c10": _pack(
        titles={"ko": "여주 역사·쇼핑 코스", "en": "Yeoju history & shopping", "ja": "驪州歴史・ショッピングコース", "zh": "骊州历史·购物路线", "zh-Hant": "驪州歷史·購物路線", "vi": "Tour Yeoju sử và mua sắm", "th": "เส้นทางยอจูประวัติศาสตร์และชอปปิง", "ru": "Ёджу: история и шопинг"},
        summaries={
            "ko": "신륵사와 세종대왕릉을 본 뒤 여주 프리미엄아울렛에서 쇼핑하는 차량 코스입니다.",
            "en": "Silleuksa and King Sejong’s tomb, then Yeoju Premium Outlets. Spread out—easier by car.",
            "ja": "神勒寺と世宗大王陵のあと驪州プレミアムアウトレット。距離があるので車が便利。",
            "zh": "神勒寺、世宗大王陵之后去骊州奥特莱斯。点与点较远，建议自驾。",
            "zh-Hant": "神勒寺、世宗大王陵之後去驪州奧特萊斯。點與點較遠，建議自駕。",
            "vi": "Chùa Silleuk, lăng Sejong, rồi outlet Yeoju. Nên ô tô.",
            "th": "วัดซิลลึก สุสานเซจง แล้วเอาต์เล็ตยอจู แนะนำรถยนต์",
            "ru": "Силлыкса, гробница Седжона и аутлет Ёджу. Удобнее на машине.",
        },
        routes={
            "ko": "신륵사 → 세종대왕릉 → 여주 아울렛",
            "en": "Silleuksa → King Sejong’s tomb → Yeoju Outlet",
            "ja": "神勒寺 → 世宗大王陵 → 驪州アウトレット",
            "zh": "神勒寺 → 世宗大王陵 → 骊州奥特莱斯",
            "zh-Hant": "神勒寺 → 世宗大王陵 → 驪州奧特萊斯",
            "vi": "Silleuksa → Lăng Sejong → Outlet Yeoju",
            "th": "ซิลลึกซา → สุสานเซจง → เอาต์เล็ตยอจู",
            "ru": "Силлыкса → гробница Седжона → аутлет Ёджу",
        },
        tips={
            "ko": "신륵사는 남한강 변에 있어 강변 산책과 잘 맞습니다. 아울렛은 주말 저녁이 붐빕니다.",
            "en": "Silleuksa sits on the Namhangang—pair it with a riverside walk. The outlet gets busy weekend evenings.",
            "ja": "神勒寺は南漢江沿い。アウトレットは週末夕方混みます。",
            "zh": "神勒寺在南汉江边，适合江边散步。奥特莱斯周末傍晚较挤。",
            "zh-Hant": "神勒寺在南漢江邊，適合江邊散步。奧特萊斯週末傍晚較擠。",
            "vi": "Silleuksa sát sông Namhan. Outlet đông tối cuối tuần.",
            "th": "วัดอยู่ริมนัมฮัน เอาต์เล็ตคนเยอะเย็นวันหยุด",
            "ru": "Силлыкса у Намхангана. Аутлет люден в выходные вечером.",
        },
        stops={
            "ko": S(("신륵사", "강변 절과 다층석탑을 둘러봅니다."), ("남한강 산책", "신륵사 앞 강변을 짧게 걷습니다."), ("점심", "신륵사 관광지 식당에서 식사합니다."), ("세종대왕릉", "영릉. 왕릉 숲길을 천천히 걷습니다."), ("여주 프리미엄아울렛", "브랜드 쇼핑과 휴식을 함께합니다."), ("종료", "아울렛에서 하루를 마무리하고 돌아갑니다.")),
            "en": S(("Silleuksa", "Riverside temple and stone pagoda."), ("Namhangang walk", "A short stroll in front of the temple."), ("Lunch", "Restaurants at the temple area."), ("King Sejong’s tomb", "Yeongneung—walk the royal tomb woods."), ("Yeoju Premium Outlets", "Brand shopping and a rest."), ("Finish", "End at the outlet and drive back.")),
            "ja": S(("神勒寺", "川辺の寺と多層石塔。"), ("南漢江散歩", "寺の前の川辺を短く歩く。"), ("昼食", "観光地の食堂で。"), ("世宗大王陵", "英陵。陵の森を歩く。"), ("驪州プレミアムアウトレット", "ブランドショッピング。"), ("終了", "アウトレットで一日を終えて帰宅。")),
            "zh": S(("神勒寺", "江边寺院与多层石塔。"), ("南汉江散步", "寺前江边走一小段。"), ("午餐", "景区餐厅用餐。"), ("世宗大王陵", "英陵，走陵园林道。"), ("骊州奥特莱斯", "品牌购物与休息。"), ("结束", "在奥特莱斯收尾后返回。")),
            "zh-Hant": S(("神勒寺", "江邊寺院與多層石塔。"), ("南漢江散步", "寺前江邊走一小段。"), ("午餐", "景區餐廳用餐。"), ("世宗大王陵", "英陵，走陵園林道。"), ("驪州奧特萊斯", "品牌購物與休息。"), ("結束", "在奧特萊斯收尾後返回。")),
            "vi": S(("Silleuksa", "Chùa ven sông và tháp đá."), ("Đi bộ Namhangang", "Đoạn ngắn trước chùa."), ("Ăn trưa", "Nhà hàng khu chùa."), ("Lăng Sejong", "Yeongneung — đi rừng lăng."), ("Outlet Yeoju", "Mua sắm thương hiệu."), ("Kết thúc", "Tan ở outlet rồi về.")),
            "th": S(("วัดซิลลึกซา", "วัดริมน้ำและเจดีย์หิน"), ("เดินนัมฮัน", "เดินสั้นหน้าวัด"), ("อาหารเที่ยง", "ร้านในโซนวัด"), ("สุสานเซจง", "ยองนึง เดินป่าสุสาน"), ("เอาต์เล็ตยอจู", "ชอปปิงแบรนด์"), ("สิ้นสุด", "จบที่เอาต์เล็ตแล้วกลับ")),
            "ru": S(("Силлыкса", "Храм у реки и каменная пагода."), ("Прогулка по Намхангану", "Коротко у храма."), ("Обед", "Кафе у храма."), ("Гробница Седжона", "Ённын — лес царских могил."), ("Аутлет Ёджу", "Бренды и отдых."), ("Финиш", "Завершите в аутлете и в обратный путь.")),
        },
    ),
}


def build_lang(lang: str) -> dict:
    gyeonggi = dict(CHROME[lang])
    gyeonggi["courses"] = {cid: COURSES[cid][lang] for cid in COURSES}
    return gyeonggi


def main() -> None:
    for lang in LANGS:
        path = ROOT / "i18n" / "pages" / "travel-courses" / f"{lang}.json"
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        curated = data.setdefault("travelCourses", {}).setdefault("curated", {})
        curated["mobility"] = MOBILITY[lang]
        curated["noticeLabel"] = NOTICE_LABEL[lang]
        curated["gyeonggi"] = build_lang(lang)
        with path.open("w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("updated", path.relative_to(ROOT), "courses", len(curated["gyeonggi"]["courses"]))


if __name__ == "__main__":
    main()
