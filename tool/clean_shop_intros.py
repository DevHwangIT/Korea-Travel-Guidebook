# -*- coding: utf-8 -*-
"""Strip scraped rating / amenity dumps from restaurant about (intro) fields.

Removes patterns like:
  - 방문자 평점 4.5 (123명) / ★ / 4.5점
  - 편의: 주차, 무선인터넷, 단체석, …

Keeps genuine merchant directions / short editorial text.
When about becomes empty, fills a short KO editorial from name + menu/category
and re-translates to all GUIDE_LANGS.

Usage:
  python tool/clean_shop_intros.py
  python tool/clean_shop_intros.py --slugs seogil-sikdang,oto
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from lib import i18n_store  # noqa: E402
from lib.translate import BatchStatus, fill_scalar_texts  # noqa: E402

# Rating dumps (KO + common variants)
RATING_RE = re.compile(
    r"(?:"
    r"방문자\s*평점\s*[\d.]+\s*(?:\([\d,.]+\s*명?\))?"
    r"|평점\s*[\d.]+\s*(?:\([\d,.]+\s*명?\))?"
    r"|★+\s*[\d.]*(?:\s*/\s*5)?"
    r"|[\d.]+\s*점\s*(?:\([\d,.]+\s*(?:명|reviews?)\))?"
    r"|(?:visitor\s*)?reviews?\s*[\d.]+"
    r"|visitor\s*rating\s*[\d.]+"
    r"|評価\s*[\d.]+"
    r"|评分\s*[\d.]+"
    r")",
    re.IGNORECASE,
)

# Amenity dump: "편의: a, b, c" (and EN/JA/ZH-ish mirrors)
AMENITY_RE = re.compile(
    r"(?:"
    r"편의\s*[:：]\s*[^\n]*"
    r"|amenities?\s*[:：]\s*[^\n]*"
    r"|設備\s*[:：]\s*[^\n]*"
    r"|设施\s*[:：]\s*[^\n]*"
    r"|便利\s*[:：]\s*[^\n]*"
    r")",
    re.IGNORECASE,
)

# Standalone amenity keyword dumps (comma/· lists that look scraped)
AMENITY_LIST_RE = re.compile(
    r"(?:^|[\s,·•])(?:"
    r"무선\s*인터넷|와이파이|Wi-?Fi|"
    r"단체석|단체\s*이용\s*가능|"
    r"남/?녀\s*화장실\s*구분|"
    r"유아의자|대기공간|발렛파킹|간편결제|"
    r"반려동물\s*동반|"
    r"포장|배달|예약|주차"
    r")(?=[\s,·•]|$)",
    re.IGNORECASE,
)

WS_RE = re.compile(r"[ \t]+\n")
MULTI_SPACE = re.compile(r"[ \t]{2,}")
MULTI_NL = re.compile(r"\n{3,}")


def clean_about_text(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        return ""
    text = value
    text = RATING_RE.sub(" ", text)
    text = AMENITY_RE.sub(" ", text)
    # Drop trailing amenity keyword salad only when little editorial remains
    stripped = text.strip()
    # If leftover is mostly amenity tokens / punctuation, clear it
    trial = AMENITY_LIST_RE.sub(" ", stripped)
    trial = re.sub(r"[\s,·•/:：]+", " ", trial).strip()
    if len(trial) < 12 and AMENITY_LIST_RE.search(stripped):
        text = trial
    else:
        text = stripped

    text = WS_RE.sub("\n", text)
    text = MULTI_SPACE.sub(" ", text)
    text = MULTI_NL.sub("\n\n", text)
    text = text.strip(" \t\n,·•/:：")
    # Drop leftover "편의" alone
    if text in ("편의", "평점", "방문자"):
        return ""
    return text.strip()


def editorial_about(entry: dict) -> str:
    name = str(entry.get("name") or "").strip() or "이 가게"
    menu = str(entry.get("menu") or "").strip()
    cat = str(entry.get("category") or "").strip()
    focus = menu or cat or "한식"
    return (
        f"{name}은(는) {focus}로 알려진 곳입니다. "
        "여행 중 한 끼로 찾아보기 좋은 현지 맛집입니다."
    )


def clean_bundle(bundle: dict, *, slugs: set[str] | None = None) -> dict[str, int]:
    stats = {"cleaned": 0, "emptied": 0, "editorial": 0, "translated": 0}
    ko_rest = bundle["ko"].setdefault("restaurants", {})
    changed_slugs: list[str] = []

    for slug, entry in list(ko_rest.items()):
        if not isinstance(entry, dict):
            continue
        if slugs is not None and slug not in slugs:
            continue
        old = str(entry.get("about") or "")
        new = clean_about_text(old)
        if new != old.strip() or (old and not new):
            if new != old:
                stats["cleaned"] += 1
            if old.strip() and not new:
                stats["emptied"] += 1
        if not new:
            new = editorial_about(entry)
            stats["editorial"] += 1
            entry["about"] = new
            changed_slugs.append(slug)
        elif new != old:
            entry["about"] = new
            changed_slugs.append(slug)

    # Propagate cleaned KO about → other langs via translate when changed
    if changed_slugs:
        st = BatchStatus()
        for slug in changed_slugs:
            ko_entry = ko_rest.get(slug) or {}
            texts = {
                "ko": {"about": str(ko_entry.get("about") or "")},
                "en": {},
                "ja": {},
                "zh": {},
            }
            filled = fill_scalar_texts(texts, ("about",), force=True, status=st)
            for lang in i18n_store.LANGS:
                if lang == "ko":
                    continue
                restaurants = bundle[lang].setdefault("restaurants", {})
                other = dict(restaurants.get(slug) or {})
                # Always sync structural fields from KO; replace about from fill
                about = (filled.get(lang) or {}).get("about") or ""
                if about:
                    other["about"] = about
                    stats["translated"] += 1
                else:
                    # Fallback: clear junk mirrors of KO if still polluted
                    other["about"] = clean_about_text(str(other.get("about") or ""))
                    if not other["about"]:
                        other["about"] = str(ko_entry.get("about") or "")
                restaurants[slug] = other
        for n in st.note_lines()[:12]:
            print(" ", n)

    # Also scrub non-KO leftovers that still match dump patterns even if KO unchanged
    for lang in i18n_store.LANGS:
        if lang == "ko":
            continue
        restaurants = bundle[lang].setdefault("restaurants", {})
        for slug, entry in list(restaurants.items()):
            if not isinstance(entry, dict):
                continue
            if slugs is not None and slug not in slugs:
                continue
            old = str(entry.get("about") or "")
            if not (RATING_RE.search(old) or AMENITY_RE.search(old)):
                continue
            new = clean_about_text(old)
            if not new:
                new = str((ko_rest.get(slug) or {}).get("about") or "")
            if new != old:
                entry["about"] = new
                stats["cleaned"] += 1

    return stats


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slugs", default="", help="comma-separated slug filter")
    ap.add_argument("--no-bundle", action="store_true")
    args = ap.parse_args()
    slug_set = {s.strip() for s in args.slugs.split(",") if s.strip()} or None

    bundle = i18n_store.load_all()
    stats = clean_bundle(bundle, slugs=slug_set)
    i18n_store.save_all(bundle)
    print(
        f"clean_shop_intros: cleaned={stats['cleaned']} emptied={stats['emptied']} "
        f"editorial={stats['editorial']} translated_fields={stats['translated']}"
    )
    if not args.no_bundle:
        print(i18n_store.build_bundle())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
