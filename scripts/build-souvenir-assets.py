# -*- coding: utf-8 -*-
"""Download/compress souvenir images and scaffold detail HTML pages."""
from __future__ import annotations

import io
import ssl
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
IMG_DIR = ROOT / "Images" / "souvenir"
PAGES = ROOT / "pages" / "souvenir"

# Unsplash photo IDs (product / lifestyle). Resized & JPEG-compressed locally.
SOURCES = {
    "mask": "1584634731339-252c581abfc5",  # face masks
    "stationery": "1456735191194-d485bcf8c0a1",  # stationery flat lay
    "olive": "1596462502278-27bfdc403348",  # cosmetics
    "daiso": "1586023492120-27b2c045efd7",  # household / decor
    "snack": "1621939514649-280e2ee0f6d1",  # snacks
    "ramen": "1569718212165-3a8278d5f624",  # noodles bowl
    "tea": "1576092768241-dec231879fc3",  # tea
    "honey": "1587049352846-4a222e784d38",  # honey / sweets jars
    "uniqlo": "1441986300917-64674bd600d8",  # clothing store
    "spa": "1489987707025-afc232f7ea0f",  # folded clothes
    "socks": "1586359902138-8e8e8e8e8e8e",  # placeholder — replaced below
    "hanbok": "1545569341-9eb8b30979d9",  # traditional / cultural fabric vibe
    "sheet": "1570172619644-dfd03ed5d881",  # skincare face
    "sunscreen": "1556228578-0d85b1a4d571",  # sunscreen bottle vibe / lotion
    "lipstick": "1586495777744-4413f21062fa",  # lipstick
    "kpop": "1511671782779-c97d3d27a1d4",  # music / merch vibe
}

# More reliable IDs for a few that may 404
SOURCES.update(
    {
        "socks": "1556905055-8f358a7a47b2",  # colorful socks / apparel
        "hanbok": "1516450360452-9312f5e86fc7",  # stage / cultural performance colors
        "honey": "1558642457-c8d0ad0477c4",  # cookies / sweets
        "ramen": "1612929636598-9047f3b0c2e4",  # instant noodles pack style
        "daiso": "1556911220-bff31c812d84",  # kitchen / household
        "kpop": "1493225457124-a3eb161ffa5f",  # microphone / music
        "sunscreen": "1556228453-efd6c1ff04f6",  # lotion bottles
        "sheet": "1596755389378-c31d21fd1273",  # skincare products
    }
)

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

CTX = ssl.create_default_context()


def fetch_jpeg(photo_id: str, out: Path) -> None:
    url = f"https://images.unsplash.com/photo-{photo_id}?w=1400&q=80"
    req = urllib.request.Request(url, headers={"User-Agent": "KoreaTravelGuidebook/1.0"})
    with urllib.request.urlopen(req, context=CTX, timeout=45) as resp:
        data = resp.read()
    im = Image.open(io.BytesIO(data)).convert("RGB")
    # Reasonable web size
    im.thumbnail((1200, 800), Image.Resampling.LANCZOS)
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, "JPEG", quality=82, optimize=True)
    print(f"img {out.name}: {out.stat().st_size // 1024}KB {im.size}")


DETAIL_HTML = """<!DOCTYPE html>
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
  <main class="page souvenir-detail">
    <p class="back-link"><a href="../index.html" data-i18n="souvenir.backList">← 기념품 목록</a></p>
    <article class="souvenir-article">
      <h1 data-i18n="souvenir.{key}Title"></h1>
      <figure class="souvenir-hero">
        <img src="../../../Images/souvenir/{key}.jpg" alt="" data-i18n-attr="alt:souvenir.{key}Title">
      </figure>
      <p class="souvenir-lead" data-i18n="souvenir.{key}Desc"></p>
      <div class="souvenir-body">
        <p data-i18n="souvenir.{key}Body1"></p>
        <p data-i18n="souvenir.{key}Body2"></p>
      </div>
      <aside class="tip souvenir-tip">
        <h2 data-i18n="souvenir.tipTitle">팁</h2>
        <p data-i18n="souvenir.{key}Tip"></p>
      </aside>
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


def write_pages() -> None:
    for key in ITEMS:
        dest = PAGES / key / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(DETAIL_HTML.format(key=key), encoding="utf-8")
        print(f"page {key}")


def main() -> None:
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    for key in ITEMS:
        pid = SOURCES[key]
        out = IMG_DIR / f"{key}.jpg"
        try:
            fetch_jpeg(pid, out)
        except Exception as e:
            print(f"FAIL {key}: {e}")
            # solid fallback so layout still works
            im = Image.new("RGB", (1200, 800), (240, 236, 228))
            im.save(out, "JPEG", quality=80)
    write_pages()


if __name__ == "__main__":
    main()
