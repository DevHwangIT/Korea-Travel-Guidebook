# -*- coding: utf-8 -*-
"""Freeform content body blocks for guidebook sections (beforeTrip / shopping / convenience / souvenir)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from . import i18n_store
from .shop_body import normalize_body


@dataclass(frozen=True)
class BodySlot:
    """One freeform body editor slot under a section root."""

    key: str  # leaf key under root, e.g. docsBody
    label: str
    image_folder: str  # section key → page media (souvenir/convenience/…) or Images/
    image_slug: str  # page slug / file prefix (body-N.jpg or {slug}-body-N.jpg)
    group: str | None = None  # for group_by_prefix sections; None = always show


# One post per detail page under pages/before-trip/{slug}/
BEFORE_TRIP_SLOTS: list[BodySlot] = [
    BodySlot("docsBody", "서류·입국", "before-trip", "docs", group="docs"),
    BodySlot("moneyBody", "돈·카드", "before-trip", "money", group="money"),
    BodySlot("connectBody", "통신·전원", "before-trip", "connect", group="connect"),
    BodySlot("packBody", "짐·예약", "before-trip", "pack", group="pack"),
    BodySlot("soloBody", "혼자 식사", "before-trip", "solo", group="solo"),
]

SHOPPING_SLOTS: list[BodySlot] = [
    BodySlot("oliveBody", "뷰티·올리브영", "shopping", "olive", group="olive"),
    BodySlot("daisoBody", "다이소·생활", "shopping", "daiso", group="daiso"),
    BodySlot("dutyBody", "면세·환급", "shopping", "duty", group="duty"),
    BodySlot("marketBody", "시장·번화가", "shopping", "market", group="market"),
]

# One post per category under pages/travel-tips/{slug}/
TIPS_SLOTS: list[BodySlot] = [
    BodySlot("dailyBody", "일상생활", "travel-tips", "daily", group="daily"),
    BodySlot(
        "restaurantBody", "식당 이용", "travel-tips", "restaurant", group="restaurant"
    ),
    BodySlot(
        "transportBody", "교통 이용", "travel-tips", "transport", group="transport"
    ),
    # Shopping tips live under pages/shopping/*; board links from tips hub on public site
]

FUN_SLOTS: list[BodySlot] = [
    BodySlot("pcbangBody", "피시방", "fun", "pcbang", group="pcbang"),
    BodySlot("noraebangBody", "코인노래방", "fun", "coin-noraebang", group="noraebang"),
    BodySlot("escapeBody", "방탈출 카페", "fun", "escape-room", group="escape"),
    BodySlot("jjimBody", "찜질방", "fun", "jjimjilbang", group="jjim"),
    BodySlot("mangaBody", "만화카페", "fun", "manga-cafe", group="manga"),
    BodySlot("boardgameBody", "보드게임 카페", "fun", "boardgame-cafe", group="boardgame"),
    BodySlot("unmannedBody", "무인 판매점", "fun", "unmanned-store", group="unmanned"),
    BodySlot("photoboothBody", "셀프 사진관", "fun", "photo-booth", group="photobooth"),
    BodySlot("lotteBody", "롯데월드", "fun", "lotte-world", group="lotte"),
    BodySlot("everlandBody", "에버랜드", "fun", "everland", group="everland"),
]

# One post per app under pages/apps/{slug}/
APPS_SLOTS: list[BodySlot] = [
    BodySlot("kakaoBody", "카카오맵", "apps", "kakao", group="kakao"),
    BodySlot("naverBody", "네이버지도", "apps", "naver", group="naver"),
    BodySlot("papagoBody", "파파고", "apps", "papago", group="papago"),
    BodySlot("kakaotalkBody", "카카오톡", "apps", "kakaotalk", group="kakaotalk"),
    BodySlot("yanoljaBody", "야놀자", "apps", "yanolja", group="yanolja"),
    BodySlot("yeogiBody", "여기어때", "apps", "yeogi", group="yeogi"),
    BodySlot("coupangBody", "쿠팡", "apps", "coupang", group="coupang"),
    BodySlot("baeminBody", "배달의민족", "apps", "baemin", group="baemin"),
    BodySlot("yogiyoBody", "요기요", "apps", "yogiyo", group="yogiyo"),
    BodySlot("tmoneyBody", "티머니 GO", "apps", "tmoney", group="tmoney"),
]

# One post per contact under pages/emergency/{slug}/
EMERGENCY_SLOTS: list[BodySlot] = [
    BodySlot("policeBody", "경찰 (112)", "emergency", "police", group="police"),
    BodySlot("fireBody", "화재·구급 (119)", "emergency", "fire", group="fire"),
    BodySlot(
        "touristBody", "관광통역 (1330)", "emergency", "tourist", group="tourist"
    ),
    BodySlot("guideBody", "알아두기", "emergency", "guide", group="guide"),
]

# Convenience detail pages: (body_key, image_slug, prose_prefix used in i18n)
# prose_prefix maps to {prefix}_lead / {prefix}_s1 / … or special biyott fields
CONVENIENCE_PAGE_BODIES: list[tuple[str, str, str]] = [
    ("introBody", "intro", "intro"),
    ("biyottBody", "biyott", "biyott"),
    ("gongganchunBody", "gongganchun", "gongganchun"),
    ("markjeongsikBody", "markjeongsik", "markjeongsik"),
    ("carbonaraBody", "carbonara", "carbonara"),
    ("eolbaksaBody", "eolbaksa", "eolbaksa"),
    ("jikgguriBody", "jikgguri", "jikgguri"),
    ("melonaBody", "melona", "melona"),
    ("blue-lemonade-milkisBody", "blue-lemonade-milkis", "blue-lemonade-milkis"),
    ("choco-banana-latteBody", "choco-banana-latte", "choco-banana-latte"),
    ("banana-americanoBody", "banana-americano", "banana-americano"),
    # Legacy cN_ pages (folder slug ≠ prefix)
    ("c1Body", "banana-coffee", "c1"),
    ("c2Body", "kimbap-milk", "c2"),
    ("c3Body", "ramyeon-egg", "c3"),
    ("c4Body", "yakgwa-coffee", "c4"),
    ("c5Body", "chicken-beer", "c5"),
    ("c6Body", "melona-coffee", "c6"),
]

SOUVENIR_SLUGS: list[str] = [
    "mask",
    "stationery",
    "olive",
    "daiso",
    "snack",
    "ramen",
    "tea",
    "honey",
    "uniqlo",
    "spa",
    "socks",
    "hanbok",
    "sheet",
    "sunscreen",
    "lipstick",
    "kpop",
]


def is_body_blocks_value(val: Any) -> bool:
    """True if value looks like a freeform body block list."""
    if not isinstance(val, list):
        return False
    if not val:
        return True
    first = val[0]
    return isinstance(first, dict) and "type" in first


def path_get(root: dict[str, Any], dotted: str) -> Any:
    cur: Any = root
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def path_set(root: dict[str, Any], dotted: str, value: Any) -> None:
    parts = dotted.split(".")
    cur: Any = root
    for part in parts[:-1]:
        nxt = cur.get(part)
        if not isinstance(nxt, dict):
            nxt = {}
            cur[part] = nxt
        cur = nxt
    cur[parts[-1]] = value


def get_body_at(
    root_key: str,
    leaf_key: str,
    *,
    bundle: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    data = bundle or i18n_store.load_all()
    for lang in i18n_store.LANGS:
        root = data[lang].get(root_key)
        if not isinstance(root, dict):
            continue
        raw = root.get(leaf_key)
        if isinstance(raw, list) and raw:
            return normalize_body(raw)
    for lang in i18n_store.LANGS:
        root = data[lang].get(root_key)
        if not isinstance(root, dict):
            continue
        raw = root.get(leaf_key)
        if isinstance(raw, list):
            return normalize_body(raw)
    return []


def write_body_at(
    root_key: str,
    leaf_key: str,
    blocks: list[dict[str, Any]],
    *,
    bundle: dict[str, dict[str, Any]] | None = None,
    persist: bool = True,
) -> list[str]:
    notes: list[str] = []
    normalized = normalize_body(blocks)
    owns = bundle is None
    data = bundle if bundle is not None else i18n_store.load_all()
    for lang in i18n_store.LANGS:
        root = data[lang].setdefault(root_key, {})
        if not isinstance(root, dict):
            raise ValueError(f"{root_key}가 객체가 아닙니다 ({lang})")
        root[leaf_key] = normalized
    if persist and owns:
        i18n_store.save_all(data)
        notes.append(i18n_store.build_bundle())
    notes.append(f"{root_key}.{leaf_key} 저장 ({len(normalized)}개)")
    return notes


def slots_for_section(section_id: str, group: str = "") -> list[BodySlot]:
    """Body editors to show on a section admin screen."""
    if section_id == "beforeTrip":
        if group and group not in ("_공통", "_기타", "전체"):
            return [s for s in BEFORE_TRIP_SLOTS if s.group == group]
        if group in ("_공통", "_기타"):
            return []
        return list(BEFORE_TRIP_SLOTS)
    if section_id == "shopping":
        if group and group not in ("_공통", "_기타", "전체"):
            return [s for s in SHOPPING_SLOTS if s.group == group]
        if group in ("_공통", "_기타"):
            return []
        return list(SHOPPING_SLOTS)
    if section_id == "tips":
        if group and group not in ("_공통", "_기타", "전체"):
            return [s for s in TIPS_SLOTS if s.group == group]
        if group in ("_공통", "_기타"):
            return []
        return list(TIPS_SLOTS)
    if section_id == "apps":
        if group and group not in ("_공통", "_기타", "전체"):
            return [s for s in APPS_SLOTS if s.group == group]
        if group in ("_공통", "_기타"):
            return []
        return list(APPS_SLOTS)
    if section_id == "emergency":
        if group and group not in ("_공통", "_기타", "전체"):
            return [s for s in EMERGENCY_SLOTS if s.group == group]
        if group in ("_공통", "_기타"):
            return []
        return list(EMERGENCY_SLOTS)
    if section_id == "fun":
        if group and group not in ("_공통", "_기타", "전체"):
            return [s for s in FUN_SLOTS if s.group == group]
        if group in ("_공통", "_기타"):
            return []
        return list(FUN_SLOTS)
    if section_id == "convenience":
        slots: list[BodySlot] = []
        for body_key, image_slug, prose_prefix in CONVENIENCE_PAGE_BODIES:
            # Group id from admin group_keys heuristic
            if body_key == "introBody":
                g = "_공통"
            elif prose_prefix.startswith("c") and prose_prefix[1:].isdigit():
                g = prose_prefix
            else:
                g = prose_prefix
            # Prefer human labels for cafe-style admin tabs
            pretty = {
                "intro": "소개",
                "biyott": "비요뜨",
                "gongganchun": "공간춘",
                "markjeongsik": "마크정식",
                "carbonara": "카르보나라",
                "eolbaksa": "얼박사",
                "jikgguri": "직구리",
                "melona": "메로나",
                "blue-lemonade-milkis": "블루 레몬에이드 밀키스",
                "choco-banana-latte": "초코 바나나 라떼",
                "banana-americano": "바나나 아메리카노",
                "c1": "콤보 1",
                "c2": "콤보 2",
                "c3": "콤보 3",
                "c4": "콤보 4",
                "c5": "콤보 5",
                "c6": "콤보 6",
            }.get(prose_prefix, prose_prefix)
            label = pretty
            slots.append(
                BodySlot(
                    body_key,
                    label,
                    "convenience",
                    image_slug,
                    group=g,
                )
            )
        if group:
            return [s for s in slots if s.group == group]
        return slots
    if section_id == "souvenir":
        souvenir_labels = {
            "mask": "마스크팩",
            "stationery": "문구",
            "olive": "올리브영",
            "daiso": "다이소",
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
        }
        slots = [
            BodySlot(
                f"{slug}Body",
                souvenir_labels.get(slug, slug),
                "souvenir",
                slug,
                group=slug,
            )
            for slug in SOUVENIR_SLUGS
        ]
        if group and group not in ("_공통", "_기타"):
            return [s for s in slots if s.group == group]
        if group in ("_공통", "_기타"):
            return []
        return slots
    return []


def _text_block(ko: str, en: str, ja: str) -> dict[str, Any] | None:
    ko, en, ja = ko.strip(), en.strip(), ja.strip()
    if not ko and not en and not ja:
        return None
    return {
        "type": "text",
        "ko": ko or en or ja,
        "en": en or ko or ja,
        "ja": ja or ko or en,
    }


def _lang_vals(
    data: dict[str, dict[str, Any]], root_key: str, leaf: str
) -> dict[str, str]:
    out: dict[str, str] = {}
    for lang in i18n_store.LANGS:
        root = data[lang].get(root_key) or {}
        val = root.get(leaf) if isinstance(root, dict) else None
        out[lang] = str(val).strip() if isinstance(val, str) else ""
    return out


def _append_titled(
    blocks: list[dict[str, Any]],
    data: dict[str, dict[str, Any]],
    root_key: str,
    title_key: str,
    body_key: str,
) -> None:
    titles = _lang_vals(data, root_key, title_key)
    bodies = _lang_vals(data, root_key, body_key)
    if not any(bodies.values()) and not any(titles.values()):
        return

    def join(lang: str) -> str:
        t = titles.get(lang) or titles.get("ko") or ""
        b = bodies.get(lang) or bodies.get("ko") or ""
        if t and b:
            return f"{t}\n\n{b}"
        return t or b

    block = _text_block(join("ko"), join("en"), join("ja"))
    if block:
        blocks.append(block)


def _append_plain(
    blocks: list[dict[str, Any]],
    data: dict[str, dict[str, Any]],
    root_key: str,
    leaf: str,
) -> None:
    vals = _lang_vals(data, root_key, leaf)
    block = _text_block(vals["ko"], vals["en"], vals["ja"])
    if block:
        blocks.append(block)


def migrate_before_trip(
    *,
    force: bool = False,
    bundle: dict[str, dict[str, Any]] | None = None,
    persist: bool = True,
) -> list[str]:
    notes: list[str] = []
    owns = bundle is None
    data = bundle if bundle is not None else i18n_store.load_all()
    mapping = {
        "docsBody": ["docs1", "docs2", "docs3"],
        "moneyBody": ["money1", "money2", "money3"],
        "connectBody": ["connect1", "connect2", "connect3"],
        "packBody": ["pack1", "pack2", "pack3"],
    }
    for body_key, leaves in mapping.items():
        existing = get_body_at("beforeTrip", body_key, bundle=data)
        if existing and not force:
            notes.append(f"beforeTrip.{body_key}: 이미 있음 — 건너뜀")
            continue
        blocks: list[dict[str, Any]] = []
        for leaf in leaves:
            _append_plain(blocks, data, "beforeTrip", leaf)
        write_body_at("beforeTrip", body_key, blocks, bundle=data, persist=False)
        notes.append(f"beforeTrip.{body_key}: {len(blocks)} 블록 이전")
    if persist and owns:
        i18n_store.save_all(data)
        notes.append(i18n_store.build_bundle())
    return notes


def migrate_shopping(
    *,
    force: bool = False,
    bundle: dict[str, dict[str, Any]] | None = None,
    persist: bool = True,
) -> list[str]:
    notes: list[str] = []
    owns = bundle is None
    data = bundle if bundle is not None else i18n_store.load_all()
    mapping = {
        "oliveBody": ["olive1", "olive2", "olive3"],
        "daisoBody": ["daiso1", "daiso2"],
        "dutyBody": ["duty1", "duty2"],
        "marketBody": ["market1", "market2"],
    }
    for body_key, leaves in mapping.items():
        existing = get_body_at("shopping", body_key, bundle=data)
        if existing and not force:
            notes.append(f"shopping.{body_key}: 이미 있음 — 건너뜀")
            continue
        blocks: list[dict[str, Any]] = []
        for leaf in leaves:
            _append_plain(blocks, data, "shopping", leaf)
        write_body_at("shopping", body_key, blocks, bundle=data, persist=False)
        notes.append(f"shopping.{body_key}: {len(blocks)} 블록 이전")
    if persist and owns:
        i18n_store.save_all(data)
        notes.append(i18n_store.build_bundle())
    return notes


def _migrate_convenience_item(
    data: dict[str, dict[str, Any]],
    body_key: str,
    prose_prefix: str,
    *,
    force: bool,
) -> str:
    existing = get_body_at("convenience", body_key, bundle=data)
    if existing and not force:
        return f"convenience.{body_key}: 이미 있음 — 건너뜀"

    blocks: list[dict[str, Any]] = []
    if prose_prefix == "intro":
        _append_plain(blocks, data, "convenience", "intro")
    elif prose_prefix == "biyott":
        _append_plain(blocks, data, "convenience", "biyott_lead")
        _append_titled(
            blocks, data, "convenience", "biyott_whatTitle", "biyott_what"
        )
        _append_titled(
            blocks, data, "convenience", "biyott_whyTitle", "biyott_why"
        )
        _append_titled(
            blocks, data, "convenience", "biyott_tipTitle", "biyott_tip"
        )
    else:
        p = prose_prefix
        _append_plain(blocks, data, "convenience", f"{p}_lead")
        _append_titled(
            blocks, data, "convenience", f"{p}_productsTitle", f"{p}_products"
        )
        # steps as one block with numbered lines
        titles = _lang_vals(data, "convenience", f"{p}_stepsTitle")
        s1 = _lang_vals(data, "convenience", f"{p}_s1")
        s2 = _lang_vals(data, "convenience", f"{p}_s2")
        s3 = _lang_vals(data, "convenience", f"{p}_s3")

        def steps_text(lang: str) -> str:
            title = titles.get(lang) or titles.get("ko") or ""
            lines = []
            for i, sv in enumerate((s1, s2, s3), start=1):
                line = sv.get(lang) or sv.get("ko") or ""
                if line:
                    lines.append(f"{i}. {line}")
            body = "\n".join(lines)
            if title and body:
                return f"{title}\n\n{body}"
            return title or body

        block = _text_block(steps_text("ko"), steps_text("en"), steps_text("ja"))
        if block:
            blocks.append(block)
        _append_titled(
            blocks, data, "convenience", f"{p}_tipTitle", f"{p}_tip"
        )

    write_body_at("convenience", body_key, blocks, bundle=data, persist=False)
    return f"convenience.{body_key}: {len(blocks)} 블록 이전"


def migrate_convenience(
    *,
    force: bool = False,
    bundle: dict[str, dict[str, Any]] | None = None,
    persist: bool = True,
) -> list[str]:
    notes: list[str] = []
    owns = bundle is None
    data = bundle if bundle is not None else i18n_store.load_all()
    for body_key, _image_slug, prose_prefix in CONVENIENCE_PAGE_BODIES:
        notes.append(
            _migrate_convenience_item(
                data, body_key, prose_prefix, force=force
            )
        )
    if persist and owns:
        i18n_store.save_all(data)
        notes.append(i18n_store.build_bundle())
    return notes


def migrate_souvenir(
    *,
    force: bool = False,
    bundle: dict[str, dict[str, Any]] | None = None,
    persist: bool = True,
) -> list[str]:
    notes: list[str] = []
    owns = bundle is None
    data = bundle if bundle is not None else i18n_store.load_all()
    tip_title = _lang_vals(data, "souvenir", "tipTitle")
    for slug in SOUVENIR_SLUGS:
        body_key = f"{slug}Body"
        existing = get_body_at("souvenir", body_key, bundle=data)
        if existing and not force:
            notes.append(f"souvenir.{body_key}: 이미 있음 — 건너뜀")
            continue
        blocks: list[dict[str, Any]] = []
        # Prefer Body1/Body2; also fold Desc into lead if useful — keep Desc for cards
        _append_plain(blocks, data, "souvenir", f"{slug}Body1")
        _append_plain(blocks, data, "souvenir", f"{slug}Body2")
        tip_vals = _lang_vals(data, "souvenir", f"{slug}Tip")
        if any(tip_vals.values()):

            def tip_text(lang: str) -> str:
                t = tip_title.get(lang) or tip_title.get("ko") or ""
                b = tip_vals.get(lang) or tip_vals.get("ko") or ""
                if t and b:
                    return f"{t}\n\n{b}"
                return t or b

            block = _text_block(tip_text("ko"), tip_text("en"), tip_text("ja"))
            if block:
                blocks.append(block)
        write_body_at("souvenir", body_key, blocks, bundle=data, persist=False)
        notes.append(f"souvenir.{body_key}: {len(blocks)} 블록 이전")
    if persist and owns:
        i18n_store.save_all(data)
        notes.append(i18n_store.build_bundle())
    return notes


def _append_tip_article(
    blocks: list[dict[str, Any]],
    data: dict[str, dict[str, Any]],
    title_key: str,
    mistake_key: str,
    body_keys: list[str],
) -> None:
    titles = _lang_vals(data, "tips", title_key)
    mistakes = _lang_vals(data, "tips", mistake_key)
    bodies_by_lang: dict[str, list[str]] = {lang: [] for lang in i18n_store.LANGS}
    for bk in body_keys:
        vals = _lang_vals(data, "tips", bk)
        for lang in i18n_store.LANGS:
            line = vals.get(lang) or vals.get("ko") or ""
            if line:
                bodies_by_lang[lang].append(line)

    def join(lang: str) -> str:
        t = titles.get(lang) or titles.get("ko") or ""
        m = mistakes.get(lang) or mistakes.get("ko") or ""
        body = "\n\n".join(bodies_by_lang.get(lang) or bodies_by_lang.get("ko") or [])
        parts: list[str] = []
        if t:
            parts.append(t)
        if m:
            parts.append(m)
        if body:
            parts.append(body)
        return "\n\n".join(parts)

    block = _text_block(join("ko"), join("en"), join("ja"))
    if block:
        blocks.append(block)


def migrate_tips(
    *,
    force: bool = False,
    bundle: dict[str, dict[str, Any]] | None = None,
    persist: bool = True,
) -> list[str]:
    notes: list[str] = []
    owns = bundle is None
    data = bundle if bundle is not None else i18n_store.load_all()
    mapping: dict[str, list[tuple[str, str, list[str]]]] = {
        "dailyBody": [
            ("mapTitle", "mapMistake", ["mapBody"]),
            ("cashTitle", "cashMistake", ["cashBody"]),
            ("trashTitle", "trashMistake", ["trashBody"]),
            ("wifiTitle", "wifiMistake", ["wifiBody"]),
            ("weekendTitle", "weekendMistake", ["weekendBody"]),
        ],
        "restaurantBody": [
            (
                "restaurantTitle",
                "restaurantMistake",
                ["restaurantBody1", "restaurantBody2", "restaurantBody3"],
            ),
            ("queueTitle", "queueMistake", ["queueBody"]),
            ("waterTitle", "waterMistake", ["waterBody"]),
        ],
        "transportBody": [
            ("cardTitle", "cardMistake", ["cardBody"]),
            ("rushTitle", "rushMistake", ["rushBody"]),
            ("taxiTitle", "taxiMistake", ["taxiBody"]),
            ("exitTitle", "exitMistake", ["exitBody"]),
        ],
    }
    for body_key, articles in mapping.items():
        existing = get_body_at("tips", body_key, bundle=data)
        if existing and not force:
            notes.append(f"tips.{body_key}: 이미 있음 — 건너뜀")
            continue
        blocks: list[dict[str, Any]] = []
        for title_key, mistake_key, body_keys in articles:
            _append_tip_article(blocks, data, title_key, mistake_key, body_keys)
        write_body_at("tips", body_key, blocks, bundle=data, persist=False)
        notes.append(f"tips.{body_key}: {len(blocks)} 블록 이전")
    if persist and owns:
        i18n_store.save_all(data)
        notes.append(i18n_store.build_bundle())
    return notes


def migrate_all_section_bodies(*, force: bool = False) -> list[str]:
    data = i18n_store.load_all()
    notes: list[str] = []
    notes.extend(migrate_before_trip(force=force, bundle=data, persist=False))
    notes.extend(migrate_shopping(force=force, bundle=data, persist=False))
    notes.extend(migrate_convenience(force=force, bundle=data, persist=False))
    notes.extend(migrate_souvenir(force=force, bundle=data, persist=False))
    notes.extend(migrate_tips(force=force, bundle=data, persist=False))
    i18n_store.save_all(data)
    notes.append(i18n_store.build_bundle())
    return notes
