#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Translate korean.p.*.en glosses to Russian; keep ko/rom/ja/zh intact."""
from __future__ import annotations

import json
import time
from pathlib import Path

from deep_translator import GoogleTranslator

ROOT = Path(__file__).resolve().parent
RU_PATH = ROOT / "ru.json"
EN_PATH = ROOT / "en.json"


def main() -> None:
    ru = json.loads(RU_PATH.read_text(encoding="utf-8"))
    en = json.loads(EN_PATH.read_text(encoding="utf-8"))
    menu = (ru.get("common") or {}).get("langMenu")
    gt = GoogleTranslator(source="en", target="ru")

    phrases = ru.setdefault("korean", {}).setdefault("p", {})
    en_phrases = (en.get("korean") or {}).get("p") or {}
    n = 0
    keys = list(en_phrases.keys())
    print("phrases", len(keys))
    for i, pid in enumerate(keys):
        e = en_phrases[pid]
        if not isinstance(e, dict):
            continue
        r = phrases.setdefault(pid, {})
        en_gloss = e.get("en")
        if not isinstance(en_gloss, str) or not en_gloss.strip():
            continue
        cur = r.get("en")
        if cur is None or cur == "" or cur == en_gloss:
            tr = (gt.translate(en_gloss) or "").strip() or en_gloss
            r["en"] = tr
            n += 1
            print(f"{i+1}/{len(keys)} {pid}: {en_gloss!r} -> {tr!r}")
            time.sleep(0.05)
        for leaf in ("ko", "rom", "ja", "zh"):
            if leaf in e and (leaf not in r or not r.get(leaf)):
                r[leaf] = e[leaf]

    if menu is not None:
        ru.setdefault("common", {})["langMenu"] = menu

    RU_PATH.write_text(
        json.dumps(ru, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print("filled", n)


if __name__ == "__main__":
    main()
