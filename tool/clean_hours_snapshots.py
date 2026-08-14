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

from lib.paths import I18N_DIR  # noqa: E402

# Live status prefixes (middle-dot separators from place scrapes).
STATUS_PREFIX_RE = re.compile(
    r"^(?:"
    r"영업\s*중"
    r"|오늘\s*휴무"
    r"|브레이크타임"
    r"|Open"
    r"|Closed\s+today"
    r"|営業中"
    r"|本日休業"
    r"|休憩中"
    r"|营业中"
    r"|今日休息"
    r")\s*[·•]\s*",
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


def clean_hours(value: str) -> str:
    if not isinstance(value, str) or not value:
        return value
    # Keep UI field labels and true static 24h strings.
    if value in ("영업시간", "Hours", "営業時間", "营业时间"):
        return value
    if re.fullmatch(r"(?:24시간\s*영업|Open\s+24\s+hours|24時間営業|24小时营业)", value.strip(), re.I):
        return value

    cleaned = STATUS_PREFIX_RE.sub("", value, count=1).strip()
    if DATED_CLOSED_ONLY_RE.match(cleaned):
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


def main() -> int:
    from lib import i18n_store  # noqa: WPS433

    total = 0
    for lang in i18n_store.LANGS:
        path = I18N_DIR / f"{lang}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        stats = {"changed": 0}
        cleaned = walk(data, stats)
        path.write_text(
            json.dumps(cleaned, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"{path.name}: cleaned {stats['changed']} hours fields")
        total += stats["changed"]
    print(f"Total cleaned: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
