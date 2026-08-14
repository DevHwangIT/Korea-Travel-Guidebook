#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fill remaining Russian gaps in ru.json only (bodies/callouts + priority scalars)."""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

from deep_translator import GoogleTranslator

ROOT = Path(__file__).resolve().parent
RU_PATH = ROOT / "ru.json"
EN_PATH = ROOT / "en.json"

SKIP_LEAVES = {
    "mapsUrl",
    "mapsEmbedUrl",
    "url",
    "href",
    "src",
    "id",
    "slug",
    "region",
    "lat",
    "lng",
    "progress",
    "sourceType",
    "mapsProvider",
    "contactLineId",
    "contactEmail",
    "contactEmailMailto",
    "policeNumber",
    "fireNumber",
    "touristNumber",
    "previewTitle",
    "previewImage",
    "placeId",
    "naverPlaceId",
    "googlePlaceId",
    "kakaoPlaceId",
    "phone",
    "score",
    "address",  # often Korean street address — leave
}

BRAND_KEEP = {
    "Kakao Map",
    "Naver Map",
    "Papago",
    "KakaoTalk",
    "Yanolja",
    "Yeogi",
    "Yeogi Eottae (Goodchoice)",
    "Baemin",
    "Yogiyo",
    "Coupang",
    "Coupang / Coupang Eats",
    "Kakao T",
    "Tmoney",
    "Olive Young",
    "Daiso",
    "Taxi",
    "Tip",
    "Wi-Fi",
    "Google",
    "Naver",
    "Kakao",
    "Phone",
}

EMAIL_RE = re.compile(r"^[\w.+-]+@[\w.-]+\.\w+$")
HTTP_RE = re.compile(r"^https?://", re.I)
ONLY_NUM_RE = re.compile(r"^[\d\s\-–—+/₩$.,:]+$")
MEDIA_RE = re.compile(r"^media/", re.I)


def load() -> dict:
    return json.loads(RU_PATH.read_text(encoding="utf-8"))


def load_en() -> dict:
    return json.loads(EN_PATH.read_text(encoding="utf-8"))


def save(data: dict) -> None:
    RU_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def flatten(d, prefix=""):
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            p = f"{prefix}.{k}" if prefix else k
            out.update(flatten(v, p))
    else:
        out[prefix] = d
    return out


def unflatten_set(data: dict, flat_key: str, value: str) -> None:
    parts = flat_key.split(".")
    cur = data
    for p in parts[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]
    cur[parts[-1]] = value


def join3(title: str, mistake: str, body: str) -> str:
    return f"{title}\n\n{mistake}\n\n{body}"


def needs_ru(block: dict) -> bool:
    en = str(block.get("en") or "").strip()
    ru = str(block.get("ru") or "").strip()
    if not en:
        return False
    return (not ru) or ru == en or ru == str(block.get("ko") or "").strip()


def translate_en(text: str, gt: GoogleTranslator) -> str:
    text = text.strip()
    if not text:
        return text
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
            # Google has length limits; chunk long parts
            if len(part) > 4200:
                chunks = [part[i : i + 4000] for i in range(0, len(part), 4000)]
                tr_bits = []
                for ch in chunks:
                    tr_bits.append((gt.translate(ch) or "").strip() or ch)
                    time.sleep(0.05)
                out.append("".join(tr_bits))
            else:
                tr = (gt.translate(part) or "").strip()
                out.append(tr if tr else part)
            time.sleep(0.05)
        except Exception as exc:  # noqa: BLE001
            print("  translate err:", exc)
            out.append(part)
    return "".join(out)


def fill_tips_bodies(data: dict) -> int:
    """Rebuild tips body text blocks from good RU scalars (like vi/th)."""
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
        daily[i]["ru"] = join3(title, mistake, body)
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
        transport[i]["ru"] = join3(title, mistake, body)
        n += 1

    for b in tips.get("restaurantBody") or []:
        if isinstance(b, dict) and b.get("type") == "callout" and needs_ru(b):
            b["ru"] = (
                "Итог: в обычных корейских ресторанах чаевые не ожидаются. "
                "Оплатите сумму по чеку у стойки."
            )
            n += 1

    return n


def fill_from_scalar_callouts(data: dict) -> int:
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
            if isinstance(b, dict) and b.get("type") == "callout" and needs_ru(b):
                b["ru"] = tip
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
            if i < len(scalars) and needs_ru(b):
                b["ru"] = scalars[i]
                n += 1

    return n


def fill_beforetrip_callouts(data: dict) -> int:
    n = 0
    before = data.get("beforeTrip") or {}
    curated = {
        "Treat travel insurance as a baseline for medical costs, lost items, and delays.": (
            "Считайте страховку путешествия базой на случай медицинских расходов, "
            "потери вещей и задержек."
        ),
        "Small bills (₩1,000 / ₩5,000) help at markets. Keep a little cash for transit top-ups too.": (
            "Мелкие купюры (₩1,000 / ₩5,000) удобны на рынках. "
            "Держите немного наличных и для пополнения транспортной карты."
        ),
        "You'll want maps on landing — note your eSIM install steps beforehand.": (
            "Сразу после посадки понадобятся карты — заранее запишите шаги установки eSIM."
        ),
        "Adapters are sold at Daiso, convenience stores, and airports — but stock can run out on arrival or holidays, so packing one is safer.": (
            "Адаптеры продаются в Daiso, магазинах у дома и аэропортах — "
            "но при прилёте или в праздники их может не быть, поэтому надёжнее взять с собой."
        ),
        "Leave suitcase space for Olive Young, Daiso, and snack gifts — they add up fast.": (
            "Оставьте место в чемодане для Olive Young, Daiso и снеков в подарок — "
            "они быстро накапливаются."
        ),
        "Overcharging is rare in Seoul these days — metered regular taxis are the norm. For extra peace of mind, you can request a ride in Kakao T or similar apps. If a fare still feels off, note the license plate and the taxi license display inside, then ask Seoul’s Dasan Call Center 120, or tourist helpline 1330. Some cabs also show an in-car QR for feedback.": (
            "Завышение цены в Сеуле сейчас редко — обычные такси ездят по счётчику. "
            "Для спокойствия можно вызвать машину через Kakao T или похожие приложения. "
            "Если тариф всё же кажется странным, запишите номер машины и лицензию такси внутри, "
            "затем обратитесь в Dasan Call Center Сеула 120 или туристическую линию 1330. "
            "В некоторых такси есть QR в салоне для отзывов."
        ),
        "Tip: More places welcome solo diners (counter seats, 1-person sets). Search maps for “honbap” / single seating.": (
            "Совет: всё больше мест рады гостям в одиночку (места у стойки, порции на 1 человека). "
            "Ищите на карте «honbap» / одиночную посадку."
        ),
        "Official info: check SES pages on Korea Immigration https://www.immigration.go.kr and Hi Korea https://www.hikorea.go.kr for eligibility and enrollment locations.": (
            "Официально: смотрите страницы SES на Korea Immigration https://www.immigration.go.kr "
            "и Hi Korea https://www.hikorea.go.kr — условия и места регистрации."
        ),
        "Common mistakes: confusing it with K-ETA, filing too early (72-hour expiry), wrong hotel address, paid fake sites. If plans change, check/edit on the official site before immigration.": (
            "Частые ошибки: путают с K-ETA, подают слишком рано (срок 72 часа), "
            "неверный адрес отеля, платные фейковые сайты. "
            "Если планы меняются, проверьте/исправьте на официальном сайте до паспортного контроля."
        ),
        "Follow official/kiosk instructions. App signup and balance checks are usually explained on-site. Avoid unnecessary paid agents.": (
            "Следуйте официальным инструкциям / киоскам. Регистрация в приложении и проверка баланса "
            "обычно объясняются на месте. Избегайте ненужных платных посредников."
        ),
        "Long weekends get busy at sights, transit, and popular restaurants. Some shops and offices close. Book early, as in peak season.": (
            "В длинные выходные людно у достопримечательностей, в транспорте и популярных ресторанах. "
            "Часть магазинов и офисов закрывается. Бронируйте заранее, как в пик сезона."
        ),
        "Spring (Mar–May) and autumn (Sep–early/mid Nov, outside Chuseok week) are usually easier for outdoor trips. Avoid peak holiday crowds if you want a calmer first visit.": (
            "Весна (март–май) и осень (сентябрь–начало/середина ноября, вне недели Чхусока) "
            "обычно удобнее для поездок на свежем воздухе. "
            "Избегайте пиковых праздничных толп, если хотите более спокойный первый визит."
        ),
        "Some regions (and Jeju) are easier by rental car. Even if you only use subway/bus inside Seoul, day one feels much lighter.": (
            "В некоторых регионах (и на Чеджу) удобнее взять авто. "
            "Даже если в Сеуле вы ездите только на метро/автобусе, первый день будет заметно легче."
        ),
        "A quick look around helps more than perfect etiquette. When unsure, quietly mirror nearby tables.": (
            "Быстрый взгляд вокруг полезнее идеального этикета. "
            "Если не уверены, тихо копируйте соседние столы."
        ),
        "Find more trip-ready phrases in Useful Korean. Even a quick skim of daily, dining, and transit tabs before you fly makes the first days calmer.": (
            "Больше готовых фраз — в разделе «Полезный корейский». "
            "Даже быстрый просмотр вкладок повседневности, еды и транспорта перед вылетом "
            "делает первые дни спокойнее."
        ),
    }

    gt = None
    for key, blocks in list(before.items()):
        if not isinstance(blocks, list):
            continue
        for b in blocks:
            if not isinstance(b, dict) or b.get("type") != "callout":
                continue
            if not needs_ru(b):
                continue
            en = str(b.get("en") or "").strip()
            ru = curated.get(en)
            if not ru:
                for cen, cru in curated.items():
                    if en.startswith(cen[:50]) or cen.startswith(en[:50]):
                        ru = cru
                        break
            if not ru:
                en_head = "".join(ch for ch in en[:60] if ch.isascii())
                for cen, cru in curated.items():
                    cen_head = "".join(ch for ch in cen[:60] if ch.isascii())
                    if en_head and cen_head and (
                        en_head[:40] in cen_head or cen_head[:40] in en_head
                    ):
                        ru = cru
                        break
            if not ru:
                if gt is None:
                    gt = GoogleTranslator(source="en", target="ru")
                print(f"  MT beforeTrip.{key} callout…")
                ru = translate_en(en, gt)
            b["ru"] = ru
            n += 1
    return n


def polish_souvenir_tips(data: dict, gt: GoogleTranslator) -> int:
    """Ensure souvenir *Tip scalars are Russian before copying into callouts."""
    n = 0
    souvenir = data.setdefault("souvenir", {})
    curated = {
        "maskTip": (
            "Совет при покупке\n\n"
            "Проверьте маркировку KF94 и дату упаковки. "
            "Для подарков оптом аптечные мультипаки обычно надёжнее."
        ),
        "stationeryTip": (
            "Совет при покупке\n\n"
            "Наборы в футляре — для подарков; стержни/штучные — для себя."
        ),
        "honeyTip": (
            "Совет при покупке\n\n"
            "Закрытые банки с этикеткой и сроком годности лучше, чем разлив на рынке — "
            "и для подарков, и для таможни."
        ),
        "socksTip": (
            "Совет при покупке\n\n"
            "Упаковки по 3 или 5 пар выгоднее штучных и заполняют пустоты в чемодане."
        ),
        "sheetTip": (
            "Совет при покупке\n\n"
            "Выбирайте наборы с ясным сроком годности и английской упаковкой — удобнее дарить."
        ),
        "daisoTip": (
            "Совет при покупке\n\n"
            "Взвесьте корзину до кассы; сначала берите то, что заполняет пустоты в багаже."
        ),
        "lipstickTip": (
            "Совет при покупке\n\n"
            "Попросите у сотрудника спокойный/тёплый тон. "
            "Осторожнее с тестерами и сохраняйте чек на случай возврата."
        ),
    }
    for k, v in curated.items():
        if souvenir.get(k) != v:
            souvenir[k] = v
            n += 1

    # Any other *Tip still English → MT
    for k, v in list(souvenir.items()):
        if not k.endswith("Tip") or not isinstance(v, str):
            continue
        if k in curated:
            continue
        ascii_letters = sum(1 for c in v if ("A" <= c <= "Z") or ("a" <= c <= "z"))
        cyr = sum(1 for c in v if "\u0400" <= c <= "\u04FF")
        looks_en = (
            v.startswith("Buying tip")
            or "Buying tip" in v[:40]
            or (ascii_letters > 20 and ascii_letters > cyr * 2)
        )
        if looks_en:
            print(f"  MT souvenir.{k}…")
            souvenir[k] = translate_en(v, gt)
            n += 1
    return n


def needs_scalar_fill(en_val: str, loc_val) -> bool:
    if loc_val is None or loc_val == "" or loc_val == en_val:
        return True
    return False


def should_skip_scalar(key: str, en_val: str) -> bool:
    leaf = key.split(".")[-1]
    if leaf in SKIP_LEAVES:
        return True
    if not en_val or not en_val.strip():
        return True
    if en_val.strip() in BRAND_KEEP:
        return True
    if HTTP_RE.match(en_val.strip()):
        return True
    if EMAIL_RE.match(en_val.strip()):
        return True
    if ONLY_NUM_RE.match(en_val.strip()):
        return True
    if MEDIA_RE.match(en_val.strip()):
        return True
    if "{current}" in en_val or "{total}" in en_val:
        return True
    # Korean phrase samples / romaji / multilingual columns
    if key.startswith("korean.p.") and leaf in ("rom", "en", "ja", "zh", "ko", "audio"):
        return True
    # Hangul-only addresses / names already Korean
    hangul = sum(1 for c in en_val if "\uac00" <= c <= "\ud7a3")
    if hangul > len(en_val.strip()) * 0.4:
        return True
    return False


def fill_priority_scalars(data: dict, en_data: dict, gt: GoogleTranslator) -> int:
    prefixes = (
        "souvenir.",
        "convenience.",
        "korean.",
        "misc.",
        "foodsHub.",
        "transport.",
        "fun.",
        "tips.",
        "beforeTrip.",
        "foodLife.quiz.",
        "places.",
        "restaurants.",
        "festivals.",
        "emergency.",
        "home.",
        "apps.",
        "areas.",
        "travelUtils.",
        "dishes.",
    )
    en_flat = {k: v for k, v in flatten(en_data).items() if isinstance(v, str)}
    ru_flat = flatten(data)
    jobs = []
    for key, en_val in en_flat.items():
        if not any(key.startswith(p) for p in prefixes):
            continue
        if should_skip_scalar(key, en_val):
            continue
        loc = ru_flat.get(key)
        if needs_scalar_fill(en_val, loc):
            jobs.append((key, en_val))

    print(f"  scalar jobs: {len(jobs)}")
    n = 0
    for i, (key, en_val) in enumerate(jobs):
        print(f"  MT scalar {i+1}/{len(jobs)} {key}…")
        tr = translate_en(en_val, gt)
        if tr:
            unflatten_set(data, key, tr)
            n += 1
        if (i + 1) % 40 == 0:
            save(data)
            print("  checkpoint save")
    return n


def polish_fixed(data: dict) -> int:
    n = 0
    foods = data.setdefault("foodsHub", {})
    if foods.get("eyebrow") in (None, "", "Korea Travel Guidebook"):
        foods["eyebrow"] = "Путеводитель по Корее"
        n += 1

    transport = data.setdefault("transport", {})
    if transport.get("route_ahd_cost") in (None, "", "AREX all-stop ~₩4,000"):
        transport["route_ahd_cost"] = "AREX со всеми остановками ~₩4,000"
        n += 1

    tips = data.setdefault("tips", {})
    # brand tabs intentional
    for k, v in {
        "tabOlive": "Olive Young",
        "tabDaiso": "Daiso",
        "tabWifi": "Wi-Fi",
        "tabTaxi": "Такси",
    }.items():
        if tips.get(k) != v:
            tips[k] = v
            n += 1

    korean = data.setdefault("korean", {})
    polish_ko = {
        "pageTitle": "Полезный корейский",
        "catDaily": "Повседневность",
        "catRestaurant": "Питание",
        "catShopping": "Шоппинг",
        "catTransport": "Транспорт",
        "catSwear": "Ругательства",
    }
    for k, v in polish_ko.items():
        if korean.get(k) in (None, "", load_en().get("korean", {}).get(k)):
            korean[k] = v
            n += 1

    return n


def leftover_bodies(data: dict) -> int:
    leftover = []

    def walk(obj, path=""):
        if isinstance(obj, dict):
            if obj.get("type") in ("text", "callout") and needs_ru(obj):
                leftover.append((path, (obj.get("en") or "")[:90]))
            for k, v in obj.items():
                walk(v, f"{path}.{k}" if path else k)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                walk(v, f"{path}[{i}]")

    walk(data)
    for p, s in leftover[:40]:
        print(f"  leftover {p}: {s!r}")
    return len(leftover)


def fill_leftover_bodies_mt(data: dict, gt: GoogleTranslator) -> int:
    n = 0

    def walk(obj, path=""):
        nonlocal n
        if isinstance(obj, dict):
            if obj.get("type") in ("text", "callout") and needs_ru(obj):
                en = str(obj.get("en") or "").strip()
                print(f"  MT leftover {path}…")
                obj["ru"] = translate_en(en, gt)
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
    en_data = load_en()
    lang_menu = (data.get("common") or {}).get("langMenu")
    gt = GoogleTranslator(source="en", target="ru")

    print("1) polish fixed scalars…")
    print("  updated", polish_fixed(data))

    print("2) polish souvenir tips (before callout copy)…")
    print("  updated", polish_souvenir_tips(data, gt))

    print("3) tips bodies + restaurant callout…")
    print("  filled", fill_tips_bodies(data))

    print("4) beforeTrip callouts…")
    print("  filled", fill_beforetrip_callouts(data))

    print("5) souvenir/fun callouts from scalars…")
    print("  filled", fill_from_scalar_callouts(data))

    print("6) priority scalars MT…")
    print("  filled", fill_priority_scalars(data, en_data, gt))

    # Re-copy callouts in case tips were translated in step 6
    print("6b) re-copy souvenir/fun callouts…")
    print("  filled", fill_from_scalar_callouts(data))

    print("7) leftover body/callout MT…")
    print("  filled", fill_leftover_bodies_mt(data, gt))

    print("8) leftover check…")
    print("  leftover", leftover_bodies(data))

    if lang_menu is not None:
        data.setdefault("common", {})["langMenu"] = lang_menu

    save(data)
    print("saved ru.json")


if __name__ == "__main__":
    main()
