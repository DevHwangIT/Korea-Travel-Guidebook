# -*- coding: utf-8 -*-
"""Generate Seoul curated day-course data + i18n fragments."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG = "../../Images/places"
PLACE = "../transportation/places"

def stop(time: str, slug: str, image: str | None = None) -> dict:
    img = image or f"{IMG}/{slug}.jpg"
    return {
        "time": time,
        "image": img,
        "href": f"{PLACE}/{slug}/index.html" if slug else "",
        "slug": slug or "",
    }

COURSES = [
    {
        "id": "c01",
        "cover": f"{IMG}/gyeongbok.jpg",
        "stops": [
            stop("09:00", "gyeongbok"),
            stop("11:00", "bukchon"),
            stop("12:30", "insadong"),
            stop("14:00", "insadong"),
            stop("15:30", "insadong"),  # ikseon vibe
            stop("17:00", "gwangjang-market"),
            stop("19:00", "cheonggyecheon"),
        ],
    },
    {
        "id": "c02",
        "cover": f"{IMG}/myeongdong.jpg",
        "stops": [
            stop("10:00", "myeongdong"),
            stop("12:00", "myeongdong"),
            stop("13:30", "namsan"),
            stop("15:00", "namsan"),
            stop("17:30", "namdaemun-market"),
            stop("19:00", "myeongdong"),
            stop("20:00", "myeongdong"),
        ],
    },
    {
        "id": "c03",
        "cover": f"{IMG}/seoul-forest.jpg",
        "stops": [
            stop("10:00", "seoul-forest"),
            stop("11:30", "seongsu-dong"),
            stop("13:00", "seongsu-dong"),
            stop("14:30", "seongsu-dong"),
            stop("17:00", "hangang-yeouido"),  # ttukseom-like riverside
            stop("19:00", "seongsu-dong"),
            stop("20:30", "seongsu-dong"),
        ],
    },
    {
        "id": "c04",
        "cover": f"{IMG}/hongdae.jpg",
        "stops": [
            stop("10:30", "hongdae"),
            stop("12:00", "hongdae"),
            stop("13:30", "hongdae"),
            stop("15:30", "hongdae"),
            stop("17:00", "mangwon-market"),
            stop("18:30", "hangang-yeouido"),
            stop("20:00", "hongdae"),
        ],
    },
    {
        "id": "c05",
        "cover": f"{IMG}/coex.jpg",
        "stops": [
            stop("10:00", "coex"),
            stop("11:00", "byeolmadang-library"),
            stop("12:30", "gangnam"),
            stop("14:00", "boteunsa"),
            stop("16:00", "seokchon-lake"),
            stop("16:30", "seokchon-lake"),
            stop("18:00", "lotte-world"),
            stop("20:00", "lotte-tower"),
        ],
    },
    {
        "id": "c06",
        "cover": f"{IMG}/naksan-park.jpg",
        "stops": [
            stop("10:00", "naksan-park"),
            stop("11:30", "naksan-park"),
            stop("13:00", "naksan-park"),
            stop("15:00", "dongdaemun"),
            stop("15:30", "dongdaemun"),
            stop("17:00", "dongdaemun-market"),
            stop("19:00", "gwangjang-market"),
            stop("20:30", "cheonggyecheon"),
        ],
    },
    {
        "id": "c07",
        "cover": f"{IMG}/hangang-yeouido.jpg",
        "stops": [
            stop("10:30", "hangang-yeouido"),
            stop("12:30", "hangang-yeouido"),
            stop("14:00", "hangang-yeouido"),
            stop("16:00", "hangang-yeouido"),
            stop("17:30", "hangang-yeouido"),
            stop("19:00", "hangang-yeouido"),
            stop("20:30", "hangang-yeouido"),
        ],
    },
    {
        "id": "c08",
        "cover": f"{IMG}/gyeongbok.jpg",
        "stops": [
            stop("09:30", "gyeongbok"),
            stop("11:30", "bukchon"),  # seochon vibe nearby
            stop("12:30", "bukchon"),
            stop("14:00", "bukchon"),
            stop("15:30", "gwathwamun"),
            stop("17:00", "cheonggyecheon"),
            stop("18:30", "bosingak"),
            stop("20:00", "bosingak"),
        ],
    },
    {
        "id": "c09",
        "cover": f"{IMG}/itaewon.jpg",
        "stops": [
            stop("11:00", "itaewon"),
            stop("12:30", "itaewon"),
            stop("14:00", "itaewon"),
            stop("16:00", "itaewon"),
            stop("17:30", "itaewon"),
            stop("19:00", "itaewon"),
            stop("20:30", "namsan"),
        ],
    },
    {
        "id": "c10",
        "cover": f"{IMG}/namdaemun-market.jpg",
        "stops": [
            stop("10:00", "namdaemun-market"),
            stop("12:00", "namdaemun-market"),
            stop("13:30", "myeongdong"),
            stop("15:30", "gwangjang-market"),
            stop("17:30", "insadong"),
            stop("19:00", "bosingak"),
            stop("20:30", "cheonggyecheon"),
        ],
    },
    {
        "id": "c11",
        "cover": f"{IMG}/lotte-world.jpg",
        "stops": [
            stop("10:00", "lotte-world"),
            stop("12:00", "lotte-world"),
            stop("13:30", "seokchon-lake"),
            stop("15:00", "seokchon-lake"),
            stop("17:00", "lotte-tower"),
            stop("19:00", "lotte-world"),
        ],
    },
    {
        "id": "c12",
        "cover": f"{IMG}/hangang-banpo.jpg",
        "stops": [
            stop("11:00", "hangang-banpo"),
            stop("13:00", "hangang-banpo"),
            stop("14:30", "hangang-banpo"),
            stop("16:00", "hangang-banpo"),
            stop("18:00", "hangang-banpo"),
            stop("20:00", "hangang-banpo"),
        ],
    },
    {
        "id": "c13",
        "cover": f"{IMG}/namsan.jpg",
        "stops": [
            stop("10:00", "namsan"),
            stop("12:30", "itaewon"),
            stop("14:00", "itaewon"),
            stop("16:00", "itaewon"),
            stop("18:00", "hangang-banpo"),
            stop("20:00", "itaewon"),
        ],
    },
    {
        "id": "c14",
        "cover": f"{IMG}/bukchon.jpg",
        "stops": [
            stop("10:00", "naksan-park"),
            stop("10:30", "bukchon"),
            stop("12:00", "bukchon"),
            stop("13:30", "jingwansa"),
            stop("15:00", "bukchon"),
            stop("17:00", "naksan-park"),
            stop("19:00", "naksan-park"),
        ],
    },
    {
        "id": "c15",
        "cover": f"{IMG}/seoul-forest.jpg",
        "stops": [
            stop("10:00", "seoul-forest"),
            stop("12:00", "seongsu-dong"),
            stop("14:00", "seongsu-dong"),
            stop("16:30", "apgujeong"),
            stop("18:00", "apgujeong"),
            stop("19:30", "apgujeong"),
        ],
    },
]

# Korean content (authoritative)
KO = {
    "pickLabel": "서울 추천 코스",
    "intro": "서울을 하루 만에 알차게 도는 대표 코스입니다. 타이틀을 고르면 시간표·사진·동선이 펼쳐집니다.",
    "routeLabel": "한눈에 보는 루트",
    "tipsLabel": "팁",
    "openCourse": "코스 보기",
    "courses": {
        "c01": {
            "title": "경복궁·북촌·인사동 코스",
            "summary": "조선의 법궁에서 시작해 한옥골목·전통거리를 걷고, 익선동 카페와 광장시장 먹거리로 마무리하는 서울 클래식 당일 코스입니다.",
            "route": "경복궁 → 북촌 → 인사동 → 익선동 → 광장시장 → 청계천",
            "tips": "경복궁은 한복 착용 시 입장료가 면제되는 경우가 많습니다. 북촌은 주거지역이니 큰 소리·무단 촬영에 주의하세요.",
            "stops": [
                {"name": "경복궁", "desc": "근정전·경회루를 중심으로 천천히 둘러보세요. 한복 대여 후 방문하면 사진도 예쁘고 입장도 유리합니다."},
                {"name": "북촌 한옥마을", "desc": "가회동·계동 골목의 기와지붕과 서울 전망 포인트를 산책합니다. 30~40분이면 핵심 골목을 볼 수 있어요."},
                {"name": "인사동 점심", "desc": "전통찻집·한정식·비빔밥 등 선택의 폭이 넓습니다. 쌈지길 안쪽으로 들어가면 웨이팅이 덜한 곳도 있어요."},
                {"name": "쌈지길·인사동 거리", "desc": "기념품·공예품·길거리 간식을 구경하며 여유롭게 걷습니다. 골목마다 소품샵과 갤러리가 이어집니다."},
                {"name": "익선동 카페", "desc": "한옥을 개조한 카페·베이커리가 밀집한 골목입니다. 디저트와 커피로 오후 에너지를 보충하세요."},
                {"name": "광장시장", "desc": "마약김밥·빈대떡·육회 등 대표 먹거리를 한곳에서 맛볼 수 있습니다. 저녁 전에 가볍게 여러 가지를 나눠 먹어보세요."},
                {"name": "청계천 산책", "desc": "하루를 마무리하며 물길을 따라 천천히 걷습니다. 야경이 예쁘고 이동도 편한 구간입니다."},
            ],
        },
        "c02": {
            "title": "명동·남산·서울 중심 코스",
            "summary": "쇼핑과 야경을 한날에 즐기는 서울 중심 코스. 명동에서 시작해 남산·N서울타워, 남대문시장까지 이어집니다.",
            "route": "명동 → 남산 → N서울타워 → 남대문시장 → 서울역·서울로",
            "tips": "N서울타워는 저녁 노을·야경 타이밍이 인기입니다. 케이블카·버스 대기 시간을 여유 있게 잡으세요.",
            "stops": [
                {"name": "명동 쇼핑", "desc": "뷰티·패션·길거리 음식을 한꺼번에 즐깁니다. 오전 개장 직후가 비교적 한산합니다."},
                {"name": "명동 점심", "desc": "칼국수·고기·글로벌 프랜차이즈까지 다양합니다. 줄이 긴 집은 피하고 골목 안쪽을 노려보세요."},
                {"name": "남산 산책", "desc": "남산순환로나 케이블카 하부를 걸어 올라갑니다. 날씨 좋은 날엔 도보만으로도 충분합니다."},
                {"name": "N서울타워", "desc": "전망대에서 서울 전경을 감상합니다. 야간 조명이 켜지기 직전이 사진 찍기 좋아요."},
                {"name": "남대문시장", "desc": "의류·생활용품·먹거리가 가득한 전통시장. 칼국수·갈치조림 등 시장 식당도 함께 즐겨보세요."},
                {"name": "서울역·서울로7017", "desc": "서울로7017 공중정원에서 도심 전망을 보며 숨 고르기. 일몰 무렵이 특히 예쁩니다."},
                {"name": "명동·을지로 저녁", "desc": "명동으로 돌아와 저녁을 먹거나, 을지로 골목의 노포·바와 야경을 즐깁니다."},
            ],
        },
        "c03": {
            "title": "성수·서울숲 코스",
            "summary": "초록 공원과 성수동의 카페·팝업을 잇는 감성 코스. 한강·건대 쪽까지 확장해 저녁을 마무리합니다.",
            "route": "서울숲 → 성수 → 뚝섬한강공원 → 건대",
            "tips": "성수는 주말 오후가 매우 붐빕니다. 카페는 오픈 직후나 평일 방문을 추천합니다.",
            "stops": [
                {"name": "서울숲", "desc": "넓은 잔디와 산책로에서 오전을 시작합니다. 자전거 대여도 가능합니다."},
                {"name": "성수동 카페거리", "desc": "공장지대를 개조한 카페·베이커리·편집숍을 구경합니다. 성수역 일대가 중심입니다."},
                {"name": "성수 점심", "desc": "브런치·파스타·한식 캐주얼까지 선택지가 많습니다. 웨이팅 많은 곳은 앱 예약이나 일찍 방문하세요."},
                {"name": "팝업스토어·편집숍", "desc": "시즌별 팝업과 디자인 숍을 둘러봅니다. SNS에 뜨는 스팟을 미리 체크하면 동선이 줄어듭니다."},
                {"name": "뚝섬한강공원", "desc": "성수에서 가까운 한강 공원. 자전거·피크닉·석양 사진에 좋습니다."},
                {"name": "건대입구 저녁", "desc": "건대 먹자골목에서 치킨·곱창·아시아 음식 등 캐주얼한 저녁을 즐깁니다."},
                {"name": "건대 거리", "desc": "상점가와 야경을 산책하며 하루를 마무리합니다."},
            ],
        },
        "c04": {
            "title": "홍대·연남·망원 코스",
            "summary": "연남동의 골목 감성에서 홍대 거리, 망원시장·한강까지 이어지는 서북권 인기 코스입니다.",
            "route": "연남동 → 홍대 → 망원시장 → 망원한강공원 → 홍대",
            "tips": "홍대는 저녁~심야가 가장 활기찹니다. 짐이 많으면 홍대입구역 락커를 활용하세요.",
            "stops": [
                {"name": "연남동", "desc": "조용한 골목 카페와 소품샵을 산책합니다. 연트럴파크(경의선숲길)도 함께 걷기 좋아요."},
                {"name": "연남동 점심", "desc": "브런치·파스타·한식 맛집이 밀집. 주말은 대기 길으니 오픈 타임에 맞춰 가세요."},
                {"name": "홍대 거리", "desc": "버스킹·벽화·스트리트 패션의 중심. 걷다 보면 시간이 빨리 갑니다."},
                {"name": "카페·쇼핑", "desc": "빈티지숍·뷰티·굿즈 매장을 둘러보고 카페에서 쉬어 갑니다."},
                {"name": "망원시장", "desc": "현지인 느낌의 시장 먹거리와 과일·분식을 즐깁니다. 포장해 한강으로 가도 좋아요."},
                {"name": "망원한강공원", "desc": "석양과 강바람을 느끼며 산책·피크닉. 자전거 대여도 인기입니다."},
                {"name": "홍대 저녁·야간", "desc": "다시 홍대로 돌아와 저녁과 야경·클럽·바 거리를 즐깁니다."},
            ],
        },
        "c05": {
            "title": "강남·잠실 코스",
            "summary": "코엑스·별마당도서관에서 봉은사를 거쳐 석촌호수·롯데월드몰·서울스카이까지 이어지는 동남권 코스.",
            "route": "코엑스 → 봉은사 → 석촌호수 → 롯데월드몰 → 서울스카이",
            "tips": "코엑스~봉은사는 도보로 가깝습니다. 서울스카이는 야경 예약이 안전합니다.",
            "stops": [
                {"name": "코엑스", "desc": "쇼핑몰·아쿠아리움·전시 공간을 둘러봅니다. 실내라 날씨에 영향이 적어요."},
                {"name": "별마당도서관", "desc": "거대한 책장 포토스팟. 짧게 들러 사진만 찍어도 충분합니다."},
                {"name": "강남 점심", "desc": "코엑스 푸드코트나 봉은사로 인근 식당에서 식사합니다."},
                {"name": "봉은사", "desc": "도심 속 사찰. 고층 빌딩과 대비되는 풍경이 인상적입니다."},
                {"name": "잠실 이동", "desc": "지하철 2호선으로 잠실·석촌 방면 이동. 약 15~25분 소요."},
                {"name": "석촌호수", "desc": "호수 산책과 벚꽃·단풍 시즌 풍경. 롯데월드타워가 배경으로 들어갑니다."},
                {"name": "롯데월드몰", "desc": "쇼핑·아쿠아리움·먹거리를 한꺼번에. 저녁 식사도 여기서 해결하기 좋습니다."},
                {"name": "서울스카이·잠실 야경", "desc": "전망대에서 한강과 서울 야경을 감상하거나, 호수 주변에서 타워 야경을 즐깁니다."},
            ],
        },
        "c06": {
            "title": "동대문·대학로 코스",
            "summary": "낙산공원 전망에서 시작해 대학로·DDP·동대문 쇼핑, 광장시장과 청계천으로 이어지는 동북~도심 코스.",
            "route": "낙산공원 → 대학로 → DDP → 동대문 → 광장시장 → 청계천",
            "tips": "낙산공원은 성곽길을 따라 걸어보세요. DDP는 저녁 조명도 아름답습니다.",
            "stops": [
                {"name": "낙산공원", "desc": "한양도성 성곽과 서울 도심 전망. 오전 빛이 부드러워 사진에 좋습니다."},
                {"name": "이화마을·대학로", "desc": "벽화마을과 대학로의 소극장·카페 거리를 산책합니다."},
                {"name": "대학로 점심", "desc": "학생가가 많아 가성비 식당이 풍부합니다. 돈가스·국밥·세계음식이 많아요."},
                {"name": "동대문 이동", "desc": "지하철이나 버스로 DDP·동대문 일대 이동."},
                {"name": "DDP", "desc": "동대문디자인플라자의 곡선 건축과 전시·이벤트 공간을 구경합니다."},
                {"name": "동대문 쇼핑", "desc": "패션·소품·야시장 감성을 즐깁니다. 낮에도 쇼핑몰은 영업합니다."},
                {"name": "광장시장 저녁", "desc": "시장 먹거리로 든든한 저녁. 주말 저녁은 붐비니 일찍 가세요."},
                {"name": "청계천", "desc": "야경 산책으로 하루를 마무리합니다."},
            ],
        },
        "c07": {
            "title": "한강·여의도 코스",
            "summary": "더현대서울에서 쇼핑 후 여의도한강공원에서 휴식·유람선·야경까지 즐기는 한강 특화 코스.",
            "route": "더현대서울 → 여의도공원 → 여의도한강공원 → 한강 야경",
            "tips": "한강 유람선은 사전 예약이 안전합니다. 피크닉 매트를 준비하면 좋습니다.",
            "stops": [
                {"name": "여의도 더현대서울", "desc": "대형 쇼핑몰과 휴식 공간. 오전부터 천천히 둘러보세요."},
                {"name": "점심", "desc": "몰 안 레스토랑이나 여의도 직장가 식당에서 식사합니다."},
                {"name": "여의도 한강공원", "desc": "넓은 잔디와 자전거 도로. 자전거 대여 후 한강변을 달려보세요."},
                {"name": "한강 카페·휴식", "desc": "공원 카페나 편의점에서 음료를 들고 강바람을  Deleg니다."},
                {"name": "유람선 또는 산책", "desc": "유람선으로 한강을 보거나, 일몰까지 천천히 산책합니다."},
                {"name": "여의도 저녁", "desc": "여의도나 국회의사당 인근에서 저녁 식사."},
                {"name": "한강 야경", "desc": "다리 조명과 강물 야경을 보며 마무리합니다."},
            ],
        },
        "c08": {
            "title": "서촌·광화문 코스",
            "summary": "경복궁과 서촌 골목의 한옥·카페, 광화문광장과 청계천·을지로까지 이어지는 도심 문화 코스.",
            "route": "경복궁 → 서촌 → 광화문 → 청계천 → 을지로",
            "tips": "서촌은 북촌보다 한산한 편입니다. 골목 카페는 좌석이 적어 웨이팅이 생길 수 있어요.",
            "stops": [
                {"name": "경복궁", "desc": "오전 개장 직후 입장하면 여유롭습니다. 영추문·광화문 동선을 미리 확인하세요."},
                {"name": "서촌", "desc": "통인동·옥인동 한옥골목과 공방·갤러리를 산책합니다."},
                {"name": "서촌 점심", "desc": "전통주점·한식·카페 브런치 중 취향껏. 좁은 골목 안쪽이 분위기 좋습니다."},
                {"name": "카페·골목 산책", "desc": "디저트 카페와 소품샵을 들르며 천천히 걷습니다."},
                {"name": "광화문광장", "desc": "광화문과 세종대왕·이순신 동상, 광장 분수대를 둘러봅니다."},
                {"name": "청계천", "desc": "광화문에서 이어지는 물길 산책. 을지로 방향으로 자연스럽게 이동할 수 있습니다."},
                {"name": "을지로", "desc": "인쇄골목·노포·힙한 바가 공존하는 거리. 골목 탐방에 좋습니다."},
                {"name": "을지로 저녁", "desc": "노포 한식이나 칵테일바로 하루를 마무리합니다."},
            ],
        },
        "c09": {
            "title": "이태원·한남 코스",
            "summary": "한남의 세련된 카페·편집숍에서 이태원·경리단길·해방촌으로 이어지는 국제적이고 감각적인 코스.",
            "route": "한남동 → 이태원 → 경리단길 → 해방촌 → 남산",
            "tips": "구릉이 많아 편한 신발을 신으세요. 저녁 이태원은 활기차지만 주말은 붐빕니다.",
            "stops": [
                {"name": "한남동", "desc": "고급 카페·갤러리·편집숍이 모인 동네. 오전~낮 분위기가 좋습니다."},
                {"name": "한남동 점심", "desc": "브런치·세계요리 레스토랑이 많아요. 예약을 추천합니다."},
                {"name": "카페·편집숍", "desc": "디자인 숍과 카페를 천천히 순회합니다."},
                {"name": "이태원", "desc": "다국적 거리와 상점. 쇼핑과 사람 구경을 즐기세요."},
                {"name": "경리단길", "desc": "언덕길 카페와 레스토랑. 경치 좋은 테라스석을 노려보세요."},
                {"name": "해방촌 저녁", "desc": "개성 있는 식당과 바가 많은 골목. 저녁 식사로 인기입니다."},
                {"name": "남산 주변 야경", "desc": "남산 아래나 전망 포인트에서 서울 야경을 감상합니다."},
            ],
        },
        "c10": {
            "title": "전통시장·먹거리 중심 코스",
            "summary": "남대문·광장시장을 축으로 명동·익선동·종로·청계천을 잇는 먹거리 특화 코스입니다.",
            "route": "남대문시장 → 명동 → 광장시장 → 익선동 → 종로 → 청계천",
            "tips": "시장은 현금·카드 모두 되는 곳이 많지만, 작은 포장마차는 현금이 편할 수 있습니다.",
            "stops": [
                {"name": "남대문시장", "desc": "오전부터 활기찬 시장. 칼국수·갈치·주전부리를 먼저 맛보세요."},
                {"name": "시장 점심", "desc": "시장 안 식당에서 든든한 한끼. 공유 테이블이 흔한 편입니다."},
                {"name": "명동", "desc": "쇼핑과 길거리 간식으로 소화 산책. 디저트·호떡도 추천."},
                {"name": "광장시장", "desc": "두 번째 시장 라운드. 육회·빈대떡·모듬전을 나눠 먹어요."},
                {"name": "익선동", "desc": "한옥 골목에서 카페·디저트로 휴식."},
                {"name": "종로 저녁", "desc": "종로·익선 인근에서 저녁. 이자카야·한식 주점이 많습니다."},
                {"name": "청계천", "desc": "식후 산책으로 가볍게 마무리."},
            ],
        },
        "c11": {
            "title": "잠실·송리단길 코스",
            "summary": "롯데월드몰과 석촌호수, 송리단길 카페, 서울스카이로 이어지는 잠실 집중 코스.",
            "route": "롯데월드몰 → 석촌호수 → 송리단길 → 서울스카이",
            "tips": "송리단길은 석촌호수 동쪽에 있습니다. 호수 한 바퀴 + 카페가 좋은 조합입니다.",
            "stops": [
                {"name": "롯데월드몰", "desc": "오전 쇼핑과 실내 관람. 아쿠아리움도 선택지입니다."},
                {"name": "점심", "desc": "몰 푸드홀이나 인근 식당에서 식사."},
                {"name": "석촌호수", "desc": "호수 산책과 타워 뷰 사진. 계절마다 풍경이 달라집니다."},
                {"name": "송리단길 카페", "desc": "감성 카페·맛집 골목. 여유롭게 디저트를 즐기세요."},
                {"name": "서울스카이", "desc": "전망대에서 서울·한강 전경. 해 질 녘 입장 추천."},
                {"name": "잠실 저녁", "desc": "몰이나 잠실역 일대에서 저녁을 먹고 마무리."},
            ],
        },
        "c12": {
            "title": "한강·반포 코스",
            "summary": "고속터미널·파미에스테이션에서 시작해 세빛섬·반포한강공원의 피크닉과 야경·분수를 즐기는 코스.",
            "route": "고속터미널 → 세빛섬 → 반포한강공원",
            "tips": "반포 달빛무지개분수는 계절·시간에 따라 운영됩니다. 당일 일정을 미리 확인하세요.",
            "stops": [
                {"name": "고속터미널·파미에스테이션", "desc": "쇼핑몰과 성당·카페가 모인 복합공간에서 오전을 시작합니다."},
                {"name": "점심", "desc": "터미널·신세계 백화점 식당가에서 식사."},
                {"name": "세빛섬", "desc": "한강 위 인공섬. 외관 사진과 카페·레스토랑이 있습니다."},
                {"name": "반포한강공원", "desc": "자전거·산책·피크닉의 명소. 돗자리 대여/편의점도 가깝습니다."},
                {"name": "한강 피크닉", "desc": "간식과 음료를 준비해 석양까지 여유롭게."},
                {"name": "야경·분수 관람", "desc": "다리 야경과 분수 쇼(운영 시)를 보며 마무리합니다."},
            ],
        },
        "c13": {
            "title": "용산·이촌 코스",
            "summary": "국립중앙박물관에서 용리단길 카페·쇼핑, 이촌한강공원까지 이어지는 여유로운 문화·산책 코스.",
            "route": "국립중앙박물관 → 용산 → 용리단길 → 이촌한강공원",
            "tips": "박물관은 규모가 커서 하이라이트만 골라 보세요. 월요일 휴관인 전시가 있으니 확인 필수.",
            "stops": [
                {"name": "국립중앙박물관", "desc": "한국사·미술 전시를 관람. 야외 정원도 산책하기 좋습니다."},
                {"name": "용산 점심", "desc": "용산역·아이파크몰 식당가에서 식사."},
                {"name": "용리단길", "desc": "용산 전자상가 인근의 카페·맛집 거리. 감각적인 공간이 많아요."},
                {"name": "카페·쇼핑", "desc": "카페 투어와 소품·패션 쇼핑."},
                {"name": "이촌한강공원", "desc": "한강변 산책과 자전거. 일몰이 예쁜 구간입니다."},
                {"name": "용산 저녁", "desc": "용산·이태원 쪽으로 이동해 저녁을 즐깁니다."},
            ],
        },
        "c14": {
            "title": "북서울·성북동 코스",
            "summary": "성북동 한옥·언덕 산책과 길상사, 북정마을 카페를 거쳐 대학로에서 저녁을 먹는 조용한 문화 코스.",
            "route": "성북동 → 길상사 → 북정마을 → 대학로",
            "tips": "성북동은 경사가 있습니다. 편한 신발과 여유 있는 일정을 추천합니다.",
            "stops": [
                {"name": "한성대입구", "desc": "성북동 진입 거점. 버스나 택시로 성북동 골목으로 이동합니다."},
                {"name": "성북동 산책", "desc": "대사관·한옥·돌담길이 이어지는 한적한 동네를 걷습니다."},
                {"name": "점심", "desc": "성북동·혜화 인근 식당에서 한끼."},
                {"name": "길상사", "desc": "도심 속 고즈넉한 사찰. 산책과 명상에 좋습니다."},
                {"name": "북정마을·카페", "desc": "전망 좋은 언덕 마을과 카페. 사진 포인트가 많아요."},
                {"name": "대학로", "desc": "소극장과 거리 공연, 카페를 구경합니다."},
                {"name": "대학로 저녁", "desc": "다양한 가격대의 식당에서 저녁을 먹고 마무리."},
            ],
        },
        "c15": {
            "title": "서울숲·한강·압구정 코스",
            "summary": "서울숲·성수의 감성에서 압구정로데오·도산공원으로 넘어가 트렌디한 저녁을 즐기는 코스.",
            "route": "서울숲 → 성수 → 압구정로데오 → 도산공원",
            "tips": "성수→압구정은 지하철·택시 모두 무난합니다. 도산공원 일대는 저녁 레스토랑 예약이 유리합니다.",
            "stops": [
                {"name": "서울숲", "desc": "오전 산책과 사진. 성수로 이어지는 좋은 출발점입니다."},
                {"name": "성수 점심", "desc": "성수 맛집에서 브런치·런치."},
                {"name": "성수 카페·쇼핑", "desc": "카페와 팝업·편집숍을 둘러봅니다."},
                {"name": "압구정로데오", "desc": "패션·뷰티·카페가 밀집한 거리. 쇼윈도 쇼핑에 좋습니다."},
                {"name": "도산공원", "desc": "공원 산책과 주변 갤러리·카페."},
                {"name": "압구정 저녁", "desc": "세련된 레스토랑·바에서 하루를 마무리합니다."},
            ],
        },
    },
}

EN = {
    "pickLabel": "Seoul curated courses",
    "intro": "Ready-made day itineraries for Seoul. Pick a title to see the timetable, photos, and walking route.",
    "routeLabel": "Route at a glance",
    "tipsLabel": "Tips",
    "openCourse": "View course",
    "courses": {
        "c01": {
            "title": "Gyeongbokgung · Bukchon · Insadong",
            "summary": "A classic Seoul day: palace grounds, hanok alleys, Insadong crafts, Ikseon café vibes, Gwangjang snacks, and a Cheonggyecheon stroll.",
            "route": "Gyeongbokgung → Bukchon → Insadong → Ikseondong → Gwangjang Market → Cheonggyecheon",
            "tips": "Wearing hanbok often means free palace entry. Bukchon is residential—keep voices down and be mindful when photographing.",
            "stops": [
                {"name": "Gyeongbokgung Palace", "desc": "Tour Geunjeongjeon and Gyeonghoeru at an easy pace. Hanbok rental makes photos and entry smoother."},
                {"name": "Bukchon Hanok Village", "desc": "Walk the tiled rooftops and viewpoint alleys of Gahoe-dong. Core lanes take 30–40 minutes."},
                {"name": "Lunch in Insadong", "desc": "Tea houses, bibimbap, and Korean set menus. Ssamziegil often has shorter waits inside."},
                {"name": "Ssamziegil & Insadong street", "desc": "Browse crafts, souvenirs, and street snacks along gallery-lined alleys."},
                {"name": "Ikseondong café", "desc": "Hanok cafés and bakeries for an afternoon dessert break."},
                {"name": "Gwangjang Market", "desc": "Try mayak gimbap, bindaetteok, and yukhoe—share a few plates before dinner hours get packed."},
                {"name": "Cheonggyecheon walk", "desc": "End with an easy waterside walk and night lights."},
            ],
        },
        "c02": {
            "title": "Myeongdong · Namsan · City center",
            "summary": "Shopping plus skyline views: Myeongdong, Namsan & N Seoul Tower, Namdaemun Market, then Seoullo 7017.",
            "route": "Myeongdong → Namsan → N Seoul Tower → Namdaemun Market → Seoul Station / Seoullo",
            "tips": "Sunset and night views at N Seoul Tower are popular—budget time for cable car or bus queues.",
            "stops": [
                {"name": "Myeongdong shopping", "desc": "Beauty, fashion, and street food. Right after opening is calmer."},
                {"name": "Lunch in Myeongdong", "desc": "From kalguksu to global chains—try side alleys if main streets are packed."},
                {"name": "Namsan walk", "desc": "Take the loop road or walk up toward the tower; on clear days walking is enough."},
                {"name": "N Seoul Tower", "desc": "City panorama from the observatory—golden hour is great for photos."},
                {"name": "Namdaemun Market", "desc": "Clothes, household goods, and market meals like grilled fish or noodles."},
                {"name": "Seoul Station · Seoullo 7017", "desc": "Pause on the elevated park for skyline views around sunset."},
                {"name": "Dinner in Myeongdong or Euljiro", "desc": "Return to Myeongdong or chase neon alleys and old-school eateries in Euljiro."},
            ],
        },
        "c03": {
            "title": "Seongsu · Seoul Forest",
            "summary": "Green park mornings, Seongsu cafés and pop-ups, then Hangang vibes and a Konkuk University area night.",
            "route": "Seoul Forest → Seongsu → Ttukseom Hangang Park → Konkuk Univ. area",
            "tips": "Weekend afternoons in Seongsu are crowded—go early or on weekdays for cafés.",
            "stops": [
                {"name": "Seoul Forest", "desc": "Start on the lawns and paths; bike rentals are available."},
                {"name": "Seongsu café streets", "desc": "Converted warehouses, bakeries, and concept stores near Seongsu Station."},
                {"name": "Lunch in Seongsu", "desc": "Brunch and casual kitchens—arrive early for popular spots."},
                {"name": "Pop-ups & shops", "desc": "Seasonal pop-ups and design stores; check what’s on before you go."},
                {"name": "Ttukseom Hangang Park", "desc": "Nearby river park for bikes, picnics, and sunset photos."},
                {"name": "Dinner near Konkuk Univ.", "desc": "Casual chicken, gopchang, and Asian eats around the station."},
                {"name": "Konkuk streets at night", "desc": "Wander the lit shopping streets to wrap up."},
            ],
        },
        "c04": {
            "title": "Hongdae · Yeonnam · Mangwon",
            "summary": "Yeonnam alleys, Hongdae street energy, Mangwon Market snacks, and Hangang sunset—then back to Hongdae nightlife.",
            "route": "Yeonnam → Hongdae → Mangwon Market → Mangwon Hangang Park → Hongdae",
            "tips": "Hongdae peaks at night. Use station lockers if you’re carrying shopping bags.",
            "stops": [
                {"name": "Yeonnam-dong", "desc": "Quiet cafés and shops; add Gyeongui Line Forest Park if you like a green walk."},
                {"name": "Lunch in Yeonnam", "desc": "Brunch spots fill up on weekends—aim for opening time."},
                {"name": "Hongdae streets", "desc": "Busking, murals, and street fashion—easy to lose track of time."},
                {"name": "Cafés & shopping", "desc": "Vintage, beauty, and lifestyle stores with coffee breaks in between."},
                {"name": "Mangwon Market", "desc": "Local market bites—pack some snacks for the river if you like."},
                {"name": "Mangwon Hangang Park", "desc": "Sunset breeze, bikes, and picnic vibes."},
                {"name": "Hongdae night", "desc": "Return for dinner, neon streets, and nightlife."},
            ],
        },
        "c05": {
            "title": "Gangnam · Jamsil",
            "summary": "COEX and Starfield Library, Bongeunsa Temple, then Seokchon Lake, Lotte World Mall, and Seoul Sky.",
            "route": "COEX → Bongeunsa → Seokchon Lake → Lotte World Mall → Seoul Sky",
            "tips": "COEX to Bongeunsa is a short walk. Book Seoul Sky for night views if you can.",
            "stops": [
                {"name": "COEX", "desc": "Mall, aquarium, and indoor events—good weather backup."},
                {"name": "Starfield Library", "desc": "Iconic book-wall photo stop; a short visit is enough."},
                {"name": "Lunch in Gangnam", "desc": "Food court or nearby restaurants before the temple."},
                {"name": "Bongeunsa", "desc": "A calm temple framed by glass towers."},
                {"name": "Transfer to Jamsil", "desc": "About 15–25 minutes on Line 2 toward Jamsil/Seokchon."},
                {"name": "Seokchon Lake", "desc": "Lakeside walk with Lotte Tower in the background."},
                {"name": "Lotte World Mall", "desc": "Shopping, aquarium, and easy dinner options under one roof."},
                {"name": "Seoul Sky or Jamsil night view", "desc": "Observatory views—or enjoy the tower lights from the lake."},
            ],
        },
        "c06": {
            "title": "Dongdaemun · Daehangno",
            "summary": "Naksan views, Daehangno theater streets, DDP architecture, Dongdaemun shopping, then Gwangjang and Cheonggyecheon.",
            "route": "Naksan Park → Daehangno → DDP → Dongdaemun → Gwangjang Market → Cheonggyecheon",
            "tips": "Walk the fortress wall at Naksan. DDP looks especially good after dark.",
            "stops": [
                {"name": "Naksan Park", "desc": "City views along the old city wall—soft morning light is lovely."},
                {"name": "Ihwa Mural Village · Daehangno", "desc": "Murals plus indie theaters and café streets."},
                {"name": "Lunch in Daehangno", "desc": "Student-friendly prices: cutlets, soups, and global casual food."},
                {"name": "Transfer to Dongdaemun", "desc": "Subway or bus toward DDP and the fashion district."},
                {"name": "DDP", "desc": "Explore the curved design plaza and any open exhibitions."},
                {"name": "Dongdaemun shopping", "desc": "Fashion malls by day; night-market energy after dark."},
                {"name": "Dinner at Gwangjang Market", "desc": "Market classics for a hearty evening—go early on weekends."},
                {"name": "Cheonggyecheon", "desc": "Night stroll to finish."},
            ],
        },
        "c07": {
            "title": "Hangang · Yeouido",
            "summary": "Shop The Hyundai Seoul, then spend the afternoon on Yeouido Hangang Park with bikes, a cruise option, and night views.",
            "route": "The Hyundai Seoul → Yeouido Park → Yeouido Hangang Park → Hangang night view",
            "tips": "Reserve river cruises ahead. A picnic mat makes the park much more comfortable.",
            "stops": [
                {"name": "The Hyundai Seoul", "desc": "A huge lifestyle mall—start slow in the morning."},
                {"name": "Lunch", "desc": "Mall restaurants or Yeouido business-district kitchens."},
                {"name": "Yeouido Hangang Park", "desc": "Grass, bike paths, and skyline views—rent a bike if you can."},
                {"name": "Café break by the river", "desc": "Coffee from a park café or convenience store, then sit by the water."},
                {"name": "Cruise or long walk", "desc": "Take a Hangang cruise or simply walk until sunset."},
                {"name": "Dinner in Yeouido", "desc": "Eat near the park or National Assembly area."},
                {"name": "Hangang night view", "desc": "Bridge lights reflecting on the river."},
            ],
        },
        "c08": {
            "title": "Seochon · Gwanghwamun",
            "summary": "Palace morning, Seochon hanok cafés, Gwanghwamun Square, then Cheonggyecheon and Euljiro alleys.",
            "route": "Gyeongbokgung → Seochon → Gwanghwamun → Cheonggyecheon → Euljiro",
            "tips": "Seochon is usually quieter than Bukchon. Tiny cafés may have waits.",
            "stops": [
                {"name": "Gyeongbokgung", "desc": "Arrive at opening for lighter crowds; check gate routes in advance."},
                {"name": "Seochon", "desc": "Tongin/Okin hanok lanes with workshops and galleries."},
                {"name": "Lunch in Seochon", "desc": "Korean homes-style spots and café brunch tucked in alleys."},
                {"name": "Café alley stroll", "desc": "Dessert stops and craft shops at a slow pace."},
                {"name": "Gwanghwamun Square", "desc": "Gate views, statues, and the open plaza."},
                {"name": "Cheonggyecheon", "desc": "Follow the stream toward Euljiro."},
                {"name": "Euljiro", "desc": "Print shops, old diners, and trendy bars share the same alleys."},
                {"name": "Dinner in Euljiro", "desc": "Classic Korean taverns or cocktail bars to close the day."},
            ],
        },
        "c09": {
            "title": "Itaewon · Hannam",
            "summary": "Hannam’s polished cafés and boutiques, then Itaewon, Gyeongnidan-gil, Haebangchon dinner, and Namsan night views.",
            "route": "Hannam → Itaewon → Gyeongnidan-gil → Haebangchon → Namsan",
            "tips": "Expect hills—wear comfortable shoes. Weekends get busy after dark.",
            "stops": [
                {"name": "Hannam-dong", "desc": "Upscale cafés, galleries, and concept stores—best by day."},
                {"name": "Lunch in Hannam", "desc": "Brunch and global restaurants; reservations help."},
                {"name": "Cafés & boutiques", "desc": "Design shopping with coffee breaks."},
                {"name": "Itaewon", "desc": "International streets for people-watching and shopping."},
                {"name": "Gyeongnidan-gil", "desc": "Hillside cafés with terrace views."},
                {"name": "Dinner in Haebangchon", "desc": "Characterful restaurants and bars in steep alleys."},
                {"name": "Namsan night views", "desc": "Catch the skyline from Namsan’s lower paths or viewpoints."},
            ],
        },
        "c10": {
            "title": "Markets & food trail",
            "summary": "A food-first day linking Namdaemun, Myeongdong, Gwangjang, Ikseon, Jongno, and Cheonggyecheon.",
            "route": "Namdaemun Market → Myeongdong → Gwangjang Market → Ikseondong → Jongno → Cheonggyecheon",
            "tips": "Most stalls take cards, but tiny stands may prefer cash.",
            "stops": [
                {"name": "Namdaemun Market", "desc": "Start with market energy—noodles and small bites work well."},
                {"name": "Market lunch", "desc": "Sit-down market restaurants; shared tables are common."},
                {"name": "Myeongdong", "desc": "Digest with shopping and street desserts."},
                {"name": "Gwangjang Market", "desc": "Round two: yukhoe, bindaetteok, and savory pancakes."},
                {"name": "Ikseondong", "desc": "Hanok cafés for a sweet pause."},
                {"name": "Dinner in Jongno", "desc": "Izakaya-style and Korean pubs near Jongno/Ikseon."},
                {"name": "Cheonggyecheon", "desc": "A light after-dinner walk."},
            ],
        },
        "c11": {
            "title": "Jamsil · Songridan-gil",
            "summary": "Lotte World Mall, Seokchon Lake, Songridan-gil cafés, and Seoul Sky—all in the Jamsil cluster.",
            "route": "Lotte World Mall → Seokchon Lake → Songridan-gil → Seoul Sky",
            "tips": "Songridan-gil sits on the east side of the lake—pair a full lake loop with café time.",
            "stops": [
                {"name": "Lotte World Mall", "desc": "Morning shopping and indoor attractions."},
                {"name": "Lunch", "desc": "Food hall or nearby restaurants."},
                {"name": "Seokchon Lake", "desc": "Scenic walk with tower views; beautiful in every season."},
                {"name": "Songridan-gil cafés", "desc": "Trendy cafés and dessert spots."},
                {"name": "Seoul Sky", "desc": "Observatory views—enter near sunset if possible."},
                {"name": "Dinner in Jamsil", "desc": "Eat back at the mall or around Jamsil Station."},
            ],
        },
        "c12": {
            "title": "Hangang · Banpo",
            "summary": "Express Bus Terminal & Seorae village vibes, Some Sevit, Banpo Hangang Park picnic, and fountain/night lights.",
            "route": "Express Bus Terminal → Some Sevit → Banpo Hangang Park",
            "tips": "The Banpo Moonlight Rainbow Fountain schedule changes by season—check before you go.",
            "stops": [
                {"name": "Express Bus Terminal · Parnie Station area", "desc": "Mall and café complex to start the day."},
                {"name": "Lunch", "desc": "Department-store or terminal food courts."},
                {"name": "Some Sevit", "desc": "Floating islands on the Hangang—great exterior photos."},
                {"name": "Banpo Hangang Park", "desc": "Bikes, walks, and picnics with easy convenience stores nearby."},
                {"name": "Hangang picnic", "desc": "Snacks and sunset on the grass."},
                {"name": "Night view & fountain", "desc": "Bridge lights and the fountain show when operating."},
            ],
        },
        "c13": {
            "title": "Yongsan · Ichon",
            "summary": "National Museum of Korea, Yongsan lunch, Yongridan-gil cafés, then Ichon Hangang Park.",
            "route": "National Museum of Korea → Yongsan → Yongridan-gil → Ichon Hangang Park",
            "tips": "The museum is huge—pick highlights. Check closed days for special exhibits.",
            "stops": [
                {"name": "National Museum of Korea", "desc": "History and art collections plus outdoor gardens."},
                {"name": "Lunch in Yongsan", "desc": "Yongsan Station / I’Park Mall dining options."},
                {"name": "Yongridan-gil", "desc": "Cafés and restaurants near the electronics market area."},
                {"name": "Cafés & shopping", "desc": "Slow café hopping and lifestyle stores."},
                {"name": "Ichon Hangang Park", "desc": "River walk and bikes with soft sunset light."},
                {"name": "Dinner in Yongsan", "desc": "Stay in Yongsan or drift toward Itaewon for dinner."},
            ],
        },
        "c14": {
            "title": "Northern Seoul · Seongbuk-dong",
            "summary": "Quiet Seongbuk-dong lanes, Gilseongsa Temple, Bukjeong village cafés, then dinner in Daehangno.",
            "route": "Seongbuk-dong → Gilseongsa → Bukjeong Village → Daehangno",
            "tips": "Expect slopes—comfortable shoes and a relaxed pace help.",
            "stops": [
                {"name": "Hansung Univ. Station area", "desc": "Gateway toward Seongbuk-dong by bus or taxi."},
                {"name": "Seongbuk-dong stroll", "desc": "Stone walls, embassies, and quiet hanok streets."},
                {"name": "Lunch", "desc": "Eat in Seongbuk-dong or nearby Hyehwa."},
                {"name": "Gilseongsa", "desc": "A peaceful temple pocket in the city."},
                {"name": "Bukjeong Village · cafés", "desc": "Hill views and photo-friendly café corners."},
                {"name": "Daehangno", "desc": "Theaters, street performers, and cafés."},
                {"name": "Dinner in Daehangno", "desc": "Plenty of casual restaurants to end the day."},
            ],
        },
        "c15": {
            "title": "Seoul Forest · Hangang · Apgujeong",
            "summary": "From Seoul Forest and Seongsu into Apgujeong Rodeo and Dosan Park for a polished evening.",
            "route": "Seoul Forest → Seongsu → Apgujeong Rodeo → Dosan Park",
            "tips": "Seongsu to Apgujeong is an easy subway/taxi hop. Book dinner around Dosan if you’re set on a popular spot.",
            "stops": [
                {"name": "Seoul Forest", "desc": "Morning walk and photos before Seongsu fills up."},
                {"name": "Lunch in Seongsu", "desc": "Brunch or lunch at a Seongsu favorite."},
                {"name": "Seongsu cafés & shops", "desc": "Cafés, pop-ups, and concept stores."},
                {"name": "Apgujeong Rodeo", "desc": "Fashion and beauty streets for window shopping."},
                {"name": "Dosan Park", "desc": "A green pause with galleries and cafés nearby."},
                {"name": "Dinner in Apgujeong", "desc": "Stylish restaurants and bars to close the night."},
            ],
        },
    },
}


def deep_translate_from_en(en_block: dict, lang: str) -> dict:
    """Lightweight localized shells; titles/summaries translated per language table."""
    # For non-en/ko we keep EN structure but overlay title translations where provided.
    return json.loads(json.dumps(en_block))  # deep copy


TITLE_I18N = {
    "ja": {
        "c01": "景福宮・北村・仁寺洞コース",
        "c02": "明洞・南山・都心コース",
        "c03": "聖水・ソウルの森コース",
        "c04": "弘大・延南・望遠コース",
        "c05": "江南・蚕室コース",
        "c06": "東大門・大学路コース",
        "c07": "漢江・汝矣島コース",
        "c08": "西村・光化門コース",
        "c09": "梨泰院・漢南コース",
        "c10": "伝統市場・グルメコース",
        "c11": "蚕室・ソンリダンギルコース",
        "c12": "漢江・盤浦コース",
        "c13": "龍山・二村コース",
        "c14": "北ソウル・城北洞コース",
        "c15": "ソウルの森・漢江・狎鴎亭コース",
        "pickLabel": "ソウルおすすめコース",
        "intro": "ソウルを1日で巡る定番コースです。タイトルを選ぶと時間割・写真・動線が表示されます。",
        "routeLabel": "ルート一覧",
        "tipsLabel": "ヒント",
        "openCourse": "コースを見る",
    },
    "zh": {
        "c01": "景福宫·北村·仁寺洞路线",
        "c02": "明洞·南山·市中心路线",
        "c03": "圣水·首尔林路线",
        "c04": "弘大·延南·望远路线",
        "c05": "江南·蚕室路线",
        "c06": "东大门·大学路路线",
        "c07": "汉江·汝矣岛路线",
        "c08": "西村·光化门路线",
        "c09": "梨泰院·汉南路线",
        "c10": "传统市场·美食路线",
        "c11": "蚕室·松坡咖啡街路线",
        "c12": "汉江·盘浦路线",
        "c13": "龙山·二村路线",
        "c14": "北首尔·城北洞路线",
        "c15": "首尔林·汉江·狎鸥亭路线",
        "pickLabel": "首尔推荐路线",
        "intro": "精选首尔一日路线。选择标题即可查看时刻表、照片与动线。",
        "routeLabel": "路线一览",
        "tipsLabel": "小贴士",
        "openCourse": "查看路线",
    },
    "zh-Hant": {
        "c01": "景福宮·北村·仁寺洞路線",
        "c02": "明洞·南山·市中心路線",
        "c03": "聖水·首爾林路線",
        "c04": "弘大·延南·望遠路線",
        "c05": "江南·蠶室路線",
        "c06": "東大門·大學路路線",
        "c07": "漢江·汝矣島路線",
        "c08": "西村·光化門路線",
        "c09": "梨泰院·漢南路線",
        "c10": "傳統市場·美食路線",
        "c11": "蠶室·松坡咖啡街路線",
        "c12": "漢江·盤浦路線",
        "c13": "龍山·二村路線",
        "c14": "北首爾·城北洞路線",
        "c15": "首爾林·漢江·狎鷗亭路線",
        "pickLabel": "首爾推薦路線",
        "intro": "精選首爾一日路線。選擇標題即可查看時刻表、照片與動線。",
        "routeLabel": "路線一覽",
        "tipsLabel": "小提示",
        "openCourse": "查看路線",
    },
    "vi": {
        "c01": "Tour Gyeongbokgung · Bukchon · Insadong",
        "c02": "Tour Myeongdong · Namsan · trung tâm",
        "c03": "Tour Seongsu · Seoul Forest",
        "c04": "Tour Hongdae · Yeonnam · Mangwon",
        "c05": "Tour Gangnam · Jamsil",
        "c06": "Tour Dongdaemun · Daehangno",
        "c07": "Tour Hangang · Yeouido",
        "c08": "Tour Seochon · Gwanghwamun",
        "c09": "Tour Itaewon · Hannam",
        "c10": "Tour chợ truyền thống & ẩm thực",
        "c11": "Tour Jamsil · Songridan-gil",
        "c12": "Tour Hangang · Banpo",
        "c13": "Tour Yongsan · Ichon",
        "c14": "Tour Bắc Seoul · Seongbuk-dong",
        "c15": "Tour Seoul Forest · Hangang · Apgujeong",
        "pickLabel": "Tour Seoul đề xuất",
        "intro": "Lịch trình một ngày tại Seoul. Chọn tiêu đề để xem giờ, ảnh và lộ trình.",
        "routeLabel": "Lộ trình tổng quan",
        "tipsLabel": "Mẹo",
        "openCourse": "Xem tour",
    },
    "th": {
        "c01": "คอร์สเคียงบก궁·บุกชน·อินซาดง",
        "c02": "คอร์สมยองดง·นัมซาน·ใจกลางโซล",
        "c03": "คอร์สซองซู·โซลฟอเรสต์",
        "c04": "คอร์สฮงแด·ยอนนัม·มังวอน",
        "c05": "คอร์สคังนัม·ชัมชิล",
        "c06": "คอร์สดงแดมุน·แทฮังโน",
        "c07": "คอร์สฮันกัง·ยออุยโด",
        "c08": "คอร์สซอชน·ควังฮวามุน",
        "c09": "คอร์สอิแทวอน·ฮันนัม",
        "c10": "คอร์สตลาดดั้งเดิมและของกิน",
        "c11": "คอร์สชัมชิล·ซงนีดานกิล",
        "c12": "คอร์สฮันกัง·บันโพ",
        "c13": "คอร์สยงซาน·อีชน",
        "c14": "คอร์สโซลเหนือ·ซองบุกดง",
        "c15": "คอร์สโซลฟอเรสต์·ฮันกัง·อัปกูจอง",
        "pickLabel": "คอร์สโซลแนะนำ",
        "intro": "ตารางเที่ยวโซลแบบวันเดียว เลือกชื่อคอร์สเพื่อดูเวลา รูป และเส้นทาง",
        "routeLabel": "เส้นทางโดยรวม",
        "tipsLabel": "เคล็ดลับ",
        "openCourse": "ดูคอร์ส",
    },
    "ru": {
        "c01": "Маршрут Кёнбоккун · Пукчхон · Инсадон",
        "c02": "Маршрут Мёндон · Намсан · центр",
        "c03": "Маршрут Сонсу · Seoul Forest",
        "c04": "Маршрут Хондэ · Ённам · Манвон",
        "c05": "Маршрут Каннам · Чамсиль",
        "c06": "Маршрут Тондэмун · Тэханно",
        "c07": "Маршрут Ханган · Йоидо",
        "c08": "Маршрут Сочхон · Кванхвамун",
        "c09": "Маршрут Итхевон · Ханнам",
        "c10": "Маршрут рынков и еды",
        "c11": "Маршрут Чамсиль · Соннидан-гиль",
        "c12": "Маршрут Ханган · Панпхо",
        "c13": "Маршрут Йонсан · Ичхон",
        "c14": "Маршрут север Сеула · Сонбуктон",
        "c15": "Маршрут Seoul Forest · Ханган · Апкучжон",
        "pickLabel": "Рекомендуемые маршруты Сеула",
        "intro": "Готовые однодневные маршруты по Сеулу. Выберите название, чтобы увидеть расписание, фото и путь.",
        "routeLabel": "Маршрут кратко",
        "tipsLabel": "Советы",
        "openCourse": "Смотреть маршрут",
    },
}


def build_lang_block(base: dict, lang: str) -> dict:
    if lang == "ko":
        return base
    if lang == "en":
        return EN
    meta = TITLE_I18N[lang]
    out = json.loads(json.dumps(EN))
    out["pickLabel"] = meta["pickLabel"]
    out["intro"] = meta["intro"]
    out["routeLabel"] = meta["routeLabel"]
    out["tipsLabel"] = meta["tipsLabel"]
    out["openCourse"] = meta["openCourse"]
    for cid, title in meta.items():
        if cid.startswith("c") and cid in out["courses"]:
            out["courses"][cid]["title"] = title
    return out


def main() -> None:
    # 1) JS data file
    js_path = ROOT / "data" / "courses" / "seoul-curated.js"
    payload = {"courses": COURSES}
    js = (
        "/** Seoul curated day courses — structure only; copy in i18n travelCourses.seoulCurated */\n"
        "window.SEOUL_CURATED_COURSES = "
        + json.dumps(COURSES, ensure_ascii=False, indent=2)
        + ";\n"
    )
    js_path.write_text(js, encoding="utf-8")
    print("wrote", js_path)

    # 2) merge into each travel-courses lang json
    for lang in ["ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru"]:
        path = ROOT / "i18n" / "pages" / "travel-courses" / f"{lang}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        block = build_lang_block(KO, lang)
        data["travelCourses"]["seoulCurated"] = block
        # Soften intro for hub
        if lang == "ko":
            data["travelCourses"]["intro"] = (
                "지역별 추천 코스와 실시간 맞춤 추천을 한곳에서 확인하세요."
            )
        elif lang == "en":
            data["travelCourses"]["intro"] = (
                "Browse curated regional courses and get a live personalized itinerary."
            )
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("updated i18n", lang)


if __name__ == "__main__":
    main()
