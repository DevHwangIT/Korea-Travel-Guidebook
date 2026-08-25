# -*- coding: utf-8 -*-
"""Remap same-place images, copy region food jpgs, download a few Commons files."""
from __future__ import annotations

import ssl
import shutil
import urllib.request
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[2]
IMG = ROOT / "Images" / "places"
UA = "KoreaTravelGuidebook/1.0 (local asset fill; educational)"

REMAP = {
    "data/courses/chungcheong-curated.js": [
        ("../../Images/places/_courses/gongsanseong.jpg", "../../Images/places/heritage/gotsanseot.jpg"),
    ],
    "data/courses/gyeongsang-curated.js": [
        ("../../Images/places/_courses/seomun-market.jpg", "../../Images/places/market/seomun-market.jpg"),
        ("../../Images/places/_courses/yeongildae.jpg", "../../Images/places/beach/yeongildae-beach.jpg"),
        ("../../Images/places/_courses/yeongildae-night.jpg", "../../Images/places/beach/yeongildae-beach.jpg"),
    ],
    "data/courses/gangwon-curated.js": [
        ("../../Images/places/heritage/gyeotpodae.jpg", "../../Images/places/lake/gyeongpo-lake.jpg"),
        ("../../Images/places/_courses/samaksan-cable.jpg", "../../Images/places/mountain/samaksan.jpg"),
    ],
    "data/courses/jeju-curated.js": [
        ("../../Images/places/_courses/gwokji.jpg", "../../Images/places/beach/gwakji-beach.jpg"),
        ("../../Images/places/_courses/dongmun-market.jpg", "../../Images/places/market/jeju-dongmun-market.jpg"),
        ("../../Images/places/_courses/jeju-mokgwanaji.jpg", "../../Images/places/heritage/jejumok-gwana.jpg"),
    ],
    "data/courses/busan-curated.js": [],
}

FOOD_SRC = {
    "food-bibimbap.jpg": [
        "food-bibimbap-jeonju.jpg",
        "food-bibimbap-gyeongju.jpg",
    ],
    "food-baekban.jpg": [
        "food-baekban-gongju.jpg",
        "food-baekban-pyeongchang.jpg",
        "food-baekban-taean.jpg",
        "food-baekban-suncheon.jpg",
        "food-baekban-yeongdo.jpg",
        "food-baekban-sagye.jpg",
    ],
    "food-gukbap.jpg": [
        "food-gukbap-danyang.jpg",
        "food-gukbap-pohang.jpg",
        "food-gukbap-mokpo.jpg",
        "food-gukbap-hallim.jpg",
        "food-gukbap-jejusi.jpg",
        "food-gukbap-songdo-busan.jpg",
    ],
    "food-seafood.jpg": [
        "food-seafood-gangneung.jpg",
        "food-seafood-yangyang.jpg",
        "food-seafood-donghae.jpg",
        "food-seafood-daecheon.jpg",
        "food-seafood-boryeong.jpg",
        "food-seafood-taean.jpg",
        "food-seafood-yeosu.jpg",
        "food-seafood-boseong.jpg",
        "food-seafood-mokpo.jpg",
        "food-seafood-tongyeong.jpg",
        "food-seafood-geoje.jpg",
        "food-seafood-guryongpo.jpg",
        "food-seafood-ulsan.jpg",
        "food-seafood-gwangalli.jpg",
        "food-seafood-gijang.jpg",
        "food-seafood-gijang-dinner.jpg",
        "food-seafood-udo.jpg",
        "food-haemul-seongsan.jpg",
        "food-haemul-aewol.jpg",
        "food-haemul-jungmun.jpg",
        "food-haemul-dongmun.jpg",
        "food-haemul-woljeong.jpg",
    ],
    "food-cafe.jpg": [
        "food-cafe-anmok.jpg",
        "food-cafe-daecheon.jpg",
        "food-cafe-taean.jpg",
        "food-cafe-jeonju.jpg",
        "food-cafe-damyang.jpg",
        "food-cafe-boseong.jpg",
        "food-cafe-pohang.jpg",
        "food-cafe-guryongpo.jpg",
        "food-cafe-haeinsa.jpg",
        "food-cafe-yeongdo.jpg",
        "food-cafe-gijang.jpg",
        "food-cafe-jeolyeong.jpg",
        "food-cafe-seongsan.jpg",
        "food-cafe-westjeju.jpg",
        "food-cafe-aewol.jpg",
        "food-cafe-jungmun.jpg",
        "food-cafe-eastjeju.jpg",
    ],
    "food-samgyeopsal.jpg": [
        "food-samgyeopsal-buyeo.jpg",
        "food-samgyeopsal-daejeon.jpg",
        "food-samgyeopsal-suncheon.jpg",
        "food-samgyeopsal-geoje.jpg",
        "food-samgyeopsal-yeongdo.jpg",
        "food-blackpork-seongsan.jpg",
        "food-blackpork-aewol.jpg",
        "food-blackpork-seogwipo.jpg",
        "food-blackpork-jungmun.jpg",
        "food-blackpork-hallasan.jpg",
        "food-dwaeji-nampo.jpg",
    ],
    "food-dolsotbap.jpg": [
        "food-dolsotbap-buyeo.jpg",
        "food-dolsotbap-boseong.jpg",
        "food-dolsotbap-haeinsa.jpg",
    ],
    "food-kalguksu.jpg": ["food-kalguksu-daejeon.jpg"],
    "food-galbijjim.jpg": ["food-galbijjim-jeonju.jpg"],
    "food-chicken.jpg": [
        "food-dakgalbi-chuncheon.jpg",
        "food-dakgalbi-seomyeon.jpg",
        "food-tteokgalbi-damyang.jpg",
    ],
    "food-toast.jpg": ["food-bread-daejeon.jpg", "food-peanut-udo.jpg"],
}

EXTRA_FOOD = {
    "food-ssambap-gangneung.jpg": "food-baekban.jpg",
    "food-salmon-yangyang.jpg": "food-seafood.jpg",
    "food-ojingeo-donghae.jpg": "food-seafood.jpg",
    "food-makguksu-cheorwon.jpg": "food-kalguksu.jpg",
    "food-heotjesabap-andong.jpg": "food-baekban.jpg",
    "food-jjimdak-andong.jpg": "food-dakhanmari.jpg",
    "food-makchang-daegu.jpg": "food-gopchang.jpg",
    "food-milmyeon-haeundae.jpg": "food-kalguksu.jpg",
    "food-milmyeon-seomyeon.jpg": "food-kalguksu.jpg",
    "food-milmyeon-ulsan.jpg": "food-kalguksu.jpg",
}

COMMONS = {
    "Images/places/_courses/cheomseongdae.jpg": "Cheomseongdae.jpg",
    "Images/places/_courses/daereungwon.jpg": "Daereungwon Tumuli Park.jpg",
    "Images/places/_courses/gungnamji.jpg": "Gungnamji.jpg",
    "Images/places/_courses/jeongnimsaji.jpg": "Jeongnimsa.jpg",
    "Images/places/_courses/dodamsambong.jpg": "Dodamsambong.jpg",
    "Images/places/_courses/juknokwon.jpg": "Juknokwon.jpg",
    "Images/places/_courses/homigot.jpg": "Homigot.jpg",
    "Images/places/_courses/yongduam.jpg": "Yongduam.jpg",
    "Images/places/_courses/sanbangsan.jpg": "Sanbangsan.jpg",
    "Images/places/_courses/osulloc.jpg": "O'sulloc Tea Museum.jpg",
    "Images/places/_courses/yongdusan.jpg": "Busan Tower.jpg",
    "Images/places/_courses/dongpirang.jpg": "Dongpirang Village.jpg",
    "Images/places/_courses/chuam-candle.jpg": "Chuam Chotdaebawi.jpg",
    "Images/places/_courses/woljeongsa.jpg": "Woljeongsa.jpg",
    "Images/places/_courses/byeongsan-seowon.jpg": "Byeongsan Seowon.jpg",
    "Images/places/_courses/muryeong-tomb.jpg": "Tomb of King Muryeong.jpg",
    "Images/places/_courses/hanbit-tower.jpg": "Hanbit Tower.jpg",
    "Images/places/_courses/space-walk.jpg": "Space Walk Pohang.jpg",
    "Images/places/_courses/songaksan.jpg": "Songaksan.jpg",
    "Images/places/_courses/cheonjiyeon.jpg": "Cheonjiyeon Waterfall.jpg",
    "Images/places/_courses/gyeonggijeon.jpg": "Gyeonggijeon.jpg",
    "Images/places/_courses/jeondong-cathedral.jpg": "Jeondong Cathedral.jpg",
    "Images/places/_courses/metasequoia-road.jpg": "Damyang Metasequoia-lined Road.jpg",
    "Images/places/_courses/haegeumgang.jpg": "Haegeumgang.jpg",
    "Images/places/_courses/windy-hill.jpg": "Windy Hill Geoje.jpg",
    "Images/places/_courses/oedo-botania.jpg": "Oedo Botania.jpg",
}


def copy_food() -> None:
    for src_name, dests in FOOD_SRC.items():
        src = IMG / src_name
        if not src.exists():
            print("missing food src", src_name)
            continue
        for dest_name in dests:
            dest = IMG / dest_name
            if dest.exists():
                continue
            shutil.copy2(src, dest)
            print("copied", dest_name)
    for dest_name, src_name in EXTRA_FOOD.items():
        src = IMG / src_name
        dest = IMG / dest_name
        if dest.exists() or not src.exists():
            continue
        shutil.copy2(src, dest)
        print("copied", dest_name)


def remap_js() -> None:
    for rel, pairs in REMAP.items():
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        orig = text
        for a, b in pairs:
            text = text.replace(a, b)
        if text != orig:
            path.write_text(text, encoding="utf-8", newline="\n")
            print("remapped", rel)


def download_commons() -> None:
    (IMG / "_courses").mkdir(parents=True, exist_ok=True)
    ctx = ssl._create_unverified_context()
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))
    opener.addheaders = [("User-Agent", UA)]
    urllib.request.install_opener(opener)
    for rel, filename in COMMONS.items():
        dest = ROOT / rel
        if dest.exists():
            continue
        url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.request.quote(filename)
        try:
            urllib.request.urlretrieve(url, dest)
            print("got", rel, dest.stat().st_size)
        except Exception as e:
            print("fail", filename, e)
            if dest.exists():
                dest.unlink()


def main() -> None:
    remap_js()
    copy_food()
    download_commons()


if __name__ == "__main__":
    main()
