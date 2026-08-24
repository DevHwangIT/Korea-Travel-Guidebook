# -*- coding: utf-8 -*-
"""Refactor meal dish pages: shop cards instead of city tabs."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MEALS = ROOT / "pages" / "foods" / "meals"

KIMBAP_SHOPS = [
    ("wonjo-nude-cheese", "wonjo-nude-cheese.jpg"),
    ("oto", "oto.jpg"),
    ("hanipsoban", "hanipsoban.jpg"),
    ("horangi", "horangi.jpg"),
    ("sua-dang", "sua-dang.jpg"),
    ("food2900", "food2900.jpg"),
    ("bapdoduk", "bapdoduk.jpg"),
    ("seoho", "seoho.jpg"),
]

EMPTY_DISHES = [
    "naengmyeon",
    "jeon",
    "jajangmyeon",
    "dakhanmari",
    "samgyeopsal",
    "budae-jjigae",
    "dakgalbi",
    "samgyetang",
    "bibimbap",
    "ganjang-gejang",
    "yangnyeom-chicken",
    "sundubu-jjigae",
    "jjimdak",
]


def extract_emoji(html: str) -> str:
    m = re.search(r"<h1>([^<]*?)\s*<span data-i18n=", html)
    if m:
        return m.group(1).strip()
    return ""


def page_shell(slug: str, emoji: str, places_block: str) -> str:
    emoji_prefix = f"{emoji} " if emoji else ""
    return f"""<!DOCTYPE html>
<html lang="ko" data-i18n-title="dishes.{slug}.title">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{slug} | Korea Travel Guide</title>
  <link rel="stylesheet" href="../../../../styles.css">
</head>
<body>
  <nav class="lang-switch" aria-label="Language">
    <button type="button" data-set-lang="ko">KR</button>
    <button type="button" data-set-lang="en">EN</button>
    <button type="button" data-set-lang="ja">JP</button>
  </nav>

  <header class="site-header">
    <a href="../../../../index.html" class="site-brand" data-i18n="common.brand">Korea Travel Guide</a>
  </header>

  <main class="page">
    <p class="back-link">
      <a href="../index.html" data-i18n="misc.backFoods">← Back</a>
    </p>

    <h1>{emoji_prefix}<span data-i18n="dishes.{slug}.title">{slug}</span></h1>

    <img src="../../../../Images/foods/dishes/{slug}.jpg" width="100%" alt="{slug}" data-i18n-attr="alt:dishes.{slug}.title">

    <section class="intro">
      <h2 data-i18n="common.about">About</h2>
      <p data-i18n="dishes.{slug}.about"></p>
    </section>

{places_block}
  </main>

  <footer class="site-footer">
    <hr>
    <img src="../../../../Images/cover/footer-korea.png" width="100%" alt="Korea Travel">
    <p class="footer-note" data-i18n="common.footer">© Korea Travel Guide</p>
  </footer>

  <script src="../../../../i18n/messages.js"></script>
  <script src="../../../../js/i18n.js"></script>
</body>
</html>
"""


def kimbap_places() -> str:
    cards = []
    for slug, img in KIMBAP_SHOPS:
        cards.append(
            f"""      <article class="card">
        <a href="./{slug}.html">
          <img src="../../../../Images/foods/restaurants/kimbap/{img}" width="100%" alt="" data-i18n-attr="alt:restaurants.{slug}.name">
        </a>
        <h2><span data-i18n="restaurants.{slug}.name"></span></h2>
        <p data-i18n="restaurants.{slug}.menu"></p>
        <p><a href="./{slug}.html" data-i18n="common.viewMore">View more →</a></p>
      </article>"""
        )
    return f"""    <h2 data-i18n="common.places">Places</h2>
    <p class="tabs-help" data-i18n="common.shopsHelp"></p>
    <div class="card-grid">
{chr(10).join(cards)}
    </div>"""


def empty_places() -> str:
    return """    <h2 data-i18n="common.places">Places</h2>
    <p class="tabs-help" data-i18n="common.shopsComing"></p>
    <p data-i18n="common.emptyPlaces">등록된 곳이 아직 없습니다.</p>"""


def main():
    kimbap_path = MEALS / "kimbap" / "index.html"
    old = kimbap_path.read_text(encoding="utf-8")
    emoji = extract_emoji(old) or "🌯"
    kimbap_path.write_text(page_shell("kimbap", emoji, kimbap_places()), encoding="utf-8")
    print("updated", kimbap_path)

    for slug in EMPTY_DISHES:
        path = MEALS / slug / "index.html"
        if not path.exists():
            print("skip missing", path)
            continue
        old = path.read_text(encoding="utf-8")
        emoji = extract_emoji(old)
        path.write_text(page_shell(slug, emoji, empty_places()), encoding="utf-8")
        print("updated", path)


if __name__ == "__main__":
    main()
