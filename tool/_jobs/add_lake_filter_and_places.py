# -*- coding: utf-8 -*-
"""Add lake place type + lakes + two national arboretums; reclassify lake natures."""
from __future__ import annotations

import os
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
COORDS = ROOT / "data" / "places" / "places-coords.js"
IMG = ROOT / "Images" / "places"
TYPE_FALLBACK_NATURE = IMG / "_types" / "nature.jpg"
TYPE_FALLBACK_LAKE = IMG / "_types" / "lake.jpg"

LAKE_SVG_PATH = (
    "M3 14c1.5-3 4-5 9-5s7.5 2 9 5c-1.2 2.8-4.2 4.5-9 4.5S4.2 16.8 3 14zm2.2-.2"
    "c.9 1.6 3.2 2.7 6.8 2.7s5.9-1.1 6.8-2.7C17.8 12.3 15.4 11 12 11s-5.8 1.3-6.8 2.8z"
    "M8.5 9.2c.4-1.2 1.6-2.2 3.5-2.2s3.1 1 3.5 2.2H8.5z"
)
LAKE_COLOR = "#2f7eb8"

REGION_LABELS = {
    "seoul": {"ko": "서울", "en": "Seoul", "ja": "ソウル", "zh": "首尔", "zh-Hant": "首爾", "vi": "Seoul", "th": "โซล", "ru": "Сеул"},
    "gyeonggi": {"ko": "경기", "en": "Gyeonggi", "ja": "京畿", "zh": "京畿", "zh-Hant": "京畿", "vi": "Gyeonggi", "th": "คยองกี", "ru": "Кёнги"},
    "gangwon": {"ko": "강원", "en": "Gangwon", "ja": "江原", "zh": "江原", "zh-Hant": "江原", "vi": "Gangwon", "th": "คังวอน", "ru": "Канвон"},
    "chungbuk": {"ko": "충북", "en": "Chungbuk", "ja": "忠北", "zh": "忠北", "zh-Hant": "忠北", "vi": "Chungbuk", "th": "ชุงบุก", "ru": "Чхунбук"},
    "chungnam": {"ko": "충남", "en": "Chungnam", "ja": "忠南", "zh": "忠南", "zh-Hant": "忠南", "vi": "Chungnam", "th": "ชุงนัม", "ru": "Чхуннам"},
    "chungcheong": {"ko": "충청", "en": "Chungcheong", "ja": "忠清", "zh": "忠清", "zh-Hant": "忠清", "vi": "Chungcheong", "th": "ชุงชอง", "ru": "Чхунчхон"},
    "jeolla": {"ko": "전라", "en": "Jeolla", "ja": "全羅", "zh": "全罗", "zh-Hant": "全羅", "vi": "Jeolla", "th": "ชอลลา", "ru": "Чолла"},
    "gyeongsang": {"ko": "경상", "en": "Gyeongsang", "ja": "慶尚", "zh": "庆尚", "zh-Hant": "慶尚", "vi": "Gyeongsang", "th": "คยองซัง", "ru": "Кёнсан"},
    "jeju": {"ko": "제주", "en": "Jeju", "ja": "済州", "zh": "济州", "zh-Hant": "濟州", "vi": "Jeju", "th": "เชจู", "ru": "Чеджу"},
    "": {"ko": "대구", "en": "Daegu", "ja": "大邱", "zh": "大邱", "zh-Hant": "大邱", "vi": "Daegu", "th": "แทกู", "ru": "Тэгу"},
    "sejong": {"ko": "세종", "en": "Sejong", "ja": "世宗", "zh": "世宗", "zh-Hant": "世宗", "vi": "Sejong", "th": "เซจง", "ru": "Седжон"},
}

RECLASSIFY_TO_LAKE = ("goyang", "suseong-mot", "suncheon-bay")


def place(
    slug: str,
    lat: float,
    lng: float,
    region: str,
    typ: str,
    maps_q: str,
    ko: dict,
    en: dict,
    ja: tuple[str, str, str],
    zh: tuple[str, str, str],
    zh_hant: tuple[str, str, str],
) -> dict:
    return {
        "slug": slug,
        "lat": lat,
        "lng": lng,
        "region": region,
        "type": typ,
        "maps_q": maps_q,
        "ko": ko,
        "en": en,
        "ja": ja,
        "zh": zh,
        "zh-Hant": zh_hant,
    }


def lake_entry(
    slug: str,
    lat: float,
    lng: float,
    region: str,
    ko_name: str,
    en_name: str,
    ko_desc: str,
    en_desc: str,
    ko_how: str,
    en_how: str,
    address: str,
    maps_q: str | None = None,
) -> dict:
    return place(
        slug,
        lat,
        lng,
        region,
        "lake",
        maps_q or ko_name,
        {
            "name": ko_name,
            "desc": ko_desc,
            "how": ko_how,
            "address": address,
        },
        {
            "name": en_name,
            "desc": en_desc,
            "how": en_how,
            "address": address,
        },
        (en_name, en_desc, en_how),
        (en_name, en_desc, en_how),
        (en_name, en_desc, en_how),
    )


ARBORETUMS = [
    place(
        "korea-national-arboretum",
        37.7486,
        127.1639,
        "gyeonggi",
        "nature",
        "국립수목원 포천",
        {
            "name": "국립수목원",
            "desc": "포천 광릉숲의 국립수목원. 사계절 정원·전시원과 숲길을 걸으며 식물과 야외를 즐기기 좋습니다.",
            "how": "서울·의정부에서 광릉수목원행 버스, 또는 자가용으로 포천시 소흘읍 광릉수목원로.",
            "address": "경기 포천시 소흘읍 광릉수목원로 415",
        },
        {
            "name": "Korea National Arboretum",
            "desc": "National arboretum in Gwangneung Forest near Pocheon — gardens, trails, and seasonal plant collections.",
            "how": "Bus toward Gwangneung from Seoul/Uijeongbu, or drive to Soheul-eup, Pocheon.",
            "address": "415 Gwangneungsumogwon-ro, Soheul-eup, Pocheon, Gyeonggi",
        },
        ("国立樹木園", "抱川・光陵の森の国立樹木園。庭園と遊歩道が魅力。", "ソウル・議政府から光陵行きバス、または車。"),
        ("国立树木园", "抱川光陵森林的国立树木园，四季庭园与步道。", "首尔·议政府乘光陵方向公交或自驾。"),
        ("國立樹木園", "抱川光陵森林的國立樹木園，四季庭園與步道。", "首爾·議政府乘光陵方向公車或自駕。"),
    ),
    place(
        "sejong-national-arboretum",
        36.4885,
        127.2865,
        "sejong",
        "nature",
        "국립세종수목원",
        {
            "name": "국립세종수목원",
            "desc": "세종시에 있는 국립수목원. 한국·세계 정원과 온실·산책로가 있어 하루 나들이하기 좋은 야외 명소입니다.",
            "how": "세종 BRT·시내버스 수목원 정류장, 또는 자가용 주차.",
            "address": "세종특별자치시 집현동 국립세종수목원",
        },
        {
            "name": "Sejong National Arboretum",
            "desc": "National arboretum in Sejong with Korean and world gardens, greenhouses, and walking paths.",
            "how": "Sejong BRT/city bus to the arboretum stop, or drive and park on-site.",
            "address": "Jiphyeon-dong, Sejong",
        },
        ("国立世宗樹木園", "世宗市の国立樹木園。韓国・世界庭園と温室。", "世宗BRT・市内バス、または車。"),
        ("国立世宗树木园", "世宗市国立树木园，有韩国·世界庭园与温室。", "世宗BRT·市内公交或自驾。"),
        ("國立世宗樹木園", "世宗市國立樹木園，有韓國·世界庭園與溫室。", "世宗BRT·市內公車或自駕。"),
    ),
]

LAKES = [
    lake_entry(
        "seokchon-lake",
        37.5112,
        127.1055,
        "seoul",
        "석촌호수",
        "Seokchon Lake",
        "잠실·송파의 도심 호수. 벚꽃·야경과 산책로로 유명하며 롯데월드타워와 한 코스로 즐기기 좋습니다.",
        "Urban lake in Songpa — cherry blossoms, night views, and walks near Lotte World Tower.",
        "2·8호선 잠실역·석촌역에서 도보.",
        "Walk from Jamsil or Seokchon Station (Lines 2/8).",
        "서울 송파구 잠실동 석촌호수 일대",
    ),
    lake_entry(
        "sanjeong-lake",
        38.0665,
        127.3145,
        "gyeonggi",
        "산정호수",
        "Sanjeong Lake",
        "포천의 대표 호수. 둘레길·카페·명성산 풍경이 어우러진 경기 북부 야외 명소입니다.",
        "Signature Pocheon lake with trails, cafes, and views of Myeongseongsan.",
        "포천시내·동두천에서 버스, 또는 자가용.",
        "Bus from Pocheon/Dongducheon, or drive.",
        "경기 포천시 영북면 산정호수 일대",
    ),
    lake_entry(
        "baegun-lake",
        37.3785,
        126.9855,
        "gyeonggi",
        "백운호수",
        "Baegun Lake",
        "의왕 청계동의 호수공원. 산책·자전거·노을 명소로 수도권 나들이에 인기입니다.",
        "Lake park in Uiwang — walks, bikes, and sunset views near the capital area.",
        "1호선 의왕역에서 버스, 또는 자가용.",
        "Bus from Uiwang Station (Line 1), or drive.",
        "경기 의왕시 청계동 백운호수",
    ),
    lake_entry(
        "wangsong-lake",
        37.3115,
        126.9485,
        "gyeonggi",
        "왕송호수",
        "Wangsong Lake",
        "의왕 왕곡동의 호수·철도공원. 산책로와 레일바이크 분위기로 가족 나들이에 좋습니다.",
        "Uiwang lake and rail park area — easy family walks and leisure paths.",
        "1호선 의왕·당정역에서 버스, 또는 자가용.",
        "Bus from Uiwang/Dangjeong Station, or drive.",
        "경기 의왕시 왕곡동 왕송호수",
    ),
    lake_entry(
        "homyeong-lake",
        37.7485,
        127.4865,
        "gyeonggi",
        "호명호수",
        "Homyeong Lake",
        "가평 호명산 자락의 호수. 산책과 전망이 좋아 당일치기 드라이브 코스로 많이 찾습니다.",
        "Lake below Homyeongsan in Gapyeong — popular for day-trip drives and walks.",
        "가평읍에서 버스·택시, 또는 자가용.",
        "Bus/taxi from Gapyeong-eup, or drive.",
        "경기 가평군 가평읍 호명호수",
    ),
    lake_entry(
        "geumgwang-lake",
        37.0535,
        127.3125,
        "gyeonggi",
        "금광호수",
        "Geumgwang Lake",
        "안성 금광면의 호수. 둘레 산책과 캠핑·피크닉으로 경기 남부 휴양지로 알려져 있습니다.",
        "Lake in Anseong’s Geumgwang area — walking loops, camping, and picnics.",
        "안성 시내에서 버스, 또는 자가용.",
        "Bus from Anseong city, or drive.",
        "경기 안성시 금광면 금광호수",
    ),
    lake_entry(
        "seolbong-lake",
        37.2795,
        127.4265,
        "gyeonggi",
        "설봉호",
        "Seolbong Lake",
        "이천 설봉공원의 호수. 산책로·조각공원·카페와 함께 여유로운 야외 시간을 보내기 좋습니다.",
        "Lake in Icheon’s Seolbong Park — paths, sculpture garden, and cafes.",
        "이천 시내버스·택시, 또는 자가용.",
        "City bus/taxi in Icheon, or drive.",
        "경기 이천시 관고동 설봉공원 설봉호",
    ),
    lake_entry(
        "sihwa-lake",
        37.3025,
        126.6805,
        "gyeonggi",
        "시화호",
        "Sihwa Lake",
        "안산·시흥의 인공 호수. 시화나래·갯골·자전거길로 넓은 수변을 즐길 수 있습니다.",
        "Large artificial lake between Ansan and Siheung — waterfront parks and bike paths.",
        "4호선 안산·오이도 방면에서 버스, 또는 자가용.",
        "Bus from Ansan/Oido (Line 4 area), or drive.",
        "경기 안산시·시흥시 시화호 일대",
    ),
    lake_entry(
        "gyeongpo-lake",
        37.7965,
        128.9075,
        "gangwon",
        "경포호",
        "Gyeongpo Lake",
        "강릉 경포대의 호수. 경포해변과 이어져 호수·바다를 하루에 둘러보기 좋습니다.",
        "Lake by Gyeongpo in Gangneung — pair with the nearby beach for a full day.",
        "강릉역·경포대 버스, 또는 자가용.",
        "Bus from Gangneung Station toward Gyeongpo, or drive.",
        "강원 강릉시 저동 경포호",
    ),
    lake_entry(
        "soyang-lake",
        37.9455,
        127.8145,
        "gangwon",
        "소양호",
        "Soyang Lake",
        "춘천의 대형 댐 호수. 유람선·수변 드라이브와 함께 강원 대표 호수 풍경을 볼 수 있습니다.",
        "Large dam lake in Chuncheon — boat rides and scenic drives.",
        "춘천역에서 버스·택시, 또는 자가용.",
        "Bus/taxi from Chuncheon Station, or drive.",
        "강원 춘천시 신북읍 소양호 일대",
    ),
    lake_entry(
        "yeongnang-lake",
        38.2145,
        128.5775,
        "gangwon",
        "영랑호",
        "Yeongnang Lake",
        "속초 북부의 호수. 둘레길 산책과 일출·갈대 풍경으로 조용한 휴식을 즐기기 좋습니다.",
        "Northern Sokcho lake — quiet shore walks, reeds, and sunrise views.",
        "속초시내 버스·택시, 또는 자가용.",
        "City bus/taxi in Sokcho, or drive.",
        "강원 속초시 영랑동 영랑호",
    ),
    lake_entry(
        "songji-lake",
        38.3355,
        128.5155,
        "gangwon",
        "송지호",
        "Songji Lake",
        "고성의 석호. 송지호해수욕장과 이어져 호수·바다를 함께 볼 수 있는 동해안 명소입니다.",
        "Lagoon in Goseong beside Songjiho Beach — lake and sea in one stop.",
        "속초·고성에서 버스, 또는 자가용.",
        "Bus from Sokcho/Goseong, or drive.",
        "강원 고성군 죽왕면 송지호",
    ),
    lake_entry(
        "hongcheon-palbong-lake",
        37.8455,
        127.8155,
        "gangwon",
        "팔봉산 홍천강·호수권",
        "Palbongsan Hongcheon River & Lake Area",
        "홍천 팔봉산 일대의 강·호수권. 수변 산책과 산행을 함께하기 좋은 강원 중부 휴양지입니다.",
        "River and lake area around Palbongsan in Hongcheon — combine waterfront walks with hiking.",
        "홍천읍에서 버스·택시, 또는 자가용.",
        "Bus/taxi from Hongcheon-eup, or drive.",
        "강원 홍천군 서면 팔봉산·홍천강 일대",
        "홍천 팔봉산",
    ),
    lake_entry(
        "paro-lake",
        38.1075,
        127.7785,
        "gangwon",
        "파로호",
        "Paro Lake",
        "화천의 댐 호수. 평화의 댐·수변 드라이브로 한적한 강원 북부 풍경을 만날 수 있습니다.",
        "Dam lake in Hwacheon — peaceful drives and Peace Dam views.",
        "춘천·화천에서 버스, 또는 자가용.",
        "Bus from Chuncheon/Hwacheon, or drive.",
        "강원 화천군 간동면 파로호",
    ),
    lake_entry(
        "soyang-lake-inje",
        38.0505,
        128.1705,
        "gangwon",
        "소양호 상류권",
        "Soyang Lake Upper Reaches (Inje)",
        "인제 쪽 소양호 상류. 산과 호수가 맞닿은 깊은 수변 풍경이 인상적입니다.",
        "Upper Soyang Lake toward Inje — deep mountain-and-water scenery.",
        "인제·춘천에서 버스, 또는 자가용.",
        "Bus from Inje/Chuncheon, or drive.",
        "강원 인제군 남면·기린면 소양호 상류",
        "인제 소양호",
    ),
    lake_entry(
        "chungju-lake",
        36.9705,
        128.0005,
        "chungbuk",
        "충주호",
        "Chungju Lake",
        "충주의 대형 댐 호수. 유람선·수안보·월악산과 연계해 충북 대표 호수 여행을 할 수 있습니다.",
        "Large dam lake in Chungju — boats and trips linking Suanbo and Woraksan.",
        "충주역에서 버스, 또는 자가용.",
        "Bus from Chungju Station, or drive.",
        "충북 충주시 동량면·종민동 충주호 일대",
    ),
    lake_entry(
        "cheongpung-lake",
        37.0005,
        128.1705,
        "chungbuk",
        "청풍호",
        "Cheongpung Lake",
        "제천 청풍의 호수. 케이블카·유람선과 함께 충북 대표 수변 관광지입니다.",
        "Lake at Cheongpung in Jecheon — cable car and lake cruises.",
        "제천역에서 청풍 방면 버스, 또는 자가용.",
        "Bus from Jecheon toward Cheongpung, or drive.",
        "충북 제천시 청풍면 청풍호",
    ),
    lake_entry(
        "goesan-lake",
        36.7805,
        127.8505,
        "chungbuk",
        "괴산호",
        "Goesan Lake",
        "괴산의 댐 호수. 산막이옛길·수변 산책과 함께하는 충북 중부 휴양지입니다.",
        "Dam lake in Goesan — pair with Sanmakyi Old Road and shore walks.",
        "괴산읍에서 버스·택시, 또는 자가용.",
        "Bus/taxi from Goesan-eup, or drive.",
        "충북 괴산군 칠성면 괴산호",
    ),
    lake_entry(
        "daecheong-lake",
        36.4505,
        127.4805,
        "chungbuk",
        "대청호",
        "Daecheong Lake",
        "청주·대전을 잇는 대형 호수. 수변 전망·드라이브 코스로 충청권 대표 호수입니다.",
        "Large lake between Cheongju and Daejeon — viewpoints and drive routes.",
        "청주·대전에서 버스, 또는 자가용.",
        "Bus from Cheongju/Daejeon, or drive.",
        "충북 청주시·대전 대청호 일대",
    ),
    lake_entry(
        "sapgyo-lake",
        36.8895,
        126.8275,
        "chungnam",
        "삽교호",
        "Sapgyo Lake",
        "당진의 하구 호수. 삽교호관광지·일몰과 함께 충남 서해 수변을 즐기기 좋습니다.",
        "Estuary lake in Dangjin — sunset views and Sapgyo Lake tourist area.",
        "당진·평택에서 버스, 또는 자가용.",
        "Bus from Dangjin/Pyeongtaek, or drive.",
        "충남 당진시 신평면 삽교호",
    ),
    lake_entry(
        "boryeong-lake",
        36.3505,
        126.5505,
        "chungnam",
        "보령호",
        "Boryeong Lake",
        "보령의 댐 호수. 대천해수욕장과 떨어져 한적한 수변·드라이브 코스로 좋습니다.",
        "Dam lake in Boryeong — quieter waterfront away from Daecheon Beach.",
        "보령시내에서 버스, 또는 자가용.",
        "Bus from Boryeong city, or drive.",
        "충남 보령시 미산면 보령호",
    ),
    lake_entry(
        "eunpa-lake-park",
        35.9555,
        126.6875,
        "jeolla",
        "은파호수공원",
        "Eunpa Lake Park",
        "군산의 도심 호수공원. 산책로·분수·야경으로 시민과 여행객이 모이는 야외 명소입니다.",
        "Urban lake park in Gunsan — paths, fountains, and evening lights.",
        "군산시내 버스·택시, 또는 자가용.",
        "City bus/taxi in Gunsan, or drive.",
        "전북 군산시 나운동 은파호수공원",
    ),
    lake_entry(
        "naejang-lake",
        35.4965,
        126.8915,
        "jeolla",
        "내장호",
        "Naejang Lake",
        "정읍 내장산 자락의 호수. 단풍 시즌과 호수 반영이 아름다운 전북 명소입니다.",
        "Lake below Naejangsan in Jeongeup — famous for autumn reflections.",
        "정읍역에서 내장산 방면 버스, 또는 자가용.",
        "Bus from Jeongeup toward Naejangsan, or drive.",
        "전북 정읍시 내장동 내장호",
    ),
    lake_entry(
        "yeongsan-lake",
        34.7705,
        126.4705,
        "jeolla",
        "영산호",
        "Yeongsan Lake",
        "영암의 영산강 하구 호수. 넓은 수변과 갈대·노을 풍경이 인상적입니다.",
        "Yeongsangang estuary lake in Yeongam — wide shores, reeds, and sunsets.",
        "목포·영암에서 버스, 또는 자가용.",
        "Bus from Mokpo/Yeongam, or drive.",
        "전남 영암군 삼호읍 영산호",
    ),
    lake_entry(
        "damyang-lake",
        35.3405,
        126.9805,
        "jeolla",
        "담양호",
        "Damyang Lake",
        "담양의 댐 호수. 메타세쿼이아길·죽녹원과 함께 전남 대표 나들이 코스로 묶기 좋습니다.",
        "Dam lake in Damyang — combine with Metasequoia Road and Jungnogwon.",
        "광주·담양에서 버스, 또는 자가용.",
        "Bus from Gwangju/Damyang, or drive.",
        "전남 담양군 용면 담양호",
    ),
    lake_entry(
        "jangseong-lake",
        35.3505,
        126.7805,
        "jeolla",
        "장성호",
        "Jangseong Lake",
        "장성의 호수. 수변길·출렁다리로 산책하기 좋은 전남 북부 휴양지입니다.",
        "Lake in Jangseong with shore trails and a suspension bridge walk.",
        "광주·장성에서 버스, 또는 자가용.",
        "Bus from Gwangju/Jangseong, or drive.",
        "전남 장성군 북이면 장성호",
    ),
    lake_entry(
        "junam-reservoir",
        35.3105,
        128.6705,
        "gyeongsang",
        "주남저수지",
        "Junam Reservoir",
        "창원의 철새·습지 저수지. 탐조·산책으로 경남 대표 수변 생태 명소입니다.",
        "Bird wetland reservoir in Changwon — top Gyeongnam waterfront for walks and birding.",
        "창원·동읍에서 버스, 또는 자가용.",
        "Bus from Changwon/Dong-eup, or drive.",
        "경남 창원시 의창구 동읍 주남저수지",
    ),
    lake_entry(
        "jinyang-lake",
        35.1705,
        128.0405,
        "gyeongsang",
        "진양호",
        "Jinyang Lake",
        "진주의 댐 호수. 동물원·전망대·수변 공원으로 가족 나들이에 좋습니다.",
        "Dam lake in Jinju with park, viewpoints, and family-friendly grounds.",
        "진주역에서 버스, 또는 자가용.",
        "Bus from Jinju Station, or drive.",
        "경남 진주시 판문동 진양호",
    ),
    lake_entry(
        "andong-lake",
        36.5805,
        128.7705,
        "gyeongsang",
        "안동호",
        "Andong Lake",
        "안동의 대형 댐 호수. 월영교·하회와 연계해 경북 대표 호수 풍경을 볼 수 있습니다.",
        "Large dam lake in Andong — link with Wolyeong Bridge and Hahoe.",
        "안동역에서 버스, 또는 자가용.",
        "Bus from Andong Station, or drive.",
        "경북 안동시 도산면·와룡면 안동호",
    ),
    lake_entry(
        "jusanji",
        36.3705,
        129.1505,
        "gyeongsang",
        "주산지",
        "Jusanji",
        "청송의 작은 저수지. 물에 비친 왕버들과 안개 풍경으로 사진 명소로 유명합니다.",
        "Small reservoir in Cheongsong — misty willow reflections make a famous photo spot.",
        "청송읍에서 버스·택시, 또는 자가용.",
        "Bus/taxi from Cheongsong-eup, or drive.",
        "경북 청송군 부남면 주산지",
    ),
    lake_entry(
        "bomun-lake",
        35.8405,
        129.2805,
        "gyeongsang",
        "보문호",
        "Bomun Lake",
        "경주 보문관광단지의 호수. 산책·자전거·야경으로 유적 여행과 함께하기 좋습니다.",
        "Lake in Gyeongju’s Bomun tourist complex — walks, bikes, and night views.",
        "경주역·보문단지 버스, 또는 자가용.",
        "Bus from Gyeongju Station to Bomun, or drive.",
        "경북 경주시 신평동 보문호",
    ),
    lake_entry(
        "yeongcheon-lake",
        36.0005,
        128.9505,
        "gyeongsang",
        "영천호",
        "Yeongcheon Lake",
        "영천의 댐 호수. 수변 공원과 드라이브로 경북 내륙의 한적한 호수 풍경을 즐길 수 있습니다.",
        "Dam lake in Yeongcheon — quiet inland waterfront parks and drives.",
        "영천역에서 버스, 또는 자가용.",
        "Bus from Yeongcheon Station, or drive.",
        "경북 영천시 자양면 영천호",
    ),
]

ALL_NEW = ARBORETUMS + LAKES


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


def entry_for_lang(lang: str, p: dict) -> dict:
    region = p["region"]
    ko, en = p["ko"], p["en"]
    slug = p["slug"]
    hl = {"zh-Hant": "zh-TW", "zh": "zh-CN"}.get(lang, lang if lang != "ko" else "ko")
    maps, embed = maps_urls(p["maps_q"], hl if lang != "en" else "en")
    img = f"Images/places/{slug}.jpg"
    rl = REGION_LABELS.get(region, REGION_LABELS["chungcheong"])[lang if lang in REGION_LABELS.get(region, REGION_LABELS["chungcheong"]) else "en"]
    rl_map = REGION_LABELS.get(region, REGION_LABELS["chungcheong"])
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
            "mapsUrl": maps_urls(p["maps_q"], "en")[0],
            "mapsEmbedUrl": maps_urls(p["maps_q"], "en")[1],
            "image": img,
        }
    else:
        if lang in ("ja", "zh", "zh-Hant"):
            name, desc, how = p[lang]
        else:
            name, desc, how = en["name"], en["desc"], en["how"]
        base = {
            "name": name,
            "desc": desc,
            "how": how,
            "address": en["address"] if lang in ("vi", "th", "ru") else ko["address"],
            "regionLabel": rl_map.get(lang, rl_map["en"]),
            "region": region,
            "mapsUrl": maps,
            "mapsEmbedUrl": embed,
            "image": img,
        }
    extras = {}
    for L in ("ja", "zh", "zh-Hant", "vi", "th", "ru"):
        if L in ("ja", "zh", "zh-Hant"):
            extras[L] = p[L]
        else:
            extras[L] = (en["name"], en["desc"], en["how"])
    base["body"] = body_block(ko, en, extras)
    return base


def atomic_write(path: Path, text: str) -> None:
    """Write via temp file; on Windows file locks, fall back to in-place write."""
    tmp = path.with_name(path.name + ".tmpwrite")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    try:
        os.replace(str(tmp), str(path))
        return
    except OSError as exc:
        print(f"  atomic replace failed ({exc}); trying direct write")
    try:
        path.write_text(text, encoding="utf-8", newline="\n")
        tmp.unlink(missing_ok=True)
        return
    except OSError as exc:
        tmp.unlink(missing_ok=True)
        raise SystemExit(f"cannot write {path}: {exc}") from exc


def patch_html() -> None:
    p = ROOT / "pages" / "transportation" / "index.html"
    text = p.read_text(encoding="utf-8")
    if 'data-places-type-filter="lake"' in text:
        print("html: lake filter already present")
        return
    insert = """            <li class="places-map-legend__item">
              <label class="places-map-legend__label">
                <input type="checkbox" class="places-map-legend__check" data-places-type-filter="lake" checked>
                <span class="places-map-legend__swatch places-map-legend__swatch--lake" aria-hidden="true"></span>
                <span data-i18n="transport.legendLake">호수</span>
              </label>
            </li>
"""
    needle = """            <li class="places-map-legend__item">
              <label class="places-map-legend__label">
                <input type="checkbox" class="places-map-legend__check" data-places-type-filter="beach" checked>"""
    if needle not in text:
        raise SystemExit("html: beach filter block not found")
    text = text.replace(needle, insert + needle, 1)
    try:
        atomic_write(p, text)
        print("patched index.html")
    except SystemExit as exc:
        alt = p.with_name("index.html.new")
        alt.write_text(text, encoding="utf-8", newline="\n")
        print(f"WARN: could not write index.html ({exc}); wrote {alt.name} instead")


def patch_js() -> None:
    p = ROOT / "js" / "places-map.js"
    text = p.read_text(encoding="utf-8")
    if "lake: true" in text and "legendLake" not in text:
        pass
    replacements = [
        (
            "    beach: true,\n    market: true,",
            "    beach: true,\n    lake: true,\n    market: true,",
        ),
        (
            'places: { types: ["city", "nature", "heritage", "mountain", "beach", "market"], metro: false },',
            'places: { types: ["city", "nature", "heritage", "mountain", "beach", "lake", "market"], metro: false },',
        ),
        (
            """              kind === "beach" ||
              kind === "market" ||""",
            """              kind === "beach" ||
              kind === "lake" ||
              kind === "market" ||""",
        ),
    ]
    for old, new in replacements:
        if new.strip() in text:
            continue
        if old not in text:
            print(f"WARN js skip missing: {old[:60]!r}")
            continue
        text = text.replace(old, new)

    glyphs_slice = text[text.find("MARKER_GLYPHS") : text.find("MARKER_GLYPHS") + 4000]
    if "lake:" not in glyphs_slice:
        lake_block = (
            "    // Lake / inland water\n"
            "    lake:\n"
            "      '<svg viewBox=\"0 0 24 24\" width=\"16\" height=\"16\" focusable=\"false\" aria-hidden=\"true\">' +\n"
            f"      '<path fill=\"currentColor\" d=\"{LAKE_SVG_PATH}\"/>' +\n"
            '      "</svg>",\n'
        )
        text = text.replace(
            "    // Pagoda: roof tiers + base pillar\n    heritage:",
            lake_block + "    // Pagoda: roof tiers + base pillar\n    heritage:",
            1,
        )
    # BADGE_MARKER_KINDS — add lake after beach
    if "lake: true" not in text.split("BADGE_MARKER_KINDS")[1][:400]:
        text = text.replace(
            "  var BADGE_MARKER_KINDS = {\n    city: true,\n    nature: true,\n    heritage: true,\n    mountain: true,\n    beach: true,\n    market: true,",
            "  var BADGE_MARKER_KINDS = {\n    city: true,\n    nature: true,\n    heritage: true,\n    mountain: true,\n    beach: true,\n    lake: true,\n    market: true,",
            1,
        )
    # PLACE_TYPES block (second occurrence after DEFAULT)
    text = text.replace(
        "  var PLACE_TYPES = {\n    city: true,\n    nature: true,\n    heritage: true,\n    mountain: true,\n    beach: true,\n    market: true,",
        "  var PLACE_TYPES = {\n    city: true,\n    nature: true,\n    heritage: true,\n    mountain: true,\n    beach: true,\n    lake: true,\n    market: true,",
        1,
    )
    # Ensure DEFAULT_TYPES has lake
    text = text.replace(
        "  var DEFAULT_TYPES = {\n    city: true,\n    nature: true,\n    heritage: true,\n    mountain: true,\n    beach: true,\n    market: true,",
        "  var DEFAULT_TYPES = {\n    city: true,\n    nature: true,\n    heritage: true,\n    mountain: true,\n    beach: true,\n    lake: true,\n    market: true,",
        1,
    )
    atomic_write(p, text)
    print("patched places-map.js")


def patch_css() -> None:
    p = ROOT / "styles.css"
    text = p.read_text(encoding="utf-8")
    if "swatch--lake" in text:
        print("css: lake already present")
        return
    text = text.replace(
        ".places-map-legend__swatch--beach,\n.places-map-legend__swatch--market,",
        ".places-map-legend__swatch--beach,\n.places-map-legend__swatch--lake,\n.places-map-legend__swatch--market,",
        1,
    )
    # Insert lake swatch block before beach swatch definition
    beach_swatch = ".places-map-legend__swatch--beach {\n"
    if beach_swatch in text and "swatch--lake {" not in text:
        lake_swatch = (
            f".places-map-legend__swatch--lake {{\n"
            f"  border-radius: 50%;\n"
            f"  background-color: {LAKE_COLOR};\n"
            f"  background-image: url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
            f"viewBox='0 0 24 24'%3E%3Cpath fill='%23fff' d='{LAKE_SVG_PATH}'/%3E%3C/svg%3E\");\n"
            f"}}\n\n"
        )
        text = text.replace(beach_swatch, lake_swatch + beach_swatch, 1)

    text = text.replace(
        ".places-map-marker__beach,\n.places-map-marker__market,",
        ".places-map-marker__beach,\n.places-map-marker__lake,\n.places-map-marker__market,",
        1,
    )
    text = text.replace(
        ".places-map-marker__beach svg,\n.places-map-marker__market svg,",
        ".places-map-marker__beach svg,\n.places-map-marker__lake svg,\n.places-map-marker__market svg,",
        1,
    )
    text = text.replace(
        """.places-map-marker__beach {
  background: linear-gradient(145deg, #5ec4e8 0%, #3aa0c8 100%);
  box-shadow: 0 2px 10px rgba(30, 120, 160, 0.5);
}

.places-map-marker__market {""",
        """.places-map-marker__beach {
  background: linear-gradient(145deg, #5ec4e8 0%, #3aa0c8 100%);
  box-shadow: 0 2px 10px rgba(30, 120, 160, 0.5);
}

.places-map-marker__lake {
  background: linear-gradient(145deg, #5aa8d8 0%, #2f7eb8 100%);
  box-shadow: 0 2px 10px rgba(30, 100, 150, 0.5);
}

.places-map-marker__market {""",
        1,
    )
    text = text.replace(
        """.places-map-marker--beach .places-map-marker__pulse {
  background: rgba(58, 160, 200, 0.4);
  top: 12px;
}

.places-map-marker--market .places-map-marker__pulse {""",
        """.places-map-marker--beach .places-map-marker__pulse {
  background: rgba(58, 160, 200, 0.4);
  top: 12px;
}

.places-map-marker--lake .places-map-marker__pulse {
  background: rgba(47, 126, 184, 0.4);
  top: 12px;
}

.places-map-marker--market .places-map-marker__pulse {""",
        1,
    )
    text = text.replace(
        """.places-map-marker--beach.is-active .places-map-marker__beach,
.places-map-marker--beach.is-hover .places-map-marker__beach,
.places-map-marker--market.is-active .places-map-marker__market,
.places-map-marker--market.is-hover .places-map-marker__market,""",
        """.places-map-marker--beach.is-active .places-map-marker__beach,
.places-map-marker--beach.is-hover .places-map-marker__beach,
.places-map-marker--lake.is-active .places-map-marker__lake,
.places-map-marker--lake.is-hover .places-map-marker__lake,
.places-map-marker--market.is-active .places-map-marker__market,
.places-map-marker--market.is-hover .places-map-marker__market,""",
        1,
    )
    text = text.replace(
        """.places-map-drawer__swatch--beach {
  border-radius: 50%;
  background: #3aa0c8;
}

.places-map-drawer__swatch--market {""",
        f""".places-map-drawer__swatch--beach {{
  border-radius: 50%;
  background: #3aa0c8;
}}

.places-map-drawer__swatch--lake {{
  border-radius: 50%;
  background: {LAKE_COLOR};
}}

.places-map-drawer__swatch--market {{""",
        1,
    )
    atomic_write(p, text)
    print("patched styles.css")


def patch_coords_header(text: str) -> str:
    if '"lake"' in text[:900]:
        return text
    text = text.replace(
        ' * type: "city" | "nature" | "heritage" | "mountain" | "beach" | "airport"',
        ' * type: "city" | "nature" | "heritage" | "mountain" | "beach" | "lake" | "airport"',
        1,
    )
    text = text.replace(
        " *   beach    — swimming beaches / seaside resorts\n",
        " *   beach    — swimming beaches / seaside resorts\n"
        " *   lake     — inland lakes / reservoirs / lake parks\n",
        1,
    )
    return text


def reclassify_lakes(text: str) -> str:
    for slug in RECLASSIFY_TO_LAKE:
        pat = re.compile(
            rf'(\{{ slug: "{re.escape(slug)}", lat: [-\d.]+, lng: [-\d.]+, region: "[^"]*", type: )"nature"'
        )
        text, n = pat.subn(r'\1"lake"', text, count=1)
        print(f"reclassify {slug}: {n}")
    return text


def existing_slugs(text: str) -> set[str]:
    return set(re.findall(r'slug:\s*"([^"]+)"', text))


def ensure_images(slugs: list[str], typ: str) -> None:
    IMG.mkdir(parents=True, exist_ok=True)
    if typ == "lake":
        if not TYPE_FALLBACK_LAKE.exists():
            src = TYPE_FALLBACK_NATURE if TYPE_FALLBACK_NATURE.exists() else None
            if src:
                shutil.copy2(src, TYPE_FALLBACK_LAKE)
                print(f"created {TYPE_FALLBACK_LAKE.name} from nature fallback")
        fallback = TYPE_FALLBACK_LAKE if TYPE_FALLBACK_LAKE.exists() else TYPE_FALLBACK_NATURE
    else:
        fallback = TYPE_FALLBACK_NATURE
    if not fallback.exists():
        print(f"WARN: missing fallback {fallback}")
        return
    for slug in slugs:
        dest = IMG / f"{slug}.jpg"
        if dest.exists() and dest.stat().st_size > 5000:
            continue
        shutil.copy2(fallback, dest)
        print(f"fallback image {dest.name}")


def fix_baegun_typo(p: dict) -> dict:
    """Fix accidental leading space in how text if present."""
    how = p["ko"].get("how", "")
    if how.startswith(" "):
        p["ko"]["how"] = how.lstrip()
    return p


def main() -> int:
    # Fix known typo in curated data
    for i, p in enumerate(LAKES):
        if p["slug"] == "baegun-lake":
            LAKES[i] = fix_baegun_typo(p)
            if LAKES[i]["ko"]["how"].startswith(" indus"):
                LAKES[i]["ko"]["how"] = "1호선 의왕역에서 버스, 또는 자가용."

    try:
        patch_html()
    except SystemExit as exc:
        print(f"WARN skip html: {exc}")
    patch_js()
    patch_css()

    text = COORDS.read_text(encoding="utf-8")
    text = patch_coords_header(text)
    text = reclassify_lakes(text)
    have = existing_slugs(text)

    to_add = []
    for p in ALL_NEW:
        if p["slug"] in have:
            print(f"skip existing {p['slug']}")
            continue
        to_add.append(p)
        have.add(p["slug"])

    if to_add:
        lines = []
        for p in to_add:
            img = f"Images/places/{p['slug']}.jpg"
            note = p["en"]["name"].replace('"', "'")
            lines.append(
                "  { "
                f'slug: "{p["slug"]}", lat: {p["lat"]}, lng: {p["lng"]}, '
                f'region: "{p["region"]}", type: "{p["type"]}", '
                f'note: "{note}", image: "{img}" '
                "},"
            )
        insert = "\n".join(lines) + "\n"
        idx = text.rfind("];")
        if idx < 0:
            raise SystemExit("places-coords.js: cannot find ];")
        text = text[:idx] + insert + text[idx:]

    # Atomic write via temp
    atomic_write(COORDS, text)
    print(f"wrote coords (+{len(to_add)})")

    sys.path.insert(0, str(ROOT / "tool"))
    from lib import i18n_store  # noqa: WPS433

    bundle = i18n_store.load_all()
    for lang in i18n_store.LANGS:
        tr = bundle[lang].setdefault("transport", {})
        labels = {
            "ko": "호수",
            "en": "Lake",
            "ja": "湖",
            "zh": "湖泊",
            "zh-Hant": "湖泊",
            "vi": "Hồ",
            "th": "ทะเลสาบ",
            "ru": "Озёра",
        }
        tr["legendLake"] = labels.get(lang) or labels["en"]
        places = bundle[lang].setdefault("places", {})
        for p in to_add:
            places[p["slug"]] = entry_for_lang(lang, p)
        print(f"i18n {lang}: legendLake + {len(to_add)} places")
    i18n_store.save_all(bundle)
    print(i18n_store.build_bundle())

    ensure_images([p["slug"] for p in to_add if p["type"] == "nature"], "nature")
    ensure_images([p["slug"] for p in to_add if p["type"] == "lake"], "lake")

    print("---")
    print(f"added: {len(to_add)}")
    for p in to_add:
        print(f"  + [{p['type']}] {p['ko']['name']} ({p['slug']})")
    print(f"reclassified to lake: {RECLASSIFY_TO_LAKE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
