# -*- coding: utf-8 -*-
"""Build named Seoul metro stations GeoJSON from KoreaMetroData vertices.

Source: https://github.com/ledyx/KoreaMetroData
  src/main/resources/seoul/vertices.min.json
(Seoul Open Data station master — names + WGS84 coords + line_num)

Properties written per station (all ~370 stations):
  name         — Korean Hangul
  name_en      — English / Revised Romanization
  name_han     — Traditional Chinese / Hanja (zh-Hant)
  name_zh      — Simplified Chinese
  name_ja      — Japanese (katakana / common forms)
  name_vi      — Vietnamese UI label (Ga …)
  name_th      — Thai phonetic label
  name_ru      — Russian (Kontsevich Cyrillic)
"""
from __future__ import annotations

import json
import re
import sys
import urllib.request
import ssl
from collections import defaultdict
from pathlib import Path


def _safe_print(*args, **kwargs) -> None:
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        stream = kwargs.get("file") or sys.stdout
        text = " ".join(str(a) for a in args) + kwargs.get("end", "\n")
        enc = getattr(stream, "encoding", None) or "utf-8"
        data = text.encode(enc, errors="replace")
        buf = getattr(stream, "buffer", None)
        if buf is not None:
            buf.write(data)
        else:
            stream.write(data.decode(enc, errors="replace"))

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "metro"
OUT_GEO = OUT_DIR / "stations.geojson"
OUT_JS = OUT_DIR / "stations-data.js"
CACHE = ROOT / "tool" / "_tmp_vertices_min.json"
SOURCE_URL = (
    "https://raw.githubusercontent.com/ledyx/KoreaMetroData/master/"
    "src/main/resources/seoul/vertices.min.json"
)

LINE_MAP = {
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
    "A": "arex",
    "K": "gyeongui",
    "B": "suin-bundang",
    "SU": "suin-bundang",
    "S": "shinbundang",
}

# Sillim Line (2022) is absent from KoreaMetroData — OSM-derived extras.
# name -> (lon, lat, name_en)
SILLIM_EXTRA: dict[str, tuple[float, float, str]] = {
    "샛강": (126.929418, 37.517367, "Saetgang"),
    "대방": (126.925174, 37.512581, "Daebang"),
    "서울지방병무청": (
        126.922724,
        37.505963,
        "Seoul Regional Office of Military Manpower",
    ),
    "보라매": (126.920474, 37.500281, "Boramae"),
    "보라매공원": (126.918190, 37.495293, "Boramae Park"),
    "보라매병원": (126.924273, 37.492964, "Boramae Medical Center"),
    "당곡": (126.927801, 37.489696, "Danggok"),
    "신림": (126.929611, 37.484659, "Sillim"),
    "서원": (126.933012, 37.478211, "Seowon"),
    "서울대벤처타운": (
        126.933706,
        37.472003,
        "Seoul Nat'l Univ. Venture Town",
    ),
    "관악산": (126.945328, 37.468736, "Gwanaksan"),
}

LINE_SORT_KEY = {
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "arex": 10,
    "gyeongui": 11,
    "suin-bundang": 12,
    "shinbundang": 13,
    "sillim": 14,
}

CURATED_PATH = OUT_GEO

# Fix empty / Hangul / broken English labels from the open-data dump
EN_OVERRIDES: dict[str, str] = {
    "지제": "Jije",
    "진위": "Jinwi",
    "세마": "Sema",
    "오산대": "Osan Univ.",
    "서동탄": "Seodongtan",
    "광명": "Gwangmyeong",
    "광운대": "Kwangwoon Univ.",
    "공항화물청사": "Incheon Airport Cargo Terminal",
    "어린이대공원": "Children's Grand Park",
    "을지로4가": "Euljiro 4-ga",
    "종로5가": "Jongno 5-ga",
    "신길온천": "Singil Oncheon",
    "온양온천": "Onyang Oncheon",
    "효창공원앞": "Hyochang Park",
    "정부과천청사": "Government Complex Gwacheon",
    "서울": "Seoul Station",
}

# Official-ish / common labels for tourist-heavy stations (override auto)
JA_OVERRIDES: dict[str, str] = {
    "강남": "カンナム",
    "명동": "ミョンドン",
    "홍대입구": "ホンデイック大学入口",
    "이태원": "イテウォン",
    "경복궁": "キョンボックン",
    "광화문": "クァンファムン",
    "잠실": "チャムシル",
    "신도림": "シンドリム",
    "서울": "ソウル駅",
    "시청": "シチョン",
    "동대문": "トンデムン",
    "동대문역사문화공원": "トンデムン歴史文化公園",
    "압구정": "アックジョン",
    "여의도": "ヨイド",
    "합정": "ハプチョン",
    "신논현": "シンノンヒョン",
    "고속터미널": "高速ターミナル",
    "인천공항1터미널": "仁川空港第1ターミナル",
    "인천공항2터미널": "仁川空港第2ターミナル",
    "김포공항": "金浦空港",
    "종각": "チョンガク",
    "종로3가": "チョンノ3街",
    "혜화": "ヘファ",
    "안국": "アングク",
    "이대": "梨花女子大",
    "신촌": "シンチョン",
    "성수": "ソンス",
    "건대입구": "建大入口",
    "서울대입구": "ソウル大入口",
    "교대": "教大",
    "사당": "サダン",
    "노량진": "ノリャンジン",
    "용산": "ヨンサン",
    "영등포": "ヨンドゥンポ",
    "왕십리": "ワンシムニ",
    "청량리": "チョンニャンニ",
    "을지로입구": "ウルチロ入口",
    "을지로3가": "ウルチロ3街",
    "충무로": "チュンムロ",
    "회현": "フェヒョン",
    "삼각지": "サンカクチ",
    "녹사평": "ノクサピョン",
    "한강진": "ハンガンジン",
    "상수": "サンス",
    "공덕": "コンドク",
    "디지털미디어시티": "デジタルメディアシティ",
    "검암": "コマム",
    "계양": "ケヤン",
    "봉은사": "ポンウンサ",
    "종합운동장": "総合運動場",
    "올림픽공원": "オリンピック公園",
    "천호": "チョンホ",
    "군자": "クンジャ",
    "불광": "プルグァン",
    "연신내": "ヨンシンネ",
    "노원": "ノウォン",
    "창동": "チャンドン",
    "당산": "タンサン",
    "신림": "シルリム",
    "신당": "シンダン",
    "동묘앞": "トンミョ前",
    "약수": "ヤクス",
    "양재": "ヤンジェ",
    "서대문": "ソデムン",
    "동작": "トンジャク",
    "숙대입구": "淑大入口",
    "성신여대입구": "誠信女子大入口",
    "선릉": "ソンルン",
    "학동": "ハクトン",
    "논현": "ノンヒョン",
    "강남구청": "江南区庁",
    "가산디지털단지": "加山デジタル団地",
    "구로디지털단지": "九老デジタル団地",
    "남부터미널": "南部ターミナル",
    "마곡나루": "マゴンナル",
    "여의나루": "ヨイナル",
    "충정로": "チュンジョンロ",
    "총신대입구(이수)": "総神大入口(梨水)",
}

# Stations missing open-data hanja: (traditional, simplified)
ZH_OVERRIDES: dict[str, tuple[str, str]] = {
    "가산디지털단지": ("加山數碼園區", "加山数码园区"),
    "고속터미널": ("高速巴士客運站", "高速巴士客运站"),
    "광나루": ("廣渡口", "广渡口"),
    "광명사거리": ("光明十字路口", "光明十字路口"),
    "구로디지털단지": ("九老數碼園區", "九老数码园区"),
    "굽은다리": ("彎橋", "弯桥"),
    "까치산": ("喜鵲山", "喜鹊山"),
    "까치울": ("喜鵲籬", "喜鹊篱"),
    "남부터미널": ("南部客運站", "南部客运站"),
    "노들": ("鷺得", "鹭得"),
    "녹번": ("錄番", "录番"),
    "당고개": ("堂嶺", "堂岭"),
    "대청": ("大青", "大青"),
    "독바위": ("獨岩", "独岩"),
    "돌곶이": ("石串", "石串"),
    "동묘앞": ("東廟", "东庙"),
    "디지털미디어시티": ("數字媒體城", "数字媒体城"),
    "뚝섬": ("纛島", "纛岛"),
    "뚝섬유원지": ("纛島遊園地", "纛岛游园地"),
    "마들": ("馬得", "马得"),
    "매봉": ("梅峰", "梅峰"),
    "먹골": ("墨谷", "墨谷"),
    "무악재": ("毋岳嶺", "毋岳岭"),
    "미아사거리": ("彌阿十字路口", "弥阿十字路口"),
    "버티고개": ("버티고개", "버티고개"),  # filled below with phonetic if needed
    "범계": ("梵溪", "梵溪"),
    "보라매": ("波拉美", "波拉美"),
    "샛강": ("間川", "间川"),
    "서울": ("首爾站", "首尔站"),
    "서울대입구": ("首爾大入口", "首尔大入口"),
    "선바위": ("立岩", "立岩"),
    "신대방삼거리": ("新大方三岔路口", "新大方三岔路口"),
    "신정네거리": ("新亭十字路口", "新亭十字路口"),
    "애오개": ("兒嶺", "儿岭"),
    "어린이대공원": ("兒童大公園", "儿童大公园"),
    "여의나루": ("汝矣渡口", "汝矣渡口"),
    "연신내": ("연신내", "연신내"),
    "올림픽공원": ("奧林匹克公園", "奥林匹克公园"),
    "외대앞": ("外大", "外大"),
    "월드컵경기장": ("世界盃競技場", "世界杯竞技场"),
    "잠실나루": ("蠶室渡口", "蚕室渡口"),
    "잠실새내": ("蠶室新川", "蚕室新川"),
    "장승배기": ("長承培基", "长承培基"),
    "학여울": ("鶴灘", "鹤滩"),
    "한대앞": ("漢大", "汉大"),
    "효창공원앞": ("孝昌公園", "孝昌公园"),
    "버티고개": ("버티고개", "버티고개"),
}

# Fix leftover Hangul placeholders with phonetic Chinese
ZH_OVERRIDES.update(
    {
        "버티고개": ("直立嶺", "直立岭"),
        "연신내": ("延新內", "延新内"),
    }
)

VI_OVERRIDES: dict[str, str] = {
    "강남": "Ga Gangnam",
    "명동": "Ga Myeongdong",
    "서울": "Ga Seoul",
    "홍대입구": "Ga Đại học Hongik",
    "이태원": "Ga Itaewon",
    "잠실": "Ga Jamsil",
    "경복궁": "Ga Cung Gyeongbok",
    "광화문": "Ga Gwanghwamun",
    "동대문": "Ga Dongdaemun",
    "시청": "Ga Tòa thị chính",
    "여의도": "Ga Yeouido",
    "신촌": "Ga Sinchon",
    "이대": "Ga Đại học Ewha",
    "건대입구": "Ga Đại học Konkuk",
    "서울대입구": "Ga Đại học Quốc gia Seoul",
    "고속터미널": "Ga Bến xe cao tốc",
    "남부터미널": "Ga Bến xe phía Nam",
    "인천공항1터미널": "Ga Sân bay Incheon T1",
    "인천공항2터미널": "Ga Sân bay Incheon T2",
    "김포공항": "Ga Sân bay Gimpo",
    "디지털미디어시티": "Ga Digital Media City",
    "어린이대공원": "Ga Công viên Thiếu nhi",
    "올림픽공원": "Ga Công viên Olympic",
    "월드컵경기장": "Ga Sân vận động World Cup",
}

TH_OVERRIDES: dict[str, str] = {
    "강남": "คังนัม",
    "명동": "มยองดง",
    "서울": "สถานีโซล",
    "홍대입구": "ฮงแด (มหาวิทยาลัยฮงอิค)",
    "이태원": "อีแทวอน",
    "잠실": "ชัมซิล",
    "경복궁": "พระราชวังคยองบก",
    "광화문": "ควังฮวามุน",
    "동대문": "ทงแดมุน",
    "시청": "ศาลาว่าการกรุงโซล",
    "여의도": "ยออึยโด",
    "신촌": "ชินชน",
    "이대": "มหาวิทยาลัยอีฮวา",
    "건대입구": "มหาวิทยาลัยคอนกุก",
    "서울대입구": "มหาวิทยาลัยแห่งชาติโซล",
    "고속터미널": "สถานีรถบัสทางด่วน",
    "인천공항1터미널": "สนามบินอินชอน เทอร์มินัล 1",
    "인천공항2터미널": "สนามบินอินชอน เทอร์มินัล 2",
    "김포공항": "สนามบินคิมโพ",
}

RU_OVERRIDES: dict[str, str] = {
    "강남": "Каннам",
    "명동": "Мёндон",
    "서울": "Сеульский вокзал",
    "홍대입구": "Хондайк (Хондэ)",
    "이태원": "Итхэвон",
    "잠실": "Чамсиль",
    "경복궁": "Кёнбоккун",
    "광화문": "Кванхвамун",
    "동대문": "Тондэмун",
    "시청": "Сити-холл",
    "여의도": "Ёыйдо",
    "신촌": "Синчхон",
    "이대": "Ихва",
    "건대입구": "Конкук",
    "서울대입구": "Сеульский университет",
    "고속터미널": "Автовокзал экспресс",
    "인천공항1터미널": "Аэропорт Инчхон T1",
    "인천공항2터미널": "Аэропорт Инчхон T2",
    "김포공항": "Аэропорт Кимпхо",
}

# Traditional/hanja → simplified (common metro name characters)
HAN_TO_ZH_CHARS: dict[str, str] = str.maketrans(
    {
        "國": "国",
        "廳": "厅",
        "門": "门",
        "東": "东",
        "廣": "广",
        "場": "场",
        "學": "学",
        "園": "园",
        "館": "馆",
        "會": "会",
        "議": "议",
        "醫": "医",
        "術": "术",
        "業": "业",
        "區": "区",
        "灣": "湾",
        "島": "岛",
        "巖": "岩",
        "龍": "龙",
        "鳳": "凤",
        "華": "华",
        "漢": "汉",
        "濟": "济",
        "陽": "阳",
        "陰": "阴",
        "溫": "温",
        "湯": "汤",
        "驛": "驿",
        "權": "权",
        "經": "经",
        "營": "营",
        "臺": "台",
        "與": "与",
        "興": "兴",
        "傳": "传",
        "運": "运",
        "動": "动",
        "體": "体",
        "競": "竞",
        "蠶": "蚕",
        "宮": "宫",
        "鐘": "钟",
        "曆": "历",
        "歷": "历",
        "橋": "桥",
        "際": "际",
        "爾": "尔",
        "數": "数",
        "碼": "码",
        "奧": "奥",
        "兒": "儿",
        "長": "长",
        "嶺": "岭",
        "彎": "弯",
        "鶴": "鹤",
        "灘": "滩",
        "鷺": "鹭",
        "得": "得",
        "錄": "录",
        "番": "番",
        "獨": "独",
        "遊": "游",
        "馬": "马",
        "梅": "梅",
        "墨": "墨",
        "谷": "谷",
        "毋": "毋",
        "岳": "岳",
        "彌": "弥",
        "阿": "阿",
        "梵": "梵",
        "溪": "溪",
        "間": "间",
        "川": "川",
        "立": "立",
        "岩": "岩",
        "新": "新",
        "大": "大",
        "方": "方",
        "亭": "亭",
        "十": "十",
        "字": "字",
        "路": "路",
        "口": "口",
        "三": "三",
        "岔": "岔",
        "兒": "儿",
        "童": "童",
        "林": "林",
        "匹": "匹",
        "克": "克",
        "世": "世",
        "界": "界",
        "盃": "杯",
        "技": "技",
        "場": "场",
        "孝": "孝",
        "昌": "昌",
        "公": "公",
        "直": "直",
        "延": "延",
        "內": "内",
        "渡": "渡",
        "喜": "喜",
        "鵲": "鹊",
        "山": "山",
        "籬": "篱",
        "客": "客",
        "運": "运",
        "站": "站",
        "高": "高",
        "速": "速",
        "巴": "巴",
        "士": "士",
        "數": "数",
        "碼": "码",
        "園": "园",
        "區": "区",
        "加": "加",
        "九": "九",
        "老": "老",
        "南": "南",
        "部": "部",
        "首": "首",
        "爾": "尔",
        "纛": "纛",
        "島": "岛",
        "明": "明",
        "洞": "洞",
        "江": "江",
        "南": "南",
        "弘": "弘",
        "入": "入",
        "口": "口",
        "梨": "梨",
        "梨": "梨",
        "泰": "泰",
        "院": "院",
    }
)

# ---------------------------------------------------------------------------
# Hangul helpers
# ---------------------------------------------------------------------------
CHOSEONG = [
    "ㄱ",
    "ㄲ",
    "ㄴ",
    "ㄷ",
    "ㄸ",
    "ㄹ",
    "ㅁ",
    "ㅂ",
    "ㅃ",
    "ㅅ",
    "ㅆ",
    "ㅇ",
    "ㅈ",
    "ㅉ",
    "ㅊ",
    "ㅋ",
    "ㅌ",
    "ㅍ",
    "ㅎ",
]
JUNGSEONG = [
    "ㅏ",
    "ㅐ",
    "ㅑ",
    "ㅒ",
    "ㅓ",
    "ㅔ",
    "ㅕ",
    "ㅖ",
    "ㅗ",
    "ㅘ",
    "ㅙ",
    "ㅚ",
    "ㅛ",
    "ㅜ",
    "ㅝ",
    "ㅞ",
    "ㅟ",
    "ㅠ",
    "ㅡ",
    "ㅢ",
    "ㅣ",
]
JONGSEONG = [
    "",
    "ㄱ",
    "ㄲ",
    "ㄳ",
    "ㄴ",
    "ㄵ",
    "ㄶ",
    "ㄷ",
    "ㄹ",
    "ㄺ",
    "ㄻ",
    "ㄼ",
    "ㄽ",
    "ㄾ",
    "ㄿ",
    "ㅀ",
    "ㅁ",
    "ㅂ",
    "ㅄ",
    "ㅅ",
    "ㅆ",
    "ㅇ",
    "ㅈ",
    "ㅊ",
    "ㅋ",
    "ㅌ",
    "ㅍ",
    "ㅎ",
]


def clean_name(name: str) -> str:
    n = (name or "").strip()
    if n.endswith("역") and len(n) > 1:
        n = n[:-1]
    return n.strip()


def has_hangul(s: str) -> bool:
    return any("\uac00" <= c <= "\ud7a3" for c in (s or ""))


def mostly_hanja(s: str) -> bool:
    s = (s or "").strip()
    if not s or has_hangul(s):
        return False
    return any("\u4e00" <= c <= "\u9fff" for c in s)


def decompose_hangul(ch: str) -> tuple[str, str, str] | None:
    if not ("가" <= ch <= "힣"):
        return None
    code = ord(ch) - 0xAC00
    return CHOSEONG[code // 588], JUNGSEONG[(code % 588) // 28], JONGSEONG[code % 28]


# ---------------------------------------------------------------------------
# Japanese: Hangul → Katakana (Seoul-metro style phonetic)
# ---------------------------------------------------------------------------
# Base CV table keyed by (choseong, jungseong) → katakana mora
_JA_CV: dict[tuple[str, str], str] = {}


def _fill_ja_row(cho: str, row: dict[str, str]) -> None:
    for jung, kata in row.items():
        _JA_CV[(cho, jung)] = kata


_fill_ja_row(
    "ㄱ",
    {
        "ㅏ": "カ",
        "ㅐ": "ケ",
        "ㅑ": "キャ",
        "ㅒ": "キャ",
        "ㅓ": "コ",
        "ㅔ": "ケ",
        "ㅕ": "キョ",
        "ㅖ": "ケ",
        "ㅗ": "コ",
        "ㅘ": "クァ",
        "ㅙ": "クェ",
        "ㅚ": "ケ",
        "ㅛ": "キョ",
        "ㅜ": "ク",
        "ㅝ": "クォ",
        "ㅞ": "クェ",
        "ㅟ": "クィ",
        "ㅠ": "キュ",
        "ㅡ": "ク",
        "ㅢ": "キ",
        "ㅣ": "キ",
    },
)
_fill_ja_row(
    "ㄲ",
    {
        "ㅏ": "ッカ",
        "ㅐ": "ッケ",
        "ㅑ": "ッキャ",
        "ㅒ": "ッキャ",
        "ㅓ": "ッコ",
        "ㅔ": "ッケ",
        "ㅕ": "ッキョ",
        "ㅖ": "ッケ",
        "ㅗ": "ッコ",
        "ㅘ": "ックァ",
        "ㅙ": "ックェ",
        "ㅚ": "ッケ",
        "ㅛ": "ッキョ",
        "ㅜ": "ック",
        "ㅝ": "ックォ",
        "ㅞ": "ックェ",
        "ㅟ": "ックィ",
        "ㅠ": "ッキュ",
        "ㅡ": "ック",
        "ㅢ": "ッキ",
        "ㅣ": "ッキ",
    },
)
_fill_ja_row(
    "ㄴ",
    {
        "ㅏ": "ナ",
        "ㅐ": "ネ",
        "ㅑ": "ニャ",
        "ㅒ": "ニャ",
        "ㅓ": "ノ",
        "ㅔ": "ネ",
        "ㅕ": "ニョ",
        "ㅖ": "ネ",
        "ㅗ": "ノ",
        "ㅘ": "ヌァ",
        "ㅙ": "ヌェ",
        "ㅚ": "ネ",
        "ㅛ": "ニョ",
        "ㅜ": "ヌ",
        "ㅝ": "ヌォ",
        "ㅞ": "ヌェ",
        "ㅟ": "ヌィ",
        "ㅠ": "ニュ",
        "ㅡ": "ヌ",
        "ㅢ": "ニ",
        "ㅣ": "ニ",
    },
)
_fill_ja_row(
    "ㄷ",
    {
        "ㅏ": "タ",
        "ㅐ": "テ",
        "ㅑ": "チャ",
        "ㅒ": "チャ",
        "ㅓ": "ト",
        "ㅔ": "テ",
        "ㅕ": "チョ",
        "ㅖ": "テ",
        "ㅗ": "ト",
        "ㅘ": "トゥァ",
        "ㅙ": "トゥェ",
        "ㅚ": "テ",
        "ㅛ": "チョ",
        "ㅜ": "トゥ",
        "ㅝ": "トゥォ",
        "ㅞ": "トゥェ",
        "ㅟ": "トゥィ",
        "ㅠ": "チュ",
        "ㅡ": "トゥ",
        "ㅢ": "ティ",
        "ㅣ": "ティ",
    },
)
_fill_ja_row(
    "ㄸ",
    {
        "ㅏ": "ッタ",
        "ㅐ": "ッテ",
        "ㅑ": "ッチャ",
        "ㅒ": "ッチャ",
        "ㅓ": "ット",
        "ㅔ": "ッテ",
        "ㅕ": "ッチョ",
        "ㅖ": "ッテ",
        "ㅗ": "ット",
        "ㅘ": "ットゥァ",
        "ㅙ": "ットゥェ",
        "ㅚ": "ッテ",
        "ㅛ": "ッチョ",
        "ㅜ": "ットゥ",
        "ㅝ": "ットゥォ",
        "ㅞ": "ットゥェ",
        "ㅟ": "ットゥィ",
        "ㅠ": "ッチュ",
        "ㅡ": "ットゥ",
        "ㅢ": "ッティ",
        "ㅣ": "ッティ",
    },
)
_fill_ja_row(
    "ㄹ",
    {
        "ㅏ": "ラ",
        "ㅐ": "レ",
        "ㅑ": "リャ",
        "ㅒ": "リャ",
        "ㅓ": "ロ",
        "ㅔ": "レ",
        "ㅕ": "リョ",
        "ㅖ": "レ",
        "ㅗ": "ロ",
        "ㅘ": "ルァ",
        "ㅙ": "ルェ",
        "ㅚ": "レ",
        "ㅛ": "リョ",
        "ㅜ": "ル",
        "ㅝ": "ルォ",
        "ㅞ": "ルェ",
        "ㅟ": "ルィ",
        "ㅠ": "リュ",
        "ㅡ": "ル",
        "ㅢ": "リ",
        "ㅣ": "リ",
    },
)
_fill_ja_row(
    "ㅁ",
    {
        "ㅏ": "マ",
        "ㅐ": "メ",
        "ㅑ": "ミャ",
        "ㅒ": "ミャ",
        "ㅓ": "モ",
        "ㅔ": "メ",
        "ㅕ": "ミョ",
        "ㅖ": "メ",
        "ㅗ": "モ",
        "ㅘ": "ムァ",
        "ㅙ": "ムェ",
        "ㅚ": "メ",
        "ㅛ": "ミョ",
        "ㅜ": "ム",
        "ㅝ": "ムォ",
        "ㅞ": "ムェ",
        "ㅟ": "ムィ",
        "ㅠ": "ミュ",
        "ㅡ": "ム",
        "ㅢ": "ミ",
        "ㅣ": "ミ",
    },
)
_fill_ja_row(
    "ㅂ",
    {
        "ㅏ": "パ",
        "ㅐ": "ペ",
        "ㅑ": "ピャ",
        "ㅒ": "ピャ",
        "ㅓ": "ポ",
        "ㅔ": "ペ",
        "ㅕ": "ピョ",
        "ㅖ": "ペ",
        "ㅗ": "ポ",
        "ㅘ": "プァ",
        "ㅙ": "プェ",
        "ㅚ": "ペ",
        "ㅛ": "ピョ",
        "ㅜ": "プ",
        "ㅝ": "プォ",
        "ㅞ": "プェ",
        "ㅟ": "プィ",
        "ㅠ": "ピュ",
        "ㅡ": "プ",
        "ㅢ": "ピ",
        "ㅣ": "ピ",
    },
)
_fill_ja_row(
    "ㅃ",
    {
        "ㅏ": "ッパ",
        "ㅐ": "ッペ",
        "ㅑ": "ッピャ",
        "ㅒ": "ッピャ",
        "ㅓ": "ッポ",
        "ㅔ": "ッペ",
        "ㅕ": "ッピョ",
        "ㅖ": "ッペ",
        "ㅗ": "ッポ",
        "ㅘ": "ップァ",
        "ㅙ": "ップェ",
        "ㅚ": "ッペ",
        "ㅛ": "ッピョ",
        "ㅜ": "ップ",
        "ㅝ": "ップォ",
        "ㅞ": "ップェ",
        "ㅟ": "ップィ",
        "ㅠ": "ッピュ",
        "ㅡ": "ップ",
        "ㅢ": "ッピ",
        "ㅣ": "ッピ",
    },
)
_fill_ja_row(
    "ㅅ",
    {
        "ㅏ": "サ",
        "ㅐ": "セ",
        "ㅑ": "シャ",
        "ㅒ": "シェ",
        "ㅓ": "ソ",
        "ㅔ": "セ",
        "ㅕ": "ショ",
        "ㅖ": "セ",
        "ㅗ": "ソ",
        "ㅘ": "スァ",
        "ㅙ": "スェ",
        "ㅚ": "セ",
        "ㅛ": "ショ",
        "ㅜ": "ス",
        "ㅝ": "スォ",
        "ㅞ": "スェ",
        "ㅟ": "スィ",
        "ㅠ": "シュ",
        "ㅡ": "ス",
        "ㅢ": "シ",
        "ㅣ": "シ",
    },
)
_fill_ja_row(
    "ㅆ",
    {
        "ㅏ": "ッサ",
        "ㅐ": "ッセ",
        "ㅑ": "ッシャ",
        "ㅒ": "ッシェ",
        "ㅓ": "ッソ",
        "ㅔ": "ッセ",
        "ㅕ": "ッショ",
        "ㅖ": "ッセ",
        "ㅗ": "ッソ",
        "ㅘ": "ッスァ",
        "ㅙ": "ッスェ",
        "ㅚ": "ッセ",
        "ㅛ": "ッショ",
        "ㅜ": "ッス",
        "ㅝ": "ッスォ",
        "ㅞ": "ッスェ",
        "ㅟ": "ッスィ",
        "ㅠ": "ッシュ",
        "ㅡ": "ッス",
        "ㅢ": "ッシ",
        "ㅣ": "ッシ",
    },
)
_fill_ja_row(
    "ㅇ",
    {
        "ㅏ": "ア",
        "ㅐ": "エ",
        "ㅑ": "ヤ",
        "ㅒ": "イェ",
        "ㅓ": "オ",
        "ㅔ": "エ",
        "ㅕ": "ヨ",
        "ㅖ": "イェ",
        "ㅗ": "オ",
        "ㅘ": "ワ",
        "ㅙ": "ウェ",
        "ㅚ": "ウェ",
        "ㅛ": "ヨ",
        "ㅜ": "ウ",
        "ㅝ": "ウォ",
        "ㅞ": "ウェ",
        "ㅟ": "ウィ",
        "ㅠ": "ユ",
        "ㅡ": "ウ",
        "ㅢ": "ウィ",
        "ㅣ": "イ",
    },
)
_fill_ja_row(
    "ㅈ",
    {
        "ㅏ": "チャ",
        "ㅐ": "チェ",
        "ㅑ": "チャ",
        "ㅒ": "チェ",
        "ㅓ": "チョ",
        "ㅔ": "チェ",
        "ㅕ": "チョ",
        "ㅖ": "チェ",
        "ㅗ": "チョ",
        "ㅘ": "チュァ",
        "ㅙ": "チュェ",
        "ㅚ": "チェ",
        "ㅛ": "チョ",
        "ㅜ": "チュ",
        "ㅝ": "チュォ",
        "ㅞ": "チュェ",
        "ㅟ": "チュィ",
        "ㅠ": "チュ",
        "ㅡ": "チュ",
        "ㅢ": "チ",
        "ㅣ": "チ",
    },
)
_fill_ja_row(
    "ㅉ",
    {
        "ㅏ": "ッチャ",
        "ㅐ": "ッチェ",
        "ㅑ": "ッチャ",
        "ㅒ": "ッチェ",
        "ㅓ": "ッチョ",
        "ㅔ": "ッチェ",
        "ㅕ": "ッチョ",
        "ㅖ": "ッチェ",
        "ㅗ": "ッチョ",
        "ㅘ": "ッチュァ",
        "ㅙ": "ッチュェ",
        "ㅚ": "ッチェ",
        "ㅛ": "ッチョ",
        "ㅜ": "ッチュ",
        "ㅝ": "ッチュォ",
        "ㅞ": "ッチュェ",
        "ㅟ": "ッチュィ",
        "ㅠ": "ッチュ",
        "ㅡ": "ッチュ",
        "ㅢ": "ッチ",
        "ㅣ": "ッチ",
    },
)
_fill_ja_row(
    "ㅊ",
    {
        "ㅏ": "チャ",
        "ㅐ": "チェ",
        "ㅑ": "チャ",
        "ㅒ": "チェ",
        "ㅓ": "チョ",
        "ㅔ": "チェ",
        "ㅕ": "チョ",
        "ㅖ": "チェ",
        "ㅗ": "チョ",
        "ㅘ": "チュァ",
        "ㅙ": "チュェ",
        "ㅚ": "チェ",
        "ㅛ": "チョ",
        "ㅜ": "チュ",
        "ㅝ": "チュォ",
        "ㅞ": "チュェ",
        "ㅟ": "チュィ",
        "ㅠ": "チュ",
        "ㅡ": "チュ",
        "ㅢ": "チ",
        "ㅣ": "チ",
    },
)
_fill_ja_row(
    "ㅋ",
    {
        "ㅏ": "カ",
        "ㅐ": "ケ",
        "ㅑ": "キャ",
        "ㅒ": "キャ",
        "ㅓ": "コ",
        "ㅔ": "ケ",
        "ㅕ": "キョ",
        "ㅖ": "ケ",
        "ㅗ": "コ",
        "ㅘ": "クァ",
        "ㅙ": "クェ",
        "ㅚ": "ケ",
        "ㅛ": "キョ",
        "ㅜ": "ク",
        "ㅝ": "クォ",
        "ㅞ": "クェ",
        "ㅟ": "クィ",
        "ㅠ": "キュ",
        "ㅡ": "ク",
        "ㅢ": "キ",
        "ㅣ": "キ",
    },
)
_fill_ja_row(
    "ㅌ",
    {
        "ㅏ": "タ",
        "ㅐ": "テ",
        "ㅑ": "チャ",
        "ㅒ": "チャ",
        "ㅓ": "ト",
        "ㅔ": "テ",
        "ㅕ": "チョ",
        "ㅖ": "テ",
        "ㅗ": "ト",
        "ㅘ": "トゥァ",
        "ㅙ": "トゥェ",
        "ㅚ": "テ",
        "ㅛ": "チョ",
        "ㅜ": "トゥ",
        "ㅝ": "トゥォ",
        "ㅞ": "トゥェ",
        "ㅟ": "トゥィ",
        "ㅠ": "チュ",
        "ㅡ": "トゥ",
        "ㅢ": "ティ",
        "ㅣ": "ティ",
    },
)
_fill_ja_row(
    "ㅍ",
    {
        "ㅏ": "パ",
        "ㅐ": "ペ",
        "ㅑ": "ピャ",
        "ㅒ": "ピャ",
        "ㅓ": "ポ",
        "ㅔ": "ペ",
        "ㅕ": "ピョ",
        "ㅖ": "ペ",
        "ㅗ": "ポ",
        "ㅘ": "プァ",
        "ㅙ": "プェ",
        "ㅚ": "ペ",
        "ㅛ": "ピョ",
        "ㅜ": "プ",
        "ㅝ": "プォ",
        "ㅞ": "プェ",
        "ㅟ": "プィ",
        "ㅠ": "ピュ",
        "ㅡ": "プ",
        "ㅢ": "ピ",
        "ㅣ": "ピ",
    },
)
_fill_ja_row(
    "ㅎ",
    {
        "ㅏ": "ハ",
        "ㅐ": "ヘ",
        "ㅑ": "ヒャ",
        "ㅒ": "ヒャ",
        "ㅓ": "ホ",
        "ㅔ": "ヘ",
        "ㅕ": "ヒョ",
        "ㅖ": "ヘ",
        "ㅗ": "ホ",
        "ㅘ": "ファ",
        "ㅙ": "フェ",
        "ㅚ": "ヘ",
        "ㅛ": "ヒョ",
        "ㅜ": "フ",
        "ㅝ": "フォ",
        "ㅞ": "フェ",
        "ㅟ": "フィ",
        "ㅠ": "ヒュ",
        "ㅡ": "フ",
        "ㅢ": "ヒ",
        "ㅣ": "ヒ",
    },
)

_JA_BATCHIM = {
    "ㄱ": "ク",
    "ㄲ": "ク",
    "ㄳ": "ク",
    "ㄴ": "ン",
    "ㄵ": "ン",
    "ㄶ": "ン",
    "ㄷ": "ト",
    "ㄹ": "ル",
    "ㄺ": "ク",
    "ㄻ": "ム",
    "ㄼ": "ル",
    "ㄽ": "ル",
    "ㄾ": "ル",
    "ㄿ": "ル",
    "ㅀ": "ル",
    "ㅁ": "ム",
    "ㅂ": "プ",
    "ㅄ": "プ",
    "ㅅ": "ト",
    "ㅆ": "ト",
    "ㅇ": "ン",
    "ㅈ": "チ",
    "ㅊ": "チ",
    "ㅋ": "ク",
    "ㅌ": "ト",
    "ㅍ": "プ",
    "ㅎ": "",
}


def hangul_to_katakana(text: str) -> str:
    out: list[str] = []
    for ch in text or "":
        parts = decompose_hangul(ch)
        if not parts:
            if ch.isdigit() or ch in "()-·/ ":
                out.append(ch)
            elif ch == "대":
                out.append("デ")
            else:
                # Latin fragments inside Korean names
                out.append(ch)
            continue
        cho, jung, jong = parts
        base = _JA_CV.get((cho, jung))
        if not base:
            continue
        out.append(base)
        if jong:
            out.append(_JA_BATCHIM.get(jong, ""))
    s = "".join(out)
    # Soften leading ッ (double consonant at start)
    while s.startswith("ッ"):
        s = s[1:]
    return s


# ---------------------------------------------------------------------------
# Russian: Hangul → Cyrillic (Kontsevich-inspired)
# ---------------------------------------------------------------------------
_RU_CV: dict[tuple[str, str], str] = {}


def _fill_ru_row(cho: str, row: dict[str, str]) -> None:
    for jung, cyr in row.items():
        _RU_CV[(cho, jung)] = cyr


def _ru_vowels(base_cons: str, soft_cons: str | None = None) -> dict[str, str]:
    soft = soft_cons or base_cons
    return {
        "ㅏ": base_cons + "а",
        "ㅐ": base_cons + "э",
        "ㅑ": soft + "я",
        "ㅒ": soft + "я",
        "ㅓ": base_cons + "о",
        "ㅔ": base_cons + "е",
        "ㅕ": soft + "ё",
        "ㅖ": soft + "е",
        "ㅗ": base_cons + "о",
        "ㅘ": base_cons + "ва",
        "ㅙ": base_cons + "вэ",
        "ㅚ": base_cons + "ве",
        "ㅛ": soft + "ё",
        "ㅜ": base_cons + "у",
        "ㅝ": base_cons + "во",
        "ㅞ": base_cons + "ве",
        "ㅟ": base_cons + "ви",
        "ㅠ": soft + "ю",
        "ㅡ": base_cons + "ы",
        "ㅢ": soft + "и",
        "ㅣ": soft + "и",
    }


_fill_ru_row("ㄱ", _ru_vowels("к", "к"))
_fill_ru_row("ㄲ", _ru_vowels("кк", "кк"))
_fill_ru_row("ㄴ", _ru_vowels("н", "н"))
_fill_ru_row("ㄷ", _ru_vowels("т", "т"))
_fill_ru_row("ㄸ", _ru_vowels("тт", "тт"))
_fill_ru_row("ㄹ", _ru_vowels("р", "р"))
_fill_ru_row("ㅁ", _ru_vowels("м", "м"))
_fill_ru_row("ㅂ", _ru_vowels("п", "п"))
_fill_ru_row("ㅃ", _ru_vowels("пп", "пп"))
_fill_ru_row("ㅅ", _ru_vowels("с", "с"))
_fill_ru_row("ㅆ", _ru_vowels("сс", "сс"))
_fill_ru_row(
    "ㅇ",
    {
        "ㅏ": "а",
        "ㅐ": "э",
        "ㅑ": "я",
        "ㅒ": "я",
        "ㅓ": "о",
        "ㅔ": "е",
        "ㅕ": "ё",
        "ㅖ": "е",
        "ㅗ": "о",
        "ㅘ": "ва",
        "ㅙ": "вэ",
        "ㅚ": "ве",
        "ㅛ": "ё",
        "ㅜ": "у",
        "ㅝ": "во",
        "ㅞ": "ве",
        "ㅟ": "ви",
        "ㅠ": "ю",
        "ㅡ": "ы",
        "ㅢ": "и",
        "ㅣ": "и",
    },
)
_fill_ru_row("ㅈ", _ru_vowels("ч", "ч"))
_fill_ru_row("ㅉ", _ru_vowels("чч", "чч"))
_fill_ru_row("ㅊ", _ru_vowels("чх", "чх"))
_fill_ru_row("ㅋ", _ru_vowels("кх", "кх"))
_fill_ru_row("ㅌ", _ru_vowels("тх", "тх"))
_fill_ru_row("ㅍ", _ru_vowels("пх", "пх"))
_fill_ru_row("ㅎ", _ru_vowels("х", "х"))

_RU_BATCHIM = {
    "ㄱ": "к",
    "ㄲ": "к",
    "ㄳ": "к",
    "ㄴ": "н",
    "ㄵ": "н",
    "ㄶ": "н",
    "ㄷ": "т",
    "ㄹ": "ль",
    "ㄺ": "к",
    "ㄻ": "м",
    "ㄼ": "ль",
    "ㄽ": "ль",
    "ㄾ": "ль",
    "ㄿ": "ль",
    "ㅀ": "ль",
    "ㅁ": "м",
    "ㅂ": "п",
    "ㅄ": "п",
    "ㅅ": "т",
    "ㅆ": "т",
    "ㅇ": "н",
    "ㅈ": "т",
    "ㅊ": "т",
    "ㅋ": "к",
    "ㅌ": "т",
    "ㅍ": "п",
    "ㅎ": "",
}


def hangul_to_cyrillic(text: str) -> str:
    out: list[str] = []
    for ch in text or "":
        parts = decompose_hangul(ch)
        if not parts:
            if ch.isdigit() or ch in "()-·/ ":
                out.append(ch)
            continue
        cho, jung, jong = parts
        base = _RU_CV.get((cho, jung))
        if not base:
            continue
        out.append(base)
        if jong:
            out.append(_RU_BATCHIM.get(jong, ""))
    s = "".join(out)
    if s:
        s = s[0].upper() + s[1:]
    return s


# ---------------------------------------------------------------------------
# Thai: Hangul → phonetic Thai (tourist-map style)
# ---------------------------------------------------------------------------
_TH_CV: dict[tuple[str, str], str] = {}


def _fill_th_row(cho: str, row: dict[str, str]) -> None:
    for jung, th in row.items():
        _TH_CV[(cho, jung)] = th


def _th_row(c: str, soft: str | None = None) -> dict[str, str]:
    s = soft or c
    return {
        "ㅏ": c + "า",
        "ㅐ": c + "แ",
        "ㅑ": s + "ยา",
        "ㅒ": s + "แย",
        "ㅓ": c + "อ",
        "ㅔ": c + "เ",
        "ㅕ": s + "ยอ",
        "ㅖ": s + "เย",
        "ㅗ": c + "อ",
        "ㅘ": c + "วา",
        "ㅙ": c + "แว",
        "ㅚ": c + "เว",
        "ㅛ": s + "โย",
        "ㅜ": c + "ู",
        "ㅝ": c + "วอ",
        "ㅞ": c + "เว",
        "ㅟ": c + "วี",
        "ㅠ": s + "ยู",
        "ㅡ": c + "ึ",
        "ㅢ": s + "ี",
        "ㅣ": s + "ี",
    }


_fill_th_row("ㄱ", _th_row("ก", "ก"))
_fill_th_row("ㄲ", _th_row("ก", "ก"))
_fill_th_row("ㄴ", _th_row("น", "น"))
_fill_th_row("ㄷ", _th_row("ต", "ต"))
_fill_th_row("ㄸ", _th_row("ต", "ต"))
_fill_th_row("ㄹ", _th_row("ร", "ร"))
_fill_th_row("ㅁ", _th_row("ม", "ม"))
_fill_th_row("ㅂ", _th_row("ป", "ป"))
_fill_th_row("ㅃ", _th_row("ป", "ป"))
_fill_th_row("ㅅ", _th_row("ซ", "ซ"))
_fill_th_row("ㅆ", _th_row("ซ", "ซ"))
_fill_th_row(
    "ㅇ",
    {
        "ㅏ": "อา",
        "ㅐ": "แอ",
        "ㅑ": "ยา",
        "ㅒ": "แย",
        "ㅓ": "ออ",
        "ㅔ": "เอ",
        "ㅕ": "ยอ",
        "ㅖ": "เย",
        "ㅗ": "โอ",
        "ㅘ": "วา",
        "ㅙ": "แว",
        "ㅚ": "เว",
        "ㅛ": "โย",
        "ㅜ": "อู",
        "ㅝ": "วอ",
        "ㅞ": "เว",
        "ㅟ": "วี",
        "ㅠ": "ยู",
        "ㅡ": "อึ",
        "ㅢ": "อี",
        "ㅣ": "อี",
    },
)
_fill_th_row("ㅈ", _th_row("จ", "จ"))
_fill_th_row("ㅉ", _th_row("จ", "จ"))
_fill_th_row("ㅊ", _th_row("ช", "ช"))
_fill_th_row("ㅋ", _th_row("ค", "ค"))
_fill_th_row("ㅌ", _th_row("ท", "ท"))
_fill_th_row("ㅍ", _th_row("พ", "พ"))
_fill_th_row("ㅎ", _th_row("ฮ", "ฮ"))

_TH_BATCHIM = {
    "ㄱ": "ก",
    "ㄲ": "ก",
    "ㄳ": "ก",
    "ㄴ": "น",
    "ㄵ": "น",
    "ㄶ": "น",
    "ㄷ": "ด",
    "ㄹ": "ล",
    "ㄺ": "ก",
    "ㄻ": "ม",
    "ㄼ": "ล",
    "ㄽ": "ล",
    "ㄾ": "ล",
    "ㄿ": "ล",
    "ㅀ": "ล",
    "ㅁ": "ม",
    "ㅂ": "บ",
    "ㅄ": "บ",
    "ㅅ": "ด",
    "ㅆ": "ด",
    "ㅇ": "ง",
    "ㅈ": "ด",
    "ㅊ": "ด",
    "ㅋ": "ก",
    "ㅌ": "ด",
    "ㅍ": "บ",
    "ㅎ": "",
}


def hangul_to_thai(text: str) -> str:
    out: list[str] = []
    for ch in text or "":
        parts = decompose_hangul(ch)
        if not parts:
            if ch.isdigit() or ch in "()-·/ ":
                out.append(ch)
            continue
        cho, jung, jong = parts
        base = _TH_CV.get((cho, jung))
        if not base:
            continue
        # Fix Thai vowel order: leading เ/แ markers should be before consonant
        if base.startswith(("เ", "แ")) and len(base) > 1:
            # already ok for ㅇ rows; for cons+เ form stored as คเ → reorder
            pass
        # Our table stores cons+vowel glyph awkwardly for ㅔ/ㅐ; normalize:
        if len(base) >= 2 and base[-1] in "เแ" and base[0] not in "เแ":
            base = base[-1] + base[:-1]
        out.append(base)
        if jong:
            out.append(_TH_BATCHIM.get(jong, ""))
    return "".join(out)


# ---------------------------------------------------------------------------
# Vietnamese labels
# ---------------------------------------------------------------------------
_VI_TERM_SUBS = [
    (r"\bUniv\.?\b", "Đại học"),
    (r"\bUniversity\b", "Đại học"),
    (r"\bStation\b", ""),
    (r"\bPark\b", "Công viên"),
    (r"\bAirport\b", "Sân bay"),
    (r"\bTerminal\b", "Bến"),
    (r"\bGovernment Complex\b", "Trung tâm hành chính"),
    (r"\bChildren's Grand Park\b", "Công viên Thiếu nhi"),
    (r"\bDigital Media City\b", "Digital Media City"),
    (r"\bWorld Cup Stadium\b", "Sân vận động World Cup"),
]


def make_vi_label(name_ko: str, name_en: str) -> str:
    if name_ko in VI_OVERRIDES:
        return VI_OVERRIDES[name_ko]
    en = (name_en or "").strip() or name_ko
    for pat, rep in _VI_TERM_SUBS:
        en = re.sub(pat, rep, en, flags=re.I)
    en = re.sub(r"\s{2,}", " ", en).strip(" ,.-")
    if not en:
        en = name_ko
    if en.lower().startswith("ga "):
        return en
    return f"Ga {en}"


def make_th_label(name_ko: str) -> str:
    if name_ko in TH_OVERRIDES:
        return TH_OVERRIDES[name_ko]
    return hangul_to_thai(name_ko) or name_ko


def make_ru_label(name_ko: str) -> str:
    if name_ko in RU_OVERRIDES:
        return RU_OVERRIDES[name_ko]
    return hangul_to_cyrillic(name_ko) or name_ko


def make_ja_label(name_ko: str) -> str:
    if name_ko in JA_OVERRIDES:
        return JA_OVERRIDES[name_ko]
    # Strip parenthetical for phonetic core, keep structure
    core = re.sub(r"\([^)]*\)", "", name_ko).strip()
    kata = hangul_to_katakana(core)
    # Restore simple (이수) style if present
    m = re.search(r"\(([^)]+)\)", name_ko)
    if m and kata:
        inner = hangul_to_katakana(m.group(1))
        if inner:
            kata = f"{kata}({inner})"
    return kata


def han_to_zh(han: str) -> str:
    if not mostly_hanja(han) and not any("\u4e00" <= c <= "\u9fff" for c in han):
        return ""
    # Normalize compatibility ideographs then simplify
    s = han.replace("\uf962", "梨").replace("梨", "梨")
    return s.translate(HAN_TO_ZH_CHARS)


def resolve_zh(name_ko: str, name_han: str) -> tuple[str, str]:
    """Return (traditional, simplified)."""
    if name_ko in ZH_OVERRIDES:
        trad, simp = ZH_OVERRIDES[name_ko]
        if has_hangul(trad) or has_hangul(simp):
            pass  # fall through if placeholder
        else:
            return trad, simp
    han = name_han if mostly_hanja(name_han) else ""
    if han:
        # Normalize odd compatibility chars
        han = han.replace("\uf962", "梨").replace("梨", "梨")
        return han, han_to_zh(han) or han
    # Last resort: leave empty (should be rare after overrides)
    return "", ""


def load_vertices() -> list[dict]:
    if CACHE.exists() and CACHE.stat().st_size > 1000:
        raw = CACHE.read_bytes()
    else:
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(
            SOURCE_URL, headers={"User-Agent": "KoreaTravelGuidebook/1.0"}
        )
        with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
            raw = r.read()
        CACHE.write_bytes(raw)
    data = json.loads(raw.decode("utf-8-sig"))
    return data.get("DATA") or data


def load_curated_majors() -> dict[str, dict]:
    """name -> curated coords / labels for tourist majors."""
    out: dict[str, dict] = {}
    if not CURATED_PATH.exists():
        return out
    try:
        fc = json.loads(CURATED_PATH.read_text(encoding="utf-8"))
    except Exception:
        return out
    for f in fc.get("features") or []:
        props = f.get("properties") or {}
        name = clean_name(props.get("name") or "")
        coords = (f.get("geometry") or {}).get("coordinates") or []
        if not name or len(coords) < 2:
            continue
        if props.get("source") == "curated" or props.get("major") is True:
            out[name] = {
                "lon": float(coords[0]),
                "lat": float(coords[1]),
                "name_en": (props.get("name_en") or "").strip(),
            }
    return out


def normalize_en(name_ko: str, name_en: str) -> str:
    if name_ko in EN_OVERRIDES:
        return EN_OVERRIDES[name_ko]
    en = (name_en or "").strip()
    if not en or en == name_ko or has_hangul(en):
        return EN_OVERRIDES.get(name_ko, "")
    if en == en.lower() and " " not in en and re.fullmatch(r"[a-z][a-z\-']*", en):
        return en[:1].upper() + en[1:]
    en = re.sub(r"\s{2,}", " ", en)
    en = en.replace(" station", "").replace(" Station", "")
    if en.endswith(" station"):
        en = en[: -len(" station")]
    return en.strip()


def usable_en(en: str, ko: str) -> bool:
    en = (en or "").strip()
    return bool(en) and en != ko and not has_hangul(en)


def build() -> dict:
    rows = load_vertices()
    curated = load_curated_majors()
    buckets: dict[str, dict] = {}

    for r in rows:
        if r.get("identifier") and r.get("identifier") != "CURRENT":
            continue
        line = LINE_MAP.get(str(r.get("line_num") or "").strip())
        if not line:
            continue
        name = clean_name(r.get("station_nm") or "")
        name_en = (r.get("station_nm_eng") or "").strip()
        name_han = (r.get("station_nm_han") or "").strip()
        lat = r.get("xpoint_wgs")
        lon = r.get("ypoint_wgs")
        if not name or lat is None or lon is None:
            continue
        lat = float(lat)
        lon = float(lon)
        if not (126.0 < lon < 128.0 and 36.5 < lat < 38.5):
            continue

        if name not in buckets:
            buckets[name] = {
                "name": name,
                "name_en": name_en,
                "name_han": name_han if mostly_hanja(name_han) else "",
                "lines": set(),
                "lon": lon,
                "lat": lat,
                "n": 0,
            }
        b = buckets[name]
        b["lines"].add(line)
        b["lon"] = (b["lon"] * b["n"] + lon) / (b["n"] + 1)
        b["lat"] = (b["lat"] * b["n"] + lat) / (b["n"] + 1)
        b["n"] += 1
        if name_en and (not b["name_en"] or len(name_en) > len(b["name_en"])):
            b["name_en"] = name_en
        if mostly_hanja(name_han) and (
            not b["name_han"] or len(name_han) > len(b["name_han"])
        ):
            b["name_han"] = name_han

    # Merge Sillim Line extras (new stations + line tag on existing transfers).
    for name, (lon, lat, en) in SILLIM_EXTRA.items():
        if name not in buckets:
            buckets[name] = {
                "name": name,
                "name_en": en,
                "name_han": "",
                "lines": {"sillim"},
                "lon": lon,
                "lat": lat,
                "n": 1,
            }
        else:
            b = buckets[name]
            b["lines"].add("sillim")
            if en and not usable_en(normalize_en(name, b["name_en"]), name):
                b["name_en"] = en

    features = []
    for name, b in buckets.items():
        lines = sorted(
            b["lines"],
            key=lambda x: (LINE_SORT_KEY.get(x, 99), x),
        )
        lon, lat = b["lon"], b["lat"]
        name_en = normalize_en(name, b["name_en"])
        name_han_src = b["name_han"] if mostly_hanja(b["name_han"]) else ""
        source = "koreametro"
        major = len(lines) > 1

        if name in curated:
            lon = curated[name]["lon"]
            lat = curated[name]["lat"]
            curated_en = curated[name].get("name_en") or ""
            if usable_en(curated_en, name):
                name_en = curated_en
            source = "curated"
            major = True

        if not usable_en(name_en, name):
            name_en = EN_OVERRIDES.get(name, name_en if usable_en(name_en, name) else "")

        name_han, name_zh = resolve_zh(name, name_han_src)
        name_ja = make_ja_label(name)
        name_vi = make_vi_label(name, name_en)
        name_th = make_th_label(name)
        name_ru = make_ru_label(name)

        props = {
            "name": name,
            "name_en": name_en or "",
            "name_han": name_han or "",
            "name_zh": name_zh or name_han or "",
            "name_ja": name_ja or "",
            "name_vi": name_vi or "",
            "name_th": name_th or "",
            "name_ru": name_ru or "",
            "lines": ",".join(lines),
            "source": source,
            "major": major,
        }
        features.append(
            {
                "type": "Feature",
                "properties": props,
                "geometry": {
                    "type": "Point",
                    "coordinates": [round(lon, 6), round(lat, 6)],
                },
            }
        )

    features.sort(key=lambda f: (f["properties"]["name"], f["properties"]["lines"]))
    unnamed = [f for f in features if not f["properties"]["name"]]
    if unnamed:
        raise SystemExit(f"{len(unnamed)} unnamed stations")

    return {
        "type": "FeatureCollection",
        "properties": {
            "generated": "KoreaMetroData vertices.min.json (Seoul open data coords)",
            "source": "https://github.com/ledyx/KoreaMetroData",
            "source_detail": (
                "vertices.min.json line_num 1-9,A(AREX),K,B/SU,S + Sillim OSM extras; "
                "name_en/han + curated + generated ja/zh/vi/th/ru"
            ),
            "count": len(features),
            "lines": "1,2,3,4,5,6,7,8,9,arex,gyeongui,suin-bundang,shinbundang,sillim",
        },
        "features": features,
    }


def main() -> None:
    fc = build()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    text = json.dumps(fc, ensure_ascii=False, separators=(",", ":"))
    OUT_GEO.write_text(text, encoding="utf-8")
    OUT_JS.write_text("window.METRO_STATION_DATA=" + text + ";\n", encoding="utf-8")
    _safe_print(f"Wrote {fc['properties']['count']} named stations")
    by_line: dict[str, int] = defaultdict(int)
    counts = {k: 0 for k in ("en", "ja", "han", "zh", "vi", "th", "ru")}
    bad_en = []
    missing = defaultdict(list)
    for f in fc["features"]:
        p = f["properties"]
        if usable_en(p.get("name_en") or "", p["name"]):
            counts["en"] += 1
        else:
            bad_en.append(p["name"])
        for key, field in (
            ("ja", "name_ja"),
            ("han", "name_han"),
            ("zh", "name_zh"),
            ("vi", "name_vi"),
            ("th", "name_th"),
            ("ru", "name_ru"),
        ):
            if p.get(field):
                counts[key] += 1
            else:
                missing[key].append(p["name"])
        for ln in p["lines"].split(","):
            by_line[ln] += 1
    _safe_print("coverage:", counts)
    if bad_en:
        _safe_print("missing/bad en:", bad_en)
    for k, names in missing.items():
        if names:
            _safe_print(f"missing {k} ({len(names)}):", names[:20])
    _safe_print("per-line counts:", dict(sorted(by_line.items())))
    _safe_print("majors:", sum(1 for f in fc["features"] if f["properties"].get("major")))
    # Sample proof
    for want in ("강남", "명동", "서울", "홍대입구"):
        for f in fc["features"]:
            if f["properties"]["name"] == want:
                p = f["properties"]
                _safe_print(
                    want,
                    {
                        "ko": p["name"],
                        "en": p["name_en"],
                        "ja": p["name_ja"],
                        "zh": p["name_zh"],
                        "han": p["name_han"],
                        "vi": p["name_vi"],
                        "th": p["name_th"],
                        "ru": p["name_ru"],
                    },
                )
                break


if __name__ == "__main__":
    main()
