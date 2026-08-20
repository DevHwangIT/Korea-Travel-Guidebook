# -*- coding: utf-8 -*-
"""Map restaurant region/location → dish filter region-group codes."""
from __future__ import annotations

import re
from typing import Any

# Tab / data-region-group values
REGION_GROUPS = (
    "all",
    "sudo",
    "gangwon",
    "chungcheong",
    "jeolla",
    "gyeongsang",
    "jeju",
)

# Korean city / province tokens → group
CITY_TO_GROUP: dict[str, str] = {
    # 수도권
    "서울": "sudo",
    "경기": "sudo",
    "인천": "sudo",
    "seoul": "sudo",
    "gyeonggi": "sudo",
    "incheon": "sudo",
    # 강원
    "강원": "gangwon",
    "gangwon": "gangwon",
    # 충청
    "충북": "chungcheong",
    "충남": "chungcheong",
    "충청": "chungcheong",
    "대전": "chungcheong",
    "세종": "chungcheong",
    "chungbuk": "chungcheong",
    "chungnam": "chungcheong",
    "chungcheong": "chungcheong",
    "daejeon": "chungcheong",
    "sejong": "chungcheong",
    # 전라
    "전북": "jeolla",
    "전남": "jeolla",
    "전라": "jeolla",
    "광주": "jeolla",
    "jeonbuk": "jeolla",
    "jeonnam": "jeolla",
    "jeolla": "jeolla",
    "gwangju": "jeolla",
    # 경상
    "경북": "gyeongsang",
    "경남": "gyeongsang",
    "경상": "gyeongsang",
    "부산": "gyeongsang",
    "대구": "gyeongsang",
    "울산": "gyeongsang",
    "gyeongbuk": "gyeongsang",
    "gyeongnam": "gyeongsang",
    "gyeongsang": "gyeongsang",
    "busan": "gyeongsang",
    "daegu": "gyeongsang",
    "ulsan": "gyeongsang",
    # 제주
    "제주": "jeju",
    "jeju": "jeju",
}

# Location/address prefix tokens (ordered longer-first for matching)
_LOC_PREFIXES: list[tuple[str, str]] = sorted(
    (
        ("서울특별시", "sudo"),
        ("경기도", "sudo"),
        ("인천광역시", "sudo"),
        ("강원특별자치도", "gangwon"),
        ("강원도", "gangwon"),
        ("충청북도", "chungcheong"),
        ("충청남도", "chungcheong"),
        ("대전광역시", "chungcheong"),
        ("세종특별자치시", "chungcheong"),
        ("전북특별자치도", "jeolla"),
        ("전라북도", "jeolla"),
        ("전라남도", "jeolla"),
        ("광주광역시", "jeolla"),
        ("경상북도", "gyeongsang"),
        ("경상남도", "gyeongsang"),
        ("부산광역시", "gyeongsang"),
        ("대구광역시", "gyeongsang"),
        ("울산광역시", "gyeongsang"),
        ("제주특별자치도", "jeju"),
        ("서울", "sudo"),
        ("경기", "sudo"),
        ("인천", "sudo"),
        ("강원", "gangwon"),
        ("충북", "chungcheong"),
        ("충남", "chungcheong"),
        ("대전", "chungcheong"),
        ("세종", "chungcheong"),
        ("전북", "jeolla"),
        ("전남", "jeolla"),
        ("광주", "jeolla"),
        ("경북", "gyeongsang"),
        ("경남", "gyeongsang"),
        ("부산", "gyeongsang"),
        ("대구", "gyeongsang"),
        ("울산", "gyeongsang"),
        ("제주", "jeju"),
    ),
    key=lambda x: -len(x[0]),
)


def region_group_from_city(city: str | None) -> str | None:
    if not city:
        return None
    key = str(city).strip().lower()
    # try exact then strip trailing 도/시
    if key in CITY_TO_GROUP:
        return CITY_TO_GROUP[key]
    # Korean mixed case
    raw = str(city).strip()
    if raw in CITY_TO_GROUP:
        return CITY_TO_GROUP[raw]
    for token, group in CITY_TO_GROUP.items():
        if raw.startswith(token) or key.startswith(token.lower()):
            return group
    return None


def region_group_from_location(location: str | None) -> str | None:
    if not location:
        return None
    text = str(location).strip()
    for prefix, group in _LOC_PREFIXES:
        if text.startswith(prefix) or f" {prefix}" in text[:40]:
            return group
    # English tokens in address
    low = text.lower()
    for token, group in CITY_TO_GROUP.items():
        if re.search(rf"\b{re.escape(token)}\b", low):
            return group
    return None


def region_group_from_restaurant(entry: dict[str, Any] | None) -> str:
    """Return region-group code; default sudo when unknown (most shops are metro)."""
    if not isinstance(entry, dict):
        return "sudo"
    region = entry.get("region")
    city = None
    if isinstance(region, dict):
        city = region.get("city") or region.get("code") or region.get("ko")
    elif isinstance(region, str):
        city = region
    group = region_group_from_city(city if isinstance(city, str) else None)
    if group:
        return group
    group = region_group_from_location(entry.get("location") or entry.get("address"))
    return group or "sudo"
