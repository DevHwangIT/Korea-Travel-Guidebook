# -*- coding: utf-8 -*-
"""Canonical image paths and upload helpers (stdlib only)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .paths import IMAGES_BRANDS, IMAGES_DISHES, IMAGES_RESTAURANTS, ROOT

MAX_UPLOAD_BYTES = 8 * 1024 * 1024  # 8MB
ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

JPEG_MAGIC = b"\xff\xd8\xff"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
WEBP_RIFF = b"RIFF"
WEBP_WEBP = b"WEBP"


@dataclass
class ImageTarget:
    """One save destination for an upload field."""

    key: str  # form field name
    label: str  # Korean UI label
    path: Path
    rel: str  # repo-relative posix path


def rel_posix(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def dish_cover_path(slug: str) -> Path:
    return IMAGES_DISHES / f"{slug}.jpg"


def shop_photo_path(kind: str, dish_slug: str, shop_slug: str) -> Path:
    if kind == "meals":
        return IMAGES_RESTAURANTS / dish_slug / f"{shop_slug}.jpg"
    return IMAGES_BRANDS / f"{shop_slug}.jpg"


def shop_menu_path(kind: str, dish_slug: str, shop_slug: str) -> Path:
    if kind == "meals":
        return IMAGES_RESTAURANTS / dish_slug / f"{shop_slug}-menu.jpg"
    return IMAGES_RESTAURANTS / "desserts" / f"{shop_slug}-menu.jpg"


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
    photo = shop_photo_path(kind, dish_slug, shop_slug)
    menu = shop_menu_path(kind, dish_slug, shop_slug)
    return [
        ImageTarget(
            key="shop_image",
            label="상호 이미지",
            path=photo,
            rel=rel_posix(photo),
        ),
        ImageTarget(
            key="menu_image",
            label="대표 메뉴 이미지",
            path=menu,
            rel=rel_posix(menu),
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
    # url_path like /media/Images/foods/dishes/kimbap.jpg
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
