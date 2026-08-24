# -*- coding: utf-8 -*-
"""Restore prepTips/travelCourses/home keys + add Korail Talk (all GUIDE_LANGS)."""
from __future__ import annotations

import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from lib import i18n_store  # noqa: E402
from lib.cache_bust import bump_asset_version  # noqa: E402
from lib.translate import BatchStatus, fill_lang_targets  # noqa: E402

PREP_TIPS_KO = {
    "pageTitle": "준비 & 여행팁 | Korea Travel Guide",
    "title": "준비 & 여행팁",
    "intro": "떠나기 전 준비와 여행 중 바로 쓰는 팁을 한곳에서 확인하세요.",
    "groupPrep": "떠나기 전에 준비할 것",
    "groupTips": "여행 팁",
    "tipsLead": "여행 중에 바로 써먹는 주제별 팁입니다. 카드를 누르면 자세한 내용으로 이동합니다.",
    "openTipsHub": "→ 여행 팁 전체 보기",
    "backToPrepTips": "← 준비 & 여행팁",
}

TRAVEL_COURSES_KO = {
    "pageTitle": "여행 코스 추천 | Korea Travel Guide",
    "title": "여행 코스 추천",
    "intro": "일정 길이에 맞는 여행 코스를 준비하고 있습니다.",
    "catPickLabel": "일정",
    "catDay": "당일",
    "cat1n2d": "1박2일",
    "cat2n3d": "2박3일",
    "cat3n4d": "3박4일",
    "empty": "추천 코스가 없습니다",
}

HOME_EXTRA_KO = {
    "menuPrepTips": "준비 & 여행팁",
    "menuTravelCourses": "여행 코스 추천",
}

APPS_KO = {
    "korailTalkName": "코레일톡 (KORAIL+)",
    "korailTalkDesc": (
        "KTX·ITX 등 코레일 열차 예매·좌석 확인 공식 앱입니다. "
        "영어·중국어·일본어 화면을 지원하는 경우가 많아 외국인 여행객에게도 유용합니다."
    ),
    "korailTalkBody": (
        "코레일톡(KORAIL+)은 한국철도공사 공식 앱으로, "
        "KTX·새마을·무궁화 등 열차 승차권을 스마트폰에서 예매하고 확인할 수 있습니다. "
        "역 창구보다 빠르게 좌석을 잡을 때, 당일·연휴 인기 구간을 미리 확보할 때 요깁니다. "
        "앱 언어를 영어·중국어·일본어로 바꿀 수 있는 경우가 많으니 "
        "처음 설치 후 설정에서 언어를 확인하세요. "
        "예매 후 QR·모바일 티켓으로 개찰할 수 있고, 변경·환불 규정도 앱에서 안내합니다."
    ),
}


def _fill_namespace(ko_map: dict[str, str], status: BatchStatus) -> dict[str, dict[str, str]]:
    """Return {lang: {key: text}} for all langs from KO map."""
    out: dict[str, dict[str, str]] = {lang: {} for lang in i18n_store.LANGS}
    out["ko"] = dict(ko_map)
    for key, ko_text in ko_map.items():
        translated = fill_lang_targets(ko_text, force=True, status=status)
        for lang in i18n_store.LANGS:
            if lang == "ko":
                continue
            out[lang][key] = translated.get(lang) or ko_text
    return out


def patch_apps_hub() -> None:
    hub = ROOT / "pages" / "apps" / "index.html"
    html = hub.read_text(encoding="utf-8")
    if 'data-app="korail-talk"' in html:
        print("apps hub: korail-talk already present")
        return
    card = """
        <article class="app-card" data-app="korail-talk">
          <div class="app-icon" aria-hidden="true">KTX</div>
          <div class="app-body">
            <h3 data-i18n="apps.korailTalkName">코레일톡 (KORAIL+)</h3>
            <p data-i18n="apps.korailTalkDesc"></p>
            <div class="app-store-links">
              <a class="store-btn store-android" href="https://play.google.com/store/apps/details?id=com.korail.talk" target="_blank" rel="noopener noreferrer"><span data-i18n="apps.android">Android</span></a>
              <a class="store-btn store-ios" href="https://apps.apple.com/app/id1000558562" target="_blank" rel="noopener noreferrer"><span data-i18n="apps.ios">iOS</span></a>
            </div>
            <p class="app-card__more"><a href="./korail-talk/index.html" data-i18n="common.viewMore">자세히 보기 →</a></p>
          </div>
        </article>
"""
    needle = '        <article class="app-card" data-app="ddareungi">'
    if needle not in html:
        raise RuntimeError("apps hub: ddareungi card not found")
    html = html.replace(needle, card + "\n" + needle, 1)
    hub.write_text(html, encoding="utf-8", newline="\n")
    print("apps hub: korail-talk card inserted")


def write_korail_detail() -> None:
    page = ROOT / "pages" / "apps" / "korail-talk" / "index.html"
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(
        """<!DOCTYPE html>
<html lang="ko" data-i18n-title="apps.korailTalkName">
<head>
  <!-- asset-v: PLACEHOLDER -->
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Korail Talk</title>
  <link rel="stylesheet" href="../../../styles.css?v=PLACEHOLDER">
</head>
<body>
  <nav class="lang-switch" aria-label="Language"></nav>
  <header class="site-header">
    <a href="../../../index.html" class="site-brand" data-i18n="common.brand">Korea Travel Guide</a>
  </header>
  <main class="page article-page tip-detail">
    <p class="back-link">
      <a href="../index.html" data-i18n="apps.backHub">← 유용한 앱</a>
    </p>
    <article class="tip-article app-detail" data-app-slug="korail-talk">
      <div class="app-detail-head">
        <div class="app-icon" aria-hidden="true" data-app="korail-talk">KTX</div>
        <div>
          <p class="app-cat" data-i18n="apps.groupTransit"></p>
          <h1 data-i18n="apps.korailTalkName"></h1>
        </div>
      </div>
      <div class="content-body" data-content-body data-body-path="apps.korailTalkBody"></div>
      <div data-content-body-fallback>
        <p data-i18n="apps.korailTalkDesc"></p>
      </div>
      <div class="app-store-links">
        <a class="store-btn store-android" href="https://play.google.com/store/apps/details?id=com.korail.talk" target="_blank" rel="noopener noreferrer"><span data-i18n="apps.android">Android</span></a>
        <a class="store-btn store-ios" href="https://apps.apple.com/app/id1000558562" target="_blank" rel="noopener noreferrer"><span data-i18n="apps.ios">iOS</span></a>
      </div>
    </article>
  </main>
  <footer class="site-footer">
    <hr>
    <img src="../../../Images/cover/footer-korea.png" width="100%" alt="Korea Travel">
    <p class="footer-note" data-i18n="common.footer">© Korea Travel Guide</p>
  </footer>
  <script src="../../../i18n/messages.js?v=PLACEHOLDER"></script>
  <script src="../../../js/i18n.js?v=PLACEHOLDER"></script>
  <script src="../../../js/content-body.js?v=PLACEHOLDER"></script>
</body>
</html>
""",
        encoding="utf-8",
        newline="\n",
    )
    print("wrote pages/apps/korail-talk/index.html")


def patch_content_body_slot() -> None:
    path = TOOL_DIR / "lib" / "content_body.py"
    text = path.read_text(encoding="utf-8")
    if "korailTalkBody" in text:
        print("APPS_SLOTS: korailTalkBody already listed")
        return
    needle = '    BodySlot("tmoneyBody", "티머니 GO", "apps", "tmoney", group="tmoney"),\n'
    insert = (
        needle
        + '    BodySlot("korailTalkBody", "코레일톡", "apps", "korailTalk", group="korailTalk"),\n'
    )
    if needle not in text:
        raise RuntimeError("tmoneyBody slot not found")
    path.write_text(text.replace(needle, insert, 1), encoding="utf-8", newline="\n")
    print("APPS_SLOTS: korailTalkBody added")


def patch_travel_tips_backlink() -> None:
    tips = ROOT / "pages" / "travel-tips" / "index.html"
    if not tips.is_file():
        return
    html = tips.read_text(encoding="utf-8")
    if "prepTips.backToPrepTips" in html or "before-trip/index.html#tips" in html:
        print("travel-tips: backlink ok")
        return
    # ensure a back link near top of main
    if 'data-i18n="common.backMain"' in html and "prepTips.backToPrepTips" not in html:
        html = html.replace(
            '<p class="back-link"><a href="../../index.html" data-i18n="common.backMain">← Main Guide</a></p>',
            '<p class="back-link"><a href="../../index.html" data-i18n="common.backMain">← Main Guide</a>'
            ' · <a href="../before-trip/index.html#tips" data-i18n="prepTips.backToPrepTips">← 준비 &amp; 여행팁</a></p>',
            1,
        )
        tips.write_text(html, encoding="utf-8", newline="\n")
        print("travel-tips: added backlink to prepTips")


def main() -> int:
    status = BatchStatus()
    bundle = i18n_store.load_all()

    print("=== translate prepTips / travelCourses / home / apps ===")
    prep = _fill_namespace(PREP_TIPS_KO, status)
    courses = _fill_namespace(TRAVEL_COURSES_KO, status)
    home_extra = _fill_namespace(HOME_EXTRA_KO, status)
    apps_extra = _fill_namespace(APPS_KO, status)

    for lang in i18n_store.LANGS:
        bundle[lang].setdefault("prepTips", {}).update(prep[lang])
        bundle[lang].setdefault("travelCourses", {}).update(courses[lang])
        bundle[lang].setdefault("home", {}).update(home_extra[lang])
        bundle[lang].setdefault("apps", {}).update(apps_extra[lang])

    i18n_store.save_all(bundle)
    print(i18n_store.build_bundle())
    for n in status.note_lines()[:12]:
        print(" ", n)

    patch_apps_hub()
    write_korail_detail()
    patch_content_body_slot()
    patch_travel_tips_backlink()

    summary = bump_asset_version()
    print(f"cache → {summary['version']}")

    # smoke
    ko = i18n_store.load_lang("ko")
    assert ko["home"].get("menuPrepTips"), "menuPrepTips missing"
    assert ko["home"].get("menuTravelCourses"), "menuTravelCourses missing"
    assert ko["prepTips"].get("title"), "prepTips.title missing"
    assert ko["travelCourses"].get("empty"), "travelCourses.empty missing"
    assert ko["apps"].get("korailTalkName"), "korailTalkName missing"
    print("smoke OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
