# -*- coding: utf-8 -*-
"""Add outdoor scenic places (type: nature) from the 야외명소 filter name list."""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
COORDS = ROOT / "data" / "places" / "places-coords.js"
IMG = ROOT / "Images" / "places"
TYPE_FALLBACK = IMG / "_types" / "nature.jpg"
SOURCE = Path(r"C:\Users\HwangInTae\Desktop\guide book\명소 추가할 자료\야외명소 필터 이름정보.txt")

LANGS = ("ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru")

REGION_HEADER = {
    "서울": "seoul",
    "부산": "busan",
    "인천": "incheon",
    "대구": "",
    "여수": "jeolla",
    "제주": "jeju",
}

REGION_LABELS = {
    "seoul": {
        "ko": "서울",
        "en": "Seoul",
        "ja": "ソウル",
        "zh": "首尔",
        "zh-Hant": "首爾",
        "vi": "Seoul",
        "th": "โซล",
        "ru": "Сеул",
    },
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
    "": {
        "ko": "대구",
        "en": "Daegu",
        "ja": "大邱",
        "zh": "大邱",
        "zh-Hant": "大邱",
        "vi": "Daegu",
        "th": "แทกู",
        "ru": "Тэгу",
    },
}

# Korean name → existing slug(s) already in places-coords.js (do not re-add)
ALREADY = {
    "한강공원": "hangang-yeouido / hangang-banpo",
    "남산공원": "namsan",
    "성산일출봉": "seongsan",
    "천지연폭포": "cheonjeyeon",
}

# Curated outdoor places keyed by Korean name from the source list
PLACES: dict[str, dict] = {
    "서울숲": {
        "slug": "seoul-forest",
        "lat": 37.5445,
        "lng": 127.0376,
        "maps_q": "서울숲",
        "ko": {
            "name": "서울숲",
            "desc": "성수동 한강변 대형 도시숲. 습지·동물원·잔디밭에서 피크닉과 산책하기 좋은 서울 대표 공원입니다.",
            "how": "분당선·경의중앙선 서울숲역 또는 2호선 뚝섬역에서 도보.",
            "address": "서울 성동구 뚝섬로 273",
        },
        "en": {
            "name": "Seoul Forest",
            "desc": "Large urban park in Seongsu — wetlands, lawns, and easy picnic walks by the Hangang.",
            "how": "Walk from Seoul Forest Station (Bundang / Gyeongui–Jungang) or Ttukseom (Line 2).",
            "address": "273 Ttukseom-ro, Seongdong-gu, Seoul",
        },
        "ja": ("ソウルの森", "聖水の漢江沿い都市公園。湿地・芝生でピクニック向き。", "盆唐線・京義中央線ソウルの森駅、または2号線トゥクソム駅から徒歩。"),
        "zh": ("首尔林", "圣水洞汉江边大型城市森林，适合散步和野餐。", "盆唐线·京义中央线首尔林站或2号线纛岛站步行。"),
        "zh-Hant": ("首爾林", "聖水洞漢江邊大型都市森林，適合散步和野餐。", "盆唐線·京義中央線首爾林站或2號線纛島站步行。"),
    },
    "북서울꿈의숲": {
        "slug": "bukseoul-kkumui-forest",
        "lat": 37.6208,
        "lng": 127.0438,
        "maps_q": "북서울꿈의숲",
        "ko": {
            "name": "북서울꿈의숲",
            "desc": "월계동 대형 공원. 전망대·호수·산책로가 있어 도심에서 여유로운 야외 시간을 보내기 좋습니다.",
            "how": "1·7호선 노원역·월계역에서 버스, 또는 공원 주차장 이용.",
            "address": "서울 강북구 월계로 173",
        },
        "en": {
            "name": "Buk Seoul Dream Forest",
            "desc": "Big north-Seoul park with viewpoints, a lake, and long walking paths.",
            "how": "Bus from Nowon or Wolgye Station (Lines 1/7), or park parking.",
            "address": "173 Wolgye-ro, Gangbuk-gu, Seoul",
        },
        "ja": ("北ソウル夢の森", "展望台・湖・遊歩道がある大型公園。", "1・7号線ノウォン・月渓駅からバス。"),
        "zh": ("北首尔梦之林", "有观景台、湖水和步道的大型公园。", "1·7号线芦原·月溪站转公交。"),
        "zh-Hant": ("北首爾夢之林", "有觀景台、湖水和步道的大型公園。", "1·7號線蘆原·月溪站轉公車。"),
    },
    "청계천": {
        "slug": "cheonggyecheon",
        "lat": 37.5695,
        "lng": 126.9788,
        "maps_q": "청계천",
        "ko": {
            "name": "청계천",
            "desc": "광화문·동대문을 잇는 도심 하천 산책로. 낮에는 산책, 저녁에는 조명이 아름다운 서울 대표 야외 코스입니다.",
            "how": "1·2호선 시청·종각·을지로3가·동대문역사문화공원역에서 청계천 방향 도보.",
            "address": "서울 종로구·중구 청계천로 일대",
        },
        "en": {
            "name": "Cheonggyecheon",
            "desc": "Restored downtown stream walk from Gwanghwamun toward Dongdaemun — day strolls and evening lights.",
            "how": "Walk from City Hall, Jonggak, Euljiro 3-ga, or Dongdaemun History & Culture Park stations.",
            "address": "Cheonggyecheon-ro area, Jongno-gu / Jung-gu, Seoul",
        },
        "ja": ("清渓川", "光化門〜東大門の都心河川遊歩道。夜のライトアップが人気。", "市庁・鐘閣・乙支路3街・東大門歴史文化公園駅から徒歩。"),
        "zh": ("清溪川", "连接光化门与东大门的市中心溪流步道，夜间灯光很美。", "市厅·钟阁·乙支路3街·东大门历史文化公园站步行。"),
        "zh-Hant": ("清溪川", "連接光化門與東大門的市中心溪流步道，夜間燈光很美。", "市廳·鐘閣·乙支路3街·東大門歷史文化公園站步行。"),
    },
    "낙산공원": {
        "slug": "naksan-park",
        "lat": 37.5806,
        "lng": 127.0075,
        "maps_q": "낙산공원",
        "ko": {
            "name": "낙산공원",
            "desc": "혜화·동대문 인근 성곽 공원. 서울 야경과 한양도성 성벽을 따라 걷기 좋은 전망 명소입니다.",
            "how": "4호선 혜화역 또는 1·4호선 동대문역에서 성곽길·낙산공원 방향 도보.",
            "address": "서울 종로구 낙산길 41",
        },
        "en": {
            "name": "Naksan Park",
            "desc": "Hilltop park by the Seoul City Wall — sunset views and fortress walks near Hyehwa.",
            "how": "Walk from Hyehwa (Line 4) or Dongdaemun (Lines 1/4) toward the city wall trail.",
            "address": "41 Naksan-gil, Jongno-gu, Seoul",
        },
        "ja": ("駱山公園", "漢陽都城の城壁と夜景が楽しめる丘の公園。", "4号線恵化駅または東大門駅から城壁方面徒歩。"),
        "zh": ("骆山公园", "惠化·东大门附近城墙公园，夜景与城郭步道有名。", "4号线惠化站或东大门站向城墙方向步行。"),
        "zh-Hant": ("駱山公園", "惠化·東大門附近城牆公園，夜景與城郭步道有名。", "4號線惠化站或東大門站向城牆方向步行。"),
    },
    "서울식물원": {
        "slug": "seoul-botanic-park",
        "lat": 37.5694,
        "lng": 126.8350,
        "maps_q": "서울식물원",
        "ko": {
            "name": "서울식물원",
            "desc": "마곡 대형 식물원·호수공원. 온실·주제정원과 산책로가 있어 하루 코스로 즐기기 좋습니다.",
            "how": "5·9호선 마곡나루역 또는 5호선 발산역에서 도보·버스.",
            "address": "서울 강서구 마곡동로 161",
        },
        "en": {
            "name": "Seoul Botanic Park",
            "desc": "Magok’s big botanic garden and lake park — greenhouse, themed gardens, and long walks.",
            "how": "Walk/bus from Magongnaru (Lines 5/9) or Balsan (Line 5).",
            "address": "161 Magokdong-ro, Gangseo-gu, Seoul",
        },
        "ja": ("ソウル植物園", "麻谷の大型植物園・湖公園。温室とテーマ庭園。", "5・9号線麻谷ナル駅または5号線鉢山駅から。"),
        "zh": ("首尔植物园", "麻谷大型植物园与湖公园，有温室和主题庭园。", "5·9号线麻谷渡口站或5号线钵山站。"),
        "zh-Hant": ("首爾植物園", "麻谷大型植物園與湖公園，有溫室和主題庭園。", "5·9號線麻谷渡口站或5號線鉢山站。"),
    },
    "올림픽공원": {
        "slug": "olympic-park",
        "lat": 37.5210,
        "lng": 127.1215,
        "maps_q": "서울 올림픽공원",
        "ko": {
            "name": "올림픽공원",
            "desc": "88올림픽 유산이 남은 대형 공원. 조각공원·호수·잔디밭과 콘서트·산책 코스로 사랑받습니다.",
            "how": "5·9호선 올림픽공원역 또는 8호선 몽촌토성·강동역에서 도보.",
            "address": "서울 송파구 올림픽로 424",
        },
        "en": {
            "name": "Olympic Park",
            "desc": "Vast Songpa park from the 1988 Olympics — sculptures, lakes, lawns, and event walks.",
            "how": "Walk from Olympic Park (Lines 5/9) or Mongchontoseong / Gangdong (Line 8).",
            "address": "424 Olympic-ro, Songpa-gu, Seoul",
        },
        "ja": ("オリンピック公園", "88五輪遺産の大型公園。彫刻・湖・芝生が広がる。", "5・9号線オリンピック公園駅などから徒歩。"),
        "zh": ("奥林匹克公园", "88奥运遗产大型公园，雕塑、湖泊与草坪适合散步。", "5·9号线奥林匹克公园站等步行。"),
        "zh-Hant": ("奧林匹克公園", "88奧運遺產大型公園，雕塑、湖泊與草坪適合散步。", "5·9號線奧林匹克公園站等步行。"),
    },
    "태종대": {
        "slug": "taejongdae",
        "lat": 35.0525,
        "lng": 129.0875,
        "maps_q": "태종대",
        "ko": {
            "name": "태종대",
            "desc": "영도 끝 절벽·소나무 숲 명소. 다누비열차와 등대 전망으로 부산 바다를 한눈에 볼 수 있습니다.",
            "how": "부산역·남포에서 버스·택시로 영도 태종대. 공원 내 다누비열차 이용 가능.",
            "address": "부산 영도구 전망로 24",
        },
        "en": {
            "name": "Taejongdae",
            "desc": "Clifftop pine park on Yeongdo — Danubi train and lighthouse views over Busan’s sea.",
            "how": "Bus/taxi from Busan Station or Nampo to Yeongdo Taejongdae; Danubi train inside the park.",
            "address": "24 Jeonmang-ro, Yeongdo-gu, Busan",
        },
        "ja": ("太宗台", "影島の断崖と松林。ダヌビ列車と灯台展望が人気。", "釜山駅・南浦からバス/タクシーで影島太宗台。"),
        "zh": ("太宗台", "影岛悬崖与松林，丹纳比列车和灯塔观景有名。", "釜山站·南浦乘公交或出租车至影岛太宗台。"),
        "zh-Hant": ("太宗台", "影島懸崖與松林，丹納比列車和燈塔觀景有名。", "釜山站·南浦乘公車或計程車至影島太宗台。"),
    },
    "오륙도": {
        "slug": "oryukdo",
        "lat": 35.1015,
        "lng": 129.1225,
        "maps_q": "오륙도 스카이워크",
        "ko": {
            "name": "오륙도",
            "desc": "부산 앞바다의 섬 군락. 스카이워크와 해안 산책로에서 동해·남해가 만나는 풍경을 볼 수 있습니다.",
            "how": "부산 2호선 경성대·부경대역에서 버스·택시, 또는 이기대·오륙도 해안 코스 연결.",
            "address": "부산 남구 오륙도길 일대",
        },
        "en": {
            "name": "Oryukdo",
            "desc": "Offshore islets off Busan — skywalk and coastal paths where East and South seas meet.",
            "how": "Bus/taxi from Kyungsung Univ. / Pukyong Nat’l Univ. Station; links to Igidae coastal trail.",
            "address": "Oryukdo-gil area, Nam-gu, Busan",
        },
        "ja": ("五六島", "釜山沖の島々。スカイウォークと海岸遊歩道が人気。", "2号線慶星大・釜慶大駅からバス/タクシー。"),
        "zh": ("五六岛", "釜山近海岛屿群，天空步道与海岸步道可看海景。", "2号线庆星大·釜庆大站转公交或出租车。"),
        "zh-Hant": ("五六島", "釜山近海島嶼群，天空步道與海岸步道可看海景。", "2號線慶星大·釜慶大站轉公車或計程車。"),
    },
    "이기대 해안산책로": {
        "slug": "igidae-coastal-trail",
        "lat": 35.1185,
        "lng": 129.1220,
        "maps_q": "이기대 해안산책로",
        "ko": {
            "name": "이기대 해안산책로",
            "desc": "남구 해안 절벽 트레일. 오륙도와 이어지는 바다·바위 풍경으로 부산 대표 산책 코스입니다.",
            "how": "부산 2호선 경성대·부경대역에서 버스·택시로 이기대 입구.",
            "address": "부산 남구 용호동 이기대 일대",
        },
        "en": {
            "name": "Igidae Coastal Trail",
            "desc": "Cliffside coastal walk in Nam-gu — rocky seascapes linking toward Oryukdo.",
            "how": "Bus/taxi from Kyungsung Univ. / Pukyong Nat’l Univ. Station to Igidae trailheads.",
            "address": "Yongho-dong Igidae area, Nam-gu, Busan",
        },
        "ja": ("二妓台海岸遊歩道", "南区の断崖トレイル。五六島へ続く海の絶景。", "2号線慶星大・釜慶大駅からバス/タクシー。"),
        "zh": ("二妓台海岸步道", "南区悬崖海岸步道，景色通往五六岛。", "2号线庆星大·釜庆大站转公交或出租车。"),
        "zh-Hant": ("二妓台海岸步道", "南區懸崖海岸步道，景色通往五六島。", "2號線慶星大·釜慶大站轉公車或計程車。"),
    },
    "을숙도": {
        "slug": "eulsukdo",
        "lat": 35.1085,
        "lng": 128.9455,
        "maps_q": "을숙도",
        "ko": {
            "name": "을숙도",
            "desc": "낙동강 하구 철새·습지 생태 섬. 탐방로와 생태공원에서 자연을 가까이 볼 수 있습니다.",
            "how": "부산 1호선 하단역에서 버스·택시로 을숙도 생태공원.",
            "address": "부산 사하구 낙동남로 1240",
        },
        "en": {
            "name": "Eulsukdo",
            "desc": "Nakdong estuary wetland island — birdwatching trails and eco-park walks.",
            "how": "Bus/taxi from Hadan Station (Line 1) to Eulsukdo Ecological Park.",
            "address": "1240 Nakdongnam-ro, Saha-gu, Busan",
        },
        "ja": ("乙淑島", "洛東江河口の渡り鳥・湿地の島。探訪路が整備。", "1号線下端駅からバス/タクシー。"),
        "zh": ("乙淑岛", "洛东江河口候鸟湿地岛，有生态探访路。", "1号线下端站转公交或出租车。"),
        "zh-Hant": ("乙淑島", "洛東江河口候鳥濕地島，有生態探訪路。", "1號線下端站轉公車或計程車。"),
    },
    "다대포 주변 자연경관": {
        "slug": "dadaepo-nature",
        "lat": 35.0475,
        "lng": 128.9665,
        "maps_q": "다대포 해수욕장",
        "ko": {
            "name": "다대포 주변 자연경관",
            "desc": "낙동강이 바다와 만나는 다대포 일대. 석양·갯벌·해안 산책으로 부산 서쪽 자연을 즐기기 좋습니다.",
            "how": "부산 1호선 다대포해수욕장역에서 해변·몰운대 방향 도보.",
            "address": "부산 사하구 다대동 일대",
        },
        "en": {
            "name": "Dadaepo Nature Scenery",
            "desc": "Where the Nakdong meets the sea — sunsets, mudflats, and west-Busan coastal walks.",
            "how": "Walk from Dadaepo Beach Station (Line 1) toward the shore and Molundae.",
            "address": "Dadae-dong area, Saha-gu, Busan",
        },
        "ja": ("多大浦周辺の自然", "洛東江が海と出会う一带。夕日と海岸散策が人気。", "1号線多大浦海水浴場駅から徒歩。"),
        "zh": ("多大浦周边自然景观", "洛东江入海口一带，日落与海岸散步很美。", "1号线多大浦海水浴场站步行。"),
        "zh-Hant": ("多大浦周邊自然景觀", "洛東江入海口一帶，日落與海岸散步很美。", "1號線多大浦海水浴場站步行。"),
    },
    "소래습지생태공원": {
        "slug": "sorae-wetland",
        "lat": 37.4015,
        "lng": 126.7425,
        "maps_q": "소래습지생태공원",
        "ko": {
            "name": "소래습지생태공원",
            "desc": "인천 남동 갯벌·염전 생태공원. 철새와 갈대밭 산책로로 도심 가까운 자연 명소입니다.",
            "how": "수인분당선 소래포구역에서 버스·택시, 또는 공원 주차장.",
            "address": "인천 남동구 소래로154번길 77",
        },
        "en": {
            "name": "Sorae Wetland Ecological Park",
            "desc": "Tidal flat and salt-field eco-park — reed walks and birdwatching near Incheon.",
            "how": "Bus/taxi from Soraepogu Station (Suin–Bundang), or park parking.",
            "address": "77 Sorae-ro 154beon-gil, Namdong-gu, Incheon",
        },
        "ja": ("蘇莱湿地生態公園", "干潟・塩田の生態公園。ヨシ原の遊歩道が人気。", "水仁盆唐線蘇莱浦口駅からバス/タクシー。"),
        "zh": ("苏莱湿地生态公园", "潮滩与盐田生态公园，适合看候鸟和芦苇散步。", "水仁盆唐线苏莱浦口站转公交或出租车。"),
        "zh-Hant": ("蘇萊濕地生態公園", "潮灘與鹽田生態公園，適合看候鳥和蘆葦散步。", "水仁盆唐線蘇萊浦口站轉公車或計程車。"),
    },
    "인천대공원": {
        "slug": "incheon-grand-park",
        "lat": 37.4585,
        "lng": 126.7545,
        "maps_q": "인천대공원",
        "ko": {
            "name": "인천대공원",
            "desc": "남동구 대형 종합공원. 호수·동물원·식물원·산책로가 있어 가족·피크닉 코스로 인기입니다.",
            "how": "인천 2호선 인천대공원역에서 도보, 또는 버스·택시.",
            "address": "인천 남동구 장수동 인천대공원",
        },
        "en": {
            "name": "Incheon Grand Park",
            "desc": "Large Namdong park with lake, zoo, botanical garden, and picnic lawns.",
            "how": "Walk from Incheon Grand Park Station (Incheon Line 2), or bus/taxi.",
            "address": "Jangsu-dong Incheon Grand Park, Namdong-gu, Incheon",
        },
        "ja": ("仁川大公園", "湖・動物園・植物園がある大型公園。", "仁川2号線仁川大公園駅から徒歩。"),
        "zh": ("仁川大公园", "有湖泊、动物园、植物园的大型公园。", "仁川2号线仁川大公园站步行。"),
        "zh-Hant": ("仁川大公園", "有湖泊、動物園、植物園的大型公園。", "仁川2號線仁川大公園站步行。"),
    },
    "무의도": {
        "slug": "muui-do",
        "lat": 37.3915,
        "lng": 126.4135,
        "maps_q": "무의도",
        "ko": {
            "name": "무의도",
            "desc": "영종도 옆 섬. 하나개·실미 해수욕장과 등산·해안 산책으로 인천 근교 자연을 즐기기 좋습니다.",
            "how": "영종도에서 버스·택시로 무의대교 건너 진입. 섬 내 순환버스·택시 이용.",
            "address": "인천 중구 무의동 일대",
        },
        "en": {
            "name": "Muui Island",
            "desc": "Island beside Yeongjong — beaches, short hikes, and coastal walks near Incheon.",
            "how": "From Yeongjong, cross Muui Bridge by bus/taxi; use island shuttle/taxi.",
            "address": "Muui-dong area, Jung-gu, Incheon",
        },
        "ja": ("舞衣島", "永宗島横の島。海水浴と海岸散策が人気。", "永宗島から舞衣大橋経由でバス/タクシー。"),
        "zh": ("舞衣岛", "永宗岛旁岛屿，沙滩与海岸散步适合近郊游。", "从永宗岛经舞衣大桥乘公交或出租车。"),
        "zh-Hant": ("舞衣島", "永宗島旁島嶼，沙灘與海岸散步適合近郊遊。", "從永宗島經舞衣大橋乘公車或計程車。"),
    },
    "영종도": {
        "slug": "yeongjong-do",
        "lat": 37.4605,
        "lng": 126.5125,
        "maps_q": "영종도",
        "ko": {
            "name": "영종도",
            "desc": "인천공항이 있는 섬. 을왕리·왕산 해안과 공항 도시 풍경이 어우러진 인천 대표 근교 명소입니다.",
            "how": "공항철도·인천공항고속도로로 진입. 섬 내 버스·택시로 해변·전망 포인트 이동.",
            "address": "인천 중구 영종동 일대",
        },
        "en": {
            "name": "Yeongjong Island",
            "desc": "Island hosting Incheon Airport — Eurwangni coast and airport-city scenery.",
            "how": "AREX or airport expressway; bus/taxi to beaches and viewpoints on-island.",
            "address": "Yeongjong-dong area, Jung-gu, Incheon",
        },
        "ja": ("永宗島", "仁川空港がある島。乙旺里など海岸スポットも。", "空港鉄道・高速道路で入り、島内バス/タクシー。"),
        "zh": ("永宗岛", "仁川机场所在岛屿，乙旺里等海岸景点。", "机场铁路或高速进入，岛内公交或出租车。"),
        "zh-Hant": ("永宗島", "仁川機場所在島嶼，乙旺里等海岸景點。", "機場鐵路或高速進入，島內公車或計程車。"),
    },
    "강화도": {
        "slug": "ganghwa-do",
        "lat": 37.7465,
        "lng": 126.4885,
        "maps_q": "강화도",
        "ko": {
            "name": "강화도",
            "desc": "서해 역사·자연이 공존하는 큰 섬. 전등사·해안도로·갯벌 전망으로 당일·1박 여행에 적합합니다.",
            "how": "서울·인천에서 버스·자가용으로 강화대교 진입. 섬 내 버스·택시로 이동.",
            "address": "인천 강화군 일대",
        },
        "en": {
            "name": "Ganghwa Island",
            "desc": "Large west-coast island of history and nature — temples, coastal roads, and mudflat views.",
            "how": "Bus/car from Seoul or Incheon via Ganghwa Bridge; island bus/taxi.",
            "address": "Ganghwa-gun area, Incheon",
        },
        "ja": ("江華島", "西海の歴史と自然の島。伝灯寺や海岸道路が人気。", "ソウル・仁川から江華大橋経由でバス/車。"),
        "zh": ("江华岛", "西海历史与自然并存的大岛，适合一日或过夜游。", "从首尔·仁川经江华大桥乘公交或自驾。"),
        "zh-Hant": ("江華島", "西海歷史與自然並存的大島，適合一日或過夜遊。", "從首爾·仁川經江華大橋乘公車或自駕。"),
    },
    "백령도": {
        "slug": "baengnyeong-do",
        "lat": 37.9695,
        "lng": 124.6655,
        "maps_q": "백령도",
        "ko": {
            "name": "백령도",
            "desc": "서해 최북단 인근의 섬. 두무진 해안 절경과 청정 자연으로 인천 원거리 섬 여행의 하이라이트입니다.",
            "how": "인천항에서 여객선. 기상·운항 일정 확인 필수. 섬 내 택시·렌터카.",
            "address": "인천 옹진군 백령면 일대",
        },
        "en": {
            "name": "Baengnyeong Island",
            "desc": "Far northwest island — Dumujin cliffs and wild west-sea scenery (ferry trip).",
            "how": "Passenger ferry from Incheon Port; check weather/schedules. Taxi/rental on-island.",
            "address": "Baengnyeong-myeon area, Ongjin-gun, Incheon",
        },
        "ja": ("白翎島", "西海の絶景島。頭武津などの海岸が有名。", "仁川港から旅客船。運航・天候を確認。"),
        "zh": ("白翎岛", "西海远岛，头武津海岸绝景。需乘船前往。", "仁川港客轮；确认天气与班次。"),
        "zh-Hant": ("白翎島", "西海遠島，頭武津海岸絕景。需乘船前往。", "仁川港客輪；確認天氣與班次。"),
    },
    "수성못": {
        "slug": "suseong-mot",
        "lat": 35.8295,
        "lng": 128.6175,
        "maps_q": "대구 수성못",
        "ko": {
            "name": "수성못",
            "desc": "대구 대표 호수공원. 산책로·카페거리·야경으로 시민과 여행객이 모이는 야외 명소입니다.",
            "how": "대구 3호선 수성구민운동장역·황금역에서 도보·버스.",
            "address": "대구 수성구 무학로 수성못 일대",
        },
        "en": {
            "name": "Suseong Lake",
            "desc": "Daegu’s signature lake park — lakeside walks, cafés, and evening lights.",
            "how": "Walk/bus from Suseong Stadium or Hwanggeum Station (Daegu Line 3).",
            "address": "Suseongmot area, Muhak-ro, Suseong-gu, Daegu",
        },
        "ja": ("寿城池", "大邱を代表する湖公園。散歩と夜景が人気。", "大邱3号線寿城区民運動場・黄金駅から。"),
        "zh": ("寿城池", "大邱代表湖公园，散步道与夜景很受欢迎。", "大邱3号线寿城运动场·黄金站。"),
        "zh-Hant": ("壽城池", "大邱代表湖公園，散步道與夜景很受歡迎。", "大邱3號線壽城運動場·黃金站。"),
    },
    "달성습지": {
        "slug": "dalseong-wetland",
        "lat": 35.8455,
        "lng": 128.4685,
        "maps_q": "달성습지",
        "ko": {
            "name": "달성습지",
            "desc": "금호강·낙동강이 만나는 습지. 철새와 갈대 풍경을 볼 수 있는 대구의 생태 야외 명소입니다.",
            "how": "대구 시내 버스·택시로 달성습지 생태학습관·탐방로 입구.",
            "address": "대구 달성군·달서구 달성습지 일대",
        },
        "en": {
            "name": "Dalseong Wetland",
            "desc": "Wetland where Geumho and Nakdong rivers meet — reeds and migratory birds near Daegu.",
            "how": "City bus/taxi to Dalseong Wetland eco-center and trailheads.",
            "address": "Dalseong Wetland area, Dalseong-gun / Dalseo-gu, Daegu",
        },
        "ja": ("達城湿地", "琴湖江・洛東江が出会う湿地。渡り鳥の観察地。", "大邱市内バス/タクシーで探訪路入口へ。"),
        "zh": ("达成湿地", "琴湖江与洛东江交汇湿地，可观候鸟。", "大邱市内公交或出租车至探访路入口。"),
        "zh-Hant": ("達成濕地", "琴湖江與洛東江交匯濕地，可觀候鳥。", "大邱市內公車或計程車至探訪路入口。"),
    },
    "두류공원": {
        "slug": "duryu-park",
        "lat": 35.8555,
        "lng": 128.5615,
        "maps_q": "대구 두류공원",
        "ko": {
            "name": "두류공원",
            "desc": "대구 도심 대형 공원. 83타워·산책로·잔디밭이 있어 휴식과 야경을 함께 즐기기 좋습니다.",
            "how": "대구 2호선 두류역에서 도보.",
            "address": "대구 달서구 두류공원로 200",
        },
        "en": {
            "name": "Duryu Park",
            "desc": "Central Daegu park with E-World / 83 Tower views, lawns, and easy walks.",
            "how": "Walk from Duryu Station (Daegu Line 2).",
            "address": "200 Duryugongwon-ro, Dalseo-gu, Daegu",
        },
        "ja": ("頭流公園", "大邱都心の大型公園。83タワーと散歩道。", "大邱2号線頭流駅から徒歩。"),
        "zh": ("头流公园", "大邱市中心大型公园，可看83塔与散步。", "大邱2号线头流站步行。"),
        "zh-Hant": ("頭流公園", "大邱市中心大型公園，可看83塔與散步。", "大邱2號線頭流站步行。"),
    },
    "오동도": {
        "slug": "odongdo",
        "lat": 34.7445,
        "lng": 127.7665,
        "maps_q": "여수 오동도",
        "ko": {
            "name": "오동도",
            "desc": "여수 앞바다의 섬 공원. 동백숲·방파제 산책과 등대 전망으로 여수 여행의 기본 코스입니다.",
            "how": "여수엑스포역·시내에서 버스·택시. 방파제 걸어 진입 또는 유람선.",
            "address": "전남 여수시 수정동 오동도",
        },
        "en": {
            "name": "Odongdo",
            "desc": "Island park off Yeosu — camellia forest, breakwater walk, and lighthouse views.",
            "how": "Bus/taxi from Yeosu Expo / downtown; walk the breakwater or take a cruise boat.",
            "address": "Odongdo, Sujeong-dong, Yeosu",
        },
        "ja": ("梧桐島", "麗水沖の島公園。椿の森と防波堤散歩が人気。", "麗水エキスポ・市内からバス/タクシー。"),
        "zh": ("梧桐岛", "丽水近海岛公园，山茶林与防波堤散步。", "丽水世博·市区乘公交或出租车。"),
        "zh-Hant": ("梧桐島", "麗水近海島公園，山茶林與防波堤散步。", "麗水世博·市區乘公車或計程車。"),
    },
    "돌산도": {
        "slug": "dolsando",
        "lat": 34.7305,
        "lng": 127.7455,
        "maps_q": "여수 돌산도",
        "ko": {
            "name": "돌산도",
            "desc": "돌산대교로 이어지는 섬. 향일암·해안도로·카페 전망으로 여수 야경과 바다를 즐기기 좋습니다.",
            "how": "돌산대교 건너 버스·택시. 향일암·돌산공원 등 포인트로 이동.",
            "address": "전남 여수시 돌산읍 일대",
        },
        "en": {
            "name": "Dolsan Island",
            "desc": "Island linked by Dolsan Bridge — Hyangiram, coastal roads, and Yeosu night views.",
            "how": "Cross Dolsan Bridge by bus/taxi; continue to Hyangiram or Dolsan Park.",
            "address": "Dolsan-eup area, Yeosu",
        },
        "ja": ("突山島", "突山大橋でつながる島。向日庵と海岸道路が人気。", "突山大橋を渡りバス/タクシー。"),
        "zh": ("突山岛", "经突山大桥连接，向日庵与海岸公路有名。", "过突山大桥后乘公交或出租车。"),
        "zh-Hant": ("突山島", "經突山大橋連接，向日庵與海岸公路有名。", "過突山大橋後乘公車或計程車。"),
    },
    "금오도": {
        "slug": "geumodo",
        "lat": 34.5285,
        "lng": 127.7555,
        "maps_q": "여수 금오도",
        "ko": {
            "name": "금오도",
            "desc": "여수 비응항에서 배로 가는 섬. 비렁길 해안 절벽 트레일로 남해 비경을 걷는 명소입니다.",
            "how": "여수 비응항·국동항 등에서 여객선. 섬 내 버스·택시로 비렁길 코스.",
            "address": "전남 여수시 남면 금오도",
        },
        "en": {
            "name": "Geumo Island",
            "desc": "Ferry island from Yeosu — famous Birang-gil cliff coastal trail.",
            "how": "Passenger ferry from Biung / Gukdong; bus/taxi to Birang-gil trailheads.",
            "address": "Geumodo, Nam-myeon, Yeosu",
        },
        "ja": ("金鰲島", "麗水から船で行く島。ビロングィル断崖トレイルが有名。", "飛鷹港などから旅客船。"),
        "zh": ("金鳌岛", "从丽水乘船前往，以飞龙崖海岸步道闻名。", "飞鹰港等乘客轮。"),
        "zh-Hant": ("金鰲島", "從麗水乘船前往，以飛龍崖海岸步道聞名。", "飛鷹港等乘客輪。"),
    },
    "거문도": {
        "slug": "geomundo",
        "lat": 34.0255,
        "lng": 127.3085,
        "maps_q": "여수 거문도",
        "ko": {
            "name": "거문도",
            "desc": "여수에서 배로 가는 다도해 섬. 등대·해안 산책과 백도 유람의 거점으로 쓰입니다.",
            "how": "여수여객터미널에서 거문도행 여객선. 운항·기상 확인 필수.",
            "address": "전남 여수시 삼산면 거문도",
        },
        "en": {
            "name": "Geomun Island",
            "desc": "Remote Yeosu island — lighthouse walks and gateway cruises toward Baekdo islets.",
            "how": "Ferry from Yeosu Passenger Terminal; check schedules and weather.",
            "address": "Geomundo, Samsan-myeon, Yeosu",
        },
        "ja": ("巨文島", "麗水から船で行く多島海の島。灯台散歩と白島クルーズ拠点。", "麗水旅客ターミナルから旅客船。"),
        "zh": ("巨文岛", "从丽水乘船前往，灯塔散步与白岛游船据点。", "丽水客运码头乘客轮。"),
        "zh-Hant": ("巨文島", "從麗水乘船前往，燈塔散步與白島遊船據點。", "麗水客運碼頭乘客輪。"),
    },
    "백도": {
        "slug": "baekdo",
        "lat": 34.0225,
        "lng": 127.3505,
        "maps_q": "여수 백도",
        "ko": {
            "name": "백도",
            "desc": "거문도 인근의 무인도 군락. 유람선으로만 볼 수 있는 기암 절벽과 남해 비경으로 유명합니다.",
            "how": "거문도 또는 여수에서 백도 유람선. 기상 시 운항이 취소될 수 있음.",
            "address": "전남 여수시 삼산면 백도 일대",
        },
        "en": {
            "name": "Baekdo Islets",
            "desc": "Uninhabited rock islets near Geomundo — cruise-only views of dramatic cliffs.",
            "how": "Sightseeing cruise from Geomundo or Yeosu; sailings may cancel in rough weather.",
            "address": "Baekdo area, Samsan-myeon, Yeosu",
        },
        "ja": ("白島", "巨文島近くの無人島群。遊覧船で見る奇岩が名所。", "巨文島または麗水から白島クルーズ。"),
        "zh": ("白岛", "巨文岛附近无人岛群，游船可见奇岩绝壁。", "巨文岛或丽水乘白岛游船。"),
        "zh-Hant": ("白島", "巨文島附近無人島群，遊船可見奇岩絕壁。", "巨文島或麗水乘白島遊船。"),
    },
    "여자만": {
        "slug": "yeojaman",
        "lat": 34.7555,
        "lng": 127.5205,
        "maps_q": "여자만",
        "ko": {
            "name": "여자만",
            "desc": "여수·순천·보성 사이 넓은 만. 갯벌·일몰·해안도로 풍경이 인상적인 남해 야외 명소입니다.",
            "how": "여수·순천에서 해안도로·버스·택시로 전망 포인트 이동.",
            "address": "전남 여수·순천·보성 여자만 일대",
        },
        "en": {
            "name": "Yeoja Bay",
            "desc": "Wide bay between Yeosu, Suncheon, and Boseong — mudflats, sunsets, and coastal drives.",
            "how": "Coastal road, bus, or taxi from Yeosu or Suncheon to viewpoints.",
            "address": "Yeoja Bay area, Yeosu / Suncheon / Boseong",
        },
        "ja": ("汝自湾", "麗水・順天・宝城の間の大きな湾。干潟と夕日が美しい。", "麗水・順天から海岸道路/バス/タクシー。"),
        "zh": ("汝自湾", "丽水·顺天·宝城之间的大海湾，滩涂与日落很美。", "从丽水·顺天沿海岸公路或乘公交出租车。"),
        "zh-Hant": ("汝自灣", "麗水·順天·寶城之間的大海灣，灘塗與日落很美。", "從麗水·順天沿海岸公路或乘公車計程車。"),
    },
    "장도": {
        "slug": "yeosu-jangdo",
        "lat": 34.7385,
        "lng": 127.7385,
        "maps_q": "여수 장도",
        "ko": {
            "name": "장도",
            "desc": "여수 엑스포·이순신광장 앞바다의 작은 섬. 보행교로 걸어가 바다 전망을 즐기기 좋습니다.",
            "how": "여수엑스포역·이순신광장에서 장도 보행교 도보.",
            "address": "전남 여수시 수정동 장도",
        },
        "en": {
            "name": "Jangdo (Yeosu)",
            "desc": "Small island off Yeosu Expo / Yi Sun-sin Square — walk the footbridge for bay views.",
            "how": "Walk the Jangdo footbridge from Yeosu Expo / Yi Sun-sin Square.",
            "address": "Jangdo, Sujeong-dong, Yeosu",
        },
        "ja": ("将島（麗水）", "エキスポ前の小さな島。歩行橋で渡れる海の眺め。", "麗水エキスポ・李舜臣広場から徒歩橋。"),
        "zh": ("将岛（丽水）", "世博·李舜臣广场前小岛，步行桥可观海。", "从丽水世博·李舜臣广场步行桥进入。"),
        "zh-Hant": ("將島（麗水）", "世博·李舜臣廣場前小島，步行橋可觀海。", "從麗水世博·李舜臣廣場步行橋進入。"),
    },
    "우도": {
        "slug": "udo",
        "lat": 33.5065,
        "lng": 126.9535,
        "maps_q": "제주 우도",
        "ko": {
            "name": "우도",
            "desc": "성산 앞바다의 소 모양 섬. 해안도로·검멀레·홍조단괴 해빈 등 제주 대표 섬 여행지입니다.",
            "how": "성산항에서 우도 여객선. 섬 내 버스·전기차·자전거 대여.",
            "address": "제주 제주시 우도면 일대",
        },
        "en": {
            "name": "Udo",
            "desc": "Cow-shaped island off Seongsan — coastal loops, Geommeolle, and coral-sand beaches.",
            "how": "Ferry from Seongsan Port; island bus, e-car, or bike rental.",
            "address": "Udo-myeon area, Jeju City",
        },
        "ja": ("牛島", "城山沖の牛の形の島。海岸道路とビーチが人気。", "城山港から旅客船。島内バス/電気自動車。"),
        "zh": ("牛岛", "城山近海牛形岛，海岸环线和沙滩很有名。", "城山港客轮；岛内公交或电动车。"),
        "zh-Hant": ("牛島", "城山近海牛形島，海岸環線和沙灘很有名。", "城山港客輪；島內公車或電動車。"),
    },
    "주상절리대": {
        "slug": "jusangjeolli",
        "lat": 33.2375,
        "lng": 126.4245,
        "maps_q": "중문 주상절리대",
        "ko": {
            "name": "주상절리대",
            "desc": "중문 해안 기둥 모양 화산암 절벽. 파도가 부딪히는 제주 남부 대표 지질 명소입니다.",
            "how": "중문관광단지 버스·택시. 주상절리대 입구에서 해안 산책로.",
            "address": "제주 서귀포시 이호동 주상절리대",
        },
        "en": {
            "name": "Jusangjeolli Cliff",
            "desc": "Columnar basalt cliffs on Jungmun coast — classic southern Jeju geology by the waves.",
            "how": "Bus/taxi in Jungmun tourist belt; coastal walk from the entrance.",
            "address": "Jusangjeolli, Iho-dong area, Seogwipo",
        },
        "ja": ("柱状節理帯", "中文海岸の柱状玄武岩の断崖。南済州の地質名所。", "中文観光団地からバス/タクシー。"),
        "zh": ("柱状节理带", "中文海岸柱状玄武岩悬崖，济州南部地质名所。", "中文旅游区乘公交或出租车。"),
        "zh-Hant": ("柱狀節理帶", "中文海岸柱狀玄武岩懸崖，濟州南部地質名所。", "中文旅遊區乘公車或計程車。"),
    },
    "비자림": {
        "slug": "bijarim",
        "lat": 33.4915,
        "lng": 126.8105,
        "maps_q": "비자림",
        "ko": {
            "name": "비자림",
            "desc": "수천 그루 비자나무 숲. 시원한 그늘 산책로로 제주 동부 대표 숲 명소입니다.",
            "how": "제주시·성산에서 버스·택시. 비자림 주차장·탐방로 입구.",
            "address": "제주 제주시 구좌읍 비자숲길 55",
        },
        "en": {
            "name": "Bijarim Forest",
            "desc": "Thousands of nutmeg yews — cool shaded trails in eastern Jeju.",
            "how": "Bus/taxi from Jeju City or Seongsan to Bijarim parking / trailhead.",
            "address": "55 Bijasup-gil, Gujwa-eup, Jeju City",
        },
        "ja": ("榧子林", "数千本のカヤの森。東済州の涼しい散歩道。", "済州市・城山からバス/タクシー。"),
        "zh": ("榧子林", "数千棵榧树森林，济州东部凉爽步道。", "济州市·城山乘公交或出租车。"),
        "zh-Hant": ("榧子林", "數千棵榧樹森林，濟州東部涼爽步道。", "濟州市·城山乘公車或計程車。"),
    },
    "사려니숲길": {
        "slug": "saryeoni-forest",
        "lat": 33.4305,
        "lng": 126.6765,
        "maps_q": "사려니숲길",
        "ko": {
            "name": "사려니숲길",
            "desc": "제주 중산간 숲길. 평탄한 산책로로 가벼운 트레킹과 삼림욕에 인기입니다.",
            "how": "제주시·서귀포에서 버스·택시로 사려니숲길 입구(붉은오름 등). 운영·통제 구간 확인.",
            "address": "제주 제주시 조천읍 사려니숲길",
        },
        "en": {
            "name": "Saryeoni Forest Path",
            "desc": "Mid-mountain Jeju forest trail — easy, mostly flat walks for light hiking.",
            "how": "Bus/taxi from Jeju City / Seogwipo to trailheads (e.g. Red Oreum). Check open sections.",
            "address": "Saryeoni Forest Path, Jocheon-eup, Jeju City",
        },
        "ja": ("サリョニの森道", "済州中山間の平坦な森の遊歩道。", "済州市・西帰浦から入口までバス/タクシー。"),
        "zh": ("思连伊林道", "济州中山间平坦森林步道，适合轻松徒步。", "济州市·西归浦乘公交或出租车至入口。"),
        "zh-Hant": ("思連伊林道", "濟州中山間平坦森林步道，適合輕鬆徒步。", "濟州市·西歸浦乘公車或計程車至入口。"),
    },
    "곶자왈": {
        "slug": "gotjawal",
        "lat": 33.3055,
        "lng": 126.2915,
        "maps_q": "제주 곶자왈",
        "ko": {
            "name": "곶자왈",
            "desc": "제주 특유의 용암 숲 지대. 돌무더기와 상록수림이 어우러진 탐방로에서 독특한 생태계를 볼 수 있습니다.",
            "how": "애월·한경·안덕 등 곶자왈 도립공원·생태공원 입구까지 버스·택시.",
            "address": "제주 제주시·서귀포시 곶자왈 일대",
        },
        "en": {
            "name": "Gotjawal Forest",
            "desc": "Jeju’s unique lava-forest terrain — rocky trails under evergreen canopy.",
            "how": "Bus/taxi to Gotjawal provincial / eco-park entrances (Aewol, Hangyeong, Andeok, etc.).",
            "address": "Gotjawal areas, Jeju City / Seogwipo",
        },
        "ja": ("コッジャワル", "済州独自の溶岩の森。岩と常緑樹林の探訪路。", "涯月・翰京・安德など入口までバス/タクシー。"),
        "zh": ("곶자왈熔岩林", "济州特有熔岩森林，岩石与常绿林探访路。", "涯月·翰京·安德等入口乘公交或出租车。"),
        "zh-Hant": ("곶자왈熔岩林", "濟州特有熔岩森林，岩石與常綠林探訪路。", "涯月·翰京·安德等入口乘公車或計程車。"),
    },
    "섭지코지": {
        "slug": "seopjikoji",
        "lat": 33.4245,
        "lng": 126.9305,
        "maps_q": "섭지코지",
        "ko": {
            "name": "섭지코지",
            "desc": "성산 인근 해안 곶. 붉은 화산송이 언덕과 등대·바다 전망으로 제주 동부 대표 포토 스폿입니다.",
            "how": "성산일출봉·성산에서 버스·택시. 주차 후 해안 산책.",
            "address": "제주 서귀포시 성산읍 섭지코지로",
        },
        "en": {
            "name": "Seopjikoji",
            "desc": "Coastal headland near Seongsan — red volcanic soil, lighthouse, and photo-famous sea views.",
            "how": "Bus/taxi from Seongsan Ilchulbong / Seongsan; park and walk the cape.",
            "address": "Seopjikoji-ro, Seongsan-eup, Seogwipo",
        },
        "ja": ("渉地コジ", "城山近くの岬。赤い火山灰の丘と灯台展望。", "城山日出峰・城山からバス/タクシー。"),
        "zh": ("涉地可支", "城山附近海岬，红火山土与灯塔海景。", "城山日出峰·城山乘公交或出租车。"),
        "zh-Hant": ("涉地可支", "城山附近海岬，紅火山土與燈塔海景。", "城山日出峰·城山乘公車或計程車。"),
    },
    "산굼부리": {
        "slug": "sangumburi",
        "lat": 33.4315,
        "lng": 126.6895,
        "maps_q": "산굼부리",
        "ko": {
            "name": "산굼부리",
            "desc": "평지형 화산 분화구. 둘레길에서 분화구 안 초원과 숲을 내려다보는 제주 중산간 명소입니다.",
            "how": "제주시·조천에서 버스·택시. 입장료·운영시간 확인.",
            "address": "제주 제주시 조천읍 교래리 산굼부리",
        },
        "en": {
            "name": "Sangumburi Crater",
            "desc": "Flat-land volcanic crater — rim walks overlooking grassland and forest inside.",
            "how": "Bus/taxi from Jeju City / Jocheon; check tickets and hours.",
            "address": "Sangumburi, Gyorae-ri, Jocheon-eup, Jeju City",
        },
        "ja": ("山君不里", "平地型の火山火口。周回路から草原と森を見下ろす。", "済州市・朝天からバス/タクシー。"),
        "zh": ("山君不里", "平地型火山口，环路可俯瞰草原与森林。", "济州市·朝天乘公交或出租车。"),
        "zh-Hant": ("山君不里", "平地型火山口，環路可俯瞰草原與森林。", "濟州市·朝天乘公車或計程車。"),
    },
    "정방폭포": {
        "slug": "jeongbang-falls",
        "lat": 33.2445,
        "lng": 126.5715,
        "maps_q": "정방폭포",
        "ko": {
            "name": "정방폭포",
            "desc": "바닷가로 떨어지는 서귀포 폭포. 천지연·천제연과 함께 제주 남부 폭포 코스에 넣기 좋습니다.",
            "how": "서귀포시내 버스·택시. 정방폭포 입구에서 도보.",
            "address": "제주 서귀포시 칠십리로214번길 37",
        },
        "en": {
            "name": "Jeongbang Falls",
            "desc": "Waterfall plunging toward the sea in Seogwipo — pair with Cheonjiyeon / Cheonjeyeon.",
            "how": "Bus/taxi in Seogwipo; short walk from the entrance.",
            "address": "37 Chilsimni-ro 214beon-gil, Seogwipo",
        },
        "ja": ("正房滝", "海に落ちる西帰浦の滝。天地淵・天帝淵とセットで。", "西帰浦市内バス/タクシー。"),
        "zh": ("正房瀑布", "落入海边的西归浦瀑布，可与天地渊·天帝渊一起逛。", "西归浦市内公交或出租车。"),
        "zh-Hant": ("正房瀑布", "落入海邊的西歸浦瀑布，可與天地淵·天帝淵一起逛。", "西歸浦市內公車或計程車。"),
    },
    "쇠소깍": {
        "slug": "soesoggak",
        "lat": 33.2525,
        "lng": 126.6225,
        "maps_q": "쇠소깍",
        "ko": {
            "name": "쇠소깍",
            "desc": "효돈천이 바다와 만나는 깊은 웅덩이. 투명 카약·산책으로 서귀포 대표 계곡·해안 명소입니다.",
            "how": "서귀포시내 버스·택시. 쇠소깍 주차장·산책로.",
            "address": "제주 서귀포시 쇠소깍로 104",
        },
        "en": {
            "name": "Soesoggak",
            "desc": "Deep estuary pool where Hyodon Stream meets the sea — clear kayaks and riverside walks.",
            "how": "Bus/taxi in Seogwipo to Soesoggak parking and trails.",
            "address": "104 Soesoggak-ro, Seogwipo",
        },
        "ja": ("ソソッカク", "川が海に出会う深い淵。カヤックと散歩が人気。", "西帰浦市内バス/タクシー。"),
        "zh": ("牛沼角", "川海交汇的深潭，透明皮划艇与散步很受欢迎。", "西归浦市内公交或出租车。"),
        "zh-Hant": ("牛沼角", "川海交匯的深潭，透明皮划艇與散步很受歡迎。", "西歸浦市內公車或計程車。"),
    },
    "용머리해안": {
        "slug": "yongmeori-coast",
        "lat": 33.2345,
        "lng": 126.3145,
        "maps_q": "용머리해안",
        "ko": {
            "name": "용머리해안",
            "desc": "산방산 아래 용의 머리 모양 해안. 밀물·썰물에 따라 탐방 가능 구간이 달라지는 지질 명소입니다.",
            "how": "중문·산방산 방면 버스·택시. 만조 시 출입 통제될 수 있으니 안내 확인.",
            "address": "제주 서귀포시 안덕면 사계리 용머리해안",
        },
        "en": {
            "name": "Yongmeori Coast",
            "desc": "Dragon-head coastal rocks under Sanbangsan — access depends on tides.",
            "how": "Bus/taxi toward Jungmun / Sanbangsan; check tide closures at the entrance.",
            "address": "Yongmeori Coast, Sagye-ri, Andeok-myeon, Seogwipo",
        },
        "ja": ("龍頭海岸", "山房山の下の龍の頭の形の海岸。潮により通行規制あり。", "中文・山房山方面バス/タクシー。"),
        "zh": ("龙头海岸", "山房山下龙头形海岸，涨潮时可能关闭。", "中文·山房山方向公交或出租车。"),
        "zh-Hant": ("龍頭海岸", "山房山下龍頭形海岸，漲潮時可能關閉。", "中文·山房山方向公車或計程車。"),
    },
    "만장굴": {
        "slug": "manjanggul",
        "lat": 33.5285,
        "lng": 126.7715,
        "maps_q": "만장굴",
        "ko": {
            "name": "만장굴",
            "desc": "세계자연유산 거문오름 용암동굴계의 대표 동굴. 시원한 지하 용암터널을 걸을 수 있습니다.",
            "how": "구좌·조천에서 버스·택시. 만장굴 주차장·매표소. 운영시간·통제 확인.",
            "address": "제주 제주시 구좌읍 만장굴길 182",
        },
        "en": {
            "name": "Manjanggul Cave",
            "desc": "UNESCO lava tube in the Geomunoreum system — walk a cool underground tunnel.",
            "how": "Bus/taxi from Gujwa / Jocheon to Manjanggul parking and ticket office; check hours.",
            "address": "182 Manjanggul-gil, Gujwa-eup, Jeju City",
        },
        "ja": ("万丈窟", "世界自然遺産の溶岩洞窟。涼しい地下トンネルを歩ける。", "旧左・朝天からバス/タクシー。"),
        "zh": ("万丈窟", "世界自然遗产熔岩洞穴，可步行地下熔岩隧道。", "旧左·朝天乘公交或出租车。"),
        "zh-Hant": ("萬丈窟", "世界自然遺產熔岩洞穴，可步行地下熔岩隧道。", "舊左·朝天乘公車或計程車。"),
    },
}


def parse_source(path: Path) -> list[tuple[str, str]]:
    """Return list of (region_key, korean_name)."""
    if not path.exists():
        raise SystemExit(f"source not found: {path}")
    items: list[tuple[str, str]] = []
    region = "seoul"
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        # Region headers like "🇰🇷 서울" or "🌃 여수"
        m = re.match(r"^[^\w가-힣]*([가-힣]+)\s*$", line)
        if m and m.group(1) in REGION_HEADER:
            region = REGION_HEADER[m.group(1)]
            continue
        # Strip leading emoji / symbols if any
        name = re.sub(r"^[^\w가-힣]+", "", line).strip()
        if not name or name in REGION_HEADER:
            continue
        items.append((region, name))
    return items


def existing_slugs(text: str) -> set[str]:
    return set(re.findall(r'slug:\s*"([^"]+)"', text))


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


def locale_tuple(place: dict, lang: str, region: str) -> tuple[str, str, str, str]:
    rl = REGION_LABELS.get(region, REGION_LABELS[""])[lang]
    if lang in ("ko", "en"):
        block = place[lang]
        return block["name"], block["desc"], block["how"], rl
    if lang in ("ja", "zh", "zh-Hant"):
        name, desc, how = place[lang]
        return name, desc, how, rl
    en = place["en"]
    return en["name"], en["desc"], en["how"], rl


def entry_for_lang(lang: str, place: dict, region: str) -> dict:
    ko, en = place["ko"], place["en"]
    slug = place["slug"]
    hl = {"zh-Hant": "zh-TW", "zh": "zh-CN"}.get(lang, lang if lang != "ko" else "ko")
    maps, embed = maps_urls(place["maps_q"], hl if lang != "en" else "en")
    img = f"Images/places/{slug}.jpg"
    rl_map = REGION_LABELS.get(region, REGION_LABELS[""])
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
            "mapsUrl": maps_urls(place["maps_q"], "en")[0],
            "mapsEmbedUrl": maps_urls(place["maps_q"], "en")[1],
            "image": img,
        }
    else:
        name, desc, how, region_label = locale_tuple(place, lang, region)
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
    extras = {L: locale_tuple(place, L, region) for L in ("ja", "zh", "zh-Hant", "vi", "th", "ru")}
    base["body"] = body_block(ko, en, extras)
    return base


def ensure_images(slugs: list[str]) -> None:
    IMG.mkdir(parents=True, exist_ok=True)
    if not TYPE_FALLBACK.exists():
        print(f"WARN: missing fallback {TYPE_FALLBACK}")
        return
    for slug in slugs:
        dest = IMG / f"{slug}.jpg"
        if dest.exists() and dest.stat().st_size > 5000:
            continue
        shutil.copy2(TYPE_FALLBACK, dest)
        print(f"fallback image {dest.name}")


def main() -> int:
    text = COORDS.read_text(encoding="utf-8")
    have = existing_slugs(text)

    parsed = parse_source(SOURCE)
    to_add: list[dict] = []
    skipped: list[str] = []
    errors: list[str] = []

    for region, name in parsed:
        if name in ALREADY:
            skipped.append(f"{name} (already: {ALREADY[name]})")
            continue
        # Skip clear mountain / beach names if they ever appear in this list
        if name.endswith("산") and name not in PLACES:
            skipped.append(f"{name} (mountain — other agent)")
            continue
        if "해수욕장" in name:
            skipped.append(f"{name} (beach — other agent)")
            continue
        place = PLACES.get(name)
        if not place:
            errors.append(f"{name} (no curated data)")
            continue
        slug = place["slug"]
        if slug in have:
            skipped.append(f"{name} (slug exists: {slug})")
            continue
        place = {**place, "region": region}
        to_add.append(place)
        have.add(slug)

    if to_add:
        lines = []
        for p in to_add:
            img = f"Images/places/{p['slug']}.jpg"
            note = p["en"]["name"].replace('"', "'")
            lines.append(
                "  { "
                f'slug: "{p["slug"]}", lat: {p["lat"]}, lng: {p["lng"]}, '
                f'region: "{p["region"]}", type: "nature", '
                f'note: "{note}", image: "{img}" '
                "},"
            )
        insert = "\n".join(lines) + "\n"
        idx = text.rfind("];")
        if idx < 0:
            raise SystemExit("places-coords.js: cannot find ];")
        COORDS.write_text(text[:idx] + insert + text[idx:], encoding="utf-8", newline="\n")

    sys.path.insert(0, str(ROOT / "tool"))
    from lib import i18n_store  # noqa: WPS433

    if to_add:
        bundle = i18n_store.load_all()
        for lang in i18n_store.LANGS:
            places = bundle[lang].setdefault("places", {})
            for p in to_add:
                places[p["slug"]] = entry_for_lang(lang, p, p["region"])
            print(f"i18n {lang}: +{len(to_add)} outdoor places")
        i18n_store.save_all(bundle)
        ensure_images([p["slug"] for p in to_add])
        print(i18n_store.build_bundle())
    else:
        print("nothing to add; skipping i18n/bundle")

    print("---")
    print(f"added: {len(to_add)}")
    for p in to_add:
        print(f"  + {p['ko']['name']} ({p['slug']})")
    print(f"skipped: {len(skipped)}")
    for s in skipped:
        print(f"  - {s}")
    print(f"errors: {len(errors)}")
    for e in errors:
        print(f"  ! {e}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
