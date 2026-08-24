# -*- coding: utf-8 -*-
"""Add beach places (type: beach) from the 해수욕장 filter list.

- Skip 대구 / 없음
- Deduplicate 만성리검은모래해변 (여수·전남)
- Migrate existing nature beaches (haeundae) to type beach
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
COORDS = ROOT / "data" / "places" / "places-coords.js"
IMG = ROOT / "Images" / "places"
LIST_FILE = Path(
    r"C:\Users\HwangInTae\Desktop\guide book\명소 추가할 자료\해수욕장 필터 이름정보.txt"
)

LANGS = ("ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru")

REGION_LABELS = {
    "busan": {
        "ko": "부산",
        "en": "Busan",
        "ja": "釜山",
        "zh": "釜山",
        "zh-Hant": "釜山",
        "vi": "Busan",
        "th": "ปูซาน",
        "ru": "Пусан",
    },
    "incheon": {
        "ko": "인천",
        "en": "Incheon",
        "ja": "仁川",
        "zh": "仁川",
        "zh-Hant": "仁川",
        "vi": "Incheon",
        "th": "อินชอน",
        "ru": "Инчхон",
    },
    "gangwon": {
        "ko": "강원",
        "en": "Gangwon",
        "ja": "江原",
        "zh": "江原",
        "zh-Hant": "江原",
        "vi": "Gangwon",
        "th": "คังวอน",
        "ru": "Канвон",
    },
    "jeolla": {
        "ko": "전라",
        "en": "Jeolla",
        "ja": "全羅",
        "zh": "全罗",
        "zh-Hant": "全羅",
        "vi": "Jeolla",
        "th": "ชอลลา",
        "ru": "Чолла",
    },
    "jeju": {
        "ko": "제주",
        "en": "Jeju",
        "ja": "済州",
        "zh": "济州",
        "zh-Hant": "濟州",
        "vi": "Jeju",
        "th": "เชจู",
        "ru": "Чеджу",
    },
    "gyeongsang": {
        "ko": "경상",
        "en": "Gyeongsang",
        "ja": "慶尚",
        "zh": "庆尚",
        "zh-Hant": "慶尚",
        "vi": "Gyeongsang",
        "th": "คยองซัง",
        "ru": "Кёнсан",
    },
    "chungcheong": {
        "ko": "충청",
        "en": "Chungcheong",
        "ja": "忠清",
        "zh": "忠清",
        "zh-Hant": "忠清",
        "vi": "Chungcheong",
        "th": "ชุงชอง",
        "ru": "Чхунчхон",
    },
}

# Existing place slug that is already the beach — change type only.
MIGRATE = {
    "해운대해수욕장": "haeundae",
}

# Korean name → beach meta (slug, coords, region, maps query, copy)
# Region keys match places-map REGION_VIEWS / existing coords convention.
BEACHES: dict[str, dict] = {
    # —— 부산 ——
    "해운대해수욕장": {
        "slug": "haeundae",
        "lat": 35.1587,
        "lng": 129.1604,
        "region": "busan",
        "maps_q": "해운대해수욕장",
        "migrate": True,
        "ko": {
            "name": "해운대해수욕장",
            "desc": "부산의 대표 해변. 동백섬·달맞이·마린시티와 함께 즐깁니다.",
            "how": "부산도시철도 2호선 해운대역. 해변은 도보 또는 짧은 버스.",
            "address": "부산 해운대구 해운대해변로 해운대해수욕장",
        },
        "en": {
            "name": "Haeundae Beach",
            "desc": "Busan’s famous beach with Dongbaek Island and Marine City nearby.",
            "how": "Busan Metro Line 2 Haeundae Station; short walk or bus to the sand.",
            "address": "Haeundae Beach, Haeundaehaebyeon-ro, Haeundae-gu, Busan",
        },
        "ja": ("海雲台海水浴場", "釜山を代表するビーチ。冬柏島やマリンシティも。", "釜山都市鉄道2号線海雲台駅。徒歩または短いバス。"),
        "zh": ("海云台海水浴场", "釜山代表性海滩。可与冬柏岛、迎月、海洋城一起玩。", "釜山地铁2号线海云台站，步行或短途公交到沙滩。"),
        "zh-Hant": ("海雲台海水浴場", "釜山代表性海灘。可與冬柏島、迎月、海洋城一起玩。", "釜山地鐵2號線海雲台站，步行或短途公車到沙灘。"),
    },
    "광안리해수욕장": {
        "slug": "gwangalli-beach",
        "lat": 35.1532,
        "lng": 129.1186,
        "region": "busan",
        "maps_q": "광안리해수욕장",
        "ko": {
            "name": "광안리해수욕장",
            "desc": "광안대교 야경이 유명한 부산 도심 해변. 카페·포차와 함께 즐기기 좋습니다.",
            "how": "부산 2호선 금련산역·광안역에서 도보 5~10분.",
            "address": "부산 수영구 광안해변로 219",
        },
        "en": {
            "name": "Gwangalli Beach",
            "desc": "City beach famous for Gwangan Bridge night views — cafés and bars along the sand.",
            "how": "Busan Metro Line 2 Geumnyeonsan or Gwangan Station; 5–10 min walk.",
            "address": "219 Gwanganhaebyeon-ro, Suyeong-gu, Busan",
        },
        "ja": ("広安里海水浴場", "広安大橋の夜景で有名な都心ビーチ。", "釜山2号線 金蓮山・広安駅から徒歩5〜10分。"),
        "zh": ("广安里海水浴场", "以广安大桥夜景闻名的釜山市中心海滩。", "釜山2号线金莲山·广安站步行5–10分钟。"),
        "zh-Hant": ("廣安里海水浴場", "以廣安大橋夜景聞名的釜山市中心海灘。", "釜山2號線金蓮山·廣安站步行5–10分鐘。"),
    },
    "송정해수욕장": {
        "slug": "songjeong-beach",
        "lat": 35.1786,
        "lng": 129.1995,
        "region": "busan",
        "maps_q": "송정해수욕장",
        "ko": {
            "name": "송정해수욕장",
            "desc": "해운대 동쪽의 서핑·산책 해변. 송정죽도공원과 이어집니다.",
            "how": "동해선 송정역에서 도보 10분, 또는 해운대에서 버스.",
            "address": "부산 해운대구 송정해변로 62",
        },
        "en": {
            "name": "Songjeong Beach",
            "desc": "Surf-friendly beach east of Haeundae, linked to Songjeong Jukdo Park.",
            "how": "~10 min walk from Donghae Line Songjeong Station, or bus from Haeundae.",
            "address": "62 Songjeonghaebyeon-ro, Haeundae-gu, Busan",
        },
        "ja": ("松亭海水浴場", "海雲台東側のサーフィンビーチ。", "東海線松亭駅から徒歩10分、または海雲台からバス。"),
        "zh": ("松亭海水浴场", "海云台东侧冲浪·散步海滩。", "东海线松亭站步行10分钟，或从海云台乘公交。"),
        "zh-Hant": ("松亭海水浴場", "海雲台東側衝浪·散步海灘。", "東海線松亭站步行10分鐘，或從海雲台乘公車。"),
    },
    "다대포해수욕장": {
        "slug": "dadaepo-beach",
        "lat": 35.0472,
        "lng": 128.9663,
        "region": "busan",
        "maps_q": "다대포해수욕장",
        "ko": {
            "name": "다대포해수욕장",
            "desc": "낙조와 다대포 꿈의 낙조분수로 유명한 서부산 해변.",
            "how": "부산 1호선 다대포해수욕장역에서 도보 5분.",
            "address": "부산 사하구 몰운대1길 14",
        },
        "en": {
            "name": "Dadaepo Beach",
            "desc": "West Busan beach known for sunsets and the Dream Sunset Fountain show.",
            "how": "Busan Metro Line 1 Dadaepo Beach Station; ~5 min walk.",
            "address": "14 Morundae 1-gil, Saha-gu, Busan",
        },
        "ja": ("多大浦海水浴場", "夕日と噴水ショーで有名な西釜山ビーチ。", "釜山1号線 多大浦海水浴場駅から徒歩5分。"),
        "zh": ("多大浦海水浴场", "以日落和梦之落日喷泉闻名的西釜山海滩。", "釜山1号线多大浦海水浴场站步行5分钟。"),
        "zh-Hant": ("多大浦海水浴場", "以日落和夢之落日噴泉聞名的西釜山海灘。", "釜山1號線多大浦海水浴場站步行5分鐘。"),
    },
    "송도해수욕장": {
        "slug": "songdo-beach",
        "lat": 35.0764,
        "lng": 129.0178,
        "region": "busan",
        "maps_q": "부산 송도해수욕장",
        "ko": {
            "name": "송도해수욕장",
            "desc": "부산 남구의 해안 산책·케이블카 명소. 암남공원과 이어집니다. (인천 송도와는 다름)",
            "how": "부산 1호선 토성역에서 버스, 또는 송도해수욕장 정류장 하차.",
            "address": "부산 서구 송도해변로 101",
        },
        "en": {
            "name": "Songdo Beach (Busan)",
            "desc": "Coastal walk and cable-car beach in Busan’s Nam/Seo-gu — not Incheon Songdo.",
            "how": "Bus from Busan Metro Line 1 Toseong Station, or Songdo Beach bus stop.",
            "address": "101 Songdohaebyeon-ro, Seo-gu, Busan",
        },
        "ja": ("松島海水浴場（釜山）", "釜山の海岸散歩・ケーブルカービーチ。仁川松島とは別。", "釜山1号線 土城駅からバス。"),
        "zh": ("松岛海水浴场（釜山）", "釜山海岸散步·缆车景点，与仁川松岛不同。", "釜山1号线土城站转公交。"),
        "zh-Hant": ("松島海水浴場（釜山）", "釜山海岸散步·纜車景點，與仁川松島不同。", "釜山1號線土城站轉公車。"),
    },
    "일광해수욕장": {
        "slug": "ilgwang-beach",
        "lat": 35.2615,
        "lng": 129.2335,
        "region": "busan",
        "maps_q": "일광해수욕장",
        "ko": {
            "name": "일광해수욕장",
            "desc": "기장군의 한적한 동해 해변. 캠핑·일출 명소로 인기입니다.",
            "how": "동해선 일광역에서 도보 10분.",
            "address": "부산 기장군 일광읍 일광해안로 127",
        },
        "en": {
            "name": "Ilgwang Beach",
            "desc": "Quieter East Sea beach in Gijang — camping and sunrise spots.",
            "how": "~10 min walk from Donghae Line Ilgwang Station.",
            "address": "127 Ilgwanghaean-ro, Ilgwang-eup, Gijang-gun, Busan",
        },
        "ja": ("日光海水浴場", "機張の穏やかな東海ビーチ。", "東海線日光駅から徒歩10分。"),
        "zh": ("日光海水浴场", "机张郡较清静的东海海滩。", "东海线日光站步行10分钟。"),
        "zh-Hant": ("日光海水浴場", "機張郡較清靜的東海海灘。", "東海線日光站步行10分鐘。"),
    },
    # —— 인천 ——
    "을왕리해수욕장": {
        "slug": "eulwangni-beach",
        "lat": 37.4475,
        "lng": 126.3725,
        "region": "incheon",
        "maps_q": "을왕리해수욕장",
        "ko": {
            "name": "을왕리해수욕장",
            "desc": "영종도 대표 해변. 공항 접근이 쉽고 카페·맛집 거리가 있습니다.",
            "how": "공항철도·인천1호선 환승 후 버스, 또는 을왕리 방면 시내버스.",
            "address": "인천 중구 용유서로302번길 16-15",
        },
        "en": {
            "name": "Eulwangni Beach",
            "desc": "Yeongjong Island’s main beach — easy from ICN with cafés nearby.",
            "how": "Airport Railroad / Incheon Line transfer then bus toward Eulwangni.",
            "address": "16-15 Yongyuseo-ro 302beon-gil, Jung-gu, Incheon",
        },
        "ja": ("乙旺里海水浴場", "永宗島の代表ビーチ。空港アクセス便利。", "空港鉄道・仁川1号線からバス。"),
        "zh": ("乙旺里海水浴场", "永宗岛代表海滩，机场交通方便。", "机场铁道·仁川1号线换乘后乘公交。"),
        "zh-Hant": ("乙旺里海水浴場", "永宗島代表海灘，機場交通方便。", "機場鐵道·仁川1號線換乘後乘公車。"),
    },
    "왕산해수욕장": {
        "slug": "wangsan-beach",
        "lat": 37.4520,
        "lng": 126.3670,
        "region": "incheon",
        "maps_q": "왕산해수욕장",
        "ko": {
            "name": "왕산해수욕장",
            "desc": "을왕리 옆 영종도 해변. 서핑·일몰 명소로 알려져 있습니다.",
            "how": "을왕리와 같은 영종도 버스 노선; 왕산해변 정류장 하차.",
            "address": "인천 중구 용유서로 379",
        },
        "en": {
            "name": "Wangsan Beach",
            "desc": "Beach next to Eulwangni on Yeongjong — surfing and sunset views.",
            "how": "Same Yeongjong bus routes as Eulwangni; Wangsan Beach stop.",
            "address": "379 Yongyuseo-ro, Jung-gu, Incheon",
        },
        "ja": ("旺山海水浴場", "乙旺里隣の永宗島ビーチ。", "乙旺里と同じ永宗島バス。"),
        "zh": ("旺山海水浴场", "乙旺里旁的永宗岛海滩。", "与乙旺里相同的永宗岛公交。"),
        "zh-Hant": ("旺山海水浴場", "乙旺里旁的永宗島海灘。", "與乙旺里相同的永宗島公車。"),
    },
    "하나개해수욕장": {
        "slug": "hanagae-beach",
        "lat": 37.2525,
        "lng": 126.4745,
        "region": "incheon",
        "maps_q": "하나개해수욕장",
        "ko": {
            "name": "하나개해수욕장",
            "desc": "무의도 대표 해변. 갯벌·산책과 섬 분위기를 즐길 수 있습니다.",
            "how": "인천대교·잠진도 방면 버스 후 무의도 진입; 하나개 해수욕장 하차.",
            "address": "인천 중구 무의동 하나개해수욕장",
        },
        "en": {
            "name": "Hanagae Beach",
            "desc": "Main beach on Muui Island — tidal flats and island walks.",
            "how": "Bus toward Incheon Bridge / Jamjindo, then into Muui Island.",
            "address": "Hanagae Beach, Muui-dong, Jung-gu, Incheon",
        },
        "ja": ("ハナゲ海水浴場", "舞衣島の代表ビーチ。干潟と散策。", "仁川大橋・蚕津島方面バスで舞衣島へ。"),
        "zh": ("哈纳盖海水浴场", "舞衣岛代表海滩，潮滩与散步。", "仁川大桥·蚕津岛方向公交后进入舞衣岛。"),
        "zh-Hant": ("哈納蓋海水浴場", "舞衣島代表海灘，潮灘與散步。", "仁川大橋·蠶津島方向公車後進入舞衣島。"),
    },
    "십리포해수욕장": {
        "slug": "sipripo-beach",
        "lat": 37.2490,
        "lng": 126.5110,
        "region": "incheon",
        "maps_q": "십리포해수욕장",
        "ko": {
            "name": "십리포해수욕장",
            "desc": "덕적도의 고운 모래 해변. 인천항 여객선으로 가는 섬 여행 코스입니다.",
            "how": "인천항 연안여객터미널에서 덕적도 여객선 후 섬 내 이동.",
            "address": "인천 옹진군 덕적면 진리 십리포해수욕장",
        },
        "en": {
            "name": "Sipripo Beach",
            "desc": "Soft-sand beach on Deokjeokdo — ferry day trip from Incheon Port.",
            "how": "Ferry from Incheon coastal passenger terminal to Deokjeokdo.",
            "address": "Sipripo Beach, Jin-ri, Deokjeok-myeon, Ongjin-gun, Incheon",
        },
        "ja": ("十里浦海水浴場", "徳積島の砂浜。仁川港フェリーで。", "仁川港から徳積島フェリー。"),
        "zh": ("十里浦海水浴场", "德积岛细沙海滩，从仁川港坐渡轮。", "仁川港沿海客运站乘德积岛渡轮。"),
        "zh-Hant": ("十里浦海水浴場", "德積島細沙海灘，從仁川港坐渡輪。", "仁川港沿海客運站乘德積島渡輪。"),
    },
    # —— 여수 / 전남 ——
    "만성리검은모래해변": {
        "slug": "manseongni-black-sand-beach",
        "lat": 34.7365,
        "lng": 127.7455,
        "region": "jeolla",
        "maps_q": "여수 만성리검은모래해변",
        "ko": {
            "name": "만성리검은모래해변",
            "desc": "여수의 검은 모래 해변. 밤바다와 산책로로 유명합니다.",
            "how": "여수시외버스터미널·여수엑스포역에서 버스·택시.",
            "address": "전남 여수시 만흥동 만성리해변",
        },
        "en": {
            "name": "Manseongni Black Sand Beach",
            "desc": "Yeosu’s black-sand beach — night sea walks and coastal paths.",
            "how": "Bus/taxi from Yeosu bus terminal or Yeosu Expo Station.",
            "address": "Manseongni Beach, Manheung-dong, Yeosu, Jeollanam-do",
        },
        "ja": ("晩聖里黒砂ビーチ", "麗水の黒い砂浜。夜の海散歩が人気。", "麗水バスターミナル・エキスポ駅からバス・タクシー。"),
        "zh": ("晚圣里黑沙海滩", "丽水黑沙海滩，夜海散步出名。", "丽水巴士站或世博会站乘公交/出租车。"),
        "zh-Hant": ("晚聖里黑沙海灘", "麗水黑沙海灘，夜海散步出名。", "麗水巴士站或世博會站乘公車/計程車。"),
    },
    "웅천친수공원 해수욕장": {
        "slug": "ungcheon-beach",
        "lat": 34.7450,
        "lng": 127.6650,
        "region": "jeolla",
        "maps_q": "웅천친수공원 해수욕장",
        "ko": {
            "name": "웅천친수공원 해수욕장",
            "desc": "여수 웅천의 친수공원형 해수욕장. 가족 피크닉·산책에 적합합니다.",
            "how": "여수 시내버스·택시로 웅천친수공원 하차.",
            "address": "전남 여수시 웅천동 웅천친수공원",
        },
        "en": {
            "name": "Ungcheon Waterfront Beach",
            "desc": "Family-friendly waterfront beach park in Yeosu’s Ungcheon area.",
            "how": "City bus/taxi to Ungcheon Waterfront Park.",
            "address": "Ungcheon Waterfront Park, Ungcheon-dong, Yeosu",
        },
        "ja": ("熊川親水公園海水浴場", "麗水・熊川の親水公園ビーチ。", "市内バス・タクシーで熊川親水公園。"),
        "zh": ("熊川亲水公园海水浴场", "丽水熊川亲水公园型海滩，适合家庭。", "市内公交或出租车到熊川亲水公园。"),
        "zh-Hant": ("熊川親水公園海水浴場", "麗水熊川親水公園型海灘，適合家庭。", "市內公車或計程車到熊川親水公園。"),
    },
    # —— 제주 ——
    "협재해수욕장": {
        "slug": "hyeopjae-beach",
        "lat": 33.3942,
        "lng": 126.2394,
        "region": "jeju",
        "maps_q": "협재해수욕장",
        "ko": {
            "name": "협재해수욕장",
            "desc": "비양도가 보이는 제주 서쪽 대표 에메랄드 해변.",
            "how": "제주시·애월에서 서쪽 해안 버스; 협재해수욕장 정류장.",
            "address": "제주 제주시 한림읍 협재리 협재해수욕장",
        },
        "en": {
            "name": "Hyeopjae Beach",
            "desc": "West Jeju emerald beach with views of Biyangdo Island.",
            "how": "West coast bus from Jeju City / Aewol; Hyeopjae Beach stop.",
            "address": "Hyeopjae Beach, Hyeopjae-ri, Hallim-eup, Jeju City",
        },
        "ja": ("挟才海水浴場", "飛揚島が見える済州西のエメラルドビーチ。", "済州市・涯月から西海岸バス。"),
        "zh": ("挟才海水浴场", "可见飞扬岛的济州西侧翡翠海滩。", "济州市·涯月乘西海岸公交。"),
        "zh-Hant": ("挾才海水浴場", "可見飛揚島的濟州西側翡翠海灘。", "濟州市·涯月乘西海岸公車。"),
    },
    "금능해수욕장": {
        "slug": "geumneung-beach",
        "lat": 33.3895,
        "lng": 126.2340,
        "region": "jeju",
        "maps_q": "금능해수욕장",
        "ko": {
            "name": "금능해수욕장",
            "desc": "협재 옆의 고운 모래 해변. 금능석물원·산책과 함께 즐깁니다.",
            "how": "협재와 같은 한림·애월 해안 버스; 금능해수욕장 하차.",
            "address": "제주 제주시 한림읍 금능리 금능해수욕장",
        },
        "en": {
            "name": "Geumneung Beach",
            "desc": "Soft-sand beach beside Hyeopjae — pair with Geumneung stone park walks.",
            "how": "Same Hallim/Aewol coast buses as Hyeopjae; Geumneung Beach stop.",
            "address": "Geumneung Beach, Geumneung-ri, Hallim-eup, Jeju City",
        },
        "ja": ("金寧海水浴場（済州西）", "挟才隣の砂浜ビーチ。", "挟才と同じ翰林・涯月海岸バス。"),
        "zh": ("金能海水浴场", "挟才旁细沙海滩。", "与挟才相同的翰林·涯月海岸公交。"),
        "zh-Hant": ("金能海水浴場", "挾才旁細沙海灘。", "與挾才相同的翰林·涯月海岸公車。"),
    },
    "함덕해수욕장": {
        "slug": "hamdeok-beach",
        "lat": 33.5433,
        "lng": 126.6694,
        "region": "jeju",
        "maps_q": "함덕해수욕장",
        "ko": {
            "name": "함덕해수욕장",
            "desc": "제주 동북부 대표 해변. 에메랄드 바다와 카페 거리가 유명합니다.",
            "how": "제주시에서 함덕·세화 방면 버스; 함덕해수욕장 정류장.",
            "address": "제주 제주시 조천읍 함덕리 함덕해수욕장",
        },
        "en": {
            "name": "Hamdeok Beach",
            "desc": "Northeast Jeju favorite — emerald water and café streets.",
            "how": "Bus from Jeju City toward Hamdeok / Sehwa; Hamdeok Beach stop.",
            "address": "Hamdeok Beach, Hamdeok-ri, Jocheon-eup, Jeju City",
        },
        "ja": ("咸徳海水浴場", "済州東北部の代表ビーチ。", "済州市から咸徳・細花方面バス。"),
        "zh": ("咸德海水浴场", "济州东北部代表海滩。", "济州市乘往咸德·细花方向公交。"),
        "zh-Hant": ("咸德海水浴場", "濟州東北部代表海灘。", "濟州市乘往咸德·細花方向公車。"),
    },
    "월정리해변": {
        "slug": "woljeong-beach",
        "lat": 33.5565,
        "lng": 126.7958,
        "region": "jeju",
        "maps_q": "월정리해변",
        "ko": {
            "name": "월정리해변",
            "desc": "카페·감성 사진으로 유명한 제주 동쪽 해변.",
            "how": "제주시·성산에서 동부 해안 버스; 월정리 정류장.",
            "address": "제주 제주시 구좌읍 월정리 월정리해변",
        },
        "en": {
            "name": "Woljeong Beach",
            "desc": "East Jeju beach famous for cafés and photo spots.",
            "how": "East coast bus from Jeju City / Seongsan; Woljeong-ri stop.",
            "address": "Woljeong Beach, Woljeong-ri, Gujwa-eup, Jeju City",
        },
        "ja": ("月汀里ビーチ", "カフェと写真スポットで有名な東済州。", "済州市・城山から東部海岸バス。"),
        "zh": ("月汀里海滩", "以咖啡店和打卡照闻名的济州东岸。", "济州市·城山乘东部海岸公交。"),
        "zh-Hant": ("月汀里海灘", "以咖啡店和打卡照聞名的濟州東岸。", "濟州市·城山乘東部海岸公車。"),
    },
    "곽지해수욕장": {
        "slug": "gwakji-beach",
        "lat": 33.4505,
        "lng": 126.3045,
        "region": "jeju",
        "maps_q": "곽지해수욕장",
        "ko": {
            "name": "곽지해수욕장",
            "desc": "애월 인근 해변. 곽지과물해변으로도 불리며 일몰이 아름답습니다.",
            "how": "애월·한림 해안 버스; 곽지해수욕장 정류장.",
            "address": "제주 제주시 애월읍 곽지리 곽지해수욕장",
        },
        "en": {
            "name": "Gwakji Beach",
            "desc": "Aewol-area beach (also called Gwakji Gwamul) with fine sunsets.",
            "how": "Aewol / Hallim coast bus; Gwakji Beach stop.",
            "address": "Gwakji Beach, Gwakji-ri, Aewol-eup, Jeju City",
        },
        "ja": ("郭支海水浴場", "涯月近くのビーチ。夕日が美しい。", "涯月・翰林海岸バス。"),
        "zh": ("郭支海水浴场", "涯月附近海滩，日落很美。", "涯月·翰林海岸公交。"),
        "zh-Hant": ("郭支海水浴場", "涯月附近海灘，日落很美。", "涯月·翰林海岸公車。"),
    },
    "이호테우해수욕장": {
        "slug": "iho-tewoo-beach",
        "lat": 33.4975,
        "lng": 126.4530,
        "region": "jeju",
        "maps_q": "이호테우해수욕장",
        "ko": {
            "name": "이호테우해수욕장",
            "desc": "말 등대(테우) 포토스팟으로 유명한 제주시 서쪽 근교 해변.",
            "how": "제주시내에서 이호·도두 방면 버스; 이호테우해수욕장 하차.",
            "address": "제주 제주시 이호일동 이호테우해수욕장",
        },
        "en": {
            "name": "Iho Tewoo Beach",
            "desc": "Near Jeju City — famous for the horse-shaped Tewoo lighthouses.",
            "how": "City bus toward Iho / Dodu; Iho Tewoo Beach stop.",
            "address": "Iho Tewoo Beach, Ihoil-dong, Jeju City",
        },
        "ja": ("梨湖テウ海水浴場", "馬の灯台で有名な済州市近郊ビーチ。", "済州市内から梨湖・道頭方面バス。"),
        "zh": ("梨湖Teu海水浴场", "以马形灯塔闻名的济州市近郊海滩。", "济州市内乘往梨湖·道头方向公交。"),
        "zh-Hant": ("梨湖Teu海水浴場", "以馬形燈塔聞名的濟州市近郊海灘。", "濟州市內乘往梨湖·道頭方向公車。"),
    },
    "중문색달해수욕장": {
        "slug": "jungmun-saekdal-beach",
        "lat": 33.2450,
        "lng": 126.4120,
        "region": "jeju",
        "maps_q": "중문색달해수욕장",
        "ko": {
            "name": "중문색달해수욕장",
            "desc": "중문관광단지 옆 서귀포 해변. 파도와 검은 현무암 해안이 인상적입니다.",
            "how": "서귀포·중문에서 버스·택시; 색달해수욕장 하차.",
            "address": "제주 서귀포시 색달동 중문색달해수욕장",
        },
        "en": {
            "name": "Jungmun Saekdal Beach",
            "desc": "Seogwipo beach by Jungmun Resort — waves and basalt coastline.",
            "how": "Bus/taxi from Seogwipo or Jungmun; Saekdal Beach stop.",
            "address": "Jungmun Saekdal Beach, Saekdal-dong, Seogwipo",
        },
        "ja": ("中文色達海水浴場", "中文観光団地横の西帰浦ビーチ。", "西帰浦・中文からバス・タクシー。"),
        "zh": ("中文色达海水浴场", "中文旅游区旁的西归浦海滩。", "西归浦·中文乘公交或出租车。"),
        "zh-Hant": ("中文色達海水浴場", "中文旅遊區旁的西歸浦海灘。", "西歸浦·中文乘公車或計程車。"),
    },
    "김녕해수욕장": {
        "slug": "gimnyeong-beach",
        "lat": 33.5575,
        "lng": 126.7465,
        "region": "jeju",
        "maps_q": "김녕해수욕장",
        "ko": {
            "name": "김녕해수욕장",
            "desc": "김녕·월정 인근의 고운 모래 해변. 김녕미로공원과도 가깝습니다.",
            "how": "동부 해안 버스; 김녕해수욕장·김녕리 정류장.",
            "address": "제주 제주시 구좌읍 김녕리 김녕해수욕장",
        },
        "en": {
            "name": "Gimnyeong Beach",
            "desc": "Sandy beach near Gimnyeong Maze Park and Woljeong.",
            "how": "East coast bus; Gimnyeong Beach / Gimnyeong-ri stop.",
            "address": "Gimnyeong Beach, Gimnyeong-ri, Gujwa-eup, Jeju City",
        },
        "ja": ("金寧海水浴場", "金寧迷路公園近くの砂浜。", "東部海岸バス。"),
        "zh": ("金宁海水浴场", "金宁迷宫公园附近细沙海滩。", "东部海岸公交。"),
        "zh-Hant": ("金寧海水浴場", "金寧迷宮公園附近細沙海灘。", "東部海岸公車。"),
    },
    "표선해수욕장": {
        "slug": "pyoseon-beach",
        "lat": 33.3255,
        "lng": 126.8345,
        "region": "jeju",
        "maps_q": "표선해수욕장",
        "ko": {
            "name": "표선해수욕장",
            "desc": "넓은 백사장과 표선민속촌이 가까운 제주 남동부 해변.",
            "how": "성산·서귀포에서 표선 방면 버스; 표선해수욕장 하차.",
            "address": "제주 서귀포시 표선면 표선리 표선해수욕장",
        },
        "en": {
            "name": "Pyoseon Beach",
            "desc": "Wide sandy bay near Pyoseon Folk Village in southeast Jeju.",
            "how": "Bus from Seongsan or Seogwipo toward Pyoseon.",
            "address": "Pyoseon Beach, Pyoseon-ri, Pyoseon-myeon, Seogwipo",
        },
        "ja": ("表善海水浴場", "広い砂浜と民俗村が近い南東済州。", "城山・西帰浦から表善方面バス。"),
        "zh": ("表善海水浴场", "宽阔白沙滩，靠近表善民俗村。", "城山·西归浦乘往表善方向公交。"),
        "zh-Hant": ("表善海水浴場", "寬闊白沙灘，靠近表善民俗村。", "城山·西歸浦乘往表善方向公車。"),
    },
    # —— 강원 ——
    "속초해수욕장": {
        "slug": "sokcho-beach",
        "lat": 38.1905,
        "lng": 128.6035,
        "region": "gangwon",
        "maps_q": "속초해수욕장",
        "ko": {
            "name": "속초해수욕장",
            "desc": "속초 도심과 가까운 동해 해변. 속초관광수산시장과 함께 즐기기 좋습니다.",
            "how": "속초시외버스터미널·속초역에서 도보·택시.",
            "address": "강원 속초시 해오름로 190",
        },
        "en": {
            "name": "Sokcho Beach",
            "desc": "East Sea beach near downtown Sokcho and the tourist fish market.",
            "how": "Walk/taxi from Sokcho bus terminal or Sokcho Station.",
            "address": "190 Haeoreum-ro, Sokcho, Gangwon-do",
        },
        "ja": ("束草海水浴場", "束草市街地近くの東海ビーチ。", "束草バスターミナル・駅から徒歩・タクシー。"),
        "zh": ("束草海水浴场", "靠近束草市区的东海海滩。", "束草巴士站或火车站步行/出租车。"),
        "zh-Hant": ("束草海水浴場", "靠近束草市區的東海海灘。", "束草巴士站或火車站步行/計程車。"),
    },
    "경포해수욕장": {
        "slug": "gyeongpo-beach",
        "lat": 37.8055,
        "lng": 128.9085,
        "region": "gangwon",
        "maps_q": "경포해수욕장",
        "ko": {
            "name": "경포해수욕장",
            "desc": "강릉 대표 해변. 경포호·경포대와 이어지는 동해 여행 코스입니다.",
            "how": "강릉역·터미널에서 버스·택시; 경포해수욕장 하차.",
            "address": "강원 강릉시 창해로 514",
        },
        "en": {
            "name": "Gyeongpo Beach",
            "desc": "Gangneung’s flagship beach by Gyeongpo Lake and pavilion.",
            "how": "Bus/taxi from Gangneung Station or terminal.",
            "address": "514 Changhae-ro, Gangneung, Gangwon-do",
        },
        "ja": ("鏡浦海水浴場", "江陵の代表ビーチ。鏡浦湖とセットで。", "江陵駅・ターミナルからバス・タクシー。"),
        "zh": ("镜浦海水浴场", "江陵代表海滩，与镜浦湖相连。", "江陵站或巴士站乘公交/出租车。"),
        "zh-Hant": ("鏡浦海水浴場", "江陵代表海灘，與鏡浦湖相連。", "江陵站或巴士站乘公車/計程車。"),
    },
    "안목해변": {
        "slug": "anmok-beach",
        "lat": 37.7725,
        "lng": 128.9475,
        "region": "gangwon",
        "maps_q": "안목해변",
        "ko": {
            "name": "안목해변",
            "desc": "강릉 커피거리와 이어지는 해변. 일출·카페 산책으로 유명합니다.",
            "how": "강릉시내에서 안목·경포 방면 버스; 안목해변 하차.",
            "address": "강원 강릉시 창해로14번길 안목해변",
        },
        "en": {
            "name": "Anmok Beach",
            "desc": "Gangneung coffee-street beach — sunrises and café walks.",
            "how": "City bus toward Anmok / Gyeongpo; Anmok Beach stop.",
            "address": "Anmok Beach, Changhae-ro 14beon-gil, Gangneung",
        },
        "ja": ("安木ビーチ", "江陵コーヒ通り沿いのビーチ。", "江陵市内から安木・鏡浦方面バス。"),
        "zh": ("安木海滩", "江陵咖啡街旁的海滩。", "江陵市内乘往安木·镜浦方向公交。"),
        "zh-Hant": ("安木海灘", "江陵咖啡街旁的海灘。", "江陵市內乘往安木·鏡浦方向公車。"),
    },
    "강문해변": {
        "slug": "gangmun-beach",
        "lat": 37.7955,
        "lng": 128.9185,
        "region": "gangwon",
        "maps_q": "강문해변",
        "ko": {
            "name": "강문해변",
            "desc": "경포와 가까운 강릉 해변. 카페·서핑숍이 모여 있습니다.",
            "how": "경포·안목과 같은 강릉 해안 버스; 강문해변 하차.",
            "address": "강원 강릉시 창해로 345",
        },
        "en": {
            "name": "Gangmun Beach",
            "desc": "Beach near Gyeongpo with cafés and surf shops.",
            "how": "Same Gangneung coast buses as Gyeongpo / Anmok.",
            "address": "345 Changhae-ro, Gangneung, Gangwon-do",
        },
        "ja": ("江門ビーチ", "鏡浦近くの江陵ビーチ。", "鏡浦・安木と同じ海岸バス。"),
        "zh": ("江门海滩", "靠近镜浦的江陵海滩。", "与镜浦·安木相同的海岸公交。"),
        "zh-Hant": ("江門海灘", "靠近鏡浦的江陵海灘。", "與鏡浦·安木相同的海岸公車。"),
    },
    "주문진해수욕장": {
        "slug": "jumunjin-beach",
        "lat": 37.8915,
        "lng": 128.8295,
        "region": "gangwon",
        "maps_q": "주문진해수욕장",
        "ko": {
            "name": "주문진해수욕장",
            "desc": "주문진항·수산시장과 가까운 강릉 북쪽 해변.",
            "how": "강릉에서 주문진 방면 버스; 주문진해수욕장·주문진항 하차.",
            "address": "강원 강릉시 주문진읍 주문리 주문진해수욕장",
        },
        "en": {
            "name": "Jumunjin Beach",
            "desc": "North Gangneung beach by Jumunjin Port and fish market.",
            "how": "Bus from Gangneung toward Jumunjin Port / beach.",
            "address": "Jumunjin Beach, Jumun-ri, Jumunjin-eup, Gangneung",
        },
        "ja": ("注文津海水浴場", "注文津港近くの江陵北ビーチ。", "江陵から注文津方面バス。"),
        "zh": ("注文津海水浴场", "靠近注文津港的江陵北海滩。", "江陵乘往注文津方向公交。"),
        "zh-Hant": ("注文津海水浴場", "靠近注文津港的江陵北海灘。", "江陵乘往注文津方向公車。"),
    },
    "정동진해수욕장": {
        "slug": "jeongdongjin-beach",
        "lat": 37.6915,
        "lng": 129.0325,
        "region": "gangwon",
        "maps_q": "정동진해수욕장",
        "ko": {
            "name": "정동진해수욕장",
            "desc": "일출과 바다열차로 유명한 강릉 남쪽 해변. 썬크루즈 호텔 전망도 인기입니다.",
            "how": "정동진역에서 도보, 또는 강릉에서 버스.",
            "address": "강원 강릉시 강동면 정동진리 정동진해수욕장",
        },
        "en": {
            "name": "Jeongdongjin Beach",
            "desc": "Sunrise beach south of Gangneung — rail and ocean views.",
            "how": "Walk from Jeongdongjin Station, or bus from Gangneung.",
            "address": "Jeongdongjin Beach, Jeongdongjin-ri, Gangdong-myeon, Gangneung",
        },
        "ja": ("正東津海水浴場", "日の出で有名な江陵南のビーチ。", "正東津駅から徒歩、または江陵からバス。"),
        "zh": ("正东津海水浴场", "以日出闻名的江陵南海滩。", "正东津站步行，或从江陵乘公交。"),
        "zh-Hant": ("正東津海水浴場", "以日出聞名的江陵南海灘。", "正東津站步行，或從江陵乘公車。"),
    },
    "양양 서피비치": {
        "slug": "yangyang-surfyy-beach",
        "lat": 38.0255,
        "lng": 128.7175,
        "region": "gangwon",
        "maps_q": "양양 서피비치",
        "ko": {
            "name": "양양 서피비치",
            "desc": "양양의 서핑·페스티벌 명소. 여름 시즌 라이브·비치바가 유명합니다.",
            "how": "양양터미널·속초에서 버스·택시; 서피비치 하차.",
            "address": "강원 양양군 현남면 인구리 서피비치",
        },
        "en": {
            "name": "Yangyang Surfyy Beach",
            "desc": "Surf and festival beach in Yangyang — summer beach bars and live events.",
            "how": "Bus/taxi from Yangyang terminal or Sokcho.",
            "address": "Surfyy Beach, Ingu-ri, Hyeonnam-myeon, Yangyang-gun",
        },
        "ja": ("襄陽サーフィービーチ", "サーフィンとフェスで有名な襄陽ビーチ。", "襄陽ターミナル・束草からバス・タクシー。"),
        "zh": ("襄阳Surfyy海滩", "襄阳冲浪·音乐节海滩。", "襄阳巴士站或束草乘公交/出租车。"),
        "zh-Hant": ("襄陽Surfyy海灘", "襄陽衝浪·音樂節海灘。", "襄陽巴士站或束草乘公車/計程車。"),
    },
    "낙산해수욕장": {
        "slug": "naksan-beach",
        "lat": 38.1245,
        "lng": 128.6345,
        "region": "gangwon",
        "maps_q": "낙산해수욕장",
        "ko": {
            "name": "낙산해수욕장",
            "desc": "낙산사와 가까운 양양 해변. 사찰·해변을 하루에 돌기 좋습니다.",
            "how": "양양·속초에서 버스; 낙산해수욕장·낙산사 하차.",
            "address": "강원 양양군 강현면 전진리 낙산해수욕장",
        },
        "en": {
            "name": "Naksan Beach",
            "desc": "Yangyang beach by Naksansa Temple — temple and sea in one stop.",
            "how": "Bus from Yangyang or Sokcho; Naksan Beach / Naksansa stop.",
            "address": "Naksan Beach, Jeonjin-ri, Ganghyeon-myeon, Yangyang-gun",
        },
        "ja": ("洛山海水浴場", "洛山寺近くの襄陽ビーチ。", "襄陽・束草からバス。"),
        "zh": ("洛山海水浴场", "靠近洛山寺的襄阳海滩。", "襄阳·束草乘公交。"),
        "zh-Hant": ("洛山海水浴場", "靠近洛山寺的襄陽海灘。", "襄陽·束草乘公車。"),
    },
    "하조대해수욕장": {
        "slug": "hajodae-beach",
        "lat": 38.0655,
        "lng": 128.6685,
        "region": "gangwon",
        "maps_q": "하조대해수욕장",
        "ko": {
            "name": "하조대해수욕장",
            "desc": "양양의 기암과 등대가 있는 해변. 일출 포인트로 유명합니다.",
            "how": "양양·속초에서 버스·택시; 하조대 하차.",
            "address": "강원 양양군 현북면 하조대해변길 하조대해수욕장",
        },
        "en": {
            "name": "Hajodae Beach",
            "desc": "Yangyang beach with rock formations and a lighthouse — sunrise spot.",
            "how": "Bus/taxi from Yangyang or Sokcho to Hajodae.",
            "address": "Hajodae Beach, Hyeonbuk-myeon, Yangyang-gun",
        },
        "ja": ("河原台海水浴場", "奇岩と灯台がある襄陽ビーチ。", "襄陽・束草からバス・タクシー。"),
        "zh": ("河原台海水浴场", "襄阳奇岩与灯塔海滩，日出出名。", "襄阳·束草乘公交或出租车。"),
        "zh-Hant": ("河原台海水浴場", "襄陽奇岩與燈塔海灘，日出出名。", "襄陽·束草乘公車或計程車。"),
    },
    "죽도해수욕장": {
        "slug": "jukdo-beach-yangyang",
        "lat": 38.0550,
        "lng": 128.6750,
        "region": "gangwon",
        "maps_q": "양양 죽도해수욕장",
        "ko": {
            "name": "죽도해수욕장",
            "desc": "양양 죽도·서핑 포인트 인근 해변. (포항 죽도시장과는 다름)",
            "how": "양양터미널에서 죽도·현남 방면 버스.",
            "address": "강원 양양군 현남면 죽도리 죽도해수욕장",
        },
        "en": {
            "name": "Jukdo Beach (Yangyang)",
            "desc": "Yangyang surf beach by Jukdo — not Pohang’s Jukdo Market.",
            "how": "Bus from Yangyang terminal toward Jukdo / Hyeonnam.",
            "address": "Jukdo Beach, Jukdo-ri, Hyeonnam-myeon, Yangyang-gun",
        },
        "ja": ("竹島海水浴場（襄陽）", "襄陽のサーフィンビーチ。浦項竹島市場とは別。", "襄陽ターミナルから竹島方面バス。"),
        "zh": ("竹岛海水浴场（襄阳）", "襄阳冲浪海滩，与浦项竹岛市场不同。", "襄阳巴士站乘往竹岛方向公交。"),
        "zh-Hant": ("竹島海水浴場（襄陽）", "襄陽衝浪海灘，與浦項竹島市場不同。", "襄陽巴士站乘往竹島方向公車。"),
    },
    "삼척해수욕장": {
        "slug": "samcheok-beach",
        "lat": 37.4405,
        "lng": 129.1905,
        "region": "gangwon",
        "maps_q": "삼척해수욕장",
        "ko": {
            "name": "삼척해수욕장",
            "desc": "삼척 도심 인근 동해 해변. 환선굴·장호항 여행과 함께 넣기 좋습니다.",
            "how": "삼척역·터미널에서 버스·택시.",
            "address": "강원 삼척시 수로부인로 삼척해수욕장",
        },
        "en": {
            "name": "Samcheok Beach",
            "desc": "East Sea beach near Samcheok — pair with caves and Jangho Port.",
            "how": "Bus/taxi from Samcheok Station or terminal.",
            "address": "Samcheok Beach, Surbuin-ro, Samcheok, Gangwon-do",
        },
        "ja": ("三陟海水浴場", "三陟市街地近くの東海ビーチ。", "三陟駅・ターミナルからバス・タクシー。"),
        "zh": ("三陟海水浴场", "三陟市区附近东海海滩。", "三陟站或巴士站乘公交/出租车。"),
        "zh-Hant": ("三陟海水浴場", "三陟市區附近東海海灘。", "三陟站或巴士站乘公車/計程車。"),
    },
    "망상해수욕장": {
        "slug": "mangsang-beach",
        "lat": 37.5925,
        "lng": 129.0905,
        "region": "gangwon",
        "maps_q": "망상해수욕장",
        "ko": {
            "name": "망상해수욕장",
            "desc": "동해시의 넓은 백사장. 오토캠핑·가족 피서지로 유명합니다.",
            "how": "동해역·터미널에서 버스; 망상해수욕장 하차.",
            "address": "강원 동해시 망상동 망상해수욕장",
        },
        "en": {
            "name": "Mangsang Beach",
            "desc": "Wide sandy beach in Donghae — popular for camping and family trips.",
            "how": "Bus from Donghae Station or terminal to Mangsang Beach.",
            "address": "Mangsang Beach, Mangsang-dong, Donghae, Gangwon-do",
        },
        "ja": ("望祥海水浴場", "東海市の広い砂浜。キャンプに人気。", "東海駅・ターミナルからバス。"),
        "zh": ("望祥海水浴场", "东海市宽阔白沙滩，适合露营。", "东海站或巴士站乘公交。"),
        "zh-Hant": ("望祥海水浴場", "東海市寬闊白沙灘，適合露營。", "東海站或巴士站乘公車。"),
    },
    "송지호해수욕장": {
        "slug": "songjiho-beach",
        "lat": 38.3355,
        "lng": 128.5205,
        "region": "gangwon",
        "maps_q": "송지호해수욕장",
        "ko": {
            "name": "송지호해수욕장",
            "desc": "고성 송지호와 이어지는 동해 해변. 철새·호수 산책과 함께 즐깁니다.",
            "how": "속초·고성에서 버스·택시; 송지호 하차.",
            "address": "강원 고성군 죽왕면 송지호해수욕장",
        },
        "en": {
            "name": "Songjiho Beach",
            "desc": "Goseong beach by Songji Lake — birds and lakeside walks.",
            "how": "Bus/taxi from Sokcho or Goseong to Songjiho.",
            "address": "Songjiho Beach, Jukwang-myeon, Goseong-gun, Gangwon-do",
        },
        "ja": ("松池湖海水浴場", "高城・松池湖沿いのビーチ。", "束草・高城からバス・タクシー。"),
        "zh": ("松池湖海水浴场", "高城松池湖旁的东海海滩。", "束草·高城乘公交或出租车。"),
        "zh-Hant": ("松池湖海水浴場", "高城松池湖旁的東海海灘。", "束草·高城乘公車或計程車。"),
    },
    # —— 경북 ——
    "영일대해수욕장": {
        "slug": "yeongildae-beach",
        "lat": 36.0585,
        "lng": 129.3785,
        "region": "gyeongsang",
        "maps_q": "영일대해수욕장",
        "ko": {
            "name": "영일대해수욕장",
            "desc": "포항 영일만의 대표 해변. 죽도시장·영일대 전망대와 가깝습니다.",
            "how": "포항역·터미널에서 택시·버스; 영일대·죽도시장 방면.",
            "address": "경북 포항시 북구 두호동 영일대해수욕장",
        },
        "en": {
            "name": "Yeongildae Beach",
            "desc": "Pohang’s Yeongil Bay beach near Jukdo Market and the pavilion.",
            "how": "Taxi/bus from Pohang Station or terminal toward Yeongildae.",
            "address": "Yeongildae Beach, Duho-dong, Buk-gu, Pohang",
        },
        "ja": ("迎日台海水浴場", "浦項・迎日湾の代表ビーチ。", "浦項駅・ターミナルからタクシー・バス。"),
        "zh": ("迎日台海水浴场", "浦项迎日湾代表海滩。", "浦项站或巴士站乘出租车/公交。"),
        "zh-Hant": ("迎日台海水浴場", "浦項迎日灣代表海灘。", "浦項站或巴士站乘計程車/公車。"),
    },
    "구룡포해수욕장": {
        "slug": "guryongpo-beach",
        "lat": 35.9905,
        "lng": 129.5585,
        "region": "gyeongsang",
        "maps_q": "구룡포해수욕장",
        "ko": {
            "name": "구룡포해수욕장",
            "desc": "포항 구룡포의 동해 해변. 과메기·일본인 가옥거리 관광과 함께 즐깁니다.",
            "how": "포항에서 구룡포 방면 버스; 구룡포해수욕장 하차.",
            "address": "경북 포항시 남구 구룡포읍 구룡포해수욕장",
        },
        "en": {
            "name": "Guryongpo Beach",
            "desc": "East Sea beach in Guryongpo — gwamegi and historic street nearby.",
            "how": "Bus from Pohang toward Guryongpo Beach.",
            "address": "Guryongpo Beach, Guryongpo-eup, Nam-gu, Pohang",
        },
        "ja": ("九龍浦海水浴場", "浦項・九龍浦のビーチ。", "浦項から九龍浦方面バス。"),
        "zh": ("九龙浦海水浴场", "浦项九龙浦东海海滩。", "浦项乘往九龙浦方向公交。"),
        "zh-Hant": ("九龍浦海水浴場", "浦項九龍浦東海海灘。", "浦項乘往九龍浦方向公車。"),
    },
    "고래불해수욕장": {
        "slug": "goraebul-beach",
        "lat": 36.5805,
        "lng": 129.4155,
        "region": "gyeongsang",
        "maps_q": "고래불해수욕장",
        "ko": {
            "name": "고래불해수욕장",
            "desc": "영덕의 넓은 동해 해변. 캠핑·일출 명소로 알려져 있습니다.",
            "how": "영덕·울진에서 버스·택시; 고래불해수욕장 하차.",
            "address": "경북 영덕군 병곡면 병곡리 고래불해수욕장",
        },
        "en": {
            "name": "Goraebul Beach",
            "desc": "Wide Yeongdeok East Sea beach — camping and sunrise.",
            "how": "Bus/taxi from Yeongdeok or Uljin.",
            "address": "Goraebul Beach, Byeonggok-ri, Byeonggok-myeon, Yeongdeok-gun",
        },
        "ja": ("고래불海水浴場", "盈徳の広い東海ビーチ。", "盈徳・蔚珍からバス・タクシー。"),
        "zh": ("鲸鱼火海水浴场", "盈德宽阔东海海滩。", "盈德·蔚珍乘公交或出租车。"),
        "zh-Hant": ("鯨魚火海水浴場", "盈德寬闊東海海灘。", "盈德·蔚珍乘公車或計程車。"),
    },
    "월포해수욕장": {
        "slug": "wolpo-beach",
        "lat": 36.2155,
        "lng": 129.3855,
        "region": "gyeongsang",
        "maps_q": "월포해수욕장",
        "ko": {
            "name": "월포해수욕장",
            "desc": "포항 북부의 가족·캠핑형 동해 해변.",
            "how": "포항에서 월포·청하 방면 버스.",
            "address": "경북 포항시 북구 청하면 월포리 월포해수욕장",
        },
        "en": {
            "name": "Wolpo Beach",
            "desc": "Family and camping beach in northern Pohang.",
            "how": "Bus from Pohang toward Wolpo / Cheongha.",
            "address": "Wolpo Beach, Wolpo-ri, Cheongha-myeon, Buk-gu, Pohang",
        },
        "ja": ("月浦海水浴場", "浦項北部のファミリービーチ。", "浦項から月浦・清河方面バス。"),
        "zh": ("月浦海水浴场", "浦项北部家庭·露营海滩。", "浦项乘往月浦·清河方向公交。"),
        "zh-Hant": ("月浦海水浴場", "浦項北部家庭·露營海灘。", "浦項乘往月浦·清河方向公車。"),
    },
    # —— 경남 ——
    "학동흑진주몽돌해수욕장": {
        "slug": "hakdong-pebble-beach",
        "lat": 34.8175,
        "lng": 128.6905,
        "region": "gyeongsang",
        "maps_q": "학동흑진주몽돌해수욕장",
        "ko": {
            "name": "학동흑진주몽돌해수욕장",
            "desc": "거제의 검은 몽돌 해변. 파도 소리가 유명한 남해 명소입니다.",
            "how": "거제·통영에서 학동 방면 버스·택시.",
            "address": "경남 거제시 동부면 학동리 학동흑진주몽돌해수욕장",
        },
        "en": {
            "name": "Hakdong Black Pearl Pebble Beach",
            "desc": "Geoje’s famous black pebble beach — distinctive wave sounds.",
            "how": "Bus/taxi from Geoje or Tongyeong toward Hakdong.",
            "address": "Hakdong Pebble Beach, Hakdong-ri, Dongbu-myeon, Geoje",
        },
        "ja": ("鶴洞黒真珠モンドルビーチ", "巨済の黒い石ビーチ。波音が有名。", "巨済・統営から鶴洞方面。"),
        "zh": ("鹤洞黑珍珠卵石海水浴场", "巨济黑卵石海滩，浪声出名。", "巨济·统营乘往鹤洞方向。"),
        "zh-Hant": ("鶴洞黑珍珠卵石海水浴場", "巨濟黑卵石海灘，浪聲出名。", "巨濟·統營乘往鶴洞方向。"),
    },
    "구조라해수욕장": {
        "slug": "gujora-beach",
        "lat": 34.8055,
        "lng": 128.6900,
        "region": "gyeongsang",
        "maps_q": "구조라해수욕장",
        "ko": {
            "name": "구조라해수욕장",
            "desc": "거제 동부의 모래 해변. 외도보타니아·학동과 가까운 코스입니다.",
            "how": "거제에서 구조라·학동 방면 버스.",
            "address": "경남 거제시 일운면 구조라리 구조라해수욕장",
        },
        "en": {
            "name": "Gujora Beach",
            "desc": "Sandy beach in eastern Geoje near Oedo and Hakdong.",
            "how": "Bus from Geoje toward Gujora / Hakdong.",
            "address": "Gujora Beach, Gujora-ri, Ilun-myeon, Geoje",
        },
        "ja": ("旧助羅海水浴場", "巨済東部の砂浜。", "巨済から旧助羅・鶴洞方面バス。"),
        "zh": ("旧助罗海水浴场", "巨济东部沙滩。", "巨济乘往旧助罗·鹤洞方向公交。"),
        "zh-Hant": ("舊助羅海水浴場", "巨濟東部沙灘。", "巨濟乘往舊助羅·鶴洞方向公車。"),
    },
    "와현모래숲해변": {
        "slug": "wahyeon-sand-forest-beach",
        "lat": 34.8050,
        "lng": 128.7055,
        "region": "gyeongsang",
        "maps_q": "와현모래숲해변",
        "ko": {
            "name": "와현모래숲해변",
            "desc": "거제 와현의 모래·소나무 숲 해변. 가족 피서지로 인기입니다.",
            "how": "거제에서 와현 방면 버스·택시.",
            "address": "경남 거제시 일운면 와현리 와현모래숲해변",
        },
        "en": {
            "name": "Wahyeon Sand Forest Beach",
            "desc": "Geoje beach with sand and pine forest — family summer spot.",
            "how": "Bus/taxi from Geoje toward Wahyeon.",
            "address": "Wahyeon Sand Forest Beach, Wahyeon-ri, Ilun-myeon, Geoje",
        },
        "ja": ("臥現砂浜の森ビーチ", "巨済・臥現の松林ビーチ。", "巨済から臥現方面。"),
        "zh": ("卧现沙子林海滩", "巨济卧现沙地松林海滩。", "巨济乘往卧现方向。"),
        "zh-Hant": ("臥現沙子林海灘", "巨濟臥現沙地松林海灘。", "巨濟乘往臥現方向。"),
    },
    "상주은모래비치": {
        "slug": "sangju-silver-sand-beach",
        "lat": 34.7215,
        "lng": 128.0005,
        "region": "gyeongsang",
        "maps_q": "상주은모래비치",
        "ko": {
            "name": "상주은모래비치",
            "desc": "남해군의 고운 은빛 모래 해변. 독일마을·상주와 가까운 코스입니다.",
            "how": "남해·진주에서 상주 방면 버스.",
            "address": "경남 남해군 상주면 상주리 상주은모래비치",
        },
        "en": {
            "name": "Sangju Silver Sand Beach",
            "desc": "Fine silver sand on Namhae — near German Village / Sangju.",
            "how": "Bus from Namhae or Jinju toward Sangju.",
            "address": "Sangju Silver Sand Beach, Sangju-ri, Sangju-myeon, Namhae-gun",
        },
        "ja": ("尚州銀砂ビーチ", "南海郡の銀色の砂浜。", "南海・晋州から尚州方面バス。"),
        "zh": ("尚州银沙海滩", "南海郡细银沙滩。", "南海·晋州乘往尚州方向公交。"),
        "zh-Hant": ("尚州銀沙海灘", "南海郡細銀沙灘。", "南海·晉州乘往尚州方向公車。"),
    },
    # —— 전남 ——
    "명사십리해수욕장": {
        "slug": "myeongsasipri-beach",
        "lat": 34.3205,
        "lng": 126.7505,
        "region": "jeolla",
        "maps_q": "명사십리해수욕장",
        "ko": {
            "name": "명사십리해수욕장",
            "desc": "완도 신지의 긴 백사장. ‘명사십리’라는 이름처럼 넓은 모래밭이 인상적입니다.",
            "how": "완도에서 신지대교·명사십리 방면 버스.",
            "address": "전남 완도군 신지면 명사십리해수욕장",
        },
        "en": {
            "name": "Myeongsasipri Beach",
            "desc": "Long white sand on Wando’s Sinji Island — famously wide beach.",
            "how": "Bus from Wando toward Sinji Bridge / Myeongsasipri.",
            "address": "Myeongsasipri Beach, Sinji-myeon, Wando-gun",
        },
        "ja": ("明沙十里海水浴場", "莞島・新智の長い白砂。", "莞島から新智・明沙十里方面バス。"),
        "zh": ("明沙十里海水浴场", "莞岛新智长白沙滩。", "莞岛乘往新智·明沙十里方向公交。"),
        "zh-Hant": ("明沙十里海水浴場", "莞島新智長白沙灘。", "莞島乘往新智·明沙十里方向公車。"),
    },
    "율포솔밭해수욕장": {
        "slug": "yulpo-pine-beach",
        "lat": 34.6805,
        "lng": 127.0855,
        "region": "jeolla",
        "maps_q": "율포솔밭해수욕장",
        "ko": {
            "name": "율포솔밭해수욕장",
            "desc": "보성 율포의 솔밭·해변. 녹차밭 여행과 함께 넣기 좋습니다.",
            "how": "보성·벌교에서 율포 방면 버스.",
            "address": "전남 보성군 회천면 율포리 율포솔밭해수욕장",
        },
        "en": {
            "name": "Yulpo Pine Grove Beach",
            "desc": "Boseong pine-grove beach — pair with green tea fields.",
            "how": "Bus from Boseong or Beolgyo toward Yulpo.",
            "address": "Yulpo Pine Beach, Yulpo-ri, Hoecheon-myeon, Boseong-gun",
        },
        "ja": ("栗浦松林海水浴場", "宝城・栗浦の松林ビーチ。", "宝城・筏橋から栗浦方面バス。"),
        "zh": ("栗浦松林海水浴场", "宝城栗浦松林海滩。", "宝城·筏桥乘往栗浦方向公交。"),
        "zh-Hant": ("栗浦松林海水浴場", "寶城栗浦松林海灘。", "寶城·筏橋乘往栗浦方向公車。"),
    },
    "남열해돋이해수욕장": {
        "slug": "namyeol-sunrise-beach",
        "lat": 34.4655,
        "lng": 127.4655,
        "region": "jeolla",
        "maps_q": "남열해돋이해수욕장",
        "ko": {
            "name": "남열해돋이해수욕장",
            "desc": "고흥의 일출 명소 해변. 남해 다도해 전망이 아름답습니다.",
            "how": "고흥에서 남열·도양 방면 버스·택시.",
            "address": "전남 고흥군 도양읍 봉암리 남열해돋이해수욕장",
        },
        "en": {
            "name": "Namyeol Sunrise Beach",
            "desc": "Goheung sunrise beach with South Sea archipelago views.",
            "how": "Bus/taxi from Goheung toward Namyeol / Doyang.",
            "address": "Namyeol Sunrise Beach, Bongam-ri, Doyang-eup, Goheung-gun",
        },
        "ja": ("南熱日の出海水浴場", "高興の日の出ビーチ。", "高興から南熱方面。"),
        "zh": ("南热日出海水浴场", "高兴日出海滩。", "高兴乘往南热方向。"),
        "zh-Hant": ("南熱日出海水浴場", "高興日出海灘。", "高興乘往南熱方向。"),
    },
    # —— 전북 ——
    "선유도해수욕장": {
        "slug": "seonyudo-beach",
        "lat": 35.8105,
        "lng": 126.4055,
        "region": "jeolla",
        "maps_q": "선유도해수욕장",
        "ko": {
            "name": "선유도해수욕장",
            "desc": "고군산군도 선유도의 맑은 해변. 다리·섬 트래킹과 함께 즐깁니다.",
            "how": "군산·새만금에서 선유도 방면 버스 후 섬 내 이동.",
            "address": "전북 군산시 옥도면 선유도리 선유도해수욕장",
        },
        "en": {
            "name": "Seonyudo Beach",
            "desc": "Clear beach on Seonyudo in the Gogunsan islands.",
            "how": "Bus from Gunsan / Saemangeum toward Seonyudo.",
            "address": "Seonyudo Beach, Seonyudo-ri, Okdo-myeon, Gunsan",
        },
        "ja": ("仙遊島海水浴場", "古群山群島・仙遊島のビーチ。", "群山・セマングムから仙遊島方面バス。"),
        "zh": ("仙游岛海水浴场", "古群山群岛仙游岛清澈海滩。", "群山·新万金乘往仙游岛方向公交。"),
        "zh-Hant": ("仙遊島海水浴場", "古群山群島仙遊島清澈海灘。", "群山·新萬金乘往仙遊島方向公車。"),
    },
    "변산해수욕장": {
        "slug": "byeonsan-beach",
        "lat": 35.6305,
        "lng": 126.4705,
        "region": "jeolla",
        "maps_q": "변산해수욕장",
        "ko": {
            "name": "변산해수욕장",
            "desc": "부안 변산반도의 대표 해변. 채석강·격포와 가까운 코스입니다.",
            "how": "부안·격포에서 버스·택시; 변산해수욕장 하차.",
            "address": "전북 부안군 변산면 대항리 변산해수욕장",
        },
        "en": {
            "name": "Byeonsan Beach",
            "desc": "Main beach on Buan’s Byeonsan Peninsula near Chaeseokgang.",
            "how": "Bus/taxi from Buan or Gyeokpo.",
            "address": "Byeonsan Beach, Daehang-ri, Byeonsan-myeon, Buan-gun",
        },
        "ja": ("辺山海水浴場", "扶安・辺山半島の代表ビーチ。", "扶安・格浦からバス・タクシー。"),
        "zh": ("边山海水浴场", "扶安边山半岛代表海滩。", "扶安·格浦乘公交或出租车。"),
        "zh-Hant": ("邊山海水浴場", "扶安邊山半島代表海灘。", "扶安·格浦乘公車或計程車。"),
    },
    "격포해수욕장": {
        "slug": "gyeokpo-beach",
        "lat": 35.6255,
        "lng": 126.4675,
        "region": "jeolla",
        "maps_q": "격포해수욕장",
        "ko": {
            "name": "격포해수욕장",
            "desc": "격포항·채석강 인근 해변. 서해 낙조와 항구 분위기를 함께 즐깁니다.",
            "how": "부안에서 격포 방면 버스; 격포해수욕장·격포항 하차.",
            "address": "전북 부안군 변산면 격포리 격포해수욕장",
        },
        "en": {
            "name": "Gyeokpo Beach",
            "desc": "Beach by Gyeokpo Port and Chaeseokgang — West Sea sunsets.",
            "how": "Bus from Buan toward Gyeokpo Port / beach.",
            "address": "Gyeokpo Beach, Gyeokpo-ri, Byeonsan-myeon, Buan-gun",
        },
        "ja": ("格浦海水浴場", "格浦港・彩石江近くのビーチ。", "扶安から格浦方面バス。"),
        "zh": ("格浦海水浴场", "格浦港·彩石江附近海滩。", "扶安乘往格浦方向公交。"),
        "zh-Hant": ("格浦海水浴場", "格浦港·彩石江附近海灘。", "扶安乘往格浦方向公車。"),
    },
    # —— 충남 ——
    "대천해수욕장": {
        "slug": "daecheon-beach",
        "lat": 36.3055,
        "lng": 126.5155,
        "region": "chungcheong",
        "maps_q": "대천해수욕장",
        "ko": {
            "name": "대천해수욕장",
            "desc": "보령의 대표 서해 해변. 머드축제·대천항과 함께 유명합니다.",
            "how": "대천역·보령터미널에서 버스; 대천해수욕장 하차.",
            "address": "충남 보령시 신흑동 대천해수욕장",
        },
        "en": {
            "name": "Daecheon Beach",
            "desc": "Boryeong’s famous West Sea beach — mud festival and port nearby.",
            "how": "Bus from Daecheon Station or Boryeong terminal.",
            "address": "Daecheon Beach, Sinhuk-dong, Boryeong, Chungnam",
        },
        "ja": ("大川海水浴場", "保寧の代表西海ビーチ。マッドフェスで有名。", "大川駅・保寧ターミナルからバス。"),
        "zh": ("大川海水浴场", "保宁代表西海海滩，泥浆节出名。", "大川站或保宁巴士站乘公交。"),
        "zh-Hant": ("大川海水浴場", "保寧代表西海海灘，泥漿節出名。", "大川站或保寧巴士站乘公車。"),
    },
    "꽃지해수욕장": {
        "slug": "kkotji-beach",
        "lat": 36.5005,
        "lng": 126.3355,
        "region": "chungcheong",
        "maps_q": "꽃지해수욕장",
        "ko": {
            "name": "꽃지해수욕장",
            "desc": "태안 안면도의 할미·할아비 바위와 일몰로 유명한 해변.",
            "how": "태안·안면도에서 버스·택시; 꽃지해수욕장 하차.",
            "address": "충남 태안군 안면읍 승언리 꽃지해수욕장",
        },
        "en": {
            "name": "Kkotji Beach",
            "desc": "Anmyeondo beach famous for Halmi/Harabi rocks and sunsets.",
            "how": "Bus/taxi from Taean or Anmyeondo to Kkotji.",
            "address": "Kkotji Beach, Seungeon-ri, Anmyeon-eup, Taean-gun",
        },
        "ja": ("花地海水浴場", "泰安・安眠島の夕日ビーチ。", "泰安・安眠島からバス・タクシー。"),
        "zh": ("花地海水浴场", "泰安安眠岛日落与岩石出名。", "泰安·安眠岛乘公交或出租车。"),
        "zh-Hant": ("花地海水浴場", "泰安安眠島日落與岩石出名。", "泰安·安眠島乘公車或計程車。"),
    },
    "만리포해수욕장": {
        "slug": "manripo-beach",
        "lat": 36.7855,
        "lng": 126.1455,
        "region": "chungcheong",
        "maps_q": "만리포해수욕장",
        "ko": {
            "name": "만리포해수욕장",
            "desc": "태안 북부의 서해 해변. 일몰·오토캠핑으로 인기입니다.",
            "how": "태안에서 만리포 방면 버스.",
            "address": "충남 태안군 소원면 모항리 만리포해수욕장",
        },
        "en": {
            "name": "Manripo Beach",
            "desc": "Northern Taean West Sea beach — sunsets and camping.",
            "how": "Bus from Taean toward Manripo.",
            "address": "Manripo Beach, Mohang-ri, Sowon-myeon, Taean-gun",
        },
        "ja": ("万里浦海水浴場", "泰安北部の西海ビーチ。", "泰安から万里浦方面バス。"),
        "zh": ("万里浦海水浴场", "泰安北部西海海滩。", "泰安乘往万里浦方向公交。"),
        "zh-Hant": ("萬里浦海水浴場", "泰安北部西海海灘。", "泰安乘往萬里浦方向公車。"),
    },
    "춘장대해수욕장": {
        "slug": "chunjangdae-beach",
        "lat": 36.1605,
        "lng": 126.5355,
        "region": "chungcheong",
        "maps_q": "춘장대해수욕장",
        "ko": {
            "name": "춘장대해수욕장",
            "desc": "서천의 솔숲·백사장 해변. 가족 피서지로 알려져 있습니다.",
            "how": "서천·장항에서 버스·택시; 춘장대 하차.",
            "address": "충남 서천군 서면 도둔리 춘장대해수욕장",
        },
        "en": {
            "name": "Chunjangdae Beach",
            "desc": "Seocheon pine-grove and sand beach — family summer favorite.",
            "how": "Bus/taxi from Seocheon or Janghang.",
            "address": "Chunjangdae Beach, Dodun-ri, Seo-myeon, Seocheon-gun",
        },
        "ja": ("春長台海水浴場", "舒川の松林ビーチ。", "舒川・長項からバス・タクシー。"),
        "zh": ("春长台海水浴场", "舒川松林白沙滩。", "舒川·长项乘公交或出租车。"),
        "zh-Hant": ("春長台海水浴場", "舒川松林白沙灘。", "舒川·長項乘公車或計程車。"),
    },
    "무창포해수욕장": {
        "slug": "muchangpo-beach",
        "lat": 36.2405,
        "lng": 126.5355,
        "region": "chungcheong",
        "maps_q": "무창포해수욕장",
        "ko": {
            "name": "무창포해수욕장",
            "desc": "보령의 ‘신비의 바닷길’로 유명한 서해 해변.",
            "how": "보령·대천에서 무창포 방면 버스.",
            "address": "충남 보령시 웅천읍 열린리 무창포해수욕장",
        },
        "en": {
            "name": "Muchangpo Beach",
            "desc": "Boryeong beach famous for the ‘Mystic Sea Road’ tidal path.",
            "how": "Bus from Boryeong or Daecheon toward Muchangpo.",
            "address": "Muchangpo Beach, Yeollin-ri, Ungcheon-eup, Boryeong",
        },
        "ja": ("茂昌浦海水浴場", "保寧の「神秘の海道」で有名。", "保寧・大川から茂昌浦方面バス。"),
        "zh": ("茂昌浦海水浴场", "保宁以“神秘的海路”闻名。", "保宁·大川乘往茂昌浦方向公交。"),
        "zh-Hant": ("茂昌浦海水浴場", "保寧以「神秘的海路」聞名。", "保寧·大川乘往茂昌浦方向公車。"),
    },
    # —— 울산 ——
    "일산해수욕장": {
        "slug": "ulsan-ilsan-beach",
        "lat": 35.4955,
        "lng": 129.4305,
        "region": "gyeongsang",
        "maps_q": "울산 일산해수욕장",
        "ko": {
            "name": "일산해수욕장",
            "desc": "울산 동구의 동해 해변. 대왕암공원·울기등대와 가깝습니다. (경기 일산과 다름)",
            "how": "울산 시내버스·택시; 일산해수욕장·대왕암 하차.",
            "address": "울산 동구 해수욕장5길 일산해수욕장",
        },
        "en": {
            "name": "Ilsan Beach (Ulsan)",
            "desc": "East Sea beach in Ulsan’s Dong-gu near Daewangam — not Gyeonggi Ilsan.",
            "how": "City bus/taxi to Ilsan Beach / Daewangam.",
            "address": "Ilsan Beach, Haesuyokjang 5-gil, Dong-gu, Ulsan",
        },
        "ja": ("日山海水浴場（蔚山）", "蔚山東区のビーチ。京畿一山とは別。", "蔚山市内バス・タクシー。"),
        "zh": ("日山海水浴场（蔚山）", "蔚山东区东海海滩，非京畿一山。", "蔚山市内公交或出租车。"),
        "zh-Hant": ("日山海水浴場（蔚山）", "蔚山東區東海海灘，非京畿一山。", "蔚山市內公車或計程車。"),
    },
    "진하해수욕장": {
        "slug": "jinha-beach",
        "lat": 35.3855,
        "lng": 129.3455,
        "region": "gyeongsang",
        "maps_q": "진하해수욕장",
        "ko": {
            "name": "진하해수욕장",
            "desc": "울주군의 동해 해변. 진하·명선도와 이어지는 산책 코스입니다.",
            "how": "울산역·터미널에서 버스·택시; 진하해수욕장 하차.",
            "address": "울산 울주군 서생면 진하리 진하해수욕장",
        },
        "en": {
            "name": "Jinha Beach",
            "desc": "Ulju East Sea beach with walks toward Myeongseondo.",
            "how": "Bus/taxi from Ulsan Station or terminal to Jinha Beach.",
            "address": "Jinha Beach, Jinha-ri, Seosaeng-myeon, Ulju-gun, Ulsan",
        },
        "ja": ("珍下海水浴場", "蔚州の東海ビーチ。", "蔚山駅・ターミナルからバス・タクシー。"),
        "zh": ("珍下海水浴场", "蔚州东海海滩。", "蔚山站或巴士站乘公交/出租车。"),
        "zh-Hant": ("珍下海水浴場", "蔚州東海海灘。", "蔚山站或巴士站乘公車/計程車。"),
    },
}


def parse_list_names(path: Path) -> list[str]:
    """Parse Korean beach names from the filter file; skip headers and 없음; dedupe."""
    text = path.read_text(encoding="utf-8")
    names: list[str] = []
    seen: set[str] = set()
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith(("🌊", "🏙️", "🏢", "🌃", "🌴", "🏔️")):
            continue
        if line == "없음":
            continue
        if line in seen:
            continue
        seen.add(line)
        names.append(line)
    return names


def maps_urls(q: str, hl: str) -> tuple[str, str]:
    enc = quote(q)
    return (
        f"https://www.google.com/maps/search/?api=1&query={enc}",
        f"https://maps.google.com/maps?q={enc}&hl={hl}&z=15&output=embed",
    )


def body_block(ko: dict, en: dict, extras: dict[str, tuple]) -> list:
    texts = {
        "ko": f"{ko['desc']}\n\n가는 방법: {ko['how']}",
        "en": f"{en['desc']}\n\nHow to get there: {en['how']}",
    }
    for lang, tup in extras.items():
        texts[lang] = f"{tup[1]}\n\n{tup[2]}"
    return [{"type": "text", **texts}]


def locale_tuple(beach: dict, lang: str) -> tuple[str, str, str, str]:
    region = beach["region"]
    rl = REGION_LABELS[region][lang]
    if lang in ("ko", "en"):
        block = beach[lang]
        return block["name"], block["desc"], block["how"], rl
    if lang in ("ja", "zh", "zh-Hant"):
        name, desc, how = beach[lang]
        return name, desc, how, rl
    en = beach["en"]
    return en["name"], en["desc"], en["how"], rl


def entry_for_lang(lang: str, beach: dict) -> dict:
    ko, en = beach["ko"], beach["en"]
    slug = beach["slug"]
    hl = {"zh-Hant": "zh-TW", "zh": "zh-CN"}.get(lang, lang if lang != "ko" else "ko")
    maps, embed = maps_urls(beach["maps_q"], hl if lang != "en" else "en")
    img = f"Images/places/{slug}.jpg"
    region = beach["region"]
    rl_map = REGION_LABELS[region]
    if lang == "ko":
        base = {
            "name": ko["name"],
            "desc": ko["desc"],
            "how": ko["how"],
            "address": ko["address"],
            "regionLabel": rl_map["ko"],
            "region": region,
            "mapsUrl": maps,
            "mapsEmbedUrl": embed,
            "image": img,
        }
    elif lang == "en":
        base = {
            "name": en["name"],
            "desc": en["desc"],
            "how": en["how"],
            "address": en["address"],
            "regionLabel": rl_map["en"],
            "region": region,
            "mapsUrl": maps_urls(beach["maps_q"], "en")[0],
            "mapsEmbedUrl": maps_urls(beach["maps_q"], "en")[1],
            "image": img,
        }
    else:
        name, desc, how, region_label = locale_tuple(beach, lang)
        base = {
            "name": name,
            "desc": desc,
            "how": how,
            "address": en["address"] if lang in ("vi", "th", "ru") else ko["address"],
            "regionLabel": region_label,
            "region": region,
            "mapsUrl": maps,
            "mapsEmbedUrl": embed,
            "image": img,
        }
    extras = {L: locale_tuple(beach, L) for L in ("ja", "zh", "zh-Hant", "vi", "th", "ru")}
    base["body"] = body_block(ko, en, extras)
    return base


def migrate_existing(coords_text: str, beaches: list[dict]) -> tuple[str, list[str]]:
    migrated: list[str] = []
    for b in beaches:
        if not b.get("migrate"):
            continue
        slug = b["slug"]
        pat = re.compile(
            rf'(\{{\s*slug:\s*"{re.escape(slug)}"[^}}]*\}})',
            re.M,
        )
        m = pat.search(coords_text)
        if not m:
            print(f"WARN: migrate target missing in coords: {slug}")
            continue
        block = m.group(1)
        block2 = re.sub(r'type:\s*"[^"]*"', 'type: "beach"', block, count=1)
        note = b["en"]["name"].replace('"', '\\"')
        if "note:" in block2:
            block2 = re.sub(r'note:\s*"[^"]*"', f'note: "{note}"', block2, count=1)
        img = f"Images/places/{slug}.jpg"
        if "image:" in block2:
            block2 = re.sub(r'image:\s*"[^"]*"', f'image: "{img}"', block2, count=1)
        else:
            block2 = block2.rstrip(" }") + f', image: "{img}" }}'
        coords_text = coords_text[: m.start(1)] + block2 + coords_text[m.end(1) :]
        migrated.append(slug)
        print(f"migrated type→beach: {slug}")
    return coords_text, migrated


def patch_coords(beaches: list[dict]) -> tuple[list[str], list[str], list[str]]:
    text = COORDS.read_text(encoding="utf-8")
    text, migrated = migrate_existing(text, beaches)

    added: list[str] = []
    skipped: list[str] = []
    lines: list[str] = []
    for b in beaches:
        slug = b["slug"]
        if b.get("migrate"):
            continue
        if re.search(rf'slug:\s*"{re.escape(slug)}"', text):
            skipped.append(slug)
            print(f"skip existing slug: {slug}")
            continue
        img = f"Images/places/{slug}.jpg"
        note = b["en"]["name"].replace('"', '\\"')
        lines.append(
            "  { "
            f'slug: "{slug}", lat: {b["lat"]}, lng: {b["lng"]}, '
            f'region: "{b["region"]}", type: "beach", '
            f'note: "{note}", image: "{img}" '
            "},"
        )
        added.append(slug)

    if lines:
        insert = "\n".join(lines) + "\n"
        idx = text.rfind("];")
        if idx < 0:
            raise SystemExit("places-coords.js: cannot find ];")
        text = text[:idx] + insert + text[idx:]

    COORDS.write_text(text, encoding="utf-8", newline="\n")
    return added, migrated, skipped


def patch_i18n(beaches: list[dict], added: list[str], migrated: list[str]) -> None:
    sys.path.insert(0, str(ROOT / "tool"))
    from lib import i18n_store  # noqa: WPS433

    update_slugs = set(added) | set(migrated)
    if not update_slugs:
        print("i18n: nothing to update")
        return

    bundle = i18n_store.load_all()
    for lang in i18n_store.LANGS:
        data = bundle[lang]
        places = data.setdefault("places", {})
        n = 0
        for b in beaches:
            if b["slug"] not in update_slugs:
                continue
            places[b["slug"]] = entry_for_lang(lang, b)
            n += 1
        print(f"i18n {lang}: upserted {n} beaches")
    i18n_store.save_all(bundle)


def ensure_images(beaches: list[dict], slugs: list[str]) -> None:
    IMG.mkdir(parents=True, exist_ok=True)
    type_dir = IMG / "_types"
    type_dir.mkdir(parents=True, exist_ok=True)
    type_dst = type_dir / "beach.jpg"
    nature = type_dir / "nature.jpg"
    if not type_dst.exists():
        if nature.exists():
            shutil.copy2(nature, type_dst)
            print("wrote type fallback beach.jpg from nature.jpg")
        else:
            raise SystemExit("missing Images/places/_types/nature.jpg for beach fallback")

    slug_set = set(slugs)
    for b in beaches:
        slug = b["slug"]
        if slug not in slug_set:
            continue
        dest = IMG / f"{slug}.jpg"
        if dest.exists() and dest.stat().st_size > 5000:
            continue
        dest.write_bytes(type_dst.read_bytes())
        print(f"fallback image {dest.name}")


def main() -> int:
    if not LIST_FILE.is_file():
        raise SystemExit(f"list file missing: {LIST_FILE}")

    names = parse_list_names(LIST_FILE)
    missing = [n for n in names if n not in BEACHES]
    if missing:
        raise SystemExit(f"BEACHES meta missing for: {missing}")

    beaches = [BEACHES[n] for n in names]
    print(f"list unique beaches: {len(beaches)}")

    added, migrated, skipped = patch_coords(beaches)
    print(f"coords added={len(added)} migrated={len(migrated)} skipped={len(skipped)}")

    patch_i18n(beaches, added, migrated)
    ensure_images(beaches, added + migrated)

    sys.path.insert(0, str(ROOT / "tool"))
    from lib import i18n_store  # noqa: WPS433

    print(i18n_store.build_bundle())

    print("\n=== SUMMARY ===")
    print("ADDED:", ", ".join(added) if added else "(none)")
    print("MIGRATED:", ", ".join(migrated) if migrated else "(none)")
    print("SKIPPED:", ", ".join(skipped) if skipped else "(none)")
    print("LIST_SKIPPED: 대구/없음 + duplicate 만성리검은모래해변")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
