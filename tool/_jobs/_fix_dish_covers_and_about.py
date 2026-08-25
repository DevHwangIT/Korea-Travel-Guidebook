# -*- coding: utf-8 -*-
"""Replace new-dish hub covers with food photos; rewrite added-shop about texts."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image

JOBS_DIR = Path(__file__).resolve().parent
TOOL_DIR = JOBS_DIR.parent
ROOT = TOOL_DIR.parent
sys.path.insert(0, str(TOOL_DIR))

from lib.cache_bust import bump_asset_version  # noqa: E402
from lib.content import _write_text_retry, rebuild_food_recommend_catalog  # noqa: E402

FOODS_DIR = ROOT / "i18n" / "pages" / "foods"
LANGS = ("ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru")
COVER_SIZE = (1400, 933)
ASSETS = Path(
    r"C:\Users\HwangInTae\.cursor\projects\c-Users-HwangInTae-Desktop-guide-book-Korea-Travel-Guidebook\assets"
)

COVERS = {
    "jaecheopguk": ("meals", "dish-jaecheopguk.jpg"),
    "agu-jjim": ("meals", "dish-agu-jjim.jpg"),
    "hamburger": ("meals", "dish-hamburger.jpg"),
    "mandu": ("meals", "dish-mandu.jpg"),
    "galbitang": ("meals", "dish-galbitang.jpg"),
    "juk": ("meals", "dish-juk.jpg"),
    "chapssal-kwabaegi": ("desserts", "dish-chapssal-kwabaegi.jpg"),
}

ABOUT = {
    "bonjuk-gyeongbokgung": {
        "ko": "경복궁역 앞 본죽 매장입니다. 죽과 비빔밥을 함께 내며, 아침·가벼운 식사로 찾기 좋습니다.",
        "en": "A Bonjuk shop by Gyeongbokgung Station. Rice porridge and bibimbap make an easy breakfast or light meal.",
    },
    "halmae-jaecheopguk-busan": {
        "ko": "광안리의 재첩국 노포입니다. 낙동강 재첩으로 끓인 맑은 국과 반찬이 나오는 부산 아침·해장 맛집입니다.",
        "en": "A Gwangalli classic for jaecheop-guk — clear marsh-clam soup with side dishes, a Busan breakfast or hangover meal.",
    },
    "gitteul-hongdae": {
        "ko": "홍대·합정 사이 고기집입니다. 이천 돼지고기를 직원이 구워 주며, 회식·데이트로 자주 찾습니다.",
        "en": "A Hongdae Korean BBQ where staff grill Icheon pork at the table. Popular for dates and group dinners.",
    },
    "oneul-gimhae-dwitgogi": {
        "ko": "하단·동아대 근처 김해 뒷고기 전문점입니다. 직원이 고기를 구워 주는 부산 고기집입니다.",
        "en": "A Busan BBQ near Hadan that specializes in Gimhae dwitgogi (pork back cuts), with staff grilling at the table.",
    },
    "kkupdang": {
        "ko": "강남 고기집으로, 목살 등 돼지고기를 구워 먹습니다. 양념·밑반찬이 깔끔해 관광객에게도 접근하기 쉽습니다.",
        "en": "A Gangnam pork BBQ known for neck and other cuts with clean sides — an easy Korean grill stop for travelers.",
    },
    "busandaek-seomyeon": {
        "ko": "서면의 돼지 모듬 고기집입니다. 한 상에 여러 부위를 나눠 먹기 좋아 현지인과 여행객이 함께 찾습니다.",
        "en": "A Seomyeon pork BBQ for mixed-cut platters — easy to share for locals and travelers.",
    },
    "seolyameok-seomyeon": {
        "ko": "서면의 미나리 돼지고기 구이집입니다. 특미나리 가브리살처럼 향긋한 채소와 고기를 함께 냅니다.",
        "en": "Seomyeon pork BBQ served with lots of minari (water dropwort). Signature cuts pair well with the greens.",
    },
    "jeongdeunjip-itaewon": {
        "ko": "이태원 우대갈비·돼지갈비 고기집입니다. 직원이 자리에서 고기를 구워 줍니다.",
        "en": "An Itaewon Korean BBQ known for thick galbi. Staff grill the meat at the table.",
    },
    "nangman-kimbap": {
        "ko": "명동의 김밥·덮밥집입니다. 낭만김밥과 제육덮밥을 빠르게 먹기 좋아 관광 동선에 넣기 쉽습니다.",
        "en": "A Myeongdong kimbap and rice-bowl shop. Nangman kimbap and jeyuk deopbap are quick tourist-friendly meals.",
    },
    "apgujeong-sanghoe": {
        "ko": "압구정로데오의 들기름 막국수집입니다. 메밀면과 들기름 양념이 고소해 가벼운 한 끼로 좋습니다.",
        "en": "Makguksu in Apgujeong Rodeo dressed with perilla oil — a light, nutty buckwheat-noodle meal.",
    },
    "yungane-uijeongbu-budae": {
        "ko": "을지로의 의정부식 부대찌개집입니다. 햄·소시지·김치 국물을 밥과 함께 나눠 먹기 좋습니다.",
        "en": "Uijeongbu-style budae-jjigae in Euljiro — ham, sausage, and kimchi stew to share with rice.",
    },
    "yeongjung-minari-bossam": {
        "ko": "영등포시장의 미나리 보쌈집입니다. 삶은 돼지고기를 미나리·김치와 싸 먹는 현지 한 끼입니다.",
        "en": "Bossam at Yeongdeungpo Market, eaten with minari and kimchi — a local boiled-pork meal.",
    },
    "samojeong-seomyeon": {
        "ko": "서면 삼계탕집입니다. 인삼 닭백숙을 든든하게 내며, 더운 날·보양식으로 찾기 좋습니다.",
        "en": "Samgyetang in Seomyeon — ginseng chicken soup that works as a hearty meal or tonic dish.",
    },
    "nojak-jinseong-agu-dongtan": {
        "ko": "동탄의 아구찜 전문점입니다. 아귀와 콩나물·대창을 매콤하게 쪄 여럿이 나눠 먹기 좋습니다.",
        "en": "Dongtan agu-jjim specialist — spicy braised monkfish with bean sprouts, made for sharing.",
    },
    "bonjeon-dwaeji-gukbap": {
        "ko": "부산역 앞 돼지국밥 노포입니다. 진한 국물에 밥을 말아 먹는 부산의 대표 한 끼입니다.",
        "en": "A pork-rice-soup institution by Busan Station — the classic dwaeji-gukbap bowl.",
    },
    "chacha-tea-club-changsin": {
        "ko": "창신동의 한옥 찻집입니다. 차를 천천히 마시며 동네 골목을 둘러보기 좋은 휴식 공간입니다.",
        "en": "A hanok teahouse in Changsin-dong — a quiet stop for tea while walking the alleys.",
    },
    "bean-brothers-hapjeong": {
        "ko": "합정·상수 인근 스페셜티 커피 로스터리입니다. 필터 커피를 중심으로 한 카페입니다.",
        "en": "A specialty coffee roastery near Hapjeong, known for filter coffee.",
    },
    "starbucks-gyeongju-daereungwon": {
        "ko": "경주 대릉원 앞 스타벅스입니다. 고분 산책 전후 커피를 마시기 좋은 위치입니다.",
        "en": "Starbucks beside Gyeongju’s Daereungwon tombs — a convenient coffee stop before or after a walk.",
    },
    "ilhosanghoe-gwangjang": {
        "ko": "광장시장의 카페·간식 가게입니다. 찹쌀 꽈배기와 커피를 시장 구경 중에 사 먹기 좋습니다.",
        "en": "A Gwangjang Market cafe-snack stall for chapssal kwabaegi and coffee while you walk the aisles.",
    },
    "dosan-jeongyuk": {
        "ko": "청담·압구정의 한우·돼지 정육 고깃집입니다. 부위 모듬을 구워 먹는 고급 고기집으로 알려져 있습니다.",
        "en": "A Cheongdam butcher-style BBQ for hanwoo and pork platters — a well-known upscale grill.",
    },
    "yuksanjang-hongdae": {
        "ko": "홍대의 우대 장갈비 고기집입니다. 두툼한 갈비를 구워 먹는 현지 인기 가게입니다.",
        "en": "Hongdae Korean BBQ known for thick jang-galbi (seasoned short ribs).",
    },
    "wangbijip": {
        "ko": "명동의 한우 불고기·살치살 노포입니다. 외국인 관광객에게도 익숙한 명동 고기집입니다.",
        "en": "A Myeongdong hanwoo institution for bulgogi and premium cuts — a familiar stop for visitors.",
    },
    "gojip": {
        "ko": "서면의 고기집으로, 테이블에서 짓는 솥밥을 함께 냅니다. 현지인이 자주 찾는 구이집입니다.",
        "en": "Seomyeon BBQ that serves complimentary pot rice cooked at the table — a local favorite.",
    },
    "seumugogae-haeundae": {
        "ko": "해운대의 한우 뭉티기·구이집입니다. 당일 도축 한우를 회로 먼저 맛보고 구워 먹습니다.",
        "en": "Haeundae hanwoo house for mungtigi (seasoned raw beef) and grilled cuts from the day’s beef.",
    },
    "hongojip-myeongdong": {
        "ko": "명동의 삼겹·목살 구이집입니다. 관광 동선에서 한식 BBQ를 먹기 좋은 위치입니다.",
        "en": "Myeongdong pork BBQ for samgyeopsal and moksal — an easy Korean grill on a sightseeing route.",
    },
    "cheongwadae-sogeumgui": {
        "ko": "선릉의 소금구이 고기집입니다. 돼지고기를 소금으로 구워 담백하게 먹습니다.",
        "en": "Seolleung salt-grilled pork BBQ — a lighter Korean grill without heavy marinade.",
    },
    "jikhwajangin-yongsan": {
        "ko": "용산의 고기집으로, 직원이 그릴에서 고기를 구워 줍니다. 그릴링 서비스가 있어 편하게 먹기 좋습니다.",
        "en": "Yongsan Korean BBQ with a grilling service — staff cook the meat at the table.",
    },
    "manmanjeong-seomyeon": {
        "ko": "서면시장 안의 수제 만두·찐빵 가게입니다. 왕만두를 포장하거나 서서 먹기 좋은 시장 간식입니다.",
        "en": "Handmade dumplings and steamed buns inside Seomyeon Market — easy to grab as a snack.",
    },
    "buan-yukbi": {
        "ko": "서초의 육회·닭도리탕 집입니다. 육회와 매콤한 닭볶음을 안주·식사로 함께 내기 좋습니다.",
        "en": "A Seocho spot for yukhoe and spicy dakdoritang — good as a meal or with drinks.",
    },
    "momstouch-seongsu": {
        "ko": "성수역의 맘스터치입니다. 싸이버거 등 한국식 치킨 버거를 빠르게 먹기 좋습니다.",
        "en": "Mom’s Touch at Seongsu Station — Korean fried-chicken burgers for a quick meal.",
    },
    "milbon-seongsu": {
        "ko": "성수의 칼국수·수육 한상 집입니다. 면과 수육을 함께 내는 든든한 한 끼입니다.",
        "en": "Seongsu kalguksu with a boiled-pork set — a filling noodle-and-meat meal.",
    },
    "darin-daebo-kalguksu": {
        "ko": "마곡의 칼국수집입니다. 장칼국수처럼 칼칼한 국물 면을 내는 곳으로 알려져 있습니다.",
        "en": "A Magok kalguksu shop known for spicy jang-kalguksu (soy-paste noodle soup).",
    },
    "gayang-kalguksu": {
        "ko": "여의도의 칼국수·버섯매운탕 집입니다. 면과 매운탕을 시켜 나눠 먹기 좋습니다.",
        "en": "Yeouido kalguksu and spicy mushroom stew — easy to share as a hearty meal.",
    },
    "namdareun-gamjatang": {
        "ko": "영등포의 감자탕 체인점입니다. 등뼈와 감자를 매콤하게 끓여 여럿이 먹기 좋습니다.",
        "en": "A Yeongdeungpo gamjatang chain — spicy pork-backbone stew made for sharing.",
    },
    "byeolyangjip": {
        "ko": "선릉·역삼의 곱창·양구이집입니다. 특양구이를 소주와 함께 내는 강남 안주 맛집입니다.",
        "en": "A Gangnam gopchang house between Seolleung and Yeoksam, known for grilled tripe.",
    },
    "nampo-seolleongtang": {
        "ko": "남포동의 설렁탕집입니다. 맑고 진한 소고기 국밥을 부산 도심에서 먹기 좋습니다.",
        "en": "Seolleongtang in Nampo-dong — a clear, rich beef-bone soup in central Busan.",
    },
    "dongdong-gomguk": {
        "ko": "홍대의 곰국·국밥집입니다. 진한 국물에 밥을 말아 먹는 가벼운 한식 한 끼입니다.",
        "en": "A Hongdae gomguk shop — milky beef broth with rice, a simple Korean bowl.",
    },
    "hapcheon-illyu-dwaeji-gukbap": {
        "ko": "사상의 돼지국밥집입니다. 합천식 고기국밥을 진하게 내는 부산 현지 맛집입니다.",
        "en": "Pork-rice soup in Sasang in the Hapcheon style — a local Busan gukbap stop.",
    },
    "gangnam-makguksu-bossam": {
        "ko": "강남역 인근 막국수·보쌈집입니다. 들기름 막국수와 보쌈을 함께 시키기 좋습니다.",
        "en": "Makguksu and bossam near Gangnam Station — perilla-oil noodles with boiled pork.",
    },
    "yongho-nakji": {
        "ko": "명동의 낙지·낙곱새집입니다. 매콤한 낙지볶음을 밥과 함께 내기 좋은 관광지 맛집입니다.",
        "en": "Nakji and nakgopsae in Myeongdong — spicy stir-fried octopus that pairs well with rice.",
    },
    "obongjip": {
        "ko": "해운대의 낙지 요리집입니다. 해변 나들이 후 매콤한 낙지를 먹기 좋은 위치입니다.",
        "en": "A Haeundae nakji restaurant — spicy octopus after a beach walk.",
    },
    "inakesanda": {
        "ko": "광안리의 부산식 낙곱새집입니다. 낙지·곱창·새우를 매콤하게 볶아 내는 현지 인기 가게입니다.",
        "en": "Gwangalli nakgopsae in Busan style — octopus, gopchang, and shrimp in a spicy stir-fry.",
    },
    "sura-gejang": {
        "ko": "명동의 간장게장 정식집입니다. 게장과 밥·반찬이 한 상에 나와 관광객이 먹기 좋습니다.",
        "en": "Ganjang-gejang set meals in Myeongdong — soy-marinated crab with rice, easy for visitors.",
    },
    "damijuk": {
        "ko": "명동의 죽집입니다. 궁중전복죽처럼 속을 편하게 하는 죽을 관광 일정 사이에 먹기 좋습니다.",
        "en": "A Myeongdong juk shop for abalone porridge and other gentle rice porridges.",
    },
    "jinurin-haejang": {
        "ko": "해운대의 갈비탕·해장국집입니다. 맑은 갈비탕으로 든든한 한 끼·해장을 해결하기 좋습니다.",
        "en": "Haeundae galbitang and hangover soup — a clear short-rib broth for a filling meal.",
    },
    "silbiok": {
        "ko": "성수의 소고기 전골·해장 한식집입니다. 미역전골처럼 국물 요리를 점심·저녁으로 냅니다.",
        "en": "A Seongsu Korean soup house for beef hotpot and hangover broths.",
    },
    "damsot": {
        "ko": "왕십리의 솥밥 전문점입니다. 가지솥밥처럼 돌솥에 지은 밥을 누룽지까지 즐깁니다.",
        "en": "A Wangsimni sotbap restaurant — pot rice (including eggplant rice) with nurungji at the bottom.",
    },
    "daraksot-pangyo": {
        "ko": "판교의 솥밥집입니다. 소갈비솥밥처럼 고기가 올라간 돌솥밥을 내는 캐주얼 한식입니다.",
        "en": "Pangyo sotbap — stone-pot rice topped with galbi, a casual one-bowl Korean meal.",
    },
    "jinjujip": {
        "ko": "여의도의 콩국수집입니다. 여름철 냉콩국수로 유명한 오래된 면집입니다.",
        "en": "A Yeouido kongguksu shop famous for cold soybean-noodle soup in summer.",
    },
    "piyang-kong-halmeoni": {
        "ko": "강남의 콩비지·콩국수 집입니다. 고소한 콩 요리를 밥·면과 함께 내는 한식집입니다.",
        "en": "A Gangnam house for kongbiji stew and kongguksu — savory soybean dishes.",
    },
    "tamna-eomarket": {
        "ko": "영등포의 수산시장형 횟집입니다. 회·해물을 고르거나 세트 요리로 먹기 좋습니다.",
        "en": "A Yeongdeungpo fish-market style hoe restaurant — pick sashimi and seafood or order a set.",
    },
    "mongttang-jokbal": {
        "ko": "천호의 족발집입니다. 부드러운 족발을 보쌈김치와 함께 내는 동네 노포입니다.",
        "en": "A Cheonho jokbal shop — tender pig’s trotters with bossam kimchi.",
    },
    "haemok-nonhyeon": {
        "ko": "논현의 장어·히츠마부시 집입니다. 장어구이를 밥과 함께 보양식으로 먹기 좋습니다.",
        "en": "Nonhyeon eel restaurant for grilled eel and hitsumabushi-style rice bowls.",
    },
    "jogaedaegyo-seomyeon": {
        "ko": "전포의 조개구이·찜 집입니다. 맛조개 세트를 구이와 찜으로 나눠 먹기 좋습니다.",
        "en": "Jeonpo grilled-and-steamed clam house — a sharing set of jogae-gui.",
    },
    "sanchon": {
        "ko": "인사동의 사찰 한식집입니다. 산채 비빔밥·정식을 채식에 가깝게 내는 오래된 가게입니다.",
        "en": "An Insadong temple-food restaurant for mountain-vegetable bibimbap and set menus.",
    },
    "bukchon-makguksu": {
        "ko": "삼청동의 막국수 제면소입니다. 직접 뽑은 메밀면으로 들기름 막국수를 냅니다.",
        "en": "A Samcheong-dong makguksu shop that mills its own buckwheat noodles, including perilla-oil makguksu.",
    },
    "jeokdang": {
        "ko": "을지로입구의 팥빙수 카페입니다. 역과 붙어 있어 도심에서 디저트를 먹기 좋습니다.",
        "en": "A patbingsu cafe by Euljiro 1-ga Station — an easy downtown dessert stop.",
    },
    "arari-bukchon": {
        "ko": "북촌의 아이스크림·디저트 카페입니다. 한옥 골목 산책 중 말차·과일 아이스크림을 먹기 좋습니다.",
        "en": "A Bukchon dessert cafe for matcha and fruit ice cream while walking the hanok streets.",
    },
    "starbucks-daegu-jongno-gotaek": {
        "ko": "대구 근대골목의 고택형 스타벅스입니다. 한옥 분위기에서 커피를 마시며 골목을 둘러보기 좋습니다.",
        "en": "A Starbucks in a traditional house on Daegu’s historic Jongno alley — coffee inside a hanok-style building.",
    },
    "bokhodu-gyeongbokgung": {
        "ko": "경복궁역의 호두과자·간식 가게입니다. 산책·선물용 호두과자를 사기 좋습니다.",
        "en": "A hodugwaja (walnut pastry) shop by Gyeongbokgung Station — a snack or small gift.",
    },
    "oile-bakery": {
        "ko": "여의도의 빵집입니다. 밤식빵처럼 식사·간식 빵을 사는 캐주얼 베이커리입니다.",
        "en": "A Yeouido bakery known for chestnut milk bread and other everyday loaves.",
    },
    "london-bagel-museum-dosan": {
        "ko": "도산공원의 베이글 카페입니다. 플레인 베이글과 커피로 브런치를 먹기 좋은 인기 가게입니다.",
        "en": "A Dosan Park bagel cafe — plain bagels and coffee, a popular brunch stop.",
    },
    "butterscotch-euljiro": {
        "ko": "을지로의 버터스카치 커피 카페입니다. 달콤한 시그니처 커피를 골목에서 마시기 좋습니다.",
        "en": "An Euljiro cafe known for butterscotch coffee — a sweet signature drink in the alleys.",
    },
    "donar": {
        "ko": "이태원의 베이커리 카페입니다. 빵과 가벼운 식사를 가구거리 근처에서 먹기 좋습니다.",
        "en": "An Itaewon bakery-cafe near Furniture Street for bread and a light sit-down.",
    },
    "haneip-bagel-seongsu": {
        "ko": "서울숲 근처 베이글 카페입니다. 베이글과 소프트 아이스크림을 산책 전후에 먹기 좋습니다.",
        "en": "A bagel cafe near Seoul Forest — bagels and soft-serve before or after a park walk.",
    },
    "jjoljjol-hotteok": {
        "ko": "청주 성안길의 호떡·떡볶이 가게입니다. 즉석 호떡을 시장 구경 중에 사 먹기 좋습니다.",
        "en": "A Cheongju street stall for hotteok and tteokbokki — a market snack stop.",
    },
    "obok-tteokjip": {
        "ko": "성수동 뚝도시장의 떡집입니다. 인절미·가래떡 등 전통 떡을 간식·선물로 사가기 좋습니다.",
        "en": "A tteok shop in Seongsu’s Ttukdo Market for injeolmi and other traditional rice cakes.",
    },
    "idorim-cafe": {
        "ko": "서촌의 빙수 카페입니다. 과일 빙수를 경복궁·통인시장 동선에서 디저트로 먹기 좋습니다.",
        "en": "A Seochon bingsu cafe — fruit shaved ice as a dessert stop near Gyeongbokgung and Tongin Market.",
    },
}


def fit_cover(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tw, th = COVER_SIZE
    target_ratio = tw / th
    with Image.open(src) as im:
        im = im.convert("RGB")
        w, h = im.size
        ratio = w / h
        if ratio > target_ratio:
            nw = int(h * target_ratio)
            left = (w - nw) // 2
            im = im.crop((left, 0, left + nw, h))
        else:
            nh = int(w / target_ratio)
            top = (h - nh) // 2
            im = im.crop((0, top, w, top + nh))
        im = im.resize(COVER_SIZE, Image.Resampling.LANCZOS)
        im.save(dest, "JPEG", quality=88, optimize=True)
    print(f"cover {dest.relative_to(ROOT)}", flush=True)


def apply_about(foods: dict) -> None:
    for slug, texts in ABOUT.items():
        ko = texts["ko"]
        en = texts["en"]
        for lang in LANGS:
            restaurants = foods[lang].setdefault("restaurants", {})
            entry = restaurants.get(slug)
            if not isinstance(entry, dict):
                print(f"missing {lang} {slug}", flush=True)
                continue
            entry["about"] = ko if lang == "ko" else en
        print(f"about {slug}", flush=True)


def main() -> int:
    for slug, (kind, fname) in COVERS.items():
        src = ASSETS / fname
        dest = ROOT / "pages" / "foods" / kind / slug / "media" / "cover.jpg"
        if not src.is_file():
            print(f"MISSING asset {src}", flush=True)
            continue
        fit_cover(src, dest)

    foods = {}
    for lang in LANGS:
        path = FOODS_DIR / f"{lang}.json"
        foods[lang] = json.loads(path.read_text(encoding="utf-8"))
    apply_about(foods)
    for lang in LANGS:
        path = FOODS_DIR / f"{lang}.json"
        _write_text_retry(
            path,
            json.dumps(foods[lang], ensure_ascii=False, indent=2) + "\n",
        )
        print(f"saved {lang}", flush=True)

    import subprocess

    subprocess.check_call(
        [sys.executable, str(ROOT / "i18n" / "build-bundle.py")],
        cwd=str(ROOT),
    )
    try:
        print(rebuild_food_recommend_catalog(), flush=True)
    except OSError as exc:
        print("catalog deferred", exc, flush=True)
    try:
        print(bump_asset_version(), flush=True)
    except OSError as exc:
        print("bump deferred", exc, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
