# -*- coding: utf-8 -*-
"""Cover-crop every Images/places photo to one landscape size.

Scale until the shorter side fills the target, then center-crop overflow.
No letterboxing. Upscale is allowed. Aspect ratio of the subject is kept.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[2]
IMG = ROOT / "Images" / "places"
TARGET_W = 1280
TARGET_H = 853  # 3:2 — course thumbs / majority of current files
JPEG_QUALITY = 85


def to_rgb(im: Image.Image) -> Image.Image:
    im = ImageOps.exif_transpose(im)
    if im.mode in ("RGBA", "LA", "P"):
        bg = Image.new("RGB", im.size, (255, 255, 255))
        if im.mode == "P":
            im = im.convert("RGBA")
        bg.paste(im, mask=im.split()[-1] if im.mode == "RGBA" else None)
        return bg
    if im.mode != "RGB":
        return im.convert("RGB")
    return im


def cover_crop(im: Image.Image, tw: int, th: int) -> Image.Image:
    sw, sh = im.size
    scale = max(tw / sw, th / sh)
    nw = max(tw, int(round(sw * scale)))
    nh = max(th, int(round(sh * scale)))
    resized = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return resized.crop((left, top, left + tw, top + th))


def save_jpeg(im: Image.Image, dest: Path) -> None:
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
    tmp = dest.with_suffix(".tmp.jpg")
    tmp.write_bytes(buf.getvalue())
    tmp.replace(dest)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    files = []
    for p in IMG.rglob("*"):
        if not p.is_file():
            continue
        if "_tmp" in p.parts or ".tmp." in p.name:
            continue
        if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
            files.append(p)
    changed = skipped = 0
    for src in files:
        im = to_rgb(Image.open(src))
        if im.size == (TARGET_W, TARGET_H) and src.suffix.lower() in {".jpg", ".jpeg"}:
            skipped += 1
            continue
        out = cover_crop(im, TARGET_W, TARGET_H)
        dest = src if src.suffix.lower() in {".jpg", ".jpeg"} else src.with_suffix(".jpg")
        save_jpeg(out, dest)
        if dest.resolve() != src.resolve() and src.exists():
            try:
                src.unlink()
            except OSError:
                pass
        changed += 1
        if changed % 50 == 0:
            print(f"... {changed}", flush=True)
    print(
        f"DONE target={TARGET_W}x{TARGET_H} changed={changed} already={skipped} total={len(files)}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
