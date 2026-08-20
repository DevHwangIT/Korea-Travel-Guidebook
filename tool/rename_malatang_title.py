# -*- coding: utf-8 -*-
"""Rename 마라탕 → 한국식 마라탕 (display titles only; slug stays malatang)."""
from __future__ import annotations

import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from lib import i18n_store  # noqa: E402

TITLES = {
    "ko": "한국식 마라탕",
    "en": "Korean-style malatang",
    "ja": "韓国式マラータン",
    "zh": "韩式麻辣烫",
    "zh-Hant": "韓式麻辣燙",
    "vi": "Lẩu mala kiểu Hàn",
    "th": "หมาล่าแทงสไตล์เกาหลี",
    "ru": "Корейский малатан",
}


def main() -> None:
    bundle = i18n_store.load_all()
    for lang, title in TITLES.items():
        data = bundle[lang]
        dishes = data.setdefault("dishes", {})
        entry = dishes.setdefault("malatang", {})
        entry["title"] = title

        # foodLife quiz result label (hub recommend UI)
        quiz = data.get("foodLife", {}).get("quiz", {}).get("results", {})
        if isinstance(quiz, dict) and "malatang" in quiz and isinstance(quiz["malatang"], dict):
            quiz["malatang"]["name"] = title

    i18n_store.save_all(bundle)
    print(i18n_store.build_bundle())
    print("Updated dishes.malatang.title + foodLife.quiz.results.malatang.name")


if __name__ == "__main__":
    main()
