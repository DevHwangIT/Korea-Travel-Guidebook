# -*- coding: utf-8 -*-
"""Migrate section prose → body blocks and patch HTML mounts. Run once from repo root."""
from __future__ import annotations

import re
import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parent
sys.path.insert(0, str(TOOL_DIR))

from lib import content_body  # noqa: E402
from lib.cache_bust import read_version  # noqa: E402

VERSION = read_version()


def ensure_script(html: str, *, prefix: str) -> str:
    if "content-body.js" in html:
        return re.sub(
            r'(src="[^"]*content-body\.js)(?:\?v=[^"]*)?(")',
            rf"\1?v={VERSION}\2",
            html,
            count=1,
        )
    tag = f'  <script src="{prefix}js/content-body.js?v={VERSION}"></script>\n'
    m = re.search(
        r'<script[^>]+src="[^"]*i18n\.js[^"]*"[^>]*>\s*</script>\s*',
        html,
        re.I,
    )
    if m:
        return html[: m.end()] + tag + html[m.end() :]
    body_close = re.search(r"</body>", html, re.I)
    if body_close:
        return html[: body_close.start()] + tag + html[body_close.start() :]
    return html + "\n" + tag


def wrap_fallback(inner: str) -> str:
    return f'<div data-content-body-fallback>\n{inner}\n      </div>'


def patch_before_trip(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    # docs panel
    text = re.sub(
        r'(<div class="tab-panel tip-article" role="tabpanel" data-prep-panel="docs"[^>]*>\s*'
        r'<h2[^>]*>.*?</h2>\s*)'
        r'(<p data-i18n="beforeTrip\.docs1"></p>\s*'
        r'<p data-i18n="beforeTrip\.docs2"></p>\s*'
        r'<p data-i18n="beforeTrip\.docs3"></p>)',
        r'\1<div class="content-body" data-content-body data-body-path="beforeTrip.docsBody"></div>\n'
        r'          ' + wrap_fallback(
            '          <p data-i18n="beforeTrip.docs1"></p>\n'
            '          <p data-i18n="beforeTrip.docs2"></p>\n'
            '          <p data-i18n="beforeTrip.docs3"></p>'
        ),
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r'(<div class="tab-panel tip-article" role="tabpanel" data-prep-panel="money"[^>]*>\s*'
        r'<h2[^>]*>.*?</h2>\s*)'
        r'(<p data-i18n="beforeTrip\.money1"></p>\s*'
        r'<p data-i18n="beforeTrip\.money2"></p>\s*'
        r'<p data-i18n="beforeTrip\.money3"></p>)',
        r'\1<div class="content-body" data-content-body data-body-path="beforeTrip.moneyBody"></div>\n'
        r'          ' + wrap_fallback(
            '          <p data-i18n="beforeTrip.money1"></p>\n'
            '          <p data-i18n="beforeTrip.money2"></p>\n'
            '          <p data-i18n="beforeTrip.money3"></p>'
        ),
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r'(<div class="tab-panel tip-article" role="tabpanel" data-prep-panel="connect"[^>]*>\s*'
        r'<h2[^>]*>.*?</h2>\s*)'
        r'(<p data-i18n="beforeTrip\.connect1"></p>\s*'
        r'<p data-i18n="beforeTrip\.connect2"></p>\s*'
        r'<p data-i18n="beforeTrip\.connect3"></p>)',
        r'\1<div class="content-body" data-content-body data-body-path="beforeTrip.connectBody"></div>\n'
        r'          ' + wrap_fallback(
            '          <p data-i18n="beforeTrip.connect1"></p>\n'
            '          <p data-i18n="beforeTrip.connect2"></p>\n'
            '          <p data-i18n="beforeTrip.connect3"></p>'
        ),
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r'(<div class="tab-panel tip-article" role="tabpanel" data-prep-panel="pack"[^>]*>\s*'
        r'<h2[^>]*>.*?</h2>\s*)'
        r'(<p data-i18n="beforeTrip\.pack1"></p>\s*'
        r'<p data-i18n="beforeTrip\.pack2"></p>\s*'
        r'<p data-i18n="beforeTrip\.pack3"></p>)',
        r'\1<div class="content-body" data-content-body data-body-path="beforeTrip.packBody"></div>\n'
        r'          ' + wrap_fallback(
            '          <p data-i18n="beforeTrip.pack1"></p>\n'
            '          <p data-i18n="beforeTrip.pack2"></p>\n'
            '          <p data-i18n="beforeTrip.pack3"></p>'
        ),
        text,
        count=1,
        flags=re.S,
    )
    text = ensure_script(text, prefix="../../")
    if text != original:
        path.write_text(text, encoding="utf-8", newline="\n")
        return True
    return False


def patch_shopping(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    replacements = [
        (
            "beauty",
            "shopping.oliveBody",
            [
                'shopping.olive1',
                'shopping.olive2',
                'shopping.olive3',
            ],
            "shopping.oliveTitle",
        ),
        (
            "daily",
            "shopping.daisoBody",
            ["shopping.daiso1", "shopping.daiso2"],
            "shopping.daisoTitle",
        ),
        (
            "duty",
            "shopping.dutyBody",
            ["shopping.duty1", "shopping.duty2"],
            "shopping.dutyTitle",
        ),
        (
            "market",
            "shopping.marketBody",
            ["shopping.market1", "shopping.market2"],
            "shopping.marketTitle",
        ),
    ]
    for panel, body_path, paras, title_key in replacements:
        para_html = "\n".join(f'          <p data-i18n="{p}"></p>' for p in paras)
        para_re = r"\s*".join(
            rf'<p data-i18n="{re.escape(p)}"></p>' for p in paras
        )
        text = re.sub(
            rf'(<div class="tab-panel tip-article" role="tabpanel" data-shop-panel="{panel}"[^>]*>\s*'
            rf'<h2 data-i18n="{re.escape(title_key)}"[^>]*></h2>\s*)'
            rf'({para_re})',
            rf'\1<div class="content-body" data-content-body data-body-path="{body_path}"></div>\n'
            rf'          <div data-content-body-fallback>\n{para_html}\n          </div>',
            text,
            count=1,
            flags=re.S,
        )
    text = ensure_script(text, prefix="../../")
    if text != original:
        path.write_text(text, encoding="utf-8", newline="\n")
        return True
    return False


def patch_convenience_index(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    text = re.sub(
        r'(<h1 data-i18n="misc\.convenienceTitle"[^>]*>.*?</h1>\s*)'
        r'(<p data-i18n="convenience\.intro"></p>)',
        r'\1<div class="content-body" data-content-body data-body-path="convenience.introBody"></div>\n'
        r'    <div data-content-body-fallback>\n'
        r'    <p data-i18n="convenience.intro"></p>\n'
        r'    </div>',
        text,
        count=1,
        flags=re.S,
    )
    text = ensure_script(text, prefix="../../")
    if text != original:
        path.write_text(text, encoding="utf-8", newline="\n")
        return True
    return False


CONV_BODY_BY_FOLDER = {
    "biyott": "convenience.biyottBody",
    "gongganchun": "convenience.gongganchunBody",
    "markjeongsik": "convenience.markjeongsikBody",
    "carbonara": "convenience.carbonaraBody",
    "eolbaksa": "convenience.eolbaksaBody",
    "jikgguri": "convenience.jikgguriBody",
    "melona": "convenience.melonaBody",
    "blue-lemonade-milkis": "convenience.blue-lemonade-milkisBody",
    "choco-banana-latte": "convenience.choco-banana-latteBody",
    "banana-americano": "convenience.banana-americanoBody",
    "banana-coffee": "convenience.c1Body",
    "kimbap-milk": "convenience.c2Body",
    "ramyeon-egg": "convenience.c3Body",
    "yakgwa-coffee": "convenience.c4Body",
    "chicken-beer": "convenience.c5Body",
    "melona-coffee": "convenience.c6Body",
}


def patch_convenience_detail(path: Path, folder: str) -> bool:
    body_path = CONV_BODY_BY_FOLDER.get(folder)
    if not body_path:
        return False
    text = path.read_text(encoding="utf-8")
    original = text
    # Capture from article-lead through tip div (or biyott what/why)
    m = re.search(
        r'(<h1[^>]*>.*?</h1>\s*)'
        r'((?:.|\n)*?)'
        r'(\s*</article>)',
        text,
        re.S,
    )
    if not m:
        return False
    head, middle, tail = m.group(1), m.group(2), m.group(3)
    if "data-content-body" in middle:
        text = ensure_script(text, prefix="../../../")
        if text != original:
            path.write_text(text, encoding="utf-8", newline="\n")
            return True
        return False
    # Keep middle as fallback
    new_middle = (
        f'\n      <div class="content-body" data-content-body data-body-path="{body_path}"></div>\n'
        f'      <div data-content-body-fallback>\n'
        f'{middle.rstrip()}\n'
        f'      </div>\n'
    )
    text = text[: m.start(1)] + head + new_middle + tail + text[m.end(3) :]
    text = ensure_script(text, prefix="../../../")
    if text != original:
        path.write_text(text, encoding="utf-8", newline="\n")
        return True
    return False


def patch_souvenir_detail(path: Path, slug: str) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    body_path = f"souvenir.{slug}Body"
    m = re.search(
        r'(<h1[^>]*>.*?</h1>\s*'
        r'<p class="article-lead"[^>]*>.*?</p>\s*)'
        r'((?:.|\n)*?)'
        r'(\s*</article>)',
        text,
        re.S,
    )
    if not m:
        return False
    head, middle, tail = m.group(1), m.group(2), m.group(3)
    if "data-content-body" in middle or "data-content-body" in head:
        text = ensure_script(text, prefix="../../../")
        if text != original:
            path.write_text(text, encoding="utf-8", newline="\n")
            return True
        return False
    # Keep lead in head; body1/body2/tip in fallback
    new_middle = (
        f'\n      <div class="content-body" data-content-body data-body-path="{body_path}"></div>\n'
        f'      <div data-content-body-fallback>\n'
        f'{middle.rstrip()}\n'
        f'      </div>\n'
    )
    text = text[: m.start()] + head + new_middle + tail + text[m.end() :]
    text = ensure_script(text, prefix="../../../")
    if text != original:
        path.write_text(text, encoding="utf-8", newline="\n")
        return True
    return False


def main() -> int:
    notes = content_body.migrate_all_section_bodies(force=False)
    print("=== i18n migrate ===")
    for n in notes:
        print(n)

    changed = []
    p = ROOT / "pages" / "before-trip" / "index.html"
    if patch_before_trip(p):
        changed.append(str(p.relative_to(ROOT)))
    p = ROOT / "pages" / "shopping" / "index.html"
    if patch_shopping(p):
        changed.append(str(p.relative_to(ROOT)))
    p = ROOT / "pages" / "convenience-store" / "index.html"
    if patch_convenience_index(p):
        changed.append(str(p.relative_to(ROOT)))

    conv_root = ROOT / "pages" / "convenience-store"
    for folder, _ in CONV_BODY_BY_FOLDER.items():
        page = conv_root / folder / "index.html"
        if page.is_file() and patch_convenience_detail(page, folder):
            changed.append(str(page.relative_to(ROOT)))

    souv_root = ROOT / "pages" / "souvenir"
    for slug in content_body.SOUVENIR_SLUGS:
        page = souv_root / slug / "index.html"
        if page.is_file() and patch_souvenir_detail(page, slug):
            changed.append(str(page.relative_to(ROOT)))

    print("=== HTML patched ===")
    for c in changed:
        print(c)
    print(f"Done. {len(changed)} HTML files updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
