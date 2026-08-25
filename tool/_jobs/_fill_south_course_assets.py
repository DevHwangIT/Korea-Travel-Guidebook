# -*- coding: utf-8 -*-
"""Copy unique food photos and download missing landmark stills for south-region courses."""
from __future__ import annotations

import hashlib
import re
import shutil
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMG = ROOT / "Images" / "places"
COURSES = IMG / "_courses"
UA = "KoreaTravelGuidebook/1.0 (course covers; educational)"
CTX = ssl._create_unverified_context()

COURSE_FILES = [
    ROOT / "data/courses/chungcheong-curated.js",
    ROOT / "data/courses/jeolla-curated.js",
    ROOT / "data/courses/gyeongsang-curated.js",
    ROOT / "data/courses/busan-curated.js",
    ROOT / "data/courses/jeju-curated.js",
]

FOOD_SRC = {
    "food-baekban-gongju.jpg": "food-baekban.jpg",
    "food-dolsotbap-buyeo.jpg": "food-dolsotbap.jpg",
    "food-samgyeopsal-buyeo.jpg": "food-samgyeopsal.jpg",
    "food-gukbap-danyang.jpg": "food-gukbap.jpg",
    "food-seafood-daecheon.jpg": "food-seafood.jpg",
    "food-cafe-daecheon.jpg": "food-cafe.jpg",
    "food-seafood-boryeong.jpg": "food-seafood.jpg",
    "food-baekban-taean.jpg": "food-baekban.jpg",
    "food-cafe-taean.jpg": "food-cafe.jpg",
    "food-seafood-taean.jpg": "food-seafood.jpg",
    "food-kalguksu-daejeon.jpg": "food-kalguksu.jpg",
    "food-bread-daejeon.jpg": "food-bread-heyri.jpg",
    "food-samgyeopsal-daejeon.jpg": "food-samgyeopsal.jpg",
    "food-bibimbap-jeonju.jpg": "food-bibimbap.jpg",
    "food-cafe-jeonju.jpg": "food-cafe.jpg",
    "food-galbijjim-jeonju.jpg": "food-galbijjim.jpg",
    "food-seafood-yeosu.jpg": "food-seafood.jpg",
    "food-baekban-suncheon.jpg": "food-baekban.jpg",
    "food-samgyeopsal-suncheon.jpg": "food-samgyeopsal.jpg",
    "food-tteokgalbi-damyang.jpg": "food-galbijjim.jpg",
    "food-cafe-damyang.jpg": "food-cafe.jpg",
    "food-dolsotbap-boseong.jpg": "food-dolsotbap.jpg",
    "food-cafe-boseong.jpg": "food-cafe.jpg",
    "food-seafood-boseong.jpg": "food-seafood.jpg",
    "food-gukbap-mokpo.jpg": "food-gukbap.jpg",
    "food-seafood-mokpo.jpg": "food-seafood.jpg",
    "food-bibimbap-gyeongju.jpg": "food-bibimbap.jpg",
    "food-heotjesabap-andong.jpg": "food-baekban.jpg",
    "food-jjimdak-andong.jpg": "food-galbijjim.jpg",
    "food-seafood-tongyeong.jpg": "food-seafood.jpg",
    "food-seafood-geoje.jpg": "food-seafood.jpg",
    "food-samgyeopsal-geoje.jpg": "food-samgyeopsal.jpg",
    "food-gukbap-pohang.jpg": "food-gukbap.jpg",
    "food-cafe-pohang.jpg": "food-cafe.jpg",
    "food-seafood-guryongpo.jpg": "food-seafood.jpg",
    "food-cafe-guryongpo.jpg": "food-cafe.jpg",
    "food-makchang-daegu.jpg": "food-gopchang.jpg",
    "food-milmyeon-ulsan.jpg": "food-kalguksu.jpg",
    "food-seafood-ulsan.jpg": "food-seafood.jpg",
    "food-dolsotbap-haeinsa.jpg": "food-dolsotbap.jpg",
    "food-cafe-haeinsa.jpg": "food-cafe.jpg",
    "food-milmyeon-haeundae.jpg": "food-kalguksu.jpg",
    "food-seafood-gwangalli.jpg": "food-seafood.jpg",
    "food-dwaeji-nampo.jpg": "food-samgyeopsal.jpg",
    "food-gukbap-songdo-busan.jpg": "food-gukbap.jpg",
    "food-cafe-yeongdo.jpg": "food-cafe.jpg",
    "food-samgyeopsal-yeongdo.jpg": "food-samgyeopsal.jpg",
    "food-seafood-gijang.jpg": "food-seafood.jpg",
    "food-cafe-gijang.jpg": "food-cafe.jpg",
    "food-seafood-gijang-dinner.jpg": "food-seafood.jpg",
    "food-baekban-yeongdo.jpg": "food-baekban.jpg",
    "food-cafe-jeolyeong.jpg": "food-cafe.jpg",
    "food-milmyeon-seomyeon.jpg": "food-kalguksu.jpg",
    "food-dakgalbi-seomyeon.jpg": "food-chicken.jpg",
    "food-haemul-seongsan.jpg": "food-seafood.jpg",
    "food-cafe-seongsan.jpg": "food-cafe.jpg",
    "food-blackpork-seongsan.jpg": "food-samgyeopsal.jpg",
    "food-seafood-udo.jpg": "food-seafood.jpg",
    "food-peanut-udo.jpg": "food-bingsu.jpg",
    "food-gukbap-hallim.jpg": "food-gukbap.jpg",
    "food-cafe-westjeju.jpg": "food-cafe.jpg",
    "food-haemul-aewol.jpg": "food-seafood.jpg",
    "food-cafe-aewol.jpg": "food-cafe.jpg",
    "food-blackpork-aewol.jpg": "food-samgyeopsal.jpg",
    "food-blackpork-seogwipo.jpg": "food-samgyeopsal.jpg",
    "food-haemul-jungmun.jpg": "food-seafood.jpg",
    "food-cafe-jungmun.jpg": "food-cafe.jpg",
    "food-blackpork-jungmun.jpg": "food-samgyeopsal.jpg",
    "food-blackpork-hallasan.jpg": "food-samgyeopsal.jpg",
    "food-gukbap-jejusi.jpg": "food-gukbap.jpg",
    "food-haemul-dongmun.jpg": "food-seafood.jpg",
    "food-haemul-woljeong.jpg": "food-seafood.jpg",
    "food-cafe-eastjeju.jpg": "food-cafe.jpg",
    "food-baekban-sagye.jpg": "food-baekban.jpg",
}

COMMONS = {
    "muryeong-tomb.jpg": ["Tomb of King Muryeong.jpg", "무령왕릉.jpg", "Songsan-ri Tombs.jpg"],
    "gongju-museum.jpg": ["Gongju National Museum.jpg", "국립공주박물관.jpg"],
    "jemincheon.jpg": ["Jemincheon.jpg", "제민천.jpg", "Gongju old town.jpg"],
    "gungnamji.jpg": ["Gungnamji.jpg", "궁남지.jpg", "Gungnamji Pond.jpg"],
    "jeongnimsaji.jpg": ["Jeongnimsa Temple Site.jpg", "정림사지.jpg", "Jeongnimsaji.jpg"],
    "dodamsambong.jpg": ["Dodamsambong.jpg", "도담삼봉.jpg", "Danyang Dodamsambong.jpg"],
    "mancheonha.jpg": ["Mancheonha Skywalk.jpg", "만천하스카이워크.jpg"],
    "danyang-jando.jpg": ["Danyanggang Jando.jpg", "단양강잔도.jpg"],
    "danyang-paragliding.jpg": ["Danyang paragliding.jpg", "단양 패러글라이딩.jpg", "Cafe San Danyang.jpg"],
    "danyang-market.jpg": ["Danyang Gyeong Market.jpg", "단양구경시장.jpg"],
    "daecheon-skybike.jpg": ["Daecheon Sky Bike.jpg", "대천 스카이바이크.jpg", "Daecheon Beach.jpg"],
    "daecheon-sunset.jpg": ["Daecheon Beach sunset.jpg", "대천해수욕장 일몰.jpg", "Daecheon Beach.jpg"],
    "anmyeondo.jpg": ["Anmyeondo.jpg", "안면도.jpg", "Anmyeon Island.jpg"],
    "kkotji-sunset.jpg": ["Kkotji Beach sunset.jpg", "꽃지해수욕장.jpg", "Kkotji Beach.jpg"],
    "daejeon-science-museum.jpg": ["National Science Museum Daejeon.jpg", "국립중앙과학관.jpg"],
    "hanbit-tower.jpg": ["Hanbit Tower.jpg", "한빛탑.jpg", "Expo Science Park Daejeon.jpg"],
    "daejeon-oldtown.jpg": ["Daejeon Eunhaeng-dong.jpg", "대전 원도심.jpg", "Daejeon downtown.jpg"],
    "gyeonggijeon.jpg": ["Gyeonggijeon.jpg", "경기전.jpg"],
    "jeondong-cathedral.jpg": ["Jeondong Cathedral.jpg", "전동성당.jpg"],
    "yeosu-cablecar.jpg": ["Yeosu Cable Car.jpg", "여수해상케이블카.jpg"],
    "yi-sunsin-square.jpg": ["Yi Sun-sin Square.jpg", "이순신광장.jpg", "Yeosu Yi Sun-sin Square.jpg"],
    "yeosu-night.jpg": ["Yeosu night view.jpg", "여수 밤바다.jpg", "Yeosu harbor night.jpg"],
    "suncheon-garden.jpg": ["Suncheon Bay National Garden.jpg", "순천만국가정원.jpg"],
    "suncheon-yongsan.jpg": ["Yongsan Observatory Suncheon.jpg", "순천만 용산전망대.jpg"],
    "suncheon-sunset.jpg": ["Suncheon Bay sunset.jpg", "순천만 일몰.jpg"],
    "juknokwon.jpg": ["Juknokwon.jpg", "죽녹원.jpg", "Damyang Juknokwon.jpg"],
    "gwanbangjerim.jpg": ["Gwanbangjerim.jpg", "관방제림.jpg"],
    "metasequoia-road.jpg": ["Damyang Metasequoia Road.jpg", "담양 메타세쿼이아길.jpg"],
    "metaprovence.jpg": ["Metaprovence.jpg", "메타프로방스.jpg", "Damyang Metaprovence.jpg"],
    "yulpo-beach.jpg": ["Yulpo Beach.jpg", "율포해수욕장.jpg"],
    "yulpo-walk.jpg": ["Yulpo Beach.jpg", "보성 율포.jpg"],
    "mokpo-cablecar.jpg": ["Mokpo Cable Car.jpg", "목포해상케이블카.jpg"],
    "yudalsan.jpg": ["Yudalsan.jpg", "유달산.jpg", "Yudal Mountain.jpg"],
    "mokpo-peace-plaza.jpg": ["Mokpo Peace Plaza.jpg", "목포 평화광장.jpg", "Gatbawi Mokpo.jpg"],
    "daereungwon.jpg": ["Daereungwon.jpg", "대릉원.jpg", "Cheonmachong.jpg"],
    "cheomseongdae.jpg": ["Cheomseongdae.jpg", "첨성대.jpg"],
    "buyongdae.jpg": ["Buyongdae.jpg", "부용대.jpg", "Hahoe Buyongdae.jpg"],
    "hahoe-mask.jpg": ["Hahoe Mask Museum.jpg", "하회탈박물관.jpg"],
    "byeongsan-seowon.jpg": ["Byeongsan Seowon.jpg", "병산서원.jpg"],
    "tongyeong-cablecar.jpg": ["Tongyeong Cable Car.jpg", "통영케이블카.jpg"],
    "dongpirang.jpg": ["Dongpirang Village.jpg", "동피랑.jpg", "Dongpirang mural village.jpg"],
    "gangguan.jpg": ["Gangguan Tongyeong.jpg", "강구안.jpg", "Tongyeong harbor.jpg"],
    "tongyeong-park.jpg": ["Yi Sun-sin Park Tongyeong.jpg", "통영 이순신공원.jpg"],
    "geoje-pier.jpg": ["Geoje ferry.jpg", "외도 선착장.jpg", "Haegeumgang cruise.jpg"],
    "haegeumgang.jpg": ["Haegeumgang.jpg", "해금강.jpg"],
    "oedo-botania.jpg": ["Oedo Botania.jpg", "외도보타니아.jpg", "Oedo Island.jpg"],
    "windy-hill.jpg": ["Windy Hill Geoje.jpg", "바람의언덕.jpg"],
    "sinseondae.jpg": ["Sinseondae Geoje.jpg", "신선대 거제.jpg"],
    "space-walk.jpg": ["Space Walk Pohang.jpg", "스페이스워크.jpg", "Pohang Space Walk.jpg"],
    "homigot.jpg": ["Homigot.jpg", "호미곶.jpg", "Homigot sunrise.jpg"],
    "guryongpo-houses.jpg": ["Guryongpo Japanese houses.jpg", "구룡포 일본인가옥거리.jpg"],
    "apsan.jpg": ["Apsan Observatory.jpg", "앞산전망대.jpg", "Apsan Daegu.jpg"],
    "apsan-night.jpg": ["Apsan night view.jpg", "대구 앞산 야경.jpg", "Apsan Observatory.jpg"],
    "taehwa-garden.jpg": ["Taehwagang National Garden.jpg", "태화강국가정원.jpg"],
    "ulsan-coast.jpg": ["Ilsan Beach Ulsan.jpg", "울산 일산해수욕장.jpg"],
    "tripitaka.jpg": ["Tripitaka Koreana.jpg", "팔만대장경.jpg", "Haeinsa Tripitaka.jpg"],
    "gayasan.jpg": ["Gayasan.jpg", "가야산.jpg", "Gayasan National Park.jpg"],
    "dongbaekseom.jpg": ["Dongbaekseom.jpg", "동백섬.jpg", "Dongbaek Island Busan.jpg"],
    "cheongsapo.jpg": ["Cheongsapo.jpg", "청사포.jpg", "Cheongsapo Daritdol.jpg"],
    "yongdusan.jpg": ["Yongdusan Park.jpg", "용두산공원.jpg", "Busan Tower.jpg"],
    "songdo-cablecar.jpg": ["Songdo Cable Car Busan.jpg", "송도해상케이블카.jpg"],
    "amnam-park.jpg": ["Amnam Park.jpg", "암남공원.jpg"],
    "huinnyeoul.jpg": ["Huinnyeoul Culture Village.jpg", "흰여울문화마을.jpg"],
    "gijang-coast.jpg": ["Gijang coast.jpg", "기장 해안.jpg", "Haedong Yonggungsa coast.jpg"],
    "osiria.jpg": ["Osiria Station.jpg", "오시리아.jpg", "Ananti Cove.jpg"],
    "gijang-sunset.jpg": ["Gijang sunset.jpg", "기장 일몰.jpg", "Haeundae sunrise.jpg"],
    "jeolyeong-trail.jpg": ["Jeolyeong Coastal Trail.jpg", "절영해안산책로.jpg"],
    "busan-port-night.jpg": ["Busan Port night.jpg", "부산항 야경.jpg"],
    "jeonpo.jpg": ["Jeonpo Cafe Street.jpg", "전포카페거리.jpg"],
    "jeonpo-shops.jpg": ["Jeonpo.jpg", "전포동.jpg", "Seomyeon Busan.jpg"],
    "seomyeon-night.jpg": ["Seomyeon night.jpg", "서면 야경.jpg", "Seomyeon Busan.jpg"],
    "gwangchigi.jpg": ["Gwangchigi Beach.jpg", "광치기해변.jpg"],
    "seongsan-port.jpg": ["Seongsan Port.jpg", "성산항.jpg", "Seongsan Ilchulbong ferry.jpg"],
    "udo-coast.jpg": ["Udo Island coast.jpg", "우도 해안.jpg", "Udo Jeju.jpg"],
    "udo-beach.jpg": ["Geommeolle Beach.jpg", "검멀레해변.jpg", "Udo Beach.jpg"],
    "osulloc.jpg": ["O'sulloc Tea Museum.jpg", "오설록.jpg", "Osulloc.jpg"],
    "westjeju-sunset.jpg": ["Hyeopjae sunset.jpg", "협재 일몰.jpg", "Hyeopjae Beach.jpg"],
    "aewol-coast.jpg": ["Aewol coast.jpg", "애월 해안도로.jpg", "Aewol Jeju.jpg"],
    "handam.jpg": ["Handam Coastal Trail.jpg", "한담해안산책로.jpg"],
    "aewol-sunset.jpg": ["Aewol sunset.jpg", "애월 일몰.jpg", "Gwokji Beach.jpg"],
    "cheonjiyeon.jpg": ["Cheonjiyeon Falls.jpg", "천지연폭포.jpg"],
    "saeyeon-bridge.jpg": ["Saeyeon Bridge.jpg", "새연교.jpg"],
    "seogwipo-coast.jpg": ["Seogwipo coast.jpg", "서귀포 해안.jpg"],
    "yeomiji.jpg": ["Yeomiji Botanical Garden.jpg", "여미지식물원.jpg"],
    "hallasan-crater.jpg": ["Hallasan Baengnokdam.jpg", "백록담.jpg", "Hallasan crater.jpg"],
    "hallasan-trail.jpg": ["Hallasan trail.jpg", "한라산 등산.jpg", "Hallasan.jpg"],
    "yongduam.jpg": ["Yongduam.jpg", "용두암.jpg"],
    "yongyeon.jpg": ["Yongyeon Valley.jpg", "용연계곡.jpg"],
    "tapdong.jpg": ["Tapdong Jeju.jpg", "탑동.jpg", "Jeju Tapdong.jpg"],
    "yongnuni.jpg": ["Yongnuni Oreum.jpg", "용눈이오름.jpg"],
    "sehwa-beach.jpg": ["Sehwa Beach.jpg", "세화해변.jpg"],
    "sanbangsan.jpg": ["Sanbangsan.jpg", "산방산.jpg"],
    "songaksan.jpg": ["Songaksan.jpg", "송악산.jpg"],
    "sagye-coast.jpg": ["Sagye Beach.jpg", "사계해안.jpg"],
    "sagye-sunset.jpg": ["Sagye sunset.jpg", "사계 일몰.jpg", "Songaksan sunset.jpg"],
}


def collect_paths() -> list[Path]:
    seen: set[str] = set()
    out: list[Path] = []
    pat = re.compile(r'(?:cover:|image:)\s*"(\.\./\.\./Images/[^"]+)"')
    for fp in COURSE_FILES:
        for rel in pat.findall(fp.read_text(encoding="utf-8")):
            if rel in seen:
                continue
            seen.add(rel)
            out.append(ROOT / rel.replace("../../", ""))
    return out


def copy_food() -> None:
    for dest_name, src_name in FOOD_SRC.items():
        dest = IMG / dest_name
        src = IMG / src_name
        if dest.exists() and dest.stat().st_size > 8000:
            continue
        if not src.exists():
            print("FOOD SRC MISSING", src_name)
            continue
        shutil.copy2(src, dest)
        print("copied food", dest_name)


def commons_urls(title: str, width: int = 1280) -> list[str]:
    name = title.replace(" ", "_")
    digest = hashlib.md5(name.encode("utf-8")).hexdigest()
    a, ab = digest[0], digest[:2]
    quoted = urllib.parse.quote(name, safe="/()")
    return [
        f"https://upload.wikimedia.org/wikipedia/commons/thumb/{a}/{ab}/{quoted}/{width}px-{quoted}",
        f"https://upload.wikimedia.org/wikipedia/commons/{a}/{ab}/{quoted}",
    ]


def save_url(url: str, dest: Path) -> bool:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=45, context=CTX) as r:
            data = r.read()
        if len(data) < 8000:
            return False
        dest.write_bytes(data)
        return True
    except Exception:
        return False


def fetch_missing(paths: list[Path]) -> None:
    COURSES.mkdir(parents=True, exist_ok=True)
    for path in paths:
        if path.exists() and path.stat().st_size > 8000:
            continue
        name = path.name
        titles = COMMONS.get(name, [])
        if not titles:
            print("NO COMMONS MAP", path.relative_to(ROOT).as_posix())
            continue
        ok = False
        for title in titles:
            for url in commons_urls(title):
                time.sleep(0.4)
                if save_url(url, path):
                    print("OK", name, title, path.stat().st_size)
                    ok = True
                    break
            if ok:
                break
        if not ok:
            print("FAIL", name)


def main() -> None:
    copy_food()
    paths = collect_paths()
    print("course image refs", len(paths))
    fetch_missing(paths)
    missing = [p for p in paths if not p.exists() or p.stat().st_size < 8000]
    print("still missing", len(missing))
    for p in missing:
        print(" ", p.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
