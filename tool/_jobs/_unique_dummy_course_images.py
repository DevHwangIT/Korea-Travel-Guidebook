# -*- coding: utf-8 -*-
"""Give every curated-course stop its own 1200x800 image file.

- Empty stops get a dummy.
- Missing files get a dummy at the original path (first use) or a unique path.
- Shared paths: first stop keeps the original; later stops get an independent
  copy (or dummy if the original is missing).
- Cover is left as-is (may match a stop on purpose).
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
TARGET = (1200, 800)
COURSE_DIR = ROOT / "Images" / "places" / "_courses"
FILES = [
    ("seoul", ROOT / "data/courses/seoul-curated.js"),
    ("incheon", ROOT / "data/courses/incheon-curated.js"),
    ("gyeonggi", ROOT / "data/courses/gyeonggi-curated.js"),
    ("gangwon", ROOT / "data/courses/gangwon-curated.js"),
    ("chungcheong", ROOT / "data/courses/chungcheong-curated.js"),
    ("jeolla", ROOT / "data/courses/jeolla-curated.js"),
    ("gyeongsang", ROOT / "data/courses/gyeongsang-curated.js"),
    ("busan", ROOT / "data/courses/busan-curated.js"),
    ("jeju", ROOT / "data/courses/jeju-curated.js"),
]

STOP_JS = re.compile(
    r"\{\s*time:\s*\"([^\"]+)\""
    r"(?:,\s*image:\s*\"([^\"]*)\")?"
    r"(?:,\s*place:\s*\"([^\"]*)\")?"
    r"\s*\}"
)
STOP_JSON = re.compile(
    r"\{\s*\"time\":\s*\"([^\"]+)\""
    r"(?:\s*,\s*\"image\":\s*\"([^\"]*)\")?"
    r"(?:\s*,\s*\"place\":\s*\"([^\"]*)\")?"
    r"\s*\}",
    re.S,
)
COURSE_ID_RE = re.compile(r'(?:id:\s*|"id":\s*)"(c\d+)"')


def dummy(path: Path, label: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    im = Image.new("RGB", TARGET, (214, 214, 214))
    draw = ImageDraw.Draw(im)
    text = "DUMMY  1200x800\n" + label
    font = ImageFont.load_default()
    for candidate in (
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/malgun.ttf"),
    ):
        if candidate.exists():
            try:
                font = ImageFont.truetype(str(candidate), 36)
                break
            except OSError:
                pass
    bbox = draw.multiline_textbbox((0, 0), text, font=font, align="center")
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.multiline_text(
        ((TARGET[0] - tw) / 2, (TARGET[1] - th) / 2),
        text,
        fill=(90, 90, 90),
        font=font,
        align="center",
    )
    im.save(path, format="JPEG", quality=82, optimize=True)


def ensure_file(dest: Path, src: Path | None, label: str) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src and src.exists() and src.resolve() != dest.resolve():
        shutil.copy2(src, dest)
        return
    if dest.exists():
        return
    dummy(dest, label)


def rel_to_path(rel: str) -> Path:
    return ROOT / rel.replace("../../", "").replace("\\", "/")


def unique_rel(region: str, cid: str, idx: int) -> str:
    return f"../../Images/places/_courses/{region}-{cid}-{idx:02d}-slot.jpg"


def process(region: str, fp: Path, used: set[str]) -> int:
    text = fp.read_text(encoding="utf-8")
    json_style = '"stops"' in text and '"id":' in text
    stop_re = STOP_JSON if json_style else STOP_JS
    id_iter = list(COURSE_ID_RE.finditer(text))
    if not id_iter:
        print("no courses", fp.name)
        return 0

    spans = []
    for i, m in enumerate(id_iter):
        start = m.start()
        end = id_iter[i + 1].start() if i + 1 < len(id_iter) else len(text)
        spans.append((m.group(1), start, end))

    replacements: list[tuple[int, int, str]] = []

    for cid, c0, c1 in spans:
        chunk = text[c0:c1]
        stops = list(stop_re.finditer(chunk))
        for idx, sm in enumerate(stops, start=1):
            time, img, place = sm.group(1), sm.group(2) or "", sm.group(3)
            rel = img.strip()
            keep = False
            if rel and rel not in used:
                disk = rel_to_path(rel)
                if not disk.exists():
                    dummy(disk, disk.name)
                used.add(rel)
                keep = True
            if keep:
                continue

            n = idx
            new_rel = unique_rel(region, cid, n)
            while new_rel in used:
                n += 1
                new_rel = unique_rel(region, cid, n)

            src = rel_to_path(rel) if rel else None
            dest = rel_to_path(new_rel)
            ensure_file(dest, src if src and src.exists() else None, dest.name)
            used.add(new_rel)

            if json_style:
                body = f'{{\n        "time": "{time}",\n        "image": "{new_rel}"'
                if place:
                    body += f',\n        "place": "{place}"'
                body += "\n      }"
            else:
                bits = [f'time: "{time}"', f'image: "{new_rel}"']
                if place:
                    bits.append(f'place: "{place}"')
                body = "{ " + ", ".join(bits) + " }"
            replacements.append((c0 + sm.start(), c0 + sm.end(), body))

    replacements.sort(key=lambda x: x[0], reverse=True)
    out = text
    for a, b, r in replacements:
        out = out[:a] + r + out[b:]

    # Re-read spans on the rewritten text so cover tracks the first stop file.
    json_style = '"stops"' in out and '"id":' in out
    stop_re = STOP_JSON if json_style else STOP_JS
    cover_re = (
        re.compile(r'"cover":\s*"[^"]*"')
        if json_style
        else re.compile(r'cover:\s*"[^"]*"')
    )
    id_iter = list(COURSE_ID_RE.finditer(out))
    cover_reps: list[tuple[int, int, str]] = []
    for i, m in enumerate(id_iter):
        cid = m.group(1)
        c0 = m.start()
        c1 = id_iter[i + 1].start() if i + 1 < len(id_iter) else len(out)
        chunk = out[c0:c1]
        cm = cover_re.search(chunk)
        stop_imgs = [(sm.group(2) or "").strip() for sm in stop_re.finditer(chunk)]
        first_img = stop_imgs[0] if stop_imgs else ""
        current_cover = ""
        if cm:
            current_cover = re.search(r'"([^"]+)"', chunk[cm.start() : cm.end()]).group(1)
        # Keep a later-stop cover (e.g. chojijin). If cover no longer matches
        # any stop (first stop was split to a unique file), point it at first.
        if cm and first_img and current_cover not in stop_imgs:
            repl = (
                f'"cover": "{first_img}"' if json_style else f'cover: "{first_img}"'
            )
            cover_reps.append((c0 + cm.start(), c0 + cm.end(), repl))
    cover_reps.sort(key=lambda x: x[0], reverse=True)
    for a, b, r in cover_reps:
        out = out[:a] + r + out[b:]

    if replacements or cover_reps:
        fp.write_text(out, encoding="utf-8", newline="\n")
    print(
        fp.name,
        "rewritten stops",
        len(replacements),
        "covers synced",
        len(cover_reps),
    )
    return len(replacements) + len(cover_reps)


def verify() -> None:
    empty = 0
    missing: list[str] = []
    seen: dict[str, int] = {}
    for _region, fp in FILES:
        text = fp.read_text(encoding="utf-8")
        json_style = '"stops"' in text and '"id":' in text
        stop_re = STOP_JSON if json_style else STOP_JS
        for sm in stop_re.finditer(text):
            img = (sm.group(2) or "").strip()
            if not img:
                empty += 1
                continue
            seen[img] = seen.get(img, 0) + 1
            if not rel_to_path(img).exists():
                missing.append(img)
    shared = {k: v for k, v in seen.items() if v > 1}
    print("empty stops", empty)
    print("missing files", len(missing))
    print("shared stop paths", len(shared))
    for k, v in sorted(shared.items(), key=lambda x: -x[1]):
        print(" ", v, k)
    if missing:
        print("missing list:")
        for m in missing[:20]:
            print(" ", m)


def main() -> None:
    COURSE_DIR.mkdir(parents=True, exist_ok=True)
    used: set[str] = set()
    for region, fp in FILES:
        process(region, fp, used)
    verify()


if __name__ == "__main__":
    main()
