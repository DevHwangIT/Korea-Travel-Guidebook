# -*- coding: utf-8 -*-
"""i18n section editors for guidebook content (stdlib)."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from . import i18n_store
from .paths import ROOT
from .translate import BatchStatus, fill_lang_pair, fill_lang_targets

PHRASES_PATH = ROOT / "js" / "korean-phrases-data.js"

# Friendly display names for common i18n key suffixes / known keys
_KEY_LABEL_MAP: dict[str, str] = {
    "title": "제목",
    "pageTitle": "페이지 제목",
    "tipTitle": "팁 제목",
    "intro": "소개",
    "readMore": "더 보기",
    "tapHint": "탭 안내",
    "backCombos": "콤보 목록으로",
    "backList": "목록으로",
    "productTitle": "제품 제목",
    "comboTitle": "콤보 제목",
    "install": "설치 안내",
    "android": "안드로이드",
    "ios": "아이폰",
    "contactTitle": "문의 제목",
    "contactLineTitle": "LINE 제목",
    "contactLineLabel": "LINE 라벨",
    "contactLineId": "LINE 아이디",
    "contactQrAlt": "QR 대체 텍스트",
    "contactQrCaption": "QR 설명",
    "contactFeedbackTitle": "피드백 제목",
    "contactFeedbackDesc": "피드백 설명",
    "contactEmailLabel": "이메일 라벨",
    "contactEmail": "이메일 주소",
    "contactEmailMailto": "이메일 링크",
}

_SUFFIX_LABELS: list[tuple[str, str]] = [
    ("Title", "제목"),
    ("Desc", "짧은 설명"),
    ("_pageTitle", "페이지 제목"),
    ("_lead", "안내 문구"),
    ("Tip", "팁"),
    ("Name", "이름"),
    ("Cat", "카테고리"),
]


@dataclass
class SectionDef:
    id: str
    title: str
    description: str
    root_key: str
    # Optional: only these leaf keys (relative to root). None = all string leaves.
    key_filter: list[str] | None = None
    # Prefix groups for convenience-style namespaces
    group_by_prefix: bool = False
    # Public site path for “사이트 미리보기” (relative to site root)
    preview_path: str = ""
    board_group: str = ""  # dashboard board grouping


SECTIONS: list[SectionDef] = [
    SectionDef(
        "beforeTrip",
        "떠나기 전에",
        "입국·돈·생활·식사·일정 (카테고리별 세부 탭) 안내 글",
        "beforeTrip",
        group_by_prefix=True,
        preview_path="pages/before-trip/",
        board_group="떠나기 전에",
    ),
    SectionDef(
        "festivals",
        "축제 및 행사",
        "공식 VisitKorea·구석구석 링크 안내 문구 (API 연동은 추후)",
        "festivals",
        key_filter=[
            "pageTitle",
            "title",
            "intro",
            "placeholder",
            "regionsTitle",
            "regionsHint",
            "back",
            "linksTitle",
            "linkVisitKoreaEyebrow",
            "linkVisitKoreaTitle",
            "linkVisitKoreaDesc",
            "linkNationwideEyebrow",
            "linkNationwideTitle",
            "linkNationwideDesc",
            "linkKoreanVisitEyebrow",
            "linkKoreanVisitTitle",
            "linkKoreanVisitDesc",
            "linkVisitKoreaEnEyebrow",
            "linkVisitKoreaEnTitle",
            "linkVisitKoreaEnDesc",
            "openExternal",
            "apiLaterNote",
            "sourceLabel",
            "sourceName",
            "sourceNote",
        ],
        preview_path="pages/festivals/",
        board_group="축제 및 행사",
    ),
    SectionDef(
        "tips",
        "여행 팁",
        "일상·식당·교통·쇼핑 팁 글을 관리합니다",
        "tips",
        group_by_prefix=True,
        preview_path="pages/travel-tips/",
        board_group="여행 팁",
    ),
    SectionDef(
        "emergency",
        "긴급 연락",
        "응급·분실 등 긴급 안내 문구를 관리합니다",
        "emergency",
        group_by_prefix=True,
        preview_path="pages/emergency/",
        board_group="준비·안내",
    ),
    SectionDef(
        "shopping",
        "쇼핑 팁",
        "올리브영·다이소·면세·시장 쇼핑 안내 (여행 팁 허브 #shopping 하위 탭)",
        "shopping",
        group_by_prefix=True,
        preview_path="pages/travel-tips/index.html#shopping",
        board_group="여행 팁",
    ),
    SectionDef(
        "souvenir",
        "쇼핑 상품",
        "기념품·추천 제품(실명) 소개 글을 관리합니다",
        "souvenir",
        group_by_prefix=True,
        preview_path="pages/buy/index.html#shopping",
        board_group="쇼핑 및 놀거리",
    ),
    SectionDef(
        "fun",
        "놀거리",
        "피시방·코인노래방·방탈출 카페 등 놀거리 안내",
        "fun",
        group_by_prefix=True,
        preview_path="pages/buy/index.html#fun",
        board_group="쇼핑 및 놀거리",
    ),
    SectionDef(
        "convenience",
        "편의점",
        "편의점 콤보·인기 제품 소개 글을 관리합니다",
        "convenience",
        group_by_prefix=True,
        preview_path="pages/convenience-store/",
        board_group="먹거리",
    ),
    SectionDef(
        "apps",
        "추천 앱",
        "여행에 도움 되는 앱 소개 문구를 고칩니다",
        "apps",
        group_by_prefix=True,
        preview_path="pages/apps/",
        board_group="준비·안내",
    ),
    SectionDef(
        "contact",
        "문의",
        "메인 화면의 LINE·이메일 문의 안내를 수정합니다",
        "home",
        key_filter=[
            "contactTitle",
            "contactLineTitle",
            "contactLineLabel",
            "contactLineId",
            "contactQrAlt",
            "contactQrCaption",
            "contactFeedbackTitle",
            "contactFeedbackDesc",
            "contactEmailLabel",
            "contactEmail",
            "contactEmailMailto",
        ],
        preview_path="index.html",
        board_group="설정",
    ),
    SectionDef(
        "korean",
        "한국어 페이지 문구",
        "유용한 한국어 페이지의 탭·안내 문구입니다 (문장 목록은 별도)",
        "korean",
        preview_path="pages/useful-korean/",
        board_group="준비·안내",
    ),
]


def get_section(section_id: str) -> SectionDef:
    for s in SECTIONS:
        if s.id == section_id:
            return s
    raise ValueError(f"알 수 없는 섹션: {section_id}")


def friendly_key_label(key: str) -> str:
    """Map technical i18n leaf keys to cafe-manager-friendly Korean labels."""
    if key in _KEY_LABEL_MAP:
        return _KEY_LABEL_MAP[key]
    for suffix, label in _SUFFIX_LABELS:
        if key.endswith(suffix) and len(key) > len(suffix):
            prefix = key[: -len(suffix)]
            # c1Title → 콤보 c1 · 제목
            if re.match(r"^c\d+$", prefix):
                return f"항목 {prefix} · {label}"
            return f"{prefix} · {label}"
    # olive_lead style
    if "_" in key:
        base, _, tail = key.partition("_")
        tail_map = {
            "lead": "안내",
            "pageTitle": "페이지 제목",
            "s1": "문단 1",
            "s2": "문단 2",
            "s3": "문단 3",
        }
        if tail in tail_map:
            return f"{base} · {tail_map[tail]}"
    return key


def friendly_group_label(group: str) -> str:
    if group == "_공통":
        return "공통 문구"
    if group == "_기타":
        return "기타"
    if group == "전체":
        return "전체"
    # souvenir / convenience item slugs
    pretty = {
        "olive": "올리브영",
        "daiso": "다이소",
        "mask": "마스크팩",
        "stationery": "문구",
        "snack": "과자",
        "ramen": "라면",
        "tea": "차",
        "honey": "꿀",
        "uniqlo": "유니클로",
        "spa": "스파",
        "socks": "양말",
        "hanbok": "한복",
        "sheet": "시트",
        "sunscreen": "선크림",
        "lipstick": "립",
        "kpop": "케이팝",
        "intro": "소개",
        "biyott": "비요뜨",
        "gongganchun": "공간춘",
        "markjeongsik": "마크정식",
        "carbonara": "카르보나라",
        "eolbaksa": "얼박사",
        "jikgguri": "직구리",
        "melona": "메로나",
        "eri": "전자입국신고(ERI)",
        "docs": "준비서류",
        "immigration": "입국 심사(SES)",
        "money": "현금·카드",
        "wowpass": "Wow Pass",
        "connect": "통신·전원",
        "pack": "짐·예약",
        "solo": "혼자 식사",
        "holidays": "공휴일",
        "avoid": "추천하지 않는 시기",
        "duty": "면세·환급",
        "market": "시장·번화가",
        "kakao": "카카오맵",
        "naver": "네이버지도",
        "papago": "파파고",
        "kakaotalk": "카카오톡",
        "yanolja": "야놀자",
        "yeogi": "여기어때",
        "coupang": "쿠팡",
        "baemin": "배달의민족",
        "yogiyo": "요기요",
        "tmoney": "티머니 GO",
        "kakao-t": "카카오 T",
        "gukbap": "국밥",
        "gomtang": "곰탕",
        "kalguksu": "칼국수",
        "kongguksu": "콩국수",
        "gopchang": "곱창",
        "tangsuyuk": "탕수육",
        "samgyeopsal": "고기집",
        "dakhanmari": "닭한마리",
        "knedlo": "크네들로",
        "bread": "빵·베이커리",
        "nangman-sandwich": "낭만샌드위치(리다이렉트)",
        "butter-bread": "버터빵(리다이렉트)",
        "police": "경찰 (112)",
        "fire": "화재·구급 (119)",
        "tourist": "관광통역 (1330)",
        "guide": "알아두기",
        "daily": "일상생활",
        "restaurant": "식당 이용",
        "transport": "교통 이용",
        "pcbang": "피시방",
        "noraebang": "코인노래방",
        "escape": "방탈출 카페",
        "jjim": "찜질방",
        "manga": "만화카페",
        "boardgame": "보드게임 카페",
        "unmanned": "무인 판매점",
        "photobooth": "셀프 사진관",
        "lotte": "롯데월드",
        "everland": "에버랜드",
    }
    return pretty.get(group, group)


def _is_body_blocks(val: Any) -> bool:
    if not isinstance(val, list):
        return False
    if not val:
        # Empty list under *Body key is still a body slot (not string leaves)
        return True
    first = val[0]
    return isinstance(first, dict) and "type" in first


def _string_leaves(obj: Any, prefix: str = "") -> list[tuple[str, str]]:
    """Return (dotted.path, value) for all string leaves.

    Skips freeform body block arrays (edited via the WYSIWYG body editor).
    """
    out: list[tuple[str, str]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            path = f"{prefix}.{k}" if prefix else str(k)
            if isinstance(v, list) and (
                str(k).endswith("Body") or _is_body_blocks(v)
            ):
                continue
            out.extend(_string_leaves(v, path))
    elif isinstance(obj, list):
        if _is_body_blocks(obj):
            return out
        for i, v in enumerate(obj):
            path = f"{prefix}[{i}]"
            out.extend(_string_leaves(v, path))
    elif isinstance(obj, str):
        out.append((prefix, obj))
    return out


def list_section_keys(section: SectionDef) -> list[str]:
    ko = i18n_store.load_lang("ko")
    root = ko.get(section.root_key)
    if not isinstance(root, dict):
        return []
    leaves = _string_leaves(root)
    keys = [p for p, _ in leaves]
    if section.key_filter is not None:
        allowed = set(section.key_filter)
        keys = [k for k in keys if k in allowed]
    return keys


# Travel-tips article prefix → category (nested hub tabs)
_TIP_ARTICLE_GROUP: dict[str, str] = {
    "map": "daily",
    "cash": "daily",
    "trash": "daily",
    "wifi": "daily",
    "weekend": "daily",
    "restaurant": "restaurant",
    "order": "restaurant",
    "notip": "restaurant",
    "noTip": "restaurant",
    "queue": "restaurant",
    "water": "restaurant",
    "card": "transport",
    "rush": "transport",
    "taxi": "transport",
    "exit": "transport",
    "olive": "shopping",
    "daiso": "shopping",
    "duty": "shopping",
    "market": "shopping",
}


def _group_key(leaf: str) -> str:
    """Heuristic group for convenience/souvenir/apps style keys."""
    if leaf.startswith("cat") or leaf.endswith("CardDesc") or leaf in (
        "intro",
        "readMore",
        "tapHint",
        "backCombos",
        "backList",
        "backHub",
        "productTitle",
        "comboTitle",
        "pageTitle",
        "title",
        "tipTitle",
        "install",
        "android",
        "ios",
        "item",
        "number",
        "contactsTitle",
        "desc",
        "stayCat",
        "shopCat",
        "payCat",
    ):
        return "_공통"
    # apps: talkName/talkDesc → kakaotalk detail page
    if leaf.startswith("talk"):
        return "kakaotalk"
    # emergency: police / policeNumber / policeBody → police
    m = re.match(
        r"^(police|fire|tourist|guide)(Number|Title|Body.*)?$",
        leaf,
        re.I,
    )
    if m:
        return m.group(1).lower()
    # tips: mapTitle / cashMistake / restaurantBody1 / noTipBody / tabMap → groups
    m = re.match(
        r"^tab(Map|Cash|Trash|Wifi|Weekend|Order|NoTip|Queue|Water|Card|Rush|Taxi|Exit|"
        r"Olive|Daiso|Duty|Market)$",
        leaf,
    )
    if m:
        tab = m.group(1)
        tab_key = "noTip" if tab == "NoTip" else tab[0].lower() + tab[1:]
        tab_key = {
            "map": "map",
            "cash": "cash",
            "trash": "trash",
            "wifi": "wifi",
            "weekend": "weekend",
            "order": "order",
            "noTip": "noTip",
            "queue": "queue",
            "water": "water",
            "card": "card",
            "rush": "rush",
            "taxi": "taxi",
            "exit": "exit",
            "olive": "olive",
            "daiso": "daiso",
            "duty": "duty",
            "market": "market",
        }.get(tab_key, tab_key)
        return _TIP_ARTICLE_GROUP.get(tab_key, "_공통")
    m = re.match(
        r"^(map|cash|trash|wifi|weekend|restaurant|queue|water|card|rush|taxi|exit|noTip)"
        r"(Title|Mistake|Body\d*)$",
        leaf,
    )
    if m:
        return _TIP_ARTICLE_GROUP[m.group(1)]
    m = re.match(r"^(daily|restaurant|transport|shopping)Body$", leaf, re.I)
    if m:
        return m.group(1).lower()
    m = re.match(r"^cat(Daily|Restaurant|Transport|Shopping)(Intro)?$", leaf)
    if m:
        return {
            "Daily": "daily",
            "Restaurant": "restaurant",
            "Transport": "transport",
            "Shopping": "shopping",
        }[m.group(1)]
    # beforeTrip: tabEri / eriBody / catEntry → eri|docs|…
    tab_map = {
        "Eri": "eri",
        "Docs": "docs",
        "Immigration": "immigration",
        "Money": "money",
        "Wowpass": "wowpass",
        "Connect": "connect",
        "Pack": "pack",
        "Solo": "solo",
        "Holidays": "holidays",
        "Avoid": "avoid",
    }
    m = re.match(
        r"^tab(Eri|Docs|Immigration|Money|Wowpass|Connect|Pack|Solo|Holidays|Avoid)$",
        leaf,
    )
    if m:
        return tab_map[m.group(1)]
    m = re.match(r"^cat(Entry|Money|Life|Dining|Schedule)(Intro)?$", leaf, re.I)
    if m:
        return "_공통"
    m = re.match(
        r"^(eri|docs|immigration|money|wowpass|connect|pack|solo|holidays|avoid)"
        r"(\d+|Title|Body.*)?$",
        leaf,
        re.I,
    )
    if m:
        return m.group(1).lower()
    # olive1 / daiso2 style prose next to freeform bodies
    m = re.match(r"^([a-z][a-z0-9-]*)\d+$", leaf, re.I)
    if m:
        return m.group(1).lower()
    # c1Title → c1, biyott_lead → biyott, kakaoName → kakao
    # oliveBody1 / oliveTip → olive (legacy prose next to freeform *Body)
    m = re.match(r"^(c\d+)[_A-Z]", leaf)
    if m:
        return m.group(1)
    m = re.match(
        r"^([a-z0-9-]+?)(?:Body\d*|Tip|Title|Desc|_pageTitle|_lead|_)",
        leaf,
        re.I,
    )
    if m:
        return m.group(1)
    m = re.match(r"^([a-z0-9-]+)(?:Title|Desc|_)", leaf, re.I)
    if m:
        return m.group(1)
    m = re.match(r"^([a-z]+)(?:Cat|Name|Desc)$", leaf, re.I)
    if m:
        return m.group(1)
    return "_기타"


def group_keys(section: SectionDef, keys: list[str]) -> dict[str, list[str]]:
    if not section.group_by_prefix:
        return {"전체": keys}
    groups: dict[str, list[str]] = {}
    for k in keys:
        g = _group_key(k)
        groups.setdefault(g, []).append(k)
    # Stable: _공통 first, then alpha
    def sort_key(name: str) -> tuple[int, str]:
        if name == "_공통":
            return (0, name)
        if name == "_기타":
            return (2, name)
        return (1, name)

    return {g: groups[g] for g in sorted(groups, key=sort_key)}


def load_entry_texts(section: SectionDef, key: str) -> dict[str, str]:
    bundle = i18n_store.load_all()
    out: dict[str, str] = {}
    for lang in i18n_store.LANGS:
        root = bundle[lang].get(section.root_key) or {}
        val = root.get(key) if isinstance(root, dict) else None
        out[lang] = str(val) if val is not None else ""
    return out


def save_entry_texts(
    section: SectionDef,
    updates: dict[str, dict[str, str]],
    *,
    force_translate: bool = False,
) -> tuple[list[str], BatchStatus]:
    """updates: { key: {ko,en,ja,zh} } — EN/JA/ZH filled from KO when blank/unchanged."""
    notes: list[str] = []
    status = BatchStatus()
    bundle = i18n_store.load_all()
    for key, texts in updates.items():
        ko = (texts.get("ko") or "").strip()
        form: dict[str, str] = {}
        for lang in ("en", "ja", "zh"):
            val = (texts.get(lang) or "").strip()
            form[lang] = "" if val == ko else val
        old = {
            lang: str(
                ((bundle[lang].get(section.root_key) or {}).get(key) or "")
            ).strip()
            if isinstance(bundle[lang].get(section.root_key), dict)
            else ""
            for lang in i18n_store.LANGS
        }
        if all(form.values()) and not force_translate:
            filled = dict(form)
            status.reused += 1
        else:
            filled = fill_lang_targets(
                ko,
                old=old,
                force=force_translate,
                status=status,
            )
            for lang in ("en", "ja", "zh"):
                if form[lang] and not force_translate:
                    filled[lang] = form[lang]
        for lang, val in (
            ("ko", ko),
            ("en", filled.get("en") or ko),
            ("ja", filled.get("ja") or ko),
            ("zh", filled.get("zh") or ko),
        ):
            root = bundle[lang].setdefault(section.root_key, {})
            if not isinstance(root, dict):
                raise ValueError(f"{section.root_key}가 객체가 아닙니다 ({lang})")
            root[key] = val
    i18n_store.save_all(bundle)
    notes.append(f"{section.title}: {len(updates)}개 항목 저장")
    notes.append(i18n_store.build_bundle())
    return notes, status


def add_string_key(
    section: SectionDef,
    key: str,
    texts: dict[str, str],
    *,
    force_translate: bool = False,
) -> tuple[list[str], BatchStatus]:
    key = key.strip()
    if not key or not re.match(r"^[A-Za-z0-9_-]+$", key):
        raise ValueError("키는 영문·숫자·_- 만 가능합니다.")
    status = BatchStatus()
    ko = (texts.get("ko") or "").strip()
    form: dict[str, str] = {}
    for lang in ("en", "ja", "zh"):
        val = (texts.get(lang) or "").strip()
        form[lang] = "" if val == ko else val
    if all(form.values()) and not force_translate:
        filled = dict(form)
        status.reused += 1
    else:
        filled = fill_lang_targets(ko, force=True, status=status)
        for lang in ("en", "ja", "zh"):
            if form[lang]:
                filled[lang] = form[lang]
    bundle = i18n_store.load_all()
    for lang, val in (
        ("ko", ko),
        ("en", filled.get("en") or ko),
        ("ja", filled.get("ja") or ko),
        ("zh", filled.get("zh") or ko),
    ):
        root = bundle[lang].setdefault(section.root_key, {})
        if key in root:
            raise ValueError(f"이미 있는 키: {section.root_key}.{key} ({lang})")
        root[key] = val
    i18n_store.save_all(bundle)
    return [
        f"항목 추가: {friendly_key_label(key)}",
        i18n_store.build_bundle(),
    ], status


def delete_string_key(section: SectionDef, key: str) -> list[str]:
    bundle = i18n_store.load_all()
    for lang in i18n_store.LANGS:
        root = bundle[lang].get(section.root_key)
        if isinstance(root, dict) and key in root:
            del root[key]
    i18n_store.save_all(bundle)
    return [f"항목 삭제: {friendly_key_label(key)}", i18n_store.build_bundle()]


# --- Useful Korean phrases (js/korean-phrases-data.js) ---


def load_phrases() -> dict[str, list[dict[str, str]]]:
    text = PHRASES_PATH.read_text(encoding="utf-8")
    # window.KOREAN_PHRASES = {...};
    m = re.search(r"window\.KOREAN_PHRASES\s*=\s*(\{.*\})\s*;?\s*$", text, re.DOTALL)
    if not m:
        raise ValueError("korean-phrases-data.js 파싱 실패")
    return json.loads(m.group(1))


def save_phrases(data: dict[str, list[dict[str, str]]]) -> list[str]:
    body = json.dumps(data, ensure_ascii=False, indent=2)
    PHRASES_PATH.write_text(
        f"window.KOREAN_PHRASES = {body};\n",
        encoding="utf-8",
        newline="\n",
    )
    return ["문장 목록을 저장했어요"]


def list_phrase_categories() -> list[str]:
    return list(load_phrases().keys())


PHRASE_CAT_LABELS: dict[str, str] = {
    "daily": "일상",
    "order": "주문",
    "transport": "교통",
    "emergency": "긴급",
    "shopping": "쇼핑",
    "greeting": "인사",
    "thanks": "감사",
}


def phrase_cat_label(cat: str) -> str:
    return PHRASE_CAT_LABELS.get(cat, cat)


def get_phrases(category: str) -> list[dict[str, str]]:
    data = load_phrases()
    if category not in data:
        raise ValueError(f"카테고리 없음: {category}")
    return list(data[category])


def save_phrase_item(
    category: str,
    phrase_id: str,
    fields: dict[str, str],
    *,
    is_new: bool = False,
    force_translate: bool = False,
) -> tuple[list[str], BatchStatus]:
    """Save phrase; auto-translate meaning (en/ja). Romanization (rom) is never translated."""
    data = load_phrases()
    items = data.setdefault(category, [])
    phrase_id = phrase_id.strip()
    if not phrase_id:
        raise ValueError("id 필수")
    status = BatchStatus()
    ko = (fields.get("ko") or "").strip()
    if not ko:
        raise ValueError("한국어 문장은 필수입니다.")
    form_en = (fields.get("en") or "").strip()
    form_ja = (fields.get("ja") or "").strip()
    if form_en == ko:
        form_en = ""
    if form_ja == ko:
        form_ja = ""
    idx = next((i for i, p in enumerate(items) if p.get("id") == phrase_id), None)
    old = items[idx] if idx is not None else {}
    if form_en and form_ja and not force_translate:
        en, ja = form_en, form_ja
        status.reused += 1
    else:
        en, ja = fill_lang_pair(
            ko,
            old_ko=str(old.get("ko") or ""),
            old_en=str(old.get("en") or ""),
            old_ja=str(old.get("ja") or ""),
            force=force_translate or is_new,
            status=status,
        )
        if form_en and not force_translate:
            en = form_en
        if form_ja and not force_translate:
            ja = form_ja
    entry = {
        "id": phrase_id,
        "ko": ko,
        "rom": (fields.get("rom") or "").strip(),
        "en": en or ko,
        "ja": ja or ko,
    }
    if is_new:
        if idx is not None:
            raise ValueError(f"이미 있는 id: {phrase_id}")
        items.append(entry)
    else:
        if idx is None:
            raise ValueError(f"없는 id: {phrase_id}")
        items[idx] = entry
    return save_phrases(data), status


def delete_phrase_item(category: str, phrase_id: str) -> list[str]:
    data = load_phrases()
    items = data.get(category) or []
    new_items = [p for p in items if p.get("id") != phrase_id]
    if len(new_items) == len(items):
        raise ValueError(f"없는 id: {phrase_id}")
    data[category] = new_items
    return save_phrases(data)


@dataclass
class DashboardCard:
    href: str
    title: str
    desc: str
    count: str = ""
    group: str = "기타"


def dashboard_cards() -> list[DashboardCard]:
    from . import content  # local import to avoid cycle at module load

    meals_n = len(content.list_dishes("meals"))
    dess_n = len(content.list_dishes("desserts"))
    shops_n = len(content.list_shops())
    from . import places as _places
    places_n = len(_places.list_places())
    cards = [
        DashboardCard(
            "/section?id=beforeTrip",
            "떠나기 전에",
            "서류·돈·통신·짐·혼자 식사 안내",
            "",
            "떠나기 전에",
        ),
        DashboardCard(
            "/section?id=emergency",
            "긴급 연락",
            "응급·분실 안내",
            "",
            "준비·안내",
        ),
        DashboardCard(
            "/dishes?kind=meals",
            "식사",
            "한식·분식 등 음식 소개",
            f"{meals_n}개",
            "먹거리",
        ),
        DashboardCard(
            "/dishes?kind=desserts",
            "디저트",
            "카페·빵·빙수 소개",
            f"{dess_n}개",
            "먹거리",
        ),
        DashboardCard(
            "/shops",
            "가게",
            "음식에 연결된 가게·브랜드 글",
            f"{shops_n}개",
            "먹거리",
        ),
        DashboardCard(
            "/section?id=convenience",
            "편의점",
            "콤보·인기 제품 소개",
            "",
            "먹거리",
        ),
        DashboardCard(
            "/section?id=shopping",
            "쇼핑 팁",
            "올리브영·다이소·면세·시장 안내",
            "",
            "쇼핑 및 놀거리",
        ),
        DashboardCard(
            "/section?id=souvenir",
            "쇼핑 상품",
            "기념품·추천 제품(실명) 소개",
            "",
            "쇼핑 및 놀거리",
        ),
        DashboardCard(
            "/section?id=fun",
            "놀거리",
            "피시방·코인노래방·방탈출 카페 등",
            "",
            "쇼핑 및 놀거리",
        ),
        DashboardCard(
            "/places",
            "대표 명소",
            "전국 명소 지도·핀 (도시·자연·유적·공항·안내)",
            f"{places_n}개",
            "명소",
        ),
        DashboardCard(
            "/section?id=tips",
            "여행 팁",
            "일상·식당·교통·쇼핑 팁",
            "",
            "여행 팁",
        ),
        DashboardCard(
            "/section?id=festivals",
            "축제 및 행사",
            "공식 VisitKorea 링크 안내 (API·지역별 정리는 추후)",
            "",
            "축제 및 행사",
        ),
    ]
    for s in SECTIONS:
        if s.id in (
            "beforeTrip",
            "tips",
            "festivals",
            "emergency",
            "shopping",
            "souvenir",
            "fun",
            "convenience",
        ):
            continue
        keys = list_section_keys(s)
        cards.append(
            DashboardCard(
                f"/section?id={s.id}",
                s.title,
                s.description,
                f"{len(keys)}항목" if keys else "",
                s.board_group or "준비·안내",
            )
        )
    try:
        phrases = load_phrases()
        n = sum(len(v) for v in phrases.values())
    except Exception:  # noqa: BLE001
        n = 0
    cards.append(
        DashboardCard(
            "/phrases",
            "유용한 한국어",
            "여행용 한마디·발음·번역 문장",
            f"{n}문장",
            "준비·안내",
        )
    )
    cards.append(
        DashboardCard(
            "/version",
            "사이트 새로고침",
            "배포 전에 한 번 눌러 캐시를 갱신하세요",
            "",
            "설정",
        )
    )
    cards.append(
        DashboardCard(
            "/tools/migrate-body",
            "본문 정리 (전문가용)",
            "예전 문구를 새 글 형식으로 옮길 때",
            "",
            "설정",
        )
    )
    return cards


BOARD_ORDER = (
    "떠나기 전에",
    "준비·안내",
    "먹거리",
    "쇼핑 및 놀거리",
    "명소",
    "축제 및 행사",
    "여행 팁",
    "설정",
)
