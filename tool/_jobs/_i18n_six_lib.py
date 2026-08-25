# -*- coding: utf-8 -*-
"""Shared helpers for six-region curated i18n injectors."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LANGS = ["ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru"]


def S(*rows):
    return [{"name": n, "desc": d} for n, d in rows]


def pack(*, titles, summaries, routes, tips, stops, notice=None):
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


FEATURED = {
    "ko": ("대표 코스", "더 둘러보기"),
    "en": ("Signature courses", "More day trips"),
    "ja": ("代表コース", "その他のコース"),
    "zh": ("代表路线", "更多一日行程"),
    "zh-Hant": ("代表路線", "更多一日行程"),
    "vi": ("Tour nổi bật", "Thêm tour trong ngày"),
    "th": ("เส้นทางเด่น", "เส้นทางเพิ่มเติม"),
    "ru": ("Главные маршруты", "Ещё маршруты"),
}

CHROME = {
    "gangwon": {
        "ko": ("강원도 추천 코스", "속초·설악부터 강릉 카페거리, 춘천·남이섬, 평창, 양양, 동해·삼척, 철원까지 강원을 하루로 도는 코스입니다. 타이틀을 고르면 소개·동선·시간표가 펼쳐집니다.", "강원도 코스 안내"),
        "en": ("Gangwon curated courses", "Day courses around Gangwon—Seoraksan and Sokcho, Gangneung cafés, Chuncheon and Nami Island, Pyeongchang, Yangyang, Donghae–Samcheok, and Cheorwon. Pick a title to see the intro, route, and timetable.", "Gangwon course guide"),
        "ja": ("江原おすすめコース", "雪岳・束草、江陵カフェ、春川・南怡島、平昌、襄陽、東海・三陟、鉄原まで江原を一日で回るコースです。タイトルを選ぶと紹介・動線・時間割が開きます。", "江原コース案内"),
        "zh": ("江原推荐路线", "从雪岳束草、江陵咖啡、春川南怡岛到平昌、襄阳、东海三陟、铁原，用一天走江原。点标题即可看介绍、动线和时刻表。", "江原路线指南"),
        "zh-Hant": ("江原推薦路線", "從雪嶽束草、江陵咖啡、春川南怡島到平昌、襄陽、東海三陟、鐵原，用一天走江原。點標題即可看介紹、動線和時刻表。", "江原路線指南"),
        "vi": ("Tour Gangwon đề xuất", "Tour một ngày quanh Gangwon: Seoraksan–Sokcho, cà phê Gangneung, Chuncheon–Nami, Pyeongchang, Yangyang, Donghae–Samcheok và Cheorwon. Chọn tiêu đề để xem giới thiệu, lộ trình và lịch.", "Hướng dẫn tour Gangwon"),
        "th": ("เส้นทางแนะนำคังวอน", "เส้นทางวันเดียวรอบคังวอน ซอรักซาน ซกโช คาเฟ่คังนึง ชุนชอน เกาะนามิ พยองชัง ยังยัง ทงแฮ และชอวอน เลือกชื่อเพื่อดูแนะนำ เส้นทาง และตาราง", "คู่มือเส้นทางคังวอน"),
        "ru": ("Рекомендуемые маршруты Канвона", "Дневные маршруты по Канвону: Сораксан и Сокчхо, кафе Каннына, Чхунчхон и Намисом, Пхёнчхан, Янъян, Тонхэ–Самчхок и Чхорвон. Выберите название — откроются описание, маршрут и расписание.", "Гид по маршрутам Канвона"),
    },
    "chungcheong": {
        "ko": ("충청도 추천 코스", "공주·부여 백제, 단양, 보령 대천, 태안 서해, 대전 도심·과학까지 충남·충북·대전을 하루로 도는 코스입니다. 타이틀을 고르면 소개·동선·시간표가 펼쳐집니다.", "충청도 코스 안내"),
        "en": ("Chungcheong curated courses", "Day courses across Chungnam, Chungbuk, and Daejeon—Baekje Gongju and Buyeo, Danyang, Boryeong Daecheon, Taean, and Daejeon science. Pick a title to see the intro, route, and timetable.", "Chungcheong course guide"),
        "ja": ("忠清おすすめコース", "公州・扶余の百済、丹陽、保寧大川、泰安西海、大田の街と科学まで忠清を一日で回るコースです。", "忠清コース案内"),
        "zh": ("忠清推荐路线", "百济公州扶余、丹阳、保宁大川、泰安西海、大田科学，用一天走忠南忠北大田。", "忠清路线指南"),
        "zh-Hant": ("忠清推薦路線", "百濟公州扶餘、丹陽、保寧大川、泰安西海、大田科學，用一天走忠南忠北大田。", "忠清路線指南"),
        "vi": ("Tour Chungcheong đề xuất", "Tour một ngày Gongju–Buyeo Baekje, Danyang, Boryeong, Taean và Daejeon.", "Hướng dẫn tour Chungcheong"),
        "th": ("เส้นทางแนะนำชุงชอง", "เส้นทางวันเดียวกงจู ปูยอ ทันยัง แทชอน แทอัน และแทจอน", "คู่มือเส้นทางชุงชอง"),
        "ru": ("Рекомендуемые маршруты Чхунчхона", "Дневные маршруты: Пэкче Конджу и Пуё, Танъян, Тэчхон, Тхэан и Тэджон.", "Гид по маршрутам Чхунчхона"),
    },
    "jeolla": {
        "ko": ("전라도 추천 코스", "전주 한옥마을, 여수 바다·야경, 순천만, 담양, 보성 녹차, 목포까지 전북·전남을 하루로 도는 코스입니다. 타이틀을 고르면 소개·동선·시간표가 펼쳐집니다.", "전라도 코스 안내"),
        "en": ("Jeolla curated courses", "Day courses across Jeonbuk and Jeonnam—Jeonju Hanok Village, Yeosu nights, Suncheon Bay, Damyang, Boseong tea, and Mokpo. Pick a title to see the intro, route, and timetable.", "Jeolla course guide"),
        "ja": ("全羅おすすめコース", "全州韓屋村、麗水の海と夜景、順天湾、潭陽、宝城茶畑、木浦まで全羅を一日で回るコースです。", "全羅コース案内"),
        "zh": ("全罗推荐路线", "全州韩屋村、丽水夜景、顺天湾、潭阳、宝城茶田、木浦，用一天走全罗。", "全罗路线指南"),
        "zh-Hant": ("全羅推薦路線", "全州韓屋村、麗水夜景、順天灣、潭陽、寶城茶田、木浦，用一天走全羅。", "全羅路線指南"),
        "vi": ("Tour Jeolla đề xuất", "Tour một ngày Jeonju, Yeosu, Suncheon, Damyang, Boseong và Mokpo.", "Hướng dẫn tour Jeolla"),
        "th": ("เส้นทางแนะนำชอลลา", "ชอนจู ยอซู ซุนชอน ทามยัง โพซอง และมกโพ", "คู่มือเส้นทางชอลลา"),
        "ru": ("Рекомендуемые маршруты Чолла", "Дневные маршруты: Чонджу, Йосу, Сунчхон, Тамьян, Посон и Мокпхо.", "Гид по маршрутам Чолла"),
    },
    "gyeongsang": {
        "ko": ("경상도 추천 코스", "경주 신라, 안동 하회, 통영, 거제 외도, 포항, 대구, 울산, 합천 해인사까지 경북·경남·대구·울산을 하루로 도는 코스입니다. 부산은 별도 탭입니다.", "경상도 코스 안내"),
        "en": ("Gyeongsang curated courses", "Day courses across Gyeongbuk, Gyeongnam, Daegu, and Ulsan—Gyeongju, Andong Hahoe, Tongyeong, Geoje Oedo, Pohang, Daegu, Ulsan, and Haeinsa. Busan has its own tab.", "Gyeongsang course guide"),
        "ja": ("慶尚おすすめコース", "慶州、安東河回、統営、巨済外島、浦項、大邱、蔚山、海印寺まで。釜山は別タブです。", "慶尚コース案内"),
        "zh": ("庆尚推荐路线", "庆州、安东河回、统营、巨济外岛、浦项、大邱、蔚山、海印寺。釜山在单独标签。", "庆尚路线指南"),
        "zh-Hant": ("慶尚推薦路線", "慶州、安東河回、統營、巨濟外島、浦項、大邱、蔚山、海印寺。釜山在單獨分頁。", "慶尚路線指南"),
        "vi": ("Tour Gyeongsang đề xuất", "Gyeongju, Andong, Tongyeong, Geoje, Pohang, Daegu, Ulsan và Haeinsa. Busan ở tab riêng.", "Hướng dẫn tour Gyeongsang"),
        "th": ("เส้นทางแนะนำคยองซัง", "คยองจู อันดง ทงยอง คอเจ โพฮัง แทกู อุลซาน และแฮอินซา ปูซานอยู่แท็บแยก", "คู่มือเส้นทางคยองซัง"),
        "ru": ("Рекомендуемые маршруты Кёнсана", "Кёнджу, Андон, Тхонъён, Кодже, Пхохан, Тэгу, Ульсан и Хэинса. Пусан — отдельная вкладка.", "Гид по маршрутам Кёнсана"),
    },
    "busan": {
        "ko": ("부산 추천 코스", "해운대·광안리, 감천·자갈치, 송도·영도, 기장 해동용궁사, 서면·전포까지 부산을 하루로 도는 코스입니다. 타이틀을 고르면 소개·동선·시간표가 펼쳐집니다.", "부산 코스 안내"),
        "en": ("Busan curated courses", "Day courses around Busan—Haeundae and Gwangalli, Gamcheon and Jagalchi, Songdo and Yeongdo, Gijang’s Haedong Yonggungsa, and Seomyeon–Jeonpo. Pick a title to see the intro, route, and timetable.", "Busan course guide"),
        "ja": ("釜山おすすめコース", "海雲台・広安里、甘川・チャガルチ、松島・影島、機張海東龍宮寺、西面・田浦まで釜山を一日で回るコースです。", "釜山コース案内"),
        "zh": ("釜山推荐路线", "海云台广安里、甘川札嘎其、松岛影岛、机张海东龙宫寺、西面田浦，用一天走釜山。", "釜山路线指南"),
        "zh-Hant": ("釜山推薦路線", "海雲臺廣安里、甘川札嘎其、松島影島、機張海東龍宮寺、西面田浦，用一天走釜山。", "釜山路線指南"),
        "vi": ("Tour Busan đề xuất", "Haeundae–Gwangalli, Gamcheon–Jagalchi, Songdo–Yeongdo, Gijang và Seomyeon–Jeonpo.", "Hướng dẫn tour Busan"),
        "th": ("เส้นทางแนะนำปูซาน", "แฮอุนแด คwangอันลี คัมชอน ซงโด คิจัง และซอมยอน", "คู่มือเส้นทางปูซาน"),
        "ru": ("Рекомендуемые маршруты Пусана", "Хэундэ и Кваналлли, Камчхон и Чагальчхи, Сондо и Ёндо, Киджан и Сомён.", "Гид по маршрутам Пусана"),
    },
    "jeju": {
        "ko": ("제주도 추천 코스", "성산·우도, 협재·애월, 서귀포 폭포, 중문, 한라산, 제주시 시장, 동부 오름, 산방산까지 제주를 하루로 도는 코스입니다. 타이틀을 고르면 소개·동선·시간표가 펼쳐집니다.", "제주도 코스 안내"),
        "en": ("Jeju curated courses", "Day courses around Jeju—Seongsan and Udo, Hyeopjae and Aewol, Seogwipo falls, Jungmun, Hallasan, Jeju City markets, eastern oreum, and Sanbangsan. Pick a title to see the intro, route, and timetable.", "Jeju course guide"),
        "ja": ("済州おすすめコース", "城山・牛島、協在・涯月、西帰浦の滝、中文、漢拏山、済州市市場、東のオルム、山房山まで済州を一日で回るコースです。", "済州コース案内"),
        "zh": ("济州推荐路线", "城山牛岛、挟才涯月、西归浦瀑布、中文、汉拿山、济州市市场、东部岳、山房山，用一天走济州。", "济州路线指南"),
        "zh-Hant": ("濟州推薦路線", "城山牛島、挾才涯月、西歸浦瀑布、中文、漢拏山、濟州市市場、東部岳、山房山，用一天走濟州。", "濟州路線指南"),
        "vi": ("Tour Jeju đề xuất", "Seongsan–Udo, Hyeopjae–Aewol, Seogwipo, Jungmun, Hallasan, chợ Jeju, oreum phía đông và Sanbangsan.", "Hướng dẫn tour Jeju"),
        "th": ("เส้นทางแนะนำเชจู", "ซองซาน อูโด ฮยอบแจ แอวอล ซอกวีโพ ฮัลลาซาน และซันบังซาน", "คู่มือเส้นทางเชจู"),
        "ru": ("Рекомендуемые маршруты Чеджу", "Сонсан и Удо, Хёпчжэ и Эволь, Согвипхо, Чунмун, Халласан, рынки Чеджу, орым на востоке и Санбансан.", "Гид по маршрутам Чеджу"),
    },
}


def chrome_block(region: str, lang: str, courses: dict) -> dict:
    pick, intro, eye = CHROME[region][lang]
    feat, more = FEATURED[lang]
    return {
        "pickLabel": pick,
        "intro": intro,
        "guideEyebrow": eye,
        "featuredLabel": feat,
        "moreLabel": more,
        "courses": {cid: courses[cid][lang] for cid in courses},
    }


def write_regions(region_courses: dict[str, dict]) -> None:
    for lang in LANGS:
        path = ROOT / "i18n" / "pages" / "travel-courses" / f"{lang}.json"
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        curated = data.setdefault("travelCourses", {}).setdefault("curated", {})
        for region, courses in region_courses.items():
            curated[region] = chrome_block(region, lang, courses)
        with path.open("w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("updated", path.name, "regions", ",".join(region_courses))
