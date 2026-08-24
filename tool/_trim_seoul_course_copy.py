# -*- coding: utf-8 -*-
"""Trim Seoul curated course copy to one concise sentence per stop/summary."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "i18n" / "pages" / "travel-courses"
LANGS = ["ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru"]

SENT_SPLIT = re.compile(r"(?<=[.!?。！？])\s+")


def first_sentence(text: str, max_len: int = 72) -> str:
    text = " ".join(str(text or "").split())
    if not text:
        return text
    parts = SENT_SPLIT.split(text.strip())
    out = parts[0].strip() if parts else text.strip()
    if len(out) > max_len:
        cut = out[: max_len - 1].rsplit(" ", 1)[0]
        out = (cut or out[: max_len - 1]).rstrip(".,;:") + "…"
    return out


def trim_lang(lang: str) -> int:
    path = PAGES / f"{lang}.json"
    if not path.exists():
        return 0
    data = json.loads(path.read_text(encoding="utf-8"))
    sc = data.get("travelCourses", {}).get("seoulCurated", {}).get("courses", {})
    if not sc:
        return 0
    n = 0
    for course in sc.values():
        if course.get("summary"):
            trimmed = first_sentence(course["summary"], 88)
            if trimmed != course["summary"]:
                course["summary"] = trimmed
                n += 1
        for stop in course.get("stops", []):
            if stop.get("desc"):
                trimmed = first_sentence(stop["desc"], 72)
                if trimmed != stop["desc"]:
                    stop["desc"] = trimmed
                    n += 1
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return n


def main() -> None:
    total = 0
    for lang in LANGS:
        count = trim_lang(lang)
        print(f"{lang}: trimmed {count} fields")
        total += count
    print(f"total: {total}")


if __name__ == "__main__":
    main()
