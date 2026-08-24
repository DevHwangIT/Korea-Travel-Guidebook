#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fill remaining Thai gaps in th.json only (bodies/callouts + a few scalars)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TH_PATH = ROOT / "th.json"


def load() -> dict:
    return json.loads(TH_PATH.read_text(encoding="utf-8"))


def save(data: dict) -> None:
    TH_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def needs_th(block: dict) -> bool:
    en = str(block.get("en") or "").strip()
    th = str(block.get("th") or "").strip()
    if not en:
        return False
    return (not th) or th == en or th == str(block.get("ko") or "").strip()


def fill_tips_callout(data: dict) -> int:
    tips = data.setdefault("tips", {})
    n = 0
    for b in tips.get("restaurantBody") or []:
        if isinstance(b, dict) and b.get("type") == "callout" and needs_th(b):
            b["th"] = (
                "สรุป: ร้านอาหารเกาหลีทั่วไปไม่คาดหวังทิป "
                "ชำระตามยอดในใบเสร็จที่เคาน์เตอร์"
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
            if isinstance(b, dict) and b.get("type") == "callout" and needs_th(b):
                b["th"] = tip
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
            if i < len(scalars) and needs_th(b):
                b["th"] = scalars[i]
                n += 1

    return n


def fill_beforetrip_callouts(data: dict) -> int:
    n = 0
    before = data.get("beforeTrip") or {}
    curated = {
        "Treat travel insurance as a baseline for medical costs, lost items, and delays.": (
            "ถือว่าประกันการเดินทางเป็นพื้นฐานสำหรับค่ารักษา พัสดุหาย และการล่าช้าของเที่ยวบิน"
        ),
        "Small bills (₩1,000 / ₩5,000) help at markets. Keep a little cash for transit top-ups too.": (
            "ธนบัตรเล็ก (₩1,000 / ₩5,000) มีประโยชน์ที่ตลาด "
            "เก็บเงินสดไว้เล็กน้อยสำหรับเติมบัตรโดยสารด้วย"
        ),
        "You'll want maps on landing — note your eSIM install steps beforehand.": (
            "เมื่อลงเครื่องคุณจะต้องการแผนที่ทันที — จดขั้นตอนติดตั้ง eSIM ไว้ล่วงหน้า"
        ),
        "Adapters are sold at Daiso, convenience stores, and airports — but stock can run out on arrival or holidays, so packing one is safer.": (
            "อะแดปเตอร์มีขายที่ Daiso ร้านสะดวกซื้อ และสนามบิน — "
            "แต่ของอาจหมดเมื่อเพิ่งถึงหรือช่วงวันหยุด ดังนั้นพกมาหนึ่งอันจะชัวร์กว่า"
        ),
        "Leave suitcase space for Olive Young, Daiso, and snack gifts — they add up fast.": (
            "เว้นที่ในกระเป๋าสำหรับ Olive Young, Daiso และของขวัญขนม — สะสมเร็วมาก"
        ),
        "Overcharging is rare in Seoul these days — metered regular taxis are the norm. For extra peace of mind, you can request a ride in Kakao T or similar apps. If a fare still feels off, note the license plate and the taxi license display inside, then ask Seoul’s Dasan Call Center 120, or tourist helpline 1330. Some cabs also show an in-car QR for feedback.": (
            "ปัจจุบันที่โซลการเรียกเก็บเกินจริงพบได้น้อย — แท็กซี่ปกติใช้มิเตอร์เป็นหลัก "
            "เพื่อความสบายใจ สามารถเรียกรถผ่าน Kakao T หรือแอปคล้ายกัน "
            "หากค่าโดยสารยังรู้สึกผิดปกติ ให้จดทะเบียนรถและใบอนุญาตแท็กซี่ในรถ "
            "แล้วสอบถามศูนย์ Dasan Call ของโซล 120 หรือสายด่วนนักท่องเที่ยว 1330 "
            "บางคันมี QR ในรถสำหรับส่งความคิดเห็นด้วย"
        ),
        "Tip: More places welcome solo diners (counter seats, 1-person sets). Search maps for “honbap” / single seating.": (
            "เคล็ดลับ: ร้านที่ยินดีรับลูกค้าคนเดียวมีมากขึ้น (ที่นั่งเคาน์เตอร์ / เซต 1 คน) "
            "ค้นหาในแผนที่ว่า “honbap” หรือที่นั่งคนเดียว"
        ),
        "Official info: check SES pages on Korea Immigration https://www.immigration.go.kr and Hi Korea https://www.hikorea.go.kr for eligibility and enrollment locations.": (
            "ข้อมูลทางการ: ดูหน้า SES บน Korea Immigration https://www.immigration.go.kr "
            "และ Hi Korea https://www.hikorea.go.kr เพื่อคุณสมบัติและจุดลงทะเบียน"
        ),
        "Common mistakes: confusing it with K-ETA, filing too early (72-hour expiry), wrong hotel address, paid fake sites. If plans change, check/edit on the official site before immigration.": (
            "ความผิดพลาดที่พบบ่อย: สับสนกับ K-ETA, ยื่นเร็วเกินไป (หมดอายุ 72 ชั่วโมง), "
            "ที่อยู่โรงแรมผิด, เว็บปลอมที่เก็บเงิน "
            "หากแผนเปลี่ยน ให้ตรวจสอบ/แก้ไขบนเว็บไซต์ทางการก่อนผ่านด่านตรวจคนเข้าเมือง"
        ),
        "Follow official/kiosk instructions. App signup and balance checks are usually explained on-site. Avoid unnecessary paid agents.": (
            "ทำตามคำแนะนำทางการ/ตู้คีออสก์ การสมัครแอปและเช็คยอดมักอธิบายที่หน้างาน "
            "หลีกเลี่ยงเอเจนต์ที่เก็บค่าบริการโดยไม่จำเป็น"
        ),
        "Long weekends get busy at sights, transit, and popular restaurants. Some shops and offices close. Book early, as in peak season.": (
            "วันหยุดยาวมักคนแน่นที่สถานที่ท่องเที่ยว การเดินทาง และร้านดัง "
            "ร้านและสำนักงานบางแห่งปิด จองล่วงหน้าเหมือนก่อนช่วงพีค"
        ),
        "Spring (Mar–May) and autumn (Sep–early/mid Nov, outside Chuseok week) are usually easier for outdoor trips. Avoid peak holiday crowds if you want a calmer first visit.": (
            "ฤดูใบไม้ผลิ (มี.ค.–พ.ค.) และฤดูใบไม้ร่วง (ก.ย.–ต้น/กลาง พ.ย. นอกสัปดาห์ชูซ็อก) "
            "มักเหมาะกับการเที่ยวนอกบ้าน "
            "เลี่ยงฝูงชนช่วงวันหยุดพีคหากอยากให้ทริปแรกสงบกว่า"
        ),
        "Some regions (and Jeju) are easier by rental car. Even if you only use subway/bus inside Seoul, day one feels much lighter.": (
            "บางภูมิภาค (และเชจู) สะดวกกว่าด้วยรถเช่า "
            "แม้ในโซลจะใช้แค่รถไฟใต้ดิน/รถเมล์ วันแรกก็รู้สึกเบาขึ้นมาก"
        ),
        "A quick look around helps more than perfect etiquette. When unsure, quietly mirror nearby tables.": (
            "มองรอบๆ สักนิดช่วยได้มากกว่ามารยาทที่สมบูรณ์แบบ "
            "เมื่อไม่แน่ใจ ให้ทำตามโต๊ะใกล้เคียงอย่างเงียบๆ"
        ),
        "Find more trip-ready phrases in Useful Korean. Even a quick skim of daily, dining, and transit tabs before you fly makes the first days calmer.": (
            "ดูประโยคพร้อมใช้เพิ่มในภาษาเกาหลีที่มีประโยชน์ "
            "เพียงอ่านคร่าวๆ แท็บชีวิตประจำวัน อาหาร และการเดินทางก่อนบิน "
            "ก็ทำให้วันแรกๆ สบายขึ้น"
        ),
    }

    for key, blocks in list(before.items()):
        if not isinstance(blocks, list):
            continue
        for b in blocks:
            if not isinstance(b, dict) or b.get("type") != "callout":
                continue
            if not needs_th(b):
                continue
            en = str(b.get("en") or "").strip()
            th = curated.get(en)
            if not th:
                for cen, cth in curated.items():
                    if en.startswith(cen[:50]) or cen.startswith(en[:50]):
                        th = cth
                        break
            if not th:
                # fuzzy: match by first 40 ascii letters
                en_head = "".join(ch for ch in en[:60] if ch.isascii())
                for cen, cth in curated.items():
                    cen_head = "".join(ch for ch in cen[:60] if ch.isascii())
                    if en_head and cen_head and (
                        en_head[:40] in cen_head or cen_head[:40] in en_head
                    ):
                        th = cth
                        break
            if not th:
                print(f"  MISSING curated beforeTrip.{key}: {en[:80]!r}")
                continue
            b["th"] = th
            n += 1
    return n


def polish_scalars(data: dict) -> int:
    n = 0
    foods = data.setdefault("foodsHub", {})
    if foods.get("eyebrow") in (None, "", "Korea Travel Guidebook"):
        foods["eyebrow"] = "คู่มือท่องเที่ยวเกาหลี"
        n += 1

    # Brand tabs intentional English OK; keep Olive Young / Daiso / Taxi as brands
    tips = data.setdefault("tips", {})
    if tips.get("tabOlive") == "Olive Young":
        pass  # brand
    if tips.get("tabDaiso") == "Daiso":
        pass

    # Light polish for badly MT'd souvenir tips that we just copy into callouts
    souvenir = data.setdefault("souvenir", {})
    polish_map = {
        "lipstickTip": (
            "ทิปซื้อ\n\nขอโทนสีเงียบ/โทนอุ่นจากพนักงาน "
            "ระวังสุขอนามัยของเทสเตอร์ และเก็บใบเสร็จไว้กรณีคืนสินค้า"
        ),
        "honeyTip": (
            "ทิปซื้อ\n\nขวดปิดผนึกมีฉลากและวันหมดอายุดีกว่าซื้อแบบเปิดจากตลาด "
            "ทั้งสำหรับของขวัญและศุลกากร"
        ),
        "stationeryTip": (
            "ทิปซื้อ\n\nชุดในกล่องสำหรับของขวัญ; ไส้/ชิ้นเดี่ยวสำหรับตัวเอง"
        ),
        "socksTip": (
            "ทิปซื้อ\n\nแพ็ก 3 หรือ 5 คู่คุ้มกว่าชิ้นเดียว และเติมช่องว่างในกระเป๋าได้"
        ),
        "sheetTip": (
            "ทิปซื้อ\n\nเลือกชุดที่มีวันหมดอายุชัดและมีบรรจุภัณฑ์ภาษาอังกฤษสำหรับของขวัญ"
        ),
        "daisoTip": (
            "ทิปซื้อ\n\nชั่งน้ำหนักตะกร้าก่อนคิดเงิน; จัดลำดับของที่เติมช่องว่างในกระเป๋า"
        ),
        "unmannedTip_fun": None,  # placeholder
    }
    for k, v in polish_map.items():
        if v is None:
            continue
        if k in souvenir and souvenir.get(k) != v:
            souvenir[k] = v
            n += 1

    fun = data.setdefault("fun", {})
    # Fix unmanned tip MT "มีการสำรองข้อมูล" -> backup plan
    if isinstance(fun.get("unmannedTip"), str) and "มีการสำรองข้อมูล" in fun["unmannedTip"]:
        fun["unmannedTip"] = (
            "เคล็ดลับ\n\nเตรียมทางเลือกไว้หากบัตรต่างประเทศใช้ไม่ได้ "
            "อ่านสติกเกอร์ประตูสำหรับขั้นตอนเข้าเมื่อล็อกอยู่"
        )
        n += 1
    # Fix noraebangPrice "เกี่ยวกับ" -> "ประมาณ"
    if isinstance(fun.get("noraebangPrice"), str) and fun["noraebangPrice"].startswith(
        "บรรยากาศราคา\n\nเกี่ยวกับ"
    ):
        fun["noraebangPrice"] = fun["noraebangPrice"].replace(
            "เกี่ยวกับ ₩", "ประมาณ ₩", 1
        )
        n += 1
    # manga tip: "นั่งที่เคาน์เตอร์ก่อนออกเดินทาง" -> settle at counter
    if isinstance(fun.get("mangaTip"), str) and "นั่งที่เคาน์เตอร์ก่อนออกเดินทาง" in fun[
        "mangaTip"
    ]:
        fun["mangaTip"] = (
            "เคล็ดลับ\n\nปฏิบัติตามกฎอาหาร/เครื่องดื่ม เงียบๆ และถามก่อนถ่ายรูป "
            "ชำระเงินที่เคาน์เตอร์ก่อนออก"
        )
        n += 1

    return n


def fill_leftover_bodies(data: dict) -> int:
    """Any leftover text/callout still == en after curated fills — report only."""
    leftover = []

    def walk(obj, path=""):
        if isinstance(obj, dict):
            if obj.get("type") in ("text", "callout") and needs_th(obj):
                leftover.append((path, (obj.get("en") or "")[:80]))
            for k, v in obj.items():
                walk(v, f"{path}.{k}" if path else k)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                walk(v, f"{path}[{i}]")

    walk(data)
    for p, s in leftover[:30]:
        print(f"  leftover {p}: {s!r}")
    return len(leftover)


def main() -> None:
    data = load()
    lang_menu = (data.get("common") or {}).get("langMenu")

    print("1) polish scalars (before callout copy)…")
    print("  updated", polish_scalars(data))

    print("2) tips restaurant callout…")
    print("  filled", fill_tips_callout(data))

    print("3) souvenir/fun callouts from scalars…")
    print("  filled", fill_from_scalar_callouts(data))

    print("4) beforeTrip callouts…")
    print("  filled", fill_beforetrip_callouts(data))

    print("5) leftover check…")
    print("  leftover", fill_leftover_bodies(data))

    if lang_menu is not None:
        data.setdefault("common", {})["langMenu"] = lang_menu

    save(data)
    print("saved th.json")


if __name__ == "__main__":
    main()
