# -*- coding: utf-8 -*-
"""Download Wikimedia Commons photos for new regional curated courses."""
from __future__ import annotations

import json
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COURSES = ROOT / "Images" / "places" / "_courses"
PLACES = ROOT / "Images" / "places"
UA = "KoreaTravelGuidebook/1.0 (regional course covers; educational; rate-limited)"
SLEEP = 1.5

# dest relative to Images/places → preferred Commons File titles
FILES: dict[str, list[str]] = {
    "_courses/gwongeumseong.jpg": [
        "Korea-Sokcho-Seoraksan-Gwongeumsung-01.jpg",
        "Gwongeumseong Fortress.jpg",
        "Seoraksan Gwongeumseong.jpg",
        "권금성.jpg",
    ],
    "_courses/oeongchi-hyanggiro.jpg": [
        "Oeongchi Beach.jpg",
        "Oeongchi Coastal Trail.jpg",
        "외옹치 바다향기로.jpg",
        "Sokcho Oeongchi.jpg",
    ],
    "_courses/daepohang.jpg": [
        "Daepo Port Sokcho.jpg",
        "Daepohang.jpg",
        "대포항.jpg",
        "Sokcho harbor.jpg",
    ],
    "_courses/samaksan-cable.jpg": [
        "Samaksan Lake Cable Car.jpg",
        "Chuncheon Samaksan Cable Car.jpg",
        "삼악산 호수케이블카.jpg",
        "Samaksan.jpg",
    ],
    "_courses/uiamho.jpg": [
        "Uiam Lake.jpg",
        "Uiamho Chuncheon.jpg",
        "의암호.jpg",
        "Chuncheon lake.jpg",
    ],
    "_courses/daegwallyeong-sheep.jpg": [
        "Daegwallyeong Sheep Farm.jpg",
        "대관령 양떼목장.jpg",
        "Pyeongchang sheep farm.jpg",
        "Daegwallyeong.jpg",
    ],
    "_courses/daegwallyeong.jpg": [
        "Daegwallyeong.jpg",
        "Daegwallyeong Ranch.jpg",
        "대관령.jpg",
    ],
    "_courses/woljeongsa.jpg": [
        "Woljeongsa.jpg",
        "Woljeongsa Temple.jpg",
        "월정사.jpg",
        "Odaesan Woljeongsa.jpg",
    ],
    "_courses/woljeongsa-fir.jpg": [
        "Woljeongsa fir tree forest.jpg",
        "월정사 전나무숲.jpg",
        "Woljeongsa forest path.jpg",
    ],
    "_courses/chuam-candle.jpg": [
        "Chuam Candle Rock.jpg",
        "Chotdaebawi.jpg",
        "추암 촛대바위.jpg",
        "Chuam Beach rock.jpg",
    ],
    "_courses/chuam-beach.jpg": [
        "Chuam Beach.jpg",
        "추암해변.jpg",
        "Donghae Chuam.jpg",
    ],
    "_courses/dojjaebigol.jpg": [
        "Dojjaebigol Sky Valley.jpg",
        "도째비골 스카이밸리.jpg",
        "Dojjaebigol.jpg",
    ],
    "_courses/mukho-nongol.jpg": [
        "Mukho Port.jpg",
        "Nongol Damgil.jpg",
        "묵호항.jpg",
        "논골담길.jpg",
        "Donghae Mukho.jpg",
    ],
    "_courses/hantan-columnar.jpg": [
        "Hantan River columnar joints.jpg",
        "한탄강 주상절리.jpg",
        "Cheorwon Hantangang.jpg",
        "Hantangang.jpg",
    ],
    "_courses/goseokjeong.jpg": [
        "Goseokjeong.jpg",
        "고석정.jpg",
        "Cheorwon Goseokjeong.jpg",
    ],
    "_courses/cheorwon-dmz.jpg": [
        "Cheorwon DMZ.jpg",
        "철원 평화전망대.jpg",
        "Cheorwon Peace Observatory.jpg",
        "Iron Triangle Cheorwon.jpg",
    ],
    "_courses/muryeong-tombs.jpg": [
        "Songsan-ri Tombs.jpg",
        "Tomb of King Muryeong.jpg",
        "무령왕릉.jpg",
        "Gongju royal tombs.jpg",
    ],
    "_courses/gongju-museum.jpg": [
        "Gongju National Museum.jpg",
        "국립공주박물관.jpg",
        "Gongju Museum.jpg",
    ],
    "_courses/jemincheon.jpg": [
        "Jemincheon Gongju.jpg",
        "제민천.jpg",
        "Gongju old town.jpg",
    ],
    "_courses/gungnamji.jpg": [
        "Gungnamji.jpg",
        "Gungnamji Pond.jpg",
        "궁남지.jpg",
        "Buyeo Gungnamji.jpg",
    ],
    "_courses/jeongnimsaji.jpg": [
        "Jeongnimsa Temple Site.jpg",
        "정림사지.jpg",
        "Jeongnimsaji pagoda.jpg",
        "Buyeo Jeongnimsa.jpg",
    ],
    "_courses/buyeo-downtown.jpg": [
        "Buyeo downtown.jpg",
        "부여 시내.jpg",
        "Buyeo town.jpg",
    ],
    "_courses/dodamsambong.jpg": [
        "Dodamsambong.jpg",
        "도담삼봉.jpg",
        "Danyang Dodamsambong.jpg",
    ],
    "_courses/mancheonha.jpg": [
        "Mancheonha Skywalk.jpg",
        "만천하스카이워크.jpg",
        "Danyang skywalk.jpg",
    ],
    "_courses/danyang-jando.jpg": [
        "Danyanggang Jando.jpg",
        "단양강 잔도.jpg",
        "Danyang cliff walk.jpg",
    ],
    "_courses/danyang-cafe-san.jpg": [
        "Danyang paragliding.jpg",
        "카페산 단양.jpg",
        "Danyang mountain cafe.jpg",
        "Danyang view.jpg",
    ],
    "_courses/danyang-market.jpg": [
        "Danyang Gyeong market.jpg",
        "단양구경시장.jpg",
        "Danyang market.jpg",
    ],
    "_courses/daecheon-skybike.jpg": [
        "Daecheon Sky Bike.jpg",
        "대천 스카이바이크.jpg",
        "Boryeong skybike.jpg",
    ],
    "_courses/daecheon-sunset.jpg": [
        "Daecheon Beach sunset.jpg",
        "대천해수욕장 일몰.jpg",
        "Boryeong sunset.jpg",
    ],
    "_courses/anmyeondo.jpg": [
        "Anmyeondo.jpg",
        "안면도.jpg",
        "Anmyeon Island.jpg",
        "Taean Anmyeondo.jpg",
    ],
    "_courses/kkoji-beach.jpg": [
        "Kkotji Beach.jpg",
        "꽃지해수욕장.jpg",
        "Anmyeondo Kkotji.jpg",
        "Taean Kkotji.jpg",
    ],
    "_courses/kkoji-sunset.jpg": [
        "Kkotji Beach sunset.jpg",
        "꽃지 일몰.jpg",
        "Anmyeondo sunset.jpg",
    ],
    "_courses/daejeon-science.jpg": [
        "National Science Museum Daejeon.jpg",
        "국립중앙과학관.jpg",
        "Daejeon science museum.jpg",
    ],
    "_courses/hanbit-tower.jpg": [
        "Hanbit Tower.jpg",
        "한빛탑.jpg",
        "Expo Park Daejeon.jpg",
        "Daejeon Expo Tower.jpg",
    ],
    "_courses/daejeon-downtown.jpg": [
        "Daejeon Jungangno.jpg",
        "대전 원도심.jpg",
        "Daejeon downtown.jpg",
        "Eunhaeng-dong Daejeon.jpg",
    ],
    "_courses/gyeonggijeon.jpg": [
        "Gyeonggijeon.jpg",
        "경기전.jpg",
        "Jeonju Gyeonggijeon.jpg",
    ],
    "_courses/jeondong-cathedral.jpg": [
        "Jeondong Cathedral.jpg",
        "전동성당.jpg",
        "Jeonju cathedral.jpg",
    ],
    "_courses/yeosu-cable.jpg": [
        "Yeosu Cable Car.jpg",
        "여수 해상케이블카.jpg",
        "Yeosu Marine Cable Car.jpg",
    ],
    "_courses/isunsin-square.jpg": [
        "Yi Sun-sin Square Yeosu.jpg",
        "이순신광장.jpg",
        "Yeosu Yi Sun-sin Square.jpg",
    ],
    "_courses/yeosu-night.jpg": [
        "Yeosu night view.jpg",
        "여수 야경.jpg",
        "Yeosu harbor night.jpg",
    ],
    "_courses/suncheon-garden.jpg": [
        "Suncheon Bay National Garden.jpg",
        "순천만국가정원.jpg",
        "Suncheon Garden.jpg",
    ],
    "_courses/yongsan-observatory.jpg": [
        "Yongsan Observatory Suncheon.jpg",
        "용산전망대.jpg",
        "Suncheon Bay observatory.jpg",
    ],
    "_courses/suncheon-sunset.jpg": [
        "Suncheon Bay sunset.jpg",
        "순천만 일몰.jpg",
        "Suncheon wetland sunset.jpg",
    ],
    "_courses/juknokwon.jpg": [
        "Juknokwon.jpg",
        "죽녹원.jpg",
        "Damyang bamboo garden.jpg",
        "Juknokwon Damyang.jpg",
    ],
    "_courses/gwanbangjerim.jpg": [
        "Gwanbangjerim.jpg",
        "관방제림.jpg",
        "Damyang Gwanbangjerim.jpg",
    ],
    "_courses/metasequoia-damyang.jpg": [
        "Metasequoia Road Damyang.jpg",
        "담양 메타세쿼이아길.jpg",
        "Damyang metasequoia.jpg",
    ],
    "_courses/metaprovence.jpg": [
        "Metaprovence Damyang.jpg",
        "메타프로방스.jpg",
        "Damyang Provence.jpg",
    ],
    "_courses/yulpo-beach.jpg": [
        "Yulpo Beach.jpg",
        "율포해수욕장.jpg",
        "Boseong Yulpo.jpg",
    ],
    "_courses/yulpo-coast.jpg": [
        "Yulpo coast Boseong.jpg",
        "율포 해안.jpg",
        "Boseong coast.jpg",
    ],
    "_courses/mokpo-cable.jpg": [
        "Mokpo Marine Cable Car.jpg",
        "목포 해상케이블카.jpg",
        "Mokpo cable car.jpg",
    ],
    "_courses/yudalsan.jpg": [
        "Yudalsan.jpg",
        "유달산.jpg",
        "Mokpo Yudalsan.jpg",
    ],
    "_courses/gatbawi-mokpo.jpg": [
        "Gatbawi Mokpo.jpg",
        "목포 갓바위.jpg",
        "Mokpo Peace Plaza.jpg",
    ],
    "_courses/daereungwon.jpg": [
        "Daereungwon.jpg",
        "대릉원.jpg",
        "Cheonmachong.jpg",
        "Gyeongju tumuli.jpg",
    ],
    "_courses/cheomseongdae.jpg": [
        "Cheomseongdae.jpg",
        "첨성대.jpg",
        "Gyeongju Cheomseongdae.jpg",
    ],
    "_courses/woljeonggyo.jpg": [
        "Woljeonggyo.jpg",
        "월정교.jpg",
        "Gyeongju Woljeonggyo.jpg",
        "Gyochon Village.jpg",
    ],
    "_courses/buyongdae.jpg": [
        "Buyongdae.jpg",
        "부용대.jpg",
        "Hahoe Buyongdae.jpg",
        "Andong Buyongdae.jpg",
    ],
    "_courses/hahoe-mask.jpg": [
        "Hahoe mask dance.jpg",
        "하회탈.jpg",
        "Hahoe Mask Museum.jpg",
        "Andong Hahoe mask.jpg",
    ],
    "_courses/byeongsanseowon.jpg": [
        "Byeongsan Seowon.jpg",
        "병산서원.jpg",
        "Byeongsanseowon.jpg",
    ],
    "_courses/woryeonggyo.jpg": [
        "Woryeonggyo.jpg",
        "월영교.jpg",
        "Andong Woryeonggyo.jpg",
    ],
    "_courses/tongyeong-cable.jpg": [
        "Tongyeong Cable Car.jpg",
        "통영 케이블카.jpg",
        "Mireuksan cable car.jpg",
    ],
    "_courses/mireuksan.jpg": [
        "Mireuksan Tongyeong.jpg",
        "미륵산.jpg",
        "Tongyeong Mireuksan view.jpg",
    ],
    "_courses/dongpirang.jpg": [
        "Dongpirang Village.jpg",
        "동피랑 벽화마을.jpg",
        "Tongyeong Dongpirang.jpg",
    ],
    "_courses/gangguan.jpg": [
        "Gangguan Tongyeong.jpg",
        "강구안.jpg",
        "Tongyeong harbor.jpg",
    ],
    "_courses/yi-sun-sin-park.jpg": [
        "Yi Sun-sin Park Tongyeong.jpg",
        "이순신공원 통영.jpg",
        "Tongyeong Yi Sun-sin Park.jpg",
    ],
    "_courses/geoje-pier.jpg": [
        "Geoje ferry terminal.jpg",
        "거제 외도 선착장.jpg",
        "Oedo ferry Geoje.jpg",
    ],
    "_courses/haegeumgang.jpg": [
        "Haegeumgang.jpg",
        "해금강.jpg",
        "Geoje Haegeumgang.jpg",
    ],
    "_courses/oeodo-botania.jpg": [
        "Oedo Botania.jpg",
        "외도 보타니아.jpg",
        "Oeodo Geoje.jpg",
        "Oedo Island.jpg",
    ],
    "_courses/baramui-eondeok.jpg": [
        "Windy Hill Geoje.jpg",
        "바람의 언덕.jpg",
        "Baramui Eondeok.jpg",
        "Geoje Windy Hill.jpg",
    ],
    "_courses/sinseondae.jpg": [
        "Sinseondae Geoje.jpg",
        "신선대 거제.jpg",
        "Geoje Sinseondae.jpg",
    ],
    "_courses/spacewalk.jpg": [
        "Space Walk Pohang.jpg",
        "스페이스워크.jpg",
        "Pohang Space Walk.jpg",
        "Hwanho Park Space Walk.jpg",
    ],
    "_courses/yeongildae-night.jpg": [
        "Yeongildae night.jpg",
        "영일대 야경.jpg",
        "Pohang Yeongildae night.jpg",
    ],
    "_courses/homigot.jpg": [
        "Homigot.jpg",
        "호미곶.jpg",
        "Homigot Sunrise Square.jpg",
        "Pohang Homigot.jpg",
    ],
    "_courses/guryongpo-houses.jpg": [
        "Guryongpo Japanese houses.jpg",
        "구룡포 일본인가옥거리.jpg",
        "Guryongpo.jpg",
    ],
    "_courses/guryongpo-port.jpg": [
        "Guryongpo Port.jpg",
        "구룡포항.jpg",
        "Pohang Guryongpo.jpg",
    ],
    "_courses/daegu-modern.jpg": [
        "Daegu Modern Culture Alley.jpg",
        "대구 근대문화골목.jpg",
        "Daegu Hyanggyo street.jpg",
        "Daegu old town.jpg",
    ],
    "_courses/apsan.jpg": [
        "Apsan Observatory.jpg",
        "앞산 전망대.jpg",
        "Daegu Apsan.jpg",
    ],
    "_courses/apsan-night.jpg": [
        "Apsan night view Daegu.jpg",
        "앞산 야경.jpg",
        "Daegu night view.jpg",
    ],
    "_courses/taehwa-garden.jpg": [
        "Taehwa River National Garden.jpg",
        "태화강 국가정원.jpg",
        "Taehwagang Garden.jpg",
        "Ulsan Taehwa.jpg",
    ],
    "_courses/ulsan-coast.jpg": [
        "Ilsan Beach Ulsan coast.jpg",
        "울산 해안.jpg",
        "Ulsan coastline.jpg",
    ],
    "_courses/tripitaka.jpg": [
        "Tripitaka Koreana.jpg",
        "팔만대장경.jpg",
        "Haeinsa Tripitaka.jpg",
        "Janggyeong Panjeon.jpg",
    ],
    "_courses/dongbaekseom.jpg": [
        "Dongbaekseom.jpg",
        "동백섬.jpg",
        "The Bay 101.jpg",
        "Haeundae Dongbaek Island.jpg",
    ],
    "_courses/daritdol.jpg": [
        "Daritdol Observatory.jpg",
        "청사포 다릿돌전망대.jpg",
        "Cheongsapo observatory.jpg",
    ],
    "_courses/gukje-market.jpg": [
        "Gukje Market.jpg",
        "부산 국제시장.jpg",
        "Busan International Market.jpg",
    ],
    "_courses/yongdusan.jpg": [
        "Yongdusan Park.jpg",
        "용두산공원.jpg",
        "Busan Tower.jpg",
        "Yongdusan Busan Tower.jpg",
    ],
    "_courses/songdo-cable.jpg": [
        "Songdo Marine Cable Car Busan.jpg",
        "부산 송도 해상케이블카.jpg",
        "Busan Songdo cable car.jpg",
    ],
    "_courses/amnam-park.jpg": [
        "Amnam Park.jpg",
        "암남공원.jpg",
        "Busan Amnam Park.jpg",
    ],
    "_courses/huinnyeoul.jpg": [
        "Huinnyeoul Culture Village.jpg",
        "흰여울문화마을.jpg",
        "Yeongdo Huinnyeoul.jpg",
    ],
    "_courses/gijang-coast.jpg": [
        "Gijang coast.jpg",
        "기장 해안.jpg",
        "Gijang sea.jpg",
    ],
    "_courses/ananti-osiria.jpg": [
        "Ananti Cove.jpg",
        "오시리아.jpg",
        "Osiria Gijang.jpg",
        "Ananti Hilton Busan.jpg",
    ],
    "_courses/gijang-sunset.jpg": [
        "Gijang sunset.jpg",
        "기장 일몰.jpg",
        "Gijang beach sunset.jpg",
    ],
    "_courses/jeolyeong-trail.jpg": [
        "Jeolyeong Coastal Trail.jpg",
        "절영해안산책로.jpg",
        "Yeongdo coastal trail.jpg",
    ],
    "_courses/busan-port-night.jpg": [
        "Busan Port night.jpg",
        "부산항 야경.jpg",
        "Busan harbor night.jpg",
    ],
    "_courses/jeonpo-cafe.jpg": [
        "Jeonpo Cafe Street.jpg",
        "전포 카페거리.jpg",
        "Busan Jeonpo.jpg",
    ],
    "_courses/jeonpo-shops.jpg": [
        "Jeonpo shops Busan.jpg",
        "전포동.jpg",
        "Busan boutique street.jpg",
    ],
    "_courses/seomyeon-night.jpg": [
        "Seomyeon night.jpg",
        "서면 야경.jpg",
        "Busan Seomyeon night.jpg",
    ],
    "_courses/aquaplanet-jeju.jpg": [
        "Aqua Planet Jeju.jpg",
        "아쿠아플라넷 제주.jpg",
        "Seopjikoji aquarium.jpg",
    ],
    "_courses/gwangchigi.jpg": [
        "Gwangchigi Beach.jpg",
        "광치기해변.jpg",
        "Seongsan Gwangchigi.jpg",
    ],
    "_courses/seongsan-port.jpg": [
        "Seongsan Port.jpg",
        "성산항.jpg",
        "Seongsan ferry terminal.jpg",
        "Udo ferry Seongsan.jpg",
    ],
    "_courses/udo-coast.jpg": [
        "Udo coast.jpg",
        "우도 해안.jpg",
        "Udo Island coast Jeju.jpg",
    ],
    "_courses/geommeolle.jpg": [
        "Geommeolle Beach.jpg",
        "검멀레해변.jpg",
        "Udo Geommeolle.jpg",
        "Hagosudong Beach.jpg",
    ],
    "_courses/osulloc.jpg": [
        "O'sulloc Tea Museum.jpg",
        "오설록 티뮤지엄.jpg",
        "Osulloc Jeju.jpg",
        "O Sulloc.jpg",
    ],
    "_courses/west-jeju-sunset.jpg": [
        "Hyeopjae sunset.jpg",
        "협재 일몰.jpg",
        "Jeju west coast sunset.jpg",
    ],
    "_courses/aewol-coast.jpg": [
        "Aewol coastal road.jpg",
        "애월 해안도로.jpg",
        "Aewol Jeju.jpg",
    ],
    "_courses/handam.jpg": [
        "Handam Coastal Walk.jpg",
        "한담해안산책로.jpg",
        "Aewol Handam.jpg",
    ],
    "_courses/aewol-sunset.jpg": [
        "Aewol sunset.jpg",
        "애월 일몰.jpg",
        "Gwakji sunset.jpg",
    ],
    "_courses/seogwipo-downtown.jpg": [
        "Seogwipo downtown.jpg",
        "서귀포 시내.jpg",
        "Seogwipo city.jpg",
    ],
    "_courses/cheonjiyeon.jpg": [
        "Cheonjiyeon Falls.jpg",
        "천지연폭포.jpg",
        "Seogwipo Cheonjiyeon.jpg",
    ],
    "_courses/saeyeongyo.jpg": [
        "Saeyeongyo.jpg",
        "새연교.jpg",
        "Saeseom Seogwipo.jpg",
        "Seogwipo Saeyeon Bridge.jpg",
    ],
    "_courses/seogwipo-coast.jpg": [
        "Seogwipo coast.jpg",
        "서귀포 해안.jpg",
        "Seogwipo harbor.jpg",
    ],
    "_courses/yeomiji.jpg": [
        "Yeomiji Botanical Garden.jpg",
        "여미지식물원.jpg",
        "Jungmun Yeomiji.jpg",
    ],
    "_courses/jungmun-resort.jpg": [
        "Jungmun Resort.jpg",
        "중문관광단지.jpg",
        "Jungmun Tourist Complex.jpg",
    ],
    "_courses/hallasan-summit.jpg": [
        "Hallasan summit.jpg",
        "한라산 정상.jpg",
        "Baeknokdam.jpg",
        "Hallasan crater.jpg",
    ],
    "_courses/hallasan-trail.jpg": [
        "Hallasan trail.jpg",
        "한라산 등산로.jpg",
        "Seongpanak trail.jpg",
        "Hallasan hiking.jpg",
    ],
    "_courses/yongduam.jpg": [
        "Yongduam.jpg",
        "용두암.jpg",
        "Dragon Head Rock Jeju.jpg",
        "Jeju Yongduam.jpg",
    ],
    "_courses/yongyeon.jpg": [
        "Yongyeon Valley.jpg",
        "용연계곡.jpg",
        "Jeju Yongyeon.jpg",
    ],
    "_courses/tapdong.jpg": [
        "Tapdong Jeju.jpg",
        "탑동.jpg",
        "Jeju Tapdong promenade.jpg",
    ],
    "_courses/yongnuni-oreum.jpg": [
        "Yongnuni Oreum.jpg",
        "용눈이오름.jpg",
        "Jeju Yongnuni.jpg",
    ],
    "_courses/sehwa-beach.jpg": [
        "Sehwa Beach.jpg",
        "세화해변.jpg",
        "Jeju Sehwa.jpg",
    ],
    "_courses/sanbangsan.jpg": [
        "Sanbangsan.jpg",
        "산방산.jpg",
        "Jeju Sanbangsan.jpg",
    ],
    "_courses/songaksan.jpg": [
        "Songaksan.jpg",
        "송악산.jpg",
        "Jeju Songaksan.jpg",
    ],
    "_courses/sagye-coast.jpg": [
        "Sagye coast.jpg",
        "사계해안.jpg",
        "Jeju Sagye.jpg",
    ],
    "_courses/southwest-sunset.jpg": [
        "Sanbangsan sunset.jpg",
        "산방산 일몰.jpg",
        "Jeju southwest sunset.jpg",
        "Songaksan sunset.jpg",
    ],
}

FOOD: dict[str, list[str]] = {
    "food-ssambap-gangneung.jpg": ["Ssambap.jpg", "Korean lettuce wrap rice.jpg", "한식 쌈밥.jpg"],
    "food-cafe-anmok.jpg": ["Cafe latte.jpg", "Pour over coffee.jpg", "Korean cafe coffee.jpg"],
    "food-seafood-gangneung.jpg": ["Hoe (raw fish).jpg", "Korean seafood.jpg", "Grilled mackerel.jpg"],
    "food-dakgalbi-chuncheon.jpg": ["Dak-galbi.jpg", "Chuncheon dakgalbi.jpg", "Korean spicy chicken stir fry.jpg"],
    "food-baekban-pyeongchang.jpg": ["Baekban.jpg", "Korean set meal.jpg", "Hanjeongsik.jpg"],
    "food-salmon-yangyang.jpg": ["Grilled salmon.jpg", "Salmon sashimi.jpg", "Salmon dish.jpg"],
    "food-seafood-yangyang.jpg": ["Korean grilled shellfish.jpg", "Hoe.jpg", "Seafood barbecue.jpg"],
    "food-ojingeo-donghae.jpg": ["Ojingeo-gui.jpg", "Grilled squid Korea.jpg", "Korean squid.jpg"],
    "food-seafood-donghae.jpg": ["Korean seafood stew.jpg", "Maeuntang.jpg", "Hoe.jpg"],
    "food-makguksu-cheorwon.jpg": ["Makguksu.jpg", "Buckwheat noodles Korea.jpg", "막국수.jpg"],
    "food-baekban-gongju.jpg": ["Korean rice set.jpg", "Baekban.jpg", "Doenjang-jjigae.jpg"],
    "food-jokbal-gongju.jpg": ["Jokbal.jpg", "Korean jokbal.jpg", "족발.jpg"],
    "food-yeonipbap-buyeo.jpg": ["Lotus leaf rice.jpg", "Yeonipbap.jpg", "연잎밥.jpg"],
    "food-trout-danyang.jpg": ["Grilled trout.jpg", "산천어.jpg", "Korean grilled fish.jpg"],
    "food-jogae-daecheon.jpg": ["Grilled clams.jpg", "조개구이.jpg", "Korean shellfish barbecue.jpg"],
    "food-cafe-daecheon.jpg": ["Iced americano.jpg", "Cafe drink ocean view.jpg", "Latte art.jpg"],
    "food-seafood-daecheon.jpg": ["Korean seafood platter.jpg", "Ganjang-gejang.jpg", "Hoe.jpg"],
    "food-baekban-taean.jpg": ["Korean side dishes.jpg", "Baekban.jpg", "Rice and banchan.jpg"],
    "food-cafe-taean.jpg": ["Cafe latte beach.jpg", "Coffee cup.jpg", "Korean cafe interior drink.jpg"],
    "food-seafood-taean.jpg": ["Grilled shrimp.jpg", "Korean seafood.jpg", "Jogae-gui.jpg"],
    "food-kalguksu-daejeon.jpg": ["Kalguksu.jpg", "Korean knife-cut noodles.jpg", "칼국수.jpg"],
    "food-bread-sungsimdang.jpg": ["Korean cream bread.jpg", "Soboro-ppang.jpg", "Bakery bread.jpg", "Cream bun.jpg"],
    "food-samgyeopsal-daejeon.jpg": ["Samgyeopsal.jpg", "Korean pork belly BBQ.jpg", "삼겹살.jpg"],
    "food-bibimbap-jeonju.jpg": ["Jeonju bibimbap.jpg", "Bibimbap.jpg", "비빔밥.jpg"],
    "food-cafe-jeonju.jpg": ["Korean traditional tea.jpg", "Omija tea.jpg", "Cafe dessert.jpg"],
    "food-makgeolli-jeonju.jpg": ["Makgeolli.jpg", "Korean rice wine.jpg", "막걸리.jpg"],
    "food-seafood-yeosu.jpg": ["Yeosu gatkimchi.jpg", "Korean seafood rice.jpg", "Hoe-deopbap.jpg"],
    "food-baekban-suncheon.jpg": ["Korean lunch set.jpg", "Baekban.jpg", "Doenjang-jjigae 2.jpg"],
    "food-chicken-suncheon.jpg": ["Korean fried chicken.jpg", "Yangnyeom chicken.jpg", "치맥.jpg"],
    "food-tteokgalbi-damyang.jpg": ["Tteok-galbi.jpg", "떡갈비.jpg", "Damyang tteokgalbi.jpg"],
    "food-cafe-damyang.jpg": ["Korean cafe cake.jpg", "Ade drink.jpg", "Iced tea.jpg"],
    "food-dolsotbap-boseong.jpg": ["Dolsotbap.jpg", "Stone pot rice.jpg", "돌솥밥.jpg"],
    "food-cafe-boseong.jpg": ["Green tea latte.jpg", "Matcha dessert.jpg", "Nokcha.jpg"],
    "food-seafood-boseong.jpg": ["Korean grilled fish.jpg", "Hoe.jpg", "Seafood stew.jpg"],
    "food-gukbap-mokpo.jpg": ["Gukbap.jpg", "Korean rice soup.jpg", "국밥.jpg"],
    "food-seafood-mokpo.jpg": ["Hongeo.jpg", "Korean skate.jpg", "Mokpo seafood.jpg", "Hoe.jpg"],
    "food-ssambap-gyeongju.jpg": ["Ssambap.jpg", "Korean barbecue wraps.jpg", "Hwangnam bread.jpg"],
    "food-jjimdak-andong.jpg": ["Andong-jjimdak.jpg", "Jjimdak.jpg", "안동찜닭.jpg"],
    "food-gan-andong.jpg": ["Heotjesabap.jpg", "Andong salted mackerel.jpg", "간고등어.jpg"],
    "food-chungmu-gimbap.jpg": ["Chungmu-gimbap.jpg", "충무김밥.jpg", "Tongyeong gimbap.jpg"],
    "food-seafood-tongyeong.jpg": ["Tongyeong seafood.jpg", "Korean oyster.jpg", "Gul-gui.jpg"],
    "food-seafood-geoje.jpg": ["Korean sashimi.jpg", "Hoe.jpg", "Grilled fish Korea.jpg"],
    "food-samgyeopsal-geoje.jpg": ["Samgyeopsal grill.jpg", "Korean BBQ pork.jpg", "삼겹살 구이.jpg"],
    "food-mulhoe-pohang.jpg": ["Mulhoe.jpg", "물회.jpg", "Pohang mulhoe.jpg"],
    "food-cafe-pohang.jpg": ["Cafe americano.jpg", "Ocean view coffee.jpg", "Latte.jpg"],
    "food-gwamegi-guryongpo.jpg": ["Gwamegi.jpg", "과메기.jpg", "Half-dried herring.jpg"],
    "food-cafe-guryongpo.jpg": ["Iced coffee.jpg", "Cafe dessert.jpg", "Coffee beans cup.jpg"],
    "food-makchang-daegu.jpg": ["Makchang.jpg", "막창.jpg", "Korean grilled intestines.jpg"],
    "food-eonyang-ulsan.jpg": ["Eonyang bulgogi.jpg", "Bulgogi.jpg", "Korean beef barbecue.jpg"],
    "food-seafood-ulsan.jpg": ["Korean seafood barbecue.jpg", "Hoe.jpg", "Grilled shellfish.jpg"],
    "food-sanchae-hapcheon.jpg": ["Sanchae-bibimbap.jpg", "Temple food Korea.jpg", "산채비빔밥.jpg"],
    "food-cafe-hapcheon.jpg": ["Korean tea.jpg", "Green tea.jpg", "Cafe drink.jpg"],
    "food-milmyeon-haeundae.jpg": ["Milmyeon.jpg", "밀면.jpg", "Busan milmyeon.jpg"],
    "food-hoe-gwangalli.jpg": ["Korean hoe.jpg", "Sashimi Korea.jpg", "회 모듬.jpg"],
    "food-gukbap-jagalchi.jpg": ["Dwaeji-gukbap.jpg", "돼지국밥.jpg", "Busan pork soup.jpg"],
    "food-ssam-nampo.jpg": ["Bossam.jpg", "Korean ssam.jpg", "보쌈.jpg"],
    "food-seafood-songdo-busan.jpg": ["Korean grilled clams.jpg", "Jogae-gui.jpg", "Hoe.jpg"],
    "food-cafe-yeongdo.jpg": ["Cafe latte ocean.jpg", "Coffee cup seaview.jpg", "Iced latte.jpg"],
    "food-samgyeopsal-yeongdo.jpg": ["Samgyeopsal restaurant.jpg", "Korean pork BBQ.jpg", "삼겹살.jpg"],
    "food-seafood-gijang.jpg": ["Gijang seafood.jpg", "Korean crab.jpg", "Hoe-deopbap.jpg"],
    "food-cafe-gijang.jpg": ["Cafe drink.jpg", "Ade.jpg", "Coffee.jpg"],
    "food-hoe-gijang.jpg": ["Sashimi platter.jpg", "Korean raw fish.jpg", "모듬회.jpg"],
    "food-gukbap-yeongdo.jpg": ["Gukbap bowl.jpg", "Korean rice soup.jpg", "국밥.jpg"],
    "food-dwaeji-gukbap-seomyeon.jpg": ["Dwaeji-gukbap.jpg", "Busan dwaeji gukbap.jpg", "돼지국밥.jpg"],
    "food-chicken-seomyeon.jpg": ["Korean fried chicken beer.jpg", "Chimaek.jpg", "양념치킨.jpg"],
    "food-haemul-seongsan.jpg": ["Jeju seafood.jpg", "Haemul-jeongol.jpg", "Korean seafood rice.jpg"],
    "food-blackpork-seongsan.jpg": ["Jeju black pork.jpg", "Heukdwaeji.jpg", "제주 흑돼지.jpg"],
    "food-haemul-udo.jpg": ["Udo seafood.jpg", "Grilled fish.jpg", "Hoe.jpg"],
    "food-peanut-ice-udo.jpg": ["Peanut ice cream.jpg", "Udo peanut ice cream.jpg", "땅콩아이스크림.jpg"],
    "food-gogi-guksu-hallim.jpg": ["Gogi-guksu.jpg", "Jeju meat noodles.jpg", "고기국수.jpg"],
    "food-cafe-west-jeju.jpg": ["Green tea dessert.jpg", "Jeju hallabong ade.jpg", "Cafe drink.jpg"],
    "food-haemul-aewol.jpg": ["Korean seafood pasta.jpg", "Hoe.jpg", "Grilled fish.jpg"],
    "food-cafe-aewol.jpg": ["Aewol cafe drink.jpg", "Latte art.jpg", "Iced americano.jpg"],
    "food-blackpork-aewol.jpg": ["Korean black pork BBQ.jpg", "Samgyeopsal.jpg", "흑돼지.jpg"],
    "food-okdom-seogwipo.jpg": ["Okdom.jpg", "옥돔.jpg", "Jeju tiled-snapper.jpg", "Grilled fish Korea.jpg"],
    "food-blackpork-seogwipo.jpg": ["Jeju heukdwaeji.jpg", "Korean BBQ pork.jpg", "Black pork.jpg"],
    "food-haemul-jungmun.jpg": ["Seafood stew.jpg", "Korean haemul.jpg", "Hoe.jpg"],
    "food-cafe-jungmun.jpg": ["Cafe dessert.jpg", "Coffee.jpg", "Ade drink.jpg"],
    "food-blackpork-jungmun.jpg": ["Grilled pork belly.jpg", "Jeju black pork.jpg", "삼겹살.jpg"],
    "food-blackpork-hallasan.jpg": ["Jeju black pork restaurant.jpg", "Heukdwaeji gui.jpg", "흑돼지 구이.jpg"],
    "food-gogi-guksu-jejusi.jpg": ["Gogi-guksu Jeju.jpg", "Meat noodle soup.jpg", "고기국수.jpg"],
    "food-market-dongmun.jpg": ["Korean market food.jpg", "Hotteok.jpg", "Eomuk.jpg", "Bungeo-ppang.jpg"],
    "food-haemul-woljeong.jpg": ["Korean seafood.jpg", "Hoe.jpg", "Grilled mackerel.jpg"],
    "food-cafe-east-jeju.jpg": ["Cafe latte.jpg", "Jeju citrus ade.jpg", "Hallabong juice.jpg"],
    "food-haemul-sagye.jpg": ["Grilled seafood.jpg", "Korean fish.jpg", "Hoe.jpg"],
}

SEARCH = {
    "_courses/gwongeumseong.jpg": "Gwongeumseong Seoraksan",
    "_courses/oeongchi-hyanggiro.jpg": "Oeongchi Sokcho coast",
    "_courses/daepohang.jpg": "Daepohang Sokcho",
    "_courses/samaksan-cable.jpg": "Samaksan cable car Chuncheon",
    "_courses/uiamho.jpg": "Uiam Lake Chuncheon",
    "_courses/daegwallyeong-sheep.jpg": "Daegwallyeong Sheep Farm",
    "_courses/woljeongsa.jpg": "Woljeongsa Odaesan",
    "_courses/chuam-candle.jpg": "Chuam Candle Rock Donghae",
    "_courses/dojjaebigol.jpg": "Dojjaebigol Sky Valley",
    "_courses/mukho-nongol.jpg": "Mukho Nongol Damgil",
    "_courses/hantan-columnar.jpg": "Hantangang columnar Cheorwon",
    "_courses/goseokjeong.jpg": "Goseokjeong Cheorwon",
    "_courses/muryeong-tombs.jpg": "King Muryeong tomb Gongju",
    "_courses/gungnamji.jpg": "Gungnamji Buyeo",
    "_courses/jeongnimsaji.jpg": "Jeongnimsa Buyeo",
    "_courses/dodamsambong.jpg": "Dodamsambong Danyang",
    "_courses/mancheonha.jpg": "Mancheonha Skywalk",
    "_courses/hanbit-tower.jpg": "Hanbit Tower Daejeon",
    "_courses/gyeonggijeon.jpg": "Gyeonggijeon Jeonju",
    "_courses/jeondong-cathedral.jpg": "Jeondong Cathedral",
    "_courses/yeosu-cable.jpg": "Yeosu cable car",
    "_courses/suncheon-garden.jpg": "Suncheon Bay National Garden",
    "_courses/juknokwon.jpg": "Juknokwon Damyang",
    "_courses/metasequoia-damyang.jpg": "Damyang Metasequoia Road",
    "_courses/cheomseongdae.jpg": "Cheomseongdae Gyeongju",
    "_courses/daereungwon.jpg": "Daereungwon Gyeongju",
    "_courses/woljeonggyo.jpg": "Woljeonggyo Gyeongju",
    "_courses/buyongdae.jpg": "Buyongdae Hahoe",
    "_courses/byeongsanseowon.jpg": "Byeongsan Seowon",
    "_courses/woryeonggyo.jpg": "Woryeonggyo Andong",
    "_courses/tongyeong-cable.jpg": "Tongyeong cable car",
    "_courses/dongpirang.jpg": "Dongpirang Tongyeong",
    "_courses/oeodo-botania.jpg": "Oedo Botania Geoje",
    "_courses/baramui-eondeok.jpg": "Windy Hill Geoje",
    "_courses/homigot.jpg": "Homigot Pohang",
    "_courses/spacewalk.jpg": "Space Walk Pohang",
    "_courses/taehwa-garden.jpg": "Taehwa River National Garden",
    "_courses/dongbaekseom.jpg": "Dongbaekseom Haeundae",
    "_courses/yongdusan.jpg": "Yongdusan Busan Tower",
    "_courses/huinnyeoul.jpg": "Huinnyeoul Culture Village",
    "_courses/gukje-market.jpg": "Gukje Market Busan",
    "_courses/osulloc.jpg": "Osulloc Tea Museum Jeju",
    "_courses/cheonjiyeon.jpg": "Cheonjiyeon Falls Seogwipo",
    "_courses/yongduam.jpg": "Yongduam Jeju",
    "_courses/sanbangsan.jpg": "Sanbangsan Jeju",
    "_courses/songaksan.jpg": "Songaksan Jeju",
    "_courses/hallasan-summit.jpg": "Hallasan summit Baeknokdam",
    "_courses/yongnuni-oreum.jpg": "Yongnuni Oreum",
}

REJECT = (
    "portrait", "selfie", "logo", "map", "svg", "diagram", "flag", "stamp",
    "coin", "document", "manuscript", "cat", "dog",
)

CTX = None


def ssl_ctx() -> ssl.SSLContext:
    global CTX
    if CTX is None:
        try:
            import certifi
            CTX = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            CTX = ssl._create_unverified_context()
    return CTX


def http_get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx()) as r:
        return r.read()


def special_filepath(title: str, width: int = 1400) -> str:
    enc = urllib.parse.quote(title.replace(" ", "_"))
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{enc}?width={width}"


def commons_search(query: str, limit: int = 10) -> list[str]:
    api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srnamespace": "6",
            "srlimit": str(limit),
            "format": "json",
        }
    )
    try:
        data = json.loads(http_get(api).decode())
    except Exception as exc:
        print(f"  search err: {exc}", flush=True)
        return []
    out = []
    for item in data.get("query", {}).get("search", []):
        t = item.get("title", "")
        if t.startswith("File:"):
            out.append(t[5:])
    return out


def ok_title(title: str, allow_food: bool) -> bool:
    if not title:
        return False
    low = title.lower()
    if low.endswith((".pdf", ".svg", ".gif", ".tif", ".tiff", ".djvu", ".webm")):
        return False
    blocked = REJECT
    if not allow_food:
        blocked = REJECT + ("food", "dish", "meal", "cuisine")
    return not any(b in low for b in blocked)


def save_image(url: str, dest: Path) -> bool:
    try:
        data = http_get(url, timeout=90)
    except Exception as exc:
        print(f"  dl err: {exc}", flush=True)
        return False
    if len(data) < 12000:
        print(f"  too small ({len(data)})", flush=True)
        return False
    head = data[:32].lstrip()
    if head.startswith(b"<") or head.startswith(b"<!DO"):
        print("  rejected html", flush=True)
        return False
    if not (
        data[:3] == b"\xff\xd8\xff"
        or data[:8] == b"\x89PNG\r\n\x1a\n"
        or data[:4] == b"RIFF"
    ):
        print("  bad magic", flush=True)
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return True


def fetch_one(rel: str, titles: list[str], allow_food: bool = False) -> bool:
    dest = PLACES / rel
    if dest.exists() and dest.stat().st_size > 20000:
        print(f"= skip existing {rel} ({dest.stat().st_size})", flush=True)
        return True
    all_titles = list(titles)
    q = SEARCH.get(rel) or Path(rel).stem.replace("-", " ")
    for t in commons_search(q, limit=8):
        if t not in all_titles:
            all_titles.append(t)
    for title in all_titles:
        if not ok_title(title, allow_food=allow_food):
            continue
        url = special_filepath(title)
        print(f"  try {title}", flush=True)
        if save_image(url, dest):
            print(f"+ {rel} <- {title} ({dest.stat().st_size})", flush=True)
            return True
        time.sleep(0.8)
    print(f"! FAIL {rel}", flush=True)
    return False


def main() -> int:
    COURSES.mkdir(parents=True, exist_ok=True)
    ok = fail = 0
    jobs = [(rel, titles, False) for rel, titles in FILES.items()]
    jobs += [(rel, titles, True) for rel, titles in FOOD.items()]
    for rel, titles, food in jobs:
        print(f"\n## {rel}", flush=True)
        if fetch_one(rel, titles, allow_food=food):
            ok += 1
        else:
            fail += 1
        time.sleep(SLEEP)
    print(f"\ndone ok={ok} fail={fail}", flush=True)
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
