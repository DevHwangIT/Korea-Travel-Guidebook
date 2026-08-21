# -*- coding: utf-8 -*-
"""Generate remaining i18n pass translations from still-missing EN/KO pairs.

Hand-curated guidebook tone for ja/zh/zh-Hant/vi/th/ru.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STILL = ROOT.parent / "_tmp_still.json"
OUT = ROOT / "04_rest_all.json"

# en -> {lang: text} — curated; keys must match EN exactly
T: dict[str, dict[str, str]] = {}


def add(en: str, ja: str, zh: str, zht: str, vi: str, th: str, ru: str) -> None:
    T[en] = {"ja": ja, "zh": zh, "zh-Hant": zht, "vi": vi, "th": th, "ru": ru}


# --- tips / short UI ---
add("Tip", "ヒント", "小贴士", "小提醒", "Mẹo", "เคล็ดลับ", "Совет")
add("English", "英語", "英文", "英文", "Tiếng Anh", "ภาษาอังกฤษ", "English")
add("Taxi", "タクシー", "出租车", "計程車", "Taxi", "แท็กซี่", "Такси")
add("Wow Pass", "Wow Pass", "Wow Pass", "Wow Pass", "Wow Pass", "Wow Pass", "Wow Pass")
add("VisitKorea", "VisitKorea", "VisitKorea", "VisitKorea", "VisitKorea", "VisitKorea", "VisitKorea")
add("CU", "CU", "CU", "CU", "CU", "CU", "CU")
add("GS25", "GS25", "GS25", "GS25", "GS25", "GS25", "GS25")
add("7-Eleven", "セブンイレブン", "7-Eleven", "7-Eleven", "7-Eleven", "7-Eleven", "7-Eleven")
add("Emart24", "Emart24", "Emart24", "Emart24", "Emart24", "Emart24", "Emart24")
add("Daiso", "ダイソー", "名创优品(Daiso)", "大創(Daiso)", "Daiso", "ไดโซ", "Daiso")
add("Uniqlo", "ユニクロ", "优衣库", "優衣庫", "Uniqlo", "ยูนิโคล่", "Uniqlo")
add("SPAO", "SPAO（スパオ）", "SPAO", "SPAO", "SPAO", "SPAO", "SPAO")
add("8Seconds", "8Seconds（エイトセカンズ）", "8Seconds", "8Seconds", "8Seconds", "8Seconds", "8Seconds")
add("Basic", "Basic（ベーシック）", "Basic", "Basic", "Basic", "Basic", "Basic")
add("Shoopen", "Shoopen（シューペン）", "Shoopen", "Shoopen", "Shoopen", "Shoopen", "Shoopen")
add("Round Lab", "ラウンドラボ", "Round Lab", "Round Lab", "Round Lab", "Round Lab", "Round Lab")
add("Anua", "アヌア", "Anua", "Anua", "Anua", "Anua", "Anua")
add("Mediheal", "メディヒール", "美迪惠尔", "Mediheal", "Mediheal", "Mediheal", "Mediheal")
add("numbuzin", "ナンバーズイン", "numbuzin", "numbuzin", "numbuzin", "numbuzin", "numbuzin")
add("TIRTIR", "ティルティル", "TIRTIR", "TIRTIR", "TIRTIR", "TIRTIR", "TIRTIR")
add("Tocobo", "トコボ", "Tocobo", "Tocobo", "Tocobo", "Tocobo", "Tocobo")
add("Green Finger", "グリーンフィンガー", "Green Finger", "Green Finger", "Green Finger", "Green Finger", "Green Finger")
add("rom&nd", "rom&nd（ロムアンド）", "rom&nd", "rom&nd", "rom&nd", "rom&nd", "rom&nd")
add("Peripera", "ペリペラ", "Peripera", "Peripera", "Peripera", "Peripera", "Peripera")
add("CLIO", "CLIO（クリオ）", "CLIO", "CLIO", "CLIO", "CLIO", "CLIO")
add("Monami", "モナミ", "慕那美", "慕那美", "Monami", "โมนามิ", "Monami")
add("Iconic", "アイコニック", "Iconic", "Iconic", "Iconic", "Iconic", "Iconic")
add("Pepero", "ペペロ", "派派乐", "Pepero", "Pepero", "เปเปโร", "Pepero")
add("Haitai Bonbon", "ヘテ・ボンボン", "海太 Bonbon", "海太 Bonbon", "Haitai Bonbon", "Haitai Bonbon", "Haitai Bonbon")
add("Binggrae Excellent", "ビングレ・エクセレント", "宾格瑞 Excellent", "Binggrae Excellent", "Binggrae Excellent", "Binggrae Excellent", "Binggrae Excellent")
add("Binggrae Together", "ビングレ・トゥゲザー", "宾格瑞 Together", "Binggrae Together", "Binggrae Together", "Binggrae Together", "Binggrae Together")
add("Kim Hye-ja Dosirak", "キム・ヘジャ弁当", "金惠子便当", "金惠子便當", "Cơm hộp Kim Hye-ja", "ข้าวกล่องคิม ฮเยจา", "Ланчбокс Ким Хеджа")
add("Cheese Bokki Ramen", "チーズボッキラーメン", "芝士炒年糕拉面", "起司炒年糕拉麵", "Mì Cheese Bokki", "ราเมนชีสโบกกี", "Сырный Cheese Bokki")
add("Achim Haetsal", "アチムヘッサル（朝の日差し）", "早晨阳光", "早晨陽光", "Achim Haetsal (Ánh nắng buổi sáng)", "อาชิมแฮซัล", "Ачим Хэцаль")
add("Sablé", "サブレ", "Sablé", "Sablé", "Sablé", "Sablé", "Sablé")
add("Bichobi", "ビチョビ", "Bichobi", "Bichobi", "Bichobi", "Bichobi", "Bichobi")
add("Cheong Kwan Jang", "正官庄", "正官庄", "正官庄", "Cheong Kwan Jang", "ชองกวานจัง", "Чонгванджан")
add("Gongganchun", "空間春", "空间春", "空間春", "Gongganchun", "กงกันชุน", "Конганчун")
add("Eolbaksa", "オルバクサ", "얼박사", "얼박사", "Eolbaksa", "ออลบักซา", "Ольбакса")
add("Jikgguri", "ジッククリ", "직꾸리", "직꾸리", "Jikgguri", "จิกกูรี", "Чиккури")
add("Biyott", "ビヨット", "Biyott", "Biyott", "Biyott", "บิยอต", "Биётт")
add("Oh Yes & Choco Pie", "オイエス＆チョコパイ", "Oh Yes 与巧克力派", "Oh Yes 與巧克力派", "Oh Yes & Choco Pie", "Oh Yes & Choco Pie", "Oh Yes и Choco Pie")
add("Lacto-Fit", "ラクトフィット", "乐多飞", "樂多飛", "Lacto-Fit", "Lacto-Fit", "Lacto-Fit")
add("Market O Brownies", "Market O ブラウニー", "Market O 布朗尼", "Market O 布朗尼", "Brownie Market O", "บราวนี่ Market O", "Брауни Market O")
add("Choco Heim & Couque D’asse", "チョコハイム＆ククダス", "Choco Heim 与 Couque D’asse", "Choco Heim 與 Couque D’asse", "Choco Heim & Couque D’asse", "Choco Heim & Couque D’asse", "Choco Heim и Couque D’asse")

# Load still and fill from a compact “use KO sense” curated map for long strings
# Remaining long strings embedded below via still index lookup after load.

def main() -> None:
    still = json.loads(STILL.read_text(encoding="utf-8"))
    # Import long-form translations module chunk
    from _rest_long import LONG  # type: ignore

    for en, locs in LONG.items():
        T[en] = locs
    OUT.write_text(json.dumps(T, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(T)} entries -> {OUT}")
    missing = [o["en"] for o in still if o["en"] not in T]
    print(f"still uncovered vs still.json: {len(missing)}")
    for en in missing[:20]:
        print("  ", en[:90])


if __name__ == "__main__":
    main()
