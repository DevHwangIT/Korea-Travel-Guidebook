# -*- coding: utf-8 -*-
"""CRUD for transportation landmark places (명소)."""
from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from typing import Any

from . import i18n_store
from .paths import PLACES_DIR, ROOT
from .scaffold import (
    maps_embed_url_from_location,
    maps_url_from_location,
    place_dir,
    place_index_path,
    place_media_dir,
    render_place_page,
    sync_transport_hub_places,
)
from .shop_body import normalize_body
from .translate import BatchStatus, fill_body_blocks, fill_scalar_texts

# slug must match content.validate_slug style
from .content import SLUG_RE, validate_slug  # noqa: F401 — re-export pattern

PLACE_TEXT_FIELDS = ("name", "desc", "how", "address", "regionLabel")
COORDS_PATH = ROOT / "data" / "places" / "places-coords.js"

REGION_LABELS = {
    "seoul": {
        "ko": "서울", "en": "Seoul", "ja": "ソウル", "zh": "首尔",
        "zh-Hant": "首爾", "vi": "Seoul", "th": "โซล", "ru": "Сеул",
    },
    "gyeonggi": {
        "ko": "경기", "en": "Gyeonggi", "ja": "京畿", "zh": "京畿",
        "zh-Hant": "京畿", "vi": "Gyeonggi", "th": "คยองกี", "ru": "Кёнги",
    },
    "incheon": {
        "ko": "인천", "en": "Incheon", "ja": "仁川", "zh": "仁川",
        "zh-Hant": "仁川", "vi": "Incheon", "th": "อินชอน", "ru": "Инчхон",
    },
    "gangwon": {
        "ko": "강원", "en": "Gangwon", "ja": "江原", "zh": "江原",
        "zh-Hant": "江原", "vi": "Gangwon", "th": "คังวอน", "ru": "Канвон",
    },
    "busan": {
        "ko": "부산", "en": "Busan", "ja": "釜山", "zh": "釜山",
        "zh-Hant": "釜山", "vi": "Busan", "th": "ปูซาน", "ru": "Пусан",
    },
    "gyeongju": {
        "ko": "경주", "en": "Gyeongju", "ja": "慶州", "zh": "庆州",
        "zh-Hant": "慶州", "vi": "Gyeongju", "th": "คยองจู", "ru": "Кёнджу",
    },
    "gyeongsang": {
        "ko": "경상", "en": "Gyeongsang", "ja": "慶尚", "zh": "庆尚",
        "zh-Hant": "慶尚", "vi": "Gyeongsang", "th": "คยองซัง", "ru": "Кёнсан",
    },
    "jeolla": {
        "ko": "전라", "en": "Jeolla", "ja": "全羅", "zh": "全罗",
        "zh-Hant": "全羅", "vi": "Jeolla", "th": "ชอลลา", "ru": "Чолла",
    },
    "jeju": {
        "ko": "제주", "en": "Jeju", "ja": "済州", "zh": "济州",
        "zh-Hant": "濟州", "vi": "Jeju", "th": "เชจู", "ru": "Чеджу",
    },
}

PLACE_TYPES = (
    ("city", "도시·번화가"),
    ("nature", "자연·공원"),
    ("heritage", "유적·문화"),
    ("airport", "공항"),
    ("info", "안내·대사관"),
)
PLACE_TYPE_IDS = {t for t, _ in PLACE_TYPES}


def read_coord_type(slug: str) -> str:
    if not COORDS_PATH.is_file():
        return "city"
    text = COORDS_PATH.read_text(encoding="utf-8")
    m = re.search(
        rf'slug:\s*"{re.escape(slug)}"[^}}]*?type:\s*"([a-z]+)"',
        text,
    )
    if m and m.group(1) in PLACE_TYPE_IDS:
        return m.group(1)
    return "city"


def upsert_coord_meta(
    slug: str,
    *,
    region: str,
    place_type: str = "city",
    note: str = "",
    lat: float | None = None,
    lng: float | None = None,
) -> list[str]:
    """Update or append a PLACES_COORDS entry for map pins."""
    notes: list[str] = []
    if not COORDS_PATH.is_file():
        return notes
    place_type = place_type if place_type in PLACE_TYPE_IDS else "city"
    text = COORDS_PATH.read_text(encoding="utf-8")
    pat = re.compile(
        rf'(\{{\s*slug:\s*"{re.escape(slug)}"[^}}]*\}})',
        re.M,
    )
    m = pat.search(text)
    if m:
        block = m.group(1)
        block2 = re.sub(r'type:\s*"[a-z]+"', f'type: "{place_type}"', block)
        block2 = re.sub(r'region:\s*"[^"]*"', f'region: "{region}"', block2)
        if note:
            if "note:" in block2:
                block2 = re.sub(r'note:\s*"[^"]*"', f'note: "{note}"', block2)
        text = text[: m.start(1)] + block2 + text[m.end(1) :]
        notes.append(f"지도 핀 유형/지역 갱신: {slug} ({place_type})")
    else:
        lat_v = lat if lat is not None else 36.5
        lng_v = lng if lng is not None else 127.8
        note_v = note or slug
        line = (
            f'  {{ slug: "{slug}", lat: {lat_v}, lng: {lng_v}, '
            f'region: "{region}", type: "{place_type}", note: "{note_v}" }}'
        )
        text = text.rstrip()
        if text.endswith("];"):
            text = text[:-2].rstrip()
            if not text.endswith(","):
                text += ","
            text += "\n" + line + "\n];\n"
            notes.append(f"지도 핀 추가: {slug} (좌표는 이후 조정)")
    COORDS_PATH.write_text(text, encoding="utf-8")
    return notes


# Migration seed: slug, region, default KO address for maps
SEED_PLACES: list[tuple[str, str, str]] = [
    ("myeongdong", "seoul", "서울 중구 명동"),
    ("gyeongbok", "seoul", "서울 종로구 사직로 161 경복궁"),
    ("gangnam", "seoul", "서울 강남구 강남역"),
    ("hongdae", "seoul", "서울 마포구 홍대입구역"),
    ("itaewon", "seoul", "서울 용산구 이태원역"),
    ("suwon", "gyeonggi", "경기 수원시 팔달구 정조로 825 수원화성"),
    ("goyang", "gyeonggi", "경기 고양시 일산동구 호수공원로 일산호수공원"),
    ("gapyeong", "gyeonggi", "경기 가평군 가평읍 남이섬"),
    ("haeundae", "busan", "부산 해운대구 해운대해변로 해운대해수욕장"),
    ("nampo", "busan", "부산 중구 자갈치해안로 52 자갈치시장"),
    ("seomyeon", "busan", "부산 부산진구 서면"),
    ("namsan", "seoul", "서울 용산구 남산공원길 105 남산서울타워"),
    ("bukchon", "seoul", "서울 종로구 계동길 북촌한옥마을"),
    ("insadong", "seoul", "서울 종로구 인사동길 인사동"),
    ("dongdaemun", "seoul", "서울 중구 을지로 281 동대문디자인플라자"),
    ("lotte-tower", "seoul", "서울 송파구 올림픽로 300 롯데월드타워"),
    ("songdo", "incheon", "인천 연수구 컨벤시아대로 송도센트럴파크"),
    ("seoraksan", "gangwon", "강원 속초시 설악산국립공원"),
    ("bulguksa", "gyeongju", "경북 경주시 불국로 385 불국사"),
    ("donggung", "gyeongju", "경북 경주시 원화로 동궁과월지"),
    ("jeonju", "jeolla", "전북 전주시 완산구 기린대로 전주한옥마을"),
    ("seongsan", "jeju", "제주 서귀포시 성산읍 일출로 성산일출봉"),
    ("jungmun", "jeju", "제주 서귀포시 중문관광로 중문관광단지"),
    ("gamcheon", "busan", "부산 사하구 감천문화마을길 감천문화마을"),
    ("haedong", "busan", "부산 기장군 기장읍 용궁길 해동용궁사"),
    ("imjingak", "gyeonggi", "경기 파주시 문산읍 임진각로 임진각"),
    ("everland", "gyeonggi", "경기 용인시 처인구 포곡읍 에버랜드로 에버랜드"),
]


@dataclass
class PlaceItem:
    slug: str
    name: str
    region: str
    desc: str
    address: str
    page_exists: bool


def _legacy_key(slug: str, field: str) -> str:
    return f"place_{slug}_{field}"


def region_slugs_from_bundle(bundle: dict[str, dict[str, Any]] | None = None) -> dict[str, list[str]]:
    data = bundle or i18n_store.load_all()
    places = (data["ko"].get("places") or {}) if isinstance(data.get("ko"), dict) else {}
    out: dict[str, list[str]] = {
        "seoul": [],
        "gyeonggi": [],
        "incheon": [],
        "gangwon": [],
        "busan": [],
        "gyeongju": [],
        "gyeongsang": [],
        "jeolla": [],
        "jeju": [],
    }
    for slug, entry in places.items():
        if not isinstance(entry, dict):
            continue
        region = str(entry.get("region") or "seoul").strip().lower()
        if region not in out:
            out[region] = []
        out[region].append(slug)
    # Stable order: SEED order first, then alpha
    seed_order = {s: i for i, (s, _, _) in enumerate(SEED_PLACES)}
    for region in out:
        out[region].sort(key=lambda s: (seed_order.get(s, 999), s))
    return out


def list_places() -> list[PlaceItem]:
    bundle = i18n_store.load_all()
    places = bundle["ko"].get("places") or {}
    items: list[PlaceItem] = []
    for slug, entry in places.items():
        if not isinstance(entry, dict):
            continue
        items.append(
            PlaceItem(
                slug=slug,
                name=str(entry.get("name") or slug),
                region=str(entry.get("region") or ""),
                desc=str(entry.get("desc") or ""),
                address=str(entry.get("address") or ""),
                page_exists=place_index_path(slug).is_file(),
            )
        )
    seed_order = {s: i for i, (s, _, _) in enumerate(SEED_PLACES)}
    items.sort(key=lambda p: (seed_order.get(p.slug, 999), p.slug))
    return items


def get_place(slug: str) -> dict[str, Any]:
    bundle = i18n_store.load_all()
    out: dict[str, Any] = {
        "slug": slug,
        "texts": {},
        "region": "seoul",
        "place_type": read_coord_type(slug),
        "body": [],
    }
    for lang in i18n_store.LANGS:
        entry = ((bundle[lang].get("places") or {}).get(slug) or {})
        if not isinstance(entry, dict):
            entry = {}
        if lang == "ko":
            out["region"] = str(entry.get("region") or "seoul")
            out["mapsUrl"] = str(entry.get("mapsUrl") or "")
            out["mapsEmbedUrl"] = str(entry.get("mapsEmbedUrl") or "")
            out["body"] = list(entry.get("body") or [])
        out["texts"][lang] = {
            "name": str(entry.get("name") or ""),
            "desc": str(entry.get("desc") or ""),
            "how": str(entry.get("how") or ""),
            "address": str(entry.get("address") or ""),
            "regionLabel": str(entry.get("regionLabel") or ""),
        }
    return out


def _place_old_texts(bundle: dict[str, dict[str, Any]], slug: str) -> dict[str, dict[str, str]]:
    old: dict[str, dict[str, str]] = {}
    for lang in i18n_store.LANGS:
        entry = ((bundle[lang].get("places") or {}).get(slug) or {})
        old[lang] = {
            f: str(entry.get(f) or "") for f in PLACE_TEXT_FIELDS
        }
    return old


def _normalize_place_texts(
    texts: dict[str, dict[str, str]],
) -> tuple[dict[str, dict[str, str]], list[str]]:
    notes: list[str] = []
    out: dict[str, dict[str, str]] = {}
    for lang in i18n_store.LANGS:
        row = texts.get(lang) or {}
        out[lang] = {f: str(row.get(f) or "").strip() for f in PLACE_TEXT_FIELDS}
    if not out["ko"]["name"]:
        raise ValueError("한국어 명소 이름은 필수입니다.")
    for lang in i18n_store.LANGS:
        if lang == "ko":
            continue
        for f in PLACE_TEXT_FIELDS:
            if not out[lang][f] and out["ko"][f]:
                if lang in ("zh-Hant", "vi", "th", "ru") and out.get("en", {}).get(f):
                    out[lang][f] = out["en"][f]
                else:
                    out[lang][f] = out["ko"][f]
                notes.append(f"{lang}.{f}: 임시 채움")
    return out, notes


def _apply_region_labels(
    normalized: dict[str, dict[str, str]], region: str
) -> dict[str, dict[str, str]]:
    labels = REGION_LABELS.get(region) or REGION_LABELS["seoul"]
    for lang in i18n_store.LANGS:
        if not normalized[lang].get("regionLabel"):
            normalized[lang]["regionLabel"] = labels.get(lang) or labels["ko"]
    return normalized


def _write_entry(
    bundle: dict[str, dict[str, Any]],
    slug: str,
    *,
    region: str,
    normalized: dict[str, dict[str, str]],
    maps_url: str,
    maps_embed: str,
    body: list[dict[str, Any]],
) -> None:
    for lang in i18n_store.LANGS:
        places = bundle[lang].setdefault("places", {})
        entry = dict(places.get(slug) or {})
        entry.update(normalized[lang])
        entry["region"] = region
        entry["mapsUrl"] = maps_url
        entry["mapsEmbedUrl"] = maps_embed
        entry["body"] = body
        places[slug] = entry


def save_place(
    slug: str,
    texts: dict[str, dict[str, str]],
    *,
    region: str = "seoul",
    place_type: str = "city",
    body: list[dict[str, Any]] | None = None,
    force_translate: bool = False,
    regenerate_maps: bool = True,
) -> tuple[list[str], BatchStatus]:
    from .content import validate_slug as _vs

    slug = _vs(slug)
    region = (region or "seoul").strip().lower()
    if region not in REGION_LABELS:
        raise ValueError(f"알 수 없는 지역: {region}")
    place_type = (place_type or "city").strip().lower()
    if place_type not in PLACE_TYPE_IDS:
        place_type = "city"

    notes: list[str] = []
    status = BatchStatus()
    bundle = i18n_store.load_all()
    old_texts = _place_old_texts(bundle, slug)
    texts = fill_scalar_texts(
        texts,
        PLACE_TEXT_FIELDS,
        old_texts=old_texts,
        force=force_translate,
        status=status,
    )
    normalized, fill_notes = _normalize_place_texts(texts)
    notes.extend(fill_notes)
    normalized = _apply_region_labels(normalized, region)

    address = normalized["ko"]["address"] or normalized["ko"]["name"]
    old = ((bundle["ko"].get("places") or {}).get(slug) or {})
    if regenerate_maps and address:
        maps_url = maps_url_from_location(address)
        maps_embed = maps_embed_url_from_location(address)
        notes.append("mapsUrl / mapsEmbedUrl을 주소 기준으로 재생성했습니다.")
    else:
        maps_url = str(old.get("mapsUrl") or maps_url_from_location(address))
        maps_embed = str(
            old.get("mapsEmbedUrl") or maps_embed_url_from_location(address)
        )

    if body is not None:
        old_body = list(old.get("body") or [])
        body = fill_body_blocks(
            body, old_blocks=old_body, force=force_translate, status=status
        )
        body = normalize_body(body)
    else:
        body = list(old.get("body") or [])

    _write_entry(
        bundle,
        slug,
        region=region,
        normalized=normalized,
        maps_url=maps_url,
        maps_embed=maps_embed,
        body=body,
    )
    i18n_store.save_all(bundle)
    notes.append("i18n 저장 완료")

    page = place_index_path(slug)
    if not page.is_file():
        place_media_dir(slug).mkdir(parents=True, exist_ok=True)
        page.write_text(render_place_page(slug), encoding="utf-8", newline="\n")
        notes.append(f"페이지 생성: {page.relative_to(ROOT).as_posix()}")

    notes.extend(sync_transport_hub_places(region_slugs_from_bundle(bundle)))
    notes.extend(
        upsert_coord_meta(
            slug,
            region=region,
            place_type=place_type,
            note=normalized["ko"]["name"] or slug,
        )
    )
    notes.append(i18n_store.build_bundle())
    return notes, status


def create_place(
    slug: str,
    texts: dict[str, dict[str, str]],
    *,
    region: str = "seoul",
    place_type: str = "city",
    body: list[dict[str, Any]] | None = None,
) -> tuple[list[str], BatchStatus]:
    from .content import validate_slug as _vs

    slug = _vs(slug)
    if place_index_path(slug).exists():
        raise ValueError(f"이미 페이지가 있습니다: places/{slug}")
    bundle = i18n_store.load_all()
    if slug in (bundle["ko"].get("places") or {}):
        raise ValueError(f"places.{slug} 이미 있음")

    status = BatchStatus()
    texts = fill_scalar_texts(
        texts,
        PLACE_TEXT_FIELDS,
        old_texts=None,
        force=True,
        status=status,
    )
    body_blocks = fill_body_blocks(
        list(body or []),
        old_blocks=None,
        force=True,
        status=status,
    )
    notes, save_status = save_place(
        slug,
        texts,
        region=region,
        place_type=place_type,
        body=body_blocks,
        force_translate=False,
        regenerate_maps=True,
    )
    status.translated += save_status.translated
    status.reused += save_status.reused
    status.copied += save_status.copied
    status.errors.extend(save_status.errors)
    if save_status.provider and not status.provider:
        status.provider = save_status.provider
    return notes, status


def delete_place(slug: str, *, delete_files: bool = True) -> list[str]:
    from .content import validate_slug as _vs

    slug = _vs(slug)
    notes: list[str] = []
    bundle = i18n_store.load_all()
    for lang in i18n_store.LANGS:
        places = bundle[lang].get("places") or {}
        if slug in places:
            del places[slug]
            bundle[lang]["places"] = places
            notes.append(f"{lang}: places.{slug} 삭제")
    i18n_store.save_all(bundle)

    if delete_files:
        d = place_dir(slug)
        if d.is_dir():
            shutil.rmtree(d)
            notes.append(f"폴더 삭제: {d.relative_to(ROOT).as_posix()}")

    notes.extend(sync_transport_hub_places(region_slugs_from_bundle(bundle)))
    notes.append(i18n_store.build_bundle())
    return notes


def migrate_legacy_places(*, force: bool = False) -> list[str]:
    """Import transport.place_*_* blurbs into places.{slug} + pages."""
    notes: list[str] = []
    bundle = i18n_store.load_all()
    how_defaults = {
        "ko": "가는 방법",
        "en": "How to get there",
        "ja": "行き方",
        "zh": "怎么去",
        "zh-Hant": "怎麼去",
        "vi": "Cách đi",
        "th": "วิธีไป",
        "ru": "Как добраться",
    }
    how_label = {
        lang: str(
            (bundle[lang].get("transport") or {}).get("howLabel")
            or how_defaults.get(lang)
            or how_defaults["en"]
        )
        for lang in i18n_store.LANGS
    }

    for slug, region, address_ko in SEED_PLACES:
        existing = ((bundle["ko"].get("places") or {}).get(slug) or {})
        if existing and not force:
            notes.append(f"건너뜀 (이미 있음): {slug}")
            continue

        texts: dict[str, dict[str, str]] = {}
        body: list[dict[str, Any]] = []
        text_block: dict[str, Any] = {"type": "text"}
        for lang in i18n_store.LANGS:
            transport = bundle[lang].get("transport") or {}
            name = str(transport.get(_legacy_key(slug, "name")) or "")
            desc = str(transport.get(_legacy_key(slug, "desc")) or "")
            how = str(transport.get(_legacy_key(slug, "how")) or "")
            labels = REGION_LABELS.get(region) or REGION_LABELS["seoul"]
            addr = address_ko if lang == "ko" else (name or address_ko)
            texts[lang] = {
                "name": name or slug,
                "desc": desc,
                "how": how,
                "address": addr,
                "regionLabel": labels.get(lang) or labels["ko"],
            }
            parts = []
            if desc:
                parts.append(desc)
            if how:
                parts.append(f"{how_label[lang]}: {how}")
            if parts:
                text_block[lang] = "\n\n".join(parts)
        if any(text_block.get(l) for l in i18n_store.LANGS):
            body.append(text_block)

        maps_url = maps_url_from_location(address_ko)
        maps_embed = maps_embed_url_from_location(address_ko)
        normalized, _ = _normalize_place_texts(texts)
        normalized = _apply_region_labels(normalized, region)
        _write_entry(
            bundle,
            slug,
            region=region,
            normalized=normalized,
            maps_url=maps_url,
            maps_embed=maps_embed,
            body=normalize_body(body),
        )
        page = place_index_path(slug)
        place_media_dir(slug).mkdir(parents=True, exist_ok=True)
        (place_media_dir(slug) / ".gitkeep").write_text("", encoding="utf-8")
        page.write_text(render_place_page(slug), encoding="utf-8", newline="\n")
        notes.append(f"명소 이전: {slug}")

    for lang, label in (
        ("ko", "← 대표 명소"),
        ("en", "← Popular sights"),
        ("ja", "← 代表スポット"),
    ):
        transport = bundle[lang].setdefault("transport", {})
        if not transport.get("backPlaces"):
            transport["backPlaces"] = label

    i18n_store.save_all(bundle)
    notes.extend(sync_transport_hub_places(region_slugs_from_bundle(bundle)))
    notes.append(i18n_store.build_bundle())
    PLACES_DIR.mkdir(parents=True, exist_ok=True)
    return notes


def place_body_from_form(
    form: dict[str, str], files: dict | None = None
) -> tuple[list[dict[str, Any]], list[str]]:
    """Parse WYSIWYG body; store images under pages/transportation/places/{slug}/media/."""
    from .content import validate_slug as _vs
    from .shop_body import body_from_form

    slug = _vs(form.get("slug") or form.get("new_slug") or "place")
    return body_from_form(
        form,
        files=files or {},
        section_folder="places",
        image_slug=slug,
        field_prefix="body",
    )
