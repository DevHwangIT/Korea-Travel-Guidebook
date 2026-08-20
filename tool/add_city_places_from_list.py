# -*- coding: utf-8 -*-
"""Add city-type sightseeing places from the curated name list."""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
COORDS = ROOT / "data" / "places" / "places-coords.js"
IMG = ROOT / "Images" / "places"
LIST_FILE = Path(r"C:\Users\HwangInTae\Desktop\guide book\명소 추가할 자료\도시 필터 이름정보.txt")

LANGS = ("ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru")

REGION_FROM_HEADER = {
    "서울": "seoul",
    "부산": "busan",
    "인천": "incheon",
    "대구": "",  # map uses empty region for Daegu (same as markets)
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

# Korean list name -> place payload (only entries we may add)
PLACES: dict[str, dict] = {
    "서울달": {
        "slug": "seouldal",
        "lat": 37.5552,
        "lng": 126.9238,
        "region": "seoul",
        "maps_q": "서울달 홍대",
        "ko": {
            "name": "서울달",
            "desc": "홍대 인근 대형 보름달 조형물 포토 스팟. 밤 조명과 인생샷으로 유명합니다.",
            "how": "지하철 2호선·공항철도·경의중앙 홍대입구역에서 도보 5~10분.",
            "address": "서울 마포구 홍대 일대 서울달",
        },
        "en": {
            "name": "Seouldal (Seoul Moon)",
            "desc": "Giant moon photo spot near Hongdae — popular for night lights and selfies.",
            "how": "Lines 2 / AREX / Gyeongui–Jungang Hongik Univ. Station; 5–10 min walk.",
            "address": "Hongdae area, Mapo-gu, Seoul",
        },
    },
    "성수동": {
        "slug": "seongsu-dong",
        "lat": 37.5445,
        "lng": 127.0557,
        "region": "seoul",
        "maps_q": "성수동",
        "ko": {
            "name": "성수동",
            "desc": "카페·팝업·편집숍이 밀집한 트렌디 동네. 공장 개조 공간과 한강 뷰 카페가 많습니다.",
            "how": "지하철 2호선 성수역·뚝섬역. 카페거리는 성수역 2번 출구 방면.",
            "address": "서울 성동구 성수동",
        },
        "en": {
            "name": "Seongsu-dong",
            "desc": "Trendy café and pop-up district in renovated warehouse spaces.",
            "how": "Line 2 Seongsu or Ttukseom Station; café streets near Seongsu exit 2.",
            "address": "Seongsu-dong, Seongdong-gu, Seoul",
        },
    },
    "코엑스": {
        "slug": "coex",
        "lat": 37.5116,
        "lng": 127.0595,
        "region": "seoul",
        "maps_q": "코엑스 서울",
        "ko": {
            "name": "코엑스",
            "desc": "삼성동 대형 컨벤션·쇼핑몰 단지. 별마당도서관·아쿠아리움·전시가 한곳에 있습니다.",
            "how": "지하철 2호선 삼성역 또는 9호선 봉은사역. 지하로 코엑스몰과 연결됩니다.",
            "address": "서울 강남구 영동대로 513 코엑스",
        },
        "en": {
            "name": "COEX",
            "desc": "Huge convention and mall complex — Starfield Library, aquarium, and exhibitions.",
            "how": "Line 2 Samseong or Line 9 Bongeunsa; underground links to COEX Mall.",
            "address": "513 Yeongdong-daero, Gangnam-gu, Seoul",
        },
    },
    "별마당도서관": {
        "slug": "byeolmadang-library",
        "lat": 37.5112,
        "lng": 127.0594,
        "region": "seoul",
        "maps_q": "별마당도서관",
        "ko": {
            "name": "별마당도서관",
            "desc": "코엑스몰 안의 초대형 개방형 도서관. 높은 책장과 포토존으로 SNS에서 유명합니다.",
            "how": "코엑스몰 지하 중앙. 삼성역·봉은사역에서 몰 안내를 따라가세요.",
            "address": "서울 강남구 영동대로 513 코엑스몰 별마당도서관",
        },
        "en": {
            "name": "Starfield Library (Byeolmadang)",
            "desc": "Open atrium library inside COEX Mall — iconic tall shelves and photo spot.",
            "how": "Central atrium of COEX Mall via Samseong or Bongeunsa Station.",
            "address": "Starfield Library, COEX Mall, Gangnam-gu, Seoul",
        },
    },
    "압구정": {
        "slug": "apgujeong",
        "lat": 37.5272,
        "lng": 127.0286,
        "region": "seoul",
        "maps_q": "압구정로데오",
        "ko": {
            "name": "압구정",
            "desc": "로데오거리·편집숍·카페가 모인 강남 북쪽 쇼핑·패션 거리입니다.",
            "how": "지하철 3호선 압구정역 또는 수인분당 압구정로데오역.",
            "address": "서울 강남구 압구정동",
        },
        "en": {
            "name": "Apgujeong",
            "desc": "Fashion and café district around Apgujeong Rodeo Street.",
            "how": "Line 3 Apgujeong or Suin–Bundang Apgujeong Rodeo Station.",
            "address": "Apgujeong-dong, Gangnam-gu, Seoul",
        },
    },
    "청담": {
        "slug": "cheongdam",
        "lat": 37.5245,
        "lng": 127.0470,
        "region": "seoul",
        "maps_q": "청담동",
        "ko": {
            "name": "청담",
            "desc": "명품 거리·갤러리·고급 카페가 있는 강남 청담동 일대입니다.",
            "how": "지하철 7호선 청담역 또는 수인분당 압구정로데오역에서 도보·택시.",
            "address": "서울 강남구 청담동",
        },
        "en": {
            "name": "Cheongdam",
            "desc": "Upscale shopping, galleries, and cafés in Cheongdam-dong.",
            "how": "Line 7 Cheongdam or walk/taxi from Apgujeong Rodeo Station.",
            "address": "Cheongdam-dong, Gangnam-gu, Seoul",
        },
    },
    "롯데월드": {
        "slug": "lotte-world",
        "lat": 37.5110,
        "lng": 127.0980,
        "region": "seoul",
        "maps_q": "롯데월드 어드벤처",
        "ko": {
            "name": "롯데월드",
            "desc": "잠실의 실내·야외 테마파크. 매직아일랜드와 어드벤처로 나뉩니다.",
            "how": "지하철 2·8호선 잠실역에서 롯데월드 방면 지하 연결.",
            "address": "서울 송파구 올림픽로 240 롯데월드",
        },
        "en": {
            "name": "Lotte World",
            "desc": "Indoor/outdoor theme park in Jamsil — Adventure plus Magic Island.",
            "how": "Lines 2/8 Jamsil Station; underground link to the park.",
            "address": "240 Olympic-ro, Songpa-gu, Seoul",
        },
    },
    "남산 케이블카": {
        "slug": "namsan-cable-car",
        "lat": 37.5536,
        "lng": 126.9867,
        "region": "seoul",
        "maps_q": "남산 케이블카",
        "ko": {
            "name": "남산 케이블카",
            "desc": "명동·회현에서 남산서울타워로 올라가는 케이블카. 야경 코스로 인기입니다.",
            "how": "지하철 4호선 명동역 또는 회현역에서 케이블카 승강장 안내를 따라가세요.",
            "address": "서울 중구 남산 케이블카",
        },
        "en": {
            "name": "Namsan Cable Car",
            "desc": "Cable car from Myeongdong/Hoehyeon up toward N Seoul Tower — great at night.",
            "how": "From Line 4 Myeongdong or Hoehyeon Station, follow cable-car signs.",
            "address": "Namsan Cable Car, Jung-gu, Seoul",
        },
    },
    "부산 엑스 더 스카이": {
        "slug": "busan-x-the-sky",
        "lat": 35.1598,
        "lng": 129.1705,
        "region": "busan",
        "maps_q": "부산 엑스 더 스카이",
        "ko": {
            "name": "부산 엑스 더 스카이",
            "desc": "해운대 초고층 전망대. 동해·마린시티 야경을 한눈에 볼 수 있습니다.",
            "how": "해운대역·센텀시티에서 버스·택시. 해운대 해변 인근 초고층 타워.",
            "address": "부산 해운대구 달맞이길 30 부산엑스더스카이",
        },
        "en": {
            "name": "Busan X the SKY",
            "desc": "Haeundae skyscraper observatory with East Sea and Marine City views.",
            "how": "Bus/taxi from Haeundae or Centum City toward the beachfront tower.",
            "address": "30 Dalmaji-gil, Haeundae-gu, Busan",
        },
    },
    "해운대 블루라인파크": {
        "slug": "haeundae-blueline-park",
        "lat": 35.1583,
        "lng": 129.1715,
        "region": "busan",
        "maps_q": "해운대 블루라인파크",
        "ko": {
            "name": "해운대 블루라인파크",
            "desc": "해변 절벽을 따라 달리는 미니열차·스카이캡슐. 해운대~청사포 코스가 유명합니다.",
            "how": "해운대 해변 또는 미포·청사포 정류장. 예약·대기 시간을 확인하세요.",
            "address": "부산 해운대구 달맞이길 블루라인파크",
        },
        "en": {
            "name": "Haeundae Blueline Park",
            "desc": "Coastal mini-train and Sky Capsule between Haeundae and Cheongsapo.",
            "how": "Stations at Haeundae beach / Mipo / Cheongsapo — check wait times.",
            "address": "Dalmaji-gil, Haeundae-gu, Busan",
        },
    },
    "롯데월드 어드벤처 부산": {
        "slug": "lotte-world-adventure-busan",
        "lat": 35.1940,
        "lng": 129.2135,
        "region": "busan",
        "maps_q": "롯데월드 어드벤처 부산",
        "ko": {
            "name": "롯데월드 어드벤처 부산",
            "desc": "기장 오시리아의 대형 테마파크. 어드벤처와 쇼핑몰이 함께 있습니다.",
            "how": "동해선 오시리아역에서 도보·셔틀. 부산 시내에서 동해선이 편합니다.",
            "address": "부산 기장군 기장읍 동부산관광로 42",
        },
        "en": {
            "name": "Lotte World Adventure Busan",
            "desc": "Major theme park at Osiria in Gijang — rides plus shopping mall.",
            "how": "Donghae Line Osiria Station; walk or shuttle. Easy from Busan by rail.",
            "address": "42 Dongbusan Tourism-ro, Gijang-eup, Busan",
        },
    },
    "신세계 센텀시티": {
        "slug": "shinsegae-centum-city",
        "lat": 35.1687,
        "lng": 129.1308,
        "region": "busan",
        "maps_q": "신세계 센텀시티",
        "ko": {
            "name": "신세계 센텀시티",
            "desc": "세계 최대급 백화점으로 알려진 센텀시티 신세계. 쇼핑·푸드코트·스파가 있습니다.",
            "how": "부산 2호선·동해선 센텀시티역과 연결.",
            "address": "부산 해운대구 센텀남대로 35 신세계센텀시티",
        },
        "en": {
            "name": "Shinsegae Centum City",
            "desc": "One of the world’s largest department stores — shopping, dining, and spa.",
            "how": "Linked to Centum City Station (Busan Line 2 / Donghae Line).",
            "address": "35 Centumnam-daero, Haeundae-gu, Busan",
        },
    },
    "더베이101": {
        "slug": "the-bay-101",
        "lat": 35.1565,
        "lng": 129.1485,
        "region": "busan",
        "maps_q": "더베이101",
        "ko": {
            "name": "더베이101",
            "desc": "마린시티의 해안 산책·카페·야경 명소. 요트와 고층 아파트 배경 포토 스팟입니다.",
            "how": "해운대·센텀에서 버스·택시. 마린시티 해안도로 인근.",
            "address": "부산 해운대구 마린시티1로 더베이101",
        },
        "en": {
            "name": "The Bay 101",
            "desc": "Waterfront promenade and cafés in Marine City — yacht views at night.",
            "how": "Bus/taxi from Haeundae or Centum toward Marine City waterfront.",
            "address": "Marine City 1-ro, Haeundae-gu, Busan",
        },
    },
    "영화의전당": {
        "slug": "busan-cinema-center",
        "lat": 35.1715,
        "lng": 129.1270,
        "region": "busan",
        "maps_q": "영화의전당",
        "ko": {
            "name": "영화의전당",
            "desc": "부산국제영화제(BIFF)의 중심 공연장. 대형 지붕과 야외 광장이 인상적입니다.",
            "how": "부산 2호선 센텀시티역에서 도보 10분, 또는 버스·택시.",
            "address": "부산 해운대구 영화의전당로 12",
        },
        "en": {
            "name": "Busan Cinema Center",
            "desc": "BIFF’s landmark venue — huge canopy roof and outdoor plaza.",
            "how": "~10 min walk from Centum City Station (Line 2), or bus/taxi.",
            "address": "12 Yeonghwa-jeondang-ro, Haeundae-gu, Busan",
        },
    },
    "월미도": {
        "slug": "wolmido",
        "lat": 37.4715,
        "lng": 126.5965,
        "region": "incheon",
        "maps_q": "월미도",
        "ko": {
            "name": "월미도",
            "desc": "인천항 앞 섬·유원지. 놀이공원·해안 산책·차이나타운과 함께 가기 좋습니다.",
            "how": "1호선·수인선 인천역에서 버스·택시, 또는 월미바다열차.",
            "address": "인천 중구 월미로 월미도",
        },
        "en": {
            "name": "Wolmido",
            "desc": "Island amusement area by Incheon Port — rides, waterfront, near Chinatown.",
            "how": "Bus/taxi from Incheon Station (Line 1 / Suin), or Wolmi Sea Train.",
            "address": "Wolmi-ro, Jung-gu, Incheon",
        },
    },
    "인스파이어 리조트": {
        "slug": "inspire-resort",
        "lat": 37.4435,
        "lng": 126.4595,
        "region": "incheon",
        "maps_q": "인스파이어 엔터테인먼트 리조트",
        "ko": {
            "name": "인스파이어 리조트",
            "desc": "영종도 대형 엔터테인먼트 리조트. 공연·카지노·쇼핑·호텔이 한 단지에 있습니다.",
            "how": "인천공항·영종에서 리조트 셔틀·택시. 공항철도 후 환승.",
            "address": "인천 중구 용유서로 인스파이어 리조트",
        },
        "en": {
            "name": "Inspire Resort",
            "desc": "Large entertainment resort on Yeongjong — shows, shopping, hotels.",
            "how": "Resort shuttle/taxi from ICN / Yeongjong; transfer after AREX.",
            "address": "Yongyuseo-ro, Jung-gu, Incheon",
        },
    },
    "파라다이스시티": {
        "slug": "paradise-city",
        "lat": 37.4370,
        "lng": 126.4555,
        "region": "incheon",
        "maps_q": "파라다이스시티 인천",
        "ko": {
            "name": "파라다이스시티",
            "desc": "영종도 복합 리조트. 호텔·카지노·스파·공연·미술 전시가 있습니다.",
            "how": "인천공항에서 리조트 셔틀·택시. 영종도 일대.",
            "address": "인천 중구 영종해안남로 파라다이스시티",
        },
        "en": {
            "name": "Paradise City",
            "desc": "Integrated resort on Yeongjong — hotels, spa, shows, and art spaces.",
            "how": "Shuttle/taxi from Incheon Airport on Yeongjong Island.",
            "address": "Yeongjonghaean-nam-ro, Jung-gu, Incheon",
        },
    },
    "인천 차이나타운": {
        "slug": "incheon-chinatown",
        "lat": 37.4755,
        "lng": 126.6180,
        "region": "incheon",
        "maps_q": "인천 차이나타운",
        "ko": {
            "name": "인천 차이나타운",
            "desc": "한국 대표 차이나타운. 짜장면 거리·공갈빵·자유공원과 가깝습니다.",
            "how": "1호선·수인선 인천역 1번 출구에서 도보 5분.",
            "address": "인천 중구 차이나타운로",
        },
        "en": {
            "name": "Incheon Chinatown",
            "desc": "Korea’s classic Chinatown — jajangmyeon street near Freedom Park.",
            "how": "Incheon Station (Line 1 / Suin) exit 1; ~5 min walk.",
            "address": "Chinatown-ro, Jung-gu, Incheon",
        },
    },
    "현대프리미엄아울렛 송도": {
        "slug": "hyundai-premium-outlet-songdo",
        "lat": 37.3815,
        "lng": 126.6595,
        "region": "incheon",
        "maps_q": "현대프리미엄아울렛 송도",
        "ko": {
            "name": "현대프리미엄아울렛 송도",
            "desc": "송도의 대형 프리미엄 아울렛. 브랜드 쇼핑과 식사가 한곳에 있습니다.",
            "how": "인천 1호선 센트럴파크·국제업무지구역에서 버스·택시.",
            "address": "인천 연수구 송도동 현대프리미엄아울렛 송도",
        },
        "en": {
            "name": "Hyundai Premium Outlet Songdo",
            "desc": "Large premium outlet mall in Songdo for brand shopping and dining.",
            "how": "Bus/taxi from Incheon Line 1 Central Park or Int’l Business District.",
            "address": "Songdo-dong, Yeonsu-gu, Incheon",
        },
    },
    "동성로": {
        "slug": "dongseong-ro",
        "lat": 35.8695,
        "lng": 128.5955,
        "region": "",
        "maps_q": "대구 동성로",
        "ko": {
            "name": "동성로",
            "desc": "대구 대표 번화가. 쇼핑·카페·길거리 음식이 밀집한 보행자 거리입니다.",
            "how": "대구 1호선 중앙로역에서 도보. 반월당역과도 가깝습니다.",
            "address": "대구 중구 동성로",
        },
        "en": {
            "name": "Dongseong-ro",
            "desc": "Daegu’s main shopping street — cafés, fashion, and street snacks.",
            "how": "Walk from Daegu Line 1 Jungangno; also near Banwoldang.",
            "address": "Dongseong-ro, Jung-gu, Daegu",
        },
    },
    "83타워": {
        "slug": "83-tower",
        "lat": 35.8535,
        "lng": 128.5645,
        "region": "",
        "maps_q": "대구 83타워",
        "ko": {
            "name": "83타워",
            "desc": "두류공원 옆 전망 타워. 이월드와 함께 대구 야경 코스로 유명합니다.",
            "how": "대구 2호선 두류역에서 도보·버스. 이월드 단지 안.",
            "address": "대구 달서구 두류공원로 83타워",
        },
        "en": {
            "name": "83 Tower",
            "desc": "Observation tower by Duryu Park — pair with E-World for night views.",
            "how": "Walk/bus from Daegu Line 2 Duryu Station; inside the E-World area.",
            "address": "Duryugongwon-ro, Dalseo-gu, Daegu",
        },
    },
    "이월드": {
        "slug": "eworld",
        "lat": 35.8538,
        "lng": 128.5660,
        "region": "",
        "maps_q": "대구 이월드",
        "ko": {
            "name": "이월드",
            "desc": "두류공원의 테마파크. 83타워·야간 조명쇼와 함께 즐기기 좋습니다.",
            "how": "대구 2호선 두류역에서 도보 10분, 또는 시내버스.",
            "address": "대구 달서구 두류공원로 200 이월드",
        },
        "en": {
            "name": "E-World",
            "desc": "Theme park in Duryu Park — rides and night lights with 83 Tower.",
            "how": "~10 min walk from Daegu Line 2 Duryu Station, or city bus.",
            "address": "200 Duryugongwon-ro, Dalseo-gu, Daegu",
        },
    },
    "대구 신세계백화점": {
        "slug": "daegu-shinsegae",
        "lat": 35.8775,
        "lng": 128.6285,
        "region": "",
        "maps_q": "대구 신세계백화점",
        "ko": {
            "name": "대구 신세계백화점",
            "desc": "동대구역과 연결된 대형 백화점. KTX 환승·쇼핑을 한곳에서 할 수 있습니다.",
            "how": "동대구역(KTX·지하철)과 직결. 복합환승센터·신세계 안내를 따르세요.",
            "address": "대구 동구 동부로 149 신세계백화점 대구점",
        },
        "en": {
            "name": "Shinsegae Department Store Daegu",
            "desc": "Major department store linked to Dongdaegu Station (KTX + metro).",
            "how": "Direct connection from Dongdaegu Station / transfer center.",
            "address": "149 Dongbu-ro, Dong-gu, Daegu",
        },
    },
    "아쿠아플라넷 여수": {
        "slug": "aquaplanet-yeosu",
        "lat": 34.7455,
        "lng": 127.7495,
        "region": "jeolla",
        "maps_q": "아쿠아플라넷 여수",
        "ko": {
            "name": "아쿠아플라넷 여수",
            "desc": "여수 해양 아쿠아리움. 대형 수조와 해양 생물을 관람할 수 있습니다.",
            "how": "여수엑스포역·시내에서 버스·택시. 오동도·엑스포 단지 인근.",
            "address": "전남 여수시 오동도로 아쿠아플라넷 여수",
        },
        "en": {
            "name": "Aqua Planet Yeosu",
            "desc": "Large aquarium in Yeosu — big tanks and marine life exhibits.",
            "how": "Bus/taxi from Yeosu Expo Station / downtown near Odongdo.",
            "address": "Odongdo-ro, Yeosu, Jeollanam-do",
        },
    },
    "여수 낭만포차거리": {
        "slug": "yeosu-nangman-pocha",
        "lat": 34.7395,
        "lng": 127.7525,
        "region": "jeolla",
        "maps_q": "여수 낭만포차거리",
        "ko": {
            "name": "여수 낭만포차거리",
            "desc": "밤바다와 함께 즐기는 여수 포장마차 거리. 해산물·맥주·야경이 포인트입니다.",
            "how": "여수 시내·엑스포 인근에서 택시·도보. 저녁 시간대가 가장 붐빕니다.",
            "address": "전남 여수시 중앙동 낭만포차거리",
        },
        "en": {
            "name": "Yeosu Nangman Pocha Street",
            "desc": "Night seafood tent street by the water — beer, views, and local snacks.",
            "how": "Taxi/walk from downtown Yeosu / Expo area; busiest after dark.",
            "address": "Jungang-dong, Yeosu, Jeollanam-do",
        },
    },
    "아르떼뮤지엄 제주": {
        "slug": "arte-museum-jeju",
        "lat": 33.3995,
        "lng": 126.3455,
        "region": "jeju",
        "maps_q": "아르떼뮤지엄 제주",
        "ko": {
            "name": "아르떼뮤지엄 제주",
            "desc": "몰입형 미디어아트 전시관. 조명·영상 공간으로 사진 명소입니다.",
            "how": "애월·한림 방면 렌터카·버스·택시. 예약·운영시간을 확인하세요.",
            "address": "제주 제주시 애월읍 아르떼뮤지엄 제주",
        },
        "en": {
            "name": "ARTE Museum Jeju",
            "desc": "Immersive media-art museum — popular light-and-video photo spaces.",
            "how": "Car/bus/taxi toward Aewol–Hallim; check hours and tickets.",
            "address": "Aewol-eup, Jeju City, Jeju",
        },
    },
    "9.81파크": {
        "slug": "981-park",
        "lat": 33.3895,
        "lng": 126.3665,
        "region": "jeju",
        "maps_q": "9.81파크 제주",
        "ko": {
            "name": "9.81파크",
            "desc": "중력·레이싱을 테마로 한 체험형 파크. 그래비티 레이서가 대표 어트랙션입니다.",
            "how": "애월 방면 렌터카·택시. 아르떼뮤지엄과 가까운 코스로 묶기 좋습니다.",
            "address": "제주 제주시 애월읍 9.81파크",
        },
        "en": {
            "name": "9.81 Park",
            "desc": "Gravity-themed experience park — Gravity Racer is the signature ride.",
            "how": "Car/taxi in Aewol; easy to pair with ARTE Museum Jeju.",
            "address": "Aewol-eup, Jeju City, Jeju",
        },
    },
    "노형슈퍼마켓": {
        "slug": "nohyeong-supermarket",
        "lat": 33.4845,
        "lng": 126.4785,
        "region": "jeju",
        "maps_q": "노형수퍼마켙",
        "ko": {
            "name": "노형슈퍼마켓",
            "desc": "제주 노형의 대형 감성 카페·복합공간(노형수퍼마켙). 포토존과 디저트로 유명합니다.",
            "how": "제주시내·공항에서 버스·택시. 노형오거리 인근.",
            "address": "제주 제주시 노형동 노형수퍼마켙",
        },
        "en": {
            "name": "Nohyeong Supermarket (café)",
            "desc": "Huge stylish café complex in Nohyeong — photo spots and desserts.",
            "how": "Bus/taxi from Jeju City or airport near Nohyeong Ogeori.",
            "address": "Nohyeong-dong, Jeju City, Jeju",
        },
    },
}

# Exact / alias Korean names already present (city or other types we must not re-add)
SKIP_ALIASES = {
    "강남": "gangnam",
    "명동": "myeongdong",
    "롯데월드타워": "lotte-tower",
    "N서울타워": "namsan",
    "홍대": "hongdae",
    "송도 센트럴파크": "songdo",
    "감천문화마을": "gamcheon",
    "서문시장": "seomun-market",
}


def norm_name(s: str) -> str:
    return re.sub(r"\s+", "", s).strip().lower()


def parse_list(path: Path) -> list[tuple[str, str]]:
    """Return [(region_key, korean_name), ...] preserving order, deduped by name."""
    region = "seoul"
    seen: set[str] = set()
    out: list[tuple[str, str]] = []
    text = path.read_text(encoding="utf-8")
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        hangul_only = re.sub(r"[^가-힣]", "", line)
        if hangul_only in REGION_FROM_HEADER and hangul_only == line.replace(" ", "")[-len(hangul_only) :]:
            # Header lines are short and end with the city name (emoji + city)
            if len(line) <= 12:
                region = REGION_FROM_HEADER[hangul_only]
                continue
        name = re.sub(r"^[^\w가-힣]+", "", line).strip()
        if not name or name in REGION_FROM_HEADER:
            continue
        if not re.search(r"[가-힣A-Za-z0-9]", name):
            continue
        key = norm_name(name)
        if key in seen:
            continue
        seen.add(key)
        out.append((region, name))
    return out


def load_existing_slugs() -> set[str]:
    coords_text = COORDS.read_text(encoding="utf-8")
    return set(re.findall(r'slug:\s*"([^"]+)"', coords_text))


def maps_urls(q: str, hl: str) -> tuple[str, str]:
    enc = quote(q)
    return (
        f"https://www.google.com/maps/search/?api=1&query={enc}",
        f"https://maps.google.com/maps?q={enc}&hl={hl}&z=15&output=embed",
    )


def body_block(ko: dict, en: dict) -> list:
    return [
        {
            "type": "text",
            "ko": f"{ko['desc']}\n\n가는 방법: {ko['how']}",
            "en": f"{en['desc']}\n\nHow to get there: {en['how']}",
            "ja": f"{en['desc']}\n\n{en['how']}",
            "zh": f"{en['desc']}\n\n{en['how']}",
            "zh-Hant": f"{en['desc']}\n\n{en['how']}",
            "vi": f"{en['desc']}\n\n{en['how']}",
            "th": f"{en['desc']}\n\n{en['how']}",
            "ru": f"{en['desc']}\n\n{en['how']}",
        }
    ]


def entry_for_lang(lang: str, place: dict) -> dict:
    ko, en = place["ko"], place["en"]
    slug = place["slug"]
    region = place["region"]
    rl = REGION_LABELS.get(region, REGION_LABELS[""])
    hl = {"zh-Hant": "zh-TW", "zh": "zh-CN"}.get(lang, lang if lang != "ko" else "ko")
    maps, embed = maps_urls(place["maps_q"], "en" if lang == "en" else hl)
    img = f"Images/places/{slug}.jpg"
    if lang == "ko":
        name, desc, how, address, region_label = (
            ko["name"],
            ko["desc"],
            ko["how"],
            ko["address"],
            rl["ko"],
        )
    elif lang == "en":
        name, desc, how, address, region_label = (
            en["name"],
            en["desc"],
            en["how"],
            en["address"],
            rl["en"],
        )
    else:
        name, desc, how = en["name"], en["desc"], en["how"]
        address = en["address"] if lang in ("vi", "th", "ru") else ko["address"]
        region_label = rl.get(lang) or rl["en"]
    return {
        "name": name,
        "desc": desc,
        "how": how,
        "address": address,
        "regionLabel": region_label,
        "region": region,
        "mapsUrl": maps,
        "mapsEmbedUrl": embed,
        "image": img,
        "body": body_block(ko, en),
    }


def should_skip(name: str, slugs: set[str], name_to_slug: dict[str, str]) -> str | None:
    if name in SKIP_ALIASES:
        return f"alias->{SKIP_ALIASES[name]}"
    n = norm_name(name)
    if n in name_to_slug:
        return f"i18n-name->{name_to_slug[n]}"
    # market-only: *시장 already present as market slug
    if "시장" in name:
        for slug in slugs:
            if "market" in slug and (n in slug or slug.replace("-", "") in n):
                return f"market-slug->{slug}"
        if n in {norm_name(k) for k in SKIP_ALIASES}:
            return "market-alias"
    return None


def select_places() -> tuple[list[dict], list[str], list[str]]:
    parsed = parse_list(LIST_FILE)
    slugs = load_existing_slugs()
    sys.path.insert(0, str(ROOT / "tool"))
    from lib import i18n_store  # noqa: WPS433

    ko = i18n_store.load_lang("ko")
    name_to_slug: dict[str, str] = {}
    for slug, entry in (ko.get("places") or {}).items():
        n = (entry or {}).get("name") or ""
        if n:
            name_to_slug[norm_name(n)] = slug
    # Also treat namsan as covering N서울타워 via alias table

    to_add: list[dict] = []
    skipped: list[str] = []
    missing: list[str] = []
    for region, name in parsed:
        reason = should_skip(name, slugs, name_to_slug)
        if reason:
            skipped.append(f"{name} ({reason})")
            continue
        place = PLACES.get(name)
        if not place:
            missing.append(name)
            continue
        if place["slug"] in slugs:
            skipped.append(f"{name} (slug->{place['slug']})")
            continue
        p = dict(place)
        p["region"] = region
        if name in ("동성로", "83타워", "이월드", "대구 신세계백화점"):
            p["region"] = ""
        to_add.append(p)
        slugs.add(p["slug"])
    return to_add, skipped, missing


def patch_coords(places: list[dict]) -> int:
    if not places:
        return 0
    text = COORDS.read_text(encoding="utf-8")
    lines = []
    for p in places:
        if f'slug: "{p["slug"]}"' in text:
            continue
        img = f"Images/places/{p['slug']}.jpg"
        note = p["en"]["name"].replace('"', "'")
        lines.append(
            "  { "
            f'slug: "{p["slug"]}", lat: {p["lat"]}, lng: {p["lng"]}, '
            f'region: "{p["region"]}", type: "city", '
            f'note: "{note}", image: "{img}" '
            "},"
        )
    if not lines:
        return 0
    insert = "\n".join(lines) + "\n"
    idx = text.rfind("];")
    if idx < 0:
        raise SystemExit("places-coords.js: cannot find ];")
    COORDS.write_text(text[:idx] + insert + text[idx:], encoding="utf-8", newline="\n")
    return len(lines)


def patch_i18n(places: list[dict]) -> None:
    sys.path.insert(0, str(ROOT / "tool"))
    from lib import i18n_store  # noqa: WPS433

    bundle = i18n_store.load_all()
    for lang in i18n_store.LANGS:
        places_map = bundle[lang].setdefault("places", {})
        for p in places:
            places_map[p["slug"]] = entry_for_lang(lang, p)
        print(f"i18n {lang}: +{len(places)} city places")
    i18n_store.save_all(bundle)


def copy_images(places: list[dict]) -> None:
    IMG.mkdir(parents=True, exist_ok=True)
    fallback = IMG / "_types" / "city.jpg"
    for p in places:
        dest = IMG / f"{p['slug']}.jpg"
        if dest.exists() and dest.stat().st_size > 2000:
            continue
        if fallback.exists():
            shutil.copy2(fallback, dest)
            print(f"fallback image {dest.name}")
        else:
            print(f"no fallback for {p['slug']}")


def main() -> int:
    if not LIST_FILE.exists():
        raise SystemExit(f"list file missing: {LIST_FILE}")
    to_add, skipped, missing = select_places()
    print(f"to_add={len(to_add)} skipped={len(skipped)} missing_data={len(missing)}")
    for s in skipped:
        print(f"  skip: {s}")
    for m in missing:
        print(f"  FAIL no PLACES data: {m}")
    n = patch_coords(to_add)
    print(f"coords added: {n}")
    if to_add:
        patch_i18n(to_add)
        copy_images(to_add)
        sys.path.insert(0, str(ROOT / "tool"))
        from lib import i18n_store  # noqa: WPS433

        print(i18n_store.build_bundle())
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
