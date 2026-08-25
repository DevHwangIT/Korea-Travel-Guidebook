# -*- coding: utf-8 -*-
"""Inject curated-course copy for chungcheong, jeolla, gyeongsang, busan, jeju."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LANGS = ["ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru"]


def T(*vals):
    if len(vals) != 8:
        raise ValueError(vals[0] if vals else "empty")
    return dict(zip(LANGS, vals))


def chrome(pick, intro, eye, feat, more):
    return {lang: {
        "pickLabel": pick[lang],
        "intro": intro[lang],
        "guideEyebrow": eye[lang],
        "featuredLabel": feat[lang],
        "moreLabel": more[lang],
    } for lang in LANGS}


def course(title, summary, route, tips, stops, notice=None):
    out = {}
    for lang in LANGS:
        item = {
            "title": title[lang],
            "summary": summary[lang],
            "route": route[lang],
            "tips": tips[lang],
            "stops": [{"name": n[lang], "desc": d[lang]} for n, d in stops],
        }
        if notice:
            item["notice"] = notice[lang]
        out[lang] = item
    return out


N = T("대표 코스", "Top picks", "代表コース", "代表路线", "代表路線", "Tour nổi bật", "เส้นทางเด่น", "Главные")
M = T("더 둘러보기", "More courses", "もっと見る", "更多路线", "更多路線", "Tour khác", "เส้นทางเพิ่ม", "Ещё")

CHROME = {
    "chungcheong": chrome(
        T("충청도 추천 코스", "Chungcheong curated courses", "忠清おすすめコース", "忠清推荐路线", "忠清推薦路線", "Tour Chungcheong đề xuất", "เส้นทางแนะนำชุงชอง", "Маршруты Чхунчхона"),
        T("공주·부여 백제와 단양·보령·태안·대전을 하루로 도는 코스입니다. 타이틀을 고르면 소개·동선·시간표가 펼쳐집니다.",
          "Day courses around Gongju and Buyeo Baekje sites, Danyang, Boryeong, Taean, and Daejeon. Pick a title for the intro, route, and timetable.",
          "公州・扶余の百済と丹陽・保寧・泰安・大田を一日で回るコースです。タイトルを選ぶと紹介・動線・時間割が開きます。",
          "公州、扶余百济与丹阳、保宁、泰安、大田的一日路线。点标题即可看介绍、动线和时刻表。",
          "公州、扶餘百濟與丹陽、保寧、泰安、大田的一日路線。點標題即可看介紹、動線和時刻表。",
          "Tour một ngày Gongju–Buyeo, Danyang, Boryeong, Taean và Daejeon. Chọn tiêu đề để xem giới thiệu, lộ trình và lịch.",
          "เส้นทางวันเดียวกงจู บูยอ ดันยัง โบรยอง แทอัน แทจอน เลือกชื่อเพื่อดูแนะนำ เส้นทาง และตารางเวลา",
          "День по Конджу и Пуё, Таняну, Порёну, Тхэану и Тэджону. Выберите название — откроются описание, маршрут и расписание."),
        T("충청도 코스 안내", "Chungcheong course guide", "忠清コース案内", "忠清路线指南", "忠清路線指南", "Hướng dẫn tour Chungcheong", "คู่มือเส้นทางชุงชอง", "Гид по маршрутам Чхунчхона"),
        N, M,
    ),
    "jeolla": chrome(
        T("전라도 추천 코스", "Jeolla curated courses", "全羅おすすめコース", "全罗推荐路线", "全羅推薦路線", "Tour Jeolla đề xuất", "เส้นทางแนะนำชอลลา", "Маршруты Чоллы"),
        T("전주 한옥마을부터 여수 밤바다, 순천만, 담양, 보성 녹차밭, 목포까지 전라도를 하루로 도는 코스입니다. 타이틀을 고르면 소개·동선·시간표가 펼쳐집니다.",
          "Day courses from Jeonju Hanok Village to Yeosu nights, Suncheon Bay, Damyang, Boseong tea fields, and Mokpo.",
          "全州韓屋村から麗水の夜、順天湾、潭陽、宝城茶畑、木浦まで全羅を一日で回ります。",
          "从全州韩屋村到丽水夜景、顺天湾、潭阳、宝城茶园和木浦。",
          "從全州韓屋村到麗水夜景、順天灣、潭陽、寶城茶園和木浦。",
          "Từ làng Hanok Jeonju đến đêm Yeosu, Suncheon, Damyang, đồi chè Boseong và Mokpo.",
          "จากหมู่บ้านฮันอกชอนจู ถึงยอซู ซุนชอน ทัมยัง โบซอง และมกโพ",
          "От ханок Чонджу к ночи Йосу, Сунчхону, Тамьяну, чайным полям Посона и Мокпхо."),
        T("전라도 코스 안내", "Jeolla course guide", "全羅コース案内", "全罗路线指南", "全羅路線指南", "Hướng dẫn tour Jeolla", "คู่มือเส้นทางชอลลา", "Гид по маршрутам Чоллы"),
        N, M,
    ),
    "gyeongsang": chrome(
        T("경상도 추천 코스", "Gyeongsang curated courses", "慶尚おすすめコース", "庆尚推荐路线", "慶尚推薦路線", "Tour Gyeongsang đề xuất", "เส้นทางแนะนำคยองซัง", "Маршруты Кёнсана"),
        T("경주 신라 유적과 안동 하회, 통영·거제 바다, 포항, 대구, 울산, 해인사까지 경상권을 하루로 도는 코스입니다. 타이틀을 고르면 소개·동선·시간표가 펼쳐집니다.",
          "Day courses across Gyeongju, Andong Hahoe, Tongyeong, Geoje, Pohang, Daegu, Ulsan, and Haeinsa.",
          "慶州・安東河回・統営・巨済・浦項・大邱・蔚山・海印寺を一日で回ります。",
          "庆州、安东河回、统营、巨济、浦项、大邱、蔚山与海印寺的一日路线。",
          "慶州、安東河回、統營、巨濟、浦項、大邱、蔚山與海印寺的一日路線。",
          "Gyeongju, Andong Hahoe, Tongyeong, Geoje, Pohang, Daegu, Ulsan và Haeinsa.",
          "คยองจู อันดง ทงยอง โกเจ โพฮัง แทกู อุลซาน และแฮอินซา",
          "Кёнджу, Андон Хвахое, Тхонъён, Кодже, Пхохан, Тэгу, Ульсан и Хэинса."),
        T("경상도 코스 안내", "Gyeongsang course guide", "慶尚コース案内", "庆尚路线指南", "慶尚路線指南", "Hướng dẫn tour Gyeongsang", "คู่มือเส้นทางคยองซัง", "Гид по маршрутам Кёнсана"),
        N, M,
    ),
    "busan": chrome(
        T("부산 추천 코스", "Busan curated courses", "釜山おすすめコース", "釜山推荐路线", "釜山推薦路線", "Tour Busan đề xuất", "เส้นทางแนะนำปูซาน", "Маршруты Пусана"),
        T("해운대·청사포·광안리부터 감천·자갈치, 송도·영도, 기장 해동용궁사, 서면·전포까지 부산을 하루로 도는 코스입니다. 타이틀을 고르면 소개·동선·시간표가 펼쳐집니다.",
          "Day courses from Haeundae, Cheongsapo and Gwangalli to Gamcheon, Jagalchi, Songdo, Yeongdo, Gijang, and Seomyeon.",
          "海雲台・青沙浦・広安里から甘川・チャガルチ、松島・影島、機張、西面まで釜山を一日で回ります。",
          "从海云台、青沙浦、广安里到甘川、札嘎其、松岛、影岛、机张和西面。",
          "從海雲台、青沙浦、廣安里到甘川、札嘎其、松島、影島、機張和西面。",
          "Haeundae, Cheongsapo, Gwangalli, Gamcheon, Jagalchi, Songdo, Yeongdo, Gijang và Seomyeon.",
          "แฮอุนแด ชองซาโพ กวางอันลี กัมชอน ชากัลชี ซงโด ยองโด คิจาง และซอมยอน",
          "Хэундэ, Чхонсапхо, Кваналлли, Камчхон, Чагальчхи, Сондо, Йондо, Киджан и Сомён."),
        T("부산 코스 안내", "Busan course guide", "釜山コース案内", "釜山路线指南", "釜山路線指南", "Hướng dẫn tour Busan", "คู่มือเส้นทางปูซาน", "Гид по маршрутам Пусана"),
        N, M,
    ),
    "jeju": chrome(
        T("제주도 추천 코스", "Jeju curated courses", "済州おすすめコース", "济州推荐路线", "濟州推薦路線", "Tour Jeju đề xuất", "เส้นทางแนะนำเชจู", "Маршруты Чеджу"),
        T("성산·우도부터 협재·애월, 서귀포 폭포, 중문, 한라산, 제주시, 오름·산방산까지 제주를 하루로 도는 코스입니다. 타이틀을 고르면 소개·동선·시간표가 펼쳐집니다.",
          "Day courses from Seongsan and Udo to Hyeopjae, Aewol, Seogwipo falls, Jungmun, Hallasan, Jeju City, oreum, and Sanbangsan.",
          "城山・牛島から協才・涯月、西帰浦の滝、中文、漢拏山、済州市、オルム、山房山まで。",
          "从城山、牛岛到挟才、涯月、西归浦瀑布、中文、汉拿山、济州市、岳和新房山。",
          "從城山、牛島到挾才、涯月、西歸浦瀑布、中文、漢拏山、濟州市、岳和山房山。",
          "Seongsan, Udo, Hyeopjae, Aewol, Seogwipo, Jungmun, Hallasan, thành phố Jeju, oreum và Sanbangsan.",
          "ซองซาน อูโด ฮยอพเจ แอวอล ซอกวีโพ จุงมุน ฮัลลาซาน เมืองเชจู และซันบังซาน",
          "Сонсан, Удо, Хёпчжэ, Эволь, Согвипхо, Чунмун, Халласан, город Чеджу, орум и Санбансан."),
        T("제주도 코스 안내", "Jeju course guide", "済州コース案内", "济州路线指南", "濟州路線指南", "Hướng dẫn tour Jeju", "คู่มือเส้นทางเชจู", "Гид по маршрутам Чеджу"),
        N, M,
    ),
}

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _south_course_copy import COURSES  # noqa: E402


def build_lang(region: str, lang: str) -> dict:
    block = dict(CHROME[region][lang])
    block["courses"] = {cid: COURSES[region][cid][lang] for cid in COURSES[region]}
    return block


def main() -> None:
    for lang in LANGS:
        path = ROOT / "i18n" / "pages" / "travel-courses" / f"{lang}.json"
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        curated = data.setdefault("travelCourses", {}).setdefault("curated", {})
        for region in CHROME:
            curated[region] = build_lang(region, lang)
        with path.open("w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("updated", path.name, "regions", list(CHROME))


if __name__ == "__main__":
    main()
