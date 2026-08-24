# -*- coding: utf-8 -*-
"""Retry remaining placeholders via ko.wikipedia page files + Commons FilePath 800px."""
from __future__ import annotations

import importlib.util
import json
import re
import shutil
import sys
import time
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "fill_ph", ROOT / "tool" / "_fill_placeholder_photos.py"
)
fill = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(fill)

ALT: dict[str, list[str]] = {
    "gukrimasiamunhwajeondat": ["국립아시아문화전당"],
    "gwatju-gukrimasiamunhwajeondat": ["국립아시아문화전당"],
    "gatjin-dasanchodat": ["다산초당"],
    "jeonnal-gatjin-dasanchodat": ["다산초당"],
    "jebiwon-seokbul": ["제비원 석불", "제비원"],
    "andot-jebiwon-seokbul": ["제비원 석불"],
    "andotminsokchon": ["안동민속촌"],
    "andot-andotminsokchon": ["안동민속촌"],
    "museolmaeul": ["무섬마을"],
    "yeotju-museolmaeul": ["무섬마을"],
    "seonbichon": ["선비촌"],
    "yeotju-seonbichon": ["선비촌"],
    "munhaksanseot": ["문학산성"],
    "isathwa-gotaek": ["이상화 고택"],
    "sotsanri-gobungun": ["무령왕릉", "송산리 고분군"],
    "gwatju-5-18-minjuhwaundot-gwanryeon-sajeok": ["국립5·18민주묘지"],
    "gwatju-gwatju-5-18-minjuhwaundot-gwanryeon-sajeok": ["국립5·18민주묘지"],
    "soyang-lake": ["소양호"],
    "paro-lake": ["파로호"],
    "junam-reservoir": ["주남저수지"],
    "seonyudo-beach": ["선유도"],
    "byeonsan-beach": ["변산해수욕장"],
    "bus-terminal-ulsan": ["울산고속버스터미널"],
    "arte-museum-jeju": ["아르떼뮤지엄"],
    "dalseong-wetland": ["달성습지"],
    "nalhae-geulsan-borial": ["보리암"],
    "seoknalsa": ["석남사"],
    "totyeot-chutryeolsa": ["충렬사 (통영시)"],
    "yeosu-chutminsa": ["충민사"],
    "iksan-watgutriyujeok": ["왕궁리 유적"],
    "dalyat-sikyeotjeot": ["식영정"],
    "dalyat-myeotokheon": ["명옥헌"],
    "wolbotseowon": ["월봉서원"],
    "sanjeong-lake": ["산정호수"],
    "jangseong-lake": ["장성호"],
    "songji-lake": ["송지호"],
    "gangcheonsan": ["강천산"],
    "cheongwansan": ["천관산"],
    "paryeongsan": ["팔영산"],
    "hwangaksan": ["황악산"],
    "namdeogyusan": ["남덕유산"],
    "cheongwansan": ["천관산"],
}


def titles_for(place: dict, ko_names: dict[str, str]) -> list[str]:
    slug = place["slug"]
    out: list[str] = []
    for t in ALT.get(slug, []):
        out.append(t)
    ko = ko_names.get(slug, "")
    stripped = re.sub(r"\s*\([^)]*\)\s*", " ", ko).strip() if ko else ""
    for t in (stripped, ko):
        if t and t not in out:
            out.append(t)
    seen = []
    for t in out:
        if t not in seen:
            seen.append(t)
    return seen[:3]


def filepath_url(filename: str) -> str:
    return (
        "https://commons.wikimedia.org/wiki/Special:FilePath/"
        + urllib.parse.quote(filename)
        + "?width=800"
    )


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    hashes = fill.type_hashes()
    ko_names = fill.load_ko_names()
    places = fill.parse_places()

    # ACC already downloaded in probe — copy regional duplicate
    acc = fill.dest_path("gukrimasiamunhwajeondat")
    acc2 = fill.dest_path("gwatju-gukrimasiamunhwajeondat")
    if acc.exists() and fill.sha1(acc) not in hashes:
        if fill.is_placeholder("gwatju-gukrimasiamunhwajeondat", hashes):
            shutil.copy2(acc, acc2)
            print("COPY ACC -> gwatju-gukrimasiamunhwajeondat", flush=True)

    need = [p for p in places if fill.is_placeholder(p["slug"], hashes)]
    groups = fill.group_places(need, ko_names)
    print(f"need={len(need)} groups={len(groups)}", flush=True)

    ok = miss = 0
    for i, group in enumerate(groups, 1):
        primary = group[0]
        slug = primary["slug"]
        dest = fill.dest_path(slug)
        print(
            f"\n[{i}/{len(groups)}] {slug} — {ko_names.get(slug, primary['note'])}",
            flush=True,
        )
        saved = False
        used = ""
        for title in titles_for(primary, ko_names):
            print(f"  wiki ko: {title}", flush=True)
            time.sleep(3.0)
            page = fill.wiki_page_bundle(title, "ko")
            if not page:
                continue
            src = fill.wiki_thumb_from_page(page)
            if src and fill.try_save(src, dest, hashes, f"thumb:{title}"):
                saved, used = True, f"thumb:{title}"
                break
            files = fill.wiki_files_from_page(page)
            named = [f for f in files if fill.name_in_candidate(f, [title])]
            rest = [f for f in files if f not in named]
            for fname in (named + rest)[:3]:
                print(f"  file: {fname}", flush=True)
                time.sleep(2.4)
                if fill.try_save(filepath_url(fname), dest, hashes, f"file:{fname}"):
                    saved, used = True, f"file:{fname}"
                    break
            if saved:
                break
        if saved:
            ok += 1
            for p in group[1:]:
                fill.copy_to(slug, p["slug"])
                print(f"  COPY -> {p['slug']}", flush=True)
            print(f"  SOURCE {used}", flush=True)
        else:
            miss += 1
            print("  MISS", flush=True)

    remain = sum(1 for p in fill.parse_places() if fill.is_placeholder(p["slug"], hashes))
    print(f"\nDONE ok={ok} miss={miss} remaining={remain}", flush=True)
    (ROOT / "tool" / "_retry_remaining_log.json").write_text(
        json.dumps({"ok": ok, "miss": miss, "remaining": remain}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
