#!/usr/bin/env python3
"""Convert Simplified Chinese JSON strings to Traditional (Taiwan-style) via OpenCC dicts."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_dict(path: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        # Prefer first conversion candidate
        mapping[parts[0]] = parts[1]
    return mapping


# Phrase first (longest-match), then characters, then TW variants on result
ST_PHRASES = load_dict(ROOT / "_opencc_STPhrases.txt")
ST_CHARS = load_dict(ROOT / "_opencc_STCharacters.txt")

# Common TW / 繁體 style overrides after s2t (phrase-level preference)
TW_EXTRA = {
    "軟件": "軟體",
    "文件": "檔案",  # careful — may over-convert; applied selectively below
    "網絡": "網路",
    "互聯網": "網際網路",
    "信息": "資訊",
    "短信": "簡訊",
    "視頻": "影片",
    "默認": "預設",
    "打印": "列印",
    "點擊": "點選",
    "數據": "資料",
    "數位": "數位",
    "優化": "最佳化",
    "質量": "品質",
    "服務器": "伺服器",
    "客戶端": "用戶端",
    "人工智能": "人工智慧",
    "算法": "演算法",
    "程序": "程式",
    "編程": "程式設計",
    "代碼": "程式碼",
    "芯片": "晶片",
    "內存": "記憶體",
    "硬盤": "硬碟",
    "鼠標": "滑鼠",
    "鍵盤": "鍵盤",
    "屏幕": "螢幕",
    "攝像頭": "攝影機",
    "出租車": "計程車",
    "出租車": "計程車",
    "的士": "計程車",
    "公交": "公車",
    "公共汽車": "公車",
    "地鐵": "捷運",  # Korea context often keeps 地鐵 — override carefully
    "騎行": "騎乘",
    "自行車": "腳踏車",
    "摩托車": "機車",
    "出租車": "計程車",
    "出租車": "計程車",
    "出租車": "計程車",
    "裡程": "里程",
    "裡": "裡",
    "裏": "裡",
    "著": "著",
    "爲": "為",
    "僞": "偽",
    "啓": "啟",
    "峯": "峰",
    "牀": "床",
    "纔": "才",
    "羣": "群",
    "衆": "眾",
    "麪": "麵",
    "祕": "秘",
    "污": "汙",
}

# TW travel-UI preferences (safe for this guidebook)
TW_UI = {
    "出租車": "計程車",
    "的士": "計程車",
    "出租車": "計程車",
    "軟件": "軟體",
    "應用": "應用程式",
    "應用程序": "應用程式",
    "手機應用": "手機應用程式",
    "信息": "資訊",
    "短信": "簡訊",
    "網絡": "網路",
    "視頻": "影片",
    "默認": "預設",
    "點擊": "點選",
    "打印": "列印",
    "質量": "品質",
    "服務器": "伺服器",
    "內存": "記憶體",
    "硬盤": "硬碟",
    "鼠標": "滑鼠",
    "屏幕": "螢幕",
    "攝像頭": "攝影機",
    "自行車": "腳踏車",
    "摩托車": "機車",
    "公交車站": "公車站",
    "公交車": "公車",
    "公共汽車": "公車",
    "裏": "裡",
    "爲": "為",
    "僞": "偽",
    "啓": "啟",
    "峯": "峰",
    "牀": "床",
    "纔": "才",
    "羣": "群",
    "衆": "眾",
    "麪": "麵",
}


def _build_phrase_regex(phrases: dict[str, str]) -> re.Pattern[str]:
    # Longest first
    keys = sorted(phrases.keys(), key=len, reverse=True)
    return re.compile("|".join(re.escape(k) for k in keys))


PHRASE_RE = _build_phrase_regex(ST_PHRASES)
UI_RE = _build_phrase_regex(TW_UI)


def s2tw(text: str) -> str:
    if not text or not isinstance(text, str):
        return text

    def repl_phrase(m: re.Match[str]) -> str:
        return ST_PHRASES[m.group(0)]

    out = PHRASE_RE.sub(repl_phrase, text)
    out = "".join(ST_CHARS.get(ch, ch) for ch in out)

    def repl_ui(m: re.Match[str]) -> str:
        return TW_UI[m.group(0)]

    out = UI_RE.sub(repl_ui, out)
    return out


def convert_obj(obj):
    if isinstance(obj, dict):
        return {k: convert_obj(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_obj(v) for v in obj]
    if isinstance(obj, str):
        return s2tw(obj)
    return obj


def main() -> None:
    zh_path = ROOT / "zh.json"
    out_path = ROOT / "zh-Hant.json"
    data = json.loads(zh_path.read_text(encoding="utf-8"))
    converted = convert_obj(data)

    # Keep brand-ish Latin / proper nouns untouched already (ASCII).
    # Preserve a few intentional zh-Hant editorial differences if needed.
    out_path.write_text(
        json.dumps(converted, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # Stats vs previous zh-Hant if any
    flat_zh = []
    flat_h = []

    def walk(a, b):
        if isinstance(a, dict) and isinstance(b, dict):
            for k in a:
                if k in b:
                    walk(a[k], b[k])
        elif isinstance(a, str) and isinstance(b, str):
            flat_zh.append(a)
            flat_h.append(b)

    walk(data, converted)
    same = sum(1 for a, b in zip(flat_zh, flat_h) if a == b)
    diff = sum(1 for a, b in zip(flat_zh, flat_h) if a != b)
    print(f"wrote {out_path.name}: {diff} strings changed, {same} unchanged")


if __name__ == "__main__":
    main()
