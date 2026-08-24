# -*- coding: utf-8 -*-
import time
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("fill_ph", ROOT / "tool" / "_fill_placeholder_photos.py")
fill = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fill)

TARGETS = [
    ("gukrimasiamunhwajeondat", "국립아시아문화전당"),
    ("gwatju-gukrimasiamunhwajeondat", "국립아시아문화전당"),
    ("gatjin-dasanchodat", "다산초당"),
    ("jeonnal-gatjin-dasanchodat", "다산초당"),
    ("jebiwon-seokbul", "제비원"),
    ("andot-jebiwon-seokbul", "제비원"),
    ("andotminsokchon", "안동민속촌"),
    ("seonbichon", "선비촌"),
    ("museolmaeul", "무섬마을"),
    ("dotchundat", "동춘당"),
    ("isathwa-gotaek", "이상화 고택"),
    ("munhaksanseot", "문학산성"),
    ("soyang-lake", "소양호"),
    ("paro-lake", "파로호"),
    ("junam-reservoir", "주남저수지"),
    ("seonyudo-beach", "선유도"),
    ("byeonsan-beach", "변산반도"),
    ("iho-tewoo-beach", "이호테우해수욕장"),
    ("sotsanri-gobungun", "무령왕릉"),
    ("gwatju-5-18-minjuhwaundot-gwanryeon-sajeok", "국립5·18민주묘지"),
]

def main():
    hashes = fill.type_hashes()
    ok = 0
    for slug, title in TARGETS:
        if not fill.is_placeholder(slug, hashes):
            print("skip", slug)
            continue
        print("rest", slug, title, flush=True)
        time.sleep(6)
        src = fill.rest_summary_thumb(title, "ko")
        if fill.try_save(src, fill.dest_path(slug), hashes, f"rest:{title}"):
            ok += 1
            # copy same title slugs
            for other, t2 in TARGETS:
                if t2 == title and other != slug and fill.is_placeholder(other, hashes):
                    fill.copy_to(slug, other)
                    print(" COPY", other)
        else:
            print(" miss", slug)
    remain = sum(1 for p in fill.parse_places() if fill.is_placeholder(p["slug"], hashes))
    print(f"DONE ok={ok} remaining={remain}", flush=True)

if __name__ == "__main__":
    main()
