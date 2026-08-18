# -*- coding: utf-8 -*-
"""Parse Korean road/land-lot addresses into a filter-friendly region taxonomy.

Output shape (values are Korean short names for now)::

    {"city": "서울", "district": "용산", "dong": "한남동"}

District short-name rule
------------------------
Strip the administrative suffix ``구`` / ``군`` / ``시`` for filter-friendly
labels (``강남구`` → ``강남``, ``수영구`` → ``수영``, ``영등포구`` → ``영등포``).

Keep the ``구`` suffix when the remaining stem is a single Hangul syllable,
so names stay clear: ``중구`` → ``중구`` (not ``중``), likewise ``동구`` /
``서구`` / ``남구`` / ``북구``. ``군`` / ``시`` always strip when present.

City short-name rule
--------------------
Strip ``특별시`` / ``광역시`` / ``특별자치시`` / ``특별자치도`` / ``도``
(``서울특별시`` → ``서울``, ``제주특별자치도`` → ``제주``, ``경기도`` → ``경기``).

Dong
----
Optional. Extract the first token matching ``…동`` that is not part of a road
name (``…동로`` / ``…동길``). Omit or ``""`` when unknown.
"""
from __future__ import annotations

import re
from typing import Any

# City / province administrative suffixes (longest first).
_CITY_SUFFIX_RE = re.compile(
    r"(특별자치시|특별자치도|광역시|특별시|자치시|도)$"
)

# District / county / city-under-province unit.
_DISTRICT_UNIT_RE = re.compile(
    r"^([가-힣]{1,10}(?:[·\-][가-힣]{1,6})?)(구|군|시)$"
)

# Legal / admin dong token (full token; avoid road names like 동로 / 동길).
_DONG_RE = re.compile(r"[가-힣]{1,12}(?:\d{1,2})?동")

# Known metro / province short names (after suffix strip or bare).
_KNOWN_CITIES = frozenset(
    {
        "서울",
        "부산",
        "대구",
        "인천",
        "광주",
        "대전",
        "울산",
        "세종",
        "경기",
        "강원",
        "충북",
        "충남",
        "전북",
        "전남",
        "경북",
        "경남",
        "제주",
        "충청북",
        "충청남",
        "전라북",
        "전라남",
        "경상북",
        "경상남",
    }
)

# Normalize verbose province stems to common short labels.
_CITY_ALIASES = {
    "충청북": "충북",
    "충청남": "충남",
    "전라북": "전북",
    "전라남": "전남",
    "경상북": "경북",
    "경상남": "경남",
}


def _hangul_syllable_len(text: str) -> int:
    return len(re.findall(r"[가-힣]", text))


def normalize_city(raw: str) -> str:
    """``서울특별시`` → ``서울``, ``인천`` → ``인천``."""
    s = (raw or "").strip()
    if not s:
        return ""
    s = _CITY_SUFFIX_RE.sub("", s).strip()
    s = _CITY_ALIASES.get(s, s)
    return s


def normalize_district(raw: str) -> str:
    """Apply the short-name rule documented in the module docstring."""
    s = (raw or "").strip()
    if not s:
        return ""
    m = _DISTRICT_UNIT_RE.match(s)
    if not m:
        return s
    stem, suffix = m.group(1), m.group(2)
    if suffix == "구" and _hangul_syllable_len(stem) <= 1:
        return f"{stem}구"
    return stem


def extract_dong(address: str) -> str:
    """Return first admin dong token, or ``\"\"``.

    Only whole space-separated tokens ending in ``동`` count (avoids matching
    the leading ``동`` inside district names like ``동대문구``).
    """
    text = (address or "").strip()
    if not text:
        return ""
    cleaned = (
        text.replace("\u3000", " ")
        .replace(",", " ")
        .replace("，", " ")
    )
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    for tok in cleaned.split(" "):
        tok_clean = tok.strip("()[]（）")
        if _DONG_RE.fullmatch(tok_clean):
            return tok_clean
    return ""


def _tokenize_city(token: str) -> str | None:
    """Return normalized city if token looks like a city/province name."""
    if not token:
        return None
    if _CITY_SUFFIX_RE.search(token):
        bare = normalize_city(token)
        if bare:
            return bare
    bare = normalize_city(token)
    if bare in _KNOWN_CITIES:
        return bare
    if token in _KNOWN_CITIES:
        return _CITY_ALIASES.get(token, token)
    # Compound scraps like ``전남광주`` (Naver sometimes glues province+city).
    for known in sorted(_KNOWN_CITIES, key=len, reverse=True):
        if len(known) >= 2 and token.startswith(known):
            return _CITY_ALIASES.get(known, known)
    return None


def parse_region(address: str) -> dict[str, str]:
    """Parse an address string into ``{city, district, dong}``.

    Missing parts are empty strings. ``city`` empty means parse failed / unknown.
    """
    text = (address or "").strip()
    out = {"city": "", "district": "", "dong": ""}
    if not text:
        return out

    cleaned = (
        text.replace("\u3000", " ")
        .replace(",", " ")
        .replace("，", " ")
    )
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    tokens = cleaned.split(" ")

    city = ""
    district = ""
    start = 0
    for i, tok in enumerate(tokens):
        if re.fullmatch(r"\(?\d{5}\)?", tok):
            continue
        tok_clean = tok.strip("()[]（）")
        if not tok_clean:
            continue
        c = _tokenize_city(tok_clean)
        if c:
            city = c
            start = i + 1
            break

    if not city:
        for tok in tokens:
            c = _tokenize_city(tok.strip("()[]（）"))
            if c:
                city = c
                break

    if city:
        units: list[str] = []
        for tok in tokens[start:]:
            tok_clean = tok.strip("()[]（）")
            if not tok_clean:
                continue
            if _DISTRICT_UNIT_RE.match(tok_clean):
                units.append(tok_clean)
        for preferred in ("구", "군", "시"):
            for tok in units:
                if tok.endswith(preferred):
                    district = normalize_district(tok)
                    break
            if district:
                break

    out["city"] = city
    out["district"] = district
    out["dong"] = extract_dong(cleaned)
    return out


def region_object(address: str) -> dict[str, str] | None:
    """Like :func:`parse_region`, but returns ``None`` when city could not be parsed.

    Always includes ``city``, ``district``, and ``dong`` (dong may be ``\"\"``).
    """
    parsed = parse_region(address)
    if not parsed.get("city"):
        return None
    return {
        "city": parsed["city"],
        "district": parsed.get("district") or "",
        "dong": (parsed.get("dong") or "").strip(),
    }


def apply_region_from_location(entry: dict[str, Any]) -> dict[str, str] | None:
    """Set ``entry['region']`` from ``entry['location']`` when parseable.

    Returns the region dict written, or ``None`` if untagged.
    """
    loc = str(entry.get("location") or "").strip()
    reg = region_object(loc)
    if not reg:
        return None
    entry["region"] = reg
    return reg
