# -*- coding: utf-8 -*-
"""Second pass: alternate Wikidata labels + known Commons filenames."""
from __future__ import annotations

import importlib.util
import json
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

wd_spec = importlib.util.spec_from_file_location(
    "wd", ROOT / "tool" / "_fill_from_wikidata.py"
)
wd = importlib.util.module_from_spec(wd_spec)
assert wd_spec and wd_spec.loader
wd_spec.loader.exec_module(wd)

# slug -> extra labels to try on Wikidata
EXTRA: dict[str, list[str]] = {
    "nalwon-gwathanruwon": ["광한루원", "광한루", "Gwanghalluwon"],
    "gukrimasiamunhwajeondat": ["국립아시아문화전당", "Asia Culture Center"],
    "gwatju-gukrimasiamunhwajeondat": ["국립아시아문화전당"],
    "gwatju-5-18-minjuhwaundot-gwanryeon-sajeok": ["국립5·18민주묘지", "5·18기념공원"],
    "gwatju-gwatju-5-18-minjuhwaundot-gwanryeon-sajeok": ["국립5·18민주묘지"],
    "gatjin-dasanchodat": ["다산초당", "Dasanchodang"],
    "jeonnal-gatjin-dasanchodat": ["다산초당"],
    "jebiwon-seokbul": ["제비원석불", "제비원 석불"],
    "andot-jebiwon-seokbul": ["제비원석불"],
    "andotminsokchon": ["안동민속촌"],
    "andot-andotminsokchon": ["안동민속촌"],
    "bothwatsa": ["봉황사 (안동시)"],
    "andot-bothwatsa": ["봉황사 (안동시)"],
    "soyang-lake": ["소양호"],
    "andong-lake": ["안동댐", "안동호"],
    "daecheong-lake": ["대청호", "대청댐"],
    "bomun-lake": ["보문호", "보문관광단지"],
    "paro-lake": ["파로호"],
    "cheongpung-lake": ["청풍호"],
    "goesan-lake": ["괴산호"],
    "sapgyo-lake": ["삽교호"],
    "boryeong-lake": ["보령호"],
    "naejang-lake": ["내장호"],
    "damyang-lake": ["담양호"],
    "yeongsan-lake": ["영산호"],
    "junam-reservoir": ["주남저수지"],
    "eunpa-lake-park": ["은파호수공원"],
    "seolbong-lake": ["설봉호"],
    "geumgwang-lake": ["금광호"],
    "sanjeong-lake": ["산정호수"],
    "wangsong-lake": ["왕송호수"],
    "homyeong-lake": ["호명호수"],
    "seonyudo-beach": ["선유도 (군산시)", "선유도"],
    "byeonsan-beach": ["변산해수욕장"],
    "chunjangdae-beach": ["춘장대해수욕장"],
    "jinha-beach": ["진하해수욕장"],
    "kkotji-beach": ["꽃지해수욕장"],
    "iho-tewoo-beach": ["이호테우해수욕장"],
    "munhaksanseot": ["문학산성"],
    "isathwa-gotaek": ["이상화고택"],
    "seosatdon-gotaek": ["서상돈고택"],
    "seonbichon": ["선비세상", "영주선비촌"],
    "yeotju-seonbichon": ["영주선비촌"],
    "museolmaeul": ["무섬마을"],
    "yeotju-museolmaeul": ["무섬마을"],
    "totyeot-chutryeolsa": ["충렬사 (통영시)"],
    "yeosu-heutguksa": ["흥국사 (여수시)"],
    "jeonnal-yeosu-heutguksa": ["흥국사 (여수시)"],
    "yeosu-chutminsa": ["충민사"],
    "jeoteum-museotseowon": ["무성서원"],
    "nalwon-manboksaji": ["만복사지"],
    "iksan-watgutriyujeok": ["왕궁리유적"],
    "sotsanri-gobungun": ["송산리고분군"],
    "neutsanri-gobungun": ["능산리고분군"],
    "dalyat-sikyeotjeot": ["식영정"],
    "jeonnal-dalyat-sikyeotjeot": ["식영정"],
    "dalyat-myeotokheon": ["명옥헌"],
    "jeonnal-dalyat-myeotokheon": ["명옥헌"],
    "jatseot-pilalseowon": ["필암서원"],
    "jeonnal-jatseot-pilalseowon": ["필암서원"],
    "wolbotseowon": ["월봉서원"],
    "gwatju-wolbotseowon": ["월봉서원"],
    "dotchundat": ["동춘당"],
    "daejeon-dotchundat": ["동춘당"],
    "cheoyotal": ["처용암"],
    "ulsan-cheoyotal": ["처용암"],
    "seoknalsa": ["석남사"],
    "ulsan-seoknalsa": ["석남사"],
    "cheonjeonri-gakseok": ["울산 천전리 각석"],
    "ulsan-cheonjeonri-gakseok": ["울산 천전리 각석"],
    "arte-museum-jeju": ["아르떼뮤지엄"],
    "oryundae-hanguksungyojabakmulgwan": ["오륜대한국순교자박물관"],
    "busanhat-je1budu-geundaeyusan": ["부산항제1부두"],
    "goseot-watgokmaeul": ["왕곡마을"],
    "nalgosanseot": ["남고산성"],
    "imokdae": ["이목대"],
    "yuksinsa": ["육신사"],
    "muju-jeoksatsanseot": ["적상산성"],
    "ilsil-saseondae": ["사선대"],
    "dokrakjeot": ["독락정"],
    "sejot-dokrakjeot": ["독락정"],
    "chwigajeot": ["취가정"],
    "gwatju-chwigajeot": ["취가정"],
    "nalhae-geulsan-borial": ["보리암 (남해군)"],
    "sotgatjeot": ["송강정"],
    "dalyat-sotgatjeot": ["송강정"],
    "okjeongobungun": ["옥전 고분군"],
    "hoedeokhyatgyo": ["회덕향교"],
    "daejeon-hoedeokhyatgyo": ["회덕향교"],
    "jatgihyatgyo": ["장기향교"],
    "gangcheonsan": ["강천산"],
    "cheongwansan": ["천관산"],
    "paryeongsan": ["팔영산"],
    "dalseong-wetland": ["달성습지"],
    "yeojaman": ["여자만"],
    "bus-terminal-ulsan": ["울산고속버스터미널", "Ulsan Express Bus Terminal"],
}

# Direct Commons filenames when the label is well-known
FILES: dict[str, list[str]] = {
    "nalwon-gwathanruwon": [
        "Gwanghalluwon 1.JPG",
        "Gwanghanru.jpg",
        "KOCIS Korea Jeonju Gwanghalluwon 20150508 04 (17265723709).jpg",
    ],
    "soyang-lake": ["Soyangho.jpg", "Soyang Lake.jpg", "소양호.jpg"],
    "andong-lake": ["Andong Dam.jpg", "안동댐.jpg"],
    "bomun-lake": ["Bomun Lake Gyeongju.jpg", "보문호.jpg"],
    "daecheong-lake": ["Daecheong Lake.jpg", "대청호.jpg"],
    "jebiwon-seokbul": ["Jebiwon Stone Buddha.jpg", "제비원 석불.jpg"],
    "gukrimasiamunhwajeondat": [
        "Asia Culture Center in Gwangju.jpg",
        "국립아시아문화전당.jpg",
    ],
    "gwatju-gukrimasiamunhwajeondat": [
        "Asia Culture Center in Gwangju.jpg",
        "국립아시아문화전당.jpg",
    ],
    "gatjin-dasanchodat": ["Dasanchodang.jpg", "다산초당.jpg"],
    "jeonnal-gatjin-dasanchodat": ["Dasanchodang.jpg"],
    "seonyudo-beach": ["Seonyudo Gunsan.jpg", "선유도.jpg"],
    "munhaksanseot": ["Munhaksanseong.jpg", "문학산성.jpg"],
    "isathwa-gotaek": ["Yi Sang-hwa House.jpg", "이상화 고택.jpg"],
    "museolmaeul": ["Museom Village.jpg", "무섬마을.jpg"],
    "yeotju-museolmaeul": ["Museom Village.jpg"],
    "jatseot-pilalseowon": ["Pilam Seowon.jpg", "필암서원.jpg"],
    "jeoteum-museotseowon": ["Museongseowon.jpg", "무성서원.jpg"],
    "sotsanri-gobungun": ["Songsan-ri Tombs.jpg", "무령왕릉.jpg"],
    "iho-tewoo-beach": ["Iho Tewoo Beach.jpg", "이호테우.jpg"],
    "arte-museum-jeju": ["ARTE Museum Jeju.jpg"],
}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    hashes = fill.type_hashes()
    ko_names = fill.load_ko_names()
    places = fill.parse_places()
    need = [p for p in places if fill.is_placeholder(p["slug"], hashes)]
    print(f"need={len(need)}", flush=True)

    labels = []
    for p in need:
        for lab in EXTRA.get(p["slug"], []):
            labels.append(lab)
    label_map = wd.lookup_map(labels, "ko") if labels else {}
    # also try @en for latin labels
    en_labels = [x for x in labels if not any("가" <= ch <= "힣" for ch in x)]
    if en_labels:
        label_map.update({k: v for k, v in wd.lookup_map(en_labels, "en").items() if v})

    ok = miss = 0
    seen_slug = set()
    for p in need:
        slug = p["slug"]
        if slug in seen_slug:
            continue
        seen_slug.add(slug)
        dest = fill.dest_path(slug)
        print(f"{slug}", flush=True)
        saved = False
        for lab in EXTRA.get(slug, []):
            image = label_map.get(lab)
            if not image:
                continue
            url = wd.file_path_url(image)
            time.sleep(2.2)
            if fill.try_save(url, dest, hashes, f"wd:{lab}"):
                saved = True
                break
        if not saved:
            for fname in FILES.get(slug, []):
                url = (
                    "https://commons.wikimedia.org/wiki/Special:FilePath/"
                    + urllib.parse.quote(fname)
                    + "?width=800"
                )
                time.sleep(2.2)
                if fill.try_save(url, dest, hashes, f"file:{fname}"):
                    saved = True
                    break
        if saved:
            ok += 1
            # copy to duplicate slugs sharing note
            for other in need:
                if other["slug"] != slug and other["note"] == p["note"]:
                    if fill.is_placeholder(other["slug"], hashes):
                        fill.copy_to(slug, other["slug"])
                        print(f"  COPY -> {other['slug']}", flush=True)
        else:
            miss += 1
            print("  miss", flush=True)

    remain = sum(1 for x in fill.parse_places() if fill.is_placeholder(x["slug"], hashes))
    print(f"DONE ok={ok} miss={miss} remaining={remain}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
