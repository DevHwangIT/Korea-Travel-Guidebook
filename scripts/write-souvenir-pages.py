# -*- coding: utf-8 -*-
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "pages" / "souvenir"
ITEMS = [
    "mask",
    "stationery",
    "olive",
    "daiso",
    "snack",
    "ramen",
    "tea",
    "honey",
    "uniqlo",
    "spa",
    "socks",
    "hanbok",
    "sheet",
    "sunscreen",
    "lipstick",
    "kpop",
]

TEMPLATE = """<!DOCTYPE html>
<html lang="ko" data-i18n-title="souvenir.{key}Title">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Souvenir</title>
  <link rel="stylesheet" href="../../../styles.css">
</head>
<body>
  <nav class="lang-switch" aria-label="Language">
    <button type="button" data-set-lang="ko">KR</button>
    <button type="button" data-set-lang="en">EN</button>
    <button type="button" data-set-lang="ja">JP</button>
  </nav>
  <header class="site-header">
    <a href="../../../index.html" class="site-brand" data-i18n="common.brand">Korea Travel Guide</a>
  </header>
  <main class="page article-page">
    <p class="back-link"><a href="../index.html" data-i18n="souvenir.backList">← 기념품 목록</a></p>
    <article class="souvenir-article">
      <img class="combo-article-hero" src="../../../Images/souvenir/{key}.jpg" alt="" data-i18n-attr="alt:souvenir.{key}Title">
      <h1 data-i18n="souvenir.{key}Title"></h1>
      <p class="article-lead" data-i18n="souvenir.{key}Desc"></p>
      <p data-i18n="souvenir.{key}Body1"></p>
      <p data-i18n="souvenir.{key}Body2"></p>
      <div class="tip">
        <h3 data-i18n="souvenir.tipTitle">사는 팁</h3>
        <p data-i18n="souvenir.{key}Tip"></p>
      </div>
    </article>
  </main>
  <footer class="site-footer">
    <hr>
    <img src="../../../Images/cover/footer-korea.png" width="100%" alt="Korea Travel">
    <p class="footer-note" data-i18n="common.footer">© Korea Travel Guide</p>
  </footer>
  <script src="../../../i18n/messages.js"></script>
  <script src="../../../js/i18n.js"></script>
</body>
</html>
"""


def main() -> None:
    for key in ITEMS:
        dest = PAGES / key / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(TEMPLATE.format(key=key), encoding="utf-8")
        print("wrote", dest.relative_to(ROOT))


if __name__ == "__main__":
    main()
