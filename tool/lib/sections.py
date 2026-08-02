# -*- coding: utf-8 -*-
"""i18n section editors for guidebook content (stdlib)."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import i18n_store
from .paths import ROOT

PHRASES_PATH = ROOT / "js" / "korean-phrases-data.js"


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


SECTIONS: list[SectionDef] = [
    SectionDef(
        "convenience",
        "편의점",
        "콤보·제품 문구 (convenience.*) + pages/convenience-store/",
        "convenience",
        group_by_prefix=True,
    ),
    SectionDef(
        "tips",
        "여행 팁",
        "tips.* 카테고리·카드 문구",
        "tips",
    ),
    SectionDef(
        "beforeTrip",
        "여행 전 준비",
        "beforeTrip.* 서류·돈·통신·짐",
        "beforeTrip",
    ),
    SectionDef(
        "souvenir",
        "기념품",
        "souvenir.* 아이템 카드",
        "souvenir",
        group_by_prefix=True,
    ),
    SectionDef(
        "shopping",
        "쇼핑",
        "shopping.* 팁",
        "shopping",
    ),
    SectionDef(
        "apps",
        "앱",
        "apps.* 추천 앱",
        "apps",
        group_by_prefix=True,
    ),
    SectionDef(
        "emergency",
        "긴급",
        "emergency.* 긴급 연락처",
        "emergency",
    ),
    SectionDef(
        "contact",
        "메인 문의",
        "home.contact* (LINE·이메일)",
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
    ),
    SectionDef(
        "korean",
        "유용한 한국어 (페이지 문구)",
        "korean.* 탭/안내 문구 — 문장 데이터는 별도 메뉴",
        "korean",
    ),
]


def get_section(section_id: str) -> SectionDef:
    for s in SECTIONS:
        if s.id == section_id:
            return s
    raise ValueError(f"알 수 없는 섹션: {section_id}")


def _string_leaves(obj: Any, prefix: str = "") -> list[tuple[str, str]]:
    """Return (dotted.path, value) for all string leaves."""
    out: list[tuple[str, str]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            path = f"{prefix}.{k}" if prefix else str(k)
            out.extend(_string_leaves(v, path))
    elif isinstance(obj, list):
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


def _group_key(leaf: str) -> str:
    """Heuristic group for convenience/souvenir/apps style keys."""
    # c1Title → c1, biyott_lead → biyott, kakaoName → kakao
    m = re.match(r"^(c\d+)[_A-Z]", leaf)
    if m:
        return m.group(1)
    m = re.match(r"^([a-z0-9-]+)(?:Title|Desc|_)", leaf, re.I)
    if m:
        return m.group(1)
    m = re.match(r"^([a-z]+)(?:Cat|Name|Desc)$", leaf, re.I)
    if m:
        return m.group(1)
    if leaf.startswith("cat") or leaf in (
        "intro",
        "readMore",
        "tapHint",
        "backCombos",
        "backList",
        "productTitle",
        "comboTitle",
        "pageTitle",
        "title",
        "tipTitle",
        "install",
        "android",
        "ios",
    ):
        return "_공통"
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
) -> list[str]:
    """updates: { key: {ko,en,ja} }"""
    notes: list[str] = []
    bundle = i18n_store.load_all()
    for key, texts in updates.items():
        for lang in i18n_store.LANGS:
            root = bundle[lang].setdefault(section.root_key, {})
            if not isinstance(root, dict):
                raise ValueError(f"{section.root_key}가 객체가 아닙니다 ({lang})")
            val = (texts.get(lang) or "").strip()
            if lang != "ko" and not val:
                val = (texts.get("ko") or "").strip()
            root[key] = val
    i18n_store.save_all(bundle)
    notes.append(f"{section.title}: {len(updates)}개 키 저장")
    notes.append(i18n_store.build_bundle())
    return notes


def add_string_key(section: SectionDef, key: str, texts: dict[str, str]) -> list[str]:
    key = key.strip()
    if not key or not re.match(r"^[A-Za-z0-9_-]+$", key):
        raise ValueError("키는 영문·숫자·_- 만 가능합니다.")
    bundle = i18n_store.load_all()
    for lang in i18n_store.LANGS:
        root = bundle[lang].setdefault(section.root_key, {})
        if key in root:
            raise ValueError(f"이미 있는 키: {section.root_key}.{key} ({lang})")
        val = (texts.get(lang) or texts.get("ko") or "").strip()
        root[key] = val
    i18n_store.save_all(bundle)
    return [
        f"키 추가: {section.root_key}.{key}",
        i18n_store.build_bundle(),
    ]


def delete_string_key(section: SectionDef, key: str) -> list[str]:
    bundle = i18n_store.load_all()
    for lang in i18n_store.LANGS:
        root = bundle[lang].get(section.root_key)
        if isinstance(root, dict) and key in root:
            del root[key]
    i18n_store.save_all(bundle)
    return [f"키 삭제: {section.root_key}.{key}", i18n_store.build_bundle()]


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
    return [f"저장: {PHRASES_PATH.relative_to(ROOT).as_posix()}"]


def list_phrase_categories() -> list[str]:
    return list(load_phrases().keys())


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
) -> list[str]:
    data = load_phrases()
    items = data.setdefault(category, [])
    phrase_id = phrase_id.strip()
    if not phrase_id:
        raise ValueError("id 필수")
    entry = {
        "id": phrase_id,
        "ko": (fields.get("ko") or "").strip(),
        "rom": (fields.get("rom") or "").strip(),
        "en": (fields.get("en") or "").strip(),
        "ja": (fields.get("ja") or "").strip(),
    }
    if not entry["ko"]:
        raise ValueError("한국어(ko) 필수")
    idx = next((i for i, p in enumerate(items) if p.get("id") == phrase_id), None)
    if is_new:
        if idx is not None:
            raise ValueError(f"이미 있는 id: {phrase_id}")
        items.append(entry)
    else:
        if idx is None:
            raise ValueError(f"없는 id: {phrase_id}")
        items[idx] = entry
    return save_phrases(data)


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


def dashboard_cards() -> list[DashboardCard]:
    from . import content  # local import to avoid cycle at module load

    meals_n = len(content.list_dishes("meals"))
    dess_n = len(content.list_dishes("desserts"))
    shops_n = len(content.list_shops())
    cards = [
        DashboardCard(
            "/dishes?kind=meals",
            "식사 음식",
            "한식·분식 등 식사 카테고리 소개와 설명",
            str(meals_n),
        ),
        DashboardCard(
            "/dishes?kind=desserts",
            "디저트",
            "카페·빵·빙수 등 디저트 소개와 설명",
            str(dess_n),
        ),
        DashboardCard(
            "/shops",
            "가게",
            "음식에 연결된 가게·브랜드와 메뉴 사진",
            str(shops_n),
        ),
    ]
    for s in SECTIONS:
        keys = list_section_keys(s)
        cards.append(
            DashboardCard(
                f"/section?id={s.id}",
                s.title,
                s.description,
                f"{len(keys)}키",
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
            "유용한 한국어 문장",
            "여행용 한마디·발음 표기·번역 문장 모음",
            f"{n}문장",
        )
    )
    cards.append(
        DashboardCard(
            "/version",
            "버전 업데이트",
            "배포 전 캐시 버전과 HTML ?v= 일괄 갱신",
            "",
        )
    )
    cards.append(
        DashboardCard(
            "/tools/patch-menus",
            "메뉴 갤러리 패치",
            "기존 가게 페이지에 다중 메뉴 갤러리 맞추기",
            "",
        )
    )
    return cards
