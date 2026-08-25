# -*- coding: utf-8 -*-
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
C = ROOT / "Images" / "places" / "_courses"
P = ROOT / "Images" / "places"

pairs = [
    ("byeongsan-seowon.jpg", C / "byeongsanseowon.jpg"),
    ("yi-sunsin-square.jpg", C / "isunsin-square.jpg"),
    ("metasequoia-road.jpg", C / "metasequoia-damyang.jpg"),
    ("daejeon-science-museum.jpg", C / "daejeon-science.jpg"),
    ("daejeon-oldtown.jpg", C / "daejeon-downtown.jpg"),
    ("songdo-cablecar.jpg", C / "songdo-cable.jpg"),
    ("osiria.jpg", C / "ananti-osiria.jpg"),
    ("windy-hill.jpg", C / "baramui-eondeok.jpg"),
    ("yongnuni.jpg", C / "yongnuni-oreum.jpg"),
    ("mokpo-peace-plaza.jpg", C / "gatbawi-mokpo.jpg"),
    ("yulpo-walk.jpg", C / "yulpo-coast.jpg"),
    ("muryeong-tomb.jpg", C / "muryeong-tombs.jpg"),
    ("jeonpo.jpg", C / "jeonpo-cafe.jpg"),
]

for dest_name, src in pairs:
    dest = C / dest_name
    if dest.exists() and dest.stat().st_size > 1000:
        print("skip", dest_name)
        continue
    if src.exists():
        shutil.copy2(src, dest)
        print("copied", dest_name, "<-", src.name)
    else:
        print("NO SRC", dest_name, src.name)
