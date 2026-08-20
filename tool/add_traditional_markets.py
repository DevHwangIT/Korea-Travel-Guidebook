# -*- coding: utf-8 -*-
"""Add traditional market places (type: market) to coords + i18n."""
from __future__ import annotations

import shutil
import ssl
import sys
import urllib.request
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
COORDS = ROOT / "data" / "places" / "places-coords.js"
IMG = ROOT / "Images" / "places"
MARKER_SLUG = "gwangjang-market"

LANGS = ("ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru")

REGION_LABELS = {
    "seoul": {
        "ko": "서울",
        "en": "Seoul",
        "ja": "ソウル",
        "zh": "首尔",
        "zh-Hant": "首爾",
        "vi": "Seoul",
        "th": "โซล",
        "ru": "Сеул",
    },
    "busan": {
        "ko": "부산",
        "en": "Busan",
        "ja": "釜山",
        "zh": "釜山",
        "zh-Hant": "釜山",
        "vi": "Busan",
        "th": "ปูซาน",
        "ru": "Пусан",
    },
    "gyeonggi": {
        "ko": "경기",
        "en": "Gyeonggi",
        "ja": "京畿",
        "zh": "京畿",
        "zh-Hant": "京畿",
        "vi": "Gyeonggi",
        "th": "คยองกี",
        "ru": "Кёнги",
    },
    "incheon": {
        "ko": "인천",
        "en": "Incheon",
        "ja": "仁川",
        "zh": "仁川",
        "zh-Hant": "仁川",
        "vi": "Incheon",
        "th": "อินชอน",
        "ru": "Инчхон",
    },
    "gangwon": {
        "ko": "강원",
        "en": "Gangwon",
        "ja": "江原",
        "zh": "江原",
        "zh-Hant": "江原",
        "vi": "Gangwon",
        "th": "강원",
        "ru": "Канвон",
    },
    "jeolla": {
        "ko": "전라",
        "en": "Jeolla",
        "ja": "全羅",
        "zh": "全罗",
        "zh-Hant": "全羅",
        "vi": "Jeolla",
        "th": "ชอลลา",
        "ru": "Чolla",
    },
    "jeju": {
        "ko": "제주",
        "en": "Jeju",
        "ja": "済州",
        "zh": "济州",
        "zh-Hant": "濟州",
        "vi": "Jeju",
        "th": "เชจู",
        "ru": "Чеджу",
    },
    "gyeongju": {
        "ko": "경주",
        "en": "Gyeongju",
        "ja": "慶州",
        "zh": "庆州",
        "zh-Hant": "慶州",
        "vi": "Gyeongju",
        "th": "คยองจู",
        "ru": "Кёndzhu",
    },
    "gyeongsang": {
        "ko": "경상",
        "en": "Gyeongsang",
        "ja": "慶尚",
        "zh": "庆尚",
        "zh-Hant": "慶尚",
        "vi": "Gyeongsang",
        "th": "คยองซัง",
        "ru": "Кёнsan",
    },
    "": {
        "ko": "대구",
        "en": "Daegu",
        "ja": "大邱",
        "zh": "大邱",
        "zh-Hant": "大邱",
        "vi": "Daegu",
        "th": "แทกู",
        "ru": "Тэgu",
    },
    "chungcheong": {
        "ko": "충남",
        "en": "Chungcheong",
        "ja": "忠清",
        "zh": "忠清",
        "zh-Hant": "忠清",
        "vi": "Chungcheong",
        "th": "Chungcheong",
        "ru": "Чхунчхон",
    },
}

# slug, lat, lng, region, maps_q, wiki (optional)
MARKETS = [
    {
        "slug": "gwangjang-market",
        "lat": 37.5700,
        "lng": 126.9996,
        "region": "seoul",
        "maps_q": "광장시장",
        "wiki": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Gwangjang_Market_2014.jpg/1280px-Gwangjang_Market_2014.jpg",
        "ko": {
            "name": "광장시장",
            "desc": "110년 넘은 서울 대표 전통시장. 빈대떡·마약김밥·육회·호떡 등 길거리 먹거리가 유명합니다.",
            "how": "지하철 1·2·4호선 종로5가역 7·8번 출구에서 도보 3분.",
            "address": "서울 종로구 종로32길 88",
        },
        "en": {
            "name": "Gwangjang Market",
            "desc": "Seoul’s iconic covered market — bindaetteok, mayak gimbap, yukhoe, and hotteok stalls.",
            "how": "Lines 1/2/4 Jongno 5-ga Station, exits 7–8; 3 min walk.",
            "address": "88 Jongno 32-gil, Jongno-gu, Seoul",
        },
        "ja": ("広蔵市場", "ソウルを代表する伝統市場。ピンデトック、麻薬キンパプ、ユッケ、ホットクが人気。", "地下鉄1・2・4号線 鐘路5街駅7・8番出口から徒歩3分。"),
        "zh": ("广藏市场", "首尔代表性传统市场，以绿豆煎饼、毒品紫菜包饭、生拌牛肉、糖饼闻名。", "地铁1·2·4号线钟路5街站7·8号出口步行3分钟。"),
        "zh-Hant": ("廣藏市場", "首爾代表性傳統市場，綠豆煎餅、麻藥김밥、生拌牛肉、糖餅很有名。", "地鐵1·2·4號線鐘路5街站7·8號出口步行3分鐘。"),
    },
    {
        "slug": "namdaemun-market",
        "lat": 37.5596,
        "lng": 126.9773,
        "region": "seoul",
        "maps_q": "남대문시장",
        "wiki": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Namdaemun_Market_2013.jpg/1280px-Namdaemun_Market_2013.jpg",
        "ko": {
            "name": "남대문시장",
            "desc": "한국 최대 규모 전통시장. 의류·잡화·먹거리·기념품을 한곳에서 구경할 수 있습니다.",
            "how": "지하철 4호선 회현역 5번 출구 또는 2·4호선 시청역·을지로입구역 도보.",
            "address": "서울 중구 남대문시장길 21",
        },
        "en": {
            "name": "Namdaemun Market",
            "desc": "Korea’s largest traditional market — clothes, souvenirs, snacks, and wholesale stalls.",
            "how": "Line 4 Hoehyeon Station exit 5, or walk from City Hall / Euljiro 1-ga.",
            "address": "21 Namdaemunsijang 4-gil, Jung-gu, Seoul",
        },
        "ja": ("南大門市場", "韓国最大級の伝統市場。衣類・雑貨・食べ物・お土産が揃います。", "地下鉄4号線 会賢駅5番出口、または市庁・乙支路入口駅から徒歩。"),
        "zh": ("南大门市场", "韩国最大传统市场，服装、杂货、小吃、纪念品一应俱全。", "地铁4号线会贤站5号出口，或从市厅·乙支路入口站步行。"),
        "zh-Hant": ("南大門市場", "韓國最大傳統市場，服飾、雜貨、小吃、紀念品應有盡有。", "地鐵4號線會賢站5號出口，或從市廳·乙支路入口站步行。"),
    },
    {
        "slug": "tongin-market",
        "lat": 37.5790,
        "lng": 126.9705,
        "region": "seoul",
        "maps_q": "통인시장",
        "ko": {
            "name": "통인시장",
            "desc": "경복궁·서촌 옆 골목시장. 도시락 카페·전통 간식과 ‘통인시장 도시락’ 문화로 유명합니다.",
            "how": "지하철 3호선 경복궁역 2번 출구에서 서촌·자하문로 방향 도보 5분.",
            "address": "서울 종로구 자하문로15길 18",
        },
        "en": {
            "name": "Tongin Market",
            "desc": "Alley market near Gyeongbokgung — famous for lunch-café dosirak tokens and street snacks.",
            "how": "Line 3 Gyeongbokgung Station exit 2; walk toward Seochon / Jahamun-ro (~5 min).",
            "address": "18 Jahamun-ro 15-gil, Jongno-gu, Seoul",
        },
        "ja": ("通仁市場", "景福宮・西村近くの路地裏市場。お弁当トークン文化で有名。", "地下鉄3号線 景福宮駅2番出口から西村方面徒歩5分。"),
        "zh": ("通仁市场", "景福宫·西村旁的小巷市场，以便当代币和街头小吃闻名。", "地铁3号线景福宫站2号出口向西村方向步行5分钟。"),
        "zh-Hant": ("通仁市場", "景福宮·西村旁的小巷市場，以便當代幣和街頭小吃聞名。", "地鐵3號線景福宮站2號出口往西村方向步行5分鐘。"),
    },
    {
        "slug": "mangwon-market",
        "lat": 37.5560,
        "lng": 126.9055,
        "region": "seoul",
        "maps_q": "망원시장",
        "ko": {
            "name": "망원시장",
            "desc": "홍대·연남동 인근 로컬 시장. 떡볶이·튀김·닭강정 등 저렴한 먹거리와 생활용품이 많습니다.",
            "how": "지하철 6호선 망원역 2번 출구에서 도보 3분.",
            "address": "서울 마포구 포은로8길 39",
        },
        "en": {
            "name": "Mangwon Market",
            "desc": "Local market near Hongdae — cheap tteokbokki, fried snacks, and everyday goods.",
            "how": "Line 6 Mangwon Station exit 2; 3 min walk.",
            "address": "39 Poeun-ro 8-gil, Mapo-gu, Seoul",
        },
        "ja": ("望遠市場", "弘大・延南洞近くのローカル市場。トッポッキや揚げ物が人気。", "地下鉄6号線 望遠駅2番出口から徒歩3分。"),
        "zh": ("望远市场", "弘大·延南洞附近的本地市场，炒年糕、炸物、炸鸡便宜好吃。", "地铁6号线望远站2号出口步行3分钟。"),
        "zh-Hant": ("望遠市場", "弘大·延南洞附近的本地市場，炒年糕、炸物便宜好吃。", "地鐵6號線望遠站2號出口步行3分鐘。"),
    },
    {
        "slug": "dongdaemun-market",
        "lat": 37.5704,
        "lng": 127.0095,
        "region": "seoul",
        "maps_q": "동대문시장",
        "ko": {
            "name": "동대문시장",
            "desc": "패션·원단·잡화 중심의 대형 전통시장. DDP와 쇼핑·야시장 거리가 이어집니다.",
            "how": "지하철 2·4·5호선 동대문역사문화공원역 6·7번 출구.",
            "address": "서울 중구 장충단로 275",
        },
        "en": {
            "name": "Dongdaemun Market",
            "desc": "Huge fashion/fabric market linked to DDP and late-night shopping streets.",
            "how": "Lines 2/4/5 Dongdaemun History & Culture Park Station, exits 6–7.",
            "address": "275 Jangchungdan-ro, Jung-gu, Seoul",
        },
        "ja": ("東大門市場", "ファッション・生地の巨大市場。DDPと夜のショッピング街が続く。", "地下鉄2・4・5号線 東大門歴史文化公園駅6・7番出口。"),
        "zh": ("东大门市场", "以时尚、布料为主的大型传统市场，与DDP和夜市相连。", "地铁2·4·5号线东大门历史文化公园站6·7号出口。"),
        "zh-Hant": ("東大門市場", "以時尚、布料為主的大型傳統市場，與DDP和夜市相連。", "地鐵2·4·5號線東大門歷史文化公園站6·7號出口。"),
    },
    {
        "slug": "noryangjin-fish-market",
        "lat": 37.5136,
        "lng": 126.9409,
        "region": "seoul",
        "maps_q": "노량진수산시장",
        "ko": {
            "name": "노량진수산시장",
            "desc": "24시간 수산물 도매·소매 시장. 회·조개·게 등을 골라 2층에서 바로 요리해 먹을 수 있습니다.",
            "how": "지하철 1·9호선 노량진역 1번 출구에서 도보 2분.",
            "address": "서울 동작구 노들로 674",
        },
        "en": {
            "name": "Noryangjin Fish Market",
            "desc": "24-hour wholesale fish market — pick seafood downstairs, eat it cooked upstairs.",
            "how": "Lines 1 & 9 Noryangjin Station exit 1; 2 min walk.",
            "address": "674 Nodeul-ro, Dongjak-gu, Seoul",
        },
        "ja": ("鷺梁津水産市場", "24時間の魚市場。1階で選び2階で調理して食べられる。", "地下鉄1・9号線 鷺梁津駅1番出口から徒歩2分。"),
        "zh": ("鹭梁津水产市场", "24小时水产市场，一楼选海鲜、二楼现做现吃。", "地铁1·9号线鹭梁津站1号出口步行2分钟。"),
        "zh-Hant": ("鷺梁津水產市場", "24小時水產市場，一樓選海鮮、二樓現做現吃。", "地鐵1·9號線鷺梁津站1號出口步行2分鐘。"),
    },
    {
        "slug": "myeongdong-night-market",
        "lat": 37.5636,
        "lng": 126.9855,
        "region": "seoul",
        "maps_q": "명동야시장",
        "ko": {
            "name": "명동야시장",
            "desc": "명동 거리 저녁·야간 길거리 음식 거리. 떡볶이·소떡·회오리감자·디저트 스낵이 많습니다.",
            "how": "지하철 4호선 명동역 또는 2호선 을지로입구역에서 명동 보행자 거리 방향.",
            "address": "서울 중구 명동길 일대",
        },
        "en": {
            "name": "Myeongdong Night Market",
            "desc": "Evening street-food lanes in Myeongdong — tteokbokki, hot dogs, tornado potatoes, desserts.",
            "how": "Line 4 Myeongdong or Line 2 Euljiro 1-ga; walk into Myeongdong pedestrian streets.",
            "address": "Myeongdong-gil area, Jung-gu, Seoul",
        },
        "ja": ("明洞夜市", "明洞の夕方〜夜の屋台エリア。トッポッキやスナックが充実。", "地下鉄4号線 明洞駅または2号線 乙支路入口駅から徒歩。"),
        "zh": ("明洞夜市", "明洞傍晚至夜间的街头美食区，炒年糕、热狗、旋风土豆等。", "地铁4号线明洞站或2号线乙支路入口站步行进入明洞。"),
        "zh-Hant": ("明洞夜市", "明洞傍晚至夜間的街頭美食區，炒年糕、熱狗、旋風土豆等。", "地鐵4號線明洞站或2號線乙支路入口站步行進入明洞。"),
    },
    {
        "slug": "gyeongdong-market",
        "lat": 37.5789,
        "lng": 127.0350,
        "region": "seoul",
        "maps_q": "경동시장",
        "ko": {
            "name": "경동시장",
            "desc": "약재·한방·생활잡화 중심의 동대문 인근 전통시장. 약초·건강식품 거리로도 알려져 있습니다.",
            "how": "지하철 1·2호선 신설동역 11번 출구에서 도보 5분.",
            "address": "서울 동대문구 고미술로 70",
        },
        "en": {
            "name": "Gyeongdong Market",
            "desc": "Herbal medicine and daily-goods market near Dongdaemun — famous for ginseng and health foods.",
            "how": "Lines 1/2 Sinseol-dong Station exit 11; ~5 min walk.",
            "address": "70 Gominsul-ro, Dongdaemun-gu, Seoul",
        },
        "ja": ("京東市場", "漢方・生薬・雑貨の市場。人参や健康食品で知られる。", "地下鉄1・2号線 新設洞駅11番出口から徒歩5分。"),
        "zh": ("京东市场", "以药材、韩方、生活用品为主，人参和健康食品有名。", "地铁1·2号线新设洞站11号出口步行5分钟。"),
        "zh-Hant": ("京東市場", "以藥材、韓方、生活用品為主，人參和健康食品有名。", "地鐵1·2號線新設洞站11號出口步行5分鐘。"),
    },
    {
        "slug": "seoul-folk-flea-market",
        "lat": 37.5708,
        "lng": 126.9993,
        "region": "seoul",
        "maps_q": "서울풍물시장",
        "ko": {
            "name": "서울풍물시장",
            "desc": "종로5가 인근 벼룩·풍물시장. 빈티지·골동·수공예·기념품을 구경하기 좋습니다.",
            "how": "지하철 1·2·4호선 종로5가역 3번 출구에서 도보 3분.",
            "address": "서울 종로구 종로58길 27",
        },
        "en": {
            "name": "Seoul Folk Flea Market",
            "desc": "Flea market near Jongno 5-ga — vintage goods, antiques, crafts, and souvenirs.",
            "how": "Lines 1/2/4 Jongno 5-ga Station exit 3; 3 min walk.",
            "address": "27 Jongno 58-gil, Jongno-gu, Seoul",
        },
        "ja": ("ソウル風物市場", "鐘路5街近くのフリーマーケット。古着・骨董・工芸品が並ぶ。", "地下鉄1・2・4号線 鐘路5街駅3番出口から徒歩3分。"),
        "zh": ("首尔风物市场", "钟路5街附近的跳蚤市场，适合逛Vintage和纪念品。", "地铁1·2·4号线钟路5街站3号出口步行3分钟。"),
        "zh-Hant": ("首爾風物市場", "鐘路5街附近的跳蚤市場，適合逛Vintage和紀念品。", "地鐵1·2·4號線鐘路5街站3號出口步行3分鐘。"),
    },
    {
        "slug": "jagalchi-market",
        "lat": 35.0974,
        "lng": 129.0307,
        "region": "busan",
        "maps_q": "자갈치시장",
        "wiki": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Jagalchi_Market.jpg/1280px-Jagalchi_Market.jpg",
        "ko": {
            "name": "자갈치시장",
            "desc": "부산 대표 수산시장. 활어·회·조개·멸치 등 해산물과 바닷가 분위기를 즐길 수 있습니다.",
            "how": "지하철 1호선 자갈치역·남포역에서 도보 5분.",
            "address": "부산 중구 자갈치해안로 52",
        },
        "en": {
            "name": "Jagalchi Market",
            "desc": "Busan’s flagship fish market — live seafood, sashimi stalls, and waterfront vibes.",
            "how": "Line 1 Jagalchi or Nampo Station; ~5 min walk.",
            "address": "52 Jagalchihaean-ro, Jung-gu, Busan",
        },
        "ja": ("札嘎其市場", "釜山を代表する魚市場。活魚・刺身・貝類が並ぶ。", "地下鉄1号線 札嘎其駅または南浦駅から徒歩5分。"),
        "zh": ("札嘎其市场", "釜山代表水产市场，活鱼、生鱼片、贝类齐全。", "地铁1号线札嘎其站或南浦站步行5分钟。"),
        "zh-Hant": ("札嘎其市場", "釜山代表水產市場，活魚、生魚片、貝類齊全。", "地鐵1號線札嘎其站或南浦站步行5分鐘。"),
    },
    {
        "slug": "gukje-market",
        "lat": 35.1028,
        "lng": 129.0258,
        "region": "busan",
        "maps_q": "국제시장",
        "ko": {
            "name": "국제시장",
            "desc": "부산 원도심 전통시장. 골목 간식·의류·잡화와 영화 「국제시장」 배경으로도 유명합니다.",
            "how": "지하철 1호선 자갈치역·중앙역·남포역에서 도보.",
            "address": "부산 중구 신창동4가 일대",
        },
        "en": {
            "name": "Gukje Market",
            "desc": "Historic Busan market maze — snacks, clothes, and the film-famous alleys.",
            "how": "Line 1 Jagalchi / Jung-ang / Nampo; walk into the market blocks.",
            "address": "Sinchang 4-ga area, Jung-gu, Busan",
        },
        "ja": ("国際市場", "釜山の旧市街市場。路地裏の食べ物と映画「国際市場」の舞台。", "地下鉄1号線 札嘎其・中央・南浦駅から徒歩。"),
        "zh": ("国际市场", "釜山老城区传统市场，小巷美食和同名电影背景地。", "地铁1号线札嘎其·中央·南浦站步行进入。"),
        "zh-Hant": ("國際市場", "釜山舊城區傳統市場，小巷美食和同名電影背景地。", "地鐵1號線札嘎其·中央·南浦站步行進入。"),
    },
    {
        "slug": "bujeon-kkangtong-market",
        "lat": 35.1178,
        "lng": 129.0403,
        "region": "busan",
        "maps_q": "부평깡통시장",
        "ko": {
            "name": "부평깡통시장",
            "desc": "부전동 골목 시장·야시장. 저녁부터 북적이는 포장마차·안주·길거리 음식이 인기입니다.",
            "how": "부산 1호선 부전역·서면역에서 도보 5~10분.",
            "address": "부산 부산진구 부전동 일대",
        },
        "en": {
            "name": "Bujeon Kkangtong Market",
            "desc": "Evening alley market in Bujeon — pojangmacha tents and street snacks after dark.",
            "how": "Busan Metro Line 1 Bujeon or Seomyeon Station; 5–10 min walk.",
            "address": "Bujeon-dong area, Busanjin-gu, Busan",
        },
        "ja": ("釜田缶詰市場", "釜田の路地裏夜市。ポジャンマチャと屋台が人気。", "釜山1号線 釜田・西面駅から徒歩5〜10分。"),
        "zh": ("釜田罐头市场", "釜田巷弄夜市，傍晚起 pojangmacha 和街头小吃很热闹。", "釜山1号线釜田·西面站步行5–10分钟。"),
        "zh-Hant": ("釜田罐頭市場", "釜田巷弄夜市，傍晚起 pojangmacha 和街頭小吃很熱鬧。", "釜山1號線釜田·西面站步行5–10分鐘。"),
    },
    {
        "slug": "gupo-market",
        "lat": 35.2045,
        "lng": 129.0840,
        "region": "busan",
        "maps_q": "구포시장",
        "ko": {
            "name": "구포시장",
            "desc": "북부 부산의 대형 전통시장. 생활용품·농수산물·시장 반찬·국밥 등 로컬 먹거리가 많습니다.",
            "how": "부산 3호선 구포역 1번 출구에서 도보 3분.",
            "address": "부산 북구 구포동 일대",
        },
        "en": {
            "name": "Gupo Market",
            "desc": "Large northern Busan market — produce, side dishes, and local gukbap stalls.",
            "how": "Busan Metro Line 3 Gupo Station exit 1; 3 min walk.",
            "address": "Gupo-dong area, Buk-gu, Busan",
        },
        "ja": ("龟浦市場", "北部釜山の大型市場。惣菜や国밥など地元の食べ物が豊富。", "釜山3号線 龜浦駅1番出口から徒歩3分。"),
        "zh": ("龟浦市场", "釜山北部大型传统市场，本地小菜、汤饭很多。", "釜山3号线龟浦站1号出口步行3分钟。"),
        "zh-Hant": ("龜浦市場", "釜山北部大型傳統市場，本地小菜、湯飯很多。", "釜山3號線龜浦站1號出口步行3分鐘。"),
    },
    {
        "slug": "seomun-market",
        "lat": 35.8698,
        "lng": 128.5930,
        "region": "",
        "maps_q": "대구 서문시장",
        "ko": {
            "name": "서문시장",
            "desc": "대구 최대 전통시장. 야시장·길거리 음식·막창·납작만두 등 대구 먹거리의 중심입니다.",
            "how": "대구 지하철 2호선 서문시장역 5번 출구.",
            "address": "대구 중구 달성로 50",
        },
        "en": {
            "name": "Seomun Market",
            "desc": "Daegu’s largest market — night stalls, flat dumplings, makchang, and local snacks.",
            "how": "Daegu Metro Line 2 Seomun Market Station exit 5.",
            "address": "50 Dalseong-ro, Jung-gu, Daegu",
        },
        "ja": ("西門市場", "大邱最大の伝統市場。夜市と地元グルメの中心。", "大邱2号線 西門市場駅5番出口。"),
        "zh": ("西门市场", "大邱最大传统市场，夜市和平底 dumplings、烤肠等本地美食。", "大邱2号线西门市场站5号出口。"),
        "zh-Hant": ("西門市場", "大邱最大傳統市場，夜市和平底 dumplings、烤腸等本地美食。", "大邱2號線西門市場站5號出口。"),
    },
    {
        "slug": "chilseong-market",
        "lat": 35.8705,
        "lng": 128.5890,
        "region": "",
        "maps_q": "대구 칠성시장",
        "ko": {
            "name": "칠성시장",
            "desc": "대구 도심 칠성로 인근 전통시장. 서문시장과 가까워 시장 투어에 함께 넣기 좋습니다.",
            "how": "대구 지하철 2호선 반월당역·중앙로역에서 도보 5~10분.",
            "address": "대구 중구 칠성로 일대",
        },
        "en": {
            "name": "Chilseong Market",
            "desc": "Traditional market near Chilseong-ro — pair with Seomun Market on a food walk.",
            "how": "Daegu Metro Line 2 Banwoldang or Jungangno; 5–10 min walk.",
            "address": "Chilseong-ro area, Jung-gu, Daegu",
        },
        "ja": ("七星市場", "大邱中心部の伝統市場。西門市場とセットで回るのがおすすめ。", "大邱2号線 半月堂・中央路駅から徒歩5〜10分。"),
        "zh": ("七星市场", "大邱市中心传统市场，可与西门市场一起逛。", "大邱2号线半月堂·中央路站步行5–10分钟。"),
        "zh-Hant": ("七星市場", "大邱市中心傳統市場，可與西門市場一起逛。", "大邱2號線半月堂·中央路站步行5–10分鐘。"),
    },
    {
        "slug": "jeonju-nambu-market",
        "lat": 35.8120,
        "lng": 127.1290,
        "region": "jeolla",
        "maps_q": "전주 남부시장",
        "ko": {
            "name": "남부시장",
            "desc": "전주 한옥마을과 가까운 시장. 비빔밥 재료·반찬·전주 향토 먹거리를 맛보기 좋습니다.",
            "how": "전주 시내 버스·택시; 한옥마을에서 도보 10~15분.",
            "address": "전북 전주시 완산구 전주천동로 70",
        },
        "en": {
            "name": "Jeonju Nambu Market",
            "desc": "Market near Hanok Village — bibimbap ingredients and Jeonju street food.",
            "how": "City bus/taxi; ~10–15 min walk from Hanok Village.",
            "address": "70 Jeonjucheondong-ro, Wansan-gu, Jeonju",
        },
        "ja": ("南部市場（全州）", "全州韓屋村近くの市場。ビビンバの材料や郷土料理が並ぶ。", "韓屋村から徒歩10〜15分、または市内バス。"),
        "zh": ("南部市场（全州）", "靠近全州韩屋村，可品尝拌饭材料和乡土小吃。", "从韩屋村步行10–15分钟或乘市内公交。"),
        "zh-Hant": ("南部市場（全州）", "靠近全州韓屋村，可品嚐拌飯材料和鄉土小吃。", "從韓屋村步行10–15分鐘或乘市內公車。"),
    },
    {
        "slug": "jeonju-jungang-market",
        "lat": 35.8145,
        "lng": 127.1275,
        "region": "jeolla",
        "maps_q": "전주중앙시장",
        "ko": {
            "name": "전주중앙시장",
            "desc": "전주 도심 전통시장. 초코파이·치즈김밥 등 SNS 간식과 향토 음식이 많습니다.",
            "how": "전주 시내 중심; 한옥마을·객리단길과 택시·버스로 이동.",
            "address": "전북 전주시 완산구 중앙동 일대",
        },
        "en": {
            "name": "Jeonju Jungang Market",
            "desc": "Downtown Jeonju market — viral snacks and local specialties.",
            "how": "Central Jeonju; bus/taxi from Hanok Village or Gaekridan-gil.",
            "address": "Jungang-dong area, Wansan-gu, Jeonju",
        },
        "ja": ("全州中央市場", "全州中心部の伝統市場。SNSで話題のスナックが多い。", "韓屋村・ゲクリダン通りからバス・タクシー。"),
        "zh": ("全州中央市场", "全州市中心传统市场，网红小吃和乡土美食很多。", "从韩屋村·客里团路乘公交或出租车。"),
        "zh-Hant": ("全州中央市場", "全州市中心傳統市場，網紅小吃和鄉土美食很多。", "從韓屋村·客里團路乘公車或計程車。"),
    },
    {
        "slug": "gangneung-jungang-market",
        "lat": 37.7515,
        "lng": 128.8960,
        "region": "gangwon",
        "maps_q": "강릉중앙시장",
        "ko": {
            "name": "강릉중앙시장",
            "desc": "강릉 도심 전통시장. 닭강정·오징어순대·커피 거리와 함께 동해 여행 코스에 넣기 좋습니다.",
            "how": "강릉역·시외버스터미널에서 택시·버스; 중앙시장 정류장 하차.",
            "address": "강원 강릉시 중앙시장길 21",
        },
        "en": {
            "name": "Gangneung Jungang Market",
            "desc": "Central Gangneung market — dakgangjeong, squid sundae, and East Coast trip stop.",
            "how": "Bus/taxi from Gangneung Station or bus terminal.",
            "address": "21 Jungang Market-gil, Gangneung",
        },
        "ja": ("江陵中央市場", "江陵の中心市場。タッカンジョンやイカソンデが人気。", "江陵駅・バスターミナルからバス・タクシー。"),
        "zh": ("江陵中央市场", "江陵市中心传统市场，炸鸡、鱿鱼血肠等东海岸美食。", "从江陵站或巴士站乘公交或出租车。"),
        "zh-Hant": ("江陵中央市場", "江陵市中心傳統市場，炸雞、魷魚血腸等東海岸美食。", "從江陵站或巴士站乘公車或計程車。"),
    },
    {
        "slug": "jeju-dongmun-market",
        "lat": 33.5115,
        "lng": 126.5290,
        "region": "jeju",
        "maps_q": "제주 동문시장",
        "ko": {
            "name": "동문시장",
            "desc": "제주시 대표 전통시장. 갈치·흑돼지·오메기떡·감귤 등 제주 특산 먹거리가 가득합니다.",
            "how": "제주 시내 버스; 동문시장·제주 관덕정류장 정류장 하차.",
            "address": "제주 제주시 동문로 20",
        },
        "en": {
            "name": "Jeju Dongmun Market",
            "desc": "Main Jeju City market — cutlass fish, black pork, omegi tteok, and citrus treats.",
            "how": "City bus to Dongmun Market / Gwandeokjeong stop.",
            "address": "20 Dongmun-ro, Jeju City",
        },
        "ja": ("東門市場（済州）", "済州シの代表市場。サバ・黒豚・オメギ餅・みかんが並ぶ。", "済州市内バス 東門市場停留所下車。"),
        "zh": ("东门市场（济州）", "济州市代表传统市场，刀鱼、黑猪肉、麻糬和柑橘特产丰富。", "济州市内公交东门市场站下车。"),
        "zh-Hant": ("東門市場（濟州）", "濟州市代表傳統市場，刀魚、黑豬肉、麻糬和柑橘特產豐富。", "濟州市內公車東門市場站下車。"),
    },
    {
        "slug": "seogwipo-maeil-olle-market",
        "lat": 33.2478,
        "lng": 126.5650,
        "region": "jeju",
        "maps_q": "서귀포매일올레시장",
        "ko": {
            "name": "서귀포매일올레시장",
            "desc": "서귀포 매일 열리는 올레시장. 제주 해산물·특산품·야간 먹거리를 즐길 수 있습니다.",
            "how": "서귀포 시내 버스·택시; 올레시장·중앙로 정류장 인근.",
            "address": "제주 서귀포시 중앙로59번길 21",
        },
        "en": {
            "name": "Seogwipo Maeil Olle Market",
            "desc": "Daily Olle market in Seogwipo — seafood, Jeju specialties, and evening snacks.",
            "how": "City bus/taxi in Seogwipo; near Olle Market bus stop.",
            "address": "21 Jungang-ro 59beon-gil, Seogwipo",
        },
        "ja": ("西帰浦毎日オルレ市場", "西帰浦の毎日開催マーケット。海産物と済州特産が並ぶ。", "西帰浦市内バス・タクシー。"),
        "zh": ("西归浦每日Olle市场", "西归浦每日举办的Olle市场，海鲜和济州特产丰富。", "西归浦市内公交或出租车。"),
        "zh-Hant": ("西歸浦每日Olle市場", "西歸浦每日舉辦的Olle市場，海鮮和濟州特產豐富。", "西歸浦市內公車或計程車。"),
    },
    {
        "slug": "sinpo-international-market",
        "lat": 37.4725,
        "lng": 126.6275,
        "region": "incheon",
        "maps_q": "신포국제시장",
        "ko": {
            "name": "신포국제시장",
            "desc": "인천 차이나타운·월미도 인근 시장. 닭강정·공갈빵 등 인천 대표 간식 거리입니다.",
            "how": "수인선·1호선 인천역에서 차이나타운·신포동 방향 도보 10분.",
            "address": "인천 중구 신포동 일대",
        },
        "en": {
            "name": "Sinpo International Market",
            "desc": "Market near Incheon Chinatown — dakgangjeong alley and local snack streets.",
            "how": "Walk from Incheon Station (Line 1 / Suin) toward Sinpo & Chinatown (~10 min).",
            "address": "Sinpo-dong area, Jung-gu, Incheon",
        },
        "ja": ("新浦国際市場", "仁川チャイナタウン近く。タッカンジョンなど仁川名物の屋台。", "仁川駅から中華街・新浦方面徒歩10分。"),
        "zh": ("新浦国际市场", "仁川中华街附近，炸鸡街和空壳面包等仁川名小吃。", "仁川站向中华街·新浦方向步行10分钟。"),
        "zh-Hant": ("新浦國際市場", "仁川中華街附近，炸雞街和空殼麵包等仁川名小吃。", "仁川站向中華街·新浦方向步行10分鐘。"),
    },
    {
        "slug": "incheon-complex-fish-market",
        "lat": 37.4515,
        "lng": 126.5980,
        "region": "incheon",
        "maps_q": "인천종합어시장",
        "ko": {
            "name": "인천종합어시장",
            "desc": "인천 항구 도시의 대형 수산시장. 신선한 회·조개·게를 고르고 근처 식당에서 즐길 수 있습니다.",
            "how": "인천 1호선 제물포역·인천역에서 택시·버스.",
            "address": "인천 중구 항동7가 48",
        },
        "en": {
            "name": "Incheon Complex Fish Market",
            "desc": "Major Incheon seafood market — pick fish and eat at nearby restaurants.",
            "how": "Taxi/bus from Incheon Line 1 Jaemulpo or Incheon Station.",
            "address": "48 Hang-dong 7-ga, Jung-gu, Incheon",
        },
        "ja": ("仁川総合魚市場", "仁川の大型魚市場。選んだ魚を近くの店で調理。", "仁川1号線 チョムルポ・仁川駅からバス・タクシー。"),
        "zh": ("仁川综合鱼市场", "仁川大型水产市场，可选海鲜后在附近餐厅加工。", "仁川1号线堤物浦·仁川站乘公交或出租车。"),
        "zh-Hant": ("仁川綜合魚市場", "仁川大型水產市場，可選海鮮後在附近餐廳加工。", "仁川1號線堤物浦·仁川站乘公車或計程車。"),
    },
    {
        "slug": "suwon-paldalmun-market",
        "lat": 37.2775,
        "lng": 127.0145,
        "region": "gyeonggi",
        "maps_q": "팔달문시장",
        "ko": {
            "name": "팔달문시장",
            "desc": "수원 화성 남문(팔달문) 인근 전통시장. 화성 관광과 함께 시장 국밥·빈대떡을 즐기기 좋습니다.",
            "how": "수인선·1호선 수원역·화서역에서 버스·택시; 팔달문 하차.",
            "address": "경기 수원시 팔달구 정조로800번길 11",
        },
        "en": {
            "name": "Suwon Paldalmun Market",
            "desc": "Market by Hwaseong’s Paldalmun Gate — pair with fortress sightseeing and gukbap.",
            "how": "Bus/taxi from Suwon or Hwaseo Station to Paldalmun.",
            "address": "11 Jeongjo-ro 800beon-gil, Paldal-gu, Suwon",
        },
        "ja": ("八達門市場", "水原華城南門近くの市場。城観光とセットで。", "水原・花水駅からバス・タクシーで八達門。"),
        "zh": ("八达门市场", "水原华城南门附近传统市场，适合与城堡游览一起。", "水原·花水站乘公交或出租车至八达门。"),
        "zh-Hant": ("八達門市場", "水原華城南門附近傳統市場，適合與城堡遊覽一起。", "水原·花水站乘公車或計程車至八達門。"),
    },
    {
        "slug": "sokcho-tourist-fish-market",
        "lat": 38.2075,
        "lng": 128.5910,
        "region": "gangwon",
        "maps_q": "속초관광수산시장",
        "ko": {
            "name": "속초관광수산시장",
            "desc": "속초 대표 수산·특산시장. 오징어순대·닭강정·속초 중앙시장과 함께 동해 북부 여행 필수 코스입니다.",
            "how": "속초 시외버스터미널·속초역에서 도보 10분.",
            "address": "강원 속초시 중앙로147번길 12",
        },
        "en": {
            "name": "Sokcho Tourist Fish Market",
            "desc": "Sokcho’s seafood hub — squid sundae and dakgangjeong; staple on the east coast north route.",
            "how": "~10 min walk from Sokcho bus terminal or Sokcho Station.",
            "address": "12 Jungang-ro 147beon-gil, Sokcho",
        },
        "ja": ("束草観光水産市場", "束草の海産物市場。イカソンデやタッカンジョンが名物。", "束草バスターミナル・駅から徒歩10分。"),
        "zh": ("束草观光水产市场", "束草代表水产市场，鱿鱼血肠、炸鸡是东海岸北部必吃。", "束草巴士站或火车站步行10分钟。"),
        "zh-Hant": ("束草觀光水產市場", "束草代表水產市場，魷魚血腸、炸雞是東海岸北部必吃。", "束草巴士站或火車站步行10分鐘。"),
    },
    {
        "slug": "chuncheon-folk-market",
        "lat": 37.8775,
        "lng": 127.7290,
        "region": "gangwon",
        "maps_q": "춘천풍물시장",
        "ko": {
            "name": "춘천풍물시장",
            "desc": "춘천 중앙로 인근 전통시장. 닭갈비·막국수·호두과자 등 춘천 향토 먹거리를 맛볼 수 있습니다.",
            "how": "ITX·경춘선 춘천역에서 중앙로·풍물시장 방향 도보 10분.",
            "address": "강원 춘천시 중앙로 62",
        },
        "en": {
            "name": "Chuncheon Folk Market",
            "desc": "Market on Chuncheon’s Jungang-ro — dakgalbi, makguksu, and walnut pastries.",
            "how": "~10 min walk from Chuncheon Station toward Jungang-ro.",
            "address": "62 Jungang-ro, Chuncheon",
        },
        "ja": ("春川風物市場", "春川中心部の市場。タッカルビ・マッククス・クルミ菓子が並ぶ。", "春川駅から中央路方面徒歩10分。"),
        "zh": ("春川风物市场", "春川中央路附近传统市场，辣炒鸡、冷面、核桃点心等。", "春川站向中央路方向步行10分钟。"),
        "zh-Hant": ("春川風物市場", "春川中央路附近傳統市場，辣炒雞、冷麵、核桃點心等。", "春川站向中央路方向步行10分鐘。"),
    },
    {
        "slug": "yeosu-seo-market",
        "lat": 34.7605,
        "lng": 127.6620,
        "region": "jeolla",
        "maps_q": "여수서시장",
        "ko": {
            "name": "여수서시장",
            "desc": "여수 도심 전통시장. 갓김치·돌게장·회·해산물 반찬 등 남해 먹거리가 풍부합니다.",
            "how": "여수엑스포역·시외버스터미널에서 택시·버스.",
            "address": "전남 여수시 서교동 65",
        },
        "en": {
            "name": "Yeosu Seo Market",
            "desc": "Central Yeosu market — gat kimchi, crab jeotgal, and southern coast seafood.",
            "how": "Bus/taxi from Yeosu Expo Station or intercity bus terminal.",
            "address": "65 Seogyo-dong, Yeosu",
        },
        "ja": ("麗水西市場", "麗水中心部の市場。ガットキムチやカニ醤が名物。", "麗水エキスポ駅・バスターミナルからバス・タクシー。"),
        "zh": ("丽水西市场", "丽水市中心传统市场，芥菜泡菜、酱蟹等南海美食丰富。", "丽水世博会站或巴士站乘公交或出租车。"),
        "zh-Hant": ("麗水西市場", "麗水市中心傳統市場，芥菜泡菜、醬蟹等南海美食豐富。", "麗水世博會站或巴士站乘公車或計程車。"),
    },
    {
        "slug": "tongyeong-jungang-market",
        "lat": 34.8465,
        "lng": 128.4255,
        "region": "gyeongsang",
        "maps_q": "통영중앙전통시장",
        "ko": {
            "name": "통영중앙전통시장",
            "desc": "통영 도심 전통시장. 꿀빵·충무김밥·굴·멸치 등 남해 특산과 길거리 간식이 유명합니다.",
            "how": "통영종합버스터미널에서 택시·도보; 중앙시장 정류장 하차.",
            "address": "경남 통영시 중앙로 77",
        },
        "en": {
            "name": "Tongyeong Jungang Market",
            "desc": "Tongyeong’s central market — kkulppang, Chungmu gimbap, oysters, and anchovy treats.",
            "how": "Taxi/walk from Tongyeong bus terminal; Jungang Market bus stop.",
            "address": "77 Jungang-ro, Tongyeong",
        },
        "ja": ("統營中央伝統市場", "統営の中心市場。クルパン・忠武キンパプ・カキが名物。", "統営バスターミナルからタクシー・徒歩。"),
        "zh": ("统营中央传统市场", "统营中心传统市场，蜂蜜面包、忠武紫菜包饭、牡蛎等有名。", "统营巴士总站乘出租车或步行。"),
        "zh-Hant": ("統營中央傳統市場", "統營中心傳統市場，蜂蜜麵包、忠武紫菜包飯、牡蠣等有名。", "統營巴士總站乘計程車或步行。"),
    },
    {
        "slug": "mokpo-fish-market",
        "lat": 34.7885,
        "lng": 126.3855,
        "region": "jeolla",
        "maps_q": "목포종합수산시장",
        "ko": {
            "name": "목포종합수산시장",
            "desc": "목포항 인근 종합수산시장. 회·조개·멸치·홍어 등 서남해 해산물을 맛보기 좋습니다.",
            "how": "목포역·버스터미널에서 택시; 목포항·수산시장 하차.",
            "address": "전남 목포시 항로7길 68",
        },
        "en": {
            "name": "Mokpo Complex Fish Market",
            "desc": "Fish market by Mokpo Port — sashimi, shellfish, and southwest coast specialties.",
            "how": "Taxi from Mokpo Station or bus terminal to the port market.",
            "address": "68 Hang-ro 7-gil, Mokpo",
        },
        "ja": ("木浦総合水産市場", "木浦港近くの魚市場。刺身・貝・ホンオなど西南海の海産物。", "木浦駅・バスターミナルからタクシー。"),
        "zh": ("木浦综合水产市场", "木浦港附近水产市场，生鱼片、贝类、斑鳐等西南海海鲜。", "木浦站或巴士站乘出租车。"),
        "zh-Hant": ("木浦綜合水產市場", "木浦港附近水產市場，生魚片、貝類、斑鳐等西南海海鮮。", "木浦站或巴士站乘計程車。"),
    },
    {
        "slug": "gyeongju-jungang-market",
        "lat": 35.8465,
        "lng": 129.2105,
        "region": "gyeongju",
        "maps_q": "경주중앙시장",
        "ko": {
            "name": "경주중앙시장",
            "desc": "경주 도심 전통시장. 황리단길·불국사 여행 전후로 경주 빵·시장 국밥·간식을 즐기기 좋습니다.",
            "how": "경주역·고속버스터미널에서 택시·버스; 중앙시장 정류장.",
            "address": "경북 경주시 중앙시장길 17",
        },
        "en": {
            "name": "Gyeongju Jungang Market",
            "desc": "Downtown Gyeongju market — local bread, gukbap, and snacks between heritage sites.",
            "how": "Bus/taxi from Gyeongju Station or express bus terminal.",
            "address": "17 Jungang Market-gil, Gyeongju",
        },
        "ja": ("慶州中央市場", "慶州中心部の市場。慶州パンや市場グルメが並ぶ。", "慶州駅・バスターミナルからバス・タクシー。"),
        "zh": ("庆州中央市场", "庆州市中心传统市场，庆州面包和市场汤饭等。", "庆州站或巴士站乘公交或出租车。"),
        "zh-Hant": ("慶州中央市場", "慶州市中心傳統市場，慶州麵包和市場湯飯等。", "慶州站或巴士站乘公車或計程車。"),
    },
    {
        "slug": "gongju-sanseong-market",
        "lat": 36.4555,
        "lng": 127.1245,
        "region": "chungcheong",
        "maps_q": "공주산성시장",
        "ko": {
            "name": "공주산성시장",
            "desc": "공주 공산성·국립공주박물관 인근 전통시장. 유네스코 공산성 관광과 함께 둘러보기 좋습니다.",
            "how": "공주역·버스터미널에서 택시; 공산성·산성시장 하차.",
            "address": "충남 공주시 산성시장길 17",
            "regionLabel": "충남",
        },
        "en": {
            "name": "Gongju Sanseong Market",
            "desc": "Market near Gongju Gongsanseong Fortress — combine with UNESCO site sightseeing.",
            "how": "Taxi from Gongju Station or bus terminal to the fortress market.",
            "address": "17 Sanseong Market-gil, Gongju",
            "regionLabel": "Chungcheong",
        },
        "ja": ("公州山城市場", "公州山城・博物館近くの市場。世界遺産観光とセットで。", "公州駅・バスターミナルからタクシー。"),
        "zh": ("公州山城市场", "公州公山城和博物馆附近传统市场，可与世界遗产游览一起。", "公州站或巴士站乘出租车。"),
        "zh-Hant": ("公州山城市場", "公州公山城和博物館附近傳統市場，可與世界遺產遊覽一起。", "公州站或巴士站乘計程車。"),
    },
    {
        "slug": "andong-gu-market",
        "lat": 36.5685,
        "lng": 128.7285,
        "region": "gyeongsang",
        "maps_q": "안동구시장",
        "ko": {
            "name": "안동구시장",
            "desc": "안동 도심 전통시장(안동구 시장). 찜닭·간고등어·헛제사밥 등 안동 향토 음식을 맛볼 수 있습니다.",
            "how": "안동역·터미널에서 택시·버스; 안동구시장 정류장.",
            "address": "경북 안동시 경동로 655",
        },
        "en": {
            "name": "Andong Gu Market",
            "desc": "Central Andong market — jjim-dak, grilled mackerel, and Andong specialty dishes.",
            "how": "Bus/taxi from Andong Station or terminal to Andong Gu Market stop.",
            "address": "655 Gyeongdong-ro, Andong",
        },
        "ja": ("安東区市場", "安東中心部の伝統市場。チムダックや干しサバが名物。", "安東駅・ターミナルからバス・タクシー。"),
        "zh": ("安东区市场", "安东市中心传统市场，炖鸡、烤鲭鱼等安东乡土菜。", "安东站或巴士站乘公交或出租车。"),
        "zh-Hant": ("安東區市場", "安東市中心傳統市場，燉雞、烤鯖魚等安東鄉土菜。", "安東站或巴士站乘公車或計程車。"),
    },
    {
        "slug": "pohang-jukdo-market",
        "lat": 36.0315,
        "lng": 129.3650,
        "region": "gyeongsang",
        "maps_q": "죽도시장",
        "ko": {
            "name": "죽도시장",
            "desc": "포항 죽도·영일대 인근 전통시장. 과메기·물회·회 등 동해 해산물과 포항 특산품이 많습니다.",
            "how": "포항역·버스터미널에서 택시; 죽도시장·영일대 방면.",
            "address": "경북 포항시 북구 죽도시장길 21",
        },
        "en": {
            "name": "Pohang Jukdo Market",
            "desc": "Market by Jukdo & Yeongildae — gwamegi, mulhoe, and east coast seafood.",
            "how": "Taxi from Pohang Station or bus terminal toward Jukdo / Yeongildae.",
            "address": "21 Jukdo Market-gil, Buk-gu, Pohang",
        },
        "ja": ("竹島市場", "浦項・迎日台近くの市場。ゴメギやムルフェが名物。", "浦項駅・バスターミナルからタクシー。"),
        "zh": ("竹岛市场", "浦项竹岛·迎日台附近市场，干明太鱼、水拌生鱼片等东海海鲜。", "浦项站或巴士站乘出租车。"),
        "zh-Hant": ("竹島市場", "浦項竹島·迎日台附近市場，乾明太魚、水拌生魚片等東海海鮮。", "浦項站或巴士站乘計程車。"),
    },
]


def _ssl() -> ssl.SSLContext:
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl._create_unverified_context()


def maps_urls(q: str, hl: str) -> tuple[str, str]:
    enc = quote(q)
    return (
        f"https://www.google.com/maps/search/?api=1&query={enc}",
        f"https://maps.google.com/maps?q={enc}&hl={hl}&z=15&output=embed",
    )


def body_block(ko: dict, en: dict, extras: dict[str, tuple]) -> list:
    texts = {
        "ko": f"{ko['desc']}\n\n가는 방법: {ko['how']}",
        "en": f"{en['desc']}\n\nHow to get there: {en['how']}",
    }
    for lang, tup in extras.items():
        texts[lang] = f"{tup[1]}\n\n{tup[2]}"
    return [{"type": "text", **texts}]


def locale_tuple(market: dict, lang: str) -> tuple[str, str, str, str]:
    region = market["region"]
    rl = REGION_LABELS.get(region, REGION_LABELS[""])[lang]
    if lang in ("ko", "en"):
        block = market[lang]
        return block["name"], block["desc"], block["how"], block.get("regionLabel", rl)
    if lang in ("ja", "zh", "zh-Hant"):
        name, desc, how = market[lang]
        return name, desc, how, rl
    en = market["en"]
    name = en["name"]
    if lang == "vi":
        name = en["name"]
    elif lang == "th":
        name = en["name"]
    elif lang == "ru":
        name = en["name"]
    return name, en["desc"], en["how"], rl


def entry_for_lang(lang: str, market: dict) -> dict:
    ko, en = market["ko"], market["en"]
    slug = market["slug"]
    hl = {"zh-Hant": "zh-TW", "zh": "zh-CN"}.get(lang, lang if lang != "ko" else "ko")
    maps, embed = maps_urls(market["maps_q"], hl if lang != "en" else "en")
    img = f"Images/places/{slug}.jpg"
    region = market["region"]
    rl_map = REGION_LABELS.get(region, REGION_LABELS[""])
    if lang == "ko":
        base = {
            "name": ko["name"],
            "desc": ko["desc"],
            "how": ko["how"],
            "address": ko["address"],
            "regionLabel": ko.get("regionLabel", rl_map["ko"]),
            "region": region,
            "mapsUrl": maps,
            "mapsEmbedUrl": embed,
            "image": img,
        }
    elif lang == "en":
        base = {
            "name": en["name"],
            "desc": en["desc"],
            "how": en["how"],
            "address": en["address"],
            "regionLabel": en.get("regionLabel", rl_map["en"]),
            "region": region,
            "mapsUrl": maps_urls(market["maps_q"], "en")[0],
            "mapsEmbedUrl": maps_urls(market["maps_q"], "en")[1],
            "image": img,
        }
    else:
        name, desc, how, region_label = locale_tuple(market, lang)
        base = {
            "name": name,
            "desc": desc,
            "how": how,
            "address": en["address"] if lang in ("vi", "th", "ru") else ko["address"],
            "regionLabel": region_label,
            "region": region,
            "mapsUrl": maps,
            "mapsEmbedUrl": embed,
            "image": img,
        }
    extras = {}
    for L in ("ja", "zh", "zh-Hant", "vi", "th", "ru"):
        extras[L] = locale_tuple(market, L)
    base["body"] = body_block(ko, en, extras)
    return base


def patch_coords() -> int:
    text = COORDS.read_text(encoding="utf-8")
    if "gwangjang-market" in text:
        print("places-coords already has traditional markets")
        return 0
    if "bus-terminal" not in text:
        raise SystemExit("expected bus-terminal in places-coords.js first")
    text = text.replace(
        ' * type: "city" | "nature" | "heritage" | "airport" | "info" | "locker" | "port" | "bus-terminal"',
        ' * type: "city" | "nature" | "heritage" | "airport" | "info" | "locker" | "port" | "bus-terminal" | "market"',
    )
    text = text.replace(
        " *   bus-terminal — major express / intercity bus terminals",
        " *   bus-terminal — major express / intercity bus terminals\n"
        " *   market     — traditional markets / night markets / fish markets",
    )
    lines = []
    for m in MARKETS:
        img = f"Images/places/{m['slug']}.jpg"
        note = m["en"]["name"]
        lines.append(
            "  { "
            f'slug: "{m["slug"]}", lat: {m["lat"]}, lng: {m["lng"]}, '
            f'region: "{m["region"]}", type: "market", '
            f'note: "{note}", image: "{img}" '
            "},"
        )
    insert = "\n".join(lines) + "\n"
    idx = text.rfind("];")
    if idx < 0:
        raise SystemExit("places-coords.js: cannot find ];")
    text = text[:idx] + insert + text[idx:]
    COORDS.write_text(text, encoding="utf-8", newline="\n")
    return len(MARKETS)


def patch_i18n() -> None:
    sys.path.insert(0, str(ROOT / "tool"))
    from lib import i18n_store  # noqa: WPS433

    transport_keys = {
        "legendMarket": {
            "ko": "전통 시장",
            "en": "Traditional market",
            "ja": "伝統市場",
            "zh": "传统市场",
            "zh-Hant": "傳統市場",
            "vi": "Chợ truyền thống",
            "th": "ตลาดดั้งเดิม",
            "ru": "Традиционный рынок",
        },
        "marketBadge": {
            "ko": "전통 시장 · 먹거리·특산품",
            "en": "Traditional market · street food & local goods",
            "ja": "伝統市場 · 屋台と特産品",
            "zh": "传统市场 · 街头美食与特产",
            "zh-Hant": "傳統市場 · 街頭美食與特產",
            "vi": "Chợ truyền thống · đồ ăn & đặc sản",
            "th": "ตลาดดั้งเดิม · อาหารและของท้องถิ่น",
            "ru": "Традиционный рынок · еда и местные товары",
        },
    }

    bundle = i18n_store.load_all()
    for lang in i18n_store.LANGS:
        data = bundle[lang]
        tr = data.setdefault("transport", {})
        for key, locales in transport_keys.items():
            tr[key] = locales.get(lang) or locales["en"]
        places = data.setdefault("places", {})
        for m in MARKETS:
            places[m["slug"]] = entry_for_lang(lang, m)
        print(f"i18n {lang}: +{len(MARKETS)} markets")
    i18n_store.save_all(bundle)


def download_images() -> None:
    IMG.mkdir(parents=True, exist_ok=True)
    shopping = ROOT / "Images" / "shopping" / "market.jpg"
    type_dst = IMG / "_types" / "market.jpg"
    if shopping.exists() and not type_dst.exists():
        shutil.copy2(shopping, type_dst)
        print("wrote type fallback market.jpg")
    elif not type_dst.exists() and (IMG / "_types" / "city.jpg").exists():
        shutil.copy2(IMG / "_types" / "city.jpg", type_dst)
        print("wrote type fallback market.jpg from city.jpg")

    ctx = _ssl()
    for m in MARKETS:
        dest = IMG / f"{m['slug']}.jpg"
        if dest.exists() and dest.stat().st_size > 5000:
            continue
        url = m.get("wiki")
        if not url:
            if type_dst.exists():
                dest.write_bytes(type_dst.read_bytes())
                print(f"fallback image {dest.name}")
            continue
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "KoreaTravelGuidebook/1.0"})
            with urllib.request.urlopen(req, timeout=40, context=ctx) as r:
                dest.write_bytes(r.read())
            print(f"downloaded {dest.name} ({dest.stat().st_size} bytes)")
        except Exception as exc:  # noqa: BLE001
            print(f"image fail {m['slug']}: {exc}")
            if type_dst.exists():
                dest.write_bytes(type_dst.read_bytes())


def main() -> int:
    n = patch_coords()
    print(f"coords added: {n}")
    patch_i18n()
    download_images()
    sys.path.insert(0, str(ROOT / "tool"))
    from lib import i18n_store  # noqa: WPS433

    print(i18n_store.build_bundle())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
