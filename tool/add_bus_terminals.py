# -*- coding: utf-8 -*-
"""Add major bus-terminal places to places-coords + all i18n locales; download photos if possible."""
from __future__ import annotations

import json
import ssl
import sys
import urllib.request
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
COORDS = ROOT / "data" / "places" / "places-coords.js"
I18N = ROOT / "i18n"
IMG = ROOT / "Images" / "places"

TERMINALS = [
    {
        "slug": "bus-terminal-seoul-express",
        "lat": 37.5046,
        "lng": 127.0045,
        "region": "seoul",
        "note": "Seoul Express Bus Terminal / Central City",
        "ko": {
            "name": "서울고속버스터미널",
            "desc": "강남 센트럴시티·고속터미널. 전국 고속버스의 대표 출발·도착지입니다.",
            "how": "지하철 3·7·9호선 고속터미널역. 센트럴시티·경부·영동선 건물 확인.",
            "address": "서울 서초구 신반포로 194",
            "regionLabel": "서울",
        },
        "en": {
            "name": "Seoul Express Bus Terminal",
            "desc": "Gangnam hub (Central City) for nationwide express coaches.",
            "how": "Subway Lines 3/7/9 Express Bus Terminal Station. Check Gyeongbu/Yeongdong/Central City halls.",
            "address": "194 Sinbanpo-ro, Seocho-gu, Seoul",
            "regionLabel": "Seoul",
        },
        "maps_q": "서울고속버스터미널",
        "wiki": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Seoul_Express_Bus_Terminal_20140726.jpg/1280px-Seoul_Express_Bus_Terminal_20140726.jpg",
    },
    {
        "slug": "bus-terminal-east-seoul",
        "lat": 37.5347,
        "lng": 127.0942,
        "region": "seoul",
        "note": "East Seoul Bus Terminal",
        "ko": {
            "name": "동서울종합터미널",
            "desc": "건대·잠실 쪽 동부 서울의 고속·시외버스 거점입니다.",
            "how": "지하철 2호선 강변역과 연결. 터미널 건물 안내판을 확인하세요.",
            "address": "서울 광진구 강변역로 50",
            "regionLabel": "서울",
        },
        "en": {
            "name": "East Seoul Bus Terminal",
            "desc": "Express/intercity buses on Seoul’s east side near Gangbyeon.",
            "how": "Connected to Line 2 Gangbyeon Station. Follow terminal signs.",
            "address": "50 Gangbyeonnyeok-ro, Gwangjin-gu, Seoul",
            "regionLabel": "Seoul",
        },
        "maps_q": "동서울종합터미널",
        "wiki": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Dongseoul_Bus_Terminal.jpg/1280px-Dongseoul_Bus_Terminal.jpg",
    },
    {
        "slug": "bus-terminal-nambu",
        "lat": 37.485,
        "lng": 127.0162,
        "region": "seoul",
        "note": "Seoul Nambu Bus Terminal",
        "ko": {
            "name": "서울남부터미널",
            "desc": "서초 남부 시외·고속버스 터미널. 경기·충청·전라 방면이 많습니다.",
            "how": "지하철 3호선 남부터미널역 바로 앞.",
            "address": "서울 서초구 효령로 208",
            "regionLabel": "서울",
        },
        "en": {
            "name": "Seoul Nambu Bus Terminal",
            "desc": "Southern Seoul intercity/express terminal toward Gyeonggi, Chungcheong, Jeolla.",
            "how": "Exit Line 3 Nambu Bus Terminal Station.",
            "address": "208 Hyoryeong-ro, Seocho-gu, Seoul",
            "regionLabel": "Seoul",
        },
        "maps_q": "서울남부터미널",
        "wiki": None,
    },
    {
        "slug": "bus-terminal-busan",
        "lat": 35.2234,
        "lng": 129.0786,
        "region": "busan",
        "note": "Busan Central Bus Terminal (Nopo)",
        "ko": {
            "name": "부산종합버스터미널",
            "desc": "노포 종합터미널. 부산의 고속·시외버스 중심 거점입니다.",
            "how": "부산 1호선 노포역·터미널 연결. 시내에서 지하철이 편합니다.",
            "address": "부산 금정구 중앙대로 2238",
            "regionLabel": "부산",
        },
        "en": {
            "name": "Busan Central Bus Terminal",
            "desc": "Nopo hub for Busan’s express and intercity coaches.",
            "how": "Busan Metro Line 1 Nopo Station links to the terminal.",
            "address": "2238 Jungang-daero, Geumjeong-gu, Busan",
            "regionLabel": "Busan",
        },
        "maps_q": "부산종합버스터미널",
        "wiki": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Busan_Central_Bus_Terminal.jpg/1280px-Busan_Central_Bus_Terminal.jpg",
    },
    {
        "slug": "bus-terminal-daegu",
        "lat": 35.8795,
        "lng": 128.6284,
        "region": "",
        "note": "Dongdaegu Complex Transfer Center",
        "ko": {
            "name": "동대구복합환승센터",
            "desc": "동대구역과 연결된 대구 고속·시외버스 환승 거점입니다.",
            "how": "KTX·대구지하철 동대구역. 환승센터 내 버스층 안내를 확인하세요.",
            "address": "대구 동구 동대구로 550",
            "regionLabel": "대구",
        },
        "en": {
            "name": "Dongdaegu Transfer Center",
            "desc": "Bus hub linked to Dongdaegu Station (KTX + Daegu Metro).",
            "how": "Dongdaegu Station — follow signs to the bus transfer floors.",
            "address": "550 Dongdaegu-ro, Dong-gu, Daegu",
            "regionLabel": "Daegu",
        },
        "maps_q": "동대구복합환승센터",
        "wiki": None,
    },
    {
        "slug": "bus-terminal-daejeon",
        "lat": 36.3515,
        "lng": 127.4375,
        "region": "",
        "note": "Daejeon Complex Terminal",
        "ko": {
            "name": "대전복합터미널",
            "desc": "대전 고속·시외가 모인 복합터미널. 중부권 환승 거점입니다.",
            "how": "대전 1호선 복합터미널역. 고속·시외 구역을 안내판으로 확인.",
            "address": "대전 동구 동서대로 1689",
            "regionLabel": "대전",
        },
        "en": {
            "name": "Daejeon Complex Terminal",
            "desc": "Combined express/intercity terminal for the central Korea hub.",
            "how": "Daejeon Metro Line 1 Complex Terminal Station.",
            "address": "1689 Dongseo-daero, Dong-gu, Daejeon",
            "regionLabel": "Daejeon",
        },
        "maps_q": "대전복합터미널",
        "wiki": None,
    },
    {
        "slug": "bus-terminal-gwangju",
        "lat": 35.1603,
        "lng": 126.882,
        "region": "jeolla",
        "note": "Gwangju Bus Terminal (U-Square)",
        "ko": {
            "name": "광주종합버스터미널 (유스퀘어)",
            "desc": "유스퀘어 복합시설의 고속·시외버스 터미널입니다.",
            "how": "광주 1호선 금남로5가·시청 방면 버스·택시, 또는 시내버스 직행.",
            "address": "광주 서구 무진대로 282",
            "regionLabel": "광주",
        },
        "en": {
            "name": "Gwangju Bus Terminal (U-Square)",
            "desc": "Express/intercity buses inside the U-Square complex.",
            "how": "City bus/taxi from Gwangju Metro Line 1 (Geumnamno 5-ga / City Hall area).",
            "address": "282 Mujin-daero, Seo-gu, Gwangju",
            "regionLabel": "Gwangju",
        },
        "maps_q": "광주종합버스터미널 유스퀘어",
        "wiki": None,
    },
    {
        "slug": "bus-terminal-incheon",
        "lat": 37.4567,
        "lng": 126.7078,
        "region": "incheon",
        "note": "Incheon Bus Terminal",
        "ko": {
            "name": "인천종합터미널",
            "desc": "인천 시내의 고속·시외버스 터미널. 구월동 일대와 가깝습니다.",
            "how": "인천 1호선 인천터미널역 연결.",
            "address": "인천 미추홀구 연남로 35",
            "regionLabel": "인천",
        },
        "en": {
            "name": "Incheon Bus Terminal",
            "desc": "Incheon city express/intercity terminal near Guwol.",
            "how": "Incheon Metro Line 1 Incheon Terminal Station.",
            "address": "35 Yeonnam-ro, Michuhol-gu, Incheon",
            "regionLabel": "Incheon",
        },
        "maps_q": "인천종합터미널",
        "wiki": None,
    },
    {
        "slug": "bus-terminal-suwon",
        "lat": 37.2505,
        "lng": 127.02,
        "region": "gyeonggi",
        "note": "Suwon Bus Terminal",
        "ko": {
            "name": "수원버스터미널",
            "desc": "수원 고속·시외버스터미널. 경기 남부 환승에 자주 쓰입니다.",
            "how": "수원역에서 버스·택시, 또는 터미널 정류장 시내버스.",
            "address": "경기 수원시 권선구 경수대로 270",
            "regionLabel": "경기",
        },
        "en": {
            "name": "Suwon Bus Terminal",
            "desc": "Suwon express/intercity terminal — southern Gyeonggi transfer hub.",
            "how": "Bus/taxi from Suwon Station, or local buses to the terminal.",
            "address": "270 Gyeongsu-daero, Gwonseon-gu, Suwon",
            "regionLabel": "Gyeonggi",
        },
        "maps_q": "수원버스터미널",
        "wiki": None,
    },
    {
        "slug": "bus-terminal-jeonju",
        "lat": 35.8415,
        "lng": 127.124,
        "region": "jeolla",
        "note": "Jeonju Express Bus Terminal",
        "ko": {
            "name": "전주고속버스터미널",
            "desc": "전주 고속버스 터미널. 한옥마을 관광의 시외 출발점으로 자주 쓰입니다.",
            "how": "전주시외·고속 터미널 일대. 한옥마을까지 버스·택시.",
            "address": "전북 전주시 덕진구 번영로 기린대로 전주고속버스터미널",
            "regionLabel": "전라",
        },
        "en": {
            "name": "Jeonju Express Bus Terminal",
            "desc": "Jeonju express coaches — common gateway for Hanok Village trips.",
            "how": "Local bus/taxi to Jeonju Hanok Village from the terminal area.",
            "address": "Jeonju Express Bus Terminal, Deokjin-gu, Jeonju",
            "regionLabel": "Jeolla",
        },
        "maps_q": "전주고속버스터미널",
        "wiki": None,
    },
    {
        "slug": "bus-terminal-ulsan",
        "lat": 35.5525,
        "lng": 129.339,
        "region": "gyeongsang",
        "note": "Ulsan Express Bus Terminal",
        "ko": {
            "name": "울산고속버스터미널",
            "desc": "울산 고속버스 터미널. 시외버스터미널과 인접한 교통 거점입니다.",
            "how": "시내버스·택시. 울산역(KTX)과는 거리가 있어 환승 시간을 보세요.",
            "address": "울산 남구 삼산로 257",
            "regionLabel": "경상",
        },
        "en": {
            "name": "Ulsan Express Bus Terminal",
            "desc": "Ulsan express bus hub (near the intercity terminal).",
            "how": "City bus/taxi. Allow time if transferring from Ulsan KTX Station.",
            "address": "257 Samsan-ro, Nam-gu, Ulsan",
            "regionLabel": "Gyeongsang",
        },
        "maps_q": "울산고속버스터미널",
        "wiki": None,
    },
    {
        "slug": "bus-terminal-gwangmyeong",
        "lat": 37.4164,
        "lng": 126.8849,
        "region": "gyeonggi",
        "note": "Near KTX Gwangmyeong — southern Gyeonggi coach access",
        "ko": {
            "name": "광명종합터미널",
            "desc": "광명·KTX광명 인근 버스 거점. 수도권 남서부 이동에 유용합니다.",
            "how": "1호선·KTX 광명 일대에서 버스·택시로 이동.",
            "address": "경기 광명시 광명종합터미널",
            "regionLabel": "경기",
        },
        "en": {
            "name": "Gwangmyeong Bus Terminal",
            "desc": "Coach access near Gwangmyeong / KTX Gwangmyeong in SW Gyeonggi.",
            "how": "Bus/taxi from Gwangmyeong Station (Line 1 / KTX area).",
            "address": "Gwangmyeong Bus Terminal, Gyeonggi",
            "regionLabel": "Gyeonggi",
        },
        "maps_q": "광명종합터미널",
        "wiki": None,
    },
]

# Lightweight translations for non-en locales (name/desc/how/regionLabel)
LOCALE_NAMES = {
    "ja": {
        "bus-terminal-seoul-express": ("ソウル高速バスターミナル", "江南セントラルシティの高速バス拠点。", "地下鉄3・7・9号線高速ターミナル駅。", "ソウル"),
        "bus-terminal-east-seoul": ("東ソウル総合ターミナル", "江辺駅とつながる東部ソウルのバス拠点。", "地下鉄2号線江辺駅。", "ソウル"),
        "bus-terminal-nambu": ("ソウル南部ターミナル", "瑞草の市外・高速バスターミナル。", "地下鉄3号線南部ターミナル駅前。", "ソウル"),
        "bus-terminal-busan": ("釜山総合バスターミナル", "老圃の高速・市外バス拠点。", "釜山1号線老圃駅。", "釜山"),
        "bus-terminal-daegu": ("東大邱複合乗り換えセンター", "東大邱駅直結のバス拠点。", "KTX・地下鉄東大邱駅。", "大邱"),
        "bus-terminal-daejeon": ("大田複合ターミナル", "大田の高速・市外複合ターミナル。", "大田1号線複合ターミナル駅。", "大田"),
        "bus-terminal-gwangju": ("光州総合バスターミナル（ユースクエア）", "ユースクエア内の高速・市外バス。", "光州市内バス・タクシー。", "光州"),
        "bus-terminal-incheon": ("仁川総合ターミナル", "仁川市内の高速・市外バスターミナル。", "仁川1号線仁川ターミナル駅。", "仁川"),
        "bus-terminal-suwon": ("水原バスターミナル", "京畿南部のバス乗り換え拠点。", "水原駅からバス・タクシー。", "京畿"),
        "bus-terminal-jeonju": ("全州高速バスターミナル", "全州韓屋村観光のバス玄関。", "韓屋村までバス・タクシー。", "全羅"),
        "bus-terminal-ulsan": ("蔚山高速バスターミナル", "蔚山の高速バス拠点。", "市内バス・タクシー。", "慶尚"),
        "bus-terminal-gwangmyeong": ("光明総合ターミナル", "光明・KTX光明付近のバス拠点。", "光明駅からバス・タクシー。", "京畿"),
    },
    "zh": {
        "bus-terminal-seoul-express": ("首尔高速巴士客运站", "江南Central City全国高速巴士枢纽。", "地铁3/7/9号线高速巴士客运站。", "首尔"),
        "bus-terminal-east-seoul": ("东首尔综合客运站", "首尔东部高速/市外巴士枢纽。", "地铁2号线江边站。", "首尔"),
        "bus-terminal-nambu": ("首尔南部客运站", "瑞草市外与高速巴士站。", "地铁3号线南部客运站。", "首尔"),
        "bus-terminal-busan": ("釜山综合客运站", "老圃高速与市外巴士中心。", "釜山地铁1号线老圃站。", "釜山"),
        "bus-terminal-daegu": ("东大邱综合换乘中心", "连接东大邱站的巴士枢纽。", "KTX/地铁东大邱站。", "大邱"),
        "bus-terminal-daejeon": ("大田综合客运站", "大田高速与市外综合站。", "大田地铁1号线综合客运站。", "大田"),
        "bus-terminal-gwangju": ("光州综合客运站（U-Square）", "U-Square内高速与市外巴士。", "市内公交/出租。", "光州"),
        "bus-terminal-incheon": ("仁川综合客运站", "仁川市区高速与市外巴士站。", "仁川地铁1号线仁川客运站。", "仁川"),
        "bus-terminal-suwon": ("水原客运站", "京畿南部巴士换乘枢纽。", "水原站公交/出租。", "京畿"),
        "bus-terminal-jeonju": ("全州高速客运站", "前往全州韩屋村的常见门户。", "客运站到韩屋村公交/出租。", "全罗"),
        "bus-terminal-ulsan": ("蔚山高速客运站", "蔚山高速巴士枢纽。", "市内公交/出租。", "庆尚"),
        "bus-terminal-gwangmyeong": ("光明综合客运站", "光明/KTX光明附近巴士节点。", "光明站公交/出租。", "京畿"),
    },
    "zh-Hant": {
        "bus-terminal-seoul-express": ("首爾高速巴士客運站", "江南Central City全國高速巴士樞紐。", "地鐵3/7/9號線高速巴士客運站。", "首爾"),
        "bus-terminal-east-seoul": ("東首爾綜合客運站", "首爾東部高速/市外巴士樞紐。", "地鐵2號線江邊站。", "首爾"),
        "bus-terminal-nambu": ("首爾南部客運站", "瑞草市外與高速巴士站。", "地鐵3號線南部客運站。", "首爾"),
        "bus-terminal-busan": ("釜山綜合客運站", "老圃高速與市外巴士中心。", "釜山地鐵1號線老圃站。", "釜山"),
        "bus-terminal-daegu": ("東大邱綜合轉乘中心", "連接東大邱站的巴士樞紐。", "KTX/地鐵東大邱站。", "大邱"),
        "bus-terminal-daejeon": ("大田綜合客運站", "大田高速與市外綜合站。", "大田地鐵1號線綜合客運站。", "大田"),
        "bus-terminal-gwangju": ("光州綜合客運站（U-Square）", "U-Square內高速與市外巴士。", "市內公車/計程車。", "光州"),
        "bus-terminal-incheon": ("仁川綜合客運站", "仁川市區高速與市外巴士站。", "仁川地鐵1號線仁川客運站。", "仁川"),
        "bus-terminal-suwon": ("水原客運站", "京畿南部巴士轉乘樞紐。", "水原站公車/計程車。", "京畿"),
        "bus-terminal-jeonju": ("全州高速客運站", "前往全州韓屋村的常見門戶。", "客運站到韓屋村公車/計程車。", "全羅"),
        "bus-terminal-ulsan": ("蔚山高速客運站", "蔚山高速巴士樞紐。", "市內公車/計程車。", "慶尚"),
        "bus-terminal-gwangmyeong": ("光明綜合客運站", "光明/KTX光明附近巴士節點。", "光明站公車/計程車。", "京畿"),
    },
    "vi": {
        "bus-terminal-seoul-express": ("Bến xe khách cao tốc Seoul", "Trung tâm xe khách toàn quốc tại Gangnam Central City.", "Tàu điện ngầm 3/7/9 ga Express Bus Terminal.", "Seoul"),
        "bus-terminal-east-seoul": ("Bến xe Đông Seoul", "Bến xe phía đông Seoul gần Gangbyeon.", "Tuyến 2 ga Gangbyeon.", "Seoul"),
        "bus-terminal-nambu": ("Bến xe Nambu Seoul", "Bến xe liên tỉnh/phía nam Seoul.", "Tuyến 3 ga Nambu Bus Terminal.", "Seoul"),
        "bus-terminal-busan": ("Bến xe trung tâm Busan", "Trung tâm xe khách tại Nopo, Busan.", "Tuyến 1 Busan ga Nopo.", "Busan"),
        "bus-terminal-daegu": ("Trung tâm trung chuyển Dongdaegu", "Bến xe liền kề ga Dongdaegu.", "KTX/metro ga Dongdaegu.", "Daegu"),
        "bus-terminal-daejeon": ("Bến xe phức hợp Daejeon", "Bến xe cao tốc/liên tỉnh Daejeon.", "Tuyến 1 Daejeon ga Complex Terminal.", "Daejeon"),
        "bus-terminal-gwangju": ("Bến xe Gwangju (U-Square)", "Xe khách trong khu phức hợp U-Square.", "Bus/taxi nội thành.", "Gwangju"),
        "bus-terminal-incheon": ("Bến xe Incheon", "Bến xe cao tốc/liên tỉnh nội thành Incheon.", "Tuyến 1 Incheon ga Incheon Terminal.", "Incheon"),
        "bus-terminal-suwon": ("Bến xe Suwon", "Trung chuyển phía nam Gyeonggi.", "Bus/taxi từ ga Suwon.", "Gyeonggi"),
        "bus-terminal-jeonju": ("Bến xe cao tốc Jeonju", "Cửa ngõ xe khách tới làng Hanok Jeonju.", "Bus/taxi tới làng Hanok.", "Jeolla"),
        "bus-terminal-ulsan": ("Bến xe cao tốc Ulsan", "Trung tâm xe khách cao tốc Ulsan.", "Bus/taxi nội thành.", "Gyeongsang"),
        "bus-terminal-gwangmyeong": ("Bến xe Gwangmyeong", "Bến xe gần Gwangmyeong/KTX.", "Bus/taxi từ ga Gwangmyeong.", "Gyeonggi"),
    },
    "th": {
        "bus-terminal-seoul-express": ("สถานีรถบัสทางด่วนโซล", "ศูนย์รถบัสทางด่วนที่ Central City แขวงคังนัม", "รถไฟใต้ดินสาย 3/7/9 สถานี Express Bus Terminal", "โซล"),
        "bus-terminal-east-seoul": ("สถานีรถบัสตะวันออกโซล", "ศูนย์รถบัสฝั่งตะวันออกใกล้คังบยอน", "สาย 2 สถานี Gangbyeon", "โซล"),
        "bus-terminal-nambu": ("สถานีรถบัสนัมบูโซล", "สถานีรถบัสชานเมือง/ทางด่วนฝั่งใต้", "สาย 3 สถานี Nambu Bus Terminal", "โซล"),
        "bus-terminal-busan": ("สถานีรถบัสกลางปูซาน", "ศูนย์รถบัสที่โนโพ ปูซาน", "สาย 1 ปูซาน สถานี Nopo", "ปูซาน"),
        "bus-terminal-daegu": ("ศูนย์เปลี่ยนถ่ายดงแดกู", "ศูนย์รถบัสติดสถานีดงแดกู", "KTX/รถไฟใต้ดิน สถานี Dongdaegu", "แทกู"),
        "bus-terminal-daejeon": ("สถานีรถบัสรวมแทจอน", "สถานีรถบัสทางด่วน/ชานเมืองแทจอน", "สาย 1 แทจอน สถานี Complex Terminal", "แทจอน"),
        "bus-terminal-gwangju": ("สถานีรถบัสกวังจู (U-Square)", "รถบัสในคอมเพล็กซ์ U-Square", "รถเมล์/แท็กซี่ในเมือง", "กวังจู"),
        "bus-terminal-incheon": ("สถานีรถบัสอินชอน", "สถานีรถบัสในเมืองอินชอน", "สาย 1 อินชอน สถานี Incheon Terminal", "อินชอน"),
        "bus-terminal-suwon": ("สถานีรถบัสซูวอน", "จุดเปลี่ยนรถบัสทางใต้คยองกี", "รถเมล์/แท็กซี่จากสถานีซูวอน", "คยองกี"),
        "bus-terminal-jeonju": ("สถานีรถบัสทางด่วนชอนจู", "ประตูสู่หมู่บ้านฮันอกชอนจู", "รถเมล์/แท็กซี่ไปหมู่บ้านฮันอก", "ชอลลา"),
        "bus-terminal-ulsan": ("สถานีรถบัสทางด่วนอุลซาน", "ศูนย์รถบัสทางด่วนอุลซาน", "รถเมล์/แท็กซี่ในเมือง", "คยองซัง"),
        "bus-terminal-gwangmyeong": ("สถานีรถบัสควังมยอง", "จุดรถบัสใกล้ควังมยอง/KTX", "รถเมล์/แท็กซี่จากสถานีควังมยอง", "คยองกี"),
    },
    "ru": {
        "bus-terminal-seoul-express": ("Сеульский экспресс-автовокзал", "Главный хаб междугородних автобусов в Central City (Каннам).", "Метро 3/7/9, станция Express Bus Terminal.", "Сеул"),
        "bus-terminal-east-seoul": ("Восточный автовокзал Сеула", "Автовокзал на востоке Сеула у Канбён.", "Линия 2, станция Gangbyeon.", "Сеул"),
        "bus-terminal-nambu": ("Южный автовокзал Сеула", "Междугородний/экспресс-вокзал в Сочхо.", "Линия 3, станция Nambu Bus Terminal.", "Сеул"),
        "bus-terminal-busan": ("Центральный автовокзал Пусана", "Главный автобусный хаб в Нопо.", "Линия 1 Пусана, станция Nopo.", "Пусан"),
        "bus-terminal-daegu": ("Трансферный центр Тондэгу", "Автобусный хаб у станции Тондэгу.", "KTX/метро, станция Dongdaegu.", "Тэгу"),
        "bus-terminal-daejeon": ("Комплексный автовокзал Тэджона", "Экспресс и междугородние рейсы Тэджона.", "Линия 1, станция Complex Terminal.", "Тэджон"),
        "bus-terminal-gwangju": ("Автовокзал Кванджу (U-Square)", "Автобусы в комплексе U-Square.", "Городской автобус/такси.", "Кванджу"),
        "bus-terminal-incheon": ("Автовокзал Инчхона", "Городской экспресс/междугородний вокзал.", "Линия 1 Инчхона, станция Incheon Terminal.", "Инчхон"),
        "bus-terminal-suwon": ("Автовокзал Сувона", "Пересадочный хаб южного Кёнги.", "Автобус/такси от станции Сувон.", "Кёнги"),
        "bus-terminal-jeonju": ("Экспресс-автовокзал Чонджу", "Частые рейсы к деревне ханок Чонджу.", "Автобус/такси до деревни ханок.", "Чолла"),
        "bus-terminal-ulsan": ("Экспресс-автовокзал Ульсана", "Главный экспресс-хаб Ульсана.", "Городской автобус/такси.", "Кёнсан"),
        "bus-terminal-gwangmyeong": ("Автовокзал Кванмёна", "Узел у Кванмён / KTX Кванмён.", "Автобус/такси от станции Кванмён.", "Кёнги"),
    },
}


def _ssl() -> ssl.SSLContext:
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl._create_unverified_context()


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


def entry_for_lang(lang: str, t: dict) -> dict:
    ko, en = t["ko"], t["en"]
    slug = t["slug"]
    hl = {"zh-Hant": "zh-TW", "zh": "zh-CN"}.get(lang, lang if lang != "ko" else "ko")
    maps, embed = maps_urls(t["maps_q"], hl if lang != "en" else "en")
    img = f"Images/places/{slug}.jpg"
    if lang == "ko":
        base = {
            "name": ko["name"],
            "desc": ko["desc"],
            "how": ko["how"],
            "address": ko["address"],
            "regionLabel": ko["regionLabel"],
            "region": t["region"] or "",
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
            "regionLabel": en["regionLabel"],
            "region": t["region"] or "",
            "mapsUrl": maps_urls(t["maps_q"], "en")[0],
            "mapsEmbedUrl": maps_urls(t["maps_q"], "en")[1],
            "image": img,
        }
    else:
        pack = LOCALE_NAMES[lang][slug]
        base = {
            "name": pack[0],
            "desc": pack[1],
            "how": pack[2],
            "address": en["address"] if lang in ("vi", "th", "ru") else ko["address"],
            "regionLabel": pack[3],
            "region": t["region"] or "",
            "mapsUrl": maps,
            "mapsEmbedUrl": embed,
            "image": img,
        }
    extras = {
        L: LOCALE_NAMES[L][slug]
        for L in ("ja", "zh", "zh-Hant", "vi", "th", "ru")
    }
    base["body"] = body_block(ko, en, extras)
    return base


def patch_coords() -> int:
    text = COORDS.read_text(encoding="utf-8")
    if "bus-terminal-seoul-express" in text:
        print("places-coords already has bus terminals")
        return 0
    text = text.replace(
        ' * type: "city" | "nature" | "heritage" | "airport" | "info" | "locker" | "port"',
        ' * type: "city" | "nature" | "heritage" | "airport" | "info" | "locker" | "port" | "bus-terminal"',
    )
    text = text.replace(
        " *   port     — major harbors / passenger ferry terminals",
        " *   port     — major harbors / passenger ferry terminals\n"
        " *   bus-terminal — major express / intercity bus terminals",
    )
    lines = []
    for t in TERMINALS:
        img = f"Images/places/{t['slug']}.jpg"
        lines.append(
            "  { "
            f'slug: "{t["slug"]}", lat: {t["lat"]}, lng: {t["lng"]}, '
            f'region: "{t["region"]}", type: "bus-terminal", '
            f'note: "{t["note"]}", image: "{img}" '
            "},"
        )
    insert = "\n".join(lines) + "\n"
    # Before closing ];
    idx = text.rfind("];")
    if idx < 0:
        raise SystemExit("places-coords.js: cannot find ];")
    text = text[:idx] + insert + text[idx:]
    COORDS.write_text(text, encoding="utf-8", newline="\n")
    return len(TERMINALS)


def patch_i18n() -> None:
    transport_keys = {
        "legendBusTerminal": {
            "ko": "버스터미널",
            "en": "Bus terminal",
            "ja": "バスターミナル",
            "zh": "巴士客运站",
            "zh-Hant": "巴士客運站",
            "vi": "Bến xe",
            "th": "สถานีรถบัส",
            "ru": "Автовокзал",
        },
        "busTerminalBadge": {
            "ko": "버스터미널 · 고속·시외 거점",
            "en": "Bus terminal · express / intercity hub",
            "ja": "バスターミナル · 高速・市外拠点",
            "zh": "巴士客运站 · 高速/市外枢纽",
            "zh-Hant": "巴士客運站 · 高速/市外樞紐",
            "vi": "Bến xe · trung tâm xe khách",
            "th": "สถานีรถบัส · ศูนย์รถโดยสาร",
            "ru": "Автовокзал · междугородний хаб",
        },
        "metroRegionSeoul": {
            "ko": "서울·수도권",
            "en": "Seoul / capital area",
            "ja": "ソウル・首都圏",
            "zh": "首尔·首都圈",
            "zh-Hant": "首爾·首都圈",
            "vi": "Seoul / thủ đô",
            "th": "โซล/ปริมณฑล",
            "ru": "Сеул / столичный регион",
        },
        "metroRegionBusan": {
            "ko": "부산",
            "en": "Busan",
            "ja": "釜山",
            "zh": "釜山",
            "zh-Hant": "釜山",
            "vi": "Busan",
            "th": "ปูซาน",
            "ru": "Пусан",
        },
        "metroRegionDaegu": {
            "ko": "대구",
            "en": "Daegu",
            "ja": "大邱",
            "zh": "大邱",
            "zh-Hant": "大邱",
            "vi": "Daegu",
            "th": "แทกู",
            "ru": "Тэгу",
        },
        "metroRegionGwangju": {
            "ko": "광주",
            "en": "Gwangju",
            "ja": "光州",
            "zh": "光州",
            "zh-Hant": "光州",
            "vi": "Gwangju",
            "th": "กวังจู",
            "ru": "Кванджу",
        },
        "metroRegionDaejeon": {
            "ko": "대전",
            "en": "Daejeon",
            "ja": "大田",
            "zh": "大田",
            "zh-Hant": "大田",
            "vi": "Daejeon",
            "th": "แทจอน",
            "ru": "Тэджон",
        },
        "lineBusan1": {"ko": "부산1호선", "en": "Busan Line 1", "ja": "釜山1号線", "zh": "釜山1号线", "zh-Hant": "釜山1號線", "vi": "Busan tuyến 1", "th": "ปูซานสาย 1", "ru": "Пусан линия 1"},
        "lineBusan2": {"ko": "부산2호선", "en": "Busan Line 2", "ja": "釜山2号線", "zh": "釜山2号线", "zh-Hant": "釜山2號線", "vi": "Busan tuyến 2", "th": "ปูซานสาย 2", "ru": "Пусан линия 2"},
        "lineBusan3": {"ko": "부산3호선", "en": "Busan Line 3", "ja": "釜山3号線", "zh": "釜山3号线", "zh-Hant": "釜山3號線", "vi": "Busan tuyến 3", "th": "ปูซานสาย 3", "ru": "Пусан линия 3"},
        "lineBusan4": {"ko": "부산4호선", "en": "Busan Line 4", "ja": "釜山4号線", "zh": "釜山4号线", "zh-Hant": "釜山4號線", "vi": "Busan tuyến 4", "th": "ปูซานสาย 4", "ru": "Пусан линия 4"},
        "lineBusanGimhae": {"ko": "부산김해경전철", "en": "Busan–Gimhae LRT", "ja": "釜山金海軽電鉄", "zh": "釜山金海轻轨", "zh-Hant": "釜山金海輕軌", "vi": "Busan–Gimhae", "th": "ปูซาน–กิมแฮ", "ru": "Пусан–Кимхэ"},
        "lineDaegu1": {"ko": "대구1호선", "en": "Daegu Line 1", "ja": "大邱1号線", "zh": "大邱1号线", "zh-Hant": "大邱1號線", "vi": "Daegu tuyến 1", "th": "แทกูสาย 1", "ru": "Тэгу линия 1"},
        "lineDaegu2": {"ko": "대구2호선", "en": "Daegu Line 2", "ja": "大邱2号線", "zh": "大邱2号线", "zh-Hant": "大邱2號線", "vi": "Daegu tuyến 2", "th": "แทกูสาย 2", "ru": "Тэгу линия 2"},
        "lineDaegu3": {"ko": "대구3호선", "en": "Daegu Line 3", "ja": "大邱3号線", "zh": "大邱3号线", "zh-Hant": "大邱3號線", "vi": "Daegu tuyến 3", "th": "แทกูสาย 3", "ru": "Тэгу линия 3"},
        "lineGwangju1": {"ko": "광주1호선", "en": "Gwangju Line 1", "ja": "光州1号線", "zh": "光州1号线", "zh-Hant": "光州1號線", "vi": "Gwangju tuyến 1", "th": "กวังจูสาย 1", "ru": "Кванджу линия 1"},
        "lineDaejeon1": {"ko": "대전1호선", "en": "Daejeon Line 1", "ja": "大田1号線", "zh": "大田1号线", "zh-Hant": "大田1號線", "vi": "Daejeon tuyến 1", "th": "แทจอนสาย 1", "ru": "Тэджон линия 1"},
        "filterGroupToggle": {
            "ko": "이 분류 전체",
            "en": "All in group",
            "ja": "この分類すべて",
            "zh": "本分类全部",
            "zh-Hant": "本分類全部",
            "vi": "Tất cả nhóm",
            "th": "ทั้งหมดในกลุ่ม",
            "ru": "Вся группа",
        },
    }

    for lang in ("ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru"):
        path = I18N / f"{lang}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        tr = data.setdefault("transport", {})
        for key, locales in transport_keys.items():
            tr[key] = locales.get(lang) or locales["en"]
        places = data.setdefault("places", {})
        for t in TERMINALS:
            places[t["slug"]] = entry_for_lang(lang, t)
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"i18n {lang}: +{len(TERMINALS)} terminals")


def download_images() -> None:
    IMG.mkdir(parents=True, exist_ok=True)
    # Type fallback: copy port-ish or create from airport if needed
    fallback_src = IMG / "_types" / "port.jpg"
    type_dst = IMG / "_types" / "bus-terminal.jpg"
    if fallback_src.exists() and not type_dst.exists():
        type_dst.write_bytes(fallback_src.read_bytes())
        print("wrote type fallback bus-terminal.jpg")

    ctx = _ssl()
    for t in TERMINALS:
        dest = IMG / f"{t['slug']}.jpg"
        if dest.exists() and dest.stat().st_size > 5000:
            continue
        url = t.get("wiki")
        if not url:
            if type_dst.exists():
                dest.write_bytes(type_dst.read_bytes())
                print(f"fallback image {dest.name}")
            continue
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "KoreaTravelGuidebook/1.0"})
            with urllib.request.urlopen(req, timeout=40, context=ctx) as r:
                dest.write_bytes(r.read())
            print(f"downloaded {dest.name} ({dest.stat().st_size} bytes)")
        except Exception as exc:  # noqa: BLE001
            print(f"image fail {t['slug']}: {exc}")
            if type_dst.exists():
                dest.write_bytes(type_dst.read_bytes())


def main() -> int:
    n = patch_coords()
    print(f"coords added: {n}")
    patch_i18n()
    download_images()
    # rebuild messages.js
    sys.path.insert(0, str(ROOT / "tool"))
    from lib import i18n_store

    print(i18n_store.build_bundle())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
