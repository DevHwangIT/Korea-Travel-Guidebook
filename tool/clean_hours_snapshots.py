# -*- coding: utf-8 -*-
"""Strip live open/closed snapshot prefixes from restaurant/shop hours in i18n JSON.

Usage:
  python tool/clean_hours_snapshots.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from lib import i18n_store  # noqa: E402
from lib.paths import ROOT  # noqa: E402

# Live status prefixes (middle-dot / dash separators from place scrapes).
STATUS_PREFIX_RE = re.compile(
    r"^(?:"
    r"영업\s*중"
    r"|영업\s*전"
    r"|오늘\s*휴무"
    r"|브레이크\s*타임"
    r"|Open(?:\s+now)?"
    r"|Closed(?:\s+today)?"
    r"|営業中"
    r"|営業前"
    r"|本日休業"
    r"|休憩中"
    r"|营业中"
    r"|营业前"
    r"|今日休息"
    r"|今日休業"
    r"|Đang\s+mở"
    r"|Đóng\s+cửa"
    r"|เปิด(?:อยู่)?"
    r"|ปิด(?:แล้ว)?"
    r"|Открыто"
    r"|Закрыто"
    r")\s*[·•\-–—]\s*",
    re.IGNORECASE,
)

# Entire field is only a live status word (no schedule left).
STATUS_ONLY_RE = re.compile(
    r"^(?:"
    r"영업\s*중"
    r"|영업\s*전"
    r"|오늘\s*휴무"
    r"|브레이크\s*타임"
    r"|Open(?:\s+now)?"
    r"|Closed(?:\s+today)?"
    r"|営業中"
    r"|営業前"
    r"|本日休業"
    r"|休憩中"
    r"|营业中"
    r"|营业前"
    r"|今日休息"
    r"|今日休業"
    r")\s*$",
    re.IGNORECASE,
)

# Leftover that is only a dated closed note (no weekly schedule).
DATED_CLOSED_ONLY_RE = re.compile(
    r"^(?:"
    r"\d{1,2}/\d{1,2}\s*휴무"
    r"|closed\s+\d{1,2}/\d{1,2}"
    r"|\d{1,2}/\d{1,2}\s*休業"
    r"|\d{1,2}/\d{1,2}\s*休息"
    r")\s*$",
    re.IGNORECASE,
)

# Live "on break since HH:MM" snapshots with no weekly schedule.
BREAK_SNAPSHOT_ONLY_RE = re.compile(
    r"^(?:"
    r"\d{1,2}:\d{2}\s*에\s*브레이크\s*타임"
    r"|\d{1,2}:\d{2}から休憩"
    r"|\d{1,2}:\d{2}休息时[间間]"
    r")\s*$",
    re.IGNORECASE,
)

# Optional JS data trees that may embed hours strings.
EXTRA_JSON_GLOBS = (
    "data/**/*.json",
)


def clean_hours(value: str) -> str:
    if not isinstance(value, str) or not value:
        return value
    # Keep UI field labels and true static 24h strings.
    if value in (
        "영업시간",
        "Hours",
        "営業時間",
        "营业时间",
        "營業時間",
        "Giờ mở cửa",
        "เวลาเปิด",
        "Часы работы",
    ):
        return value
    if re.fullmatch(
        r"(?:24시간\s*영업|Open\s+24\s+hours|24時間営業|24小时营业|เปิดตลอด\s*24\s*ชม\.?)",
        value.strip(),
        re.I,
    ):
        return value

    cleaned = STATUS_PREFIX_RE.sub("", value, count=1).strip()
    if (
        STATUS_ONLY_RE.match(cleaned)
        or DATED_CLOSED_ONLY_RE.match(cleaned)
        or BREAK_SNAPSHOT_ONLY_RE.match(cleaned)
    ):
        return ""
    return cleaned


def walk(obj, stats: dict) -> object:
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k == "hours" and isinstance(v, str):
                nv = clean_hours(v)
                if nv != v:
                    stats["changed"] += 1
                out[k] = nv
            else:
                out[k] = walk(v, stats)
        return out
    if isinstance(obj, list):
        return [walk(x, stats) for x in obj]
    return obj


def _clean_json_file(path: Path, stats: dict) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    cleaned = walk(data, stats)
    path.write_text(
        json.dumps(cleaned, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    total = 0
    bundle = i18n_store.load_all()
    for lang in i18n_store.LANGS:
        stats = {"changed": 0}
        bundle[lang] = walk(bundle[lang], stats)  # type: ignore[assignment]
        print(f"{lang}: cleaned {stats['changed']} hours fields")
        total += stats["changed"]
    if total:
        i18n_store.save_all(bundle)
        print(i18n_store.build_bundle())

    for pattern in EXTRA_JSON_GLOBS:
        for path in sorted(ROOT.glob(pattern)):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            if '"hours"' not in text:
                continue
            stats = {"changed": 0}
            _clean_json_file(path, stats)
            if stats["changed"]:
                print(f"{path.relative_to(ROOT).as_posix()}: cleaned {stats['changed']} hours fields")
                total += stats["changed"]

    print(f"Total cleaned: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
