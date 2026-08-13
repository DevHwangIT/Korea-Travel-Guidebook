# -*- coding: utf-8 -*-
from __future__ import annotations

import copy
import json
import sys
import time
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parent
sys.path.insert(0, str(TOOL_DIR))

from lib import i18n_store  # noqa: E402
from lib.translate import BatchStatus, translate_text  # noqa: E402

MISSING = ("festivals", "travelTips", "usefulKorean")


def looks_korean(text: str) -> bool:
    return any("\uac00" <= ch <= "\ud7a3" for ch in text)


def walk(ko_node, zh_node, status: BatchStatus):
    if isinstance(ko_node, dict):
        if str(ko_node.get("type") or "") == "text" and "ko" in ko_node:
            out = dict(zh_node) if isinstance(zh_node, dict) else dict(ko_node)
            for lang in ("ko", "en", "ja"):
                if lang in ko_node:
                    out[lang] = ko_node[lang]
            ko_val = str(ko_node.get("ko") or "")
            zh_val = str(out.get("zh") or "")
            if not zh_val or zh_val == ko_val or looks_korean(zh_val):
                out["zh"] = translate_text(ko_val, "zh", status=status) if ko_val else ""
                time.sleep(0.02)
            return out
        out = {}
        zh_dict = zh_node if isinstance(zh_node, dict) else {}
        for key, val in ko_node.items():
            out[key] = walk(val, zh_dict.get(key), status)
        return out
    if isinstance(ko_node, list):
        zh_list = zh_node if isinstance(zh_node, list) else []
        return [
            walk(ko_node[i], zh_list[i] if i < len(zh_list) else None, status)
            for i in range(len(ko_node))
        ]
    if isinstance(ko_node, str):
        zh_str = zh_node if isinstance(zh_node, str) else ""
        if not zh_str or zh_str == ko_node or looks_korean(zh_str):
            if looks_korean(ko_node):
                t = translate_text(ko_node, "zh", status=status)
                time.sleep(0.02)
                return t or ko_node
        return zh_str or ko_node
    return copy.deepcopy(ko_node)


def main() -> int:
    ko = i18n_store.load_lang("ko")
    zh = i18n_store.load_lang("zh")
    status = BatchStatus()

    print("check:", {lang: ("festivals" in i18n_store.load_lang(lang)) for lang in i18n_store.LANGS})
    for ns in MISSING:
        if ns not in ko:
            print(f"skip missing in ko: {ns}")
            continue
        print(f"translating {ns}…", flush=True)
        zh[ns] = walk(ko[ns], zh.get(ns), status)

    # Force high-quality festival labels
    zh.setdefault("festivals", {})
    zh["festivals"].update(
        {
            "pageTitle": "节日与活动 | Korea Travel Guide",
            "title": "节日与活动",
            "intro": "各地区节日与代表性活动将陆续添加。",
            "placeholder": "各地区节日与代表性活动将陆续添加",
            "regionsTitle": "按地区浏览节日",
            "regionsHint": "首尔、釜山、济州等地区板块正在准备中。",
            "back": "← 节日与活动",
        }
    )
    zh.setdefault("home", {})["menuFestivals"] = "节日与活动"
    zh.setdefault("apps", {})["kakaoTName"] = "Kakao T"
    zh["apps"]["kakaoTDesc"] = (
        "出租车、代驾、单车、停车等出行服务集于一款应用，常支持境外银行卡支付。"
    )
    if "kakaoTBody" in (ko.get("apps") or {}):
        zh["apps"]["kakaoTBody"] = copy.deepcopy(ko["apps"]["kakaoTBody"])

    # Sync restaurant menuItems from KO
    for slug, entry in (ko.get("restaurants") or {}).items():
        if not isinstance(entry, dict):
            continue
        z = zh.setdefault("restaurants", {}).setdefault(slug, {})
        if not isinstance(z, dict):
            z = {}
            zh["restaurants"][slug] = z
        for key in (
            "menuItems",
            "placeId",
            "placeUrl",
            "mapsUrl",
            "mapsEmbedUrl",
            "mapsProvider",
            "sourceType",
            "phone",
            "hours",
            "category",
            "score",
            "previewImage",
            "previewTitle",
            "body",
        ):
            if key in entry:
                z[key] = copy.deepcopy(entry[key])
        z.pop("photos", None)
        z.pop("gallery", None)
        items = z.get("menuItems")
        if isinstance(items, list):
            for it in items:
                if isinstance(it, dict):
                    it.pop("image", None)

    i18n_store.save_lang("zh", zh)
    print(i18n_store.build_bundle())
    for line in status.note_lines():
        print(line)
    print("zh festivals title:", zh.get("festivals", {}).get("title"))
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
