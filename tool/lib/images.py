# -*- coding: utf-8 -*-
"""Canonical image paths and upload helpers (stdlib only)."""
from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path

from .paths import IMAGES_BRANDS, IMAGES_DISHES, IMAGES_RESTAURANTS, ROOT

MAX_UPLOAD_BYTES = 8 * 1024 * 1024  # 8MB
ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

JPEG_MAGIC = b"\xff\xd8\xff"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
WEBP_RIFF = b"RIFF"
WEBP_WEBP = b"WEBP"

# {slug}-menu-1.jpg / {slug}-menu-01.jpg
_MENU_NUM_RE = re.compile(
    r"^(?P<slug>.+)-menu-(?P<num>0*[1-9]\d*)\.jpg$",
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


def dish_cover_path(slug: str) -> Path:
    return IMAGES_DISHES / f"{slug}.jpg"


def shop_photo_path(kind: str, dish_slug: str, shop_slug: str) -> Path:
    if kind == "meals":
        return IMAGES_RESTAURANTS / dish_slug / f"{shop_slug}.jpg"
    return IMAGES_BRANDS / f"{shop_slug}.jpg"


def shop_menu_dir(kind: str, dish_slug: str) -> Path:
    if kind == "meals":
        return IMAGES_RESTAURANTS / dish_slug
    return IMAGES_RESTAURANTS / "desserts"


def shop_menu_path(kind: str, dish_slug: str, shop_slug: str) -> Path:
    """Legacy single-menu path: {slug}-menu.jpg (kept for compat / migration)."""
    return shop_menu_dir(kind, dish_slug) / f"{shop_slug}-menu.jpg"


def shop_menu_numbered_path(
    kind: str, dish_slug: str, shop_slug: str, index: int
) -> Path:
    if index < 1:
        raise ValueError("메뉴 이미지 번호는 1 이상이어야 합니다.")
    return shop_menu_dir(kind, dish_slug) / f"{shop_slug}-menu-{index}.jpg"


def discover_menu_images(
    kind: str, dish_slug: str, shop_slug: str
) -> list[MenuImage]:
    """Find menu photos for a shop, ordered by number.

    Prefers `{slug}-menu-N.jpg`. Legacy `{slug}-menu.jpg` counts as index 1
    when no numbered menu-1 file exists.
    """
    folder = shop_menu_dir(kind, dish_slug)
    if not folder.is_dir():
        return []

    numbered: dict[int, Path] = {}
    legacy: Path | None = None
    prefix = f"{shop_slug}-menu"
    for p in folder.iterdir():
        if not p.is_file() or p.suffix.lower() != ".jpg":
            continue
        name = p.name
        if name.lower() == f"{prefix}.jpg".lower():
            legacy = p
            continue
        m = _MENU_NUM_RE.match(name)
        if not m:
            continue
        if m.group("slug").lower() != shop_slug.lower():
            continue
        idx = int(m.group("num"))
        # Prefer unpadded name if duplicates (menu-1 over menu-01)
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
    """Rename legacy / padded names to canonical `{slug}-menu-N.jpg`."""
    notes: list[str] = []
    items = discover_menu_images(kind, dish_slug, shop_slug)
    if not items:
        return notes
    # Stage via temp names to avoid collisions
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
    # Normalize first so numbering is contiguous
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

    # Check if already canonical and in order
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
    """Rename shop photo + all menu images for a slug change."""
    notes: list[str] = []
    old_photo = shop_photo_path(kind, dish_slug, old_slug)
    new_photo = shop_photo_path(kind, dish_slug, new_slug)
    if old_photo.is_file() and not new_photo.exists():
        new_photo.parent.mkdir(parents=True, exist_ok=True)
        old_photo.rename(new_photo)
        notes.append(f"이미지: {old_photo.name} → {new_photo.name}")
    elif old_photo.is_file() and new_photo.exists():
        notes.append(f"상호 이미지 대상이 이미 있어 유지: {rel_posix(new_photo)}")

    menus = discover_menu_images(kind, dish_slug, old_slug)
    for m in menus:
        dest = shop_menu_numbered_path(kind, dish_slug, new_slug, m.index)
        if m.path.is_file() and not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            m.path.rename(dest)
            notes.append(f"메뉴 이미지: {m.path.name} → {dest.name}")
        elif m.path.is_file() and dest.exists() and m.path.resolve() != dest.resolve():
            m.path.unlink()
            notes.append(f"메뉴 이미지 정리(대상 유지): {rel_posix(m.path)}")
    # Also catch stray legacy if discover missed due to partial rename
    legacy = shop_menu_path(kind, dish_slug, old_slug)
    if legacy.is_file():
        dest = shop_menu_numbered_path(kind, dish_slug, new_slug, 1)
        if not dest.exists():
            legacy.rename(dest)
            notes.append(f"레거시 메뉴: {legacy.name} → {dest.name}")
        elif legacy.resolve() != dest.resolve():
            legacy.unlink()
    return notes


def relocate_all_shop_images(
    src_kind: str,
    src_dish: str,
    dest_kind: str,
    dest_dish: str,
    shop_slug: str,
) -> list[str]:
    notes: list[str] = []
    _relocate_one(
        shop_photo_path(src_kind, src_dish, shop_slug),
        shop_photo_path(dest_kind, dest_dish, shop_slug),
        notes,
    )
    for m in discover_menu_images(src_kind, src_dish, shop_slug):
        dest = shop_menu_numbered_path(dest_kind, dest_dish, shop_slug, m.index)
        _relocate_one(m.path, dest, notes)
    # legacy leftover
    legacy = shop_menu_path(src_kind, src_dish, shop_slug)
    if legacy.is_file():
        dest = shop_menu_numbered_path(dest_kind, dest_dish, shop_slug, 1)
        _relocate_one(legacy, dest, notes)
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
    photo = shop_photo_path(kind, dish_slug, shop_slug)
    if photo.is_file():
        photo.unlink()
        notes.append(f"이미지 삭제: {rel_posix(photo)}")
    for m in discover_menu_images(kind, dish_slug, shop_slug):
        if m.path.is_file():
            m.path.unlink()
            notes.append(f"이미지 삭제: {rel_posix(m.path)}")
    legacy = shop_menu_path(kind, dish_slug, shop_slug)
    if legacy.is_file():
        legacy.unlink()
        notes.append(f"이미지 삭제: {rel_posix(legacy)}")
    return notes


def dish_image_targets(slug: str) -> list[ImageTarget]:
    path = dish_cover_path(slug)
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
            continue
        notes.extend(save_image_bytes(t.path, data, filename=filename))
    return notes


def safe_media_path(url_path: str) -> Path | None:
    """Map /media/Images/... → absolute Path under ROOT/Images, or None."""
    prefix = "/media/"
    if not url_path.startswith(prefix):
        return None
    rel = url_path[len(prefix) :].lstrip("/")
    if ".." in rel.replace("\\", "/").split("/"):
        return None
    candidate = (ROOT / rel).resolve()
    images_root = (ROOT / "Images").resolve()
    try:
        candidate.relative_to(images_root)
    except ValueError:
        return None
    if not candidate.is_file():
        return None
    return candidate
