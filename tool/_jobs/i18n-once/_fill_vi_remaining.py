#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fill remaining Vietnamese gaps in vi.json only (bodies/callouts + a few scalars)."""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

from deep_translator import GoogleTranslator

ROOT = Path(__file__).resolve().parent
VI_PATH = ROOT / "vi.json"


def load() -> dict:
    return json.loads(VI_PATH.read_text(encoding="utf-8"))


def save(data: dict) -> None:
    VI_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def join3(title: str, mistake: str, body: str) -> str:
    return f"{title}\n\n{mistake}\n\n{body}"


def needs_vi(block: dict) -> bool:
    en = str(block.get("en") or "").strip()
    vi = str(block.get("vi") or "").strip()
    if not en:
        return False
    return (not vi) or vi == en


def fill_tips_bodies(data: dict) -> int:
    tips = data.setdefault("tips", {})
    n = 0

    daily_map = [
        ("mapTitle", "mapMistake", "mapBody"),
        ("trashTitle", "trashMistake", "trashBody"),
        ("weekendTitle", "weekendMistake", "weekendBody"),
        ("convenienceTitle", "convenienceMistake", "convenienceBody"),
        ("rainTitle", "rainMistake", "rainBody"),
    ]
    daily = tips.get("dailyBody") or []
    for i, keys in enumerate(daily_map):
        if i >= len(daily) or not isinstance(daily[i], dict):
            continue
        if daily[i].get("type") != "text":
            continue
        title, mistake, body = (tips.get(k) or "" for k in keys)
        if not (title and mistake and body):
            continue
        daily[i]["vi"] = join3(title, mistake, body)
        n += 1

    transport_map = [
        ("cardTitle", "cardMistake", "cardBody"),
        ("rushTitle", "rushMistake", "rushBody"),
        ("exitTitle", "exitMistake", "exitBody"),
        ("etiquetteTitle", "etiquetteMistake", "etiquetteBody"),
    ]
    transport = tips.get("transportBody") or []
    for i, keys in enumerate(transport_map):
        if i >= len(transport) or not isinstance(transport[i], dict):
            continue
        if transport[i].get("type") != "text":
            continue
        title, mistake, body = (tips.get(k) or "" for k in keys)
        if not (title and mistake and body):
            continue
        transport[i]["vi"] = join3(title, mistake, body)
        n += 1

    # restaurant callout
    for b in tips.get("restaurantBody") or []:
        if isinstance(b, dict) and b.get("type") == "callout" and needs_vi(b):
            b["vi"] = (
                "Tóm lại: nhà hàng Hàn thông thường không tip. "
                "Thanh toán đúng số trên hóa đơn tại quầy."
            )
            n += 1

    return n


def fill_from_scalar_callouts(data: dict) -> int:
    """Copy souvenir *Tip / fun *Price|*Tip scalars into matching callout blocks."""
    n = 0

    souvenir = data.get("souvenir") or {}
    souvenir_pairs = [
        ("maskBody", "maskTip"),
        ("stationeryBody", "stationeryTip"),
        ("oliveBody", "oliveTip"),
        ("daisoBody", "daisoTip"),
        ("snackBody", "snackTip"),
        ("ramenBody", "ramenTip"),
        ("teaBody", "teaTip"),
        ("honeyBody", "honeyTip"),
        ("socksBody", "socksTip"),
        ("sheetBody", "sheetTip"),
        ("sunscreenBody", "sunscreenTip"),
        ("lipstickBody", "lipstickTip"),
        ("kpopBody", "kpopTip"),
        ("spaBody", "spaTip"),
        ("uniqloBody", "uniqloTip"),
        ("hanbokBody", "hanbokTip"),
    ]
    for body_key, tip_key in souvenir_pairs:
        blocks = souvenir.get(body_key)
        tip = souvenir.get(tip_key)
        if not isinstance(blocks, list) or not isinstance(tip, str) or not tip.strip():
            continue
        for b in blocks:
            if isinstance(b, dict) and b.get("type") == "callout" and needs_vi(b):
                # Prefer Vietnamese tip scalar even if English title still says Buying tip
                b["vi"] = tip
                n += 1

    fun = data.get("fun") or {}
    fun_pairs = [
        ("noraebangBody", ["noraebangPrice", "noraebangTip"]),
        ("mangaBody", ["mangaPrice", "mangaTip"]),
        ("boardgameBody", ["boardgamePrice", "boardgameTip"]),
        ("unmannedBody", ["unmannedPrice", "unmannedTip"]),
        ("photoboothBody", ["photoboothPrice", "photoboothTip"]),
        ("pcbangBody", ["pcbangPrice", "pcbangTip"]),
        ("escapeBody", ["escapePrice", "escapeTip"]),
        ("jjimBody", ["jjimPrice", "jjimTip"]),
        ("lotteBody", ["lottePrice", "lotteTip"]),
        ("everlandBody", ["everlandPrice", "everlandTip"]),
    ]
    for body_key, scalar_keys in fun_pairs:
        blocks = fun.get(body_key)
        if not isinstance(blocks, list):
            continue
        scalars = [fun.get(k) for k in scalar_keys if isinstance(fun.get(k), str)]
        if not scalars:
            continue
        callouts = [
            b for b in blocks if isinstance(b, dict) and b.get("type") == "callout"
        ]
        for i, b in enumerate(callouts):
            if i < len(scalars) and needs_vi(b):
                text = scalars[i]
                # Fix bad MT "Giá rung cảm" leftover
                text = text.replace("Giá rung cảm", "Khoảng giá")
                b["vi"] = text
                n += 1

    return n


def translate_en(text: str, gt: GoogleTranslator) -> str:
    text = text.strip()
    if not text:
        return text
    # Keep URLs intact — translate in chunks around them
    parts = re.split(r"(https?://\S+)", text)
    out = []
    for part in parts:
        if part.startswith("http"):
            out.append(part)
            continue
        if not part.strip():
            out.append(part)
            continue
        try:
            tr = (gt.translate(part) or "").strip()
            out.append(tr if tr else part)
            time.sleep(0.05)
        except Exception as exc:  # noqa: BLE001
            print("  translate err:", exc)
            out.append(part)
    return "".join(out)


def fill_beforetrip_callouts(data: dict) -> int:
    gt = GoogleTranslator(source="en", target="vi")
    n = 0
    before = data.get("beforeTrip") or {}
    # curated overrides for quality (EN fingerprint -> VI)
    curated = {
        "Treat travel insurance as a baseline for medical costs, lost items, and delays.": (
            "Hãy coi bảo hiểm du lịch là nền tảng cho chi phí y tế, thất lạc đồ và trì hoãn chuyến đi."
        ),
        "Small bills (₩1,000 / ₩5,000) help at markets. Keep a little cash for transit top-ups too.": (
            "Tiền lẻ (₩1,000 / ₩5,000) hữu ích ở chợ. Giữ một ít tiền mặt để nạp thẻ giao thông nữa."
        ),
        "You'll want maps on landing — note your eSIM install steps beforehand.": (
            "Bạn sẽ cần bản đồ ngay khi hạ cánh — ghi sẵn các bước cài eSIM trước."
        ),
        "Adapters are sold at Daiso, convenience stores, and airports — but stock can run out on arrival or holidays, so packing one is safer.": (
            "Ổ chuyển đổi bán ở Daiso, cửa hàng tiện lợi và sân bay — nhưng hàng có thể hết khi vừa đến hoặc ngày lễ, nên mang sẵn một cái an toàn hơn."
        ),
        "Leave suitcase space for Olive Young, Daiso, and snack gifts — they add up fast.": (
            "Chừa chỗ trong vali cho Olive Young, Daiso và quà snack — chúng tăng nhanh."
        ),
        "Overcharging is rare in Seoul these days — metered regular taxis are the norm. For extra peace of mind, you can request a ride in Kakao T or similar apps. If a fare still feels off, note the license plate and the taxi license display inside, then ask Seoul’s Dasan Call Center 120, or tourist helpline 1330. Some cabs also show an in-car QR for feedback.": (
            "Ở Seoul hiện nay việc chặt chém khá hiếm — taxi thường chạy đồng hồ. Để yên tâm hơn, có thể gọi xe trên Kakao T hoặc app tương tự. "
            "Nếu cước vẫn thấy lạ, ghi biển số và giấy phép taxi trong xe, rồi hỏi Trung tâm Dasan Call của Seoul 120, hoặc đường dây du lịch 1330. "
            "Một số xe cũng có mã QR trong xe để góp ý."
        ),
        "Tip: More places welcome solo diners (counter seats, 1-person sets). Search maps for “honbap” / single seating.": (
            "Mẹo: Ngày càng nhiều nơi chào đón khách đi một mình (ghế quầy, suất 1 người). Tìm trên bản đồ “honbap” / chỗ ngồi một người."
        ),
        "Official info: check SES pages on Korea Immigration https://www.immigration.go.kr and Hi Korea https://www.hikorea.go.kr for eligibility and enrollment locations.": (
            "Thông tin chính thức: xem trang SES trên Korea Immigration https://www.immigration.go.kr và Hi Korea https://www.hikorea.go.kr "
            "để biết điều kiện và địa điểm đăng ký."
        ),
        "Common mistakes: confusing it with K-ETA, filing too early (72-hour expiry), wrong hotel address, paid fake sites. If plans change, check/edit on the official site before immigration.": (
            "Lỗi thường gặp: nhầm với K-ETA, khai quá sớm (hết hạn 72 giờ), sai địa chỉ khách sạn, trang giả thu phí. "
            "Nếu đổi kế hoạch, kiểm tra/sửa trên trang chính thức trước khi làm thủ tục nhập cảnh."
        ),
        "Follow official/kiosk instructions. App signup and balance checks are usually explained on-site. Avoid unnecessary paid agents.": (
            "Làm theo hướng dẫn chính thức/ki-ốt. Đăng ký app và kiểm tra số dư thường được giải thích tại chỗ. Tránh đại lý thu phí không cần thiết."
        ),
        "Long weekends get busy at sights, transit, and popular restaurants. Some shops and offices close. Book early, as in peak season.": (
            "Cuối tuần dài thường đông ở điểm tham quan, giao thông và quán nổi tiếng. Một số cửa hàng và cơ quan đóng cửa. Hãy đặt sớm như mùa cao điểm."
        ),
        "Spring (Mar–May) and autumn (Sep–early/mid Nov, outside Chuseok week) are usually easier for outdoor trips. Avoid peak holiday crowds if you want a calmer first visit.": (
            "Mùa xuân (thg 3–5) và mùa thu (thg 9–đầu/giữa thg 11, ngoài tuần Chuseok) thường dễ chịu hơn cho chuyến ngoài trời. "
            "Tránh đám đông ngày lễ cao điểm nếu muốn chuyến đầu êm hơn."
        ),
        "Some regions (and Jeju) are easier by rental car. Even if you only use subway/bus inside Seoul, day one feels much lighter.": (
            "Một số vùng (và Jeju) thuận hơn với xe thuê. Dù chỉ đi tàu/xe buýt trong Seoul, ngày đầu cũng nhẹ nhàng hơn nhiều."
        ),
        "A quick look around helps more than perfect etiquette. When unsure, quietly mirror nearby tables.": (
            "Quan sát nhanh xung quanh hữu ích hơn phép lịch sự hoàn hảo. Khi không chắc, hãy lặng lẽ làm theo các bàn gần đó."
        ),
        "Find more trip-ready phrases in Useful Korean. Even a quick skim of daily, dining, and transit tabs before you fly makes the first days calmer.": (
            "Xem thêm câu sẵn dùng trong Tiếng Hàn hữu ích. Chỉ cần đọc nhanh các tab hàng ngày, ăn uống và di chuyển trước khi bay "
            "cũng khiến những ngày đầu dễ chịu hơn."
        ),
    }

    for key, blocks in list(before.items()):
        if not isinstance(blocks, list):
            continue
        for b in blocks:
            if not isinstance(b, dict) or b.get("type") != "callout":
                continue
            if not needs_vi(b):
                continue
            en = str(b.get("en") or "").strip()
            # try curated by exact or prefix
            vi = curated.get(en)
            if not vi:
                for cen, cvi in curated.items():
                    if en.startswith(cen[:60]):
                        vi = cvi
                        break
            if not vi:
                print(f"  MT beforeTrip.{key} callout…")
                vi = translate_en(en, gt)
            b["vi"] = vi
            n += 1
    return n


def polish_scalars(data: dict) -> int:
    n = 0
    tips = data.setdefault("tips", {})
    for k, v in {
        "tabOlive": "Olive Young",
        "tabDaiso": "Daiso",
        "tabWifi": "Wi-Fi",
        "tabTaxi": "Taxi",
        "noTipTitle": "Tip",
    }.items():
        if tips.get(k) != v:
            tips[k] = v
            n += 1

    before = data.setdefault("beforeTrip", {})
    if before.get("tabTaxi") != "Taxi":
        before["tabTaxi"] = "Taxi"
        n += 1

    fun = data.setdefault("fun", {})
    if fun.get("jjimTitle") in (None, "", "Jjimjilbang (spa)"):
        fun["jjimTitle"] = "Jjimjilbang (xông hơi)"
        n += 1
    if fun.get("everlandTitle") in (None, "", "Everland"):
        fun["everlandTitle"] = "Everland"  # brand intentional
    # Fix Price vibe MT leftovers in fun scalars
    for k, v in list(fun.items()):
        if isinstance(v, str) and "Giá rung cảm" in v:
            fun[k] = v.replace("Giá rung cảm", "Khoảng giá")
            n += 1

    shopping = data.setdefault("shopping", {})
    if shopping.get("dutyTitle") in (None, "", "Duty-free & tax free"):
        shopping["dutyTitle"] = "Miễn thuế & hoàn thuế"
        n += 1

    foods = data.setdefault("foodsHub", {})
    if foods.get("eyebrow") in (None, "", "Korea Travel Guidebook"):
        foods["eyebrow"] = "Cẩm nang du lịch Hàn Quốc"
        n += 1

    # areas: translate slash labels gently
    areas = data.get("areas") or {}
    area_map = {
        "Jongno": "Jongno",
        "Jung / Myeongdong": "Jung / Myeongdong",
        "Yongsan / Itaewon": "Yongsan / Itaewon",
        "Mapo / Hongdae": "Mapo / Hongdae",
        "Seongbuk": "Seongbuk",
        "Gangnam / Apgujeong": "Gangnam / Apgujeong",
        "Songpa / Jamsil": "Songpa / Jamsil",
        "Suwon": "Suwon",
        "Seongnam / Bundang": "Seongnam / Bundang",
        "Goyang / Ilsan": "Goyang / Ilsan",
        "Jung / Wolmi": "Jung / Wolmi",
        "Nampo / Jagalchi": "Nampo / Jagalchi",
        "Seocho · Bangbae": "Seocho · Bangbae",
    }
    # leave place-name areas as romaji intentional

    # travelUtils cities with country — Vietnamese country names
    tu = data.setdefault("travelUtils", {}).setdefault("cities", {})
    city_map = {
        "Manila (Philippines)": "Manila (Philippines)",
        "Kuala Lumpur (Malaysia)": "Kuala Lumpur (Malaysia)",
        "Jakarta (Indonesia)": "Jakarta (Indonesia)",
        "Dubai (UAE)": "Dubai (UAE)",
        "Toronto (Canada)": "Toronto (Canada)",
        "Vancouver (Canada)": "Vancouver (Canada)",
        "São Paulo (Brazil)": "São Paulo (Brazil)",
        "Auckland (New Zealand)": "Auckland (New Zealand)",
        "Honolulu (Hawaii)": "Honolulu (Hawaii)",
        "Singapore": "Singapore",
    }
    # Prefer Vietnamese country labels where natural
    city_vi = {
        "Manila (Philippines)": "Manila (Philippines)",
        "Kuala Lumpur (Malaysia)": "Kuala Lumpur (Malaysia)",
        "Jakarta (Indonesia)": "Jakarta (Indonesia)",
        "Dubai (UAE)": "Dubai (UAE)",
        "Toronto (Canada)": "Toronto (Canada)",
        "Vancouver (Canada)": "Vancouver (Canada)",
        "São Paulo (Brazil)": "São Paulo (Brazil)",
        "Auckland (New Zealand)": "Auckland (New Zealand)",
        "Honolulu (Hawaii)": "Honolulu (Hawaii)",
    }
    for k, v in list(tu.items()):
        if isinstance(v, str) and v in city_vi and tu[k] != city_vi[v]:
            # already same intentionally for international city names
            pass

    # restaurantFields
    rf = data.setdefault("restaurantFields", {})
    if rf.get("sourceGoogle") == "Google":
        pass  # brand intentional

    # apps yeogi descriptive
    apps = data.setdefault("apps", {})
    if apps.get("yeogiName") == "Yeogi Eottae (Goodchoice)":
        apps["yeogiName"] = "Yeogi Eottae (Goodchoice)"  # brand intentional
        # leave

    return n


def fill_remaining_callouts_mt(data: dict) -> int:
    """Any leftover text/callout still == en → Google translate."""
    gt = GoogleTranslator(source="en", target="vi")
    n = 0

    def walk(obj, path=""):
        nonlocal n
        if isinstance(obj, dict):
            if obj.get("type") in ("text", "callout") and needs_vi(obj):
                en = str(obj.get("en") or "").strip()
                print(f"  MT leftover {path}…")
                obj["vi"] = translate_en(en, gt)
                n += 1
            for k, v in obj.items():
                walk(v, f"{path}.{k}" if path else k)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                walk(v, f"{path}[{i}]")

    walk(data)
    return n


def main() -> None:
    data = load()
    lang_menu = (data.get("common") or {}).get("langMenu")

    print("1) tips bodies…")
    print("  filled", fill_tips_bodies(data))

    print("2) souvenir/fun callouts from scalars…")
    print("  filled", fill_from_scalar_callouts(data))

    print("3) beforeTrip callouts…")
    print("  filled", fill_beforetrip_callouts(data))

    print("4) polish scalars…")
    print("  updated", polish_scalars(data))

    print("5) leftover body/callout MT…")
    print("  filled", fill_remaining_callouts_mt(data))

    if lang_menu is not None:
        data.setdefault("common", {})["langMenu"] = lang_menu

    save(data)
    print("saved vi.json")


if __name__ == "__main__":
    main()
