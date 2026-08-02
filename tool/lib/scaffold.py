# -*- coding: utf-8 -*-
"""HTML page scaffolding for dishes and shops."""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import quote

from .cache_bust import read_version
from .images import (
    discover_menu_images,
    dish_cover_path,
    rel_posix,
    shop_menu_numbered_path,
    shop_photo_path,
)
from .paths import DESSERTS_DIR, MEALS_DIR, ROOT


def maps_url_from_location(location: str) -> str:
    return (
        "https://www.google.com/maps/search/?api=1&query="
        + quote(location.strip(), safe="")
    )


def current_asset_version() -> str:
    try:
        return read_version()
    except SystemExit:
        return "0"


def dish_dir(kind: str, slug: str) -> Path:
    base = MEALS_DIR if kind == "meals" else DESSERTS_DIR
    return base / slug


def dish_index_path(kind: str, slug: str) -> Path:
    return dish_dir(kind, slug) / "index.html"


def hub_index_path(kind: str) -> Path:
    return (MEALS_DIR if kind == "meals" else DESSERTS_DIR) / "index.html"


def shop_page_path(kind: str, dish_slug: str, shop_slug: str) -> Path:
    return dish_dir(kind, dish_slug) / f"{shop_slug}.html"


def asset_prefix_from(html_path: Path) -> str:
    """Relative path from html_path's directory up to site root."""
    depth = len(html_path.parent.relative_to(ROOT).parts)
    return "../" * depth


def render_menu_gallery_html(
    kind: str,
    dish_slug: str,
    shop_slug: str,
    *,
    asset_prefix: str = "../../../../",
) -> str:
    """Render all menu images (or a menu-1 placeholder) for a shop page."""
    menus = discover_menu_images(kind, dish_slug, shop_slug)
    if not menus:
        # Placeholder so new shops have a stable first slot
        rel = rel_posix(shop_menu_numbered_path(kind, dish_slug, shop_slug, 1))
        menus_data = [(1, rel)]
    else:
        menus_data = [(m.index, m.rel) for m in menus]

    parts = ['    <div class="menu-photo-gallery">']
    for i, (_idx, rel) in enumerate(menus_data):
        caption = ""
        if i == 0:
            caption = (
                '      <figcaption data-i18n="restaurantFields.menuPhoto"></figcaption>\n'
            )
        parts.append(
            f'      <figure class="menu-photo">\n'
            f"{caption}"
            f'        <img src="{asset_prefix}{rel}" width="100%" alt="" '
            f'data-i18n-attr="alt:restaurants.{shop_slug}.menu">\n'
            f"      </figure>"
        )
    parts.append("    </div>")
    return "\n".join(parts)


_GALLERY_RE = re.compile(
    r'(?:<div class="menu-photo-gallery">.*?</div>\s*'
    r'|<figure class="menu-photo">.*?</figure>\s*)+',
    re.IGNORECASE | re.DOTALL,
)


def patch_shop_menu_gallery(
    html: str,
    kind: str,
    dish_slug: str,
    shop_slug: str,
    *,
    asset_prefix: str = "../../../../",
) -> str:
    """Replace legacy single menu-photo figure(s) with full gallery."""
    gallery = render_menu_gallery_html(
        kind, dish_slug, shop_slug, asset_prefix=asset_prefix
    )
    if _GALLERY_RE.search(html):
        return _GALLERY_RE.sub(gallery + "\n", html, count=1)
    # Insert before tip block if present
    tip = re.search(r'<div class="tip">', html, re.IGNORECASE)
    if tip:
        return html[: tip.start()] + gallery + "\n    " + html[tip.start() :]
    main_close = re.search(r"</main>", html, re.IGNORECASE)
    if main_close:
        return html[: main_close.start()] + gallery + "\n  " + html[main_close.start() :]
    return html + "\n" + gallery


def sync_shop_page_menu_gallery(
    kind: str, dish_slug: str, shop_slug: str
) -> list[str]:
    """Rewrite gallery on an existing shop HTML page. Returns notes."""
    page = shop_page_path(kind, dish_slug, shop_slug)
    if not page.is_file():
        return []
    text = page.read_text(encoding="utf-8")
    prefix = asset_prefix_from(page)
    updated = patch_shop_menu_gallery(
        text, kind, dish_slug, shop_slug, asset_prefix=prefix
    )
    if updated != text:
        page.write_text(updated, encoding="utf-8", newline="\n")
        return [f"메뉴 갤러리 HTML 갱신: {page.relative_to(ROOT).as_posix()}"]
    return []


def patch_all_shop_menu_galleries() -> list[str]:
    """One-time / on-demand: expand menu-photo on every shop detail page."""
    notes: list[str] = []
    for kind, base in (("meals", MEALS_DIR), ("desserts", DESSERTS_DIR)):
        if not base.is_dir():
            continue
        for dish_dir_path in sorted(base.iterdir()):
            if not dish_dir_path.is_dir():
                continue
            for page in sorted(dish_dir_path.glob("*.html")):
                if page.name == "index.html":
                    continue
                shop_slug = page.stem
                notes.extend(
                    sync_shop_page_menu_gallery(kind, dish_dir_path.name, shop_slug)
                )
    if not notes:
        notes.append("메뉴 갤러리: 변경된 페이지 없음 (이미 최신이거나 가게 없음)")
    else:
        notes.insert(0, f"메뉴 갤러리 패치: {len(notes)}개 페이지")
    return notes


def render_dish_page(kind: str, slug: str, emoji: str = "🍽️") -> str:
    version = current_asset_version()
    back_key = "misc.backFoods" if kind == "meals" else "misc.backDesserts"
    prefix = "../../../../"
    return f"""<!DOCTYPE html>
<html lang="ko" data-i18n-title="dishes.{slug}.title">
<head>
  <!-- asset-v: {version} -->
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{slug} | Korea Travel Guide</title>
  <link rel="stylesheet" href="{prefix}styles.css?v={version}">
</head>
<body>
  <nav class="lang-switch" aria-label="Language">
    <button type="button" data-set-lang="ko">KR</button>
    <button type="button" data-set-lang="en">EN</button>
    <button type="button" data-set-lang="ja">JP</button>
  </nav>

  <header class="site-header">
    <a href="{prefix}index.html" class="site-brand" data-i18n="common.brand">Korea Travel Guide</a>
  </header>

  <main class="page">
    <p class="back-link">
      <a href="../index.html" data-i18n="{back_key}">← Back</a>
    </p>

    <h1>{emoji} <span data-i18n="dishes.{slug}.title">{slug}</span></h1>

    <img src="{prefix}{rel_posix(dish_cover_path(slug))}" width="100%" alt="{slug}" data-i18n-attr="alt:dishes.{slug}.title">

    <section class="intro">
      <h2 data-i18n="common.about">About</h2>
      <p data-i18n="dishes.{slug}.about"></p>
    </section>

    <h2 data-i18n="common.places">Places</h2>
    <p class="tabs-help" data-i18n="common.shopsComing"></p>
    <p data-i18n="common.emptyPlaces">등록된 곳이 아직 없습니다.</p>
  </main>

  <footer class="site-footer">
    <hr>
    <img src="{prefix}Images/cover/footer-korea.png" width="100%" alt="Korea Travel">
    <p class="footer-note" data-i18n="common.footer">© Korea Travel Guide</p>
  </footer>

  <script src="{prefix}i18n/messages.js?v={version}"></script>
  <script src="{prefix}js/i18n.js?v={version}"></script>
</body>
</html>
"""


def render_shop_page(kind: str, dish_slug: str, shop_slug: str) -> str:
    version = current_asset_version()
    prefix = "../../../../"
    photo = rel_posix(shop_photo_path(kind, dish_slug, shop_slug))
    gallery = render_menu_gallery_html(
        kind, dish_slug, shop_slug, asset_prefix=prefix
    )

    return f"""<!DOCTYPE html>
<html lang="ko" data-i18n-title="restaurants.{shop_slug}.name">
<head>
  <!-- asset-v: {version} -->
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{shop_slug}</title>
  <link rel="stylesheet" href="{prefix}styles.css?v={version}">
</head>
<body>
  <nav class="lang-switch" aria-label="Language">
    <button type="button" data-set-lang="ko">KR</button>
    <button type="button" data-set-lang="en">EN</button>
    <button type="button" data-set-lang="ja">JP</button>
  </nav>
  <header class="site-header">
    <a href="{prefix}index.html" class="site-brand" data-i18n="common.brand">Korea Travel Guide</a>
  </header>
  <main class="page">
    <p class="back-link">
      <a href="./index.html">← <span data-i18n="dishes.{dish_slug}.title"></span></a>
    </p>
    <h1 data-i18n="restaurants.{shop_slug}.name"></h1>
    <img class="shop-photo" src="{prefix}{photo}" width="100%" alt="" data-i18n-attr="alt:restaurants.{shop_slug}.name">
    <p data-i18n="restaurants.{shop_slug}.about"></p>
    <table class="content-table">
      <tr><th data-i18n="restaurantFields.name"></th><td data-i18n="restaurants.{shop_slug}.name"></td></tr>
      <tr><th data-i18n="restaurantFields.location"></th><td><a class="maps-link" href="#" target="_blank" rel="noopener noreferrer" data-i18n-attr="href:restaurants.{shop_slug}.mapsUrl"><span data-i18n="restaurants.{shop_slug}.location"></span></a></td></tr>
      <tr><th data-i18n="restaurantFields.menu"></th><td data-i18n="restaurants.{shop_slug}.menu"></td></tr>
      <tr><th data-i18n="restaurantFields.price"></th><td data-i18n="restaurants.{shop_slug}.price"></td></tr>
    </table>
{gallery}
    <div class="tip">
      <h3 data-i18n="common.tip">TIP</h3>
      <p data-i18n="restaurants.{shop_slug}.tip"></p>
    </div>
  </main>
  <footer class="site-footer">
    <hr>
    <img src="{prefix}Images/cover/footer-korea.png" width="100%" alt="Korea Travel">
    <p class="footer-note" data-i18n="common.footer"></p>
  </footer>
  <script src="{prefix}i18n/messages.js?v={version}"></script>
  <script src="{prefix}js/i18n.js?v={version}"></script>
</body>
</html>
"""


def dish_card_html(kind: str, slug: str, emoji: str) -> str:
    cover = "../../../" + rel_posix(dish_cover_path(slug))
    return f"""      <article class="card">
        <a href="./{slug}/index.html">
          <img src="{cover}" width="100%" alt="" data-i18n-attr="alt:dishes.{slug}.title">
        </a>
        <h2>{emoji} <span data-i18n="dishes.{slug}.title"></span></h2>
        <p data-i18n="dishes.{slug}.desc"></p>
        <p><a href="./{slug}/index.html" data-i18n="common.viewMore">View more →</a></p>
      </article>
"""


def shop_card_html(kind: str, dish_slug: str, shop_slug: str) -> str:
    img = "../../../../" + rel_posix(shop_photo_path(kind, dish_slug, shop_slug))
    return f"""      <article class="card">
        <a href="./{shop_slug}.html">
          <img src="{img}" width="100%" alt="" data-i18n-attr="alt:restaurants.{shop_slug}.name">
        </a>
        <h2><span data-i18n="restaurants.{shop_slug}.name"></span></h2>
        <p data-i18n="restaurants.{shop_slug}.menu"></p>
        <p><a href="./{shop_slug}.html" data-i18n="common.viewMore">View more →</a></p>
      </article>
"""


def insert_before_card_grid_close(html: str, card_html: str) -> str:
    """Insert a card before the closing </div> of .card-grid."""
    marker = re.search(
        r'(</article>\s*)(</div>\s*</main>)',
        html,
        re.IGNORECASE | re.DOTALL,
    )
    if marker:
        return html[: marker.end(1)] + card_html + html[marker.start(2) :]

    # Empty places placeholder → replace with card-grid
    empty = re.search(
        r'<p[^>]*data-i18n="common\.emptyPlaces"[^>]*>.*?</p>',
        html,
        re.IGNORECASE | re.DOTALL,
    )
    if empty:
        grid = (
            '<div class="card-grid">\n'
            + card_html
            + "    </div>\n"
        )
        # Also remove shopsComing help if present just above
        before = html[: empty.start()]
        after = html[empty.end() :]
        help_re = re.compile(
            r'<p class="tabs-help"[^>]*data-i18n="common\.shopsComing"[^>]*>.*?</p>\s*',
            re.IGNORECASE | re.DOTALL,
        )
        before = help_re.sub(
            '<p class="tabs-help" data-i18n="common.shopsHelp"></p>\n    ',
            before,
            count=1,
        )
        return before + grid + after

    # Fallback: before </main>
    main_close = re.search(r"</main>", html, re.IGNORECASE)
    if main_close:
        block = (
            '    <div class="card-grid">\n'
            + card_html
            + "    </div>\n  "
        )
        return html[: main_close.start()] + block + html[main_close.start() :]
    return html + "\n" + card_html


def remove_card_referencing(html: str, href_fragment: str) -> str:
    """Remove an <article class="card"> that links to href_fragment."""
    pattern = re.compile(
        r'\s*<article class="card">\s*'
        r'(?:(?!</article>).)*?'
        + re.escape(href_fragment)
        + r'(?:(?!</article>).)*?'
        r"</article>",
        re.IGNORECASE | re.DOTALL,
    )
    return pattern.sub("", html, count=1)


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def rewrite_shop_slug_in_html(html: str, old_slug: str, new_slug: str) -> str:
    """Rewrite restaurant i18n keys and image basename references for a shop rename."""
    text = html
    text = text.replace(f"restaurants.{old_slug}.", f"restaurants.{new_slug}.")
    text = text.replace(f"/{old_slug}.jpg", f"/{new_slug}.jpg")
    text = text.replace(f"/{old_slug}-menu.jpg", f"/{new_slug}-menu.jpg")
    # Numbered menus: -menu-1.jpg, -menu-01.jpg, …
    text = re.sub(
        rf"/({re.escape(old_slug)})-menu-(\d+)\.jpg",
        rf"/{new_slug}-menu-\2.jpg",
        text,
        flags=re.IGNORECASE,
    )
    return text
