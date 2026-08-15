# -*- coding: utf-8 -*-
"""One-shot: lockers + ports coords/i18n, transport/app keys, category cover images."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import quote

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tool"))
from lib import i18n_store  # noqa: E402

COORDS = ROOT / "data" / "places" / "places-coords.js"
IMG_TYPES = ROOT / "Images" / "places" / "_types"
IMG_PLACES = ROOT / "Images" / "places"

LOCKER_NOTE = {
    "ko": "운영 시간·빈칸·요금은 변동될 수 있으니 또타라커 앱 또는 현장 안내로 확인하세요.",
    "en": "Hours, availability, and fees change — confirm in the Tota Locker app or on-site.",
    "ja": "営業時間・空き・料金は変わるので、もうたロッカーアプリか現地案内で確認を。",
    "zh": "营业时间、空位与费用可能变动，请用又他储物柜App或现场确认。",
    "zh-Hant": "營業時間、空位與費用可能變動，請用又他置物櫃App或現場確認。",
    "vi": "Giờ mở cửa, chỗ trống và phí có thể đổi — xác nhận trên app Tota Locker hoặc tại chỗ.",
    "th": "เวลา/ช่องว่าง/ค่าบริการเปลี่ยนได้ — ยืนยันในแอป Tota Locker หรือที่หน้างาน",
    "ru": "Часы, свободные ячейки и тарифы меняются — уточняйте в приложении Tota Locker или на месте.",
}

REGION_LABEL = {
    "seoul": {
        "ko": "서울", "en": "Seoul", "ja": "ソウル", "zh": "首尔",
        "zh-Hant": "首爾", "vi": "Seoul", "th": "โซล", "ru": "Сеул",
    },
    "busan": {
        "ko": "부산", "en": "Busan", "ja": "釜山", "zh": "釜山",
        "zh-Hant": "釜山", "vi": "Busan", "th": "ปูซาน", "ru": "Пусан",
    },
    "incheon": {
        "ko": "인천", "en": "Incheon", "ja": "仁川", "zh": "仁川",
        "zh-Hant": "仁川", "vi": "Incheon", "th": "อินชอน", "ru": "Инчхон",
    },
    "jeju": {
        "ko": "제주", "en": "Jeju", "ja": "済州", "zh": "济州",
        "zh-Hant": "濟州", "vi": "Jeju", "th": "เชจู", "ru": "Чеджу",
    },
    "jeolla": {
        "ko": "전라", "en": "Jeolla", "ja": "全羅", "zh": "全罗",
        "zh-Hant": "全羅", "vi": "Jeolla", "th": "ชอลลา", "ru": "Чолла",
    },
    "gyeongsang": {
        "ko": "경상", "en": "Gyeongsang", "ja": "慶尚", "zh": "庆尚",
        "zh-Hant": "慶尚", "vi": "Gyeongsang", "th": "คยองซัง", "ru": "Кёнсан",
    },
}


def maps_urls(q: str, hl: str = "ko") -> tuple[str, str]:
    enc = quote(q)
    return (
        f"https://www.google.com/maps/search/?api=1&query={enc}",
        f"https://maps.google.com/maps?q={enc}&hl={hl}&z=15&output=embed",
    )


# slug -> lat, lng, region, type, note_en, image path (optional), texts per lang
NEW_PLACES: list[dict] = [
    # --- Lockers ---
    {
        "slug": "locker-seoul-station",
        "lat": 37.5547,
        "lng": 126.9707,
        "region": "seoul",
        "type": "locker",
        "note": "Seoul Station luggage lockers",
        "image": "Images/places/locker-seoul-station.jpg",
        "address_ko": "서울 중구 한강대로 405 서울역",
        "name": {
            "ko": "서울역 물품보관함",
            "en": "Seoul Station lockers",
            "ja": "ソウル駅コインロッカー",
            "zh": "首尔站行李寄存",
            "zh-Hant": "首爾站行李寄物櫃",
            "vi": "Tủ gửi đồ Ga Seoul",
            "th": "ล็อกเกอร์สถานีโซล",
            "ru": "Камеры хранения на станции Сеул",
        },
        "desc": {
            "ko": "KTX·AREX·지하철이 모이는 서울역 일대 물품보관함. 캐리어 보관에 자주 쓰입니다.",
            "en": "Luggage lockers around Seoul Station (KTX, AREX, subway hub) — popular for large bags.",
            "ja": "KTX・AREX・地下鉄が集まるソウル駅周辺のロッカー。キャリー保管に便利。",
            "zh": "KTX、AREX与地铁交汇的首尔站一带行李柜，适合放大件行李。",
            "zh-Hant": "KTX、AREX與地鐵交會的首爾站一帶寄物櫃，適合放大件行李。",
            "vi": "Tủ gửi đồ quanh Ga Seoul (KTX/AREX/tàu điện) — hữu ích cho vali lớn.",
            "th": "ล็อกเกอร์แถวสถานีโซล (KTX/AREX/รถไฟใต้ดิน) เหมาะกับกระเป๋าใหญ่",
            "ru": "Камеры хранения у станции Сеул (KTX/AREX/метро) — удобно для чемоданов.",
        },
        "how": {
            "ko": "서울역 대합실·출구 안내판의 ‘물품보관함/Locker’ 표시를 따르세요. 또타라커 앱으로 빈칸을 확인할 수 있습니다.",
            "en": "Follow Locker signs in the concourse. Check empty units in the Tota Locker app when available.",
            "ja": "コンコースのLocker案内に従う。空きはもうたロッカーアプリで確認できる場合あり。",
            "zh": "按大厅 Locker 指示前往；可用又他储物柜App查看空位。",
            "zh-Hant": "依大廳 Locker 指示前往；可用又他置物櫃App查看空位。",
            "vi": "Theo bảng Locker trong sảnh. Kiểm tra chỗ trống trên app Tota Locker nếu có.",
            "th": "ตามป้าย Locker ในโถงสถานี และเช็คช่องว่างในแอป Tota Locker",
            "ru": "Следуйте указателям Locker. Свободные ячейки смотрите в приложении Tota Locker.",
        },
    },
    {
        "slug": "locker-yongsan-station",
        "lat": 37.5299,
        "lng": 126.9648,
        "region": "seoul",
        "type": "locker",
        "note": "Yongsan Station lockers",
        "image": "Images/places/locker-yongsan-station.jpg",
        "address_ko": "서울 용산구 한강대로 23길 55 용산역",
        "name": {
            "ko": "용산역 물품보관함",
            "en": "Yongsan Station lockers",
            "ja": "龍山駅コインロッカー",
            "zh": "龙山站行李寄存",
            "zh-Hant": "龍山站行李寄物櫃",
            "vi": "Tủ gửi đồ Ga Yongsan",
            "th": "ล็อกเกอร์สถานีโยงซาน",
            "ru": "Камеры хранения на станции Йонсан",
        },
        "desc": {
            "ko": "용산역·아이파크몰 일대 보관함. KTX·관광 동선 사이에 짐을 맡기기 좋습니다.",
            "en": "Lockers near Yongsan Station / I'Park Mall — handy between KTX and sightseeing.",
            "ja": "龍山駅・アイパークモール周辺。KTXと観光の合間の荷物預けに。",
            "zh": "龙山站与I·Park Mall一带寄存柜，适合KTX与观光之间暂存。",
            "zh-Hant": "龍山站與I·Park Mall一帶寄物櫃，適合KTX與觀光之間暫存。",
            "vi": "Tủ gần Ga Yongsan / I'Park Mall — tiện giữa KTX và tham quan.",
            "th": "ล็อกเกอร์แถวสถานีโยงซาน/ไอพาร์คมอลล์ ระหว่าง KTX กับเที่ยว",
            "ru": "Камеры у станции Йонсан / I'Park Mall — удобно между KTX и прогулками.",
        },
        "how": {
            "ko": "용산역 내 안내판 또는 또타라커 앱에서 위치를 확인하세요.",
            "en": "Check station signs or the Tota Locker app for exact spots.",
            "ja": "駅内案内かもうたロッカーアプリで場所を確認。",
            "zh": "在站内指示或又他储物柜App确认位置。",
            "zh-Hant": "在站內指示或又他置物櫃App確認位置。",
            "vi": "Xem biển chỉ dẫn trong ga hoặc app Tota Locker.",
            "th": "ดูป้ายในสถานีหรือแอป Tota Locker",
            "ru": "Смотрите указатели на станции или приложение Tota Locker.",
        },
    },
    {
        "slug": "locker-busan-station",
        "lat": 35.1152,
        "lng": 129.0413,
        "region": "busan",
        "type": "locker",
        "note": "Busan Station lockers",
        "image": "Images/places/locker-busan-station.jpg",
        "address_ko": "부산 동구 중앙대로 206 부산역",
        "name": {
            "ko": "부산역 물품보관함",
            "en": "Busan Station lockers",
            "ja": "釜山駅コインロッカー",
            "zh": "釜山站行李寄存",
            "zh-Hant": "釜山站行李寄物櫃",
            "vi": "Tủ gửi đồ Ga Busan",
            "th": "ล็อกเกอร์สถานีปูซาน",
            "ru": "Камеры хранения на станции Пусан",
        },
        "desc": {
            "ko": "부산역 대합실·주변 물품보관함. KTX 하차 후 시내 관광 전에 캐리어를 맡기기 좋습니다.",
            "en": "Lockers at/near Busan Station — stash bags after KTX before exploring the city.",
            "ja": "釜山駅周辺ロッカー。KTX下車後の市内観光前にキャリー預けに便利。",
            "zh": "釜山站一带行李柜，KTX下车后逛市区前可暂存行李。",
            "zh-Hant": "釜山站一帶寄物櫃，KTX下車後逛市區前可暫存行李。",
            "vi": "Tủ tại/gần Ga Busan — gửi vali sau KTX trước khi đi phố.",
            "th": "ล็อกเกอร์ที่สถานีปูซาน — ฝากกระเป๋าหลัง KTX ก่อนเที่ยวเมือง",
            "ru": "Камеры у станции Пусан — оставьте чемодан после KTX перед прогулкой.",
        },
        "how": {
            "ko": "부산역 안내판의 물품보관함/Locker를 따르세요. 성수기는 일찍 찰 수 있습니다.",
            "en": "Follow Locker signs inside Busan Station. Peak hours fill up fast.",
            "ja": "駅内のLocker案内に従う。繁忙時は早く埋まることも。",
            "zh": "按站内 Locker 指示；高峰时段可能很快满柜。",
            "zh-Hant": "按站內 Locker 指示；高峰時段可能很快滿櫃。",
            "vi": "Theo biển Locker trong ga. Giờ cao điểm mau hết chỗ.",
            "th": "ตามป้าย Locker ในสถานี ช่วงพีกเต็มเร็ว",
            "ru": "Следуйте указателям Locker. В пик места заканчиваются быстро.",
        },
    },
    {
        "slug": "locker-myeongdong-station",
        "lat": 37.5609,
        "lng": 126.9863,
        "region": "seoul",
        "type": "locker",
        "note": "Myeongdong Station T-locker",
        "image": "Images/places/locker-myeongdong-station.jpg",
        "address_ko": "서울 중구 명동역",
        "name": {
            "ko": "명동역 또타라커",
            "en": "Myeongdong Station Tota Locker",
            "ja": "明洞駅もうたロッカー",
            "zh": "明洞站又他储物柜",
            "zh-Hant": "明洞站又他置物櫃",
            "vi": "Tota Locker Ga Myeongdong",
            "th": "Tota Locker สถานีเมียงดง",
            "ru": "Tota Locker на станции Мёндон",
        },
        "desc": {
            "ko": "명동 쇼핑가 인근 지하철 물품보관함(또타라커). 쇼핑·체크아웃 당일 짐 보관에 유용합니다.",
            "en": "Subway lockers (Tota Locker) near Myeongdong shopping — useful on shopping or checkout days.",
            "ja": "明洞ショッピング街近くの地下鉄ロッカー。買い物・チェックアウト日に便利。",
            "zh": "明洞商圈附近地铁储物柜（又他），适合逛街或退房当天。",
            "zh-Hant": "明洞商圈附近地鐵置物櫃（又他），適合逛街或退房當天。",
            "vi": "Tủ tàu điện gần Myeongdong — tiện ngày shopping/checkout.",
            "th": "ล็อกเกอร์รถไฟใต้ดินใกล้เมียงดง เหมาะวันช้อป/เช็คเอาต์",
            "ru": "Камеры метро у Мёндона — удобно в день шопинга или выезда.",
        },
        "how": {
            "ko": "또타라커 앱에서 명동역을 검색해 예약·결제하세요.",
            "en": "Search Myeongdong Station in the Tota Locker app to reserve and pay.",
            "ja": "もうたロッカーアプリで明洞駅を検索して予約・支払い。",
            "zh": "在又他储物柜App搜索明洞站预约付款。",
            "zh-Hant": "在又他置物櫃App搜尋明洞站預約付款。",
            "vi": "Tìm ga Myeongdong trên app Tota Locker để đặt và thanh toán.",
            "th": "ค้นหาสถานีเมียงดงในแอป Tota Locker เพื่อจองและจ่าย",
            "ru": "Найдите станцию Мёндон в приложении Tota Locker для брони и оплаты.",
        },
    },
    {
        "slug": "locker-hongdae-station",
        "lat": 37.5572,
        "lng": 126.9254,
        "region": "seoul",
        "type": "locker",
        "note": "Hongdae Station T-locker",
        "image": "Images/places/locker-hongdae-station.jpg",
        "address_ko": "서울 마포구 홍대입구역",
        "name": {
            "ko": "홍대입구역 또타라커",
            "en": "Hongik Univ. Station Tota Locker",
            "ja": "弘大入口駅もうたロッカー",
            "zh": "弘大入口站又他储物柜",
            "zh-Hant": "弘大入口站又他置物櫃",
            "vi": "Tota Locker Ga Hongik Univ.",
            "th": "Tota Locker สถานีฮงแด",
            "ru": "Tota Locker на станции Хондэ",
        },
        "desc": {
            "ko": "홍대·합정 일대 관광·클럽 전에 가방을 맡기기 좋은 지하철 보관함입니다.",
            "en": "Subway lockers handy before exploring Hongdae / Hapjeong nightlife and cafés.",
            "ja": "弘大・合井エリア観光前に荷物を預けやすい地下鉄ロッカー。",
            "zh": "逛弘大、合井前暂存背包的地铁储物柜。",
            "zh-Hant": "逛弘大、合井前暫存背包的地鐵置物櫃。",
            "vi": "Tủ tàu điện tiện trước khi đi Hongdae/Hapjeong.",
            "th": "ล็อกเกอร์รถไฟใต้ดินก่อนเที่ยวฮงแด/ฮัปจอง",
            "ru": "Камеры метро перед прогулкой по Хондэ/Хапчон.",
        },
        "how": {
            "ko": "또타라커 앱에서 홍대입구역을 검색하세요.",
            "en": "Search Hongik University Station in the Tota Locker app.",
            "ja": "もうたロッカーアプリで弘大入口駅を検索。",
            "zh": "在又他储物柜App搜索弘大入口站。",
            "zh-Hant": "在又他置物櫃App搜尋弘大入口站。",
            "vi": "Tìm ga Hongik Univ. trên app Tota Locker.",
            "th": "ค้นหาสถานีฮงแดในแอป Tota Locker",
            "ru": "Найдите станцию Хондэ в приложении Tota Locker.",
        },
    },
    {
        "slug": "locker-gangnam-station",
        "lat": 37.4979,
        "lng": 127.0276,
        "region": "seoul",
        "type": "locker",
        "note": "Gangnam Station T-locker",
        "image": "Images/places/locker-gangnam-station.jpg",
        "address_ko": "서울 강남구 강남역",
        "name": {
            "ko": "강남역 또타라커",
            "en": "Gangnam Station Tota Locker",
            "ja": "江南駅もうたロッカー",
            "zh": "江南站又他储物柜",
            "zh-Hant": "江南站又他置物櫃",
            "vi": "Tota Locker Ga Gangnam",
            "th": "Tota Locker สถานีคังนัม",
            "ru": "Tota Locker на станции Каннам",
        },
        "desc": {
            "ko": "강남역 일대 지하철 물품보관함. 쇼핑·미팅 전 짧은 짐 보관에 적합합니다.",
            "en": "Subway lockers around Gangnam Station for short stops between shopping and meetings.",
            "ja": "江南駅周辺の地下鉄ロッカー。買い物や用事の合間の短時間預けに。",
            "zh": "江南站一带地铁储物柜，适合购物或办事间隙短存。",
            "zh-Hant": "江南站一帶地鐵置物櫃，適合購物或辦事間隙短存。",
            "vi": "Tủ tàu điện quanh Ga Gangnam cho gửi ngắn giữa shopping/họp.",
            "th": "ล็อกเกอร์รถไฟใต้ดินแถวคังนัม สำหรับฝากสั้น ๆ",
            "ru": "Камеры метро у Каннама для короткого хранения между делами.",
        },
        "how": {
            "ko": "또타라커 앱에서 강남역을 검색해 빈칸을 확인하세요.",
            "en": "Search Gangnam Station in the Tota Locker app for availability.",
            "ja": "もうたロッカーアプリで江南駅の空きを確認。",
            "zh": "在又他储物柜App搜索江南站查看空位。",
            "zh-Hant": "在又他置物櫃App搜尋江南站查看空位。",
            "vi": "Tìm ga Gangnam trên app Tota Locker để xem chỗ trống.",
            "th": "ค้นหาสถานีคังนัมในแอป Tota Locker",
            "ru": "Найдите станцию Каннам в приложении Tota Locker.",
        },
    },
    {
        "slug": "locker-express-bus-terminal",
        "lat": 37.5046,
        "lng": 127.0045,
        "region": "seoul",
        "type": "locker",
        "note": "Express Bus Terminal lockers",
        "image": "Images/places/locker-express-bus-terminal.jpg",
        "address_ko": "서울 서초구 신반포로 194 고속터미널",
        "name": {
            "ko": "고속터미널 물품보관함",
            "en": "Express Bus Terminal lockers",
            "ja": "高速ターミナルロッカー",
            "zh": "高速巴士客运站寄存",
            "zh-Hant": "高速巴士客運站寄物",
            "vi": "Tủ gửi đồ Bến xe Express Bus",
            "th": "ล็อกเกอร์สถานีรถบัสด่วน",
            "ru": "Камеры на автовокзале Express Bus Terminal",
        },
        "desc": {
            "ko": "서울 고속터미널·센트럴시티 일대 보관함. 지방행 버스 전후 짐 보관에 유용합니다.",
            "en": "Lockers at Seoul Express Bus Terminal / Central City — useful before or after intercity buses.",
            "ja": "高速ターミナル・セントラルシティ周辺。地方行きバス前後の荷物預けに。",
            "zh": "首尔高速巴士站与Central City一带寄存，适合长途巴士前后。",
            "zh-Hant": "首爾高速巴士站與Central City一帶寄物，適合長途巴士前後。",
            "vi": "Tủ tại bến xe Express Bus / Central City — tiện trước/sau xe liên tỉnh.",
            "th": "ล็อกเกอร์ที่สถานีรถบัสด่วนโซล ก่อน/หลังรถต่างจังหวัด",
            "ru": "Камеры у автовокзала / Central City — до или после междугородних автобусов.",
        },
        "how": {
            "ko": "터미널·지하철 고속터미널역 안내판을 확인하세요. 빈칸은 앱·현장에서 확인.",
            "en": "Follow terminal / subway signs. Confirm empty units on-site or in apps.",
            "ja": "ターミナル・地下鉄案内を確認。空きは現地かアプリで。",
            "zh": "按客运站/地铁指示；空位请现场或App确认。",
            "zh-Hant": "按客運站/地鐵指示；空位請現場或App確認。",
            "vi": "Theo biển bến/tàu điện. Xác nhận chỗ trống tại chỗ hoặc app.",
            "th": "ตามป้ายสถานี/รถไฟใต้ดิน เช็คช่องว่างที่หน้างานหรือแอป",
            "ru": "Смотрите указатели вокзала/метро. Свободные места — на месте или в приложении.",
        },
    },
    {
        "slug": "locker-icn-t1",
        "lat": 37.4474,
        "lng": 126.4525,
        "region": "incheon",
        "type": "locker",
        "note": "ICN T1 luggage storage",
        "image": "Images/places/locker-icn-t1.jpg",
        "address_ko": "인천 중구 공항로 272 인천국제공항 제1여객터미널",
        "name": {
            "ko": "인천공항 T1 수하물 보관",
            "en": "ICN Terminal 1 luggage storage",
            "ja": "仁川空港T1荷物預かり",
            "zh": "仁川机场T1行李寄存",
            "zh-Hant": "仁川機場T1行李寄物",
            "vi": "Gửi hành lý ICN T1",
            "th": "ฝากกระเป๋า ICN T1",
            "ru": "Камера хранения ICN T1",
        },
        "desc": {
            "ko": "인천공항 제1터미널 수하물 보관 서비스. 출국·환승·시내 관광 전 짐을 맡길 때 참고하세요.",
            "en": "Luggage storage at Incheon Airport T1 — useful before city day trips or long layovers.",
            "ja": "仁川空港第1ターミナルの荷物預かり。市内観光や乗り継ぎ前に。",
            "zh": "仁川机场一号航站楼行李寄存，适合进城一日游或转机前。",
            "zh-Hant": "仁川機場一號航廈行李寄物，適合進城一日遊或轉機前。",
            "vi": "Gửi hành lý tại ICN T1 — tiện trước khi vào phố hoặc chờ nối chuyến.",
            "th": "ฝากกระเป๋าที่ ICN T1 ก่อนเที่ยวเมืองหรือรอต่อเครื่อง",
            "ru": "Камера хранения в ICN T1 — перед поездкой в город или пересадкой.",
        },
        "how": {
            "ko": "터미널 안내판 ‘Luggage Storage / 수하물 보관’을 따르세요. 위치·요금은 공항 안내·앱으로 확인.",
            "en": "Follow Luggage Storage signs. Confirm location and fees via airport info.",
            "ja": "Luggage Storage案内に従う。場所・料金は空港案内で確認。",
            "zh": "按 Luggage Storage 指示；位置与费用以机场信息为准。",
            "zh-Hant": "按 Luggage Storage 指示；位置與費用以機場資訊為準。",
            "vi": "Theo biển Luggage Storage. Xác nhận vị trí/phí qua thông tin sân bay.",
            "th": "ตามป้าย Luggage Storage ยืนยันตำแหน่ง/ราคาจากข้อมูลสนามบิน",
            "ru": "Следуйте указателям Luggage Storage. Уточняйте место и тарифы у аэропорта.",
        },
    },
    {
        "slug": "locker-icn-t2",
        "lat": 37.4689,
        "lng": 126.4335,
        "region": "incheon",
        "type": "locker",
        "note": "ICN T2 luggage storage",
        "image": "Images/places/locker-icn-t2.jpg",
        "address_ko": "인천 중구 공항로 272 인천국제공항 제2여객터미널",
        "name": {
            "ko": "인천공항 T2 수하물 보관",
            "en": "ICN Terminal 2 luggage storage",
            "ja": "仁川空港T2荷物預かり",
            "zh": "仁川机场T2行李寄存",
            "zh-Hant": "仁川機場T2行李寄物",
            "vi": "Gửi hành lý ICN T2",
            "th": "ฝากกระเป๋า ICN T2",
            "ru": "Камера хранения ICN T2",
        },
        "desc": {
            "ko": "인천공항 제2터미널 수하물 보관. T1과 위치가 다르니 탑승 터미널을 먼저 확인하세요.",
            "en": "Luggage storage at Incheon Airport T2 — confirm your terminal first (T1 vs T2).",
            "ja": "仁川空港第2ターミナルの荷物預かり。T1と場所が違うのでターミナル確認を。",
            "zh": "仁川机场二号航站楼行李寄存；请先确认自己的航站楼。",
            "zh-Hant": "仁川機場二號航廈行李寄物；請先確認自己的航廈。",
            "vi": "Gửi hành lý tại ICN T2 — kiểm tra đúng nhà ga trước.",
            "th": "ฝากกระเป๋าที่ ICN T2 — ตรวจเทอร์มินัลให้ถูกก่อน",
            "ru": "Камера хранения в ICN T2 — сначала проверьте терминал.",
        },
        "how": {
            "ko": "T2 안내판의 수하물 보관/Luggage Storage를 확인하세요.",
            "en": "Follow Luggage Storage signs inside Terminal 2.",
            "ja": "T2内のLuggage Storage案内を確認。",
            "zh": "按T2内 Luggage Storage 指示。",
            "zh-Hant": "按T2內 Luggage Storage 指示。",
            "vi": "Theo biển Luggage Storage trong T2.",
            "th": "ตามป้าย Luggage Storage ใน T2",
            "ru": "Следуйте указателям Luggage Storage в T2.",
        },
    },
    {
        "slug": "locker-dongdaemun-station",
        "lat": 37.5656,
        "lng": 127.0090,
        "region": "seoul",
        "type": "locker",
        "note": "Dongdaemun History Culture Park Station lockers",
        "image": "Images/places/locker-dongdaemun-station.jpg",
        "address_ko": "서울 중구 동대문역사문화공원역",
        "name": {
            "ko": "동대문역사문화공원역 또타라커",
            "en": "Dongdaemun H&C Park Station Tota Locker",
            "ja": "東大門歴史文化公園駅もうたロッカー",
            "zh": "东大门历史文化公园站又他储物柜",
            "zh-Hant": "東大門歷史文化公園站又他置物櫃",
            "vi": "Tota Locker Ga Dongdaemun H&C Park",
            "th": "Tota Locker สถานีดงแดemun",
            "ru": "Tota Locker на станции Тондэмун",
        },
        "desc": {
            "ko": "DDP·동대문 쇼핑 전 가방을 맡기기 좋은 지하철 보관함입니다.",
            "en": "Subway lockers near DDP / Dongdaemun shopping districts.",
            "ja": "DDP・東大門ショッピング前に荷物を預けやすい地下鉄ロッカー。",
            "zh": "逛DDP与东大门商圈前暂存的地铁储物柜。",
            "zh-Hant": "逛DDP與東大門商圈前暫存的地鐵置物櫃。",
            "vi": "Tủ tàu điện gần DDP / Dongdaemun.",
            "th": "ล็อกเกอร์รถไฟใต้ดินใกล้ DDP/ดงแดemun",
            "ru": "Камеры метро у DDP / Тондэмуна.",
        },
        "how": {
            "ko": "또타라커 앱에서 동대문역사문화공원역을 검색하세요.",
            "en": "Search Dongdaemun History & Culture Park Station in the Tota Locker app.",
            "ja": "もうたロッカーアプリで東大門歴史文化公園駅を検索。",
            "zh": "在又他储物柜App搜索东大门历史文化公园站。",
            "zh-Hant": "在又他置物櫃App搜尋東大門歷史文化公園站。",
            "vi": "Tìm ga Dongdaemun H&C Park trên app Tota Locker.",
            "th": "ค้นหาสถานีดงแดemunในแอป Tota Locker",
            "ru": "Найдите станцию в приложении Tota Locker.",
        },
    },
    {
        "slug": "locker-haeundae-station",
        "lat": 35.1631,
        "lng": 129.1636,
        "region": "busan",
        "type": "locker",
        "note": "Haeundae Station lockers",
        "image": "Images/places/locker-haeundae-station.jpg",
        "address_ko": "부산 해운대구 해운대역",
        "name": {
            "ko": "해운대역 물품보관함",
            "en": "Haeundae Station lockers",
            "ja": "海雲台駅ロッカー",
            "zh": "海云台站行李寄存",
            "zh-Hant": "海雲台站行李寄物",
            "vi": "Tủ gửi đồ Ga Haeundae",
            "th": "ล็อกเกอร์สถานีแฮอุนแด",
            "ru": "Камеры хранения на станции Хэундэ",
        },
        "desc": {
            "ko": "해운대 해변·관광 전 짐을 맡기기 좋은 역 인근 보관함입니다.",
            "en": "Station-area lockers before Haeundae Beach sightseeing.",
            "ja": "海雲台ビーチ観光前に荷物を預けやすい駅周辺ロッカー。",
            "zh": "去海云台海滩前可暂存行李的车站寄存。",
            "zh-Hant": "去海雲台海灘前可暫存行李的車站寄物。",
            "vi": "Tủ gần ga trước khi ra biển Haeundae.",
            "th": "ล็อกเกอร์แถวสถานีก่อนเที่ยวหาดแฮอุนแด",
            "ru": "Камеры у станции перед пляжем Хэундэ.",
        },
        "how": {
            "ko": "해운대역·관광안내 근처 보관함 안내를 확인하세요. 성수기는 만석일 수 있습니다.",
            "en": "Check locker signs near the station/tourist info. Peak season fills quickly.",
            "ja": "駅・観光案内付近のロッカー案内を確認。繁忙期は満杯になりやすい。",
            "zh": "查看车站/旅游咨询附近寄存指示；旺季可能满柜。",
            "zh-Hant": "查看車站/旅遊諮詢附近寄物指示；旺季可能滿櫃。",
            "vi": "Xem biển tủ gần ga/quầy thông tin. Mùa cao điểm mau hết chỗ.",
            "th": "ดูป้ายล็อกเกอร์ใกล้สถานี ช่วงพีกเต็มเร็ว",
            "ru": "Смотрите указатели у станции. В сезон места заканчиваются быстро.",
        },
    },
    # --- Ports ---
    {
        "slug": "port-busan",
        "lat": 35.1028,
        "lng": 129.0403,
        "region": "busan",
        "type": "port",
        "note": "Busan Port passenger terminal",
        "image": "Images/places/port-busan.jpg",
        "address_ko": "부산 동구 충장대로 206 부산항국제여객터미널",
        "name": {
            "ko": "부산항",
            "en": "Busan Port",
            "ja": "釜山港",
            "zh": "釜山港",
            "zh-Hant": "釜山港",
            "vi": "Cảng Busan",
            "th": "ท่าเรือปูซาน",
            "ru": "Порт Пусан",
        },
        "desc": {
            "ko": "부산의 대표 항구. 국제여객터미널·크루즈·항만 경관을 볼 수 있는 여행 거점입니다.",
            "en": "Busan's main port — international passenger terminal, cruises, and waterfront views.",
            "ja": "釜山の代表港。国際旅客ターミナルやクルーズ、港湾景観の拠点。",
            "zh": "釜山代表性港口，有国际客运码头、邮轮与港湾景观。",
            "zh-Hant": "釜山代表性港口，有國際客運碼頭、郵輪與港灣景觀。",
            "vi": "Cảng chính của Busan — nhà ga hành khách quốc tế, du thuyền, cảnh cảng.",
            "th": "ท่าเรือหลักของปูซาน — ท่าผู้โดยสารระหว่างประเทศ/เรือสำราญ",
            "ru": "Главный порт Пусана — пассажирский терминал, круизы, набережная.",
        },
        "how": {
            "ko": "부산역에서 버스·택시로 국제여객터미널 방면. 배편·출국 심사는 공식 안내를 확인하세요.",
            "en": "From Busan Station by bus/taxi to the international passenger terminal. Confirm sailings officially.",
            "ja": "釜山駅からバス・タクシーで国際旅客ターミナルへ。運航は公式確認を。",
            "zh": "从釜山站乘公交/出租车至国际客运码头；班次以官方为准。",
            "zh-Hant": "從釜山站乘公車/計程車至國際客運碼頭；班次以官方為準。",
            "vi": "Từ Ga Busan đi xe buýt/taxi đến nhà ga hành khách quốc tế.",
            "th": "จากสถานีปูซานไปท่าผู้โดยสารด้วยบัส/แท็กซี่",
            "ru": "От станции Пусан на автобусе/такси к международному терминалу.",
        },
    },
    {
        "slug": "port-incheon",
        "lat": 37.4536,
        "lng": 126.6149,
        "region": "incheon",
        "type": "port",
        "note": "Incheon Port passenger terminal",
        "image": "Images/places/port-incheon.jpg",
        "address_ko": "인천 중구 월미로 115 인천항국제여객터미널",
        "name": {
            "ko": "인천항",
            "en": "Incheon Port",
            "ja": "仁川港",
            "zh": "仁川港",
            "zh-Hant": "仁川港",
            "vi": "Cảng Incheon",
            "th": "ท่าเรืออินชอน",
            "ru": "Порт Инчхон",
        },
        "desc": {
            "ko": "수도권 관문 항구. 국제여객·크루즈와 월미도·차이나타운 관광권과 가깝습니다.",
            "en": "Capital-region gateway port — passenger ferries/cruises near Wolmido and Chinatown.",
            "ja": "首都圏の玄関港。国際旅客・クルーズと月尾島・中華街観光が近い。",
            "zh": "首都圈门户港口，靠近月尾岛与中华街旅游区。",
            "zh-Hant": "首都圈門戶港口，靠近月尾島與中華街旅遊區。",
            "vi": "Cảng cửa ngõ thủ đô — gần Wolmido và phố người Hoa.",
            "th": "ท่าเรือประตูเมืองหลวง ใกล้ Wolmido และไชน่าทาวน์",
            "ru": "Порт-ворота столичного региона — рядом Вольмидо и Чайна-таун.",
        },
        "how": {
            "ko": "인천 시내·공항에서 버스·택시. 여객터미널 위치는 배편 회사 안내를 확인하세요.",
            "en": "Bus/taxi from Incheon city or the airport. Confirm the passenger terminal with your ferry operator.",
            "ja": "市内・空港からバス・タクシー。ターミナルは運航会社案内で確認。",
            "zh": "从仁川市区或机场乘公交/出租车；码头以船公司信息为准。",
            "zh-Hant": "從仁川市區或機場乘公車/計程車；碼頭以船公司資訊為準。",
            "vi": "Xe buýt/taxi từ nội thành hoặc sân bay Incheon.",
            "th": "บัส/แท็กซี่จากเมืองหรือสนามบินอินชอน",
            "ru": "Автобус/такси из города или аэропорта Инчхона.",
        },
    },
    {
        "slug": "port-jeju",
        "lat": 33.5172,
        "lng": 126.5263,
        "region": "jeju",
        "type": "port",
        "note": "Jeju Port",
        "image": "Images/places/port-jeju.jpg",
        "address_ko": "제주 제주시 임항로 제주항",
        "name": {
            "ko": "제주항",
            "en": "Jeju Port",
            "ja": "済州港",
            "zh": "济州港",
            "zh-Hant": "濟州港",
            "vi": "Cảng Jeju",
            "th": "ท่าเรือเชจู",
            "ru": "Порт Чеджу",
        },
        "desc": {
            "ko": "제주 본섬 여객항. 목포·완도 등 육지 배편과 연결되는 관문입니다.",
            "en": "Main passenger harbor on Jeju Island — ferries from Mokpo, Wando, and other mainland ports.",
            "ja": "済州本島の旅客港。木浦・莞島など本土航路の玄関。",
            "zh": "济州本岛客运港，连接木浦、莞岛等陆地航线。",
            "zh-Hant": "濟州本島客運港，連接木浦、莞島等陸地航線。",
            "vi": "Cảng hành khách chính đảo Jeju — phà từ Mokpo, Wando…",
            "th": "ท่าเรือผู้โดยสารหลักของเชจู — เรือจากโมกโพ/วันโด ฯลฯ",
            "ru": "Главный пассажирский порт Чеджу — паромы с материка.",
        },
        "how": {
            "ko": "제주시내·공항에서 버스·택시. 기상·결항이 잦을 수 있으니 출발전 확인하세요.",
            "en": "Bus/taxi from Jeju city or the airport. Check weather delays before sailing.",
            "ja": "市内・空港からバス・タクシー。欠航があり得るので出発前確認を。",
            "zh": "从济州市区或机场乘公交/出租车；出航前确认天气与班次。",
            "zh-Hant": "從濟州市區或機場乘公車/計程車；出航前確認天氣與班次。",
            "vi": "Xe buýt/taxi từ thành phố/sân bay Jeju. Kiểm tra hủy chuyến vì thời tiết.",
            "th": "บัส/แท็กซี่จากเมืองหรือสนามบินเชจู ตรวจดีเลย์อากาศก่อน",
            "ru": "Автобус/такси из города или аэропорта. Проверяйте отмены из‑за погоды.",
        },
    },
    {
        "slug": "port-mokpo",
        "lat": 34.7917,
        "lng": 126.3889,
        "region": "jeolla",
        "type": "port",
        "note": "Mokpo Port",
        "image": "Images/places/port-mokpo.jpg",
        "address_ko": "전남 목포시 해안로 목포항",
        "name": {
            "ko": "목포항",
            "en": "Mokpo Port",
            "ja": "木浦港",
            "zh": "木浦港",
            "zh-Hant": "木浦港",
            "vi": "Cảng Mokpo",
            "th": "ท่าเรือโมกโพ",
            "ru": "Порт Мокпхо",
        },
        "desc": {
            "ko": "서남해 대표 여객항. 제주행 배편과 항구 야경·유달산 관광권과 가깝습니다.",
            "en": "Major southwest passenger port — ferries to Jeju and access to harbor views / Yudalsan.",
            "ja": "西南海の代表旅客港。済州航路と港の夜景・儒達山観光が近い。",
            "zh": "西南海代表性客运港，有济州航线与港湾夜景、儒达山。",
            "zh-Hant": "西南海代表性客運港，有濟州航線與港灣夜景、儒達山。",
            "vi": "Cảng hành khách tây-nam — phà Jeju, cảnh cảng/Yudalsan.",
            "th": "ท่าเรือผู้โดยสารตะวันตกเฉียงใต้ — เรือเชจูและวิวท่าเรือ",
            "ru": "Крупный юго‑западный порт — паромы на Чеджу и виды гавани.",
        },
        "how": {
            "ko": "목포역·시외버스터미널에서 택시·시내버스. 배편 시간표는 여객선사 안내를 확인하세요.",
            "en": "Taxi/city bus from Mokpo Station or the bus terminal. Confirm ferry schedules with operators.",
            "ja": "木浦駅・バスターミナルからタクシー・市内バス。時刻は運航会社で確認。",
            "zh": "从木浦站或客运站乘出租车/公交；班次以船公司为准。",
            "zh-Hant": "從木浦站或客運站乘計程車/公車；班次以船公司為準。",
            "vi": "Taxi/xe buýt từ ga/bến xe Mokpo.",
            "th": "แท็กซี่/บัสจากสถานีโมกโพ",
            "ru": "Такси/автобус от станции или автовокзала Мокпхо.",
        },
    },
    {
        "slug": "port-yeosu",
        "lat": 34.7380,
        "lng": 127.7450,
        "region": "jeolla",
        "type": "port",
        "note": "Yeosu Port / Expo waterfront",
        "image": "Images/places/port-yeosu.jpg",
        "address_ko": "전남 여수시 여수항",
        "name": {
            "ko": "여수항",
            "en": "Yeosu Port",
            "ja": "麗水港",
            "zh": "丽水港",
            "zh-Hant": "麗水港",
            "vi": "Cảng Yeosu",
            "th": "ท่าเรือยอซู",
            "ru": "Порт Йосу",
        },
        "desc": {
            "ko": "여수 엑스포·낭만포차 일대와 이어지는 항구. 섬 배편·야경 명소와 가깝습니다.",
            "en": "Harbor linked to Yeosu Expo and the waterfront — island ferries and night views nearby.",
            "ja": "麗水エキスポや臨海エリアにつながる港。島航路・夜景スポットが近い。",
            "zh": "连接丽水世博与海滨的港口，近岛屿渡轮与夜景。",
            "zh-Hant": "連接麗水世博與海濱的港口，近島嶼渡輪與夜景。",
            "vi": "Cảng gắn với Yeosu Expo/ven biển — phà đảo và đêm gần đó.",
            "th": "ท่าเรือเชื่อม Yeosu Expo และชายฝั่ง — เรือเกาะและวิวยามค่ำ",
            "ru": "Порт у Yeosu Expo и набережной — паромы на острова и ночные виды.",
        },
        "how": {
            "ko": "여수엑스포역·시내에서 버스·택시. 배편·케이블카는 현장·앱으로 확인하세요.",
            "en": "Bus/taxi from Yeosu Expo Station or downtown. Confirm ferries and cable cars on-site.",
            "ja": "麗水エキスポ駅・市内からバス・タクシー。航路は現地・アプリで確認。",
            "zh": "从丽水世博站或市区乘公交/出租车；渡轮请现场确认。",
            "zh-Hant": "從麗水世博站或市區乘公車/計程車；渡輪請現場確認。",
            "vi": "Xe buýt/taxi từ ga Yeosu Expo hoặc trung tâm.",
            "th": "บัส/แท็กซี่จากสถานี Yeosu Expo หรือตัวเมือง",
            "ru": "Автобус/такси от станции Yeosu Expo или центра.",
        },
    },
    {
        "slug": "port-pohang",
        "lat": 36.0515,
        "lng": 129.3840,
        "region": "gyeongsang",
        "type": "port",
        "note": "Pohang Port / Yeongil Bay",
        "image": "Images/places/port-pohang.jpg",
        "address_ko": "경북 포항시 북구 포항항",
        "name": {
            "ko": "포항항",
            "en": "Pohang Port",
            "ja": "浦項港",
            "zh": "浦项港",
            "zh-Hant": "浦項港",
            "vi": "Cảng Pohang",
            "th": "ท่าเรือโพฮัง",
            "ru": "Порт Пхохан",
        },
        "desc": {
            "ko": "동해안 산업·여객이 함께하는 항구. 영일대·호미곶 여행권의 거점입니다.",
            "en": "East-coast industrial and passenger port — a base for Yeongildae and Homigot trips.",
            "ja": "東海岸の産業・旅客港。迎日台・虎尾岬観光の拠点。",
            "zh": "东海岸工业与客运港，是迎日台、虎尾岬行程的据点。",
            "zh-Hant": "東海岸工業與客運港，是迎日台、虎尾岬行程的據點。",
            "vi": "Cảng công nghiệp/hành khách bờ đông — gần Yeongildae, Homigot.",
            "th": "ท่าเรือฝั่งตะวันออก — ฐานเที่ยว Yeongildae/Homigot",
            "ru": "Восточный порт — база для Ёнильдэ и Хомигот.",
        },
        "how": {
            "ko": "포항역·시외버스터미널에서 택시·버스. 배편은 여객선 안내를 확인하세요.",
            "en": "Taxi/bus from Pohang Station or the bus terminal. Confirm ferry info with operators.",
            "ja": "浦項駅・バスターミナルからタクシー・バス。航路は運航案内で確認。",
            "zh": "从浦项站或客运站乘出租车/公交；班次以船公司为准。",
            "zh-Hant": "從浦項站或客運站乘計程車/公車；班次以船公司為準。",
            "vi": "Taxi/xe buýt từ ga/bến xe Pohang.",
            "th": "แท็กซี่/บัสจากสถานีโพฮัง",
            "ru": "Такси/автобус от станции или автовокзала Пхохана.",
        },
    },
]


TRANSPORT_KEYS = {
    "ko": {
        "legendLocker": "물품보관함",
        "legendPort": "항구",
        "filterTitle": "유형 필터",
        "filterAll": "전체",
        "filterHelp": "표시할 유형을 선택하세요",
        "lockerBadge": "물품보관 · 시간·빈칸은 앱/현장에서 확인",
        "portBadge": "항구 · 여객·크루즈 거점",
    },
    "en": {
        "legendLocker": "Lockers",
        "legendPort": "Ports",
        "filterTitle": "Type filters",
        "filterAll": "All",
        "filterHelp": "Choose which types to show",
        "lockerBadge": "Luggage storage — confirm hours/availability in app or on-site",
        "portBadge": "Port / harbor — passenger & cruise gateway",
    },
    "ja": {
        "legendLocker": "ロッカー",
        "legendPort": "港",
        "filterTitle": "種類フィルター",
        "filterAll": "すべて",
        "filterHelp": "表示する種類を選んでください",
        "lockerBadge": "荷物預かり・時間・空きはアプリ/現地で確認",
        "portBadge": "港・旅客・クルーズの拠点",
    },
    "zh": {
        "legendLocker": "行李寄存",
        "legendPort": "港口",
        "filterTitle": "类型筛选",
        "filterAll": "全部",
        "filterHelp": "选择要显示的类型",
        "lockerBadge": "行李寄存 · 时间与空位请以App/现场为准",
        "portBadge": "港口 · 客运与邮轮据点",
    },
    "zh-Hant": {
        "legendLocker": "行李寄物",
        "legendPort": "港口",
        "filterTitle": "類型篩選",
        "filterAll": "全部",
        "filterHelp": "選擇要顯示的類型",
        "lockerBadge": "行李寄物 · 時間與空位請以App/現場為準",
        "portBadge": "港口 · 客運與郵輪據點",
    },
    "vi": {
        "legendLocker": "Tủ gửi đồ",
        "legendPort": "Cảng",
        "filterTitle": "Lọc loại",
        "filterAll": "Tất cả",
        "filterHelp": "Chọn loại muốn hiện",
        "lockerBadge": "Gửi hành lý — xác nhận giờ/chỗ trống trên app hoặc tại chỗ",
        "portBadge": "Cảng — cửa ngõ hành khách & du thuyền",
    },
    "th": {
        "legendLocker": "ล็อกเกอร์",
        "legendPort": "ท่าเรือ",
        "filterTitle": "ตัวกรองประเภท",
        "filterAll": "ทั้งหมด",
        "filterHelp": "เลือกประเภทที่จะแสดง",
        "lockerBadge": "ฝากกระเป๋า — ยืนยันเวลา/ช่องว่างในแอปหรือหน้างาน",
        "portBadge": "ท่าเรือ — จุดผู้โดยสารและเรือสำราญ",
    },
    "ru": {
        "legendLocker": "Камеры хранения",
        "legendPort": "Порты",
        "filterTitle": "Фильтр типов",
        "filterAll": "Все",
        "filterHelp": "Выберите типы для показа",
        "lockerBadge": "Камера хранения — часы и места уточняйте в приложении или на месте",
        "portBadge": "Порт — пассажирский и круизный узел",
    },
}

APPS_KEYS = {
    "ko": {
        "totaLockerName": "또타라커 (T Locker)",
        "totaLockerDesc": "서울 지하철 물품보관함 위치·빈칸을 찾고 예약·결제할 수 있습니다. 쇼핑·체크아웃 날 짐 보관에 유용합니다.",
        "ddareungiName": "따릉이 (서울자전거)",
        "ddareungiDesc": "서울 공공자전거. 앱으로 대여소·이용권 확인 후 QR로 대여하세요. (카드·앱 준비가 필요할 수 있습니다)",
    },
    "en": {
        "totaLockerName": "Tota Locker (T Locker)",
        "totaLockerDesc": "Find Seoul subway lockers, check availability, and reserve/pay in-app — handy on shopping or checkout days.",
        "ddareungiName": "Ddareungi (Seoul Bike)",
        "ddareungiDesc": "Seoul’s public bike share. Use the app for stations and passes, then unlock by QR. (App/card setup may be needed.)",
    },
    "ja": {
        "totaLockerName": "もうたロッカー (T Locker)",
        "totaLockerDesc": "ソウル地下鉄のロッカー位置・空きを調べ、予約・支払いできるアプリ。買い物やチェックアウト日に便利。",
        "ddareungiName": "トゥルンイ (ソウル自転車)",
        "ddareungiDesc": "ソウルの公共自転車。アプリでポートと利用券を確認しQRで貸出。(アプリ/カード準備が必要な場合あり)",
    },
    "zh": {
        "totaLockerName": "又他储物柜 (T Locker)",
        "totaLockerDesc": "查找首尔地铁储物柜位置与空位，并在App内预约付款。适合逛街或退房当天。",
        "ddareungiName": "首尔公共自行车（따릉이）",
        "ddareungiDesc": "首尔公共自行车。用App查看站点与通票，再扫QR租车。（可能需要App/卡片准备）",
    },
    "zh-Hant": {
        "totaLockerName": "又他置物櫃 (T Locker)",
        "totaLockerDesc": "查找首爾地鐵置物櫃位置與空位，並在App內預約付款。適合逛街或退房當天。",
        "ddareungiName": "首爾公共自行車（따릉이）",
        "ddareungiDesc": "首爾公共自行車。用App查看站點與通票，再掃QR租車。（可能需要App/卡片準備）",
    },
    "vi": {
        "totaLockerName": "Tota Locker (T Locker)",
        "totaLockerDesc": "Tìm tủ gửi đồ tàu điện Seoul, xem chỗ trống và đặt/thanh toán trong app — tiện ngày shopping/checkout.",
        "ddareungiName": "Ddareungi (xe đạp Seoul)",
        "ddareungiDesc": "Xe đạp công cộng Seoul. Dùng app xem trạm/vé rồi mở bằng QR. (Có thể cần chuẩn bị app/thẻ.)",
    },
    "th": {
        "totaLockerName": "Tota Locker (T Locker)",
        "totaLockerDesc": "ค้นหาล็อกเกอร์รถไฟใต้ดินโซล ดูช่องว่าง และจอง/จ่ายในแอป — เหมาะวันช้อปหรือเช็คเอาต์",
        "ddareungiName": "Ddareungi (จักรยานโซล)",
        "ddareungiDesc": "จักรยานสาธารณะโซล ใช้แอปดูสถานี/บัตร แล้วปลดล็อกด้วย QR (อาจต้องเตรียมแอป/บัตร)",
    },
    "ru": {
        "totaLockerName": "Tota Locker (T Locker)",
        "totaLockerDesc": "Находите камеры хранения в метро Сеула, смотрите свободные места и бронируйте/оплачивайте в приложении.",
        "ddareungiName": "Ddareungi (велосипед Сеула)",
        "ddareungiDesc": "Общественный велопрокат Сеула. В приложении — станции и билеты, разблокировка по QR. (Может понадобиться карта/приложение.)",
    },
}

TYPE_COLORS = {
    "city": ((240, 193, 75), (40, 55, 70)),
    "nature": ((62, 207, 142), (20, 55, 45)),
    "heritage": ((232, 106, 92), (55, 30, 35)),
    "airport": ((74, 124, 255), (20, 35, 70)),
    "info": ((138, 150, 163), (35, 40, 48)),
    "locker": ((180, 140, 90), (45, 35, 25)),
    "port": ((70, 170, 200), (15, 45, 60)),
}


def make_cover(path: Path, top: tuple[int, int, int], bottom: tuple[int, int, int], label: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    w, h = 960, 640
    img = Image.new("RGB", (w, h), bottom)
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / (h - 1)
        r = int(top[0] * (1 - t) + bottom[0] * t)
        g = int(top[1] * (1 - t) + bottom[1] * t)
        b = int(top[2] * (1 - t) + bottom[2] * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    # soft vignette bands
    for i in range(0, w, 48):
        draw.rectangle([i, 0, i + 16, h], fill=None, outline=None)
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.rectangle([i, int(h * 0.15), i + 2, int(h * 0.85)], fill=(255, 255, 255, 18))
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)
    # title plate
    draw.rounded_rectangle([48, h - 140, w - 48, h - 48], radius=18, fill=(8, 16, 22, 200) if False else (12, 22, 30))
    try:
        font = ImageFont.truetype("arial.ttf", 42)
    except Exception:
        font = ImageFont.load_default()
    draw.text((72, h - 118), label, fill=(245, 248, 250), font=font)
    img.save(path, "JPEG", quality=86, optimize=True)


def patch_coords() -> int:
    text = COORDS.read_text(encoding="utf-8")
    # update type comment
    text = re.sub(
        r'type: "city" \| "nature" \| "heritage" \| "airport" \| "info".*?(?=\n \*/)',
        'type: "city" | "nature" | "heritage" | "airport" | "info" | "locker" | "port"\n'
        ' *   city     — urban nightlife / shopping / modern landmarks\n'
        ' *   nature   — mountains, beaches, parks, scenic outdoors\n'
        ' *   heritage — palaces, temples, historic / cultural villages\n'
        ' *   airport  — major passenger airports (plane icon on map)\n'
        ' *   info     — embassies / visitor help centers (muted secondary badge)\n'
        ' *   locker   — luggage storage / coin lockers (station & airport)\n'
        ' *   port     — major harbors / passenger ferry terminals',
        text,
        count=1,
        flags=re.S,
    )
    added = 0
    for p in NEW_PLACES:
        if f'slug: "{p["slug"]}"' in text:
            continue
        img = p.get("image") or ""
        img_part = f', image: "{img}"' if img else ""
        line = (
            f'  {{ slug: "{p["slug"]}", lat: {p["lat"]}, lng: {p["lng"]}, '
            f'region: "{p["region"]}", type: "{p["type"]}", note: "{p["note"]}"{img_part} }},'
        )
        # insert before closing ];
        text = text.rstrip()
        if text.endswith("];"):
            body = text[:-2].rstrip()
            if not body.endswith(","):
                # last entry may lack comma
                body += ","
            text = body + "\n" + line + "\n];\n"
            added += 1
    COORDS.write_text(text, encoding="utf-8", newline="\n")
    return added


def place_entry(p: dict, lang: str) -> dict:
    labels = REGION_LABEL.get(p["region"], REGION_LABEL["seoul"])
    note = LOCKER_NOTE[lang] if p["type"] == "locker" else ""
    desc = p["desc"][lang]
    if note:
        desc = f"{desc} {note}"
    maps_url, maps_embed = maps_urls(p["address_ko"], "en" if lang == "en" else "ko")
    body_block = {"type": "text"}
    for L in i18n_store.LANGS:
        d = p["desc"][L]
        if p["type"] == "locker":
            d = f"{d} {LOCKER_NOTE[L]}"
        body_block[L] = f"{d}\n\n{p['how'][L]}"
    entry = {
        "name": p["name"][lang],
        "desc": desc,
        "how": p["how"][lang],
        "address": p["address_ko"],
        "regionLabel": labels.get(lang) or labels["ko"],
        "region": p["region"],
        "mapsUrl": maps_url,
        "mapsEmbedUrl": maps_embed,
        "body": [body_block],
    }
    if p.get("image"):
        entry["image"] = p["image"]
    return entry


def update_i18n() -> None:
    bundle = i18n_store.load_all()
    for lang in i18n_store.LANGS:
        data = bundle[lang]
        transport = data.setdefault("transport", {})
        transport.update(TRANSPORT_KEYS[lang])
        apps = data.setdefault("apps", {})
        apps.update(APPS_KEYS[lang])
        places = data.setdefault("places", {})
        for p in NEW_PLACES:
            places[p["slug"]] = place_entry(p, lang)
    i18n_store.save_all(bundle)


def make_images() -> None:
    labels = {
        "city": "City",
        "nature": "Nature",
        "heritage": "Heritage",
        "airport": "Airport",
        "info": "Info",
        "locker": "Lockers",
        "port": "Ports",
    }
    for kind, (top, bottom) in TYPE_COLORS.items():
        make_cover(IMG_TYPES / f"{kind}.jpg", top, bottom, labels[kind])
    for p in NEW_PLACES:
        kind = p["type"]
        top, bottom = TYPE_COLORS[kind]
        make_cover(IMG_PLACES / f"{p['slug']}.jpg", top, bottom, p["name"]["en"][:40])


def main() -> None:
    n = patch_coords()
    update_i18n()
    make_images()
    print(i18n_store.build_bundle())
    print(f"coords added: {n}; places: {len(NEW_PLACES)}")


if __name__ == "__main__":
    main()
