# -*- coding: utf-8 -*-
"""Update travel-courses region labels and quiz options."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIR = ROOT / "i18n" / "pages" / "travel-courses"

LABELS = {
    "ko": {
        "regionGyeonggi": "경기도",
        "regionGangwon": "강원도",
        "regionChungcheong": "충청도",
        "regionJeolla": "전라도",
        "regionGyeongsang": "경상도",
        "options": {
            "seoul": "서울",
            "incheon": "인천",
            "gyeonggi": "경기도",
            "gangwon": "강원도",
            "chungcheong": "충청도",
            "jeolla": "전라도",
            "gyeongsang": "경상도",
            "busan": "부산",
            "jeju": "제주도",
        },
        "hints": {
            "seoul": "궁궐·한옥·한강과 트렌디한 거리가 한곳에",
            "incheon": "송도·차이나타운, 공항 접근이 편한 곳",
            "gyeonggi": "수원·민속촌 등 서울에서 가까운 근교",
            "gangwon": "설악산·강릉·속초처럼 산과 동해가 있는 곳",
            "chungcheong": "공주·부여 백제 유적과 서해 해변",
            "jeolla": "전주 한옥마을·여수·보성 녹차밭",
            "gyeongsang": "경주·안동 하회·통영 등 영남 일대",
            "busan": "해운대·감천·자갈치의 바다 도시",
            "jeju": "오름·해변·한라산이 있는 섬 여행",
        },
        "gyeonggi_pick": "경기도 추천 코스",
        "gyeonggi_eye": "경기도 코스 안내",
    },
    "en": {
        "regionGyeonggi": "Gyeonggi",
        "regionGangwon": "Gangwon",
        "regionChungcheong": "Chungcheong",
        "regionJeolla": "Jeolla",
        "regionGyeongsang": "Gyeongsang",
        "options": {
            "seoul": "Seoul",
            "incheon": "Incheon",
            "gyeonggi": "Gyeonggi",
            "gangwon": "Gangwon",
            "chungcheong": "Chungcheong",
            "jeolla": "Jeolla",
            "gyeongsang": "Gyeongsang",
            "busan": "Busan",
            "jeju": "Jeju Island",
        },
        "hints": {
            "seoul": "Palaces, hanok, the Hangang, and trendy streets in one city",
            "incheon": "Songdo, Chinatown, and handy airport access",
            "gyeonggi": "Suwon, folk villages, and easy Seoul day trips",
            "gangwon": "Seoraksan, Gangneung, and the East Sea",
            "chungcheong": "Baekje sites in Gongju and Buyeo, plus west-coast beaches",
            "jeolla": "Jeonju hanok village, Yeosu, and Boseong tea fields",
            "gyeongsang": "Gyeongju, Andong Hahoe, Tongyeong, and more of Yeongnam",
            "busan": "Haeundae, Gamcheon, and Jagalchi by the sea",
            "jeju": "Oreum, beaches, and Hallasan on an island trip",
        },
        "gyeonggi_pick": "Gyeonggi curated courses",
        "gyeonggi_eye": "Gyeonggi course guide",
    },
    "ja": {
        "regionGyeonggi": "京畿道",
        "regionGangwon": "江原道",
        "regionChungcheong": "忠清道",
        "regionJeolla": "全羅道",
        "regionGyeongsang": "慶尚道",
        "options": {
            "seoul": "ソウル",
            "incheon": "仁川",
            "gyeonggi": "京畿道",
            "gangwon": "江原道",
            "chungcheong": "忠清道",
            "jeolla": "全羅道",
            "gyeongsang": "慶尚道",
            "busan": "釜山",
            "jeju": "済州島",
        },
        "hints": {
            "seoul": "宮殿・韓屋・漢江とトレンドの街がひとつに",
            "incheon": "松島・中華街、空港アクセスも便利",
            "gyeonggi": "水原や民俗村など、ソウル近郊",
            "gangwon": "雪岳山・江陵・束草など山と東海岸",
            "chungcheong": "公州・扶余の百済遺跡と西海岸",
            "jeolla": "全州韓屋村・麗水・宝城茶畑",
            "gyeongsang": "慶州・安東河回・統営など嶺南",
            "busan": "海雲台・甘川・チャガルチの海の街",
            "jeju": "オルム・ビーチ・漢拏山の島旅",
        },
        "gyeonggi_pick": "京畿道のおすすめコース",
        "gyeonggi_eye": "京畿道コース案内",
    },
    "zh": {
        "regionGyeonggi": "京畿道",
        "regionGangwon": "江原道",
        "regionChungcheong": "忠清道",
        "regionJeolla": "全罗道",
        "regionGyeongsang": "庆尚道",
        "options": {
            "seoul": "首尔",
            "incheon": "仁川",
            "gyeonggi": "京畿道",
            "gangwon": "江原道",
            "chungcheong": "忠清道",
            "jeolla": "全罗道",
            "gyeongsang": "庆尚道",
            "busan": "釜山",
            "jeju": "济州岛",
        },
        "hints": {
            "seoul": "宫殿、韩屋、汉江与潮流街区集于一城",
            "incheon": "松岛、唐人街，去机场也方便",
            "gyeonggi": "水原、民俗村等首尔近郊",
            "gangwon": "雪岳山、江陵、束草，山海兼备",
            "chungcheong": "公州、扶余百济遗迹与西海岸",
            "jeolla": "全州韩屋村、丽水、宝城茶园",
            "gyeongsang": "庆州、安东河回、统营等岭南",
            "busan": "海云台、甘川、札嘎其的海滨城市",
            "jeju": "火山丘、海滩、汉拿山的海岛之旅",
        },
        "gyeonggi_pick": "京畿道推荐路线",
        "gyeonggi_eye": "京畿道路线指南",
    },
    "zh-Hant": {
        "regionGyeonggi": "京畿道",
        "regionGangwon": "江原道",
        "regionChungcheong": "忠清道",
        "regionJeolla": "全羅道",
        "regionGyeongsang": "慶尚道",
        "options": {
            "seoul": "首爾",
            "incheon": "仁川",
            "gyeonggi": "京畿道",
            "gangwon": "江原道",
            "chungcheong": "忠清道",
            "jeolla": "全羅道",
            "gyeongsang": "慶尚道",
            "busan": "釜山",
            "jeju": "濟州島",
        },
        "hints": {
            "seoul": "宮殿、韓屋、漢江與潮流街區集於一城",
            "incheon": "松島、唐人街，去機場也方便",
            "gyeonggi": "水原、民俗村等首爾近郊",
            "gangwon": "雪嶽山、江陵、束草，山海兼備",
            "chungcheong": "公州、扶餘百濟遺跡與西海岸",
            "jeolla": "全州韓屋村、麗水、寶城茶園",
            "gyeongsang": "慶州、安東河回、統營等嶺南",
            "busan": "海雲台、甘川、札嘎其的海濱城市",
            "jeju": "火山丘、海灘、漢拏山的海島之旅",
        },
        "gyeonggi_pick": "京畿道推薦路線",
        "gyeonggi_eye": "京畿道路線指南",
    },
    "vi": {
        "regionGyeonggi": "Gyeonggi",
        "regionGangwon": "Gangwon",
        "regionChungcheong": "Chungcheong",
        "regionJeolla": "Jeolla",
        "regionGyeongsang": "Gyeongsang",
        "options": {
            "seoul": "Seoul",
            "incheon": "Incheon",
            "gyeonggi": "Gyeonggi",
            "gangwon": "Gangwon",
            "chungcheong": "Chungcheong",
            "jeolla": "Jeolla",
            "gyeongsang": "Gyeongsang",
            "busan": "Busan",
            "jeju": "Jeju",
        },
        "hints": {
            "seoul": "Cung điện, hanok, sông Hàn và phố trendy trong một thành phố",
            "incheon": "Songdo, phố Trung Hoa, gần sân bay",
            "gyeonggi": "Suwon, làng dân tộc, gần Seoul",
            "gangwon": "Seoraksan, Gangneung, Sokcho — núi và biển Đông",
            "chungcheong": "Di tích Baekje Gongju–Buyeo và bãi biển phía tây",
            "jeolla": "Làng hanok Jeonju, Yeosu, đồi chè Boseong",
            "gyeongsang": "Gyeongju, Hahoe Andong, Tongyeong thuộc Yeongnam",
            "busan": "Haeundae, Gamcheon, Jagalchi bên biển",
            "jeju": "Oreum, bãi biển, Hallasan trên đảo",
        },
        "gyeonggi_pick": "Tour Gyeonggi chọn lọc",
        "gyeonggi_eye": "Hướng dẫn tour Gyeonggi",
    },
    "th": {
        "regionGyeonggi": "คยองกี",
        "regionGangwon": "คังวอน",
        "regionChungcheong": "ชุงชอง",
        "regionJeolla": "ชอลลา",
        "regionGyeongsang": "คยองซัง",
        "options": {
            "seoul": "โซล",
            "incheon": "อินชอน",
            "gyeonggi": "คยองกี",
            "gangwon": "คังวอน",
            "chungcheong": "ชุงชอง",
            "jeolla": "ชอลลา",
            "gyeongsang": "คยองซัง",
            "busan": "ปูซาน",
            "jeju": "เชจู",
        },
        "hints": {
            "seoul": "พระราชวัง ฮันอก แม่น้ำฮัน และย่านฮิปในเมืองเดียว",
            "incheon": "ซองโด ไชน่าทาวน์ ใกล้สนามบิน",
            "gyeonggi": "ซูวอน หมู่บ้านพื้นบ้าน ใกล้โซล",
            "gangwon": "ซอรัคซาน คังนึง ซ็อกโช — ภูเขาและทะเลตะวันออก",
            "chungcheong": "โบราณสถานแพกเจคงจู–บูยอ และชายฝั่งตะวันตก",
            "jeolla": "หมู่บ้านฮันอกชอนจู ยอซู สวนชาโบซอง",
            "gyeongsang": "คยองจู ฮาฮเวอันดง ทงยอง ในยองนัม",
            "busan": "แฮอุนแด คัมชอน ชากัลชี เมืองทะเล",
            "jeju": "โอรึม ชายหาด ฮัลลาซาน ทริปเกาะ",
        },
        "gyeonggi_pick": "คอร์สคยองกีแนะนำ",
        "gyeonggi_eye": "คู่มือคอร์สคยองกี",
    },
    "ru": {
        "regionGyeonggi": "Кёнги",
        "regionGangwon": "Канвон",
        "regionChungcheong": "Чхунчхон",
        "regionJeolla": "Чолла",
        "regionGyeongsang": "Кёнсан",
        "options": {
            "seoul": "Сеул",
            "incheon": "Инчхон",
            "gyeonggi": "Кёнги",
            "gangwon": "Канвон",
            "chungcheong": "Чхунчхон",
            "jeolla": "Чолла",
            "gyeongsang": "Кёнсан",
            "busan": "Пусан",
            "jeju": "Чеджу",
        },
        "hints": {
            "seoul": "Дворцы, ханок, Ханган и модные улицы в одном городе",
            "incheon": "Сондо, Чайна-таун, удобно до аэропорта",
            "gyeonggi": "Сувон, фольклорные деревни, рядом с Сеулом",
            "gangwon": "Сораксан, Каннын, Сокчхо — горы и Восточное море",
            "chungcheong": "Паекче в Конджу и Пуё, западное побережье",
            "jeolla": "Хан ок Чонджу, Йосу, чайные поля Посона",
            "gyeongsang": "Кёнджу, Хахве в Андоне, Тхонъён — Ённам",
            "busan": "Хэундэ, Камчхон, Чагальчхи — город у моря",
            "jeju": "Орым, пляжи и Халласан — островная поездка",
        },
        "gyeonggi_pick": "Курсы Кёнги",
        "gyeonggi_eye": "Гид по курсам Кёнги",
    },
}

OPTION_ORDER = [
    "seoul",
    "incheon",
    "gyeonggi",
    "gangwon",
    "chungcheong",
    "jeolla",
    "gyeongsang",
    "busan",
    "jeju",
]


def ordered(src: dict, keys: list[str]) -> dict:
    return {k: src[k] for k in keys}


def main() -> None:
    for lang, pack in LABELS.items():
        path = DIR / f"{lang}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        tc = data["travelCourses"]
        tc["regionGyeonggi"] = pack["regionGyeonggi"]
        tc["regionGangwon"] = pack["regionGangwon"]
        tc["regionChungcheong"] = pack["regionChungcheong"]
        tc["regionJeolla"] = pack["regionJeolla"]
        tc["regionGyeongsang"] = pack["regionGyeongsang"]

        # Keep region keys in a stable block after regionPickLabel.
        region_keys = [
            "regionPickLabel",
            "regionSeoul",
            "regionIncheon",
            "regionGyeonggi",
            "regionGangwon",
            "regionChungcheong",
            "regionJeolla",
            "regionGyeongsang",
            "regionBusan",
            "regionJeju",
            "regionGyeongju",
            "regionComingSoon",
            "scheduleComingSoon",
        ]
        rebuilt = {}
        for key, value in tc.items():
            if key == "regionPickLabel":
                for rk in region_keys:
                    if rk in tc:
                        rebuilt[rk] = tc[rk]
                continue
            if key in region_keys:
                continue
            rebuilt[key] = value
        data["travelCourses"] = rebuilt
        tc = data["travelCourses"]

        gg = tc.get("curated", {}).get("gyeonggi")
        if isinstance(gg, dict):
            gg["pickLabel"] = pack["gyeonggi_pick"]
            gg["guideEyebrow"] = pack["gyeonggi_eye"]

        region_q = tc["quiz"]["questions"]["region"]
        region_q["options"] = ordered(pack["options"], OPTION_ORDER)
        region_q["hints"] = ordered(pack["hints"], OPTION_ORDER)

        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print("updated", path.name)


if __name__ == "__main__":
    main()
