# -*- coding: utf-8 -*-
"""Freeform shop body blocks (text / image / youtube) in i18n restaurants.*.body."""
from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import parse_qs, urlparse

from . import i18n_store
from .images import (
    discover_menu_images,
    next_body_index,
    next_section_body_index,
    rel_posix,
    save_image_bytes,
    section_body_numbered_path,
    shop_body_numbered_path,
    shop_menu_dir,
)
YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "youtu.be",
    "www.youtu.be",
    "youtube-nocookie.com",
    "www.youtube-nocookie.com",
}

_YT_ID_RE = re.compile(r"^[A-Za-z0-9_-]{6,}$")


def extract_youtube_id(url: str) -> str | None:
    """Return YouTube video id from common URL shapes, or None."""
    raw = (url or "").strip()
    if not raw:
        return None
    if _YT_ID_RE.match(raw) and "://" not in raw and "/" not in raw:
        return raw
    if "://" not in raw:
        raw = "https://" + raw
    try:
        parsed = urlparse(raw)
    except ValueError:
        return None
    host = (parsed.hostname or "").lower()
    if host not in YOUTUBE_HOSTS:
        return None
    if host in ("youtu.be", "www.youtu.be"):
        vid = parsed.path.strip("/").split("/")[0]
        return vid if _YT_ID_RE.match(vid) else None
    path = parsed.path or ""
    if path.startswith("/embed/") or path.startswith("/shorts/") or path.startswith("/live/"):
        vid = path.strip("/").split("/")[1] if "/" in path.strip("/") else ""
        return vid if _YT_ID_RE.match(vid) else None
    qs = parse_qs(parsed.query)
    vid = (qs.get("v") or [""])[0]
    return vid if _YT_ID_RE.match(vid) else None


def youtube_embed_url(url_or_id: str) -> str | None:
    vid = extract_youtube_id(url_or_id)
    if not vid:
        return None
    return f"https://www.youtube-nocookie.com/embed/{vid}"


def youtube_watch_url(url_or_id: str) -> str | None:
    vid = extract_youtube_id(url_or_id)
    if not vid:
        return None
    return f"https://www.youtube.com/watch?v={vid}"


def empty_body() -> list[dict[str, Any]]:
    return []


def normalize_body_block(
    raw: Any, *, fill_missing_langs: bool = True
) -> dict[str, Any] | None:
    """Normalize one block dict. Returns None if invalid / empty skippable.

    When fill_missing_langs is False, empty en/ja stay empty so auto-translate
    can detect missing translations (admin KO-only save path).
    """
    if not isinstance(raw, dict):
        return None
    btype = str(raw.get("type") or "").strip().lower()
    if btype == "text":
        ko = str(raw.get("ko") or "").strip()
        en = str(raw.get("en") or "").strip()
        ja = str(raw.get("ja") or "").strip()
        if not ko and not en and not ja:
            return None
        if fill_missing_langs:
            if not en:
                en = ko
            if not ja:
                ja = ko
        return {"type": "text", "ko": ko, "en": en, "ja": ja}
    if btype == "image":
        src = str(raw.get("src") or "").strip().replace("\\", "/")
        if not src:
            return None
        if src.startswith("/"):
            src = src.lstrip("/")
        return {"type": "image", "src": src}
    if btype == "youtube":
        url = str(raw.get("url") or "").strip()
        watch = youtube_watch_url(url)
        if not watch:
            return None
        return {"type": "youtube", "url": watch}
    return None


def normalize_body(
    blocks: Any, *, fill_missing_langs: bool = True
) -> list[dict[str, Any]]:
    if not isinstance(blocks, list):
        return []
    out: list[dict[str, Any]] = []
    for raw in blocks:
        block = normalize_body_block(raw, fill_missing_langs=fill_missing_langs)
        if block:
            out.append(block)
    return out


def body_from_form(
    form: dict[str, str],
    *,
    files: dict[str, tuple[str, bytes]] | None = None,
    kind: str = "",
    dish_slug: str = "",
    shop_slug: str = "",
    field_prefix: str = "body",
    section_folder: str = "",
    image_slug: str = "",
) -> tuple[list[dict[str, Any]], list[str]]:
    """Parse indexed body_* fields (+ optional file uploads) into normalized blocks.

    field_prefix defaults to \"body\" (shops). Section editors may pass e.g. \"docsBody\".
    Section image uploads use section_folder + image_slug → page media/body-N.jpg
    (or pages/<section>/media/{slug}-body-N.jpg for shared tab pages).
    """
    notes: list[str] = []
    files = files or {}
    prefix = (field_prefix or "body").strip() or "body"
    try:
        count = int(form.get(f"{prefix}_count") or form.get("body_count") or "0")
    except ValueError:
        count = 0
    count = max(0, min(count, 200))

    use_shop = bool(kind and dish_slug and shop_slug)
    use_section = bool(section_folder and (image_slug or shop_slug))
    section_slug = (image_slug or shop_slug or "").strip()

    # Prefer JSON payload if present (reorder-friendly)
    raw_json = (form.get(f"{prefix}_json") or form.get("body_json") or "").strip()
    if raw_json:
        try:
            parsed = json.loads(raw_json)
            if isinstance(parsed, list):
                # Keep empty image placeholders until uploads are applied
                raw_blocks: list[dict[str, Any]] = []
                for item in parsed:
                    if not isinstance(item, dict):
                        continue
                    raw_blocks.append(dict(item))
                if use_shop or use_section:
                    raw_blocks, up_notes = _apply_body_uploads(
                        raw_blocks,
                        form,
                        files,
                        kind=kind,
                        dish_slug=dish_slug,
                        shop_slug=shop_slug,
                        field_prefix=prefix,
                        section_folder=section_folder,
                        image_slug=section_slug,
                    )
                    notes.extend(up_notes)
                # Leave en/ja empty when absent so save-path auto-translate can fill them.
                return normalize_body(raw_blocks, fill_missing_langs=False), notes
        except json.JSONDecodeError:
            notes.append(f"{prefix}_json 파싱 실패 — 개별 필드로 처리합니다.")

    blocks: list[dict[str, Any]] = []
    for i in range(count):
        btype = (form.get(f"{prefix}_{i}_type") or form.get(f"body_{i}_type") or "").strip().lower()
        if btype == "text":
            blocks.append(
                {
                    "type": "text",
                    "ko": form.get(f"{prefix}_{i}_ko", form.get(f"body_{i}_ko", "")),
                    "en": form.get(f"{prefix}_{i}_en", form.get(f"body_{i}_en", "")),
                    "ja": form.get(f"{prefix}_{i}_ja", form.get(f"body_{i}_ja", "")),
                }
            )
        elif btype == "image":
            src = (form.get(f"{prefix}_{i}_src") or form.get(f"body_{i}_src") or "").strip()
            file_key = f"{prefix}_{i}_file"
            upload = files.get(file_key) or files.get(f"body_{i}_file")
            if upload and upload[1]:
                if use_shop:
                    n = next_body_index(kind, dish_slug, shop_slug)
                    while any(
                        b.get("type") == "image"
                        and str(b.get("src", "")).endswith(f"-body-{n}.jpg")
                        for b in blocks
                    ):
                        n += 1
                    dest = shop_body_numbered_path(kind, dish_slug, shop_slug, n)
                    notes.extend(save_image_bytes(dest, upload[1], filename=upload[0]))
                    src = rel_posix(dest)
                elif use_section:
                    n = next_section_body_index(section_folder, section_slug)
                    while any(
                        b.get("type") == "image"
                        and str(b.get("src", "")).endswith(f"-body-{n}.jpg")
                        for b in blocks
                    ):
                        n += 1
                    dest = section_body_numbered_path(section_folder, section_slug, n)
                    notes.extend(save_image_bytes(dest, upload[1], filename=upload[0]))
                    src = rel_posix(dest)
            blocks.append({"type": "image", "src": src})
        elif btype == "youtube":
            blocks.append(
                {
                    "type": "youtube",
                    "url": form.get(f"{prefix}_{i}_url", form.get(f"body_{i}_url", "")),
                }
            )
    return normalize_body(blocks, fill_missing_langs=False), notes


def _apply_body_uploads(
    blocks: list[dict[str, Any]],
    form: dict[str, str],
    files: dict[str, tuple[str, bytes]],
    *,
    kind: str = "",
    dish_slug: str = "",
    shop_slug: str = "",
    field_prefix: str = "body",
    section_folder: str = "",
    image_slug: str = "",
) -> tuple[list[dict[str, Any]], list[str]]:
    """Apply body_N_file uploads onto image blocks (by index)."""
    notes: list[str] = []
    out = [dict(b) for b in blocks]
    prefix = (field_prefix or "body").strip() or "body"
    use_shop = bool(kind and dish_slug and shop_slug)
    section_slug = (image_slug or shop_slug or "").strip()
    if use_shop:
        n = next_body_index(kind, dish_slug, shop_slug)
    elif section_folder and section_slug:
        n = next_section_body_index(section_folder, section_slug)
    else:
        return out, notes

    for i, block in enumerate(out):
        if str(block.get("type") or "").lower() != "image":
            continue
        upload = files.get(f"{prefix}_{i}_file") or files.get(f"body_{i}_file")
        if not upload or not upload[1]:
            continue
        while any(
            str(b.get("type") or "").lower() == "image"
            and str(b.get("src", "")).endswith(f"-body-{n}.jpg")
            for b in out
        ):
            n += 1
        if use_shop:
            dest = shop_body_numbered_path(kind, dish_slug, shop_slug, n)
        else:
            dest = section_body_numbered_path(section_folder, section_slug, n)
        notes.extend(save_image_bytes(dest, upload[1], filename=upload[0]))
        out[i]["src"] = rel_posix(dest)
        n += 1
    return out, notes


def get_shop_body(slug: str, *, bundle: dict[str, dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    data = bundle or i18n_store.load_all()
    # Prefer KO; all langs should mirror
    for lang in i18n_store.LANGS:
        raw = ((data[lang].get("restaurants") or {}).get(slug) or {}).get("body")
        if isinstance(raw, list) and raw:
            return normalize_body(raw)
    for lang in i18n_store.LANGS:
        raw = ((data[lang].get("restaurants") or {}).get(slug) or {}).get("body")
        if isinstance(raw, list):
            return normalize_body(raw)
    return []


def write_shop_body(
    slug: str,
    blocks: list[dict[str, Any]],
    *,
    bundle: dict[str, dict[str, Any]] | None = None,
    clear_tip: bool = False,
) -> list[str]:
    """Write identical body array into all language restaurant entries."""
    notes: list[str] = []
    normalized = normalize_body(blocks)
    data = bundle if bundle is not None else i18n_store.load_all()
    for lang in i18n_store.LANGS:
        restaurants = data[lang].setdefault("restaurants", {})
        entry = dict(restaurants.get(slug) or {})
        entry["body"] = normalized
        if clear_tip:
            entry["tip"] = ""
        restaurants[slug] = entry
    if bundle is None:
        i18n_store.save_all(data)
        notes.append(i18n_store.build_bundle())
    notes.append(f"restaurants.{slug}.body 저장 ({len(normalized)}개)")
    return notes


def migrate_shop_body_from_legacy(
    kind: str,
    dish_slug: str,
    shop_slug: str,
    *,
    force: bool = False,
    bundle: dict[str, dict[str, Any]] | None = None,
    persist: bool = True,
) -> list[str]:
    """Build body from tip + menu images if body missing/empty.

    Does not delete menu image files. Clears tip after successful migrate.
    When persist=False, only mutates the provided bundle (caller saves).
    """
    notes: list[str] = []
    owns_bundle = bundle is None
    data = bundle if bundle is not None else i18n_store.load_all()
    existing = get_shop_body(shop_slug, bundle=data)
    if existing and not force:
        return [f"{shop_slug}: body 이미 있음 ({len(existing)} 블록) — 건너뜀"]

    blocks: list[dict[str, Any]] = []
    tips = {}
    for lang in i18n_store.LANGS:
        r = (data[lang].get("restaurants") or {}).get(shop_slug) or {}
        tips[lang] = str(r.get("tip") or "").strip()
    if any(tips.values()):
        blocks.append(
            {
                "type": "text",
                "ko": tips.get("ko") or tips.get("en") or tips.get("ja") or "",
                "en": tips.get("en") or tips.get("ko") or "",
                "ja": tips.get("ja") or tips.get("ko") or "",
            }
        )

    menus = discover_menu_images(kind, dish_slug, shop_slug)
    for m in menus:
        blocks.append({"type": "image", "src": m.rel})

    if not blocks:
        write_shop_body(shop_slug, [], bundle=data, clear_tip=False)
        notes.append(f"{shop_slug}: tip/메뉴 이미지 없음 — 빈 body 기록")
    else:
        notes.extend(
            write_shop_body(shop_slug, blocks, bundle=data, clear_tip=True)
        )
        notes.insert(
            0,
            f"{shop_slug}: tip→문단 + 메뉴 {len(menus)}장 → body ({len(blocks)} 블록)",
        )

    if persist and owns_bundle:
        i18n_store.save_all(data)
        notes.append(i18n_store.build_bundle())
    return notes


def rewrite_body_slug_refs(
    blocks: list[dict[str, Any]], old_slug: str, new_slug: str
) -> list[dict[str, Any]]:
    """Update image src basenames when shop slug changes."""
    out: list[dict[str, Any]] = []
    for block in blocks:
        b = dict(block)
        if b.get("type") == "image":
            src = str(b.get("src") or "")
            src = src.replace(f"/{old_slug}-body-", f"/{new_slug}-body-")
            src = src.replace(f"/{old_slug}-menu-", f"/{new_slug}-menu-")
            src = src.replace(f"/{old_slug}-menu.jpg", f"/{new_slug}-menu.jpg")
            b["src"] = src
        out.append(b)
    return out


def rewrite_body_folder_refs(
    blocks: list[dict[str, Any]],
    src_folder: str,
    dest_folder: str,
) -> list[dict[str, Any]]:
    if src_folder == dest_folder:
        return blocks
    src = src_folder.rstrip("/") + "/"
    dest = dest_folder.rstrip("/") + "/"
    out: list[dict[str, Any]] = []
    for block in blocks:
        b = dict(block)
        if b.get("type") == "image":
            s = str(b.get("src") or "")
            if s.startswith(src):
                b["src"] = dest + s[len(src) :]
        out.append(b)
    return out


def body_image_paths_on_disk(
    kind: str, dish_slug: str, shop_slug: str
) -> list[str]:
    """List repo-relative body-N.jpg files (for admin preview helpers)."""
    folder = shop_menu_dir(kind, dish_slug, shop_slug)
    if not folder.is_dir():
        return []
    out: list[str] = []
    for p in sorted(folder.iterdir()):
        if not p.is_file():
            continue
        name = p.name.lower()
        if name.startswith("body-") and name.endswith(".jpg"):
            out.append(rel_posix(p))
        elif name.startswith(f"{shop_slug.lower()}-body-") and name.endswith(".jpg"):
            out.append(rel_posix(p))
    return out
