#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fill restaurants / convenience / souvenir / korean / misc scalars for vi/th/ru/zh-Hant."""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

from deep_translator import GoogleTranslator

ROOT = Path(__file__).resolve().parent
SECONDARY = ("vi", "th", "ru", "zh-Hant")
GMAP = {"vi": "vi", "th": "th", "ru": "ru", "zh-Hant": "zh-TW"}

SKIP_LEAVES = {
    "mapsUrl",
    "mapsEmbedUrl",
    "url",
    "href",
    "src",
    "id",
    "slug",
    "region",
    "lat",
    "lng",
    "progress",
    "sourceType",
    "mapsProvider",
    "previewTitle",
    "previewImage",
    "placeId",
    "placeUrl",
    "score",
    "phone",
    "contactLineId",
    "contactEmail",
    "contactEmailMailto",
    "policeNumber",
    "fireNumber",
    "touristNumber",
}

HTTP_RE = re.compile(r"^https?://", re.I)
EMAIL_RE = re.compile(r"^[\w.+-]+@[\w.-]+\.\w+$")
ONLY_NUM_RE = re.compile(r"^[\d\s\-–—+/₩$.,:]+$")

# Curated proper-noun maps (avoid MT disasters like Busan→屍速列車)
CITIES = {
    "vi": {
        "서울": "Seoul",
        "경기": "Gyeonggi",
        "인천": "Incheon",
        "부산": "Busan",
        "제주": "Jeju",
        "대구": "Daegu",
        "대전": "Daejeon",
        "광주": "Gwangju",
    },
    "th": {
        "서울": "โซล",
        "경기": "คยองกี",
        "인천": "อินชอน",
        "부산": "ปูซาน",
        "제주": "เชจู",
        "대구": "แทกู",
        "대전": "แทจอน",
        "광주": "ควังจู",
    },
    "ru": {
        "서울": "Сеул",
        "경기": "Кёнги",
        "인천": "Инчхон",
        "부산": "Пусан",
        "제주": "Чеджу",
        "대구": "Тэгу",
        "대전": "Тэджон",
        "광주": "Кванджу",
    },
    "zh-Hant": {
        "서울": "首爾",
        "경기": "京畿",
        "인천": "仁川",
        "부산": "釜山",
        "제주": "濟州",
        "대구": "大邱",
        "대전": "大田",
        "광주": "光州",
    },
}

REGION_LABEL = {
    "vi": {
        "Seoul": "Seoul",
        "Busan": "Busan",
        "Jeju": "Jeju",
        "Gyeonggi": "Gyeonggi",
        "Incheon": "Incheon",
        "Daegu": "Daegu",
        "Daejeon": "Daejeon",
        "Gwangju": "Gwangju",
        "Gangwon": "Gangwon",
        "Chungcheong": "Chungcheong",
        "Jeolla": "Jeolla",
        "Gyeongsang": "Gyeongsang",
    },
    "th": {
        "Seoul": "โซล",
        "Busan": "ปูซาน",
        "Jeju": "เชจู",
        "Gyeonggi": "คยองกี",
        "Incheon": "อินชอน",
        "Daegu": "แทกู",
        "Daejeon": "แทจอน",
        "Gwangju": "ควังจู",
        "Gangwon": "คังวอน",
        "Chungcheong": "ชุงชอง",
        "Jeolla": "ชอลลา",
        "Gyeongsang": "คยองซัง",
    },
    "ru": {
        "Seoul": "Сеул",
        "Busan": "Пусан",
        "Jeju": "Чеджу",
        "Gyeonggi": "Кёнги",
        "Incheon": "Инчхон",
        "Daegu": "Тэгу",
        "Daejeon": "Тэджон",
        "Gwangju": "Кванджу",
        "Gangwon": "Канвон",
        "Chungcheong": "Чхунчхон",
        "Jeolla": "Чолла",
        "Gyeongsang": "Кёнсан",
    },
    "zh-Hant": {
        "Seoul": "首爾",
        "Busan": "釜山",
        "Jeju": "濟州",
        "Gyeonggi": "京畿",
        "Incheon": "仁川",
        "Daegu": "大邱",
        "Daejeon": "大田",
        "Gwangju": "光州",
        "Gangwon": "江原",
        "Chungcheong": "忠清",
        "Jeolla": "全羅",
        "Gyeongsang": "慶尚",
    },
}

QUIZ_NAMES = {
    "vi": {
        "Naengmyeon": "Naengmyeon (Mì lạnh)",
        "Gukbap": "Gukbap (Cơm canh)",
        "Bingsu": "Bingsu (Đá bào)",
        "Dakhanmari": "Dakhanmari (Gà nguyên con)",
        "Malatang": "Malatang",
        "Samgyeopsal": "Samgyeopsal (Ba chỉ nướng)",
        "Sundubu jjigae": "Sundubu jjigae (Canh đậu phụ mềm)",
        "Tteokbokki": "Tteokbokki (Bánh gạo cay)",
    },
    "th": {
        "Naengmyeon": "แนงมยอน (เส้นเย็น)",
        "Gukbap": "กุกบับ (ข้าวซุป)",
        "Bingsu": "บิงซู",
        "Dakhanmari": "ดักฮันมาริ (ไก่ทั้งตัว)",
        "Malatang": "มาล่าถัง",
        "Samgyeopsal": "ซัมยอปซัล (สามชั้นย่าง)",
        "Sundubu jjigae": "ซุนดูบูจจิกแก (เต้าหู้นุ่ม)",
        "Tteokbokki": "ต็อกบกกิ",
    },
    "ru": {
        "Naengmyeon": "Нэнмён (холодная лапша)",
        "Gukbap": "Кукпап (суп с рисом)",
        "Bingsu": "Пингсу",
        "Dakhanmari": "Такханмари (целая курица)",
        "Malatang": "Малатанг",
        "Samgyeopsal": "Самгёпсаль",
        "Sundubu jjigae": "Сундубу чиге",
        "Tteokbokki": "Ттокпокки",
    },
    "zh-Hant": {
        "Naengmyeon": "冷麵",
        "Gukbap": "湯飯",
        "Bingsu": "冰酥",
        "Dakhanmari": "一隻雞",
        "Malatang": "麻辣燙",
        "Samgyeopsal": "三層肉",
        "Sundubu jjigae": "嫩豆腐鍋",
        "Tteokbokki": "辣炒年糕",
    },
}


def log(msg: str) -> None:
    print(msg, flush=True)


def load(lang: str) -> dict:
    return json.loads((ROOT / f"{lang}.json").read_text(encoding="utf-8"))


def save(lang: str, data: dict) -> None:
    (ROOT / f"{lang}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def flatten(d, prefix=""):
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            p = f"{prefix}.{k}" if prefix else k
            out.update(flatten(v, p))
    else:
        out[prefix] = d
    return out


def unflatten_set(data: dict, flat_key: str, value: str) -> None:
    parts = flat_key.split(".")
    cur = data
    for p in parts[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]
    cur[parts[-1]] = value


def should_skip(key: str, en_val: str) -> bool:
    leaf = key.split(".")[-1]
    if leaf in SKIP_LEAVES:
        return True
    if not en_val or not str(en_val).strip():
        return True
    s = str(en_val).strip()
    if HTTP_RE.match(s) or EMAIL_RE.match(s) or ONLY_NUM_RE.match(s):
        return True
    if "{current}" in s or "{total}" in s:
        return True
    if key.startswith("korean.p.") and leaf in ("rom", "en", "ja", "zh", "ko", "audio"):
        return True
    # media paths
    if leaf.endswith("Image") or s.startswith("media/"):
        return True
    return False


def batch_translate(texts: list[str], source: str, target: str, chunk: int = 18) -> list[str]:
    if not texts:
        return []
    out: list[str] = [""] * len(texts)
    tr = GoogleTranslator(source=source, target=target)
    for i in range(0, len(texts), chunk):
        batch = texts[i : i + chunk]
        try:
            if hasattr(tr, "translate_batch"):
                res = tr.translate_batch(batch)
            else:
                res = [tr.translate(t) for t in batch]
            if not isinstance(res, list) or len(res) != len(batch):
                raise RuntimeError("bad batch")
            for j, r in enumerate(res):
                out[i + j] = (r or "").strip() or batch[j]
        except Exception as exc:
            log(f"  batch fail @{i}: {exc}")
            for j, t in enumerate(batch):
                try:
                    out[i + j] = (tr.translate(t) or "").strip() or t
                except Exception:
                    out[i + j] = t
                time.sleep(0.1)
        log(f"  {source}->{target}: {min(i + chunk, len(texts))}/{len(texts)}")
        time.sleep(0.15)
    return out


def apply_curated(lang: str, data: dict) -> int:
    n = 0
    # cities
    for k, v in CITIES.get(lang, {}).items():
        if "cities" in data and k in data["cities"]:
            if data["cities"][k] != v:
                data["cities"][k] = v
                n += 1
    # quiz result names
    quiz = data.get("foodLife", {}).get("quiz", {}).get("results", {})
    mapping = QUIZ_NAMES.get(lang, {})
    for rid, obj in quiz.items():
        if not isinstance(obj, dict):
            continue
        en_name = None
        # use English file for source name
        name = obj.get("name")
        for en_n, loc_n in mapping.items():
            if name == en_n or name == loc_n:
                if obj.get("name") != loc_n:
                    obj["name"] = loc_n
                    n += 1
                break
            # also match if still English
        if name in mapping and obj.get("name") != mapping[name]:
            obj["name"] = mapping[name]
            n += 1
    # places regionLabel
    rmap = REGION_LABEL.get(lang, {})
    places = data.get("places", {})
    for slug, obj in places.items():
        if not isinstance(obj, dict):
            continue
        rl = obj.get("regionLabel")
        if rl in rmap and obj.get("regionLabel") != rmap[rl]:
            # only if current equals English label
            obj["regionLabel"] = rmap[rl]
            n += 1
        elif rl and rl in ("Seoul", "Busan", "Jeju", "Gyeonggi", "Incheon", "Daegu", "Daejeon", "Gwangju"):
            if rl in rmap:
                obj["regionLabel"] = rmap[rl]
                n += 1
    return n


def fill_prefixes(prefixes: tuple[str, ...], langs=None) -> None:
    langs = langs or SECONDARY
    en_flat = flatten(load("en"))
    for lang in langs:
        data = load(lang)
        menu = (data.get("common") or {}).get("langMenu")
        curated = apply_curated(lang, data)
        flat = flatten(data)
        jobs = []
        for key, en_val in en_flat.items():
            if not isinstance(en_val, str):
                continue
            if not any(key.startswith(p) for p in prefixes):
                continue
            if should_skip(key, en_val):
                continue
            # skip cities (handled curated)
            if key.startswith("cities."):
                continue
            if key.endswith(".regionLabel"):
                continue
            if key.startswith("foodLife.quiz.results.") and key.endswith(".name"):
                continue
            loc = flat.get(key)
            if loc is None or loc == "" or loc == en_val:
                jobs.append((key, en_val))
        log(f"{lang}: {len(jobs)} jobs (+{curated} curated)")
        if jobs:
            keys = [j[0] for j in jobs]
            srcs = [j[1] for j in jobs]
            outs = batch_translate(srcs, "en", GMAP[lang], chunk=18)
            for k, v in zip(keys, outs):
                if v:
                    unflatten_set(data, k, v)
        if menu is not None:
            data.setdefault("common", {})["langMenu"] = menu
        save(lang, data)
        log(f"saved {lang}.json")


def main():
    t0 = time.time()
    mode = sys.argv[1] if len(sys.argv) > 1 else "restaurants"
    queues = {
        "restaurants": ("restaurants.", "restaurantFields.", "areas."),
        "convenience": ("convenience.",),
        "souvenir": ("souvenir.",),
        "korean": ("korean.",),
        "misc": ("misc.", "apps.", "travelUtils.", "dishes.", "fun.", "transport.", "home.", "emergency.", "festivals.", "beforeTrip.", "tips."),
        "places": ("places.",),
        "all": None,
    }
    if mode == "all":
        for name in ("places", "restaurants", "convenience", "souvenir", "korean", "misc"):
            log(f"\n===== {name} =====")
            fill_prefixes(queues[name])
    elif mode in queues and queues[mode]:
        fill_prefixes(queues[mode])
    else:
        log("usage: restaurants|convenience|souvenir|korean|misc|places|all")
        sys.exit(1)
    log(f"done in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
