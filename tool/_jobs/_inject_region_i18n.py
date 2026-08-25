# -*- coding: utf-8 -*-
"""Insert travelCourses.curated.{gangwon,chungcheong,jeolla,gyeongsang,busan,jeju} into locale JSON."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "i18n" / "pages" / "travel-courses"


def S(*pairs):
    return [{"name": n, "desc": d} for n, d in pairs]


def C(title, summary, route, tips, stops, notice=None):
    out = {
        "title": title,
        "summary": summary,
        "route": route,
        "tips": tips,
        "stops": S(*stops),
    }
    if notice:
        out["notice"] = notice
    return out


KO = {
    "gangwon": {
        "pickLabel": "강원도 추천 코스",
        "intro": "설악산·속초·강릉부터 춘천 남이섬, 평창 대관령, 양양, 동해·삼척, 철원까지 강원을 하루로 도는 코스입니다. 타이틀을 고르면 소개·동선·시간표가 펼쳐집니다.",
        "guideEyebrow": "강원도 코스 안내",
        "courses": {
            "c01": C("속초·설악산 대표 코스", "설악산과 권금성에서 하루를 열고, 속초관광수산시장·해수욕장·외옹치 바다향기로를 거쳐 대포항으로 닫는 강원 1순위 코스입니다.", "설악산 → 속초시장 → 속초해변 → 외옹치 → 대포항", "케이블카는 대기·운휴를 확인하세요. 시장은 점심에 붐빕니다. 외옹치 산책로는 편한 신발이 좋습니다.", [("설악산국립공원", "울산바위·소공원 일대를 걸으며 하루를 엽니다."), ("설악산 케이블카·권금성", "케이블카로 올라가 권금성 능선과 동해를 봅니다."), ("속초관광수산시장", "시장에서 회·핫바 등 속초 별미로 점심을 먹습니다."), ("속초해수욕장", "동해 해변을 따라 산책합니다."), ("외옹치 바다향기로", "해안 산책로에서 파도와 기암을 봅니다."), ("대포항", "항구 풍경과 저녁 식사로 하루를 닫습니다.")]),
            "c02": C("강릉 바다·카페 코스", "경포호와 경포해변, 중앙시장, 안목 커피거리, 강문해변으로 이어지는 바다·카페 하루입니다. 역사 관광보다 동해 감성이 핵심입니다.", "경포 → 강릉 중앙시장 → 안목 → 강문", "안목은 주차·주말이 붐빕니다. 해변은 바람에 추울 수 있으니 겉옷을 챙기세요.", [("경포대·경포호", "경포호와 경포대를 천천히 둘러봅니다."), ("경포해변", "백사장과 소나무 숲 사이를 걷습니다."), ("강릉 중앙시장·점심", "시장 골목에서 강릉 먹거리로 점심을 먹습니다."), ("안목 커피거리", "바다를 보며 커피 한 잔 합니다."), ("강문해변", "경포와 이어진 해변을 더 걷습니다."), ("저녁", "해 진 뒤 강릉에서 저녁을 먹습니다.")]),
            "c03": C("춘천·남이섬 코스", "남이섬에서 시작해 춘천 닭갈비, 삼악산 호수케이블카, 의암호, 춘천 시내로 이어지는 하루입니다.", "남이섬 → 춘천 → 삼악산 케이블카 → 의암호", "남이섬은 선착장 대기를 보세요. 삼악산 케이블카는 날씨·운휴를 확인하세요.", [("남이섬", "메타세쿼이아 길을 걸으며 섬을 한 바퀴 돕니다."), ("춘천 닭갈비 점심", "춘천 시내에서 닭갈비로 든든히 식사합니다."), ("삼악산 호수케이블카", "의암호 위를 가로지르는 케이블카를 탑니다."), ("의암호", "호숫가에서 풍경을 봅니다."), ("춘천 시내", "명동·중앙시장 일대를 걷고 저녁을 먹습니다.")]),
            "c04": C("평창·대관령 코스", "대관령 양떼목장과 고원 풍경, 월정사 전나무숲길로 이어지는 자연 코스입니다. 설경·고원을 좋아하는 여행객에게 맞습니다.", "대관령 → 월정사 → 전나무숲길", "목장은 날씨와 운영 시간을 확인하세요. 월정사 숲길은 미끄러울 수 있습니다.", [("대관령 양떼목장", "고원 목장에서 양떼와 초원을 봅니다."), ("평창 점심", "대관령·전나무숲 인근에서 식사합니다."), ("대관령 일대", "고원 드라이브와 전망을 즐깁니다."), ("월정사", "오대산 월정사 경내를 둘러봅니다."), ("전나무숲길", "천년 전나무 숲길을 천천히 걷습니다.")]),
            "c05": C("양양 바다·서핑 코스", "낙산사와 낙산해변, 하조대·서피비치로 이어지는 양양 해안 하루입니다.", "낙산사 → 낙산해변 → 하조대 → 서피비치", "서핑 비치는 계절·파도에 따라 분위기가 달라집니다. 일몰 시간을 미리 보세요.", [("낙산사", "동해를 내려다보는 산사와 의상대를 봅니다."), ("양양 점심", "낙산·양양 시내에서 식사합니다."), ("낙산해변", "사찰 아래 해변을 걷습니다."), ("하조대·서피비치", "기암과 서핑 해변 풍경을 봅니다."), ("일몰·저녁", "해 질 녘 바다를 보고 저녁을 먹습니다.")]),
            "c06": C("동해·삼척 해안 코스", "추암 촛대바위와 해변, 도째비골 스카이밸리, 묵호항 논골담길로 이어지는 해안 하루입니다.", "추암 → 도째비골 → 묵호항", "스카이밸리는 높이 체험이 있으니 고소 공포를 확인하세요. 논골담길은 골목이 가파릅니다.", [("추암 촛대바위", "바다 위 촛대바위를 전망대에서 봅니다."), ("추암해변", "촛대바위 아래 해변을 걷습니다."), ("점심", "추암·묵호 인근에서 오징어·해산물로 식사합니다."), ("도째비골 스카이밸리", "해안 절벽 위 스카이워크·시설을 체험합니다."), ("묵호항·논골담길", "벽화 골목과 항구 풍경을 봅니다."), ("저녁", "묵호에서 해산물 저녁을 먹습니다.")]),
            "c07": C("철원 한탄강·DMZ 코스", "한탄강 주상절리길과 고석정, 철원 DMZ를 잇는 차량 코스입니다. 한탄강 주상절리길은 한국관광 100선에 포함됩니다.", "한탄강 → 고석정 → 철원 DMZ", "DMZ 관광은 예약·신분증·운영일이 바뀝니다. 주상절리길은 미끄럼에 주의하세요.", [("한탄강 주상절리길", "현무암 협곡 위의 잔도를 걷습니다."), ("점심", "고석정·철원 시내에서 막국수 등으로 식사합니다."), ("고석정", "한탄강 가운데 바위와 유원지를 봅니다."), ("철원 DMZ 관광", "안보 관광 코스를 안내를 따라 둘러봅니다."), ("종료", "철원에서 하루를 마치고 돌아갑니다.")]),
        },
    },
    "chungcheong": {
        "pickLabel": "충청도 추천 코스",
        "intro": "공주·부여 백제 역사부터 단양 액티비티, 보령 대천, 태안 일몰, 대전 도심까지 충청을 하루로 도는 코스입니다.",
        "guideEyebrow": "충청도 코스 안내",
        "courses": {
            "c01": C("공주 백제 역사 코스", "공산성, 산성시장, 무령왕릉과 왕릉원, 국립공주박물관, 제민천 원도심으로 이어지는 백제 대표 하루입니다.", "공산성 → 산성시장 → 무령왕릉 → 국립공주박물관 → 제민천", "왕릉원은 실내 관람 동선을 확인하세요. 공산성 성곽은 편한 신발이 좋습니다.", [("공산성", "금강이 내려다보이는 백제 왕성 성곽을 걷습니다."), ("공주 산성시장·점심", "시장 골목에서 점심을 먹습니다."), ("무령왕릉과 왕릉원", "백제 왕릉과 전시관을 둘러봅니다."), ("국립공주박물관", "무령왕릉 출토품 등 백제 유물을 봅니다."), ("제민천·공주 원도심", "제민천 물길과 원도심 골목을 걷습니다."), ("저녁", "공주 시내에서 저녁을 먹습니다.")]),
            "c02": C("부여 백제 역사 코스", "부소산성, 궁남지, 국립부여박물관, 정림사지로 이어지는 부여 하루입니다. 공주와 분위기가 달라 별도 코스로 둡니다.", "부소산성 → 궁남지 → 국립부여박물관 → 정림사지", "부소산성은 오르막이 있습니다. 궁남지는 해 질 녘 사진이 좋습니다.", [("부소산성", "백제 마지막 왕성 숲길을 걷습니다."), ("부여 점심", "부소산성 관광지 식당에서 식사합니다."), ("궁남지", "백제 별궁 연못을 한 바퀴 돕니다."), ("국립부여박물관", "백제 금동대향로 등 대표 유물을 봅니다."), ("정림사지", "오층석탑과 절터를 둘러봅니다."), ("부여 시내", "시내에서 저녁을 먹고 하루를 닫습니다.")]),
            "c03": C("단양 대표 자연·액티비티 코스", "도담삼봉, 만천하스카이워크, 단양강 잔도, 패러글라이딩 또는 카페산, 구경시장으로 이어지는 충청권 액티비티 대표 코스입니다.", "도담삼봉 → 만천하스카이워크 → 단양강 잔도 → 패러글라이딩 → 단양시장", "스카이워크·패러글라이딩은 날씨·예약이 필수입니다. 잔도는 미끄럼에 주의하세요.", [("도담삼봉", "남한강 세 봉우리를 전망대에서 봅니다."), ("만천하스카이워크", "절벽 위 유리 스카이워크를 걷습니다."), ("단양 점심", "단양읍에서 마늘·올갱이국 등으로 식사합니다."), ("단양강 잔도", "강변 절벽 산책로를 걷습니다."), ("패러글라이딩 또는 카페산", "활공 체험 또는 카페산에서 풍경을 봅니다."), ("단양구경시장", "시장 골목에서 저녁과 특산물을 봅니다.")]),
            "c04": C("보령 대천해수욕장 코스", "대천해수욕장, 해산물, 스카이바이크, 해변 카페와 일몰로 이어지는 여름 강한 서해 코스입니다. 머드축제로 외국인 인지도도 높습니다.", "대천해수욕장 → 스카이바이크 → 해변 → 일몰", "여름·축제 기간은 매우 붐빕니다. 스카이바이크는 운영 시간을 확인하세요.", [("대천해수욕장", "서해 대표 해변에서 하루를 엽니다."), ("해산물·점심", "해변 주변에서 해산물로 점심을 먹습니다."), ("대천 스카이바이크", "해안 레일을 따라 스카이바이크를 탑니다."), ("해변 카페", "바다를 보는 카페에서 쉽니다."), ("해변 산책", "해 지기 전 백사장을 걷습니다."), ("일몰", "서해 노을을 봅니다."), ("저녁", "대천에서 해산물 저녁을 먹습니다.")]),
            "c05": C("태안 서해·일몰 코스", "안면도 일대와 꽃지해수욕장, 카페·해안 산책, 꽃지 일몰로 하루를 채웁니다. 장소를 많이 찍기보다 바다와 노을이 테마입니다.", "안면도 → 꽃지해수욕장 → 서해 일몰", "꽃지 할미바위·할아비바위 일몰 포인트를 미리 보세요. 대중교통은 드뭅니다.", [("안면도 자연휴양림·꽃지 일대", "안면도 숲길 또는 꽃지 입구에서 하루를 엽니다."), ("태안 점심", "안면도·꽃지 인근에서 식사합니다."), ("꽃지해수욕장", "할미·할아비바위가 보이는 해변을 걷습니다."), ("카페·해안 산책", "해안 카페에서 쉬고 다시 걷습니다."), ("꽃지 일몰", "바위 사이로 지는 해를 봅니다."), ("저녁", "태안에서 저녁을 먹습니다.")]),
            "c06": C("대전 도심·과학 코스", "국립중앙과학관, 엑스포 한빛탑, 성심당·중앙로, 원도심으로 이어지는 대전 도심 하루입니다. 청주공항·KTX 이용객에게 맞습니다.", "국립중앙과학관 → 엑스포 → 성심당 → 대전 원도심", "성심당은 주말 줄이 깁니다. 과학관은 전시 시간을 확인하세요.", [("국립중앙과학관", "체험형 전시를 둘러봅니다."), ("대전 점심", "유성·엑스포 인근에서 칼국수 등으로 식사합니다."), ("엑스포과학공원·한빛탑", "한빛탑과 엑스포 광장을 걷습니다."), ("성심당·중앙로", "튀김소보로 등 빵을 사고 중앙로를 걷습니다."), ("대전 원도심", "은행동·대흥동 골목을 둘러봅니다."), ("저녁", "원도심에서 저녁을 먹습니다.")]),
        },
    },
    "jeolla": {
        "pickLabel": "전라도 추천 코스",
        "intro": "전주 한옥마을, 여수 밤바다, 순천만, 담양 대나무, 보성 녹차밭, 목포 근대문화까지 전라도를 하루로 도는 코스입니다.",
        "guideEyebrow": "전라도 코스 안내",
        "courses": {
            "c01": C("전주 한옥마을 코스", "한옥마을, 경기전, 비빔밥, 전동성당, 오목대, 한옥 카페, 남부시장 청년몰로 이어지는 전라도 대표 코스입니다.", "한옥마을 → 경기전 → 전동성당 → 오목대 → 남부시장", "한복 대여는 오전을 추천합니다. 주말 한옥마을은 매우 붐빕니다.", [("전주한옥마을", "한옥 골목을 천천히 걷습니다."), ("경기전", "태조 어진을 모신 전각을 둘러봅니다."), ("전주비빔밥·한식 점심", "비빔밥이나 한식으로 점심을 먹습니다."), ("전동성당", "한옥 사이 붉은 벽돌 성당을 봅니다."), ("오목대", "한옥마을이 내려다보이는 언덕에 오릅니다."), ("한옥 카페·전통체험", "한옥 카페에서 쉬거나 전통 체험을 합니다."), ("남부시장·청년몰", "야시장·청년몰을 걷습니다."), ("저녁", "전주 한식으로 하루를 닫습니다.")]),
            "c02": C("여수 바다·야경 코스", "오동도, 해산물, 해상케이블카, 돌산공원, 이순신광장, 낭만포차, 여수 밤바다로 이어지는 하루입니다.", "오동도 → 해상케이블카 → 돌산공원 → 이순신광장 → 여수 밤바다", "케이블카는 대기 시간이 깁니다. 낭만포차는 저녁 이후에 열립니다.", [("오동도", "동백 숲과 방파제를 걷습니다."), ("여수 해산물 점심", "여수 시내에서 게장·해산물로 식사합니다."), ("해상케이블카", "바다 위를 가로지르는 케이블카를 탑니다."), ("돌산공원", "여수 시내와 바다가 보이는 공원에 오릅니다."), ("이순신광장", "하멜등대와 광장을 걷습니다."), ("낭만포차거리", "포차 거리에서 분위기 있게 시간을 보냅니다."), ("여수 밤바다·야경", "조명이 켜진 바다를 보며 마무리합니다.")]),
            "c03": C("순천 자연·정원 코스", "순천만국가정원, 순천만습지, 용산전망대, 일몰로 이어지는 전라도 자연 대표 하루입니다.", "순천만국가정원 → 순천만습지 → 용산전망대", "정원과 습지는 이동 시간이 있습니다. 일몰은 용산전망대가 핵심입니다.", [("순천만국가정원", "정원과 호수정원을 천천히 걷습니다."), ("점심", "정원·습지 인근에서 식사합니다."), ("순천만습지", "갈대밭과 탐방로를 걷습니다."), ("용산전망대", "습지 전체가 내려다보이는 전망대에 오릅니다."), ("순천만 일몰", "노을 지는 습지를 봅니다."), ("순천 저녁", "순천 시내에서 저녁을 먹습니다.")]),
            "c04": C("담양 대나무·전통 코스", "죽녹원, 관방제림, 떡갈비·대통밥, 메타세쿼이아길, 카페, 메타프로방스로 이어지는 하루입니다.", "죽녹원 → 관방제림 → 메타세쿼이아길 → 메타프로방스", "메타세쿼이아길은 차량이 많으니 보행로를 이용하세요.", [("죽녹원", "대나무 숲길을 걷습니다."), ("관방제림", "강변 느티나무 숲을 걷습니다."), ("담양 떡갈비·대통밥", "담양 별미로 점심을 먹습니다."), ("메타세쿼이아길", "가로수길을 따라 사진을 찍습니다."), ("담양 카페", "숲길 인근 카페에서 쉽니다."), ("메타프로방스", "유럽풍 거리와 소품샵을 둘러봅니다."), ("종료", "담양에서 하루를 마치고 돌아갑니다.")]),
            "c05": C("보성 녹차·자연 코스", "보성 녹차밭, 녹차 카페, 율포해수욕장으로 이어지는 사진 맛집 코스입니다.", "보성 녹차밭 → 율포해수욕장", "녹차밭은 입장·촬영 규칙을 지키세요. 율포는 바람이 강할 수 있습니다.", [("보성 녹차밭", "계단식 녹차밭을 걷고 사진을 찍습니다."), ("점심", "녹차밭 관광지에서 돌솥밥 등으로 식사합니다."), ("녹차 체험·카페", "녹차 음료와 디저트를 즐깁니다."), ("율포해수욕장", "녹차밭에서 가까운 해변으로 내려갑니다."), ("해안 산책", "율포 해안을 천천히 걷습니다."), ("저녁", "보성·벌교 인근에서 저녁을 먹습니다.")]),
            "c06": C("목포 근대문화·바다 코스", "근대역사문화공간, 해상케이블카, 유달산, 갓바위·평화광장, 해산물 저녁으로 이어지는 하루입니다.", "근대역사문화거리 → 해상케이블카 → 유달산 → 평화광장", "유달산은 오르막이 있습니다. 케이블카는 날씨에 영향을 받습니다.", [("목포 근대역사문화공간", "근대 건축 거리를 걷습니다."), ("목포 점심", "목포 시내에서 국밥·한식으로 식사합니다."), ("목포 해상케이블카", "바다 위 케이블카를 탑니다."), ("유달산", "목포 시내와 다도해가 보이는 산에 오릅니다."), ("갓바위·평화광장", "해안 산책과 갓바위를 봅니다."), ("목포 해산물 저녁", "목포 수산시장·항구에서 저녁을 먹습니다.")]),
        },
    },
    "gyeongsang": {
        "pickLabel": "경상도 추천 코스",
        "intro": "경주 신라, 안동 하회, 통영·거제 바다, 포항, 대구, 울산, 해인사까지 영남을 하루로 도는 코스입니다.",
        "guideEyebrow": "경상도 코스 안내",
        "courses": {
            "c01": C("경주 신라 역사 코스", "불국사, 황리단길, 대릉원, 첨성대, 월정교, 동궁과 월지 야경으로 이어지는 경상도 최우선 코스입니다.", "불국사 → 황리단길 → 대릉원 → 첨성대 → 월정교 → 동궁과 월지", "동궁과 월지는 야간 입장이 핵심입니다. 폐장 시간을 꼭 확인하세요.", [("불국사", "유네스코 사찰을 천천히 둘러봅니다."), ("황리단길 점심", "한옥 골목에서 점심을 먹습니다."), ("대릉원", "천마총 등 고분 공원을 걷습니다."), ("첨성대", "신라 천문대를 가까이에서 봅니다."), ("교촌마을·월정교", "월정교와 교촌 한옥을 걷습니다."), ("동궁과 월지 야경", "조명이 켜진 연못으로 하루를 닫습니다.")]),
            "c02": C("안동 하회마을 전통문화 코스", "부용대, 하회마을, 하회탈박물관, 병산서원, 월영교로 이어지는 전통문화 코스입니다.", "부용대 → 하회마을 → 병산서원 → 월영교", "하회마을은 입장료가 있습니다. 병산서원은 이동에 차량이 편합니다.", [("부용대", "하회마을이 한눈에 보이는 절벽에 오릅니다."), ("하회마을", "낙동강 물돌이 마을의 한옥을 걷습니다."), ("안동 점심", "헛제삿밥·국밥으로 식사합니다."), ("하회탈박물관·탈춤", "하회탈과 공연·전시를 봅니다."), ("병산서원", "만대루와 서원 풍경을 봅니다."), ("월영교", "해 질 녘 월영교를 걷습니다."), ("저녁", "안동찜닭 등으로 저녁을 먹습니다.")]),
            "c03": C("통영 바다·전망 코스", "케이블카와 미륵산, 중앙시장, 동피랑, 강구안, 이순신공원으로 이어지는 남해 도시 하루입니다.", "케이블카·미륵산 → 중앙시장 → 동피랑 → 강구안 → 이순신공원", "케이블카 정상은 바람이 강합니다. 동피랑 골목은 가파릅니다.", [("통영 케이블카", "바다 위 케이블카를 탑니다."), ("미륵산 전망", "한려수도가 내려다보이는 정상 전망을 봅니다."), ("통영 중앙시장·점심", "충무김밥·꿀빵으로 점심을 먹습니다."), ("동피랑 벽화마을", "벽화 골목과 항구 전망을 봅니다."), ("강구안", "동피랑 아래 항구를 걷습니다."), ("이순신공원", "통제영과 바다 공원을 둘러봅니다."), ("통영 저녁", "통영 해산물로 저녁을 먹습니다.")], "외도와 달리 당일은 시내·전망 중심입니다."),
            "c04": C("거제 외도·바다 코스", "해금강, 외도 보타니아, 바람의 언덕, 신선대로 이어지는 자연·사진 코스입니다.", "해금강 → 외도 보타니아 → 바람의 언덕 → 신선대", "외도는 선박 운항이 날씨에 좌우됩니다. 당일 결항 여부를 꼭 확인하세요.", [("유람선 선착장", "장승포·외도 선착장에서 배에 오릅니다."), ("해금강", "바다 위 기암을 유람선에서 봅니다."), ("외도 보타니아", "섬 정원을 한 바퀴 걷습니다."), ("거제 점심", "외도에서 내린 뒤 거제에서 식사합니다."), ("바람의 언덕", "풍차와 언덕 위 바다 전망을 봅니다."), ("신선대", "기암과 바다가 맞닿은 전망을 봅니다."), ("거제 저녁", "거제 시내에서 저녁을 먹습니다.")], "외도 유람선은 풍랑·안개 시 결항될 수 있습니다."),
            "c05": C("포항 바다·스페이스워크 코스", "죽도시장, 영일대해수욕장, 스페이스워크, 해안 카페, 영일대 야경으로 이어지는 공식 추천과 잘 맞는 코스입니다.", "죽도시장 → 영일대 → 스페이스워크 → 해안", "스페이스워크는 높이 체험입니다. 야경은 영일대 해상누각이 포인트입니다.", [("죽도시장", "포항 대표 시장을 걷고 아침·오전을 보냅니다."), ("점심", "죽도·영일대 인근에서 식사합니다."), ("영일대해수욕장", "해변과 해상누각을 봅니다."), ("스페이스워크", "환호공원 스페이스워크를 걷습니다."), ("해안 카페", "바다를 보는 카페에서 쉽니다."), ("영일대 야경", "조명이 켜진 해변으로 하루를 닫습니다.")]),
            "c06": C("포항 호미곶·구룡포 코스", "호미곶과 구룡포 일본인가옥거리, 구룡포항으로 이어지는 포항 시내와 다른 성격의 하루입니다.", "호미곶 → 구룡포 → 구룡포항", "호미곶은 일출 명소라 오전 방문이 맞습니다. 구룡포는 골목이 좁습니다.", [("호미곶", "상생의 손과 한반도 최동단 광장을 봅니다."), ("구룡포 일본인가옥거리", "근대 가옥 거리를 걷습니다."), ("구룡포 점심", "과메기·해산물로 점심을 먹습니다."), ("구룡포항", "어항 풍경을 봅니다."), ("카페·해안", "해안 카페에서 쉽니다."), ("포항 복귀", "포항 시내로 돌아갑니다.")]),
            "c07": C("대구 전통시장·도심 코스", "서문시장, 근대문화골목, 동성로, 앞산 전망·야경으로 이어지는 로컬 도시 코스입니다.", "서문시장 → 근대골목 → 동성로 → 앞산", "서문시장은 넓으니 시간을 넉넉히 두세요. 앞산은 해 질 녘이 좋습니다.", [("서문시장", "대구 대표 시장을 걷습니다."), ("대구 먹거리 점심", "막창·따로국밥 등 대구 음식으로 식사합니다."), ("근대문화골목", "계산동 근대 골목을 둘러봅니다."), ("동성로", "대구 중심 쇼핑 거리를 걷습니다."), ("앞산 전망대", "대구 시내가 내려다보이는 전망대에 오릅니다."), ("앞산·대구 야경", "야경과 저녁으로 하루를 닫습니다.")]),
            "c08": C("울산 자연·해안 코스", "태화강 국가정원, 대왕암공원, 일산해수욕장으로 이어지는 의외의 자연 코스입니다.", "태화강 국가정원 → 대왕암공원 → 일산해수욕장", "대왕암은 산책로가 깁니다. 산업도시 편견과 다른 해안 풍경이 핵심입니다.", [("태화강 국가정원", "십리대숲과 정원을 걷습니다."), ("울산 점심", "태화강·일산 인근에서 밀면 등으로 식사합니다."), ("대왕암공원", "기암과 등대가 있는 해안 공원을 걷습니다."), ("일산해수욕장", "대왕암과 이어진 해변을 봅니다."), ("해안 산책", "해안 데크를 더 걷습니다."), ("저녁", "울산에서 저녁을 먹습니다.")]),
            "c09": C("합천 해인사 코스", "해인사, 팔만대장경, 가야산 산책으로 이어지는 불교·유네스코 특화 코스입니다.", "해인사 → 팔만대장경 → 가야산", "대장경 판전 관람 규칙을 지키세요. 산사는 저녁이 이릅니다.", [("해인사", "가야산 해인사 경내를 오릅니다."), ("점심", "산사 관광지에서 식사합니다."), ("팔만대장경·사찰 관람", "장경판전과 사찰을 안내를 따라 봅니다."), ("가야산 산책", "경내·산길을 짧게 걷습니다."), ("카페·휴식", "하산 후 카페에서 쉽니다."), ("종료", "합천에서 하루를 마치고 돌아갑니다.")]),
        },
    },
    "busan": {
        "pickLabel": "부산 추천 코스",
        "intro": "해운대·광안리, 감천·자갈치, 송도·영도, 기장 해동용궁사, 서면·전포까지 부산을 하루로 도는 코스입니다.",
        "guideEyebrow": "부산 코스 안내",
        "courses": {
            "c01": C("해운대·청사포·광안리 코스", "해운대, 동백섬, 블루라인파크·청사포, 다릿돌전망대, 광안리 야경으로 이어지는 부산 첫 방문 추천 코스입니다.", "해운대 → 동백섬 → 청사포 → 광안리", "블루라인파크는 대기·좌석을 확인하세요. 광안대교 야경은 해변에서 보기 좋습니다.", [("해운대해수욕장", "부산 대표 해변에서 하루를 엽니다."), ("동백섬·더베이101", "동백섬 산책과 마린시티 풍경을 봅니다."), ("점심", "해운대에서 밀면·회 등으로 식사합니다."), ("블루라인파크·청사포", "해변 열차로 청사포로 이동합니다."), ("청사포 다릿돌전망대", "절벽 위 전망대에서 동해를 봅니다."), ("광안리해수욕장", "광안대교가 보이는 해변으로 갑니다."), ("저녁·광안대교 야경", "다리 조명을 보며 저녁을 먹습니다.")]),
            "c02": C("감천·자갈치·남포동 코스", "감천문화마을, 자갈치시장, BIFF광장, 국제시장, 용두산공원, 남포동으로 이어지는 원도심 대표 코스입니다.", "감천문화마을 → 자갈치시장 → BIFF광장 → 국제시장 → 용두산공원 → 남포동", "감천은 가파른 골목입니다. 자갈치는 점심이 붐빕니다.", [("감천문화마을", "알록달록 골목과 전망을 봅니다."), ("자갈치시장·점심", "시장에서 회·해물로 점심을 먹습니다."), ("BIFF광장", "영화의 전당 손바닥 광장을 걷습니다."), ("국제시장", "만물시장 골목을 둘러봅니다."), ("용두산공원·부산타워", "타워와 항구 전망을 봅니다."), ("남포동", "원도심 거리를 걷습니다."), ("저녁", "남포·광복동에서 돼지국밥 등으로 저녁을 먹습니다.")]),
            "c03": C("송도·영도 해안 코스", "송도해수욕장, 해상케이블카, 암남공원, 흰여울문화마을, 영도 카페로 이어지는 해안 하루입니다.", "송도해수욕장 → 해상케이블카 → 암남공원 → 흰여울문화마을 → 영도", "케이블카는 운휴를 확인하세요. 흰여울은 골목이 좁고 가파릅니다.", [("송도해수욕장", "부산 서부 해변에서 하루를 엽니다."), ("송도 해상케이블카", "바다 위 케이블카를 탑니다."), ("점심", "송도·영도에서 국밥 등으로 식사합니다."), ("암남공원", "송도 끝 해안 공원을 걷습니다."), ("흰여울문화마을", "절벽 위 골목과 바다를 봅니다."), ("영도 해안 카페", "영도 카페에서 쉽니다."), ("저녁", "영도에서 저녁을 먹습니다.")]),
            "c04": C("기장·해동용궁사 코스", "해동용궁사, 기장 해안, 오시리아, 해안 카페, 일몰로 이어지는 바다 옆 사찰 코스입니다.", "해동용궁사 → 기장 해안 → 오시리아 → 해안 카페", "용궁사는 오전이 한산합니다. 일몰은 기장 해안이 좋습니다.", [("해동용궁사", "파도 옆 사찰을 둘러봅니다."), ("기장 해안", "용궁사 주변 기암 해안을 걷습니다."), ("해산물 점심", "기장에서 대게·회 등으로 식사합니다."), ("아난티·오시리아 일대", "리조트·쇼핑몰 단지를 걷습니다."), ("해안 카페", "바다 카페에서 쉽니다."), ("기장 바다·일몰", "해 질 녘 기장 바다를 봅니다."), ("저녁", "기장에서 저녁을 먹습니다.")]),
            "c05": C("영도 집중 코스", "태종대, 흰여울, 절영해안산책로, 영도 카페, 부산항 야경으로 이어지는 느린 바다 코스입니다.", "태종대 → 흰여울문화마을 → 절영해안산책로 → 영도 카페", "태종대 다누빔 열차와 산책로를 고르세요. 절영로는 일몰이 좋습니다.", [("태종대", "영도 끝 기암과 등대를 봅니다."), ("영도 점심", "영도에서 백반·국밥으로 식사합니다."), ("흰여울문화마을", "절벽 마을을 걷습니다."), ("절영해안산책로", "영도 남쪽 해안 데크를 걷습니다."), ("영도 카페", "바다 카페에서 쉽니다."), ("부산항 야경·저녁", "항구 조명을 보며 저녁을 먹습니다.")]),
            "c06": C("서면·전포 로컬 코스", "서면, 전포 카페거리, 편집숍, 서면 쇼핑, 저녁과 야간거리로 이어지는 생활 밀착 코스입니다.", "서면 → 전포 → 서면", "전포는 골목이 넓습니다. 야간은 서면 지하상가·거리가 붐빕니다.", [("서면", "부산의 교차로 서면에서 하루를 엽니다."), ("점심", "서면에서 밀면·국밥으로 식사합니다."), ("전포 카페거리", "카페와 작은 가게를 걷습니다."), ("소품숍·편집숍", "전포 골목의 숍을 둘러봅니다."), ("서면 쇼핑", "지하상가·백화점 쇼핑을 합니다."), ("부산 음식·저녁", "서면에서 저녁을 먹습니다."), ("서면 야간거리", "밤 서면의 네온과 거리를 걷습니다.")]),
        },
    },
    "jeju": {
        "pickLabel": "제주도 추천 코스",
        "intro": "성산·우도, 협재·애월, 서귀포 폭포, 중문, 한라산, 제주시 시장, 오름, 산방산까지 제주를 하루로 도는 코스입니다.",
        "guideEyebrow": "제주도 코스 안내",
        "courses": {
            "c01": C("성산·제주 동부 대표 코스", "성산일출봉, 섭지코지, 광치기해변으로 이어지는 동부 대표 하루입니다. 성산일출봉은 제주 대표 유네스코 자연유산입니다.", "성산일출봉 → 섭지코지 → 광치기해변", "일출봉은 오전이 한산합니다. 정상 등반은 체력을 보세요.", [("성산일출봉", "분화구 능선에 오르거나 기슭을 걷습니다."), ("섭지코지", "성산일출봉을 배경으로 해안을 걷습니다."), ("성산 점심", "성산읍에서 해산물로 식사합니다."), ("아쿠아플라넷 또는 카페", "아쿠아리움 또는 주변 카페에서 쉽니다."), ("광치기해변", "일출봉이 정면으로 보이는 해변을 걷습니다."), ("성산 일대 저녁", "성산에서 흑돼지·해산물로 저녁을 먹습니다.")]),
            "c02": C("우도 하루 코스", "성산항에서 우도에 들어가 해안 일주, 검멀레·하고수동, 땅콩아이스크림 후 성산으로 돌아옵니다. 다른 관광지를 억지로 묶지 않습니다.", "성산항 → 우도 → 해안 관광 → 성산항", "배편은 날씨에 영향을 받습니다. 섬 안은 스쿠터·버스·택시 중 고르세요.", [("성산항", "우도 여객선에 탑니다."), ("우도 입도", "천진항·하우목동항에 내립니다."), ("우도 해안 일주", "섬 둘레 해안도로를 한 바퀴 돕니다."), ("점심", "우도에서 해산물·김밥으로 식사합니다."), ("검멀레해변·하고수동해변", "검은 모래와 하얀 해변을 봅니다."), ("카페·땅콩아이스크림", "우도 땅콩 디저트를 먹습니다."), ("성산 복귀", "배로 성산에 돌아옵니다.")]),
            "c03": C("협재·제주 서부 코스", "협재·금능 해변, 한림 점심, 오설록, 서부 카페, 해안 일몰로 이어지는 하루입니다.", "협재 → 금능 → 오설록 → 서부 해안", "협재는 비양도가 포인트입니다. 오설록은 주말 주차 줄을 보세요.", [("협재해수욕장", "에메랄드 바다와 비양도를 봅니다."), ("금능해변", "협재와 이어진 백사장을 걷습니다."), ("한림 점심", "한림·협재에서 식사합니다."), ("오설록 티뮤지엄", "녹차밭과 뮤지엄을 둘러봅니다."), ("서부 카페", "녹차밭·해안 카페에서 쉽니다."), ("해안 일몰", "서부 해안에서 노을을 봅니다.")]),
            "c04": C("애월·한담 해안 코스", "애월 해안도로, 한담해안산책로, 카페거리, 곽지해수욕장, 일몰로 이어지는 카페·해안 감성 코스입니다.", "애월 → 한담 → 곽지해수욕장", "한담 산책로는 일몰 전에 걷기 좋습니다. 주말 애월은 차가 막힙니다.", [("애월 해안도로", "해안 도로를 따라 카페와 바다를 봅니다."), ("한담해안산책로", "검은 현무암 해안 데크를 걷습니다."), ("애월 점심", "애월읍에서 해산물·한식으로 식사합니다."), ("카페거리", "애월 카페에서 커피를 마십니다."), ("곽지해수욕장", "한담과 이어진 해변을 걷습니다."), ("일몰", "애월 바다로 지는 해를 봅니다."), ("저녁", "애월에서 흑돼지 등으로 저녁을 먹습니다.")]),
            "c05": C("서귀포 폭포·남부 코스", "정방폭포, 올레시장, 천지연폭포, 새연교·새섬, 서귀포 해안으로 이어지는 남부 하루입니다.", "정방폭포 → 서귀포매일올레시장 → 천지연폭포 → 새연교", "폭포는 비가 온 뒤 수량이 좋습니다. 시장은 점심에 붐빕니다.", [("정방폭포", "바다로 떨어지는 폭포를 봅니다."), ("서귀포 시내", "서귀포 원도심을 걷습니다."), ("올레시장·점심", "매일올레시장에서 점심을 먹습니다."), ("천지연폭포", "도심 속 폭포 계곡을 걷습니다."), ("새연교·새섬", "다리와 섬 산책로를 걷습니다."), ("서귀포 해안", "남쪽 바다를 보며 쉽니다."), ("저녁", "서귀포에서 흑돼지·해산물로 저녁을 먹습니다.")]),
            "c06": C("중문 관광단지 코스", "주상절리대, 중문해수욕장, 여미지식물원 또는 박물관, 중문 단지로 이어지는 하루입니다.", "주상절리 → 중문해수욕장 → 중문관광단지", "주상절리는 절벽이라 안전선을 지키세요. 중문 해변은 파도가 거칠 수 있습니다.", [("주상절리대", "기둥 모양 절리를 전망대에서 봅니다."), ("중문해수욕장", "중문 색달해변을 걷습니다."), ("점심", "중문 단지에서 식사합니다."), ("여미지식물원 또는 박물관", "실내 정원이나 박물관에서 쉽니다."), ("중문 관광단지", "호텔·쇼핑몰 단지를 걷습니다."), ("해안·카페", "해안 카페에서 풍경을 봅니다."), ("저녁", "중문에서 저녁을 먹습니다.")]),
            "c07": C("한라산 등산 코스", "한라산만 하루로 잡습니다. 성판악·관음사 정상 코스는 장시간 등산이며 사전예약이 필요합니다.", "한라산 집중", "백록담·윗세오름 코스를 체력에 맞게 고르세요. 정상 탐방은 예약·입산 시간을 지키세요. 다른 관광지를 끼우지 마세요.", [("등산 시작", "성판악 또는 관음사 탐방로에서 입산합니다."), ("정상 또는 윗세오름", "백록담 또는 윗세오름에서 점심·휴식을 합니다."), ("하산", "같은 탐방로로 내려옵니다."), ("제주 흑돼지·저녁", "제주시에서 흑돼지로 체력을 회복합니다.")], "성판악·관음사 정상 코스는 사전예약이 필요합니다."),
            "c08": C("제주시·시장·해안 코스", "용두암, 용연계곡, 제주목관아, 동문시장, 탑동으로 이어지는 공항 가까운 하루입니다. 입국·출국일에 쓰기 좋습니다.", "용두암 → 제주 원도심 → 동문시장 → 탑동", "동문시장은 저녁 먹거리가 풍부합니다. 용두암은 파도가 셉니다.", [("용두암", "용 머리 모양 바위를 봅니다."), ("용연계곡·해안", "용두암 옆 해안 계곡을 걷습니다."), ("제주시 점심", "원도심에서 국밥 등으로 식사합니다."), ("제주목관아·원도심", "목관아와 관덕정 일대를 걷습니다."), ("동문시장", "시장 골목을 둘러봅니다."), ("탑동·해안 산책", "탑동 해변을 걷습니다."), ("시장 먹거리·저녁", "동문시장에서 저녁을 먹습니다.")]),
            "c09": C("제주 동부 숲·오름 코스", "비자림, 월정리해변, 용눈이오름, 세화해변으로 이어지는 동부 숲·오름 하루입니다.", "비자림 → 월정리 → 오름 → 세화", "용눈이오름은 경사가 있습니다. 비자림은 이슬에 미끄러울 수 있습니다.", [("비자림", "천년 비자나무 숲을 걷습니다."), ("월정리해변", "에메랄드 해변과 카페 거리를 봅니다."), ("점심", "월정리·세화에서 해산물로 식사합니다."), ("용눈이오름", "부드러운 능선 오름에 오릅니다."), ("세화해변", "한적한 동부 해변을 걷습니다."), ("동부 카페·저녁", "세화·월정리 카페에서 하루를 닫습니다.")]),
            "c10": C("산방산·제주 남서부 코스", "산방산, 용머리해안, 송악산, 사계해안으로 이어지는 남서부 일몰 코스입니다.", "산방산 → 용머리해안 → 송악산 → 사계해안", "용머리해안은 만조·너울에 통제됩니다. 송악산은 짧은 능선 산책입니다.", [("산방산", "종 모양 화산체를 바라보거나 산방굴에 오릅니다."), ("용머리해안", "층층 화산 해안을 걷습니다."), ("점심", "사계·화순에서 식사합니다."), ("송악산", "마라도가 보이는 능선을 걷습니다."), ("사계해안", "산방산이 보이는 해변을 봅니다."), ("남서부 일몰", "사계 바다로 지는 해를 봅니다.")]),
        },
    },
}


def tr_stop(n, d):
    return (n, d)


EN = {
    "gangwon": {
        "pickLabel": "Gangwon curated courses",
        "intro": "Day courses across Seoraksan and Sokcho, Gangneung’s coast, Nami Island and Chuncheon, Daegwallyeong, Yangyang, Donghae–Samcheok, and Cheorwon.",
        "guideEyebrow": "Gangwon course guide",
        "courses": {
            "c01": C("Sokcho · Seoraksan", "Seoraksan and Gwongeumseong, then Sokcho’s fish market, beach, Oeongchi coastal trail, and Daepo Port—the strongest Gangwon day.", "Seoraksan → Sokcho Market → Sokcho Beach → Oeongchi → Daepo Port", "Check cable-car queues and weather. The market is busy at lunch. Wear walking shoes for Oeongchi.", [("Seoraksan National Park", "Start around Sogongwon and the Ulsanbawi area."), ("Cable car · Gwongeumseong", "Ride up for ridge and East Sea views."), ("Sokcho Tourist Fish Market", "Lunch on raw fish and market snacks."), ("Sokcho Beach", "Walk the East Sea shoreline."), ("Oeongchi coastal trail", "Follow the cliffside path above the waves."), ("Daepo Port", "Finish with harbor views and dinner.")]),
            "c02": C("Gangneung sea · café", "Gyeongpo Lake and Beach, Jungang Market, Anmok coffee street, and Gangmun Beach—sea and cafés, not forced history stops.", "Gyeongpo → Gangneung Jungang Market → Anmok → Gangmun", "Anmok is crowded on weekends. Bring a layer for the wind.", [("Gyeongpodae · Gyeongpo Lake", "Walk the lake and pavilion area."), ("Gyeongpo Beach", "Stroll between pines and sand."), ("Jungang Market lunch", "Eat Gangneung food in the market lanes."), ("Anmok coffee street", "Coffee with a sea view."), ("Gangmun Beach", "Continue along the linked shoreline."), ("Dinner", "Eat after sunset in Gangneung.")]),
            "c03": C("Chuncheon · Nami Island", "Nami Island, dakgalbi lunch, the Samaksan lake cable car, Uiam Lake, and downtown Chuncheon.", "Nami Island → Chuncheon → Samaksan cable car → Uiam Lake", "Allow ferry time at Nami. Check cable-car weather closures.", [("Nami Island", "Walk the metasequoia lanes."), ("Chuncheon dakgalbi lunch", "Eat spicy stir-fried chicken in town."), ("Samaksan lake cable car", "Cross Uiam Lake by gondola."), ("Uiam Lake", "Pause for lakeside views."), ("Chuncheon downtown", "Walk Myeong-dong and the market, then dinner.")]),
            "c04": C("Pyeongchang · Daegwallyeong", "Sheep farm, highland roads, Woljeongsa and the fir-tree path—best for visitors who want nature and snow-country scenery.", "Daegwallyeong → Woljeongsa → fir forest path", "Check farm hours and weather. The temple path can be slippery.", [("Daegwallyeong Sheep Farm", "See sheep on the highland pasture."), ("Pyeongchang lunch", "Eat near the farm or temple."), ("Daegwallyeong area", "Drive the ridge for open views."), ("Woljeongsa", "Visit the Odaesan temple grounds."), ("Fir forest path", "Walk the thousand-year fir avenue.")]),
            "c05": C("Yangyang surf · coast", "Naksansa, Naksan Beach, Hajodae and Surfyy Beach—a Yangyang shoreline day.", "Naksansa → Naksan Beach → Hajodae → Surfyy Beach", "Surf beaches change with season and swell. Time the sunset.", [("Naksansa", "Temple and Uisangdae above the East Sea."), ("Yangyang lunch", "Eat near Naksan."), ("Naksan Beach", "Walk the sand below the temple."), ("Hajodae · Surfyy Beach", "Sea stacks and surf culture."), ("Sunset · dinner", "Watch the light drop, then eat.")]),
            "c06": C("Donghae · Samcheok coast", "Chuam Candle Rock, Dokjaebi Sky Valley, and Mukho’s Nongol mural alleys.", "Chuam → Dokjaebi Sky Valley → Mukho Port", "Sky Valley is high—skip if you dislike heights. Nongol alleys are steep.", [("Chuam Candle Rock", "See the sea stack from the lookout."), ("Chuam Beach", "Walk the sand under the rock."), ("Lunch", "Squid and seafood near Chuam or Mukho."), ("Dokjaebi Sky Valley", "Cliff walkways and sky attractions."), ("Mukho Port · Nongol", "Murals and harbor views."), ("Dinner", "Seafood in Mukho.")]),
            "c07": C("Cheorwon Hantangang · DMZ", "Columnar-joint trail, Goseokjeong, and Cheorwon DMZ—Hantangang is on Korea’s tourism 100 list.", "Hantangang → Goseokjeong → Cheorwon DMZ", "DMZ tours need ID, bookings, and run on set days.", [("Hantangang columnar-joint trail", "Walk the cliff path above basalt columns."), ("Lunch", "Makguksu or Korean food near Goseokjeong."), ("Goseokjeong", "The river rock and park."), ("Cheorwon DMZ tour", "Follow the official security-tour route."), ("End", "Return from Cheorwon.")]),
        },
    },
}


def fill_en_from_ko_regions():
    """Copy remaining KO regions into EN with English already defined above; merge Chungcheong+."""
    # EN already has gangwon. Add the rest by translating in this function body below.
    extra = {}
    extra["chungcheong"] = {
        "pickLabel": "Chungcheong curated courses",
        "intro": "Baekje Gongju and Buyeo, Danyang activities, Daecheon Beach, Taean sunsets, and Daejeon city.",
        "guideEyebrow": "Chungcheong course guide",
        "courses": {
            "c01": C("Gongju Baekje history", "Gongsanseong, Sanseong Market, King Muryeong’s tomb, the Gongju museum, and Jemincheon old town.", "Gongsanseong → Sanseong Market → Royal tombs → Gongju National Museum → Jemincheon", "Check indoor tomb-museum routing. Wear walking shoes on the fortress.", [("Gongsanseong", "Walk the Baekje walls above the Geumgang."), ("Sanseong Market lunch", "Eat in the market lanes."), ("Tomb of King Muryeong", "Royal tombs and exhibition halls."), ("Gongju National Museum", "Baekje finds from the tombs."), ("Jemincheon old town", "Walk the stream and downtown alleys."), ("Dinner", "Eat in Gongju.")]),
            "c02": C("Buyeo Baekje history", "Busosanseong, Gungnamji, Buyeo National Museum, and Jeongnimsaji—same era as Gongju, different mood.", "Busosanseong → Gungnamji → Buyeo National Museum → Jeongnimsaji", "Busosanseong has a climb. Gungnamji is best near sunset.", [("Busosanseong", "Walk the last Baekje fortress woods."), ("Buyeo lunch", "Eat near the fortress."), ("Gungnamji", "Loop the palace pond."), ("Buyeo National Museum", "See the gilt-bronze incense burner and more."), ("Jeongnimsaji", "Five-story pagoda and temple site."), ("Buyeo downtown", "Dinner in town.")]),
            "c03": C("Danyang nature · activities", "Dodamsambong, Mancheonha Skywalk, the river trail, paragliding or Café San, then Guyeong Market.", "Dodamsambong → Mancheonha Skywalk → Danyanggang trail → paragliding → market", "Skywalk and paragliding need weather and bookings.", [("Dodamsambong", "Three river peaks from the lookout."), ("Mancheonha Skywalk", "Glass walk over the cliff."), ("Danyang lunch", "Garlic and local stews in town."), ("Danyanggang trail", "Cliff path beside the river."), ("Paragliding or Café San", "Fly or take in the view from Café San."), ("Guyeong Market", "Snacks and souvenirs.")]),
            "c04": C("Boryeong Daecheon Beach", "Beach, seafood, Sky Bike, cafés, and a West Sea sunset—strong in summer; Mud Festival keeps it famous.", "Daecheon Beach → Sky Bike → shore → sunset", "Summer and festival days are packed. Check Sky Bike hours.", [("Daecheon Beach", "Open the day on the West Sea sand."), ("Seafood lunch", "Eat near the beach."), ("Daecheon Sky Bike", "Ride the coastal rail bike."), ("Beach café", "Coffee with a sea view."), ("Shore walk", "Walk the sand before dusk."), ("Sunset", "West Sea colors."), ("Dinner", "More seafood in Daecheon.")]),
            "c05": C("Taean West Sea sunset", "Anmyeondo and Kkotji Beach, cafés, and the famous rock sunset—theme the day around sea and light.", "Anmyeondo → Kkotji Beach → West Sea sunset", "Aim for the Halmi/Harabi rocks at sunset. Transit is thin.", [("Anmyeondo forest or Kkotji", "Start in the woods or at Kkotji."), ("Taean lunch", "Eat on Anmyeondo."), ("Kkotji Beach", "Walk toward the twin sea rocks."), ("Café · coast walk", "Pause, then walk again."), ("Kkotji sunset", "Sun dropping between the rocks."), ("Dinner", "Eat in Taean.")]),
            "c06": C("Daejeon city · science", "National Science Museum, Expo Hanbit Tower, Seongsimdang and Jungang-ro, then old downtown—useful near Cheongju Airport and KTX.", "Science Museum → Expo → Seongsimdang → old Daejeon", "Seongsimdang queues on weekends. Check museum hours.", [("National Science Museum", "Hands-on exhibitions."), ("Daejeon lunch", "Kalguksu or Korean food near Expo."), ("Expo Park · Hanbit Tower", "Walk the plaza and tower."), ("Seongsimdang · Jungang-ro", "Famous bread, then the main street."), ("Old downtown", "Eunhaeng-dong and Daeheung-dong."), ("Dinner", "Eat in the old center.")]),
        },
    }
    extra["jeolla"] = {
        "pickLabel": "Jeolla curated courses",
        "intro": "Jeonju Hanok Village, Yeosu night sea, Suncheon Bay, Damyang bamboo, Boseong tea, and Mokpo’s modern port streets.",
        "guideEyebrow": "Jeolla course guide",
        "courses": {
            "c01": C("Jeonju Hanok Village", "Village, Gyeonggijeon, bibimbap, Jeondong Cathedral, Omokdae, hanok cafés, and Nambu Market—the first Jeolla pick.", "Hanok Village → Gyeonggijeon → Jeondong Cathedral → Omokdae → Nambu Market", "Rent hanbok in the morning. Weekends are packed.", [("Jeonju Hanok Village", "Walk the tiled-roof lanes."), ("Gyeonggijeon", "Shrine of Taejo’s portrait."), ("Bibimbap lunch", "Jeonju bibimbap or Korean food."), ("Jeondong Cathedral", "Red-brick church among hanok."), ("Omokdae", "Hill view over the village."), ("Hanok café · craft", "Tea or a short traditional workshop."), ("Nambu Market · Youth Mall", "Evening market and youth mall."), ("Dinner", "Jeonju Korean food.")]),
            "c02": C("Yeosu sea · night views", "Odongdo, seafood, cable car, Dolsan Park, Yi Sun-sin Square, Nangman pocha, and the night sea.", "Odongdo → cable car → Dolsan Park → Yi Sun-sin Square → night sea", "Cable-car waits run long. Pocha streets open later.", [("Odongdo", "Camellia paths and the breakwater."), ("Seafood lunch", "Gejang and fish in Yeosu."), ("Marine cable car", "Gondolas over the water."), ("Dolsan Park", "City and sea from the hill."), ("Yi Sun-sin Square", "Hamel lighthouse and the waterfront."), ("Nangman pocha street", "Casual evening drinks and snacks."), ("Yeosu night sea", "Lit harbor views.")]),
            "c03": C("Suncheon garden · wetland", "Suncheon Bay National Garden, the wetland, Yongsan Observatory, and sunset—the nature day in Jeolla.", "National Garden → Suncheon Bay wetland → Yongsan Observatory", "Garden and wetland sit apart; plan transfer time.", [("National Garden", "Walk lakes and themed gardens."), ("Lunch", "Eat between garden and wetland."), ("Suncheon Bay wetland", "Reed boardwalks."), ("Yongsan Observatory", "The whole wetland from above."), ("Sunset", "Golden reeds at dusk."), ("Suncheon dinner", "Eat in town.")]),
            "c04": C("Damyang bamboo", "Juknokwon, Gwanbangjerim, tteokgalbi, the metasequoia road, cafés, and Metaprovence.", "Juknokwon → Gwanbangjerim → Metasequoia Road → Metaprovence", "Use the pedestrian side of the tree road.", [("Juknokwon", "Bamboo forest paths."), ("Gwanbangjerim", "Riverside zelkova grove."), ("Tteokgalbi · bamboo rice", "Damyang lunch specialties."), ("Metasequoia Road", "Photo stop under the trees."), ("Damyang café", "Rest near the road."), ("Metaprovence", "European-style shops."), ("End", "Head back from Damyang.")]),
            "c05": C("Boseong tea · coast", "Green-tea terraces, a tea café, then Yulpo Beach—easy to photograph.", "Boseong tea fields → Yulpo Beach", "Follow field photo rules. Yulpo can be windy.", [("Boseong tea fields", "Walk the terraces."), ("Lunch", "Hot-pot rice near the fields."), ("Tea café", "Green-tea drinks and sweets."), ("Yulpo Beach", "Drop down to the shore."), ("Coast walk", "Slow walk at Yulpo."), ("Dinner", "Eat near Boseong or Beolgyo.")]),
            "c06": C("Mokpo modern streets · sea", "Modern historic district, marine cable car, Yudalsan, Gatbawi and Peace Plaza, seafood dinner.", "Modern streets → cable car → Yudalsan → Peace Plaza", "Yudalsan is a climb. Cable cars pause in wind.", [("Modern historic district", "Colonial-era streets."), ("Mokpo lunch", "Gukbap or Korean food."), ("Marine cable car", "Ride over the water."), ("Yudalsan", "City and archipelago views."), ("Gatbawi · Peace Plaza", "Coast and hat-shaped rocks."), ("Seafood dinner", "Fish market and harbor.")]),
        },
    }
    extra["gyeongsang"] = {
        "pickLabel": "Gyeongsang curated courses",
        "intro": "Silla Gyeongju, Andong Hahoe, Tongyeong and Geoje, Pohang, Daegu, Ulsan, and Haeinsa.",
        "guideEyebrow": "Gyeongsang course guide",
        "courses": {
            "c01": C("Gyeongju Silla history", "Bulguksa, Hwangnidan-gil, Daereungwon, Cheomseongdae, Woljeonggyo, and Donggung & Wolji at night—the top Gyeongsang day.", "Bulguksa → Hwangnidan-gil → Daereungwon → Cheomseongdae → Woljeonggyo → Donggung & Wolji", "Night entry at Wolji is the point; check closing time.", [("Bulguksa", "UNESCO temple at an easy pace."), ("Hwangnidan-gil lunch", "Eat in the hanok café street."), ("Daereungwon", "Walk the royal tumuli park."), ("Cheomseongdae", "Silla’s stone observatory."), ("Gyochon · Woljeonggyo", "Bridge and village at dusk."), ("Donggung & Wolji night", "Lit pond to close the day.")]),
            "c02": C("Andong Hahoe culture", "Buyongdae, Hahoe Village, mask museum, Byeongsan Seowon, and Woryeonggyo.", "Buyongdae → Hahoe Village → Byeongsan Seowon → Woryeonggyo", "Hahoe charges admission. Byeongsan is easier by car.", [("Buyongdae", "Cliff view over the village bend."), ("Hahoe Village", "Hanok inside the river loop."), ("Andong lunch", "Heotjesabap or gukbap."), ("Mask museum · dance", "Hahoe masks and shows."), ("Byeongsan Seowon", "Mandaeru and academy grounds."), ("Woryeonggyo", "Evening walk on the long bridge."), ("Dinner", "Andong jjimdak.")]),
            "c03": C("Tongyeong sea · views", "Cable car, Mireuksan, Jungang Market, Dongpirang, Gangguan, Yi Sun-sin Park.", "Cable car · Mireuksan → market → Dongpirang → Gangguan → Yi Sun-sin Park", "The summit is windy. Dongpirang alleys are steep.", [("Tongyeong cable car", "Gondolas over the harbor."), ("Mireuksan view", "Hallyeohaesang from the top."), ("Jungang Market lunch", "Chungmu gimbap and honey bread."), ("Dongpirang murals", "Painted alleys and port views."), ("Gangguan", "Harbor below the village."), ("Yi Sun-sin Park", "Naval history by the water."), ("Tongyeong dinner", "Seafood.")]),
            "c04": C("Geoje Oedo · sea", "Haegeumgang, Oedo Botania, Windy Hill, and Sinseondae—nature and photos. Boats depend on weather.", "Haegeumgang → Oedo Botania → Windy Hill → Sinseondae", "Confirm sailings the same morning.", [("Ferry pier", "Board at Jangseungpo or the Oedo pier."), ("Haegeumgang", "Sea cliffs from the boat."), ("Oedo Botania", "Walk the island garden."), ("Geoje lunch", "Eat after returning to Geoje."), ("Windy Hill", "Windmill and grass above the sea."), ("Sinseondae", "Rocks meeting the water."), ("Geoje dinner", "Eat in Geoje.")], "Oedo boats can cancel in wind or fog."),
            "c05": C("Pohang Space Walk", "Jukdo Market, Yeongildae Beach, Space Walk, a coast café, and Yeongildae at night.", "Jukdo Market → Yeongildae → Space Walk → coast", "Space Walk is high. Night views center on the pavilion.", [("Jukdo Market", "Pohang’s big market in the morning."), ("Lunch", "Eat near Jukdo or Yeongildae."), ("Yeongildae Beach", "Sand and the sea pavilion."), ("Space Walk", "Hwanho Park’s sky walk."), ("Coast café", "Coffee facing the water."), ("Yeongildae night", "Lights on the beach.")]),
            "c06": C("Pohang Homigot · Guryongpo", "Homigot sunrise square and Guryongpo’s Japanese house street—different from downtown Pohang.", "Homigot → Guryongpo → Guryongpo Port", "Homigot is an morning/sunrise place. Guryongpo alleys are narrow.", [("Homigot", "The bronze hands at Korea’s eastern tip."), ("Guryongpo Japanese houses", "Colonial-era street."), ("Guryongpo lunch", "Gwamegi and seafood."), ("Guryongpo Port", "Working harbor."), ("Café · coast", "Rest by the water."), ("Return to Pohang", "Head back to the city.")]),
            "c07": C("Daegu markets · city", "Seomun Market, modern alley, Dongseong-ro, and Apsan views—local rather than must-see.", "Seomun Market → modern alley → Dongseong-ro → Apsan", "Seomun is huge; leave time. Apsan is best at dusk.", [("Seomun Market", "Daegu’s landmark market."), ("Daegu lunch", "Makchang or beef soup."), ("Modern culture alley", "Gyesan-dong heritage lanes."), ("Dongseong-ro", "Main shopping street."), ("Apsan Observatory", "City lookout."), ("Apsan night", "Lights and dinner.")]),
            "c08": C("Ulsan nature · coast", "Taehwa River National Garden, Daewangam Park, and Ilsan Beach—a surprise nature day.", "Taehwa Garden → Daewangam → Ilsan Beach", "Daewangam paths are long.", [("Taehwa River National Garden", "Bamboo and garden walks."), ("Ulsan lunch", "Milmyeon or Korean food."), ("Daewangam Park", "Sea rocks and lighthouse."), ("Ilsan Beach", "Sand beside the park."), ("Coast walk", "More boardwalk."), ("Dinner", "Eat in Ulsan.")]),
            "c09": C("Hapcheon Haeinsa", "Haeinsa, the Tripitaka Koreana, and a Gayasan walk—UNESCO and Buddhist culture.", "Haeinsa → Tripitaka → Gayasan", "Follow hall rules in the wood-block libraries. The mountain closes early.", [("Haeinsa", "Climb into the temple."), ("Lunch", "Eat at the temple village."), ("Tripitaka halls", "Guided look at the wood blocks."), ("Gayasan walk", "Short forest paths."), ("Café", "Rest after the descent."), ("End", "Leave Hapcheon.")]),
        },
    }
    extra["busan"] = {
        "pickLabel": "Busan curated courses",
        "intro": "Haeundae and Gwangalli, Gamcheon and Jagalchi, Songdo and Yeongdo, Haedong Yonggungsa in Gijang, and Seomyeon–Jeonpo.",
        "guideEyebrow": "Busan course guide",
        "courses": {
            "c01": C("Haeundae · Cheongsapo · Gwangalli", "The first-visit Busan day: Haeundae, Dongbaekseom, Blueline Park, Cheongsapo observatory, Gwangalli night.", "Haeundae → Dongbaekseom → Cheongsapo → Gwangalli", "Check Blueline waits. Gwangandaegyo looks best from the beach at night.", [("Haeundae Beach", "Start on Busan’s famous sand."), ("Dongbaekseom · The Bay 101", "Camellia island and Marine City views."), ("Lunch", "Milmyeon or raw fish in Haeundae."), ("Blueline Park · Cheongsapo", "Coastal train toward Cheongsapo."), ("Cheongsapo observatory", "Cliff lookout over the East Sea."), ("Gwangalli Beach", "Bridge views across the bay."), ("Dinner · bridge lights", "Eat with Gwangandaegyo lit up.")]),
            "c02": C("Gamcheon · Jagalchi · Nampo", "Culture village, fish market, BIFF Square, Gukje Market, Yongdusan, Nampo—old Busan in one day.", "Gamcheon → Jagalchi → BIFF Square → Gukje Market → Yongdusan → Nampo", "Gamcheon is steep. Jagalchi peaks at lunch.", [("Gamcheon Culture Village", "Painted alleys and views."), ("Jagalchi Market lunch", "Fish and seafood in the market."), ("BIFF Square", "Handprints and cinema square."), ("Gukje Market", "Packed traditional stalls."), ("Yongdusan · Busan Tower", "Tower and port outlook."), ("Nampo", "Old downtown streets."), ("Dinner", "Dwaeji-gukbap in Nampo.")]),
            "c03": C("Songdo · Yeongdo coast", "Songdo Beach, marine cable car, Amnam Park, Huinnyeoul Village, Yeongdo cafés.", "Songdo Beach → cable car → Amnam Park → Huinnyeoul → Yeongdo", "Cable cars pause in wind. Huinnyeoul alleys are steep and narrow.", [("Songdo Beach", "West Busan sand."), ("Songdo marine cable car", "Gondolas over the water."), ("Lunch", "Gukbap near Songdo or Yeongdo."), ("Amnam Park", "Headland paths at Songdo."), ("Huinnyeoul Culture Village", "Cliff houses above the sea."), ("Yeongdo café", "Coffee on the island."), ("Dinner", "Eat on Yeongdo.")]),
            "c04": C("Gijang · Haedong Yonggungsa", "Temple in the waves, Gijang coast, Osiria, cafés, sunset.", "Haedong Yonggungsa → Gijang coast → Osiria → coast café", "Go early to the temple. Sunset is best on the Gijang shore.", [("Haedong Yonggungsa", "Temple beside the surf."), ("Gijang coast", "Rocks around the temple."), ("Seafood lunch", "Crab and fish in Gijang."), ("Ananti · Osiria", "Resort and outlet cluster."), ("Coast café", "Sea-view coffee."), ("Gijang sunset", "Evening light on the water."), ("Dinner", "Eat in Gijang.")]),
            "c05": C("Yeongdo focus", "Taejongdae, Huinnyeoul, Jeolyeong coastal trail, cafés, Busan Port night—slow sea day.", "Taejongdae → Huinnyeoul → Jeolyeong trail → Yeongdo café", "Choose the Danubi train or walking paths at Taejongdae.", [("Taejongdae", "Cliffs and lighthouse at Yeongdo’s tip."), ("Yeongdo lunch", "Baekban or gukbap."), ("Huinnyeoul Culture Village", "Cliff village walk."), ("Jeolyeong coastal trail", "Southern boardwalk."), ("Yeongdo café", "Another sea-view stop."), ("Port night · dinner", "Harbor lights.")]),
            "c06": C("Seomyeon · Jeonpo local", "Seomyeon, Jeonpo cafés and shops, shopping, dinner, and night streets—how younger Busan actually hangs out.", "Seomyeon → Jeonpo → Seomyeon", "Jeonpo is spread out. Nights crowd Seomyeon’s underground mall.", [("Seomyeon", "Busan’s crossroads."), ("Lunch", "Milmyeon or gukbap."), ("Jeonpo café street", "Cafés and small stores."), ("Concept shops", "Independent shops in the alleys."), ("Seomyeon shopping", "Malls and underground arcades."), ("Dinner", "Busan food in Seomyeon."), ("Seomyeon night", "Neon and late streets.")]),
        },
    }
    extra["jeju"] = {
        "pickLabel": "Jeju curated courses",
        "intro": "Seongsan and Udo, Hyeopjae and Aewol, Seogwipo waterfalls, Jungmun, Hallasan, Jeju City markets, oreum, and Sanbangsan.",
        "guideEyebrow": "Jeju course guide",
        "courses": {
            "c01": C("Seongsan · east Jeju", "Seongsan Ilchulbong, Seopjikoji, and Gwangchigi Beach—UNESCO sunrise peak plus coast views.", "Seongsan Ilchulbong → Seopjikoji → Gwangchigi Beach", "Mornings are quieter on the peak. The summit climb needs legs.", [("Seongsan Ilchulbong", "Climb the crater rim or walk the base."), ("Seopjikoji", "Coast with Seongsan in the background."), ("Seongsan lunch", "Seafood in Seongsan-eup."), ("Aqua Planet or café", "Aquarium or a nearby café."), ("Gwangchigi Beach", "Straight-on views of the peak."), ("Seongsan dinner", "Black pork or seafood.")]),
            "c02": C("Udo full day", "Ferry from Seongsan, loop the island, Geommeolle and Hagwisu-dong, peanut ice cream, back to Seongsan. Don’t bolt on extra sights.", "Seongsan Port → Udo → coast loop → Seongsan Port", "Boats depend on weather. On the island pick scooter, bus, or taxi.", [("Seongsan Port", "Board the Udo ferry."), ("Arrive on Udo", "Land at Cheonjin or Haumokdong."), ("Coast loop", "Circle the island road."), ("Lunch", "Seafood or gimbap on Udo."), ("Geommeolle · Hagwisu-dong", "Black sand and white beach."), ("Café · peanut ice cream", "Udo peanut desserts."), ("Return to Seongsan", "Ferry back.")]),
            "c03": C("Hyeopjae · west Jeju", "Hyeopjae and Geumneung, Hallim lunch, Osulloc, west cafés, sunset.", "Hyeopjae → Geumneung → Osulloc → west coast", "Biyangdo is the Hyeopjae photo. Osulloc parking queues on weekends.", [("Hyeopjae Beach", "Turquoise water and Biyangdo."), ("Geumneung Beach", "Linked white sand."), ("Hallim lunch", "Eat near Hallim or Hyeopjae."), ("Osulloc Tea Museum", "Tea fields and museum."), ("West café", "Tea or coast café."), ("Coast sunset", "West Jeju light.")]),
            "c04": C("Aewol · Handam coast", "Coastal road, Handam walkway, café street, Gwakji Beach, sunset—Jeju café mood.", "Aewol → Handam → Gwakji Beach", "Walk Handam before sunset. Weekend traffic is heavy.", [("Aewol coastal road", "Cafés along the shore road."), ("Handam walkway", "Basalt boardwalk."), ("Aewol lunch", "Seafood or Korean food."), ("Café street", "Coffee in Aewol."), ("Gwakji Beach", "Sand beyond Handam."), ("Sunset", "West-coast color."), ("Dinner", "Black pork in Aewol.")]),
            "c05": C("Seogwipo waterfalls", "Jeongbang Falls, Olle Market, Cheonjiyeon Falls, Saeyeon Bridge and Saeseom.", "Jeongbang Falls → daily Olle Market → Cheonjiyeon Falls → Saeyeon Bridge", "Falls run stronger after rain. The market peaks at lunch.", [("Jeongbang Falls", "Water falling into the sea."), ("Seogwipo downtown", "Walk the old center."), ("Olle Market lunch", "Eat in the daily market."), ("Cheonjiyeon Falls", "Canyon waterfall in town."), ("Saeyeon Bridge · Saeseom", "Bridge and islet paths."), ("Seogwipo coast", "South-coast pause."), ("Dinner", "Black pork or seafood.")]),
            "c06": C("Jungmun resort belt", "Jusangjeolli, Jungmun Beach, Yeomiji or a museum, the resort cluster.", "Jusangjeolli → Jungmun Beach → Jungmun complex", "Stay behind cliff rails. Jungmun surf can be rough.", [("Jusangjeolli Cliff", "Columnar joint lookout."), ("Jungmun Beach", "Saekdal sand."), ("Lunch", "Eat in the complex."), ("Yeomiji or museum", "Indoor garden or museum rest."), ("Jungmun complex", "Hotels and shops."), ("Coast café", "Sea-view coffee."), ("Dinner", "Eat in Jungmun.")]),
            "c07": C("Hallasan hike", "Hallasan only. Seongpanak and Gwaneumsa to Baengnokdam are long and need reservations.", "Hallasan focus", "Pick Baengnokdam or Witse-oreum by fitness. Do not add other sightseeing.", [("Start hike", "Enter at Seongpanak or Gwaneumsa."), ("Summit or Witse-oreum", "Lunch and views at the high point."), ("Descent", "Walk out the same trail."), ("Black pork dinner", "Recover in Jeju City.")], "Seongpanak and Gwaneumsa summit routes require advance booking."),
            "c08": C("Jeju City · market · coast", "Yongduam, Yongyeon, Mokgwana, Dongmun Market, Tapdong—close to the airport for arrival or departure days.", "Yongduam → old Jeju City → Dongmun Market → Tapdong", "Dongmun shines at dinner. Yongduam spray is strong.", [("Yongduam", "Dragon-head rock."), ("Yongyeon coast", "Gorge beside Yongduam."), ("Jeju City lunch", "Gukbap downtown."), ("Mokgwana · old town", "Former government compound."), ("Dongmun Market", "Covered market lanes."), ("Tapdong waterfront", "Harbor promenade."), ("Market dinner", "Eat at Dongmun.")]),
            "c09": C("East forest · oreum", "Bijarim, Woljeongri Beach, Yongnuni Oreum, Sehwa Beach.", "Bijarim → Woljeongri → oreum → Sehwa", "Yongnuni has a grade. Bijarim can be slippery.", [("Bijarim Forest", "Nutmeg-yew woods."), ("Woljeongri Beach", "Turquoise water and cafés."), ("Lunch", "Seafood in Woljeong or Sehwa."), ("Yongnuni Oreum", "Soft-ridge volcanic hill."), ("Sehwa Beach", "Quieter east sand."), ("East café · dinner", "Close in Sehwa or Woljeong.")]),
            "c10": C("Sanbangsan · southwest", "Sanbangsan, Yongmeori Coast, Songaksan, Sagye Beach sunset.", "Sanbangsan → Yongmeori Coast → Songaksan → Sagye Beach", "Yongmeori closes in high surf. Songaksan is a short ridge walk.", [("Sanbangsan", "Bell-shaped peak or Sanbanggul."), ("Yongmeori Coast", "Layered volcanic shore."), ("Lunch", "Eat in Sagye or Hwasun."), ("Songaksan", "Ridge toward Marado."), ("Sagye Beach", "Sanbangsan across the water."), ("Southwest sunset", "Light on Sagye Bay.")]),
        },
    }
    EN.update(extra)


def inject(lang: str, payload: dict) -> None:
    path = PAGE / f"{lang}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    curated = data["travelCourses"]["curated"]
    for key, block in payload.items():
        curated[key] = block
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("injected", lang, list(payload))


def main() -> None:
    fill_en_from_ko_regions()
    inject("ko", KO)
    inject("en", EN)
    for lang in ("ja", "zh", "zh-Hant", "vi", "th", "ru"):
        inject(lang, EN)


if __name__ == "__main__":
    main()
