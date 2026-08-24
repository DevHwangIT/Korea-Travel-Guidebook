# -*- coding: utf-8 -*-
"""Add region filter i18n keys under common.*"""
from __future__ import annotations

import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from lib import i18n_store  # noqa: E402

KEYS = {
    "ko": {
        "regionTabAll": "전체",
        "regionTabSudo": "수도권",
        "regionTabGangwon": "강원권",
        "regionTabChungcheong": "충청권",
        "regionTabJeolla": "전라권",
        "regionTabGyeongsang": "경상권",
        "regionTabJeju": "제주권",
        "regionFilterEmpty": "이 권역에 등록된 가게가 없습니다.",
    },
    "en": {
        "regionTabAll": "All",
        "regionTabSudo": "Seoul metro",
        "regionTabGangwon": "Gangwon",
        "regionTabChungcheong": "Chungcheong",
        "regionTabJeolla": "Jeolla",
        "regionTabGyeongsang": "Gyeongsang",
        "regionTabJeju": "Jeju",
        "regionFilterEmpty": "No shops listed in this region yet.",
    },
    "ja": {
        "regionTabAll": "すべて",
        "regionTabSudo": "首都圏",
        "regionTabGangwon": "江原",
        "regionTabChungcheong": "忠清",
        "regionTabJeolla": "全羅",
        "regionTabGyeongsang": "慶尚",
        "regionTabJeju": "済州",
        "regionFilterEmpty": "この地域の店舗はまだありません。",
    },
    "zh": {
        "regionTabAll": "全部",
        "regionTabSudo": "首都圈",
        "regionTabGangwon": "江原",
        "regionTabChungcheong": "忠清",
        "regionTabJeolla": "全罗",
        "regionTabGyeongsang": "庆尚",
        "regionTabJeju": "济州",
        "regionFilterEmpty": "该地区暂无店铺。",
    },
    "zh-Hant": {
        "regionTabAll": "全部",
        "regionTabSudo": "首都圈",
        "regionTabGangwon": "江原",
        "regionTabChungcheong": "忠清",
        "regionTabJeolla": "全羅",
        "regionTabGyeongsang": "慶尚",
        "regionTabJeju": "濟州",
        "regionFilterEmpty": "此地區尚無店家。",
    },
    "vi": {
        "regionTabAll": "Tất cả",
        "regionTabSudo": "Vùng thủ đô",
        "regionTabGangwon": "Gangwon",
        "regionTabChungcheong": "Chungcheong",
        "regionTabJeolla": "Jeolla",
        "regionTabGyeongsang": "Gyeongsang",
        "regionTabJeju": "Jeju",
        "regionFilterEmpty": "Chưa có quán trong khu vực này.",
    },
    "th": {
        "regionTabAll": "ทั้งหมด",
        "regionTabSudo": "กรุงโซลและปริมณฑล",
        "regionTabGangwon": "คังวอน",
        "regionTabChungcheong": "ชุงชอง",
        "regionTabJeolla": "ชอลลา",
        "regionTabGyeongsang": "คยองซัง",
        "regionTabJeju": "เชจู",
        "regionFilterEmpty": "ยังไม่มีร้านในภูมิภาคนี้",
    },
    "ru": {
        "regionTabAll": "Все",
        "regionTabSudo": "Столичный регион",
        "regionTabGangwon": "Канвон",
        "regionTabChungcheong": "Чхунчхон",
        "regionTabJeolla": "Чолла",
        "regionTabGyeongsang": "Кёнсан",
        "regionTabJeju": "Чеджу",
        "regionFilterEmpty": "В этом регионе пока нет заведений.",
    },
}


def main() -> None:
    bundle = i18n_store.load_all()
    for lang, keys in KEYS.items():
        common = bundle[lang].setdefault("common", {})
        for k, v in keys.items():
            common[k] = v
    i18n_store.save_all(bundle)
    print(i18n_store.build_bundle())


if __name__ == "__main__":
    main()
