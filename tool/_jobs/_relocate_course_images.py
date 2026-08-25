# -*- coding: utf-8 -*-
"""Move curated-course photos into Images/travel-courses/{region}/{courseId}/.

Each cover and each stop gets its own file (copied, never shared).
After rewrite, delete Images/places/_courses files that nothing in the live
site still references.
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
DEST_ROOT = ROOT / "Images" / "travel-courses"
FALLBACK = DEST_ROOT / "_fallback.jpg"
TARGET = (1200, 800)

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

LIVE_GLOBS = [
    "data/**/*.js",
    "js/**/*.js",
    "pages/**/*.html",
    "components/**/*.html",
    "*.html",
]

COURSE_ID_RE = re.compile(r'(?:id:\s*|"id":\s*)"(c\d+)"')
COVER_JSON = re.compile(r'"cover":\s*"([^"]*)"')
COVER_JS = re.compile(r'cover:\s*"([^"]*)"')
STOP_JSON = re.compile(
    r"\{\s*\"time\":\s*\"([^\"]+)\""
    r"(?:\s*,\s*\"image\":\s*\"([^\"]*)\")?"
    r"(?:\s*,\s*\"place\":\s*\"([^\"]*)\")?"
    r"\s*\}",
    re.S,
)
STOP_JS = re.compile(
    r"\{\s*time:\s*\"([^\"]+)\""
    r"(?:,\s*image:\s*\"([^\"]*)\")?"
    r"(?:,\s*place:\s*\"([^\"]*)\")?"
    r"\s*\}"
)
IMG_REF_RE = re.compile(
    r"""(?:\.\./)*Images/(?:places/_courses|travel-courses)/[^\s"'\\]+"""
)

REGIONS = [r for r, _ in FILES]


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
                font = ImageFont.truetype(str(candidate), 28)
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


def rel_to_path(rel: str) -> Path:
    clean = rel.replace("\\", "/").split("?", 1)[0]
    return ROOT / clean.replace("../../", "").lstrip("./")


def web_rel(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    return "../../" + rel


def slugify(place: str | None, orig_rel: str, idx: int) -> str:
    raw = (place or "").strip()
    if not raw:
        stem = Path(orig_rel.replace("\\", "/")).stem if orig_rel else ""
        stem = re.sub(r"-slot$", "", stem)
        stem = re.sub(
            rf"^({'|'.join(REGIONS)})-c\d+-\d+$",
            "",
            stem,
        )
        raw = stem
    raw = re.sub(r"[^a-zA-Z0-9_-]+", "-", raw).strip("-").lower()
    return raw or f"stop-{idx:02d}"


def copy_image(src_rel: str, dest: Path, label: str) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    src = rel_to_path(src_rel) if src_rel else None
    if src and src.exists():
        if src.resolve() == dest.resolve():
            return
        shutil.copy2(src, dest)
        return
    dummy(dest, label)


def process_file(region: str, fp: Path) -> dict:
    text = fp.read_text(encoding="utf-8")
    json_style = '"stops"' in text and '"id":' in text
    stop_re = STOP_JSON if json_style else STOP_JS
    cover_re = COVER_JSON if json_style else COVER_JS
    id_iter = list(COURSE_ID_RE.finditer(text))
    if not id_iter:
        print("no courses", fp.name)
        return {"courses": 0, "copied": 0}

    replacements: list[tuple[int, int, str]] = []
    copied = 0

    for i, m in enumerate(id_iter):
        cid = m.group(1)
        c0 = m.start()
        c1 = id_iter[i + 1].start() if i + 1 < len(id_iter) else len(text)
        chunk = text[c0:c1]
        used_names: set[str] = set()

        cm = cover_re.search(chunk)
        if cm:
            cover_src = cm.group(1)
            dest = DEST_ROOT / region / cid / "cover.jpg"
            copy_image(cover_src, dest, f"{region}/{cid}/cover.jpg")
            copied += 1
            new_rel = web_rel(dest)
            replacements.append((c0 + cm.start(1), c0 + cm.end(1), new_rel))

        for idx, sm in enumerate(stop_re.finditer(chunk), start=1):
            orig = (sm.group(2) or "").strip()
            place = sm.group(3)
            slug = slugify(place, orig, idx)
            name = f"{idx:02d}-{slug}.jpg"
            n = 2
            while name in used_names:
                name = f"{idx:02d}-{slug}-{n}.jpg"
                n += 1
            used_names.add(name)
            dest = DEST_ROOT / region / cid / name
            copy_image(orig, dest, f"{region}/{cid}/{name}")
            copied += 1
            new_rel = web_rel(dest)
            if sm.group(2) is not None:
                replacements.append((c0 + sm.start(2), c0 + sm.end(2), new_rel))
            else:
                # Insert image field after time.
                insert_at = c0 + sm.end(1) + 1  # after closing quote of time
                if json_style:
                    snippet = f',\n        "image": "{new_rel}"'
                else:
                    snippet = f', image: "{new_rel}"'
                replacements.append((insert_at, insert_at, snippet))

    replacements.sort(key=lambda x: x[0], reverse=True)
    out = text
    for a, b, r in replacements:
        out = out[:a] + r + out[b:]
    fp.write_text(out, encoding="utf-8", newline="\n")
    print(fp.name, "courses", len(id_iter), "files", copied)
    return {"courses": len(id_iter), "copied": copied}


def collect_live_refs() -> set[str]:
    refs: set[str] = set()
    for pattern in LIVE_GLOBS:
        for fp in ROOT.glob(pattern):
            if not fp.is_file():
                continue
            try:
                text = fp.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for m in IMG_REF_RE.findall(text):
                refs.add(m.replace("\\", "/").lstrip("./"))
            for m in re.findall(
                r"""(?:\.\./)*Images/places/_courses/[^"'\\s]+""", text
            ):
                refs.add(m.replace("\\", "/").lstrip("./"))
            for m in re.findall(
                r"""(?:\.\./)*Images/travel-courses/[^"'\\s]+""", text
            ):
                refs.add(m.replace("\\", "/").lstrip("./"))
    normalized: set[str] = set()
    for r in refs:
        r = r.split("?", 1)[0]
        r = re.sub(r"^(\.\./)+", "", r)
        normalized.add(r)
    return normalized


def is_dummy_jpeg(path: Path) -> bool:
    try:
        with Image.open(path) as im:
            im = im.convert("RGB")
            if im.size != TARGET:
                return False
            px = im.getpixel((10, 10))
            cx = im.getpixel((TARGET[0] // 2, TARGET[1] // 2))
            return px == (214, 214, 214) and cx[0] > 80
    except OSError:
        return False


def delete_orphans(live_refs: set[str]) -> tuple[int, int]:
    courses_dir = ROOT / "Images" / "places" / "_courses"
    if not courses_dir.exists():
        return 0, 0
    deleted_dummy = 0
    deleted_other = 0
    for fp in sorted(courses_dir.glob("*.jpg")):
        rel = fp.relative_to(ROOT).as_posix()
        variants = {rel, "../../" + rel, "../" + rel}
        if variants & live_refs or rel in live_refs:
            continue
        dummy = is_dummy_jpeg(fp) or "-slot" in fp.stem
        try:
            fp.unlink()
        except OSError as exc:
            print("could not delete", rel, exc)
            continue
        if dummy:
            deleted_dummy += 1
        else:
            deleted_other += 1
    return deleted_dummy, deleted_other


def verify() -> None:
    empty = 0
    missing: list[str] = []
    place_refs: list[str] = []
    seen: dict[str, int] = {}
    for _region, fp in FILES:
        text = fp.read_text(encoding="utf-8")
        json_style = '"stops"' in text and '"id":' in text
        stop_re = STOP_JSON if json_style else STOP_JS
        cover_re = COVER_JSON if json_style else COVER_JS
        for cm in cover_re.finditer(text):
            rel = cm.group(1)
            seen[rel] = seen.get(rel, 0) + 1
            if "Images/places/" in rel and "travel-courses" not in rel:
                place_refs.append(f"cover {fp.name} {rel}")
            if not rel_to_path(rel).exists():
                missing.append(rel)
        for sm in stop_re.finditer(text):
            img = (sm.group(2) or "").strip()
            if not img:
                empty += 1
                continue
            seen[img] = seen.get(img, 0) + 1
            if "Images/places/" in img and "travel-courses" not in img:
                place_refs.append(f"stop {fp.name} {img}")
            if not rel_to_path(img).exists():
                missing.append(img)
    shared = {k: v for k, v in seen.items() if v > 1}
    print("empty stops", empty)
    print("missing files", len(missing))
    print("shared paths", len(shared))
    print("still pointing at Images/places", len(place_refs))
    for row in place_refs[:15]:
        print(" ", row)
    for k, v in sorted(shared.items(), key=lambda x: -x[1])[:10]:
        print(" shared", v, k)
    if missing:
        print("missing list:")
        for m in missing[:20]:
            print(" ", m)


def ensure_fallback() -> None:
    src = ROOT / "Images" / "places" / "_types" / "city.jpg"
    FALLBACK.parent.mkdir(parents=True, exist_ok=True)
    if src.exists():
        shutil.copy2(src, FALLBACK)
    elif not FALLBACK.exists():
        dummy(FALLBACK, "_fallback.jpg")


def main() -> None:
    ensure_fallback()
    total_copied = 0
    for region, fp in FILES:
        total_copied += process_file(region, fp)["copied"]
    print("copied", total_copied)
    live = collect_live_refs()
    print("live image refs", len(live))
    d, o = delete_orphans(live)
    print("deleted unused dummy", d)
    print("deleted unused other _courses", o)
    leftover = list((ROOT / "Images" / "places" / "_courses").glob("*.jpg"))
    print("remaining _courses files", len(leftover))
    verify()


if __name__ == "__main__":
    main()
