# -*- coding: utf-8 -*-
"""Canonical image paths and upload helpers (stdlib only).

Page-owned media lives next to the HTML page under ``media/``:
  pages/foods/meals/kimbap/oto/media/cover.jpg
  pages/foods/meals/kimbap/oto/media/body-1.jpg

Shared assets stay under ``Images/`` (menu icons, covers, transport, hub, …).
Legacy ``Images/foods/...`` paths remain readable for older i18n/HTML refs.
"""
from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path

from .paths import (
    DESSERTS_DIR,
    IMAGES_BRANDS,
    IMAGES_DISHES,
    IMAGES_RESTAURANTS,
    MEALS_DIR,
    ROOT,
)

MAX_UPLOAD_BYTES = 8 * 1024 * 1024  # 8MB
ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

JPEG_MAGIC = b"\xff\xd8\xff"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
WEBP_RIFF = b"RIFF"
WEBP_WEBP = b"WEBP"

# {slug}-menu-1.jpg / {slug}-menu-01.jpg (legacy)
_MENU_NUM_RE = re.compile(
    r"^(?P<slug>.+)-menu-(?P<num>0*[1-9]\d*)\.jpg$",
    re.IGNORECASE,
)
# page-local menu-1.jpg
_PAGE_MENU_RE = re.compile(
    r"^menu-(?P<num>0*[1-9]\d*)\.jpg$",
    re.IGNORECASE,
)

# {slug}-body-1.jpg (legacy)
_BODY_NUM_RE = re.compile(
    r"^(?P<slug>.+)-body-(?P<num>0*[1-9]\d*)\.jpg$",
    re.IGNORECASE,
)
# page-local body-1.jpg
_PAGE_BODY_RE = re.compile(
    r"^body-(?P<num>0*[1-9]\d*)\.jpg$",
    re.IGNORECASE,
)


@dataclass
class ImageTarget:
    """One save destination for an upload field."""

    key: str  # form field name
    label: str  # Korean UI label
    path: Path
    rel: str  # repo-relative posix path


@dataclass
class MenuImage:
    """One menu / representative photo for a shop."""

    index: int
    path: Path
    rel: str
    legacy: bool = False  # True if file is {slug}-menu.jpg (no number)


def rel_posix(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def foods_kind_base(kind: str) -> Path:
    return MEALS_DIR if kind == "meals" else DESSERTS_DIR


def shop_dir(kind: str, dish_slug: str, shop_slug: str) -> Path:
    return foods_kind_base(kind) / dish_slug / shop_slug


def shop_media_dir(kind: str, dish_slug: str, shop_slug: str) -> Path:
    """Page-local media folder for a shop detail page."""
    return shop_dir(kind, dish_slug, shop_slug) / "media"


def dish_media_dir(kind: str, slug: str) -> Path:
    return foods_kind_base(kind) / slug / "media"


def resolve_dish_kind(slug: str) -> str | None:
    if (MEALS_DIR / slug / "index.html").is_file():
        return "meals"
    if (DESSERTS_DIR / slug / "index.html").is_file():
        return "desserts"
    return None


def dish_cover_path(slug: str, kind: str | None = None) -> Path:
    """Dish hub cover: pages/foods/{kind}/{slug}/media/cover.jpg."""
    k = kind if kind in ("meals", "desserts") else resolve_dish_kind(slug)
    if k is None:
        k = "meals"
    return dish_media_dir(k, slug) / "cover.jpg"


def legacy_dish_cover_path(slug: str) -> Path:
    return IMAGES_DISHES / f"{slug}.jpg"


def shop_photo_path(kind: str, dish_slug: str, shop_slug: str) -> Path:
    return shop_media_dir(kind, dish_slug, shop_slug) / "cover.jpg"


def legacy_shop_photo_path(kind: str, dish_slug: str, shop_slug: str) -> Path:
    if kind == "meals":
        return IMAGES_RESTAURANTS / dish_slug / f"{shop_slug}.jpg"
    return IMAGES_BRANDS / f"{shop_slug}.jpg"


def shop_menu_dir(kind: str, dish_slug: str, shop_slug: str = "") -> Path:
    """Media directory for shop menus/body images.

    ``shop_slug`` is required for page-local media; omitted only for legacy
    callers that still expect the old restaurants folder (empty → legacy).
    """
    if shop_slug:
        return shop_media_dir(kind, dish_slug, shop_slug)
    if kind == "meals":
        return IMAGES_RESTAURANTS / dish_slug
    return IMAGES_RESTAURANTS / "desserts"


def shop_menu_path(kind: str, dish_slug: str, shop_slug: str) -> Path:
    """Legacy single-menu path name kept for compat; lives under page media."""
    return shop_media_dir(kind, dish_slug, shop_slug) / "menu.jpg"


def shop_menu_numbered_path(
    kind: str, dish_slug: str, shop_slug: str, index: int
) -> Path:
    if index < 1:
        raise ValueError("메뉴 이미지 번호는 1 이상이어야 합니다.")
    return shop_media_dir(kind, dish_slug, shop_slug) / f"menu-{index}.jpg"


def shop_body_numbered_path(
    kind: str, dish_slug: str, shop_slug: str, index: int
) -> Path:
    if index < 1:
        raise ValueError("본문 이미지 번호는 1 이상이어야 합니다.")
    return shop_media_dir(kind, dish_slug, shop_slug) / f"body-{index}.jpg"


def section_page_root(section_folder: str) -> Path | None:
    folder = (section_folder or "").strip().replace("\\", "/").strip("/")
    mapping = {
        "souvenir": ROOT / "pages" / "souvenir",
        "convenience": ROOT / "pages" / "convenience-store",
        "before-trip": ROOT / "pages" / "before-trip",
        "shopping": ROOT / "pages" / "shopping",
        "travel-tips": ROOT / "pages" / "travel-tips",
        "apps": ROOT / "pages" / "apps",
        "emergency": ROOT / "pages" / "emergency",
        "fun": ROOT / "pages" / "fun",
        "places": ROOT / "pages" / "transportation" / "places",
    }
    return mapping.get(folder)


def section_media_dir(section_folder: str, slug: str = "") -> Path:
    """Target media dir for section body uploads."""
    folder = (section_folder or "").strip().replace("\\", "/").strip("/")
    if not folder or ".." in folder.split("/"):
        raise ValueError("잘못된 섹션 이미지 폴더입니다.")
    root = section_page_root(folder)
    safe_slug = (slug or "").strip()
    if root is None:
        return ROOT / "Images" / Path(folder)
    # Per-item detail pages
    if folder == "souvenir" and safe_slug:
        return root / safe_slug / "media"
    if folder == "places" and safe_slug:
        return root / safe_slug / "media"
    if folder == "before-trip" and safe_slug:
        return root / safe_slug / "media"
    if folder == "shopping" and safe_slug:
        return root / safe_slug / "media"
    if folder == "travel-tips" and safe_slug:
        return root / safe_slug / "media"
    if folder == "apps" and safe_slug:
        return root / safe_slug / "media"
    if folder == "emergency" and safe_slug:
        return root / safe_slug / "media"
    if folder == "fun" and safe_slug:
        return root / safe_slug / "media"
    if folder == "convenience" and safe_slug and safe_slug != "intro":
        return root / safe_slug / "media"
    # Shared media/ (hub pages, convenience intro)
    return root / "media"


def section_image_dir(section_folder: str) -> Path:
    """Repo Images/<section_folder>/ fallback / shared uploads root."""
    folder = (section_folder or "").strip().replace("\\", "/").strip("/")
    if not folder or ".." in folder.split("/"):
        raise ValueError("잘못된 섹션 이미지 폴더입니다.")
    return ROOT / "Images" / Path(folder)


def section_uses_plain_body_names(section_folder: str, slug: str) -> bool:
    """True → body-N.jpg; False → {slug}-body-N.jpg (shared media folder)."""
    folder = (section_folder or "").strip()
    safe_slug = (slug or "").strip()
    if folder == "souvenir" and safe_slug:
        return True
    if folder == "places" and safe_slug:
        return True
    if folder == "before-trip" and safe_slug:
        return True
    if folder == "shopping" and safe_slug:
        return True
    if folder == "travel-tips" and safe_slug:
        return True
    if folder == "apps" and safe_slug:
        return True
    if folder == "emergency" and safe_slug:
        return True
    if folder == "fun" and safe_slug:
        return True
    if folder == "convenience" and safe_slug and safe_slug != "intro":
        return True
    return False


def section_body_numbered_path(
    section_folder: str, slug: str, index: int
) -> Path:
    if index < 1:
        raise ValueError("본문 이미지 번호는 1 이상이어야 합니다.")
    safe_slug = (slug or "").strip()
    if not safe_slug or "/" in safe_slug or "\\" in safe_slug:
        raise ValueError("잘못된 본문 이미지 slug입니다.")
    media = section_media_dir(section_folder, safe_slug)
    if section_uses_plain_body_names(section_folder, safe_slug):
        return media / f"body-{index}.jpg"
    return media / f"{safe_slug}-body-{index}.jpg"


def discover_body_images_in_dir(folder: Path, slug: str = "") -> list[MenuImage]:
    """Find ``body-N.jpg`` (preferred) or ``{slug}-body-N.jpg`` in a folder."""
    if not folder.is_dir():
        return []
    numbered: dict[int, Path] = {}
    for p in folder.iterdir():
        if not p.is_file() or p.suffix.lower() != ".jpg":
            continue
        m_page = _PAGE_BODY_RE.match(p.name)
        if m_page:
            idx = int(m_page.group("num"))
            prev = numbered.get(idx)
            # Prefer plain body-N over slug-prefixed when both exist
            if prev is None or _PAGE_BODY_RE.match(prev.name):
                if prev is None or not _PAGE_BODY_RE.match(prev.name):
                    numbered[idx] = p
                elif len(p.stem) <= len(prev.stem):
                    numbered[idx] = p
            continue
        m = _BODY_NUM_RE.match(p.name)
        if not m:
            continue
        if slug and m.group("slug").lower() != slug.lower():
            continue
        idx = int(m.group("num"))
        if idx in numbered and _PAGE_BODY_RE.match(numbered[idx].name):
            continue
        prev = numbered.get(idx)
        if prev is None or len(p.stem) <= len(prev.stem):
            numbered[idx] = p
    return [
        MenuImage(index=idx, path=numbered[idx], rel=rel_posix(numbered[idx]))
        for idx in sorted(numbered)
    ]


def discover_body_images(
    kind: str, dish_slug: str, shop_slug: str
) -> list[MenuImage]:
    """Find body photos for a shop, ordered by number."""
    return discover_body_images_in_dir(
        shop_media_dir(kind, dish_slug, shop_slug), shop_slug
    )


def next_body_index_in_dir(folder: Path, slug: str = "") -> int:
    existing = discover_body_images_in_dir(folder, slug)
    if not existing:
        return 1
    return max(m.index for m in existing) + 1


def next_body_index(kind: str, dish_slug: str, shop_slug: str) -> int:
    return next_body_index_in_dir(
        shop_media_dir(kind, dish_slug, shop_slug), shop_slug
    )


def next_section_body_index(section_folder: str, slug: str) -> int:
    return next_body_index_in_dir(section_media_dir(section_folder, slug), slug)


def discover_menu_images(
    kind: str, dish_slug: str, shop_slug: str
) -> list[MenuImage]:
    """Find menu photos for a shop, ordered by number.

    Prefers ``menu-N.jpg`` in page media. Also accepts legacy
    ``{slug}-menu-N.jpg`` / ``{slug}-menu.jpg`` in page media or old Images dirs.
    """
    folders = [
        shop_media_dir(kind, dish_slug, shop_slug),
        legacy_shop_photo_path(kind, dish_slug, shop_slug).parent,
    ]
    if kind != "meals":
        folders.append(IMAGES_RESTAURANTS / "desserts")

    numbered: dict[int, Path] = {}
    legacy: Path | None = None
    prefix = f"{shop_slug}-menu"

    for folder in folders:
        if not folder.is_dir():
            continue
        for p in folder.iterdir():
            if not p.is_file() or p.suffix.lower() != ".jpg":
                continue
            name = p.name
            m_page = _PAGE_MENU_RE.match(name)
            if m_page:
                idx = int(m_page.group("num"))
                prev = numbered.get(idx)
                if prev is None or _PAGE_MENU_RE.match(prev.name):
                    if prev is None or len(p.stem) <= len(prev.stem):
                        numbered[idx] = p
                continue
            if name.lower() == "menu.jpg":
                legacy = legacy or p
                continue
            if name.lower() == f"{prefix}.jpg".lower():
                legacy = legacy or p
                continue
            m = _MENU_NUM_RE.match(name)
            if not m:
                continue
            if m.group("slug").lower() != shop_slug.lower():
                continue
            idx = int(m.group("num"))
            if idx in numbered and _PAGE_MENU_RE.match(numbered[idx].name):
                continue
            prev = numbered.get(idx)
            if prev is None or (len(p.stem) <= len(prev.stem)):
                numbered[idx] = p

    if legacy is not None and 1 not in numbered:
        numbered[1] = legacy

    out: list[MenuImage] = []
    for idx in sorted(numbered):
        path = numbered[idx]
        is_legacy = legacy is not None and path.resolve() == legacy.resolve()
        out.append(
            MenuImage(
                index=idx,
                path=path,
                rel=rel_posix(path),
                legacy=is_legacy,
            )
        )
    return out


def next_menu_index(kind: str, dish_slug: str, shop_slug: str) -> int:
    existing = discover_menu_images(kind, dish_slug, shop_slug)
    if not existing:
        return 1
    return max(m.index for m in existing) + 1


def normalize_menu_filenames(
    kind: str, dish_slug: str, shop_slug: str
) -> list[str]:
    """Rename legacy / padded names to canonical ``menu-N.jpg`` in page media."""
    notes: list[str] = []
    items = discover_menu_images(kind, dish_slug, shop_slug)
    if not items:
        return notes
    staged: list[tuple[Path, Path, int]] = []
    for i, item in enumerate(items, start=1):
        dest = shop_menu_numbered_path(kind, dish_slug, shop_slug, i)
        if item.path.resolve() == dest.resolve():
            continue
        tmp = item.path.with_name(f".__menu_norm_{shop_slug}_{i}__.jpg")
        item.path.rename(tmp)
        staged.append((tmp, dest, i))
        if item.legacy:
            notes.append(f"레거시 메뉴 → menu-{i}: {item.path.name}")
        else:
            notes.append(f"메뉴 정규화: {item.path.name} → {dest.name}")
    for tmp, dest, _i in staged:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            dest.unlink()
        tmp.rename(dest)
    return notes


def append_menu_uploads(
    kind: str,
    dish_slug: str,
    shop_slug: str,
    uploads: list[tuple[str, bytes]],
) -> list[str]:
    """Save one or more new menu images as next menu-N.jpg files."""
    notes: list[str] = []
    notes.extend(normalize_menu_filenames(kind, dish_slug, shop_slug))
    n = next_menu_index(kind, dish_slug, shop_slug)
    for filename, data in uploads:
        if not data:
            continue
        dest = shop_menu_numbered_path(kind, dish_slug, shop_slug, n)
        notes.extend(save_image_bytes(dest, data, filename=filename))
        n += 1
    return notes


def delete_menu_image_at(
    kind: str, dish_slug: str, shop_slug: str, index: int
) -> list[str]:
    notes: list[str] = []
    items = {m.index: m for m in discover_menu_images(kind, dish_slug, shop_slug)}
    item = items.get(index)
    if not item or not item.path.is_file():
        raise ValueError(f"메뉴 이미지 #{index} 없음")
    item.path.unlink()
    notes.append(f"메뉴 이미지 삭제: {rel_posix(item.path)}")
    notes.extend(renumber_menu_images(kind, dish_slug, shop_slug))
    return notes


def renumber_menu_images(
    kind: str, dish_slug: str, shop_slug: str, order: list[int] | None = None
) -> list[str]:
    """Renumber menu files to 1..N. If order given, that index sequence is used."""
    notes: list[str] = []
    current = discover_menu_images(kind, dish_slug, shop_slug)
    if not current:
        return notes
    by_idx = {m.index: m for m in current}
    if order is None:
        sequence = [m.index for m in current]
    else:
        sequence = [i for i in order if i in by_idx]
        for m in current:
            if m.index not in sequence:
                sequence.append(m.index)
    if not sequence:
        return notes

    already_ok = True
    for new_i, old_i in enumerate(sequence, start=1):
        src = by_idx[old_i].path
        dest = shop_menu_numbered_path(kind, dish_slug, shop_slug, new_i)
        if src.resolve() != dest.resolve() or old_i != new_i:
            already_ok = False
            break
    if already_ok:
        return notes

    staged: list[tuple[Path, Path]] = []
    for new_i, old_i in enumerate(sequence, start=1):
        src = by_idx[old_i].path
        tmp = src.with_name(f".__menu_ord_{shop_slug}_{new_i}__.jpg")
        src.rename(tmp)
        dest = shop_menu_numbered_path(kind, dish_slug, shop_slug, new_i)
        staged.append((tmp, dest))
    for tmp, dest in staged:
        if dest.exists():
            dest.unlink()
        tmp.rename(dest)
        notes.append(f"메뉴 순서 정리: → {dest.name}")
    return notes


def rename_shop_images(
    kind: str,
    dish_slug: str,
    old_slug: str,
    new_slug: str,
) -> list[str]:
    """Move page media folder when shop slug changes (cover/body names are stable)."""
    notes: list[str] = []
    old_media = shop_media_dir(kind, dish_slug, old_slug)
    new_media = shop_media_dir(kind, dish_slug, new_slug)
    old_dir = shop_dir(kind, dish_slug, old_slug)
    new_dir = shop_dir(kind, dish_slug, new_slug)

    if old_dir.is_dir() and old_dir.resolve() != new_dir.resolve():
        if new_dir.exists():
            notes.append(f"대상 가게 폴더가 이미 있어 이미지 폴더 유지: {rel_posix(new_dir)}")
        else:
            new_dir.parent.mkdir(parents=True, exist_ok=True)
            # Prefer renaming whole shop dir (includes index.html + media)
            # Callers that already moved HTML should only move media.
            if (old_dir / "index.html").is_file() or any(old_dir.iterdir()):
                # Only relocate media if HTML was handled separately
                if old_media.is_dir() and not new_media.exists():
                    new_media.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(old_media), str(new_media))
                    notes.append(
                        f"media 이동: {rel_posix(old_media)} → {rel_posix(new_media)}"
                    )
        return notes

    # Flat leftover / media-only
    if old_media.is_dir() and not new_media.exists():
        new_media.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(old_media), str(new_media))
        notes.append(f"media 이동: {rel_posix(old_media)} → {rel_posix(new_media)}")
        return notes

    # Legacy Images/ files
    old_photo = legacy_shop_photo_path(kind, dish_slug, old_slug)
    new_photo = shop_photo_path(kind, dish_slug, new_slug)
    if old_photo.is_file() and not new_photo.exists():
        new_photo.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(old_photo), str(new_photo))
        notes.append(f"이미지: {old_photo.name} → {rel_posix(new_photo)}")
    return notes


def relocate_all_shop_images(
    src_kind: str,
    src_dish: str,
    dest_kind: str,
    dest_dish: str,
    shop_slug: str,
) -> list[str]:
    notes: list[str] = []
    src_media = shop_media_dir(src_kind, src_dish, shop_slug)
    dest_media = shop_media_dir(dest_kind, dest_dish, shop_slug)
    if src_media.is_dir() and src_media.resolve() != dest_media.resolve():
        dest_media.parent.mkdir(parents=True, exist_ok=True)
        if dest_media.exists():
            for src in src_media.iterdir():
                if not src.is_file():
                    continue
                target = dest_media / src.name
                _relocate_one(src, target, notes)
            try:
                next(src_media.iterdir())
            except StopIteration:
                src_media.rmdir()
        else:
            shutil.move(str(src_media), str(dest_media))
            notes.append(
                f"media 이동: {rel_posix(src_media)} → {rel_posix(dest_media)}"
            )
        return notes

    _relocate_one(
        shop_photo_path(src_kind, src_dish, shop_slug),
        shop_photo_path(dest_kind, dest_dish, shop_slug),
        notes,
    )
    _relocate_one(
        legacy_shop_photo_path(src_kind, src_dish, shop_slug),
        shop_photo_path(dest_kind, dest_dish, shop_slug),
        notes,
    )
    for m in discover_menu_images(src_kind, src_dish, shop_slug):
        dest = shop_menu_numbered_path(dest_kind, dest_dish, shop_slug, m.index)
        _relocate_one(m.path, dest, notes)
    for m in discover_body_images(src_kind, src_dish, shop_slug):
        dest = shop_body_numbered_path(dest_kind, dest_dish, shop_slug, m.index)
        _relocate_one(m.path, dest, notes)
    return notes


def _relocate_one(src: Path, dst: Path, notes: list[str]) -> None:
    if not src.is_file():
        return
    if src.resolve() == dst.resolve():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        src.unlink()
        notes.append(f"이미지 정리(대상 유지): {rel_posix(src)}")
        return
    shutil.move(str(src), str(dst))
    notes.append(f"이미지 이동: {rel_posix(src)} → {rel_posix(dst)}")


def delete_all_shop_images(kind: str, dish_slug: str, shop_slug: str) -> list[str]:
    notes: list[str] = []
    media = shop_media_dir(kind, dish_slug, shop_slug)
    if media.is_dir():
        for p in list(media.iterdir()):
            if p.is_file():
                p.unlink()
                notes.append(f"이미지 삭제: {rel_posix(p)}")
        try:
            media.rmdir()
        except OSError:
            pass
    # Legacy leftovers
    for path in (
        legacy_shop_photo_path(kind, dish_slug, shop_slug),
        IMAGES_RESTAURANTS / dish_slug / f"{shop_slug}-menu.jpg",
        IMAGES_RESTAURANTS / "desserts" / f"{shop_slug}-menu.jpg",
    ):
        if path.is_file():
            path.unlink()
            notes.append(f"이미지 삭제: {rel_posix(path)}")
    return notes


def dish_image_targets(slug: str, kind: str | None = None) -> list[ImageTarget]:
    path = dish_cover_path(slug, kind)
    return [
        ImageTarget(
            key="cover_image",
            label="음식 대표 이미지",
            path=path,
            rel=rel_posix(path),
        )
    ]


def shop_image_targets(kind: str, dish_slug: str, shop_slug: str) -> list[ImageTarget]:
    """Shop photo only — menus use multi-upload helpers."""
    photo = shop_photo_path(kind, dish_slug, shop_slug)
    return [
        ImageTarget(
            key="shop_image",
            label="상호 이미지",
            path=photo,
            rel=rel_posix(photo),
        ),
    ]


def detect_image_format(data: bytes) -> str | None:
    if len(data) < 12:
        return None
    if data.startswith(JPEG_MAGIC):
        return "jpeg"
    if data.startswith(PNG_MAGIC):
        return "png"
    if data[:4] == WEBP_RIFF and data[8:12] == WEBP_WEBP:
        return "webp"
    return None


def validate_upload(filename: str, data: bytes) -> str:
    """Return detected format name or raise ValueError (Korean message)."""
    if not data:
        raise ValueError("빈 이미지 파일입니다.")
    if len(data) > MAX_UPLOAD_BYTES:
        mb = MAX_UPLOAD_BYTES // (1024 * 1024)
        raise ValueError(f"이미지가 너무 큽니다. 최대 {mb}MB까지 가능합니다.")
    ext = Path(filename or "").suffix.lower()
    if ext and ext not in ALLOWED_EXTS:
        raise ValueError("허용 형식: JPG, PNG, WebP")
    fmt = detect_image_format(data)
    if not fmt:
        raise ValueError(
            "이미지 형식을 확인할 수 없습니다. JPG/PNG/WebP 파일을 올려 주세요."
        )
    return fmt


def save_image_bytes(dest: Path, data: bytes, *, filename: str = "") -> list[str]:
    """Save upload to canonical dest (.jpg). Returns note lines."""
    fmt = validate_upload(filename, data)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    notes = [f"이미지 저장: {rel_posix(dest)} ({len(data)} bytes)"]
    if fmt != "jpeg":
        notes.append(
            f"원본은 {fmt.upper()}입니다. HTML이 기대하는 이름(.jpg)으로 저장했습니다."
        )
    return notes


def save_uploads_for_targets(
    targets: list[ImageTarget],
    files: dict[str, tuple[str, bytes]],
) -> list[str]:
    notes: list[str] = []
    for t in targets:
        item = files.get(t.key)
        if not item:
            continue
        filename, data = item
        if not data:
            notes.append(
                f"{t.label}: 파일이 비어 있습니다. 다른 사진으로 다시 올려 주세요."
            )
            continue
        try:
            notes.extend(save_image_bytes(t.path, data, filename=filename))
        except ValueError as exc:
            raise ValueError(f"{t.label} 업로드 실패: {exc}") from exc
    return notes


def safe_media_path(url_path: str) -> Path | None:
    """Map /media/<repo-relative> → absolute Path under Images/ or pages/."""
    prefix = "/media/"
    if not url_path.startswith(prefix):
        return None
    rel = url_path[len(prefix) :].lstrip("/")
    if ".." in rel.replace("\\", "/").split("/"):
        return None
    candidate = (ROOT / rel).resolve()
    root = ROOT.resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    allowed = False
    for base_name in ("Images", "pages"):
        try:
            candidate.relative_to((ROOT / base_name).resolve())
            allowed = True
            break
        except ValueError:
            continue
    if not allowed or not candidate.is_file():
        return None
    return candidate
