# -*- coding: utf-8 -*-
"""Patch 이태원 정든집 location/about/cover, rebuild messages.js, bump cache."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

JOBS_DIR = Path(__file__).resolve().parent
TOOL_DIR = JOBS_DIR.parent
ROOT = TOOL_DIR.parent
sys.path.insert(0, str(TOOL_DIR))

from lib.cache_bust import bump_asset_version  # noqa: E402
from lib.content import _write_text_retry  # noqa: E402
from lib.images import dish_cover_path, shop_photo_path  # noqa: E402
from lib.region_parse import apply_region_from_location  # noqa: E402
from lib.scaffold import sync_shop_page_visual  # noqa: E402

FOODS_DIR = ROOT / "i18n" / "pages" / "foods"
SLUG = "jeongdeunjip-itaewon"
LANGS = ("ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru")

SHARED = {
    "placeUrl": "https://map.naver.com/p/entry/place/1376882672",
    "mapsUrl": "https://map.naver.com/p/entry/place/1376882672",
    "mapsEmbedUrl": (
        "https://maps.google.com/maps?q="
        "서울+용산구+이태원로19길+13&hl=ko&z=16&output=embed"
    ),
    "mapsProvider": "naver",
    "sourceType": "naver",
    "previewImage": "media/cover.jpg",
    "placeId": "1376882672",
    "previewTitle": "이태원 정든집",
    "phone": "",
    "hours": "",
    "tip": "",
    "price": "",
    "body": [],
}

TEXT = {
    "ko": {
        "name": "이태원 정든집",
        "location": "서울 용산구 이태원로19길 13",
        "menu": "우대갈비",
        "about": (
            "이태원의 우대갈비·돼지갈비 고기집입니다. "
            "직원이 고기를 구워 주는 곳으로, 이태원 나들이에 자주 찾습니다."
        ),
    },
    "en": {
        "name": "Jeongdeunjip (Itaewon)",
        "location": "13 Itaewon-ro 19-gil, Yongsan-gu, Seoul",
        "menu": "Premium galbi",
        "about": (
            "An Itaewon Korean BBQ spot known for thick galbi. "
            "Staff grill the meat for you at the table."
        ),
    },
    "ja": {
        "name": "イテウォン チョンドゥンジップ",
        "location": "ソウル特別市龍山区梨泰院路19ギル13",
        "menu": "ウデカルビ",
        "about": "梨泰院の厚切りカルビの焼肉店です。スタッフが席で肉を焼いてくれます。",
    },
    "zh": {
        "name": "梨泰院情敦家",
        "location": "首尔市龙山区梨泰院路19街13",
        "menu": "厚切排骨",
        "about": "梨泰院的厚切排骨烤肉店，店员会在座位上帮忙烤肉。",
    },
    "zh-Hant": {
        "name": "梨泰院情敦家",
        "location": "首爾市龍山區梨泰院路19街13",
        "menu": "厚切排骨",
        "about": "梨泰院的厚切排骨烤肉店，店員會在座位上幫忙烤肉。",
    },
}


def ensure_cover() -> None:
    dest = shop_photo_path("meals", "samgyeopsal", SLUG)
    dest.parent.mkdir(parents=True, exist_ok=True)
    src = dish_cover_path("samgyeopsal", "meals")
    if dest.is_file() and dest.stat().st_size > 0:
        print(f"cover exists ({dest.stat().st_size} bytes)", flush=True)
        return
    if src.is_file():
        shutil.copy2(src, dest)
        print(f"copied dish cover → {dest}", flush=True)
    else:
        print("WARNING: no samgyeopsal dish cover to copy", flush=True)


def patch_foods_json() -> None:
    region = None
    for lang in LANGS:
        path = FOODS_DIR / f"{lang}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        restaurants = data.setdefault("restaurants", {})
        entry = dict(restaurants.get(SLUG) or {})
        entry.update(SHARED)
        text = TEXT.get(lang) or TEXT["en"]
        entry.update(text)
        if lang == "ko":
            apply_region_from_location(entry)
            region = entry.get("region")
        elif region:
            entry["region"] = region
        restaurants[SLUG] = entry
        _write_text_retry(
            path,
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        )
        print(f"patched {lang}", flush=True)


def main() -> int:
    import subprocess

    ensure_cover()
    patch_foods_json()
    for n in sync_shop_page_visual("meals", "samgyeopsal", SLUG):
        print(n, flush=True)
    subprocess.check_call(
        [sys.executable, str(ROOT / "i18n" / "build-bundle.py")],
        cwd=str(ROOT),
    )
    try:
        print(bump_asset_version(), flush=True)
    except OSError as exc:
        print("bump deferred", exc, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
