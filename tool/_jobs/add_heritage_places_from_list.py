# -*- coding: utf-8 -*-
"""Add heritage sightseeing places from cultural-heritage name list.

Parses the large 문화재 filter list, skips duplicates / already-present places,
appends to places-coords.js + i18n (ko/en + copy for other langs), uses
Images/places/_types/heritage.jpg as image fallback, then rebuilds messages.js.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
COORDS = ROOT / "data" / "places" / "places-coords.js"
IMG = ROOT / "Images" / "places"
TYPE_FALLBACK = IMG / "_types" / "heritage.jpg"
SOURCE = Path(
    r"C:\Users\HwangInTae\Desktop\guide book\명소 추가할 자료\문화재 필터 이름정보.txt"
)

sys.path.insert(0, str(ROOT / "tool"))

# Section header → places-coords region key
SECTION_REGION = {
    "서울": "seoul",
    "경기": "gyeonggi",
    "인천": "incheon",
    "부산": "busan",
    "대구": "",  # daegu uses empty region in this guidebook
    "경주": "gyeongju",
    "안동": "gyeongsang",
    "전주": "jeolla",
    "공주": "chungcheong",
    "부여": "chungcheong",
    "강원": "gangwon",
    "충북": "chungcheong",
    "충남": "chungcheong",
    "전북": "jeolla",
    "전남": "jeolla",
    "광주": "jeolla",
    "경남": "gyeongsang",
    "울산": "gyeongsang",
    "제주": "jeju",
    "대전": "chungcheong",
    "세종": "chungcheong",
    "포항": "gyeongsang",
    "영주": "gyeongsang",
    "통영": "gyeongsang",
    "순천": "jeolla",
    "담양": "jeolla",
    "합천": "gyeongsang",
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
    "gyeonggi": {
        "ko": "경기",
        "en": "Gyeonggi",
        "ja": "京畿",
        "zh": "京畿",
        "zh-Hant": "京畿",
        "vi": "Gyeonggi",
        "th": "คยองกี",
        "ru": "Кёнги",
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
    "gyeongju": {
        "ko": "경주",
        "en": "Gyeongju",
        "ja": "慶州",
        "zh": "庆州",
        "zh-Hant": "慶州",
        "vi": "Gyeongju",
        "th": "คยองจู",
        "ru": "Кёнджу",
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

# Approximate guidebook centers when a place has no curated coords
REGION_CENTER = {
    "seoul": (37.5665, 126.9780),
    "gyeonggi": (37.4138, 127.5183),
    "incheon": (37.4563, 126.7052),
    "busan": (35.1796, 129.0756),
    "": (35.8714, 128.6014),  # daegu
    "gyeongju": (35.8562, 129.2247),
    "gyeongsang": (35.5384, 129.3114),
    "jeolla": (35.8242, 127.1480),
    "chungcheong": (36.4500, 127.1200),
    "gangwon": (37.8228, 128.1555),
    "jeju": (33.4996, 126.5312),
}

# Explicit skip: mountains / beaches / nature rocks / theme parks (not heritage sightseeing)
SKIP_NAMES = {
    "산방산",
    "용두암",
    "부안 채석강",
    "채석강",
    "완산칠봉",
    "남해 독일마을",
    "합천영상테마파크",
    "오대산 월정사 전나무숲길",
    "유성온천 문화유적",
    "금강수목원 주변 역사유적",
}

# Known aliases → existing slug (skip as already present)
EXISTING_ALIASES = {
    "경복궁": "gyeongbok",
    "수원화성": "suwon",
    "수원 화성": "suwon",
    "북촌한옥마을": "bukchon",
    "북촌 한옥마을": "bukchon",
    "불국사": "bulguksa",
    "동궁과 월지": "donggung",
    "동궁과월지": "donggung",
    "전주한옥마을": "jeonju",
    "전주 한옥마을": "jeonju",
    "해동용궁사": "haedong",
    "파주 임진각": "imjingak",
    "임진각": "imjingak",
    "임진각·DMZ": "imjingak",
    "파주 DMZ": "imjingak",
    "하회마을": "hahoe",
    "안동 하회마을": "hahoe",
}

# Curated lat/lng for major / recognizable sites (guidebook-approximate)
KNOWN_COORDS: dict[str, tuple[float, float]] = {
    "경복궁": (37.5796, 126.9770),
    "창덕궁": (37.5794, 126.9910),
    "창경궁": (37.5788, 126.9950),
    "덕수궁": (37.5658, 126.9750),
    "경희궁": (37.5714, 126.9682),
    "종묘": (37.5744, 126.9940),
    "북촌한옥마을": (37.5826, 126.9831),
    "남산골한옥마을": (37.5592, 126.9944),
    "한양도성": (37.5815, 126.9875),
    "숭례문": (37.5599, 126.9753),
    "흥인지문": (37.5712, 127.0095),
    "광화문": (37.5760, 126.9769),
    "운현궁": (37.5755, 126.9865),
    "서대문형무소역사관": (37.5745, 126.9562),
    "독립문": (37.5724, 126.9595),
    "탑골공원": (37.5709, 126.9883),
    "암사동 선사유적지": (37.5603, 127.1298),
    "몽촌토성": (37.5215, 127.1228),
    "풍납토성": (37.5315, 127.1165),
    "석촌동 고분군": (37.5108, 127.1025),
    "선릉·정릉": (37.5075, 127.0485),
    "정릉": (37.6105, 127.0065),
    "홍릉·유릉": (37.5965, 127.0825),
    "성균관": (37.5875, 126.9940),
    "양화진 외국인선교사묘원": (37.5485, 126.9115),
    "진관사": (37.6385, 126.9465),
    "봉은사": (37.5150, 127.0575),
    "길상사": (37.5965, 126.9955),
    "보신각": (37.5698, 126.9836),
    "서울성곽길": (37.5815, 126.9875),
    "수원화성": (37.2851, 127.0115),
    "화성행궁": (37.2825, 127.0145),
    "남한산성": (37.4785, 127.1825),
    "광명동굴": (37.4255, 126.8655),
    "한국민속촌": (37.2585, 127.1175),
    "파주 임진각": (37.8892, 126.7403),
    "파주 DMZ": (37.8905, 126.7400),
    "용인 호암미술관 전통정원": (37.2205, 127.2155),
    "실학박물관": (37.5955, 127.1955),
    "세종대왕릉": (37.3055, 127.4155),
    "신륵사": (37.2955, 127.5855),
    "용주사": (37.2105, 127.0055),
    "융건릉": (37.2105, 126.9855),
    "남양주 홍유릉": (37.6355, 127.2155),
    "광릉": (37.7505, 127.1755),
    "아차산성": (37.5555, 127.1055),
    "행주산성": (37.5955, 126.8255),
    "파주 삼릉": (37.7255, 126.8455),
    "파주 장릉": (37.7455, 126.7755),
    "강화역사유적지구": (37.7455, 126.4855),
    "강화 전등사": (37.6325, 126.4855),
    "강화 고인돌": (37.7255, 126.4455),
    "강화 초지진": (37.6355, 126.5255),
    "강화 광성보": (37.6455, 126.5155),
    "강화 덕진진": (37.6555, 126.5055),
    "강화 고려궁지": (37.7485, 126.4855),
    "강화 외규장각": (37.7485, 126.4875),
    "강화 성공회성당": (37.7475, 126.4855),
    "인천 개항장 문화지구": (37.4735, 126.6215),
    "인천 중구청 구 일본우선주식회사 건물": (37.4725, 126.6215),
    "인천 내리교회": (37.4735, 126.6255),
    "인천향교": (37.4555, 126.7055),
    "문학산성": (37.4355, 126.6855),
    "계양산성": (37.5455, 126.7355),
    "송월동 동화마을": (37.4755, 126.6255),
    "범어사": (35.2835, 129.0685),
    "해동용궁사": (35.1884, 129.2233),
    "충렬사": (35.2055, 129.0855),
    "동래읍성": (35.2055, 129.0855),
    "복천동고분군": (35.2085, 129.0905),
    "부산근대역사관": (35.1025, 129.0325),
    "임시수도기념관": (35.1055, 129.0355),
    "부산진성": (35.1055, 129.0405),
    "금정산성": (35.2555, 129.0555),
    "유엔기념공원": (35.1285, 129.0955),
    "오륜대 한국순교자박물관": (35.2455, 129.1055),
    "기장 죽성리 왜성": (35.1955, 129.2255),
    "몰운대": (35.0455, 128.9655),
    "부산항 제1부두 근대유산": (35.1025, 129.0405),
    "동화사": (35.9955, 128.7055),
    "갓바위": (35.9855, 128.7255),
    "달성공원": (35.8755, 128.5655),
    "대구읍성 유적": (35.8705, 128.5955),
    "계산성당": (35.8685, 128.5855),
    "이상화 고택": (35.8685, 128.5905),
    "서상돈 고택": (35.8685, 128.5925),
    "대구근대역사관": (35.8685, 128.5955),
    "약령시 한의약박물관": (35.8685, 128.5905),
    "국채보상운동기념관": (35.8705, 128.6005),
    "육신사": (35.8755, 128.6105),
    "파계사": (35.9955, 128.6355),
    "한훤당 고택": (35.8555, 128.5555),
    "남평문씨본리세거지": (35.8255, 128.5255),
    "불국사": (35.7900, 129.3320),
    "석굴암": (35.7950, 129.3490),
    "첨성대": (35.8347, 129.2190),
    "대릉원": (35.8385, 129.2125),
    "동궁과 월지": (35.8347, 129.2268),
    "월정교": (35.8295, 129.2185),
    "황룡사지": (35.8415, 129.2285),
    "분황사": (35.8405, 129.2335),
    "포석정": (35.8125, 129.2155),
    "경주 교촌마을": (35.8325, 129.2125),
    "최부자댁": (35.8455, 129.2055),
    "국립경주박물관": (35.8295, 129.2285),
    "무열왕릉": (35.8255, 129.2055),
    "김유신묘": (35.8455, 129.1955),
    "문무대왕릉": (35.7055, 129.4755),
    "감은사지": (35.7305, 129.4755),
    "골굴사": (35.7755, 129.3555),
    "남산 불교유적": (35.8055, 129.2255),
    "계림": (35.8325, 129.2155),
    "경주 읍성": (35.8455, 129.2155),
    "하회마을": (36.5391, 128.5178),
    "도산서원": (36.7255, 128.8455),
    "병산서원": (36.5355, 128.5355),
    "봉정사": (36.6455, 128.6655),
    "월영교": (36.5655, 128.7155),
    "안동민속촌": (36.5655, 128.7155),
    "임청각": (36.5655, 128.7255),
    "월영교 주변 전통문화유적": (36.5655, 128.7155),
    "안동향교": (36.5685, 128.7255),
    "제비원 석불": (36.6055, 128.7555),
    "봉황사": (36.5555, 128.7055),
    "예안향교": (36.6555, 128.7855),
    "전주한옥마을": (35.8150, 127.1530),
    "경기전": (35.8155, 127.1495),
    "전동성당": (35.8135, 127.1495),
    "풍남문": (35.8135, 127.1485),
    "전주향교": (35.8125, 127.1555),
    "오목대": (35.8155, 127.1555),
    "이목대": (35.8155, 127.1565),
    "조경단": (35.8155, 127.1575),
    "남고산성": (35.7955, 127.1555),
    "한벽당": (35.8055, 127.1655),
    "전주 객사": (35.8205, 127.1455),
    "공산성": (36.4625, 127.1265),
    "공주 공산성": (36.4625, 127.1265),
    "무령왕릉과 왕릉원": (36.4615, 127.1135),
    "공주 무령왕릉": (36.4615, 127.1135),
    "국립공주박물관": (36.4655, 127.1155),
    "공주 마곡사": (36.5605, 127.0155),
    "마곡사": (36.5605, 127.0155),
    "공주향교": (36.4555, 127.1255),
    "공주 충청감영": (36.4555, 127.1255),
    "공주 제민천 역사문화거리": (36.4555, 127.1255),
    "송산리 고분군": (36.4615, 127.1135),
    "부소산성": (36.2755, 126.9155),
    "부여 부소산성": (36.2755, 126.9155),
    "관북리유적": (36.2755, 126.9125),
    "정림사지": (36.2755, 126.9105),
    "부여 정림사지": (36.2755, 126.9105),
    "궁남지": (36.2705, 126.9155),
    "부여 궁남지": (36.2705, 126.9155),
    "능산리 고분군": (36.2755, 126.9255),
    "백제문화단지": (36.3055, 126.9055),
    "국립부여박물관": (36.2755, 126.9105),
    "부여 나성": (36.2755, 126.9055),
    "무량사": (36.2955, 126.8555),
    "성흥산성": (36.2855, 126.8855),
    "오죽헌": (37.7795, 128.8785),
    "선교장": (37.7855, 128.8855),
    "경포대": (37.7955, 128.8955),
    "강릉향교": (37.7555, 128.8955),
    "낙산사": (38.1255, 128.6255),
    "월정사": (37.7255, 128.5955),
    "상원사": (37.7355, 128.6055),
    "신흥사": (38.1755, 128.4855),
    "고성 왕곡마을": (38.3055, 128.5255),
    "강릉대도호부 관아": (37.7555, 128.8955),
    "죽서루": (37.4455, 129.1655),
    "청평사": (37.9855, 127.8155),
    "홍천 수타사": (37.6955, 127.8855),
    "법주사": (36.5455, 127.8355),
    "청남대": (36.6355, 127.4855),
    "상당산성": (36.6655, 127.5255),
    "충주 탄금대": (36.9855, 127.9255),
    "충주 탑평리 칠층석탑": (37.0055, 127.8655),
    "단양 온달관광지": (37.0155, 128.3655),
    "단양 적성": (36.9855, 128.3655),
    "청풍문화재단지": (37.0055, 128.1755),
    "보은 삼년산성": (36.4855, 127.7255),
    "괴산 화양구곡": (36.6655, 127.9255),
    "영동 영국사": (36.1755, 127.7855),
    "진천 농다리": (36.8555, 127.4455),
    "해미읍성": (36.7155, 126.5155),
    "현충사": (36.8055, 126.9755),
    "외암민속마을": (36.7355, 126.7955),
    "독립기념관": (36.7855, 127.2255),
    "돈암서원": (36.2755, 127.0855),
    "논산 관촉사": (36.2055, 127.0855),
    "논산 돈암서원": (36.2755, 127.0855),
    "서산 개심사": (36.7455, 126.5955),
    "익산 미륵사지": (36.0155, 127.0255),
    "익산 왕궁리유적": (35.9755, 127.0555),
    "고창 고인돌유적": (35.4355, 126.6355),
    "고창읍성": (35.4355, 126.7055),
    "무주 적상산성": (35.9655, 127.6955),
    "남원 광한루원": (35.4105, 127.3855),
    "남원 만복사지": (35.4055, 127.3855),
    "순창 강천사": (35.3755, 127.1455),
    "김제 금산사": (35.8055, 127.0555),
    "부안 내소사": (35.6255, 126.5855),
    "임실 사선대": (35.6155, 127.2855),
    "정읍 무성서원": (35.5655, 126.8555),
    "순천 낙안읍성": (34.9055, 127.3455),
    "낙안읍성": (34.9055, 127.3455),
    "순천 선암사": (34.9955, 127.3255),
    "선암사": (34.9955, 127.3255),
    "구례 화엄사": (35.2555, 127.4955),
    "구례 운조루": (35.2055, 127.4655),
    "담양 소쇄원": (35.2855, 126.9855),
    "소쇄원": (35.2855, 126.9855),
    "담양 식영정": (35.2955, 126.9955),
    "식영정": (35.2955, 126.9955),
    "담양 명옥헌": (35.3055, 127.0055),
    "명옥헌": (35.3055, 127.0055),
    "해남 대흥사": (34.4755, 126.6155),
    "장성 필암서원": (35.3055, 126.7855),
    "보성 대원사": (34.7755, 127.0855),
    "강진 무위사": (34.6055, 126.7655),
    "강진 다산초당": (34.5755, 126.7955),
    "영암 도갑사": (34.7455, 126.6655),
    "여수 진남관": (34.7405, 127.7355),
    "여수 흥국사": (34.7655, 127.7155),
    "여수 충민사": (34.7555, 127.7255),
    "목포 근대역사문화공간": (34.7855, 126.3855),
    "국립아시아문화전당": (35.1455, 126.9155),
    "광주향교": (35.1455, 126.9155),
    "포충사": (35.1455, 126.9355),
    "충장사": (35.1555, 126.9255),
    "무등산 증심사": (35.1355, 126.9855),
    "월봉서원": (35.1655, 126.8555),
    "환벽당": (35.1555, 126.9455),
    "취가정": (35.1555, 126.9455),
    "광주 5·18 민주화운동 관련 사적": (35.1455, 126.9155),
    "해인사": (35.8015, 128.0975),
    "통도사": (35.4855, 129.0655),
    "쌍계사": (35.2255, 127.6455),
    "진주성": (35.1905, 128.0805),
    "촉석루": (35.1905, 128.0805),
    "남해 금산 보리암": (34.7555, 127.9855),
    "통영 세병관": (34.8455, 128.4255),
    "세병관": (34.8455, 128.4255),
    "통영 충렬사": (34.8455, 128.4255),
    "합천 황매산성": (35.4855, 128.0055),
    "함양 남계서원": (35.5155, 127.7255),
    "산청 목면시배유지": (35.4155, 127.8755),
    "고성 송학동고분군": (34.9755, 128.3255),
    "창녕 교동·송현동 고분군": (35.5455, 128.4955),
    "반구대 암각화": (35.6055, 129.1755),
    "천전리 각석": (35.6155, 129.1755),
    "울산왜성": (35.5555, 129.3255),
    "언양읍성": (35.5655, 129.1255),
    "석남사": (35.6255, 129.0455),
    "대곡박물관": (35.6055, 129.1755),
    "처용암": (35.4655, 129.3555),
    "울산향교": (35.5555, 129.3155),
    "제주목 관아": (33.5155, 126.5255),
    "관덕정": (33.5155, 126.5255),
    "삼성혈": (33.5055, 126.5255),
    "항파두리 항몽유적지": (33.4555, 126.4055),
    "성읍민속마을": (33.3855, 126.7955),
    "대정성지": (33.2355, 126.2555),
    "제주 4·3 관련 유적": (33.3855, 126.6155),
    "제주 돌문화공원": (33.4455, 126.6655),
    "방사탑": (33.2555, 126.5155),
    "알뜨르비행장": (33.2055, 126.2655),
    "계족산성": (36.3855, 127.4255),
    "우암사적공원": (36.3555, 127.4055),
    "동춘당": (36.3555, 127.4455),
    "회덕향교": (36.3655, 127.4255),
    "남간정사": (36.3255, 127.3855),
    "대전근현대사전시관": (36.3255, 127.4255),
    "비암사": (36.5455, 127.2555),
    "세종대왕 영릉 관련 역사문화권": (37.3055, 127.4155),
    "김종서 장군 묘": (36.5055, 127.2855),
    "독락정": (36.4855, 127.2655),
    "연기향교": (36.5055, 127.2755),
    "보경사": (36.2555, 129.3255),
    "장기읍성": (36.0855, 129.3755),
    "장기향교": (36.0855, 129.3755),
    "오어사": (35.9955, 129.3455),
    "흥해향교": (36.1155, 129.3455),
    "부석사": (36.9955, 128.6855),
    "소수서원": (36.9455, 128.6155),
    "선비촌": (36.9455, 128.6155),
    "무섬마을": (36.8255, 128.5555),
    "영주 근대역사문화거리": (36.8055, 128.6255),
    "통영성지": (34.8455, 128.4255),
    "착량묘": (34.8455, 128.4355),
    "통영 삼도수군통제영": (34.8455, 128.4255),
    "송광사": (35.0055, 127.2755),
    "순천왜성": (34.9455, 127.4855),
    "순천향교": (34.9505, 127.4855),
    "면앙정": (35.3155, 126.9955),
    "송강정": (35.3255, 127.0055),
    "해인사 장경판전": (35.8015, 128.0975),
    "옥전고분군": (35.5655, 128.1555),
    "합천 삼가향교": (35.4155, 128.1255),
}

# English name overrides (else romanize)
EN_NAMES: dict[str, str] = {
    "경복궁": "Gyeongbokgung Palace",
    "창덕궁": "Changdeokgung Palace",
    "창경궁": "Changgyeonggung Palace",
    "덕수궁": "Deoksugung Palace",
    "경희궁": "Gyeonghuigung Palace",
    "종묘": "Jongmyo Shrine",
    "북촌한옥마을": "Bukchon Hanok Village",
    "남산골한옥마을": "Namsangol Hanok Village",
    "한양도성": "Hanyangdoseong City Wall",
    "숭례문": "Sungnyemun (Namdaemun)",
    "흥인지문": "Heunginjimun (Dongdaemun Gate)",
    "광화문": "Gwanghwamun",
    "운현궁": "Unhyeongung",
    "서대문형무소역사관": "Seodaemun Prison History Hall",
    "독립문": "Independence Gate",
    "탑골공원": "Tapgol Park",
    "암사동 선사유적지": "Amsa-dong Prehistoric Site",
    "몽촌토성": "Mongchontoseong",
    "풍납토성": "Pungnaptoseong",
    "석촌동 고분군": "Seokchon-dong Tumuli",
    "선릉·정릉": "Seolleung & Jeongneung Royal Tombs",
    "정릉": "Jeongneung Royal Tomb",
    "홍릉·유릉": "Hongneung & Yureung",
    "성균관": "Sungkyunkwan",
    "양화진 외국인선교사묘원": "Yanghwajin Foreign Missionary Cemetery",
    "진관사": "Jingwansa Temple",
    "봉은사": "Bongeunsa Temple",
    "길상사": "Gilsangsa Temple",
    "보신각": "Bosingak Bell Pavilion",
    "서울성곽길": "Seoul City Wall Trail",
    "수원화성": "Suwon Hwaseong Fortress",
    "화성행궁": "Hwaseong Haenggung",
    "남한산성": "Namhansanseong Fortress",
    "광명동굴": "Gwangmyeong Cave",
    "한국민속촌": "Korean Folk Village",
    "파주 임진각": "Imjingak",
    "파주 DMZ": "Paju DMZ Area",
    "용인 호암미술관 전통정원": "Ho-Am Art Museum Traditional Garden",
    "실학박물관": "Silhak Museum",
    "세종대왕릉": "Royal Tomb of King Sejong",
    "신륵사": "Silleuksa Temple",
    "용주사": "Yongjusa Temple",
    "융건릉": "Yungneung & Geolleung",
    "남양주 홍유릉": "Hongyureung Royal Tombs",
    "광릉": "Gwangneung",
    "아차산성": "Achasanseong Fortress",
    "행주산성": "Haengjusanseong Fortress",
    "파주 삼릉": "Paju Samneung",
    "파주 장릉": "Paju Jangneung",
    "강화역사유적지구": "Ganghwa Historic Sites",
    "강화 전등사": "Jeondeungsa Temple",
    "강화 고인돌": "Ganghwa Dolmens",
    "강화 초지진": "Chojijin Fort",
    "강화 광성보": "Gwangseongbo Fort",
    "강화 덕진진": "Deokjinjin Fort",
    "강화 고려궁지": "Ganghwa Goryeo Palace Site",
    "강화 외규장각": "Oegyujanggak",
    "강화 성공회성당": "Ganghwa Anglican Cathedral",
    "인천 개항장 문화지구": "Incheon Open Port Culture District",
    "인천 중구청 구 일본우선주식회사 건물": "Former Nippon Yusen Building (Incheon)",
    "인천 내리교회": "Naeri Church",
    "인천향교": "Incheon Hyanggyo",
    "문학산성": "Munhaksanseong Fortress",
    "계양산성": "Gyeyangsanseong Fortress",
    "송월동 동화마을": "Songwol-dong Fairy Tale Village",
    "범어사": "Beomeosa Temple",
    "해동용궁사": "Haedong Yonggungsa Temple",
    "충렬사": "Chungnyeolsa Shrine",
    "동래읍성": "Dongnae Eupseong",
    "복천동고분군": "Bokcheon-dong Tumuli",
    "부산근대역사관": "Busan Modern History Museum",
    "임시수도기념관": "Provisional Capital Memorial Hall",
    "부산진성": "Busanjinseong Fortress",
    "금정산성": "Geumjeongsanseong Fortress",
    "유엔기념공원": "UN Memorial Cemetery",
    "오륜대 한국순교자박물관": "Oryundae Korean Martyrs Museum",
    "기장 죽성리 왜성": "Jukseong-ri Japanese Fortress",
    "몰운대": "Morundae",
    "부산항 제1부두 근대유산": "Busan Port Pier 1 Modern Heritage",
    "동화사": "Donghwasa Temple",
    "갓바위": "Gatbawi",
    "달성공원": "Dalseong Park",
    "대구읍성 유적": "Daegu Eupseong Remains",
    "계산성당": "Gyesan Cathedral",
    "이상화 고택": "Yi Sang-hwa Historic House",
    "서상돈 고택": "Seo Sang-don Historic House",
    "대구근대역사관": "Daegu Modern History Museum",
    "약령시 한의약박물관": "Yangnyeongsi Oriental Medicine Museum",
    "국채보상운동기념관": "National Debt Redemption Movement Memorial",
    "육신사": "Yukshinsa Shrine",
    "파계사": "Pagyesa Temple",
    "한훤당 고택": "Hanhwondang Historic House",
    "남평문씨본리세거지": "Nampyeong Mun Clan Village",
    "불국사": "Bulguksa Temple",
    "석굴암": "Seokguram Grotto",
    "첨성대": "Cheomseongdae",
    "대릉원": "Daereungwon Tumuli Park",
    "동궁과 월지": "Donggung Palace & Wolji Pond",
    "월정교": "Woljeonggyo Bridge",
    "황룡사지": "Hwangnyongsa Temple Site",
    "분황사": "Bunhwangsa Temple",
    "포석정": "Poseokjeong",
    "경주 교촌마을": "Gyeongju Gyochon Village",
    "최부자댁": "Choi Buja House",
    "국립경주박물관": "Gyeongju National Museum",
    "무열왕릉": "Tomb of King Muyeol",
    "김유신묘": "Tomb of Kim Yu-sin",
    "문무대왕릉": "Underwater Tomb of King Munmu",
    "감은사지": "Gameunsa Temple Site",
    "골굴사": "Golgulsa Temple",
    "남산 불교유적": "Namsan Buddhist Relics (Gyeongju)",
    "계림": "Gyerim Forest",
    "경주 읍성": "Gyeongju Eupseong",
    "하회마을": "Hahoe Folk Village",
    "도산서원": "Dosan Seowon",
    "병산서원": "Byeongsan Seowon",
    "봉정사": "Bongjeongsa Temple",
    "월영교": "Woryeonggyo Bridge",
    "안동민속촌": "Andong Folk Village",
    "임청각": "Imcheonggak",
    "월영교 주변 전통문화유적": "Woryeonggyo Heritage Area",
    "안동향교": "Andong Hyanggyo",
    "제비원 석불": "Jebiwon Stone Buddha",
    "봉황사": "Bonghwangsa Temple",
    "예안향교": "Yean Hyanggyo",
    "전주한옥마을": "Jeonju Hanok Village",
    "경기전": "Gyeonggijeon Shrine",
    "전동성당": "Jeondong Cathedral",
    "풍남문": "Pungnammun Gate",
    "전주향교": "Jeonju Hyanggyo",
    "오목대": "Omokdae",
    "이목대": "Imokdae",
    "조경단": "Jogyeongdan",
    "남고산성": "Namgosanseong Fortress",
    "한벽당": "Hanbyeokdang",
    "전주 객사": "Jeonju Gaeksa",
    "공산성": "Gongsanseong Fortress",
    "무령왕릉과 왕릉원": "Royal Tomb of King Muryeong",
    "국립공주박물관": "Gongju National Museum",
    "공주 마곡사": "Magoksa Temple",
    "마곡사": "Magoksa Temple",
    "공주향교": "Gongju Hyanggyo",
    "공주 충청감영": "Chungcheong Gamyeong Site",
    "공주 제민천 역사문화거리": "Jemincheon Historic Street",
    "송산리 고분군": "Songsan-ri Tumuli",
    "부소산성": "Busosanseong Fortress",
    "관북리유적": "Gwanbuk-ri Historic Site",
    "정림사지": "Jeongnimsaji Temple Site",
    "궁남지": "Gungnamji Pond",
    "능산리 고분군": "Neungsan-ri Tumuli",
    "백제문화단지": "Baekje Cultural Land",
    "국립부여박물관": "Buyeo National Museum",
    "부여 나성": "Buyeo Naseong Wall",
    "무량사": "Muryangsa Temple",
    "성흥산성": "Seongheungsanseong Fortress",
    "오죽헌": "Ojukheon",
    "선교장": "Seongyojang",
    "경포대": "Gyeongpodae Pavilion",
    "강릉향교": "Gangneung Hyanggyo",
    "낙산사": "Naksansa Temple",
    "월정사": "Woljeongsa Temple",
    "상원사": "Sangwonsa Temple",
    "신흥사": "Sinheungsa Temple",
    "고성 왕곡마을": "Wanggok Village",
    "강릉대도호부 관아": "Gangneung Daedohobu Office",
    "죽서루": "Jukseoru Pavilion",
    "청평사": "Cheongpyeongsa Temple",
    "홍천 수타사": "Sutasa Temple",
    "법주사": "Beopjusa Temple",
    "청남대": "Cheongnamdae",
    "상당산성": "Sangdangsanseong Fortress",
    "충주 탄금대": "Tangeumdae",
    "충주 탑평리 칠층석탑": "Tappyeong-ri Seven-story Pagoda",
    "단양 온달관광지": "Ondal Tourist Site",
    "단양 적성": "Danyang Jeokseong",
    "청풍문화재단지": "Cheongpung Cultural Heritage Complex",
    "보은 삼년산성": "Samnyeonsanseong Fortress",
    "괴산 화양구곡": "Hwayanggu Valley",
    "영동 영국사": "Yeongguksa Temple",
    "진천 농다리": "Nongdari Bridge",
    "해미읍성": "Haemi Eupseong",
    "현충사": "Hyeonchungsa Shrine",
    "외암민속마을": "Oeam Folk Village",
    "독립기념관": "Independence Hall of Korea",
    "돈암서원": "Donamseowon",
    "논산 관촉사": "Gwanchoksa Temple",
    "논산 돈암서원": "Donamseowon (Nonsan)",
    "서산 개심사": "Gaesimsa Temple",
    "익산 미륵사지": "Mireuksaji Temple Site",
    "익산 왕궁리유적": "Wanggung-ri Historic Site",
    "고창 고인돌유적": "Gochang Dolmen Sites",
    "고창읍성": "Gochang Eupseong",
    "무주 적상산성": "Jeoksangsanseong Fortress",
    "남원 광한루원": "Gwanghalluwon Garden",
    "남원 만복사지": "Manboksa Temple Site",
    "순창 강천사": "Gangcheonsa Temple",
    "김제 금산사": "Geumsansa Temple",
    "부안 내소사": "Naesosa Temple",
    "임실 사선대": "Sasandae",
    "정읍 무성서원": "Museongseowon",
    "순천 낙안읍성": "Naganeupseong Fortress Village",
    "낙안읍성": "Naganeupseong Fortress Village",
    "순천 선암사": "Seonamsa Temple",
    "선암사": "Seonamsa Temple",
    "구례 화엄사": "Hwaeomsa Temple",
    "구례 운조루": "Unjoru House",
    "담양 소쇄원": "Soswaewon Garden",
    "소쇄원": "Soswaewon Garden",
    "담양 식영정": "Sigyeongjeong Pavilion",
    "식영정": "Sigyeongjeong Pavilion",
    "담양 명옥헌": "Myeongokheon Garden",
    "명옥헌": "Myeongokheon Garden",
    "해남 대흥사": "Daeheungsa Temple",
    "장성 필암서원": "Pilamseowon",
    "보성 대원사": "Daewonsa Temple",
    "강진 무위사": "Muwisa Temple",
    "강진 다산초당": "Dasanchodang",
    "영암 도갑사": "Dogapsa Temple",
    "여수 진남관": "Jinnamgwan",
    "여수 흥국사": "Heungguksa Temple",
    "여수 충민사": "Chungminsa Shrine",
    "목포 근대역사문화공간": "Mokpo Modern History Culture Space",
    "국립아시아문화전당": "Asia Culture Center",
    "광주향교": "Gwangju Hyanggyo",
    "포충사": "Pochungsa Shrine",
    "충장사": "Chungjangsa Shrine",
    "무등산 증심사": "Jeungsimsa Temple",
    "월봉서원": "Wolbongseowon",
    "환벽당": "Hwanbyeokdang",
    "취가정": "Chwigajeong",
    "광주 5·18 민주화운동 관련 사적": "May 18 Democratization Movement Sites",
    "해인사": "Haeinsa Temple",
    "통도사": "Tongdosa Temple",
    "쌍계사": "Ssanggyesa Temple",
    "진주성": "Jinju Fortress",
    "촉석루": "Chokseongnu Pavilion",
    "남해 금산 보리암": "Boriam Hermitage (Geumsan)",
    "통영 세병관": "Sebyeonggwan",
    "세병관": "Sebyeonggwan",
    "통영 충렬사": "Tongyeong Chungnyeolsa",
    "합천 황매산성": "Hwangmaesanseong Fortress",
    "함양 남계서원": "Namgyeseowon",
    "산청 목면시배유지": "Cotton Cultivation Historic Site",
    "고성 송학동고분군": "Songhak-dong Tumuli",
    "창녕 교동·송현동 고분군": "Gyodong & Songhyeon-dong Tumuli",
    "반구대 암각화": "Bangudae Petroglyphs",
    "천전리 각석": "Cheonjeon-ri Petroglyphs",
    "울산왜성": "Ulsan Japanese Fortress",
    "언양읍성": "Eonyang Eupseong",
    "석남사": "Seongnamsa Temple",
    "대곡박물관": "Daegok Museum",
    "처용암": "Cheoyongam Rock",
    "울산향교": "Ulsan Hyanggyo",
    "제주목 관아": "Jeju Mokgwana",
    "관덕정": "Gwandeokjeong Pavilion",
    "삼성혈": "Samseonghyeol",
    "항파두리 항몽유적지": "Hangpaduri Anti-Mongol Historic Site",
    "성읍민속마을": "Seongeup Folk Village",
    "대정성지": "Daejeongseong Fortress Site",
    "제주 4·3 관련 유적": "Jeju April 3 Historic Sites",
    "제주 돌문화공원": "Jeju Stone Culture Park",
    "방사탑": "Bangsatap Stone Towers",
    "알뜨르비행장": "Altreu Airfield",
    "계족산성": "Gyejoksanseong Fortress",
    "우암사적공원": "Uam Historic Park",
    "동춘당": "Dongchundang",
    "회덕향교": "Hoedeok Hyanggyo",
    "남간정사": "Namganjeongsa",
    "대전근현대사전시관": "Daejeon Modern History Exhibition Hall",
    "비암사": "Biamsa Temple",
    "세종대왕 영릉 관련 역사문화권": "King Sejong Yeongneung Heritage Area",
    "김종서 장군 묘": "Tomb of General Kim Jong-seo",
    "독락정": "Dongnakjeong Pavilion",
    "연기향교": "Yeongi Hyanggyo",
    "보경사": "Bogyeongsa Temple",
    "장기읍성": "Janggi Eupseong",
    "장기향교": "Janggi Hyanggyo",
    "오어사": "Oeosa Temple",
    "흥해향교": "Heunghae Hyanggyo",
    "부석사": "Buseoksa Temple",
    "소수서원": "Sosu Seowon",
    "선비촌": "Seonbichon Village",
    "무섬마을": "Museom Village",
    "영주 근대역사문화거리": "Yeongju Modern History Culture Street",
    "통영성지": "Tongyeong Fortress Site",
    "착량묘": "Changnyangmyo Shrine",
    "통영 삼도수군통제영": "Tongyeong Naval Command Site",
    "송광사": "Songgwangsa Temple",
    "순천왜성": "Suncheon Japanese Fortress",
    "순천향교": "Suncheon Hyanggyo",
    "면앙정": "Myeonangjeong Pavilion",
    "송강정": "Songgangjeong Pavilion",
    "해인사 장경판전": "Haeinsa Janggyeong Panjeon",
    "옥전고분군": "Okjeon Tumuli",
    "합천 삼가향교": "Samga Hyanggyo",
    "공주 공산성": "Gongsanseong Fortress",
    "공주 무령왕릉": "Royal Tomb of King Muryeong",
    "부여 부소산성": "Busosanseong Fortress",
    "부여 정림사지": "Jeongnimsaji Temple Site",
    "부여 궁남지": "Gungnamji Pond",
}

# Revised Romanization (basic) for slug + fallback English
_CHO = [
    "g", "kk", "n", "d", "tt", "r", "m", "b", "pp", "s", "ss", "", "j", "jj", "ch", "k", "t", "p", "h",
]
_JUNG = [
    "a", "ae", "ya", "yae", "eo", "e", "yeo", "ye", "o", "wa", "wae", "oe", "yo", "u", "wo", "we", "wi", "yu", "eu", "ui", "i",
]
_JONG = [
    "",  # 0
    "k",
    "k",
    "k",  # 1-3
    "n",
    "n",
    "n",  # 4-6
    "t",  # 7
    "l",  # 8
    "k",
    "m",
    "l",
    "l",
    "l",
    "l",
    "l",  # 9-15
    "m",  # 16
    "p",
    "p",  # 17-18
    "t",
    "t",  # 19-20
    "ng",  # 21
    "t",
    "t",
    "k",
    "t",
    "p",
    "t",  # 22-27
]


def romanize_syllable(ch: str) -> str:
    code = ord(ch)
    if not (0xAC00 <= code <= 0xD7A3):
        return ch
    s = code - 0xAC00
    cho, jung, jong = s // 588, (s % 588) // 28, s % 28
    return _CHO[cho] + _JUNG[jung] + _JONG[jong]


def romanize(text: str) -> str:
    out = []
    for ch in text:
        if "가" <= ch <= "힣":
            out.append(romanize_syllable(ch))
        elif ch.isalnum():
            out.append(ch.lower())
        elif ch in ("·", "・", "/", "&"):
            out.append("-")
        elif ch.isspace() or ch in "-_":
            out.append("-")
        # drop punctuation
    s = "".join(out)
    s = re.sub(r"-+", "-", s).strip("-").lower()
    return s


def compact(name: str) -> str:
    n = unicodedata.normalize("NFKC", name)
    n = n.replace("·", "").replace("・", "").replace(" ", "").replace("-", "")
    return n.lower()


# City/region prefixes used in list names (for cross-section dedup)
_PREFIXES = sorted(
    {
        "서울",
        "파주",
        "용인",
        "남양주",
        "강화",
        "인천",
        "기장",
        "부산",
        "대구",
        "경주",
        "안동",
        "전주",
        "공주",
        "부여",
        "강릉",
        "고성",
        "홍천",
        "충주",
        "단양",
        "보은",
        "괴산",
        "영동",
        "진천",
        "논산",
        "서산",
        "익산",
        "고창",
        "무주",
        "남원",
        "순창",
        "김제",
        "부안",
        "임실",
        "정읍",
        "순천",
        "구례",
        "담양",
        "해남",
        "장성",
        "보성",
        "강진",
        "영암",
        "여수",
        "목포",
        "광주",
        "남해",
        "통영",
        "합천",
        "함양",
        "산청",
        "창녕",
        "울산",
        "제주",
        "대전",
        "세종",
        "포항",
        "영주",
        "장기",
        "흥해",
        "무등산",
    },
    key=len,
    reverse=True,
)


def bare_key(name: str) -> str:
    c = compact(name)
    for p in _PREFIXES:
        pc = compact(p)
        if c.startswith(pc) and len(c) > len(pc):
            return c[len(pc) :]
    return c


_PREFIX_COMPACT = {compact(p) for p in _PREFIXES}

# Sections that are the same metro region family (province vs city listing)
_SECTION_FAMILY = {
    "서울": "seoul",
    "경기": "gyeonggi",
    "인천": "incheon",
    "부산": "busan",
    "대구": "daegu",
    "경주": "gyeongju",
    "안동": "gyeongsang",
    "전주": "jeolla-n",
    "공주": "chungnam",
    "부여": "chungnam",
    "강원": "gangwon",
    "충북": "chungbuk",
    "충남": "chungnam",
    "전북": "jeolla-n",
    "전남": "jeolla-s",
    "광주": "jeolla-s",
    "경남": "gyeongsang-s",
    "울산": "ulsan",
    "제주": "jeju",
    "대전": "daejeon",
    "세종": "sejong",
    "포항": "gyeongsang-n",
    "영주": "gyeongsang-n",
    "통영": "gyeongsang-s",
    "순천": "jeolla-s",
    "담양": "jeolla-s",
    "합천": "gyeongsang-s",
}


def same_site(a_name: str, a_section: str, b_name: str, b_section: str) -> bool:
    """True when the same heritage site is listed twice (e.g. 공산성 / 공주 공산성)."""
    ca, cb = compact(a_name), compact(b_name)
    fa, fb = _SECTION_FAMILY.get(a_section), _SECTION_FAMILY.get(b_section)
    if ca == cb:
        # Identical label: only merge if same region family (충남/공주),
        # not Busan 충렬사 vs Tongyeong 충렬사.
        return fa == fb
    # Prefixed form: "공주공산성" vs "공산성" — only if families compatible
    # or the bare listing's section is the city prefix.
    if ca.endswith(cb) and len(ca) > len(cb):
        prefix = ca[: -len(cb)]
        if prefix in _PREFIX_COMPACT:
            if fa and fb and fa == fb:
                return True
            # bare name listed under the city that appears as prefix
            if b_section and compact(b_section) == prefix:
                return True
            if a_section and compact(a_section) == prefix:
                return True
            return False
    if cb.endswith(ca) and len(cb) > len(ca):
        prefix = cb[: -len(ca)]
        if prefix in _PREFIX_COMPACT:
            if fa and fb and fa == fb:
                return True
            if a_section and compact(a_section) == prefix:
                return True
            if b_section and compact(b_section) == prefix:
                return True
            return False
    # Near aliases (same site, different wording)
    alias_groups = [
        frozenset({"무령왕릉과왕릉원", "무령왕릉", "공주무령왕릉"}),
        frozenset({"월영교주변전통문화유적", "월영교"}),
        frozenset({"해인사장경판전", "해인사"}),
    ]

    def alias_group(name: str):
        c, b = compact(name), bare_key(name)
        for g in alias_groups:
            if c in g or b in g:
                return g
        return None

    ga, gb = alias_group(a_name), alias_group(b_name)
    if ga and ga == gb and (not fa or not fb or fa == fb):
        return True
    return False


# Generic stems that must NOT alone prove two places are the same
_GENERIC_STEMS = {
    "향교",
    "읍성",
    "왜성",
    "산성",
    "고분군",
    "근대역사관",
    "박물관",
    "서원",
    "충렬사",
    "성당",
    "사찰",
    "사지",
    "고택",
    "마을",
    "공원",
    "유적",
    "유적지",
    "사적",
}


def is_already_present(name: str, section: str, existing: list[tuple[str, str]]) -> bool:
    if any(compact(name) == compact(a) for a in EXISTING_ALIASES):
        return True

    region_to_family = {
        "seoul": "seoul",
        "gyeonggi": "gyeonggi",
        "incheon": "incheon",
        "busan": "busan",
        "": "daegu",
        "gyeongju": "gyeongju",
        "gyeongsang": "gyeongsang-s",
        "jeolla": "jeolla-n",
        "chungcheong": "chungnam",
        "gangwon": "gangwon",
        "jeju": "jeju",
    }
    fam = _SECTION_FAMILY.get(section, "")
    for ename, eregion in existing:
        efam = region_to_family.get(eregion, eregion or "")
        ca, cb = compact(name), compact(ename)
        if ca == cb:
            if fam and efam and fam != efam:
                continue
            return True
        # Prefixed duplicate of an already-added place
        if ca.endswith(cb) and ca[: -len(cb)] in _PREFIX_COMPACT:
            if not fam or not efam or fam == efam:
                return True
            continue
        if cb.endswith(ca) and cb[: -len(ca)] in _PREFIX_COMPACT:
            if not fam or not efam or fam == efam:
                return True
            continue
        # Bare-key match only when stem is distinctive (not 향교/읍성/…)
        ba, bb = bare_key(name), bare_key(ename)
        if ba == bb and ba not in _GENERIC_STEMS and len(ba) >= 3:
            if fam and efam and fam != efam:
                continue
            return True
    return False


def parse_source(path: Path) -> list[tuple[str, str]]:
    text = path.read_text(encoding="utf-8")
    # Flag emoji is two regional-indicator codepoints; also accept 🏯
    header_re = re.compile(
        r"^(?:\U0001F1F0\U0001F1F7|🏯)\s*(.+)$"
    )
    section = None
    items: list[tuple[str, str]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = header_re.match(line)
        if m:
            section = m.group(1).strip()
            continue
        if section:
            items.append((section, line))
    return items


def unique_places(items: list[tuple[str, str]]) -> tuple[list[dict], list[dict]]:
    """Return (unique list, skipped dups). Prefer first (more specific) section."""
    unique: list[dict] = []
    dups: list[dict] = []
    for section, name in items:
        region = SECTION_REGION.get(section, "gyeongsang")
        entry = {"section": section, "name": name, "region": region}
        hit = None
        for prev in unique:
            if same_site(name, section, prev["name"], prev["section"]):
                hit = prev
                break
        if hit:
            dups.append({**entry, "dup_of": hit["name"], "dup_section": hit["section"]})
            continue
        unique.append(entry)
    return unique, dups


def load_existing() -> tuple[set[str], list[tuple[str, str]]]:
    """slugs + list of (name, region/section hint) already in guidebook."""
    slugs: set[str] = set()
    existing: list[tuple[str, str]] = []
    text = COORDS.read_text(encoding="utf-8")
    for m in re.finditer(r'slug:\s*"([^"]+)"', text):
        slugs.add(m.group(1))
    ko_path = ROOT / "i18n" / "pages" / "transport" / "ko.json"
    data = json.loads(ko_path.read_text(encoding="utf-8"))
    places = data.get("places", {})
    for slug, p in places.items():
        slugs.add(slug)
        n = p.get("name") or ""
        region = p.get("region") or ""
        if n:
            existing.append((n, region))
    for alias, _slug in EXISTING_ALIASES.items():
        existing.append((alias, ""))
    return slugs, existing


def make_slug(name: str, section: str, used: set[str]) -> str:
    base = romanize(name)
    if not base:
        base = "heritage"
    # Disambiguate identical bare names across cities (e.g. 충렬사)
    if compact(name) == bare_key(name):
        # bare name — include section when slug already taken
        pass
    if len(base) > 48:
        base = base[:48].rstrip("-")
    slug = base
    if slug in used:
        sec = romanize(section) or "kr"
        slug = f"{sec}-{base}"
        if len(slug) > 56:
            slug = slug[:56].rstrip("-")
    i = 2
    orig = slug
    while slug in used:
        slug = f"{orig}-{i}"
        i += 1
    used.add(slug)
    return slug


def coords_for(name: str, region: str, index: int, section: str = "") -> tuple[float, float]:
    # Prefer "통영 충렬사"-style keys when section + name is known
    if section:
        prefixed = f"{section} {name}"
        if prefixed in KNOWN_COORDS:
            return KNOWN_COORDS[prefixed]
    if name in KNOWN_COORDS:
        # Ambiguous bare names that exist in multiple cities
        if compact(name) in {"충렬사"} and section and section not in ("부산",):
            # fall through to section/region center unless prefixed key exists
            pass
        else:
            return KNOWN_COORDS[name]
    c = compact(name)
    for kn, xy in KNOWN_COORDS.items():
        if compact(kn) == c:
            if compact(name) in {"충렬사"} and section not in ("부산",) and not kn.startswith(section):
                continue
            return xy
    b = bare_key(name)
    for kn, xy in KNOWN_COORDS.items():
        knc = compact(kn)
        if knc == c:
            return xy
        if bare_key(kn) == b and knc.endswith(b) and knc != b:
            return xy
        if bare_key(kn) == b and c.endswith(bare_key(kn)) and c != bare_key(kn):
            return xy
    # Section city centers for disambiguation
    section_centers = {
        "통영": (34.8455, 128.4255),
        "부산": (35.1796, 129.0756),
        "순천": (34.9505, 127.4875),
        "담양": (35.3215, 126.9885),
        "합천": (35.5665, 128.1655),
        "영주": (36.8055, 128.6255),
        "포항": (36.0195, 129.3435),
        "공주": (36.4505, 127.1255),
        "부여": (36.2755, 126.9105),
        "안동": (36.5685, 128.7255),
        "전주": (35.8150, 127.1530),
        "경주": (35.8562, 129.2247),
        "대전": (36.3505, 127.3845),
        "세종": (36.4805, 127.2895),
        "울산": (35.5384, 129.3114),
        "광주": (35.1595, 126.8525),
        "제주": (33.4996, 126.5312),
    }
    if section in section_centers:
        lat, lng = section_centers[section]
    else:
        lat, lng = REGION_CENTER.get(region, (36.5, 127.5))
    off = ((index % 17) - 8) * 0.008
    off2 = ((index % 13) - 6) * 0.009
    return round(lat + off, 4), round(lng + off2, 4)


def en_name(name: str) -> str:
    if name in EN_NAMES:
        return EN_NAMES[name]
    for kn, en in EN_NAMES.items():
        if bare_key(kn) == bare_key(name) or compact(kn) == compact(name):
            return en
    # Title-case romanization
    rom = romanize(name).replace("-", " ").strip()
    return rom.title() if rom else name


def maps_urls(q: str, hl: str) -> tuple[str, str]:
    enc = quote(q)
    return (
        f"https://www.google.com/maps/search/?api=1&query={enc}",
        f"https://maps.google.com/maps?q={enc}&hl={hl}&z=15&output=embed",
    )


def build_entry(place: dict, slug: str, lat: float, lng: float) -> dict:
    name = place["name"]
    region = place["region"]
    en = en_name(name)
    rl = REGION_LABELS.get(region, REGION_LABELS[""])
    ko_desc = f"{name}은(는) 한국 대표 문화유산·역사 명소입니다. 유적·건축·전통 풍경을 가까이에서 볼 수 있습니다."
    en_desc = f"{en} is a notable Korean heritage site — historic architecture, relics, and cultural scenery."
    ko_how = f"지역 내 버스·택시 또는 내비게이션으로 '{name}'을(를) 검색해 이동하세요."
    en_how = f"Go by local bus/taxi, or search “{en}” / “{name}” in a maps app."
    ko_addr = f"{rl['ko']} {name}"
    en_addr = f"{en}, {rl['en']}"
    return {
        "slug": slug,
        "lat": lat,
        "lng": lng,
        "region": region,
        "maps_q": name,
        "ko": {
            "name": name,
            "desc": ko_desc,
            "how": ko_how,
            "address": ko_addr,
            "regionLabel": rl["ko"],
        },
        "en": {
            "name": en,
            "desc": en_desc,
            "how": en_how,
            "address": en_addr,
            "regionLabel": rl["en"],
        },
    }


def entry_for_lang(lang: str, item: dict) -> dict:
    ko, en = item["ko"], item["en"]
    slug = item["slug"]
    region = item["region"]
    rl = REGION_LABELS.get(region, REGION_LABELS[""])
    hl = {"zh-Hant": "zh-TW", "zh": "zh-CN"}.get(lang, lang if lang != "ko" else "ko")
    maps, embed = maps_urls(item["maps_q"], hl if lang != "en" else "en")
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
        maps, embed = maps_urls(item["maps_q"], "en")
    else:
        # copy en for vi/th/ru; copy en name + en desc for ja/zh (acceptable fallback)
        name = en["name"] if lang in ("vi", "th", "ru", "ja") else en["name"]
        if lang == "zh":
            name = en["name"]
        if lang == "zh-Hant":
            name = en["name"]
        desc = en["desc"]
        how = en["how"]
        address = en["address"] if lang in ("vi", "th", "ru") else ko["address"]
        region_label = rl.get(lang) or rl["en"]
    body = {
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
        "body": [body],
    }


def patch_coords(items: list[dict]) -> int:
    text = COORDS.read_text(encoding="utf-8")
    lines = []
    for m in items:
        note = m["en"]["name"].replace('"', "'")
        lines.append(
            "  { "
            f'slug: "{m["slug"]}", lat: {m["lat"]}, lng: {m["lng"]}, '
            f'region: "{m["region"]}", type: "heritage", '
            f'note: "{note}", image: "Images/places/{m["slug"]}.jpg" '
            "},"
        )
    insert = "\n".join(lines) + "\n"
    idx = text.rfind("];")
    if idx < 0:
        raise SystemExit("places-coords.js: cannot find ];")
    COORDS.write_text(text[:idx] + insert + text[idx:], encoding="utf-8", newline="\n")
    return len(items)


def ensure_images(items: list[dict]) -> None:
    IMG.mkdir(parents=True, exist_ok=True)
    if not TYPE_FALLBACK.exists():
        print(f"WARN: missing type fallback {TYPE_FALLBACK}")
        return
    for m in items:
        dest = IMG / f"{m['slug']}.jpg"
        if dest.exists() and dest.stat().st_size > 2000:
            continue
        shutil.copy2(TYPE_FALLBACK, dest)


def main() -> int:
    from lib import i18n_store  # noqa: WPS433

    if not SOURCE.exists():
        raise SystemExit(f"source missing: {SOURCE}")

    raw = parse_source(SOURCE)
    unique, list_dups = unique_places(raw)
    existing_slugs, existing_places = load_existing()

    skipped_existing: list[str] = []
    skipped_filter: list[str] = []
    to_add: list[dict] = []
    failures: list[str] = []

    used_slugs = set(existing_slugs)
    skip_compact = {compact(x) for x in SKIP_NAMES}

    for i, place in enumerate(unique):
        name = place["name"]
        if name in SKIP_NAMES or compact(name) in skip_compact or bare_key(name) in skip_compact:
            skipped_filter.append(name)
            continue
        if is_already_present(name, place["section"], existing_places):
            skipped_existing.append(name)
            continue
        try:
            slug = make_slug(name, place["section"], used_slugs)
            lat, lng = coords_for(name, place["region"], i, place["section"])
            entry = build_entry(place, slug, lat, lng)
            to_add.append(entry)
            # so later list items can detect newly added within same run
            existing_places.append((name, place["region"]))
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{name}: {exc}")

    print(f"raw_parsed={len(raw)}")
    print(f"unique={len(unique)}")
    print(f"list_internal_dups={len(list_dups)}")
    print(f"skipped_existing={len(skipped_existing)}")
    print(f"skipped_non_heritage={len(skipped_filter)}")
    print(f"to_add={len(to_add)}")
    print(f"failures={len(failures)}")
    for f in failures[:20]:
        print("FAIL", f)
    for n in skipped_existing[:30]:
        print("SKIP_EXIST", n)
    for n in skipped_filter:
        print("SKIP_FILTER", n)
    for d in list_dups:
        print("SKIP_DUP", d["section"], d["name"], "<-", d["dup_section"], d["dup_of"])

    if not to_add:
        print("nothing to add")
        return 0

    n = patch_coords(to_add)
    print(f"coords_appended={n}")

    bundle = i18n_store.load_all()
    for lang in i18n_store.LANGS:
        places = bundle[lang].setdefault("places", {})
        for item in to_add:
            places[item["slug"]] = entry_for_lang(lang, item)
        print(f"i18n {lang}: +{len(to_add)}")
    i18n_store.save_all(bundle)

    ensure_images(to_add)
    print(i18n_store.build_bundle())

    # summary file for parent agent
    summary = {
        "raw_parsed": len(raw),
        "unique": len(unique),
        "added": len(to_add),
        "skipped_existing": len(skipped_existing),
        "skipped_list_dups": len(list_dups),
        "skipped_non_heritage": len(skipped_filter),
        "failures": failures,
        "added_slugs": [m["slug"] for m in to_add],
        "skipped_existing_names": skipped_existing,
        "skipped_filter_names": skipped_filter,
        "list_dups": [
            {"name": d["name"], "section": d["section"], "dup_of": d["dup_of"]}
            for d in list_dups
        ],
    }
    out = ROOT / "tool" / "_heritage_add_summary.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"summary_written={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
