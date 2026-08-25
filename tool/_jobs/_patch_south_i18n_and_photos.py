# -*- coding: utf-8 -*-
"""Patch south-region i18n chrome/notices, copy same-place photos, fetch FilePath, list gaps."""
from __future__ import annotations

import json
import re
import shutil
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMG = ROOT / "Images" / "places"
I18N = ROOT / "i18n" / "pages" / "travel-courses"
UA = "KoreaTravelGuidebook/1.0 (course covers; educational)"
CTX = ssl._create_unverified_context()

LANGS = ["ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru"]

FEATURED = {
    "ko": ("대표 코스", "더 둘러보기"),
    "en": ("Signature courses", "More courses"),
    "ja": ("代表コース", "もっと見る"),
    "zh": ("代表路线", "更多路线"),
    "zh-Hant": ("代表路線", "更多路線"),
    "vi": ("Tour nổi bật", "Tour khác"),
    "th": ("เส้นทางเด่น", "เส้นทางเพิ่ม"),
    "ru": ("Главные маршруты", "Ещё маршруты"),
}

UDO_NOTICE = {
    "ko": "우도 여객선은 파고·안개·강풍 시 결항될 수 있습니다. 당일 성산항 운항과 마지막 복귀 배 시각을 확인하세요.",
    "en": "Udo ferries can cancel for swell, fog, or wind. Check Seongsan Port the same day and do not miss the last return boat.",
    "ja": "牛島船は波・霧・強風で欠航することがあります。当日城山港の運航と最終便を確認してください。",
    "zh": "牛岛客船可能因浪、雾、大风停航。请当天确认城山港船班，不要错过末班返回船。",
    "zh-Hant": "牛島客船可能因浪、霧、大風停航。請當天確認城山港船班，不要錯過末班返回船。",
    "vi": "Phà Udo có thể hủy vì sóng, sương mù hoặc gió. Kiểm tra cảng Seongsan trong ngày và đừng lỡ chuyến về cuối.",
    "th": "เรืออูโดอาจยกเลิกเมื่อคลื่น หมอก หรือลมแรง ตรวจท่าซองซานวันนั้นและอย่าพลาดเที่ยวกลับสุดท้าย",
    "ru": "Паромы на Удо отменяют при волне, тумане и ветре. В тот же день сверьте порт Сонсан и не опоздайте на последний рейс обратно.",
}

COURSE_FILES = [
    ROOT / "data/courses/chungcheong-curated.js",
    ROOT / "data/courses/jeolla-curated.js",
    ROOT / "data/courses/gyeongsang-curated.js",
    ROOT / "data/courses/busan-curated.js",
    ROOT / "data/courses/jeju-curated.js",
]

# Same landmark, different filename — allowed copies.
SAME_PLACE = {
    "Images/places/_courses/daecheon-sunset.jpg": "Images/places/beach/daecheon-beach.jpg",
    "Images/places/_courses/kkotji-sunset.jpg": "Images/places/beach/kkotji-beach.jpg",
    "Images/places/_courses/suncheon-sunset.jpg": "Images/places/lake/suncheon-bay.jpg",
    "Images/places/_courses/yulpo-walk.jpg": "Images/places/_courses/yulpo-beach.jpg",
    "Images/places/_courses/udo-coast.jpg": "Images/places/nature/udo.jpg",
    "Images/places/_courses/udo-beach.jpg": "Images/places/nature/udo.jpg",
    "Images/places/_courses/seomyeon-night.jpg": "Images/places/city/seomyeon.jpg",
    "Images/places/_courses/apsan-night.jpg": "Images/places/_courses/apsan.jpg",
    "Images/places/_courses/westjeju-sunset.jpg": "Images/places/beach/hyeopjae-beach.jpg",
    "Images/places/_courses/aewol-sunset.jpg": "Images/places/beach/gwakji-beach.jpg",
    "Images/places/_courses/sagye-sunset.jpg": "Images/places/_courses/sagye-coast.jpg",
    "Images/places/_courses/ulsan-coast.jpg": "Images/places/beach/ulsan-ilsan-beach.jpg",
}

FILEPATH = {
    "muryeong-tomb.jpg": "Songsan-ri_Tombs.jpg",
    "gongju-museum.jpg": "Gongju_National_Museum.jpg",
    "gungnamji.jpg": "Gungnamji.jpg",
    "jeongnimsaji.jpg": "Jeongnimsaji_Five-story_Pagoda.jpg",
    "dodamsambong.jpg": "Dodamsambong.jpg",
    "gyeonggijeon.jpg": "Gyeonggijeon.jpg",
    "jeondong-cathedral.jpg": "Jeondong_Cathedral.jpg",
    "juknokwon.jpg": "Juknokwon.jpg",
    "cheomseongdae.jpg": "Cheomseongdae.jpg",
    "daereungwon.jpg": "Cheonmachong.jpg",
    "byeongsan-seowon.jpg": "Byeongsan_Seowon.jpg",
    "haegeumgang.jpg": "Haegeumgang.jpg",
    "homigot.jpg": "Homigot_Sunrise_Square.jpg",
    "yongdusan.jpg": "Busan_Tower.jpg",
    "huinnyeoul.jpg": "Huinnyeoul_Culture_Village.jpg",
    "osulloc.jpg": "Osulloc_Tea_Museum.jpg",
    "cheonjiyeon.jpg": "Cheonjiyeon_Falls.jpg",
    "yongduam.jpg": "Yongduam.jpg",
    "sanbangsan.jpg": "Sanbangsan.jpg",
    "songaksan.jpg": "Songaksan.jpg",
    "space-walk.jpg": "Space_Walk_Pohang.jpg",
    "oedo-botania.jpg": "Oedo-Botania.jpg",
    "windy-hill.jpg": "Windy_Hill_(Geoje).jpg",
    "yudalsan.jpg": "Yudalsan.jpg",
    "suncheon-garden.jpg": "Suncheon_Bay_National_Garden.jpg",
}


def patch_i18n() -> None:
    for lang in LANGS:
        path = I18N / f"{lang}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        curated = data["travelCourses"]["curated"]
        feat, more = FEATURED[lang]
        for region in ("chungcheong", "jeolla", "busan", "gyeongsang", "jeju"):
            block = curated.get(region)
            if not block:
                print("missing region", lang, region)
                continue
            block.setdefault("featuredLabel", feat)
            block.setdefault("moreLabel", more)
        jeju = curated.get("jeju", {}).get("courses", {}).get("c02")
        if jeju is not None:
            jeju["notice"] = UDO_NOTICE[lang]
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("patched", path.name)


def collect_image_paths() -> list[Path]:
    seen: set[str] = set()
    out: list[Path] = []
    pat = re.compile(r'(?:cover:|image:)\s*"(\.\./\.\./Images/[^"]+)"')
    for fp in COURSE_FILES:
        for rel in pat.findall(fp.read_text(encoding="utf-8")):
            if rel in seen:
                continue
            seen.add(rel)
            out.append(ROOT / rel.replace("../../", ""))
    return out


def copy_same_place() -> None:
    for dest_rel, src_rel in SAME_PLACE.items():
        dest = ROOT / dest_rel
        src = ROOT / src_rel
        if dest.exists() and dest.stat().st_size > 8000:
            continue
        if not src.exists() or src.stat().st_size < 8000:
            print("SAME PLACE SRC MISSING", src_rel)
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        print("copied same-place", dest_rel)


def fetch_filepath(title: str, dest: Path) -> bool:
    quoted = urllib.parse.quote(title)
    url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{quoted}?width=1280"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=45, context=CTX) as r:
            data = r.read()
        if len(data) < 8000:
            return False
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return True
    except Exception as e:
        print("  filepath fail", title, type(e).__name__)
        return False


def fetch_missing(paths: list[Path]) -> None:
    for path in paths:
        if path.exists() and path.stat().st_size > 8000:
            continue
        title = FILEPATH.get(path.name)
        if not title:
            continue
        time.sleep(0.35)
        if fetch_filepath(title, path):
            print("OK filepath", path.name, path.stat().st_size)


def report_stops() -> None:
    import ast

    js_pat = re.compile(
        r'id:\s*"(c\d+)"[\s\S]*?stops:\s*\[([\s\S]*?)\]',
        re.M,
    )
    print("--- stop counts ---")
    for fp in COURSE_FILES:
        region = fp.stem.replace("-curated", "")
        text = fp.read_text(encoding="utf-8")
        js_counts = {}
        for m in js_pat.finditer(text):
            cid = m.group(1)
            block = m.group(2)
            n = len(re.findall(r"\{\s*time:", block))
            js_counts[cid] = n
        ko = json.loads((I18N / "ko.json").read_text(encoding="utf-8"))
        courses = ko["travelCourses"]["curated"][region]["courses"]
        for cid, n_js in sorted(js_counts.items()):
            n_i18n = len(courses.get(cid, {}).get("stops", []))
            flag = "OK" if n_js == n_i18n else "MISMATCH"
            print(f"  {flag} {region} {cid} js={n_js} i18n={n_i18n}")


def main() -> None:
    patch_i18n()
    report_stops()
    copy_same_place()
    paths = collect_image_paths()
    fetch_missing(paths)
    missing = [p for p in paths if not p.exists() or p.stat().st_size < 8000]
    print("still missing", len(missing))
    for p in missing:
        print(" ", p.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
