# -*- coding: utf-8 -*-
"""Clean scraped fluff from aug20 batch shops (about + live hours status).

- Strip 영업중/영업종료 live prefixes from hours (keep real schedule)
- Replace name-only / marketing / long Naver blurbs in about with
  short guidebook directions or a brief editorial
- Re-translate cleaned KO about to other langs; sync hours across langs

Usage:
  python tool/cleanup_aug20_shop_copy.py
  python tool/cleanup_aug20_shop_copy.py --dry-run
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from add_food_batch_aug20_user_list import SHOPS  # noqa: E402
from clean_hours_snapshots import clean_hours  # noqa: E402
from lib import i18n_store  # noqa: E402
from lib.translate import BatchStatus, fill_scalar_texts  # noqa: E402

EXTRA_SLUGS = ("yoajeong", "benson-creamery-seoul")

NOISE_MARKERS = (
    "찾아오시는",
    "오시는길",
    "오시는 길",
    "찾아오는 길",
    "네비게이션",
    "네비로",
    "네이버",
    "주차 안내",
    "주차장 안내",
    "주차안내",
    "Tel.",
    "전화번호",
    "항상 감사",
    "고객님께",
    "맛집으로 유명",
    "회식이나",
    "특별하게 만들어",
    "검색하시면",
    "검색 후",
    "검색하고",
    "카카오T",
    "T맵",
    "발렛",
    "방문해 보세요",
    "사랑받아온",
    "인근 유료주차장",
    "주변 매장",
    "주변 버스정류장",
    "자차 이용",
    "대중교통 이용",
    "도보 이용",
    "연락주세요",
    "감사합니다",
    "올려드립니다",
    "올림-",
    "대형주차장",
    "무료 발렛",
    "주차는 불가",
    "따뜻한 감성이",
    "제대로 된 닭발",
)

LIGHT_FLUFF_RE = re.compile(
    r"(?:ㅋ+|ㅎ+|\^\^+|!~+|♡+|♥+|:\s*\)|※+|★+|☞+|<<|>>|"
    r"꼭\s*정면만\s*보세요~?ㅋ*|"
    r"찾아오실\s*때\s*궁금하신\s*점이\s*있다면[^\n]*|"
    r"네이버\s*지도로[^\n]*|"
    r"네비게이션\s*이용시[^\n]*|"
    r"주차는\s*불가하니[^\n]*)",
    re.IGNORECASE,
)

SECTION_HEADER_RE = re.compile(
    r"^(?:\[.*?\]|※+\s*.*|<{1,2}.*?>{1,2}|\*{1,3}\s*.*|"
    r"\d+\)\s*.*|-\s*(?:대중교통|자차|도보|승용차|버스|택시).*)$"
)

BAD_MENU_RE = re.compile(
    r"(?:"
    r"^평일$|^주말$|^점심$|^저녁$|"
    r"전화예약|한정판매|NEW\]|❄️|💙|🎉|파워냉방|무료\s*제공|"
    r"SINGLE|싱글\(|이벤트|청첩장|생일/|"
    r"^\[|^\W+$"
    r")",
    re.IGNORECASE,
)


def _norm_name(value: str) -> str:
    return re.sub(r"\s+", "", (value or "").strip())


def _focus_label(entry: dict) -> str:
    name = str(entry.get("name") or "").strip()
    menu = str(entry.get("menu") or "").strip()
    cat = str(entry.get("category") or "").split(",")[0].strip()
    focus = menu
    if (
        not focus
        or _norm_name(focus) == _norm_name(name)
        or BAD_MENU_RE.search(focus)
        or len(focus) > 36
        or re.search(r"\d+\s*[gG]|중\(|소\(|대\(", focus)
    ):
        focus = cat or "한식"
    return focus


def editorial_about(entry: dict) -> str:
    name = str(entry.get("name") or "").strip() or "이 가게"
    focus = _focus_label(entry)
    ch = name[-1]
    particle = (
        "는"
        if ("가" <= ch <= "힣" and (ord(ch) - 0xAC00) % 28 == 0)
        else "은"
    )
    return f"{name}{particle} {focus} 맛집입니다. 여행 중 한 끼로 찾아보기 좋습니다."


def is_name_only(about: str, entry: dict) -> bool:
    a = _norm_name(about)
    if not a:
        return True
    names = {
        _norm_name(str(entry.get("name") or "")),
        _norm_name(str(entry.get("previewTitle") or "")),
    }
    names.discard("")
    if a in names:
        return True
    if len(about.strip()) <= 24 and any(a in n or n in a for n in names):
        return True
    return False


def has_noise(about: str) -> bool:
    if any(m in about for m in NOISE_MARKERS):
        return True
    if len(about) > 140:
        return True
    if about.count("\n") >= 3 and len(about) > 90:
        return True
    if re.search(r"Tel\.?\s*\d|02\)\d|0\d{1,2}-\d{3,4}-\d{4}", about):
        return True
    if re.search(r"쭈~+|ㅋ+|ㅎㅎ|고객님|항상 감사", about):
        return True
    return False


def _score_direction_line(para: str) -> int:
    score = 0
    if re.search(r"\d+\s*번\s*출구", para):
        score += 5
    if "도보" in para:
        score += 3
    if re.search(r"\d호선|지하철|\w+역", para):
        score += 2
    if any(x in para for x in ("직진", "골목", "층", "맞은편", "앞에", "사이")):
        score += 2
    if "위치" in para:
        score += 1
    if any(x in para for x in ("버스", "자가용", "자차", "승용차", "기본요금", "여분")):
        score -= 3
    if len(para) > 90:
        score -= 2
    if not re.search(r"(습니다|입니다|요|분\s*$|거리$|있습니다|위치합니다|나와주세요|직진하세요)", para):
        score -= 2
    return score


def _split_sentences(para: str) -> list[str]:
    # Keep terminators with the sentence.
    parts = re.findall(r"[^。\.!?]+[。\.!?]?", para)
    return [p.strip() for p in parts if p.strip()]


def extract_short_directions(about: str) -> str:
    skip_if = (
        "주차",
        "네비",
        "네이버",
        "Tel",
        "전화",
        "카카오",
        "T맵",
        "발렛",
        "검색",
        "감사",
        "회식",
        "사랑받아",
        "특별하게",
        "맛집 [",
        "맛집으로 유명",
        "유료주차",
        "주차장",
        "주소]",
        "[주소",
        "버스-",
        "택시-",
        "대형",
        "발렛파킹",
        "고객님",
        "올림",
        "인근 유료",
        "주변 매장",
        "주변 버스",
        "카카오T",
        "주차요금",
        "주차 요금",
        "민영주차",
        "공영주차",
        "모두의 주차",
        "접근이 용이",
        "기본요금",
        "경남호텔",
        "이내에 위치",
        "20여분",
    )
    keep_if = ("출구", "도보", "역", "직진", "골목", "위치", "앞에", "층", "맞은편", "사이")

    scored: list[tuple[int, str]] = []
    for raw in re.split(r"[\n\r]+", about):
        para = raw.strip(" \t-•*·~^")
        if not para or SECTION_HEADER_RE.match(para):
            continue
        # Strip bullets / stars only — keep leading "5호선" digits
        para = re.sub(r"^[*※•·\-]+\s*", "", para)
        para = re.sub(r"^\d+\)\s*", "", para)
        para = LIGHT_FLUFF_RE.sub(" ", para)
        para = re.sub(r"[★※☞<>\[\]\{\}]+", " ", para)
        para = re.sub(r"[ \t]{2,}", " ", para).strip(" \t-·~^:：")
        if re.match(r"^[a-zA-Z]\s", para):
            continue
        chunks = _split_sentences(para) if (len(para) > 80 or "저희" in para or para.count(".") >= 1) else [para]
        for chunk in chunks:
            chunk = chunk.strip()
            if len(chunk) < 8:
                continue
            if any(s in chunk for s in skip_if):
                continue
            if not any(k in chunk for k in keep_if):
                continue
            if re.search(r"쭈~+|ㅋ+|ㅎㅎ|머리를 들고|보이실 겁니다|저희\s+\S+\s*매장", chunk):
                continue
            if len(chunk) > 100:
                continue  # incomplete truncation — prefer editorial
            if chunk.endswith(
                (
                    "에",
                    "을",
                    "를",
                    "이",
                    "가",
                    "의",
                    "와",
                    "과",
                    "한",
                    "된",
                    "로",
                    "으로",
                    "뒤",
                    "면",
                    "보이는",
                    "에서",
                )
            ):
                continue
            scored.append((_score_direction_line(chunk), chunk))

    if not scored:
        return ""
    scored.sort(key=lambda x: (-x[0], len(x[1])))
    scored = [x for x in scored if x[0] >= 2]
    if not scored:
        return ""
    top = [scored[0][1]]
    if len(scored) > 1 and scored[1][0] >= 5 and len(top[0]) + len(scored[1][1]) <= 120:
        if scored[1][1] not in top[0]:
            top.append(scored[1][1])
    return " ".join(top)


def polish_short_about(about: str) -> str:
    text = LIGHT_FLUFF_RE.sub(" ", about)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip(" \t\n~^")
    text = re.sub(r"(?:\n|^)\s*찾아오실\s*때[^\n]*$", "", text, flags=re.M)
    return text.strip()


def clean_about(about: str, entry: dict) -> str:
    about = (about or "").strip()
    if is_name_only(about, entry):
        return editorial_about(entry)
    if not has_noise(about):
        polished = polish_short_about(about)
        if is_name_only(polished, entry):
            return editorial_about(entry)
        return polished or editorial_about(entry)

    extracted = extract_short_directions(about)
    if extracted and len(extracted) <= 120 and _score_direction_line(extracted) >= 2:
        return extracted
    return editorial_about(entry)


def target_slugs() -> list[str]:
    slugs = [s["slug"] for s in SHOPS]
    for extra in EXTRA_SLUGS:
        if extra not in slugs:
            slugs.append(extra)
    return slugs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-bundle", action="store_true")
    ap.add_argument("--no-translate", action="store_true")
    args = ap.parse_args()

    bundle = i18n_store.load_all()
    ko_rest = bundle["ko"].setdefault("restaurants", {})
    slugs = target_slugs()

    about_changed: list[str] = []
    hours_changed: list[str] = []
    examples: list[tuple[str, str, str, str, str]] = []

    for slug in slugs:
        entry = ko_rest.get(slug)
        if not isinstance(entry, dict):
            print(f"[missing] {slug}")
            continue

        old_about = str(entry.get("about") or "")
        old_hours = str(entry.get("hours") or "")
        new_about = clean_about(old_about, entry)
        new_hours = clean_hours(old_hours) if old_hours else old_hours

        if new_about != old_about:
            about_changed.append(slug)
            entry["about"] = new_about
        if new_hours != old_hours:
            hours_changed.append(slug)
            entry["hours"] = new_hours

        if new_about != old_about or new_hours != old_hours:
            examples.append((slug, old_about[:90], new_about[:90], old_hours, new_hours))

        for lang in i18n_store.LANGS:
            if lang == "ko":
                continue
            other = bundle[lang].setdefault("restaurants", {}).setdefault(slug, {})
            if isinstance(other, dict):
                other["hours"] = entry.get("hours", "")

    if about_changed and not args.no_translate and not args.dry_run:
        st = BatchStatus()
        for slug in about_changed:
            ko_entry = ko_rest[slug]
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
                about = (filled.get(lang) or {}).get("about") or ""
                other["about"] = about or str(ko_entry.get("about") or "")
                other["hours"] = str(ko_entry.get("hours") or "")
                restaurants[slug] = other
        for n in st.note_lines()[:16]:
            print(" ", n)

    print(f"slugs scanned: {len(slugs)}")
    print(f"about cleaned: {len(about_changed)}")
    print(f"hours cleaned: {len(hours_changed)}")
    print("changed slugs:", ", ".join(about_changed[:40]), ("..." if len(about_changed) > 40 else ""))
    print("examples:")
    for slug, oa, na, oh, nh in examples[:22]:
        print(f"  --- {slug}")
        if oa != na:
            print(f"    about: {oa!r}")
            print(f"       -> {na!r}")
        if oh != nh:
            print(f"    hours: {oh!r} -> {nh!r}")

    if args.dry_run:
        print("dry-run: not saved")
        return 0

    i18n_store.save_all(bundle)
    if not args.no_bundle:
        print(i18n_store.build_bundle())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
