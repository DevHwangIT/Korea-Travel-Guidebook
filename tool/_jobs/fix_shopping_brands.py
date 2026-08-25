# -*- coding: utf-8 -*-
"""Align souvenir copy with downloaded product photos."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tool"
sys.path.insert(0, str(TOOL))
from lib.content import _write_text_retry  # noqa: E402

SHOP = ROOT / "i18n" / "pages" / "shopping"
LANGS = ("ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru")

FLAT = {
    "ko": {
        "mallangCowDesc": "롯데 말랑카우 — 말랑한 캐러멜 캔디.",
        "mallangCowBody1": "말랑카우는 롯데의 말랑한 캐러멜 캔디입니다. 작아서 가방에 넣기 쉽고, 한국 과자 선물 묶음에 자주 들어갑니다.",
        "gosomiDesc": "오리온 고소미 — 참깨 고소한 크래커.",
        "gosomiBody1": "고소미는 오리온의 참깨 풍미 크래커입니다. 에이스·예감과 함께 한국 과자 세트로 사 가기 좋은 스테디셀러입니다.",
        "ahriCupRamenDesc": "AHRI(패키지 표기 ARIH) 컵라면 — 아리 모던 누들.",
        "ahriCupRamenBody1": "AHRI 컵라면은 패키지에 ARIH·아리로 적힌 모던 누들 컵라면입니다. 색이 다른 맛 여러 종이 있어 기념품으로 사 가기 좋습니다. 편의점·온라인에서 재고가 들쭉날쭉합니다.",
        "chaltteokDameunPieDesc": "속에 찰떡이 들어간 파이·쿠키 — 마트 과자 코너 인기 품목.",
        "chaltteokDameunPieBody1": "찰떡 담은파이는 청우(CW) 초코파이 찰떡·찰떡쿠키, 롯데 찰떡파이처럼 속에 찰떡이 들어간 파이·쿠키를 말합니다. 편의점·마트 상온 과자 코너에서 쉽게 찾습니다.",
        "chaltteokDameunPieBody2": "박스 포장이라 깨지지 않게 옷 사이에 넣으세요. 대형마트 묶음이 공항보다 저렴합니다.",
        "chaltteokDameunPieTip": "구매 팁\n\n롯데 찰떡파이와 청우 찰떡 쿠키를 헷갈리지 말고, 유통기한을 확인하세요.",
    },
    "en": {
        "mallangCowDesc": "Lotte Mallang Cow — a soft caramel chewy candy.",
        "mallangCowBody1": "Mallang Cow is Lotte’s soft caramel candy. Small and easy to pack, it often shows up in Korean snack gift piles.",
        "gosomiDesc": "Orion Gosomi — a sesame-savory cracker.",
        "gosomiBody1": "Gosomi is Orion’s sesame-flavored cracker. A steady seller to pack with Ace and Yegam in a Korean snack set.",
        "ahriCupRamenDesc": "AHRI cup ramen (packaged as ARIH) — Ari Modern Noodle.",
        "ahriCupRamenBody1": "AHRI cup ramen is labeled ARIH / Ari Modern Noodle on the cup. Several color-coded flavors make a fun souvenir set. Stock jumps around at convenience stores and online.",
        "chaltteokDameunPieDesc": "Chaltteok-filled pies and cookies — a mart snack-aisle favorite.",
        "chaltteokDameunPieBody1": "Chaltteok-Dameun Pie covers chewy rice-cake pies and cookies such as CW Choco Pie Chaltteok, CW Chaltteok Cookie, and Lotte Chaltteok Pie. Find them in convenience-store and mart snack aisles.",
        "chaltteokDameunPieBody2": "Boxes crush easily — pack between clothes. Hypermarket multipacks beat airport prices.",
        "chaltteokDameunPieTip": "Buying tip\n\nDon’t mix up Lotte Chaltteok Pie and CW chaltteok cookies; check the expiry date.",
    },
    "ja": {
        "mallangCowDesc": "ロッテの柔らかいキャラメルキャンディ。",
        "mallangCowBody1": "Mallang Cow is Lotte’s soft caramel candy. Small and easy to pack, it often shows up in Korean snack gift piles.",
        "gosomiDesc": "オリオン・ゴソミ。ごま風味クラッカー。",
        "gosomiBody1": "Gosomi is Orion’s sesame-flavored cracker. A steady seller to pack with Ace and Yegam in a Korean snack set.",
        "ahriCupRamenDesc": "AHRIカップ麺（パッケージ表記ARIH）。アリ・モダンヌードル。",
        "ahriCupRamenBody1": "AHRI cup ramen is labeled ARIH / Ari Modern Noodle on the cup. Several color-coded flavors make a fun souvenir set. Stock jumps around at convenience stores and online.",
        "chaltteokDameunPieDesc": "餅入りパイ・クッキー。マート菓子売り場の定番。",
        "chaltteokDameunPieBody1": "Chaltteok-Dameun Pie covers chewy rice-cake pies and cookies such as CW Choco Pie Chaltteok, CW Chaltteok Cookie, and Lotte Chaltteok Pie. Find them in convenience-store and mart snack aisles.",
        "chaltteokDameunPieBody2": "Boxes crush easily — pack between clothes. Hypermarket multipacks beat airport prices.",
        "chaltteokDameunPieTip": "Buying tip\n\nDon’t mix up Lotte Chaltteok Pie and CW chaltteok cookies; check the expiry date.",
    },
    "zh": {
        "mallangCowDesc": "乐天软牛糖，软糯焦糖糖。",
        "mallangCowBody1": "Mallang Cow is Lotte’s soft caramel candy. Small and easy to pack, it often shows up in Korean snack gift piles.",
        "gosomiDesc": "好丽友高笑美，芝麻香饼干。",
        "gosomiBody1": "Gosomi is Orion’s sesame-flavored cracker. A steady seller to pack with Ace and Yegam in a Korean snack set.",
        "ahriCupRamenDesc": "AHRI杯面（包装标ARIH），阿里现代面。",
        "ahriCupRamenBody1": "AHRI cup ramen is labeled ARIH / Ari Modern Noodle on the cup. Several color-coded flavors make a fun souvenir set. Stock jumps around at convenience stores and online.",
        "chaltteokDameunPieDesc": "内馅糯米派与曲奇，超市零食区常卖。",
        "chaltteokDameunPieBody1": "Chaltteok-Dameun Pie covers chewy rice-cake pies and cookies such as CW Choco Pie Chaltteok, CW Chaltteok Cookie, and Lotte Chaltteok Pie. Find them in convenience-store and mart snack aisles.",
        "chaltteokDameunPieBody2": "Boxes crush easily — pack between clothes. Hypermarket multipacks beat airport prices.",
        "chaltteokDameunPieTip": "Buying tip\n\nDon’t mix up Lotte Chaltteok Pie and CW chaltteok cookies; check the expiry date.",
    },
    "zh-Hant": {
        "mallangCowDesc": "樂天軟牛糖，軟糯焦糖糖。",
        "mallangCowBody1": "Mallang Cow is Lotte’s soft caramel candy. Small and easy to pack, it often shows up in Korean snack gift piles.",
        "gosomiDesc": "好麗友高笑美，芝麻香餅乾。",
        "gosomiBody1": "Gosomi is Orion’s sesame-flavored cracker. A steady seller to pack with Ace and Yegam in a Korean snack set.",
        "ahriCupRamenDesc": "AHRI杯麵（包裝標ARIH），阿里現代麵。",
        "ahriCupRamenBody1": "AHRI cup ramen is labeled ARIH / Ari Modern Noodle on the cup. Several color-coded flavors make a fun souvenir set. Stock jumps around at convenience stores and online.",
        "chaltteokDameunPieDesc": "內餡糯米派與餅乾，超市零食區常賣。",
        "chaltteokDameunPieBody1": "Chaltteok-Dameun Pie covers chewy rice-cake pies and cookies such as CW Choco Pie Chaltteok, CW Chaltteok Cookie, and Lotte Chaltteok Pie. Find them in convenience-store and mart snack aisles.",
        "chaltteokDameunPieBody2": "Boxes crush easily — pack between clothes. Hypermarket multipacks beat airport prices.",
        "chaltteokDameunPieTip": "Buying tip\n\nDon’t mix up Lotte Chaltteok Pie and CW chaltteok cookies; check the expiry date.",
    },
}

# vi/th/ru reuse English flats
for lang in ("vi", "th", "ru"):
    FLAT[lang] = dict(FLAT["en"])

SHARED_BODY = {
    "mallangCowBody": {
        0: {
            "ko": FLAT["ko"]["mallangCowBody1"],
            "en": FLAT["en"]["mallangCowBody1"],
            "ja": FLAT["en"]["mallangCowBody1"],
            "zh": FLAT["en"]["mallangCowBody1"],
            "zh-Hant": FLAT["en"]["mallangCowBody1"],
            "vi": FLAT["en"]["mallangCowBody1"],
            "th": FLAT["en"]["mallangCowBody1"],
            "ru": FLAT["en"]["mallangCowBody1"],
        }
    },
    "gosomiBody": {
        0: {
            "ko": FLAT["ko"]["gosomiBody1"],
            "en": FLAT["en"]["gosomiBody1"],
            "ja": FLAT["en"]["gosomiBody1"],
            "zh": FLAT["en"]["gosomiBody1"],
            "zh-Hant": FLAT["en"]["gosomiBody1"],
            "vi": FLAT["en"]["gosomiBody1"],
            "th": FLAT["en"]["gosomiBody1"],
            "ru": FLAT["en"]["gosomiBody1"],
        }
    },
    "ahriCupRamenBody": {
        0: {
            "ko": FLAT["ko"]["ahriCupRamenBody1"],
            "en": FLAT["en"]["ahriCupRamenBody1"],
            "ja": FLAT["en"]["ahriCupRamenBody1"],
            "zh": FLAT["en"]["ahriCupRamenBody1"],
            "zh-Hant": FLAT["en"]["ahriCupRamenBody1"],
            "vi": FLAT["en"]["ahriCupRamenBody1"],
            "th": FLAT["en"]["ahriCupRamenBody1"],
            "ru": FLAT["en"]["ahriCupRamenBody1"],
        }
    },
    "chaltteokDameunPieBody": {
        0: {
            "ko": FLAT["ko"]["chaltteokDameunPieBody1"],
            "en": FLAT["en"]["chaltteokDameunPieBody1"],
            "ja": FLAT["en"]["chaltteokDameunPieBody1"],
            "zh": FLAT["en"]["chaltteokDameunPieBody1"],
            "zh-Hant": FLAT["en"]["chaltteokDameunPieBody1"],
            "vi": FLAT["en"]["chaltteokDameunPieBody1"],
            "th": FLAT["en"]["chaltteokDameunPieBody1"],
            "ru": FLAT["en"]["chaltteokDameunPieBody1"],
        },
        1: {
            "ko": FLAT["ko"]["chaltteokDameunPieBody2"],
            "en": FLAT["en"]["chaltteokDameunPieBody2"],
            "ja": FLAT["en"]["chaltteokDameunPieBody2"],
            "zh": FLAT["en"]["chaltteokDameunPieBody2"],
            "zh-Hant": FLAT["en"]["chaltteokDameunPieBody2"],
            "vi": FLAT["en"]["chaltteokDameunPieBody2"],
            "th": FLAT["en"]["chaltteokDameunPieBody2"],
            "ru": FLAT["en"]["chaltteokDameunPieBody2"],
        },
        2: {
            "ko": FLAT["ko"]["chaltteokDameunPieTip"],
            "en": FLAT["en"]["chaltteokDameunPieTip"],
            "ja": FLAT["en"]["chaltteokDameunPieTip"],
            "zh": FLAT["en"]["chaltteokDameunPieTip"],
            "zh-Hant": FLAT["en"]["chaltteokDameunPieTip"],
            "vi": FLAT["en"]["chaltteokDameunPieTip"],
            "th": FLAT["en"]["chaltteokDameunPieTip"],
            "ru": FLAT["en"]["chaltteokDameunPieTip"],
        },
    },
}


def main() -> None:
    for lang in LANGS:
        path = SHOP / f"{lang}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        souvenir = data["souvenir"]
        for key, value in FLAT[lang].items():
            souvenir[key] = value
        for body_key, idx_map in SHARED_BODY.items():
            blocks = souvenir[body_key]
            for idx, texts in idx_map.items():
                blocks[idx].update(texts)
        _write_text_retry(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        print("patched", path.name)


if __name__ == "__main__":
    main()
