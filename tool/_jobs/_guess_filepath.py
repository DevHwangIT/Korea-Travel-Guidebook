# -*- coding: utf-8 -*-
"""Guess Commons FilePath from Korean names for leftover places."""
from __future__ import annotations

import importlib.util
import re
import sys
import time
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "fill_ph", ROOT / "tool" / "_fill_placeholder_photos.py"
)
fill = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fill)

GUESSES: dict[str, list[str]] = {
    "soyang-lake": ["소양호.jpg", "Soyangho.jpg", "Soyang Lake.jpg"],
    "paro-lake": ["파로호.jpg", "Paroho.jpg"],
    "junam-reservoir": ["주남저수지.jpg", "Junam Reservoir.jpg"],
    "sanjeong-lake": ["산정호수.jpg", "Sanjeong Lake.jpg"],
    "seonyudo-beach": ["선유도.jpg", "Seonyudo.jpg", "선유도 해수욕장.jpg"],
    "byeonsan-beach": ["변산해수욕장.jpg", "Byeonsan.jpg"],
    "jebiwon-seokbul": ["제비원석불.jpg", "제비원 석불.jpg", "Jebiwon.jpg"],
    "andotminsokchon": ["안동민속촌.jpg", "Andong Folk Village.jpg"],
    "museolmaeul": ["무섬마을.jpg", "Museom Village.jpg"],
    "seonbichon": ["선비촌.jpg", "영주선비촌.jpg"],
    "munhaksanseot": ["문학산성.jpg", "Munhaksanseong.jpg"],
    "isathwa-gotaek": ["이상화고택.jpg", "이상화 고택.jpg"],
    "seoknalsa": ["석남사.jpg", "Seongnamsa.jpg"],
    "nalhae-geulsan-borial": ["보리암.jpg", "남해보리암.jpg", "Boriam.jpg"],
    "sotsanri-gobungun": ["무령왕릉.jpg", "송산리고분군.jpg"],
    "neutsanri-gobungun": ["능산리고분군.jpg"],
    "dalyat-sikyeotjeot": ["식영정.jpg"],
    "dalyat-myeotokheon": ["명옥헌.jpg"],
    "wolbotseowon": ["월봉서원.jpg"],
    "totyeot-chutryeolsa": ["통영충렬사.jpg", "충렬사.jpg"],
    "yeosu-chutminsa": ["충민사.jpg"],
    "iksan-watgutriyujeok": ["왕궁리유적.jpg"],
    "bus-terminal-ulsan": ["울산고속버스터미널.jpg"],
    "arte-museum-jeju": ["아르떼뮤지엄.jpg", "ARTE Museum.jpg"],
    "gangcheonsan": ["강천산.jpg"],
    "cheongwansan": ["천관산.jpg"],
    "paryeongsan": ["팔영산.jpg"],
    "iho-tewoo-beach": ["이호테우해수욕장.jpg"],
    "kkotji-beach": ["꽃지해수욕장.jpg"],
    "jangseong-lake": ["장성호.jpg"],
    "eunpa-lake-park": ["은파호수공원.jpg"],
    "cheongpung-lake": ["청풍호.jpg"],
    "gwatju-5-18-minjuhwaundot-gwanryeon-sajeok": [
        "국립5·18민주묘지.jpg",
        "5.18 묘지.jpg",
        "May 18th National Cemetery.jpg",
    ],
    "oryundae-hanguksungyojabakmulgwan": ["한국순교자박물관.jpg"],
    "busanhat-je1budu-geundaeyusan": ["부산항 제1부두.jpg", "부산항.jpg"],
}


def filepath(name: str) -> str:
    return (
        "https://commons.wikimedia.org/wiki/Special:FilePath/"
        + urllib.parse.quote(name)
        + "?width=800"
    )


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    hashes = fill.type_hashes()
    ko_names = fill.load_ko_names()
    places = fill.parse_places()
    need = [p for p in places if fill.is_placeholder(p["slug"], hashes)]
    by_slug = {p["slug"]: p for p in need}
    ok = 0
    for slug, names in GUESSES.items():
        if slug not in by_slug and not fill.is_placeholder(slug, hashes):
            continue
        if not fill.is_placeholder(slug, hashes):
            print("skip", slug)
            continue
        print(slug, flush=True)
        saved = False
        for name in names:
            time.sleep(2.2)
            if fill.try_save(filepath(name), fill.dest_path(slug), hashes, f"guess:{name}"):
                saved = True
                note = by_slug.get(slug, {}).get("note")
                if note:
                    for p in need:
                        if p["note"] == note and p["slug"] != slug and fill.is_placeholder(p["slug"], hashes):
                            fill.copy_to(slug, p["slug"])
                            print(" COPY", p["slug"])
                break
        if saved:
            ok += 1
        else:
            print(" miss")
    remain = sum(1 for p in fill.parse_places() if fill.is_placeholder(p["slug"], hashes))
    print(f"DONE ok={ok} remaining={remain}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
