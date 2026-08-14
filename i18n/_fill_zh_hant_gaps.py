#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fill remaining zh-Hant gaps only: bodies, restaurant hours/category, Hans leftovers.

Does not touch vi/th/ru/zh/en/ko locale files.
"""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

spec = importlib.util.spec_from_file_location("s2tw", ROOT / "_s2tw_convert.py")
_s2tw_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_s2tw_mod)

ST_PHRASES = _s2tw_mod.ST_PHRASES
ST_CHARS = dict(_s2tw_mod.ST_CHARS)

# Prefer modern TW forms; avoid archaic 喫 for 吃
ST_CHARS["吃"] = "吃"
ST_CHARS["里"] = "裡"  # OpenCC maps to 裏; normalize to 裡

PHRASE_KEYS = sorted(ST_PHRASES.keys(), key=len, reverse=True)
PHRASE_RE = re.compile("|".join(re.escape(k) for k in PHRASE_KEYS))

# Safe UI phrase prefs AFTER char convert (no bare 應用 → 應用程式)
SAFE_UI = {
    "出租車": "計程車",
    "的士": "計程車",
    "軟件": "軟體",
    "應用程序": "應用程式",
    "信息": "資訊",
    "短信": "簡訊",
    "網絡": "網路",
    "視頻": "影片",
    "默認": "預設",
    "點擊": "點選",
    "打印": "列印",
    "質量": "品質",
    "服務器": "伺服器",
    "內存": "記憶體",
    "硬盤": "硬碟",
    "鼠標": "滑鼠",
    "屏幕": "螢幕",
    "攝像頭": "攝影機",
    "自行車": "腳踏車",
    "摩托車": "機車",
    "公交車站": "公車站",
    "公交車": "公車",
    "公共汽車": "公車",
    "裏": "裡",
    "爲": "為",
    "僞": "偽",
    "啓": "啟",
    "峯": "峰",
    "牀": "床",
    "纔": "才",
    "羣": "群",
    "衆": "眾",
    "麪": "麵",
    "麪條": "麵條",
    "方便麪": "泡麵",
    "泡麪": "泡麵",
    "最後點單": "最後點餐",
    "截止點單": "最後點餐",
    "开始营业": "開始營業",
    "開始營業": "開始營業",
    "打烊": "打烊",
    "休息时间": "休息時間",
    "休息時間": "休息時間",
    "面包店": "麵包店",
    "麵包店": "麵包店",
    "咖啡店": "咖啡店",
    "外带咖啡": "外帶咖啡",
    "紫菜包饭": "紫菜包飯",
    "紫菜包飯": "紫菜包飯",
    "刨冰": "刨冰",
    "冰淇淋": "冰淇淋",
    "小吃": "小吃",
    "韩式": "韓式",
    "한식": "韓式料理",
    "베이커리": "麵包店",
    "카페,디저트": "咖啡廳、甜點",
}
UI_KEYS = sorted(SAFE_UI.keys(), key=len, reverse=True)
UI_RE = re.compile("|".join(re.escape(k) for k in UI_KEYS))

HANGUL = re.compile(r"[\uac00-\ud7a3]")


def s2tw_safe(text: str) -> str:
    if not text or not isinstance(text, str):
        return text

    def repl_phrase(m: re.Match[str]) -> str:
        return ST_PHRASES[m.group(0)]

    out = PHRASE_RE.sub(repl_phrase, text)
    out = "".join(ST_CHARS.get(ch, ch) for ch in out)

    def repl_ui(m: re.Match[str]) -> str:
        return SAFE_UI[m.group(0)]

    out = UI_RE.sub(repl_ui, out)
    # Fix accidental double 應用程式程式 from older converters
    out = out.replace("應用程式程式", "應用程式")
    out = out.replace("喫", "吃")  # safety if any slipped through
    return out


# Curated restaurant hours/categories (Traditional)
RESTAURANT_FIXES = {
    "paris-baguette": {"hours": "20:00打烊", "category": "麵包店"},
    "butter-and-shelter": {"hours": "21:30最後點餐", "category": "咖啡廳、甜點"},
    "index-caramel": {"hours": "20:30打烊", "category": "咖啡廳、甜點"},
    "hyodam-myeongdong": {"hours": "17:00開始營業", "category": "韓式料理"},
}

# Manual high-quality body fills (when zh missing / bad MT)
MANUAL_BODIES = {
    ("convenience.c4Body", 0): (
        "酥脆蜂蜜藥果配上略苦的咖啡——便利商店就能享受的韓式下午茶組合。"
    ),
}


def load(name: str) -> dict:
    return json.loads((ROOT / f"{name}.json").read_text(encoding="utf-8"))


def save(name: str, data: dict) -> None:
    (ROOT / f"{name}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def fill_bodies(hant: dict, zh: dict, en: dict) -> int:
    n = 0

    def walk(h, z, e, path: str = "") -> None:
        nonlocal n
        if isinstance(h, dict):
            for k in list(h.keys()):
                p = f"{path}.{k}" if path else k
                walk(
                    h[k],
                    z.get(k) if isinstance(z, dict) else None,
                    e.get(k) if isinstance(e, dict) else None,
                    p,
                )
        elif (
            isinstance(h, list)
            and h
            and isinstance(h[0], dict)
            and any(
                isinstance(x, dict) and x.get("type") in ("text", "callout") for x in h
            )
        ):
            for i, block in enumerate(h):
                if not isinstance(block, dict) or block.get("type") not in (
                    "text",
                    "callout",
                ):
                    continue
                key = (path, i)
                if key in MANUAL_BODIES:
                    new_t = MANUAL_BODIES[key]
                    if block.get("zh-Hant") != new_t:
                        block["zh-Hant"] = new_t
                        n += 1
                    continue

                cur = str(block.get("zh-Hant") or "").strip()
                z_block = (
                    z[i]
                    if isinstance(z, list) and i < len(z) and isinstance(z[i], dict)
                    else {}
                )
                e_block = (
                    e[i]
                    if isinstance(e, list) and i < len(e) and isinstance(e[i], dict)
                    else {}
                )
                src_zh = str(
                    (z_block.get("zh") if isinstance(z_block, dict) else None)
                    or block.get("zh")
                    or ""
                ).strip()
                src_en = str(
                    (e_block.get("en") if isinstance(e_block, dict) else None)
                    or block.get("en")
                    or ""
                ).strip()

                need = (
                    (not cur)
                    or (src_en and cur == src_en)
                    or (HANGUL.search(cur) and src_zh)
                )
                if not need:
                    # still polish remaining Hans in existing Hant
                    polished = s2tw_safe(cur)
                    if polished != cur:
                        block["zh-Hant"] = polished
                        n += 1
                    continue

                if src_zh:
                    new_t = s2tw_safe(src_zh)
                elif key in MANUAL_BODIES:
                    new_t = MANUAL_BODIES[key]
                else:
                    continue
                if new_t and new_t != cur:
                    block["zh-Hant"] = new_t
                    n += 1
        elif isinstance(h, list):
            for i, item in enumerate(h):
                walk(
                    item,
                    z[i] if isinstance(z, list) and i < len(z) else None,
                    e[i] if isinstance(e, list) and i < len(e) else None,
                    f"{path}[{i}]",
                )

    walk(hant, zh, en)
    return n


def fill_scalars(hant: dict, zh: dict, en: dict) -> int:
    n = 0
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
        "rom",
        "romaji",
        "audio",
        "ko",
        "en",
        "ja",
        "zh",  # keep Simplified mirror inside multilingual name objects
        "price",
        "brand",
        "footer",
        "eyebrow",
    }

    def walk(h, z, e, path: str = "") -> None:
        nonlocal n
        if isinstance(h, dict):
            for k, v in list(h.items()):
                p = f"{path}.{k}" if path else k
                leaf = k
                if leaf in SKIP_LEAVES:
                    continue
                # nested locale mirrors under korean.p.*.{rom,en,ja,...}
                if path.startswith("korean.p.") and leaf in (
                    "rom",
                    "en",
                    "ja",
                    "zh",
                    "ko",
                    "audio",
                ):
                    continue
                walk(
                    v,
                    z.get(k) if isinstance(z, dict) else None,
                    e.get(k) if isinstance(e, dict) else None,
                    p,
                )
        elif isinstance(h, list):
            # body arrays handled elsewhere
            if h and isinstance(h[0], dict) and any(
                isinstance(x, dict) and x.get("type") in ("text", "callout", "image")
                for x in h
            ):
                return
            for i, item in enumerate(h):
                walk(
                    item,
                    z[i] if isinstance(z, list) and i < len(z) else None,
                    e[i] if isinstance(e, list) and i < len(e) else None,
                    f"{path}[{i}]",
                )
        elif isinstance(h, str):
            cur = h
            zv = z if isinstance(z, str) else ""
            ev = e if isinstance(e, str) else ""
            leaf = path.split(".")[-1]

            # Restaurant hours/category hangul → curated or from zh
            if path.startswith("restaurants.") and leaf in ("hours", "category"):
                rid = path.split(".")[1]
                if rid in RESTAURANT_FIXES and leaf in RESTAURANT_FIXES[rid]:
                    new_t = RESTAURANT_FIXES[rid][leaf]
                    if cur != new_t:
                        # mutate via path set later — return signal by replacing parent
                        pass
                elif HANGUL.search(cur) and zv:
                    new_t = s2tw_safe(zv)
                elif HANGUL.search(cur):
                    new_t = s2tw_safe(cur)
                else:
                    new_t = s2tw_safe(cur)
                # apply via container — handled in set_path below
                return

            new_t = None
            if HANGUL.search(cur) and zv and zv != cur:
                new_t = s2tw_safe(zv)
            elif (not cur or cur == ev) and zv and zv != ev:
                new_t = s2tw_safe(zv)
            else:
                polished = s2tw_safe(cur)
                if polished != cur:
                    new_t = polished

            if new_t is not None and new_t != cur:
                set_path(hant, path, new_t)
                n += 1

    walk(hant, zh, en)

    # Direct restaurant fixes
    for rid, fixes in RESTAURANT_FIXES.items():
        r = hant.get("restaurants", {}).get(rid)
        if not isinstance(r, dict):
            continue
        for k, v in fixes.items():
            if r.get(k) != v:
                r[k] = v
                n += 1

    # Explicit scalar fixes
    explicit = {
        "common.tip": "小貼士",
        "foodsHub.mealsLabel": "分類 01",
        "foodsHub.dessertsLabel": "分類 02",
        "restaurantFields.sourceNaver": "Naver",
        "restaurantFields.sourceKakao": "Kakao",
        "restaurantFields.sourceGoogle": "Google",
    }
    for k, v in explicit.items():
        cur = get_path(hant, k)
        if cur != v and get_path(en, k) is not None:
            # only overwrite tip/labels; keep source brand names as Latin intentionally
            if k.startswith("restaurantFields.source"):
                continue
            set_path(hant, k, v)
            n += 1
        elif k in ("common.tip", "foodsHub.mealsLabel", "foodsHub.dessertsLabel"):
            if cur != v:
                set_path(hant, k, v)
                n += 1

    return n


def get_path(obj, dotted: str):
    cur = obj
    for p in dotted.split("."):
        if not isinstance(cur, dict) or p not in cur:
            return None
        cur = cur[p]
    return cur


def set_path(obj, dotted: str, value) -> None:
    parts = dotted.split(".")
    cur = obj
    for p in parts[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]
    cur[parts[-1]] = value


def polish_all_hant_strings(hant: dict) -> int:
    """Final pass: s2tw_safe on every zh-Hant locale scalar + body zh-Hant keys."""
    n = 0

    def walk(obj, path: str = "") -> None:
        nonlocal n
        if isinstance(obj, dict):
            # body block language keys
            if obj.get("type") in ("text", "callout") and "zh-Hant" in obj:
                cur = obj.get("zh-Hant")
                if isinstance(cur, str) and cur:
                    new_t = s2tw_safe(cur)
                    if new_t != cur:
                        obj["zh-Hant"] = new_t
                        n += 1
                return
            for k, v in obj.items():
                if k in ("ko", "en", "ja", "zh", "vi", "th", "ru", "rom", "romaji", "audio"):
                    continue
                walk(v, f"{path}.{k}" if path else k)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                walk(v, f"{path}[{i}]")
        elif isinstance(obj, str) and obj:
            # only polish if contains CJK and conversion changes
            if re.search(r"[\u4e00-\u9fff]", obj):
                # skip if this is under a skipped leaf — handled by parent skip
                new_t = s2tw_safe(obj)
                if new_t != obj:
                    # can't set from here without parent — use set via path for top scalars only
                    pass

    # Use mutable walk that sets strings in place for non-body
    def walk_set(obj) -> None:
        nonlocal n
        if isinstance(obj, dict):
            if obj.get("type") in ("text", "callout"):
                cur = obj.get("zh-Hant")
                if isinstance(cur, str) and cur:
                    new_t = s2tw_safe(cur)
                    if new_t != cur:
                        obj["zh-Hant"] = new_t
                        n += 1
                return
            for k, v in list(obj.items()):
                if k in (
                    "ko",
                    "en",
                    "ja",
                    "zh",
                    "vi",
                    "th",
                    "ru",
                    "rom",
                    "romaji",
                    "audio",
                    "mapsUrl",
                    "mapsEmbedUrl",
                    "url",
                    "href",
                    "src",
                    "id",
                    "slug",
                    "placeId",
                    "placeUrl",
                    "phone",
                    "price",
                    "previewImage",
                    "previewTitle",
                ):
                    continue
                if isinstance(v, str) and re.search(r"[\u4e00-\u9fff]", v):
                    new_t = s2tw_safe(v)
                    if new_t != v:
                        obj[k] = new_t
                        n += 1
                else:
                    walk_set(v)
        elif isinstance(obj, list):
            for v in obj:
                walk_set(v)

    walk_set(hant)
    return n


def main() -> None:
    hant = load("zh-Hant")
    zh = load("zh")
    en = load("en")

    n_body = fill_bodies(hant, zh, en)
    n_scalar = fill_scalars(hant, zh, en)
    n_polish = polish_all_hant_strings(hant)

    # Fix 應用程式程式 if any remain
    raw = json.dumps(hant, ensure_ascii=False)
    fixed = raw.replace("應用程式程式", "應用程式")
    if fixed != raw:
        hant = json.loads(fixed)
        print("fixed double 應用程式程式")

    save("zh-Hant", hant)
    print(f"bodies updated: {n_body}")
    print(f"scalars updated: {n_scalar}")
    print(f"polish pass: {n_polish}")

    # Quick verify
    h2 = load("zh-Hant")
    assert h2["common"]["tip"] == "小貼士"
    assert h2["foodsHub"]["mealsLabel"] == "分類 01"
    assert "영업" not in h2["restaurants"]["paris-baguette"]["hours"]
    assert "베이커리" not in h2["restaurants"]["paris-baguette"]["category"]
    c4 = h2["convenience"]["c4Body"][0]["zh-Hant"]
    assert c4 and not c4.startswith("Crispy")
    taxi = h2["beforeTrip"]["taxiBody"][2]["zh-Hant"]
    assert not HANGUL.search(taxi)
    print("verify OK")
    print("c4:", c4[:60])
    print("taxi2:", taxi[:80])
    print("paris hours:", h2["restaurants"]["paris-baguette"]["hours"])


if __name__ == "__main__":
    main()
