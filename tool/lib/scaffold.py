# -*- coding: utf-8 -*-
"""HTML page scaffolding for dishes and shops."""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import quote

from .cache_bust import read_version
from .images import (
    discover_menu_images,
    rel_posix,
    shop_dir,
    shop_media_dir,
    shop_menu_numbered_path,
)
from .paths import DESSERTS_DIR, MEALS_DIR, PLACES_DIR, ROOT, TRANSPORT_DIR


def maps_url_from_location(location: str) -> str:
    return (
        "https://www.google.com/maps/search/?api=1&query="
        + quote(location.strip(), safe="")
    )


def maps_embed_url_from_location(location: str) -> str:
    """Google Maps iframe embed (no API key) from address or place name."""
    q = quote(location.strip(), safe="")
    return f"https://maps.google.com/maps?q={q}&hl=ko&z=15&output=embed"


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
    """Canonical shop detail page: …/{shop}/index.html."""
    return shop_dir(kind, dish_slug, shop_slug) / "index.html"


def legacy_shop_page_path(kind: str, dish_slug: str, shop_slug: str) -> Path:
    """Pre-migration flat file: …/{shop}.html."""
    return dish_dir(kind, dish_slug) / f"{shop_slug}.html"


def resolve_shop_page(kind: str, dish_slug: str, shop_slug: str) -> Path | None:
    page = shop_page_path(kind, dish_slug, shop_slug)
    if page.is_file():
        return page
    legacy = legacy_shop_page_path(kind, dish_slug, shop_slug)
    if legacy.is_file():
        return legacy
    return None


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


def iter_shop_pages(kind: str, dish_slug: str) -> list[tuple[str, Path]]:
    """Return (shop_slug, html_path) for shop details under a dish."""
    d = dish_dir(kind, dish_slug)
    if not d.is_dir():
        return []
    out: list[tuple[str, Path]] = []
    seen: set[str] = set()
    for page in sorted(d.glob("*.html")):
        if page.name == "index.html":
            continue
        out.append((page.stem, page))
        seen.add(page.stem)
    for child in sorted(d.iterdir()):
        if not child.is_dir() or child.name in seen:
            continue
        index = child / "index.html"
        if index.is_file():
            out.append((child.name, index))
    return out


def sync_shop_page_menu_gallery(
    kind: str, dish_slug: str, shop_slug: str
) -> list[str]:
    """Rewrite gallery on an existing shop HTML page. Returns notes."""
    page = resolve_shop_page(kind, dish_slug, shop_slug)
    if not page:
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
            for shop_slug, _page in iter_shop_pages(kind, dish_dir_path.name):
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

    <img src="media/cover.jpg" width="100%" alt="{slug}" data-i18n-attr="alt:dishes.{slug}.title">

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


def render_shop_body_mount(shop_slug: str) -> str:
    """Mount point for js/shop-body.js (+ tip fallback when body empty)."""
    return (
        f'    <div id="shop-body" class="shop-body" data-shop-slug="{shop_slug}"></div>\n'
        f'    <div class="tip" data-shop-tip-fallback>\n'
        f'      <h3 data-i18n="common.tip">TIP</h3>\n'
        f'      <p data-i18n="restaurants.{shop_slug}.tip"></p>\n'
        f"    </div>"
    )


def render_shop_visual(shop_slug: str) -> str:
    """
    Simple public shop layout:
      1) Cover / storefront photo
      2) Shop name (h1)
      3) Detailed shop info (address, phone, hours, about/tips, optional map-app link)
      4) Menu list (text; filled from i18n by content-body.js)
      5) Photos CTA → placeUrl (no scraped review gallery)
      6) Location map iframe (Google Maps embed)
    """
    return f"""    <div class="shop-detail" data-shop-detail data-shop-slug="{shop_slug}">
      <img class="shop-photo" data-shop-photo src="media/cover.jpg" width="100%" alt="" data-i18n-attr="alt:restaurants.{shop_slug}.name">
      <h1 data-i18n="restaurants.{shop_slug}.name"></h1>
      <section class="shop-info-block" data-shop-info-block>
        <h2 class="shop-info-block__title" data-i18n="restaurantFields.detailInfo">자세한 가게 정보</h2>
        <dl class="shop-info" data-shop-info>
          <div class="shop-info__row" data-shop-info-row="name">
            <dt data-i18n="restaurantFields.name">가게명</dt>
            <dd data-i18n="restaurants.{shop_slug}.name" data-shop-info-name></dd>
          </div>
          <div class="shop-info__row" data-shop-info-row="location">
            <dt data-i18n="restaurantFields.location">위치</dt>
            <dd data-i18n="restaurants.{shop_slug}.location"></dd>
          </div>
          <div class="shop-info__row" data-shop-info-row="phone" hidden>
            <dt data-i18n="restaurantFields.phone">전화</dt>
            <dd data-i18n="restaurants.{shop_slug}.phone"></dd>
          </div>
          <div class="shop-info__row" data-shop-info-row="hours" hidden>
            <dt data-i18n="restaurantFields.hours">영업시간</dt>
            <dd data-i18n="restaurants.{shop_slug}.hours"></dd>
          </div>
          <div class="shop-info__row shop-info__row--about" data-shop-info-row="about" hidden>
            <dt data-i18n="restaurantFields.about">소개</dt>
            <dd data-i18n="restaurants.{shop_slug}.about" data-shop-info-about></dd>
          </div>
          <div class="shop-info__row shop-info__row--place" data-shop-info-row="place" hidden>
            <dt data-i18n="restaurantFields.openOnMaps">지도 앱</dt>
            <dd>
              <a class="shop-place-link shop-place-link--subtle" data-shop-place-link href="#" target="_blank" rel="noopener noreferrer"
                 data-i18n="restaurantFields.openPlace">지도에서 열기</a>
            </dd>
          </div>
        </dl>
      </section>
      <section class="shop-menu-block" data-shop-menu-block hidden>
        <h2 class="shop-menu-block__title" data-i18n="restaurantFields.menuList">메뉴</h2>
        <ul class="shop-menu-list" data-shop-menu-list></ul>
      </section>
      <section class="shop-photos-cta shop-gallery-block" data-shop-photos-cta data-shop-gallery-block hidden>
        <h2 class="shop-photos-cta__title" data-i18n="restaurantFields.photoGallery">사진·리뷰 더 보기</h2>
        <p class="shop-photos-cta__note" data-i18n="restaurantFields.photosOnMapsNote">추가 사진과 리뷰는 지도·플레이스 페이지에서 확인할 수 있습니다.</p>
        <a class="shop-place-link shop-photos-cta__link" data-shop-photos-link href="#" target="_blank" rel="noopener noreferrer"
           data-i18n="restaurantFields.viewOnPlaceMaps">네이버 지도에서 보기</a>
      </section>
      <div class="shop-map" data-shop-map hidden>
        <div class="place-map-wrap">
          <iframe
            class="place-map-embed shop-map-embed"
            title="map"
            loading="lazy"
            referrerpolicy="no-referrer-when-downgrade"
            allowfullscreen
            data-i18n-attr="src:restaurants.{shop_slug}.mapsEmbedUrl"
            src="about:blank"></iframe>
        </div>
      </div>
    </div>"""


_SHOP_BODY_SECTION_RE = re.compile(
    r'(?:'
    r'<div class="menu-photo-gallery">.*?</div>\s*'
    r'|<figure class="menu-photo">.*?</figure>\s*'
    r'|<div id="shop-body"[^>]*>.*?</div>\s*'
    r'|<div class="tip"[^>]*>.*?</div>\s*'
    r')+',
    re.IGNORECASE | re.DOTALL,
)


def patch_shop_body_section(html: str, shop_slug: str) -> str:
    """Replace menu gallery + tip with shop-body mount (+ tip fallback)."""
    mount = render_shop_body_mount(shop_slug)
    if _SHOP_BODY_SECTION_RE.search(html):
        return _SHOP_BODY_SECTION_RE.sub(mount + "\n", html, count=1)
    # Insert after content-table if present
    table_end = re.search(r"</table>\s*", html, re.IGNORECASE)
    if table_end:
        return html[: table_end.end()] + mount + "\n" + html[table_end.end() :]
    main_close = re.search(r"</main>", html, re.IGNORECASE)
    if main_close:
        return html[: main_close.start()] + mount + "\n  " + html[main_close.start() :]
    return html + "\n" + mount


def ensure_shop_body_script(html: str, *, asset_prefix: str, version: str) -> str:
    """Ensure content-body.js (or legacy shop-body.js) is loaded after i18n.js."""
    if "content-body.js" in html:
        return re.sub(
            r'(src="[^"]*content-body\.js)(?:\?v=[^"]*)?(")',
            rf"\1?v={version}\2",
            html,
            count=1,
        )
    if "shop-body.js" in html:
        return re.sub(
            r'(src="[^"]*)shop-body\.js((?:\?v=[^"]*)?")',
            rf"\1content-body.js\2",
            html,
            count=1,
        )
    tag = (
        f'  <script src="{asset_prefix}js/content-body.js?v={version}"></script>\n'
    )
    # Insert after i18n.js
    m = re.search(
        r'<script[^>]+src="[^"]*i18n\.js[^"]*"[^>]*>\s*</script>\s*',
        html,
        re.IGNORECASE,
    )
    if m:
        return html[: m.end()] + tag + html[m.end() :]
    # Before </body>
    body_close = re.search(r"</body>", html, re.IGNORECASE)
    if body_close:
        return html[: body_close.start()] + tag + html[body_close.start() :]
    return html + "\n" + tag


def sync_shop_page_body(kind: str, dish_slug: str, shop_slug: str) -> list[str]:
    """Rewrite freeform body mount on an existing shop HTML page."""
    page = resolve_shop_page(kind, dish_slug, shop_slug)
    if not page:
        return []
    text = page.read_text(encoding="utf-8")
    prefix = asset_prefix_from(page)
    version = current_asset_version()
    updated = patch_shop_body_section(text, shop_slug)
    updated = ensure_shop_body_script(updated, asset_prefix=prefix, version=version)
    # Also ensure data-shop-slug matches current slug if mount already existed oddly
    updated = re.sub(
        r'(id="shop-body"[^>]*data-shop-slug=")[^"]*(")',
        rf"\g<1>{shop_slug}\2",
        updated,
        count=1,
    )
    if updated != text:
        page.write_text(updated, encoding="utf-8", newline="\n")
        return [f"본문 영역 HTML 갱신: {page.relative_to(ROOT).as_posix()}"]
    return []


def sync_all_shop_page_bodies() -> list[str]:
    notes: list[str] = []
    for kind, base in (("meals", MEALS_DIR), ("desserts", DESSERTS_DIR)):
        if not base.is_dir():
            continue
        for dish_dir_path in sorted(base.iterdir()):
            if not dish_dir_path.is_dir():
                continue
            for shop_slug, _page in iter_shop_pages(kind, dish_dir_path.name):
                notes.extend(
                    sync_shop_page_body(kind, dish_dir_path.name, shop_slug)
                )
    if not notes:
        notes.append("본문 HTML: 변경된 페이지 없음")
    else:
        notes.insert(0, f"본문 HTML 동기화: {len(notes)}개 페이지")
    return notes


def render_shop_page(kind: str, dish_slug: str, shop_slug: str) -> str:
    version = current_asset_version()
    page = shop_page_path(kind, dish_slug, shop_slug)
    prefix = asset_prefix_from(page)
    body_mount = render_shop_body_mount(shop_slug)
    visual = render_shop_visual(shop_slug)
    # Ensure media/ exists for new shops
    shop_media_dir(kind, dish_slug, shop_slug).mkdir(parents=True, exist_ok=True)

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
      <a href="../index.html">← <span data-i18n="dishes.{dish_slug}.title"></span></a>
    </p>
{visual}
{body_mount}
  </main>
  <footer class="site-footer">
    <hr>
    <img src="{prefix}Images/cover/footer-korea.png" width="100%" alt="Korea Travel">
    <p class="footer-note" data-i18n="common.footer"></p>
  </footer>
  <script src="{prefix}i18n/messages.js?v={version}"></script>
  <script src="{prefix}js/i18n.js?v={version}"></script>
  <script src="{prefix}js/content-body.js?v={version}"></script>
</body>
</html>
"""


# Redundant about + content-table after visual (old layout clutter)
_SHOP_CLUTTER_RE = re.compile(
    r'(?:'
    r'<p\s+data-i18n="restaurants\.[^"]+\.about"[^>]*>.*?</p>\s*'
    r')?'
    r'<table class="content-table">[\s\S]*?</table>\s*',
    re.IGNORECASE,
)

_SHOP_LEGACY_HEADING_RE = re.compile(
    r'<h1\b[^>]*>[\s\S]*?</h1>\s*'
    r'(?:<p class="region-badge">[\s\S]*?</p>\s*)?',
    re.IGNORECASE,
)

_SHOP_BODY_START_RE = re.compile(
    r'(?:'
    r'<div id="shop-body"\b'
    r'|<div class="tip"\b'
    r'|</main>'
    r')',
    re.IGNORECASE,
)


def _consume_shop_visual_prefix(rest: str) -> tuple[str, str]:
    """
    Strip one legacy/new shop visual block from the start of `rest`.
    Returns (region_badge_html, remainder).
    """
    region_badge = ""
    s = rest.lstrip("\n\r\t ")

    # Optional legacy h1 (+ region badge) before visual
    hm = _SHOP_LEGACY_HEADING_RE.match(s)
    if hm:
        bm = re.search(
            r'(<p class="region-badge">[\s\S]*?</p>\s*)',
            hm.group(0),
            re.IGNORECASE,
        )
        if bm:
            region_badge = bm.group(1)
        s = s[hm.end() :].lstrip("\n\r\t ")

    # New simple block
    if re.match(r'<div class="shop-detail"\b', s, re.IGNORECASE):
        end = _find_matching_div_end(s)
        if end > 0:
            return region_badge, s[end:].lstrip("\n\r\t ")
        bm = _SHOP_BODY_START_RE.search(s)
        if bm:
            return region_badge, s[bm.start() :]

    # Old dual panel
    if re.match(r'<div class="shop-place-panel"\b', s, re.IGNORECASE):
        end = _find_matching_div_end(s)
        if end > 0:
            s = s[end:].lstrip("\n\r\t ")
        pm = re.match(r'<img class="shop-photo"[^>]*>\s*', s, re.IGNORECASE)
        if pm:
            s = s[pm.end() :].lstrip("\n\r\t ")
        return region_badge, s

    # Lone cover photo
    pm = re.match(r'<img class="shop-photo"[^>]*>\s*', s, re.IGNORECASE)
    if pm:
        return region_badge, s[pm.end() :].lstrip("\n\r\t ")

    return region_badge, rest if not region_badge else s


def _find_matching_div_end(html: str) -> int:
    """Return index after the closing </div> that matches the first opening <div>."""
    open_re = re.compile(r"<div\b[^>]*>", re.IGNORECASE)
    close_re = re.compile(r"</div\s*>", re.IGNORECASE)
    m0 = open_re.match(html)
    if not m0:
        return -1
    depth = 1
    pos = m0.end()
    while depth > 0 and pos < len(html):
        mo = open_re.search(html, pos)
        mc = close_re.search(html, pos)
        if not mc:
            return -1
        if mo and mo.start() < mc.start():
            depth += 1
            pos = mo.end()
        else:
            depth -= 1
            pos = mc.end()
    return pos if depth == 0 else -1


def sync_shop_page_visual(kind: str, dish_slug: str, shop_slug: str) -> list[str]:
    """Ensure shop HTML has simple cover → name → info → map layout (idempotent)."""
    page = resolve_shop_page(kind, dish_slug, shop_slug)
    if not page or not page.is_file():
        return []
    html = page.read_text(encoding="utf-8")
    visual = render_shop_visual(shop_slug).rstrip() + "\n"
    notes: list[str] = []

    back = re.search(
        r'(<p class="back-link">[\s\S]*?</p>\s*)',
        html,
        re.IGNORECASE,
    )
    if not back:
        return []

    start = back.end(0)
    # Prefer shop-body; also accept body mount bundled with tip fallback
    body_m = re.search(r'<div\s+id="shop-body"', html[start:], re.IGNORECASE)
    tip_m = re.search(
        r'<div\s+class="tip"[^>]*data-shop-tip-fallback',
        html[start:],
        re.IGNORECASE,
    )
    main_m = re.search(r"</main>", html[start:], re.IGNORECASE)

    if body_m:
        cut = start + body_m.start()
        tail = html[cut:]
        # If a duplicate tip was inserted before an older tip, leave as-is
    elif tip_m:
        cut = start + tip_m.start()
        # Only insert body mount (not tip) — tip already at cut
        tail = (
            f'    <div id="shop-body" class="shop-body" data-shop-slug="{shop_slug}"></div>\n'
            + html[cut:]
        )
        notes.append("shop-body mount 복구")
    elif main_m:
        cut = start + main_m.start()
        tail = render_shop_body_mount(shop_slug) + "\n  " + html[cut:]
        notes.append("shop-body mount 복구")
    else:
        return []

    mid = html[start:cut]

    region_badge = ""
    bm = re.search(
        r'(<p class="region-badge">[\s\S]*?</p>\s*)',
        mid,
        re.IGNORECASE,
    )
    if bm:
        region_badge = bm.group(1)

    if region_badge:
        visual_out = visual.replace(
            f'<h1 data-i18n="restaurants.{shop_slug}.name"></h1>',
            f'<h1 data-i18n="restaurants.{shop_slug}.name"></h1>\n'
            f"      {region_badge.strip()}",
            1,
        )
    else:
        visual_out = visual

    new_html = html[:start] + visual_out + tail

    cleaned, n_sub = _SHOP_CLUTTER_RE.subn("", new_html, count=1)
    if n_sub:
        new_html = cleaned
        notes.append("중복 소개·정보 표 제거")

    # Ensure content-body script is present
    prefix = asset_prefix_from(page)
    version = current_asset_version()
    new_html = ensure_shop_body_script(new_html, asset_prefix=prefix, version=version)

    if new_html == html:
        return []
    page.write_text(new_html, encoding="utf-8", newline="\n")
    notes.insert(0, f"가게 비주얼 동기화: {page.relative_to(ROOT).as_posix()}")
    return notes


def sync_all_shop_page_visuals() -> list[str]:
    notes: list[str] = []
    for kind, base in (("meals", MEALS_DIR), ("desserts", DESSERTS_DIR)):
        if not base.is_dir():
            continue
        for dish_dir_path in sorted(base.iterdir()):
            if not dish_dir_path.is_dir():
                continue
            for shop_slug, _page in iter_shop_pages(kind, dish_dir_path.name):
                notes.extend(
                    sync_shop_page_visual(kind, dish_dir_path.name, shop_slug)
                )
    if not notes:
        notes.append("가게 비주얼: 변경된 페이지 없음")
    else:
        notes.insert(0, f"가게 비주얼 동기화: {len(notes)}개 페이지")
    return notes


def dish_card_html(kind: str, slug: str, emoji: str) -> str:
    return f"""      <article class="card">
        <a href="./{slug}/index.html">
          <img src="./{slug}/media/cover.jpg" width="100%" alt="" data-i18n-attr="alt:dishes.{slug}.title">
        </a>
        <h2>{emoji} <span data-i18n="dishes.{slug}.title"></span></h2>
        <p data-i18n="dishes.{slug}.desc"></p>
        <p><a href="./{slug}/index.html" data-i18n="common.viewMore">View more →</a></p>
      </article>
"""


def shop_card_html(kind: str, dish_slug: str, shop_slug: str) -> str:
    return f"""      <article class="card">
        <a href="./{shop_slug}/index.html">
          <img src="./{shop_slug}/media/cover.jpg" width="100%" alt="" data-i18n-attr="alt:restaurants.{shop_slug}.name">
        </a>
        <h2><span data-i18n="restaurants.{shop_slug}.name"></span></h2>
        <p data-i18n="restaurants.{shop_slug}.menu"></p>
        <p><a href="./{shop_slug}/index.html" data-i18n="common.viewMore">View more →</a></p>
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
    text = text.replace(f'data-shop-slug="{old_slug}"', f'data-shop-slug="{new_slug}"')
    text = text.replace(f"/{old_slug}.jpg", f"/{new_slug}.jpg")
    text = text.replace(f"/{old_slug}-menu.jpg", f"/{new_slug}-menu.jpg")
    # Numbered menus: -menu-1.jpg, -menu-01.jpg, …
    text = re.sub(
        rf"/({re.escape(old_slug)})-menu-(\d+)\.jpg",
        rf"/{new_slug}-menu-\2.jpg",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        rf"/({re.escape(old_slug)})-body-(\d+)\.jpg",
        rf"/{new_slug}-body-\2.jpg",
        text,
        flags=re.IGNORECASE,
    )
    return text


def place_dir(slug: str) -> Path:
    return PLACES_DIR / slug


def place_index_path(slug: str) -> Path:
    return place_dir(slug) / "index.html"


def place_media_dir(slug: str) -> Path:
    return place_dir(slug) / "media"


def transport_hub_path() -> Path:
    return TRANSPORT_DIR / "index.html"


def render_place_page(slug: str) -> str:
    version = current_asset_version()
    page = place_index_path(slug)
    prefix = asset_prefix_from(page)
    place_media_dir(slug).mkdir(parents=True, exist_ok=True)
    return f"""<!DOCTYPE html>
<html lang="ko" data-i18n-title="places.{slug}.name">
<head>
  <!-- asset-v: {version} -->
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{slug}</title>
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
  <main class="page article-page place-detail">
    <p class="back-link">
      <a href="../../index.html" data-i18n="transport.backPlaces">← 대표 명소</a>
    </p>
    <article class="place-article" data-place-slug="{slug}">
      <h1 data-i18n="places.{slug}.name"></h1>
      <p class="article-lead" data-i18n="places.{slug}.desc"></p>
      <p class="place-region-badge"><span data-i18n="places.{slug}.regionLabel"></span></p>
      <p class="place-address">
        <a class="maps-link" href="#" target="_blank" rel="noopener noreferrer"
           data-i18n-attr="href:places.{slug}.mapsUrl">
          <span data-i18n="places.{slug}.address"></span>
        </a>
      </p>
      <div class="place-map-wrap">
        <iframe
          class="place-map-embed"
          title="map"
          loading="lazy"
          referrerpolicy="no-referrer-when-downgrade"
          allowfullscreen
          data-i18n-attr="src:places.{slug}.mapsEmbedUrl"
          src="about:blank"></iframe>
      </div>
      <div class="content-body" data-content-body data-body-path="places.{slug}.body"></div>
      <div class="tip" data-content-body-fallback>
        <h3 data-i18n="transport.howLabel">가는 방법</h3>
        <p data-i18n="places.{slug}.how"></p>
      </div>
    </article>
  </main>
  <footer class="site-footer">
    <hr>
    <img src="{prefix}Images/cover/footer-korea.png" width="100%" alt="Korea Travel">
    <p class="footer-note" data-i18n="common.footer">© Korea Travel Guide</p>
  </footer>
  <script src="{prefix}i18n/messages.js?v={version}"></script>
  <script src="{prefix}js/i18n.js?v={version}"></script>
  <script src="{prefix}js/content-body.js?v={version}"></script>
</body>
</html>
"""


def place_card_html(slug: str) -> str:
    return f"""                  <a class="place-card-link" href="places/{slug}/index.html" data-place-slug="{slug}">
                    <article class="place-card">
                      <h3 data-i18n="places.{slug}.name"></h3>
                      <p data-i18n="places.{slug}.desc"></p>
                      <p class="place-how"><strong data-i18n="transport.howLabel"></strong> <span data-i18n="places.{slug}.how"></span></p>
                      <p class="place-more" data-i18n="common.viewMore">View more →</p>
                    </article>
                  </a>
"""


def render_region_place_grid(slugs: list[str]) -> str:
    cards = "".join(place_card_html(s) for s in slugs)
    return f'                <div class="place-grid">\n{cards}                </div>\n'


def sync_transport_hub_places(region_slugs: dict[str, list[str]]) -> list[str]:
    """Rewrite place grids inside transportation/index.html from slug lists."""
    path = transport_hub_path()
    if not path.is_file():
        return ["교통 허브 페이지 없음"]
    text = path.read_text(encoding="utf-8")
    notes: list[str] = []
    for region, slugs in region_slugs.items():
        grid = render_region_place_grid(slugs)
        pattern = re.compile(
            rf'(<div class="tab-panel" role="tabpanel" data-region-panel="{re.escape(region)}"[^>]*>\s*)'
            r'(?:<div class="place-grid">.*?</div>\s*)?',
            re.IGNORECASE | re.DOTALL,
        )

        def _repl(m: re.Match[str], g: str = grid) -> str:
            return m.group(1) + g

        new_text, n = pattern.subn(_repl, text, count=1)
        if n:
            text = new_text
            notes.append(f"허브 그리드 갱신: {region} ({len(slugs)}곳)")
        else:
            notes.append(f"허브 패널을 찾지 못함: {region}")
    if notes:
        path.write_text(text, encoding="utf-8", newline="\n")
    return notes
