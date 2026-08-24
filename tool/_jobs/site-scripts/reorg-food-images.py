# -*- coding: utf-8 -*-
"""Reorganize Images/foods into dishes / brands / restaurants and rewrite refs."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOODS = ROOT / "Images" / "foods"

DISHES = {
    "bibimbap-cover.jpg": "dishes/bibimbap.jpg",
    "budae-jjigae-cover.jpg": "dishes/budae-jjigae.jpg",
    "dakgalbi-cover.jpg": "dishes/dakgalbi.jpg",
    "dakhanmari-cover.jpg": "dishes/dakhanmari.jpg",
    "ganjang-gejang-cover.jpg": "dishes/ganjang-gejang.jpg",
    "jajangmyeon-cover.jpg": "dishes/jajangmyeon.jpg",
    "jeon-cover.jpg": "dishes/jeon.jpg",
    "kimbap-cover.jpg": "dishes/kimbap.jpg",
    "naengmyeon-cover.jpg": "dishes/naengmyeon.jpg",
    "samgyeopsal-cover.jpg": "dishes/samgyeopsal.jpg",
    "samgyetang-cover.jpg": "dishes/samgyetang.jpg",
    "sundubu-jjigae-cover.jpg": "dishes/sundubu-jjigae.jpg",
    "yangnyeom-chicken-cover.jpg": "dishes/yangnyeom-chicken.jpg",
}

BRANDS = {
    "paris-baguette-cover.jpg": "brands/paris-baguette.jpg",
    "tous-les-jours-cover.jpg": "brands/tous-les-jours.jpg",
    "sulbing-cover.jpg": "brands/sulbing.jpg",
}

RESTAURANTS = {
    "kimbap-wonjo-nude-cheese.jpg": "restaurants/kimbap/wonjo-nude-cheese.jpg",
    "kimbap-oto.jpg": "restaurants/kimbap/oto.jpg",
    "kimbap-horangi.jpg": "restaurants/kimbap/horangi.jpg",
    "kimbap-food2900.jpg": "restaurants/kimbap/food2900.jpg",
}

HUB = {
    "food-guide-header.jpg": "hub/food-guide-header.jpg",
}

MOVES = {}
MOVES.update(DISHES)
MOVES.update(BRANDS)
MOVES.update(RESTAURANTS)
MOVES.update(HUB)


def main():
    for sub in ("dishes", "brands", "restaurants/kimbap", "hub"):
        (FOODS / sub).mkdir(parents=True, exist_ok=True)

    path_map = {}  # old relative fragment -> new
    for src_name, dest_rel in MOVES.items():
        src = FOODS / src_name
        dest = FOODS / dest_rel
        if src.exists():
            if dest.exists():
                dest.unlink()
            shutil.move(str(src), str(dest))
            print("moved", src_name, "->", dest_rel)
        path_map[f"Images/foods/{src_name}"] = f"Images/foods/{dest_rel}"
        path_map[f"Images\\foods\\{src_name}"] = f"Images/foods/{dest_rel}"

    # Also map common patterns without Images/ prefix variations
    replacements = []
    for old, new in path_map.items():
        old_fwd = old.replace("\\", "/")
        new_fwd = new.replace("\\", "/")
        replacements.append((old_fwd, new_fwd))
        # relative forms used in pages
        replacements.append((old_fwd.replace("Images/foods/", ""), new_fwd.replace("Images/foods/", "")))

    # Broader: replace filename occurrences in html/css/md/js/json carefully
    file_globs = ["**/*.html", "**/*.md", "**/*.css", "**/*.js", "**/*.json"]
    count = 0
    for pattern in file_globs:
        for path in ROOT.glob(pattern):
            if "node_modules" in str(path) or ".git" in str(path):
                continue
            text = path.read_text(encoding="utf-8")
            orig = text
            for src_name, dest_rel in MOVES.items():
                # replace full path segments
                text = text.replace(f"Images/foods/{src_name}", f"Images/foods/{dest_rel}")
                text = text.replace(f"../Images/foods/{src_name}", f"../Images/foods/{dest_rel}")
                # depth variants already covered by Images/foods/ prefix
            if text != orig:
                path.write_text(text, encoding="utf-8")
                count += 1
                print("updated refs in", path.relative_to(ROOT))
    print("files updated:", count)

    # write README snippet helper
    readme = FOODS / "README.md"
    readme.write_text(
        """# Foods images

- `dishes/` — 음식 본문/목록용 대표 사진
- `brands/` — 디저트·베이커리 브랜드 이미지
- `restaurants/` — 가게별 사진 (`kimbap/` 등)
- `hub/` — 음식 가이드 허브 헤더 등
""",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
