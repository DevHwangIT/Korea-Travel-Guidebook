# -*- coding: utf-8 -*-
"""Add mountain places (type: mountain) from the outdoor filter name list.

- New mountains → places-coords.js + i18n places.*
- Existing type \"nature\" mountains (e.g. hallasan, seoraksan) → migrate type only
- Dedupes Korean names (마니산 listed twice in source)
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
LIST_PATH = Path(r"C:\Users\HwangInTae\Desktop\guide book\명소 추가할 자료\산 필터 이름정보.txt")

LANGS = ("ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru")

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

# ko_name -> meta (slug, lat, lng, region, en, ja, zh, zh_hant, address_ko)
# Approximate summit / main trailhead coords.
MOUNTAINS: dict[str, dict] = {
    "한라산": {
        "slug": "hallasan",
        "lat": 33.3617,
        "lng": 126.5292,
        "region": "jeju",
        "en": "Hallasan",
        "ja": "漢拏山",
        "zh": "汉拿山",
        "zh_hant": "漢拏山",
        "address": "제주 제주시 한라산국립공원",
    },
    "지리산": {
        "slug": "jirisan",
        "lat": 35.3369,
        "lng": 127.7305,
        "region": "jeolla",
        "en": "Jirisan",
        "ja": "智異山",
        "zh": "智异山",
        "zh_hant": "智異山",
        "address": "전남 구례군·경남 산청군 지리산국립공원",
    },
    "설악산": {
        "slug": "seoraksan",
        "lat": 38.1195,
        "lng": 128.4654,
        "region": "gangwon",
        "en": "Seoraksan",
        "ja": "雪嶽山",
        "zh": "雪岳山",
        "zh_hant": "雪嶽山",
        "address": "강원 속초시·양양군 설악산국립공원",
    },
    "북한산": {
        "slug": "bukhansan",
        "lat": 37.6587,
        "lng": 126.9936,
        "region": "seoul",
        "en": "Bukhansan",
        "ja": "北漢山",
        "zh": "北汉山",
        "zh_hant": "北漢山",
        "address": "서울 은평구·강북구 북한산국립공원",
    },
    "덕유산": {
        "slug": "deogyusan",
        "lat": 35.8603,
        "lng": 127.7464,
        "region": "jeolla",
        "en": "Deogyusan",
        "ja": "德裕山",
        "zh": "德裕山",
        "zh_hant": "德裕山",
        "address": "전북 무주군 덕유산국립공원",
    },
    "오대산": {
        "slug": "odaesan",
        "lat": 37.794,
        "lng": 128.542,
        "region": "gangwon",
        "en": "Odaesan",
        "ja": "五臺山",
        "zh": "五台山",
        "zh_hant": "五臺山",
        "address": "강원 평창군 오대산국립공원",
    },
    "태백산": {
        "slug": "taebaeksan",
        "lat": 37.096,
        "lng": 128.915,
        "region": "gangwon",
        "en": "Taebaeksan",
        "ja": "太白山",
        "zh": "太白山",
        "zh_hant": "太白山",
        "address": "강원 태백시 태백산국립공원",
    },
    "소백산": {
        "slug": "sobaeksan",
        "lat": 36.958,
        "lng": 128.48,
        "region": "chungcheong",
        "en": "Sobaeksan",
        "ja": "小白山",
        "zh": "小白山",
        "zh_hant": "小白山",
        "address": "충북 단양군·경북 영주시 소백산국립공원",
    },
    "속리산": {
        "slug": "songnisan",
        "lat": 36.543,
        "lng": 127.87,
        "region": "chungcheong",
        "en": "Songnisan",
        "ja": "俗離山",
        "zh": "俗离山",
        "zh_hant": "俗離山",
        "address": "충북 보은군 속리산국립공원",
    },
    "내장산": {
        "slug": "naejangsan",
        "lat": 35.488,
        "lng": 126.888,
        "region": "jeolla",
        "en": "Naejangsan",
        "ja": "內藏山",
        "zh": "内藏山",
        "zh_hant": "內藏山",
        "address": "전북 정읍시 내장산국립공원",
    },
    "무등산": {
        "slug": "mudeungsan",
        "lat": 35.134,
        "lng": 126.989,
        "region": "jeolla",
        "en": "Mudeungsan",
        "ja": "無等山",
        "zh": "无等山",
        "zh_hant": "無等山",
        "address": "광주 동구·화순군 무등산국립공원",
    },
    "계룡산": {
        "slug": "gyeryongsan",
        "lat": 36.343,
        "lng": 127.206,
        "region": "chungcheong",
        "en": "Gyeryongsan",
        "ja": "鷄龍山",
        "zh": "鸡龙山",
        "zh_hant": "雞龍山",
        "address": "충남 공주시·계룡시 계룡산국립공원",
    },
    "치악산": {
        "slug": "chiaksan",
        "lat": 37.365,
        "lng": 128.05,
        "region": "gangwon",
        "en": "Chiaksan",
        "ja": "雉岳山",
        "zh": "雉岳山",
        "zh_hant": "雉岳山",
        "address": "강원 원주시 치악산국립공원",
    },
    "가야산": {
        "slug": "gayasan",
        "lat": 35.822,
        "lng": 128.122,
        "region": "gyeongsang",
        "en": "Gayasan",
        "ja": "伽倻山",
        "zh": "伽倻山",
        "zh_hant": "伽倻山",
        "address": "경북 성주군·경남 합천군 가야산국립공원",
    },
    "관악산": {
        "slug": "gwanaksan",
        "lat": 37.445,
        "lng": 126.964,
        "region": "seoul",
        "en": "Gwanaksan",
        "ja": "冠岳山",
        "zh": "冠岳山",
        "zh_hant": "冠岳山",
        "address": "서울 관악구·경기 과천시 관악산",
    },
    "금정산": {
        "slug": "geumjeongsan",
        "lat": 35.283,
        "lng": 129.055,
        "region": "busan",
        "en": "Geumjeongsan",
        "ja": "金井山",
        "zh": "金井山",
        "zh_hant": "金井山",
        "address": "부산 금정구·북구 금정산",
    },
    "팔공산": {
        "slug": "palgongsan",
        "lat": 35.987,
        "lng": 128.695,
        "region": "gyeongsang",
        "en": "Palgongsan",
        "ja": "八公山",
        "zh": "八公山",
        "zh_hant": "八公山",
        "address": "대구 동구·경북 영천시 팔공산",
    },
    "월악산": {
        "slug": "woraksan",
        "lat": 36.885,
        "lng": 128.1,
        "region": "chungcheong",
        "en": "Woraksan",
        "ja": "月岳山",
        "zh": "月岳山",
        "zh_hant": "月岳山",
        "address": "충북 제천시·충주시 월악산국립공원",
    },
    "주왕산": {
        "slug": "juwangsan",
        "lat": 36.402,
        "lng": 129.167,
        "region": "gyeongsang",
        "en": "Juwangsan",
        "ja": "周王山",
        "zh": "周王山",
        "zh_hant": "周王山",
        "address": "경북 청송군 주왕산국립공원",
    },
    "마이산": {
        "slug": "maisan",
        "lat": 35.762,
        "lng": 127.413,
        "region": "jeolla",
        "en": "Maisan",
        "ja": "馬耳山",
        "zh": "马耳山",
        "zh_hant": "馬耳山",
        "address": "전북 진안군 마이산",
    },
    "도봉산": {
        "slug": "dobongsan",
        "lat": 37.698,
        "lng": 127.015,
        "region": "seoul",
        "en": "Dobongsan",
        "ja": "道峰山",
        "zh": "道峰山",
        "zh_hant": "道峰山",
        "address": "서울 도봉구 도봉산",
    },
    "수락산": {
        "slug": "suraksan",
        "lat": 37.697,
        "lng": 127.081,
        "region": "seoul",
        "en": "Suraksan",
        "ja": "水落山",
        "zh": "水落山",
        "zh_hant": "水落山",
        "address": "서울 노원구·경기 남양주시 수락산",
    },
    "청계산": {
        "slug": "cheonggyesan",
        "lat": 37.423,
        "lng": 127.041,
        "region": "seoul",
        "en": "Cheonggyesan",
        "ja": "淸溪山",
        "zh": "清溪山",
        "zh_hant": "清溪山",
        "address": "서울 서초구·경기 성남시 청계산",
    },
    "금오산": {
        "slug": "geumosan",
        "lat": 36.162,
        "lng": 128.3,
        "region": "gyeongsang",
        "en": "Geumosan",
        "ja": "金烏山",
        "zh": "金乌山",
        "zh_hant": "金烏山",
        "address": "경북 구미시 금오산",
    },
    "신불산": {
        "slug": "sinbulsan",
        "lat": 35.538,
        "lng": 129.053,
        "region": "gyeongsang",
        "en": "Sinbulsan",
        "ja": "神佛山",
        "zh": "神佛山",
        "zh_hant": "神佛山",
        "address": "울산 울주군 신불산",
    },
    "가지산": {
        "slug": "gajisan",
        "lat": 35.62,
        "lng": 129.004,
        "region": "gyeongsang",
        "en": "Gajisan",
        "ja": "加智山",
        "zh": "加智山",
        "zh_hant": "加智山",
        "address": "울산 울주군·경남 밀양시 가지산",
    },
    "월출산": {
        "slug": "wolchulsan",
        "lat": 34.763,
        "lng": 126.702,
        "region": "jeolla",
        "en": "Wolchulsan",
        "ja": "月出山",
        "zh": "月出山",
        "zh_hant": "月出山",
        "address": "전남 영암군 월출산국립공원",
    },
    "대둔산": {
        "slug": "daedunsan",
        "lat": 36.124,
        "lng": 127.305,
        "region": "chungcheong",
        "en": "Daedunsan",
        "ja": "大芚山",
        "zh": "大芚山",
        "zh_hant": "大芚山",
        "address": "충남 금산군·전북 완주군 대둔산",
    },
    "황매산": {
        "slug": "hwangmaesan",
        "lat": 35.492,
        "lng": 127.974,
        "region": "gyeongsang",
        "en": "Hwangmaesan",
        "ja": "黃梅山",
        "zh": "黄梅山",
        "zh_hant": "黃梅山",
        "address": "경남 합천군·거창군 황매산",
    },
    "두륜산": {
        "slug": "duryunsan",
        "lat": 34.476,
        "lng": 126.619,
        "region": "jeolla",
        "en": "Duryunsan",
        "ja": "頭輪山",
        "zh": "头轮山",
        "zh_hant": "頭輪山",
        "address": "전남 해남군 두륜산",
    },
    "주흘산": {
        "slug": "juheulsan",
        "lat": 36.787,
        "lng": 128.101,
        "region": "gyeongsang",
        "en": "Juheulsan",
        "ja": "主屹山",
        "zh": "主屹山",
        "zh_hant": "主屹山",
        "address": "경북 문경시 주흘산",
    },
    "조계산": {
        "slug": "jogyesan",
        "lat": 34.995,
        "lng": 127.316,
        "region": "jeolla",
        "en": "Jogyesan",
        "ja": "曹溪山",
        "zh": "曹溪山",
        "zh_hant": "曹溪山",
        "address": "전남 순천시 조계산",
    },
    "선운산": {
        "slug": "seonunsan",
        "lat": 35.497,
        "lng": 126.579,
        "region": "jeolla",
        "en": "Seonunsan",
        "ja": "禪雲山",
        "zh": "禅云山",
        "zh_hant": "禪雲山",
        "address": "전북 고창군 선운산",
    },
    "강천산": {
        "slug": "gangcheonsan",
        "lat": 35.403,
        "lng": 127.05,
        "region": "jeolla",
        "en": "Gangcheonsan",
        "ja": "剛泉山",
        "zh": "刚泉山",
        "zh_hant": "剛泉山",
        "address": "전북 순창군 강천산",
    },
    "모악산": {
        "slug": "moaksan",
        "lat": 35.728,
        "lng": 127.085,
        "region": "jeolla",
        "en": "Moaksan",
        "ja": "母岳山",
        "zh": "母岳山",
        "zh_hant": "母岳山",
        "address": "전북 전주시·완주군 모악산",
    },
    "변산": {
        "slug": "byeonsan",
        "lat": 35.617,
        "lng": 126.58,
        "region": "jeolla",
        "en": "Byeonsan",
        "ja": "邊山",
        "zh": "边山",
        "zh_hant": "邊山",
        "address": "전북 부안군 변산반도국립공원",
    },
    "비슬산": {
        "slug": "biseulsan",
        "lat": 35.716,
        "lng": 128.533,
        "region": "gyeongsang",
        "en": "Biseulsan",
        "ja": "琵琶山",
        "zh": "琵琶山",
        "zh_hant": "琵琶山",
        "address": "대구 달성군·경북 청도군 비슬산",
    },
    "화왕산": {
        "slug": "hwawangsan",
        "lat": 35.548,
        "lng": 128.534,
        "region": "gyeongsang",
        "en": "Hwawangsan",
        "ja": "火旺山",
        "zh": "火旺山",
        "zh_hant": "火旺山",
        "address": "경남 창녕군 화왕산",
    },
    "천관산": {
        "slug": "cheongwansan",
        "lat": 34.544,
        "lng": 126.909,
        "region": "jeolla",
        "en": "Cheongwansan",
        "ja": "天冠山",
        "zh": "天冠山",
        "zh_hant": "天冠山",
        "address": "전남 장흥군 천관산",
    },
    "팔영산": {
        "slug": "paryeongsan",
        "lat": 34.623,
        "lng": 127.427,
        "region": "jeolla",
        "en": "Paryeongsan",
        "ja": "八嶺山",
        "zh": "八岭山",
        "zh_hant": "八嶺山",
        "address": "전남 고흥군 팔영산",
    },
    "무학산": {
        "slug": "muhaksan",
        "lat": 35.178,
        "lng": 128.525,
        "region": "gyeongsang",
        "en": "Muhaksan",
        "ja": "舞鶴山",
        "zh": "舞鹤山",
        "zh_hant": "舞鶴山",
        "address": "경남 창원시 무학산",
    },
    "천성산": {
        "slug": "cheonseongsan",
        "lat": 35.389,
        "lng": 129.097,
        "region": "gyeongsang",
        "en": "Cheonseongsan",
        "ja": "千聖山",
        "zh": "千圣山",
        "zh_hant": "千聖山",
        "address": "경남 양산시 천성산",
    },
    "운문산": {
        "slug": "unmunsan",
        "lat": 35.638,
        "lng": 129.025,
        "region": "gyeongsang",
        "en": "Unmunsan",
        "ja": "雲門山",
        "zh": "云门山",
        "zh_hant": "雲門山",
        "address": "경북 청도군 운문산",
    },
    "재약산": {
        "slug": "jaeyaksan",
        "lat": 35.565,
        "lng": 128.978,
        "region": "gyeongsang",
        "en": "Jaeyaksan",
        "ja": "載藥山",
        "zh": "载药山",
        "zh_hant": "載藥山",
        "address": "경남 밀양시 재약산",
    },
    "가리왕산": {
        "slug": "gariwangsan",
        "lat": 37.46,
        "lng": 128.563,
        "region": "gangwon",
        "en": "Gariwangsan",
        "ja": "加里王山",
        "zh": "加里王山",
        "zh_hant": "加里王山",
        "address": "강원 정선군 가리왕산",
    },
    "함백산": {
        "slug": "hambaeksan",
        "lat": 37.161,
        "lng": 128.917,
        "region": "gangwon",
        "en": "Hambaeksan",
        "ja": "咸白山",
        "zh": "咸白山",
        "zh_hant": "咸白山",
        "address": "강원 태백시·정선군 함백산",
    },
    "방태산": {
        "slug": "bangtaesan",
        "lat": 37.896,
        "lng": 128.389,
        "region": "gangwon",
        "en": "Bangtaesan",
        "ja": "方台山",
        "zh": "方台山",
        "zh_hant": "方台山",
        "address": "강원 인제군 방태산",
    },
    "점봉산": {
        "slug": "jeombongsan",
        "lat": 38.047,
        "lng": 128.43,
        "region": "gangwon",
        "en": "Jeombongsan",
        "ja": "點鳳山",
        "zh": "点凤山",
        "zh_hant": "點鳳山",
        "address": "강원 인제군·양양군 점봉산",
    },
    "화악산": {
        "slug": "hwaaksan",
        "lat": 37.992,
        "lng": 127.492,
        "region": "gyeonggi",
        "en": "Hwaaksan",
        "ja": "華岳山",
        "zh": "华岳山",
        "zh_hant": "華岳山",
        "address": "경기 가평군 화악산",
    },
    "명지산": {
        "slug": "myeongjisan",
        "lat": 37.936,
        "lng": 127.454,
        "region": "gyeonggi",
        "en": "Myeongjisan",
        "ja": "明智山",
        "zh": "明智山",
        "zh_hant": "明智山",
        "address": "경기 가평군 명지산",
    },
    "운악산": {
        "slug": "unaksan",
        "lat": 37.88,
        "lng": 127.326,
        "region": "gyeonggi",
        "en": "Unaksan",
        "ja": "雲岳山",
        "zh": "云岳山",
        "zh_hant": "雲岳山",
        "address": "경기 가평군·포천시 운악산",
    },
    "용문산": {
        "slug": "yongmunsan",
        "lat": 37.551,
        "lng": 127.57,
        "region": "gyeonggi",
        "en": "Yongmunsan",
        "ja": "龍門山",
        "zh": "龙门山",
        "zh_hant": "龍門山",
        "address": "경기 양평군 용문산",
    },
    "감악산": {
        "slug": "gamaksan",
        "lat": 37.918,
        "lng": 126.984,
        "region": "gyeonggi",
        "en": "Gamaksan",
        "ja": "紺岳山",
        "zh": "绀岳山",
        "zh_hant": "紺岳山",
        "address": "경기 파주시·양주시 감악산",
    },
    "마니산": {
        "slug": "manisan",
        "lat": 37.612,
        "lng": 126.435,
        "region": "incheon",
        "en": "Manisan",
        "ja": "摩尼山",
        "zh": "摩尼山",
        "zh_hant": "摩尼山",
        "address": "인천 강화군 마니산",
    },
    "소요산": {
        "slug": "soyosan",
        "lat": 37.948,
        "lng": 127.073,
        "region": "gyeonggi",
        "en": "Soyosan",
        "ja": "逍遙山",
        "zh": "逍遥山",
        "zh_hant": "逍遙山",
        "address": "경기 동두천시 소요산",
    },
    "천마산": {
        "slug": "cheonmasan",
        "lat": 37.68,
        "lng": 127.272,
        "region": "gyeonggi",
        "en": "Cheonmasan",
        "ja": "天摩山",
        "zh": "天摩山",
        "zh_hant": "天摩山",
        "address": "경기 남양주시 천마산",
    },
    "축령산": {
        "slug": "chukryeongsan",
        "lat": 37.754,
        "lng": 127.323,
        "region": "gyeonggi",
        "en": "Chukryeongsan",
        "ja": "祝靈山",
        "zh": "祝灵山",
        "zh_hant": "祝靈山",
        "address": "경기 남양주시·가평군 축령산",
    },
    "유명산": {
        "slug": "yumyeongsan",
        "lat": 37.594,
        "lng": 127.489,
        "region": "gyeonggi",
        "en": "Yumyeongsan",
        "ja": "有明山",
        "zh": "有明山",
        "zh_hant": "有明山",
        "address": "경기 가평군·양평군 유명산",
    },
    "광덕산": {
        "slug": "gwangdeoksan",
        "lat": 38.115,
        "lng": 127.433,
        "region": "gyeonggi",
        "en": "Gwangdeoksan",
        "ja": "廣德山",
        "zh": "广德山",
        "zh_hant": "廣德山",
        "address": "경기 포천시·강원 철원군 광덕산",
    },
    "검단산": {
        "slug": "geomdansan",
        "lat": 37.533,
        "lng": 127.22,
        "region": "gyeonggi",
        "en": "Geomdansan",
        "ja": "黔丹山",
        "zh": "黔丹山",
        "zh_hant": "黔丹山",
        "address": "경기 하남시 검단산",
    },
    "삼악산": {
        "slug": "samaksan",
        "lat": 37.866,
        "lng": 127.658,
        "region": "gangwon",
        "en": "Samaksan",
        "ja": "三岳山",
        "zh": "三岳山",
        "zh_hant": "三岳山",
        "address": "강원 춘천시 삼악산",
    },
    "오봉산": {
        "slug": "obongsan",
        "lat": 37.953,
        "lng": 127.748,
        "region": "gangwon",
        "en": "Obongsan",
        "ja": "五峰山",
        "zh": "五峰山",
        "zh_hant": "五峰山",
        "address": "강원 춘천시 오봉산",
    },
    "대암산": {
        "slug": "daeamsan",
        "lat": 38.215,
        "lng": 128.135,
        "region": "gangwon",
        "en": "Daeamsan",
        "ja": "大岩山",
        "zh": "大岩山",
        "zh_hant": "大岩山",
        "address": "강원 인제군·양구군 대암산",
    },
    "두타산": {
        "slug": "dutasan",
        "lat": 37.44,
        "lng": 129.002,
        "region": "gangwon",
        "en": "Dutasan",
        "ja": "頭陀山",
        "zh": "头陀山",
        "zh_hant": "頭陀山",
        "address": "강원 동해시·삼척시 두타산",
    },
    "청옥산": {
        "slug": "cheongoksan",
        "lat": 37.312,
        "lng": 129.05,
        "region": "gangwon",
        "en": "Cheongoksan",
        "ja": "靑玉山",
        "zh": "青玉山",
        "zh_hant": "青玉山",
        "address": "강원 삼척시 청옥산",
    },
    "민주지산": {
        "slug": "minjujisan",
        "lat": 36.048,
        "lng": 127.85,
        "region": "chungcheong",
        "en": "Minjujisan",
        "ja": "珉周之山",
        "zh": "珉周之山",
        "zh_hant": "珉周之山",
        "address": "충북 영동군 민주지산",
    },
    "황악산": {
        "slug": "hwangaksan",
        "lat": 36.118,
        "lng": 127.978,
        "region": "gyeongsang",
        "en": "Hwangaksan",
        "ja": "黃岳山",
        "zh": "黄岳山",
        "zh_hant": "黃岳山",
        "address": "경북 김천시 황악산",
    },
    "희양산": {
        "slug": "huiyangsan",
        "lat": 36.715,
        "lng": 127.975,
        "region": "gyeongsang",
        "en": "Huiyangsan",
        "ja": "犧陽山",
        "zh": "牺阳山",
        "zh_hant": "犧陽山",
        "address": "경북 문경시 희양산",
    },
    "조령산": {
        "slug": "joryeongsan",
        "lat": 36.807,
        "lng": 128.045,
        "region": "chungcheong",
        "en": "Joryeongsan",
        "ja": "鳥嶺山",
        "zh": "鸟岭山",
        "zh_hant": "鳥嶺山",
        "address": "충북 괴산군·경북 문경시 조령산",
    },
    "금수산": {
        "slug": "geumsusan",
        "lat": 36.986,
        "lng": 128.255,
        "region": "chungcheong",
        "en": "Geumsusan",
        "ja": "錦繡山",
        "zh": "锦绣山",
        "zh_hant": "錦繡山",
        "address": "충북 제천시 금수산",
    },
    "도락산": {
        "slug": "doraksan",
        "lat": 36.86,
        "lng": 128.24,
        "region": "chungcheong",
        "en": "Doraksan",
        "ja": "道樂山",
        "zh": "道乐山",
        "zh_hant": "道樂山",
        "address": "충북 단양군 도락산",
    },
    "대야산": {
        "slug": "daeyasan",
        "lat": 36.67,
        "lng": 127.95,
        "region": "gyeongsang",
        "en": "Daeyasan",
        "ja": "大耶山",
        "zh": "大耶山",
        "zh_hant": "大耶山",
        "address": "경북 문경시 대야산",
    },
    "황석산": {
        "slug": "hwangseoksan",
        "lat": 35.7,
        "lng": 127.77,
        "region": "gyeongsang",
        "en": "Hwangseoksan",
        "ja": "黃石山",
        "zh": "黄石山",
        "zh_hant": "黃石山",
        "address": "경남 함양군 황석산",
    },
    "구병산": {
        "slug": "gubyeongsan",
        "lat": 36.47,
        "lng": 127.86,
        "region": "chungcheong",
        "en": "Gubyeongsan",
        "ja": "九屛山",
        "zh": "九屏山",
        "zh_hant": "九屛山",
        "address": "충북 보은군 구병산",
    },
    "운장산": {
        "slug": "unjangsan",
        "lat": 35.93,
        "lng": 127.42,
        "region": "jeolla",
        "en": "Unjangsan",
        "ja": "雲長山",
        "zh": "云长山",
        "zh_hant": "雲長山",
        "address": "전북 진안군 운장산",
    },
    "구봉산": {
        "slug": "gubongsan",
        "lat": 35.94,
        "lng": 127.25,
        "region": "jeolla",
        "en": "Gubongsan",
        "ja": "九峰山",
        "zh": "九峰山",
        "zh_hant": "九峰山",
        "address": "전북 완주군 구봉산",
    },
    "장안산": {
        "slug": "jangansan",
        "lat": 35.63,
        "lng": 127.59,
        "region": "jeolla",
        "en": "Jangansan",
        "ja": "長安山",
        "zh": "长安山",
        "zh_hant": "長安山",
        "address": "전북 장수군 장안산",
    },
    "덕항산": {
        "slug": "deokhangsan",
        "lat": 37.25,
        "lng": 129.0,
        "region": "gangwon",
        "en": "Deokhangsan",
        "ja": "德項山",
        "zh": "德项山",
        "zh_hant": "德項山",
        "address": "강원 삼척시 덕항산",
    },
    "적상산": {
        "slug": "jeoksangsan",
        "lat": 35.955,
        "lng": 127.695,
        "region": "jeolla",
        "en": "Jeoksangsan",
        "ja": "赤裳山",
        "zh": "赤裳山",
        "zh_hant": "赤裳山",
        "address": "전북 무주군 적상산",
    },
    "남덕유산": {
        "slug": "namdeogyusan",
        "lat": 35.76,
        "lng": 127.68,
        "region": "gyeongsang",
        "en": "Namdeogyusan",
        "ja": "南德裕山",
        "zh": "南德裕山",
        "zh_hant": "南德裕山",
        "address": "경남 거창군·함양군 남덕유산",
    },
    "방장산": {
        "slug": "bangjangsan",
        "lat": 35.45,
        "lng": 126.75,
        "region": "jeolla",
        "en": "Bangjangsan",
        "ja": "方丈山",
        "zh": "方丈山",
        "zh_hant": "方丈山",
        "address": "전북 고창군·전남 장성군 방장산",
    },
    "백암산": {
        "slug": "baegamsan",
        "lat": 35.495,
        "lng": 126.87,
        "region": "jeolla",
        "en": "Baegamsan",
        "ja": "白巖山",
        "zh": "白岩山",
        "zh_hant": "白巖山",
        "address": "전남 장성군 백암산",
    },
    "백운산": {
        "slug": "baegunsan",
        "lat": 35.106,
        "lng": 127.621,
        "region": "jeolla",
        "en": "Baegunsan",
        "ja": "白雲山",
        "zh": "白云山",
        "zh_hant": "白雲山",
        "address": "전남 광양시 백운산",
    },
    "서대산": {
        "slug": "seodaesan",
        "lat": 36.55,
        "lng": 127.34,
        "region": "chungcheong",
        "en": "Seodaesan",
        "ja": "西大山",
        "zh": "西大山",
        "zh_hant": "西大山",
        "address": "충남 금산군 서대산",
    },
    "성인봉": {
        "slug": "seonginbong",
        "lat": 37.499,
        "lng": 130.866,
        "region": "gyeongsang",
        "en": "Seonginbong",
        "ja": "聖人峰",
        "zh": "圣人峰",
        "zh_hant": "聖人峰",
        "address": "경북 울릉군 성인봉",
    },
    "내연산": {
        "slug": "naeyeonsan",
        "lat": 36.25,
        "lng": 129.2,
        "region": "gyeongsang",
        "en": "Naeyeonsan",
        "ja": "內延山",
        "zh": "内延山",
        "zh_hant": "內延山",
        "address": "경북 포항시 내연산",
    },
    "가리산": {
        "slug": "garisan",
        "lat": 37.87,
        "lng": 127.95,
        "region": "gangwon",
        "en": "Garisan",
        "ja": "加里山",
        "zh": "加里山",
        "zh_hant": "加里山",
        "address": "강원 홍천군 가리산",
    },
    "계방산": {
        "slug": "gyebangsan",
        "lat": 37.728,
        "lng": 128.465,
        "region": "gangwon",
        "en": "Gyebangsan",
        "ja": "桂芳山",
        "zh": "桂芳山",
        "zh_hant": "桂芳山",
        "address": "강원 평창군·홍천군 계방산",
    },
    "공작산": {
        "slug": "gongjaksan",
        "lat": 37.72,
        "lng": 128.0,
        "region": "gangwon",
        "en": "Gongjaksan",
        "ja": "孔雀山",
        "zh": "孔雀山",
        "zh_hant": "孔雀山",
        "address": "강원 홍천군 공작산",
    },
    "명성산": {
        "slug": "myeongseongsan",
        "lat": 38.1,
        "lng": 127.27,
        "region": "gyeonggi",
        "en": "Myeongseongsan",
        "ja": "明星山",
        "zh": "明星山",
        "zh_hant": "明星山",
        "address": "경기 포천시 명성산",
    },
    "덕숭산": {
        "slug": "deoksungsan",
        "lat": 36.65,
        "lng": 126.67,
        "region": "chungcheong",
        "en": "Deoksungsan",
        "ja": "德崇山",
        "zh": "德崇山",
        "zh_hant": "德崇山",
        "address": "충남 예산군 덕숭산(수덕사)",
    },
    "미륵산": {
        "slug": "mireuksan",
        "lat": 36.2,
        "lng": 127.17,
        "region": "chungcheong",
        "en": "Mireuksan",
        "ja": "彌勒山",
        "zh": "弥勒山",
        "zh_hant": "彌勒山",
        "address": "충남 논산시 미륵산",
    },
    "깃대봉": {
        "slug": "gitdaebong",
        "lat": 34.684,
        "lng": 125.195,
        "region": "jeolla",
        "en": "Gitdaebong",
        "ja": "旗竿峰",
        "zh": "旗杆峰",
        "zh_hant": "旗竿峰",
        "address": "전남 신안군 흑산도 깃대봉",
    },
    "금산": {
        "slug": "geumsan",
        "lat": 35.052,
        "lng": 129.086,
        "region": "busan",
        "en": "Geumsan",
        "ja": "金山",
        "zh": "金山",
        "zh_hant": "金山",
        "address": "부산 남구 용호동 금산",
    },
    "고려산": {
        "slug": "goryeosan",
        "lat": 37.737,
        "lng": 126.449,
        "region": "incheon",
        "en": "Goryeosan",
        "ja": "高麗山",
        "zh": "高丽山",
        "zh_hant": "高麗山",
        "address": "인천 강화군 고려산",
    },
    "팔봉산": {
        "slug": "palbongsan",
        "lat": 37.7,
        "lng": 127.7,
        "region": "gangwon",
        "en": "Palbongsan",
        "ja": "八峰山",
        "zh": "八峰山",
        "zh_hant": "八峰山",
        "address": "강원 홍천군 팔봉산",
    },
}


def read_list_names() -> list[str]:
    raw = LIST_PATH.read_text(encoding="utf-8")
    names: list[str] = []
    seen: set[str] = set()
    for line in raw.splitlines():
        name = line.strip()
        if not name or name.startswith("#"):
            continue
        if name in seen:
            continue
        seen.add(name)
        names.append(name)
    return names


def maps_urls(q: str, hl: str) -> tuple[str, str]:
    enc = quote(q)
    return (
        f"https://www.google.com/maps/search/?api=1&query={enc}",
        f"https://maps.google.com/maps?q={enc}&hl={hl}&z=12&output=embed",
    )


def texts_for(ko_name: str, m: dict) -> dict[str, dict[str, str]]:
    en = m["en"]
    region = m["region"]
    rl = REGION_LABELS.get(region, REGION_LABELS[""])
    how_ko = "인근 시내·터미널에서 버스·택시로 탐방로 입구까지. 날씨·입산 통제는 공식 안내를 확인하세요."
    how_en = "Bus or taxi from the nearest town/terminal to the trailhead. Check official notices for weather and closures."
    how_ja = "最寄りの市街・ターミナルからバス・タクシーで登山口へ。天候・入山規制は公式案内を確認。"
    how_zh = "从附近市区或客运站乘公交/出租车到登山口。天气与入山管制请查官方公告。"
    how_zh_hant = "從附近市區或客運站搭公車/計程車到登山口。天氣與入山管制請查官方公告。"
    return {
        "ko": {
            "name": ko_name,
            "desc": f"{rl['ko']}의 대표 등산·트레킹 명소 {ko_name}. 정상·능선 전망과 계절별 풍경이 인기입니다.",
            "how": how_ko,
            "address": m["address"],
            "regionLabel": rl["ko"],
        },
        "en": {
            "name": en,
            "desc": f"Popular hiking peak in {rl['en']} — trails, ridge views, and seasonal scenery at {en}.",
            "how": how_en,
            "address": m["address"],
            "regionLabel": rl["en"],
        },
        "ja": {
            "name": m["ja"],
            "desc": f"{rl['ja']}の代表的な登山スポット。稜線の展望と季節の風景が人気です。",
            "how": how_ja,
            "address": m["address"],
            "regionLabel": rl["ja"],
        },
        "zh": {
            "name": m["zh"],
            "desc": f"{rl['zh']}代表性登山目的地，山脊景观与四季景色都很受欢迎。",
            "how": how_zh,
            "address": m["address"],
            "regionLabel": rl["zh"],
        },
        "zh-Hant": {
            "name": m["zh_hant"],
            "desc": f"{rl['zh-Hant']}代表性登山目的地，山脊景觀與四季景色都很受歡迎。",
            "how": how_zh_hant,
            "address": m["address"],
            "regionLabel": rl["zh-Hant"],
        },
        "vi": {
            "name": en,
            "desc": f"Núi leo phổ biến ở {rl['vi']} — đường mòn, tầm nhìn và cảnh theo mùa tại {en}.",
            "how": how_en,
            "address": m["address"],
            "regionLabel": rl["vi"],
        },
        "th": {
            "name": en,
            "desc": f"ภูเขาปีนยอดนิยมใน{rl['th']} — เส้นทาง ทิวทัศน์ และฤดูกาลที่ {en}",
            "how": how_en,
            "address": m["address"],
            "regionLabel": rl["th"],
        },
        "ru": {
            "name": en,
            "desc": f"Популярная гора для походов в регионе {rl['ru']} — тропы и виды на {en}.",
            "how": how_en,
            "address": m["address"],
            "regionLabel": rl["ru"],
        },
    }


def body_block(all_texts: dict[str, dict[str, str]]) -> list:
    block = {"type": "text"}
    for lang in LANGS:
        t = all_texts[lang]
        if lang == "ko":
            block[lang] = f"{t['desc']}\n\n가는 방법: {t['how']}"
        elif lang == "en":
            block[lang] = f"{t['desc']}\n\nHow to get there: {t['how']}"
        elif lang == "ja":
            block[lang] = f"{t['desc']}\n\n行き方: {t['how']}"
        elif lang in ("zh", "zh-Hant"):
            block[lang] = f"{t['desc']}\n\n如何前往: {t['how']}"
        else:
            block[lang] = f"{t['desc']}\n\nHow to get there: {t['how']}"
    return [block]


def entry_for_lang(lang: str, ko_name: str, m: dict) -> dict:
    all_texts = texts_for(ko_name, m)
    t = all_texts[lang]
    hl = {"zh-Hant": "zh-TW", "zh": "zh-CN"}.get(lang, lang if lang != "ko" else "ko")
    maps, embed = maps_urls(m["address"], hl if lang != "en" else "en")
    if lang == "en":
        maps, embed = maps_urls(m["address"], "en")
    return {
        "name": t["name"],
        "desc": t["desc"],
        "how": t["how"],
        "address": t["address"],
        "regionLabel": t["regionLabel"],
        "region": m["region"],
        "mapsUrl": maps,
        "mapsEmbedUrl": embed,
        "image": f"Images/places/{m['slug']}.jpg",
        "body": body_block(all_texts),
    }


def parse_existing_coords(text: str) -> dict[str, str]:
    """slug -> type"""
    out: dict[str, str] = {}
    for m in re.finditer(
        r'\{\s*slug:\s*"([^"]+)"[^}]*?type:\s*"([^"]+)"',
        text,
        re.S,
    ):
        out[m.group(1)] = m.group(2)
    return out


def migrate_type(text: str, slug: str, new_type: str = "mountain") -> str:
    pat = re.compile(
        rf'(\{{\s*slug:\s*"{re.escape(slug)}"[^}}]*?type:\s*")[^"]+(")',
        re.S,
    )

    def repl(m: re.Match) -> str:
        return m.group(1) + new_type + m.group(2)

    new_text, n = pat.subn(repl, text, count=1)
    if n != 1:
        raise SystemExit(f"failed to migrate type for {slug}")
    return new_text


def coord_line(ko_name: str, m: dict) -> str:
    img = f"Images/places/{m['slug']}.jpg"
    note = m["en"]
    return (
        "  { "
        f'slug: "{m["slug"]}", lat: {m["lat"]}, lng: {m["lng"]}, '
        f'region: "{m["region"]}", type: "mountain", '
        f'note: "{note}", image: "{img}" '
        "},"
    )


def patch_coords(names: list[str]) -> tuple[list[str], list[str], list[str]]:
    text = COORDS.read_text(encoding="utf-8")
    existing = parse_existing_coords(text)
    added: list[str] = []
    migrated: list[str] = []
    skipped: list[str] = []
    new_lines: list[str] = []

    for ko_name in names:
        meta = MOUNTAINS.get(ko_name)
        if not meta:
            print(f"WARN: no meta for {ko_name}")
            skipped.append(ko_name)
            continue
        slug = meta["slug"]
        cur = existing.get(slug)
        if cur == "mountain":
            skipped.append(f"{slug} (already mountain)")
            continue
        if cur == "nature":
            text = migrate_type(text, slug, "mountain")
            existing[slug] = "mountain"
            migrated.append(slug)
            continue
        if cur is not None:
            skipped.append(f"{slug} (exists as {cur})")
            continue
        new_lines.append(coord_line(ko_name, meta))
        existing[slug] = "mountain"
        added.append(slug)

    if new_lines:
        insert = "\n".join(new_lines) + "\n"
        idx = text.rfind("];")
        if idx < 0:
            raise SystemExit("places-coords.js: cannot find ];")
        text = text[:idx] + insert + text[idx:]

    COORDS.write_text(text, encoding="utf-8", newline="\n")
    return added, migrated, skipped


def patch_i18n(names: list[str], added_slugs: set[str]) -> None:
    sys.path.insert(0, str(ROOT / "tool"))
    from lib import i18n_store  # noqa: WPS433

    bundle = i18n_store.load_all()
    count = 0
    for lang in i18n_store.LANGS:
        places = bundle[lang].setdefault("places", {})
        for ko_name in names:
            meta = MOUNTAINS.get(ko_name)
            if not meta:
                continue
            slug = meta["slug"]
            if slug not in added_slugs:
                continue
            if slug in places:
                continue
            places[slug] = entry_for_lang(lang, ko_name, meta)
            count += 1
        print(f"i18n {lang}: mountain entries touched")
    i18n_store.save_all(bundle)
    print(f"i18n place entries written (~{count // len(LANGS)} mountains × langs)")


def ensure_images(added_slugs: list[str]) -> None:
    IMG.mkdir(parents=True, exist_ok=True)
    types = IMG / "_types"
    types.mkdir(parents=True, exist_ok=True)
    mountain_fb = types / "mountain.jpg"
    nature_fb = types / "nature.jpg"
    if not mountain_fb.exists():
        if nature_fb.exists():
            shutil.copy2(nature_fb, mountain_fb)
            print("wrote _types/mountain.jpg from nature.jpg")
        else:
            print("WARN: no nature.jpg fallback for mountain type")
    for slug in added_slugs:
        dest = IMG / f"{slug}.jpg"
        if dest.exists() and dest.stat().st_size > 2000:
            continue
        src = mountain_fb if mountain_fb.exists() else nature_fb
        if src.exists():
            shutil.copy2(src, dest)
            print(f"fallback image {dest.name}")


def main() -> int:
    names = read_list_names()
    print(f"list unique names: {len(names)}")
    missing = [n for n in names if n not in MOUNTAINS]
    if missing:
        raise SystemExit(f"missing MOUNTAINS meta: {missing}")

    added, migrated, skipped = patch_coords(names)
    print(f"coords added: {len(added)}")
    print(f"coords migrated nature→mountain: {len(migrated)} {migrated}")
    print(f"coords skipped: {len(skipped)}")
    if skipped:
        for s in skipped:
            print(f"  skip: {s}")

    patch_i18n(names, set(added))
    ensure_images(added)

    sys.path.insert(0, str(ROOT / "tool"))
    from lib import i18n_store  # noqa: WPS433

    print(i18n_store.build_bundle())

    print("--- summary ---")
    print(f"added ({len(added)}): {', '.join(added)}")
    print(f"type-migrated ({len(migrated)}): {', '.join(migrated)}")
    print(f"skipped ({len(skipped)}): {', '.join(skipped) if skipped else '(none)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
