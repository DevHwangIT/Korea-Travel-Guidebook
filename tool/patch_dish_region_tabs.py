# -*- coding: utf-8 -*-
"""Patch all meal/dessert dish index pages with region filter tabs + data-region-group."""
from __future__ import annotations

import re
import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from lib import i18n_store  # noqa: E402
from lib.cache_bust import read_version  # noqa: E402
from lib.paths import DESSERTS_DIR, MEALS_DIR  # noqa: E402
from lib.region_groups import region_group_from_restaurant  # noqa: E402
from lib.scaffold import dish_region_tabs_html  # noqa: E402

CARD_RE = re.compile(
    r'(<article\s+class="card")([^>]*>)(\s*<a\s+href="\./([^"/]+)/)',
    re.IGNORECASE,
)
SCRIPT_MARKER = "js/dish-region-filter.js"
TABS_MARKER = "data-dish-region-filter"


def ensure_script(html: str, version: str) -> str:
    if SCRIPT_MARKER in html:
        return html
    tag = (
        f'  <script src="../../../../js/dish-region-filter.js?v={version}"></script>\n'
    )
    # Insert before analytics if present, else before </body>
    if "js/analytics.js" in html:
        return html.replace(
            '  <script src="../../../../js/analytics.js',
            tag + '  <script src="../../../../js/analytics.js',
            1,
        )
    return re.sub(
        r"</body>",
        tag + "</body>",
        html,
        count=1,
        flags=re.IGNORECASE,
    )


def ensure_tabs(html: str) -> str:
    if TABS_MARKER in html:
        return html
    tabs = dish_region_tabs_html()
    # After intro section, before Places h2 — prefer insert after Places h2
    m = re.search(
        r'(<h2[^>]*data-i18n="common\.places"[^>]*>.*?</h2>\s*)',
        html,
        re.IGNORECASE | re.DOTALL,
    )
    if m:
        return html[: m.end(1)] + tabs + html[m.end(1) :]
    # Fallback: before card-grid or emptyPlaces
    m2 = re.search(
        r'(<p class="tabs-help"[^>]*>.*?</p>\s*)',
        html,
        re.IGNORECASE | re.DOTALL,
    )
    if m2:
        return html[: m2.start(1)] + tabs + html[m2.start(1) :]
    m3 = re.search(r'<div class="card-grid">', html, re.IGNORECASE)
    if m3:
        return html[: m3.start()] + tabs + html[m3.start() :]
    return html


def patch_cards(html: str, restaurants: dict) -> tuple[str, int]:
    updated = 0

    def repl(m: re.Match[str]) -> str:
        nonlocal updated
        open_tag, rest, _link, slug = m.group(1), m.group(2), m.group(3), m.group(4)
        # already has data-region-group?
        full_open = open_tag + rest
        if "data-region-group=" in full_open:
            return m.group(0)
        entry = restaurants.get(slug)
        group = region_group_from_restaurant(entry if isinstance(entry, dict) else None)
        updated += 1
        return f'{open_tag} data-region-group="{group}"{rest}{m.group(3)}'

    return CARD_RE.sub(repl, html), updated


def patch_file(path: Path, restaurants: dict, version: str) -> list[str]:
    notes: list[str] = []
    html = path.read_text(encoding="utf-8")
    head = html[:4000].lower()
    if 'http-equiv="refresh"' in head or "location.replace(" in head:
        # Redirect stub — strip accidental filter script if present
        if SCRIPT_MARKER in html:
            html2 = re.sub(
                r'\s*<script src="[^"]*dish-region-filter\.js[^"]*"></script>\s*',
                "\n",
                html,
                flags=re.IGNORECASE,
            )
            if html2 != html:
                path.write_text(html2, encoding="utf-8", newline="\n")
                notes.append("stripped-script-from-redirect")
        return notes
    orig = html
    html = ensure_tabs(html)
    html, n = patch_cards(html, restaurants)
    if n:
        notes.append(f"cards+{n}")
    html = ensure_script(html, version)
    if html != orig:
        path.write_text(html, encoding="utf-8", newline="\n")
        notes.append("written")
    return notes


def main() -> None:
    ko = i18n_store.load_lang("ko")
    restaurants = ko.get("restaurants") or {}
    if not isinstance(restaurants, dict):
        restaurants = {}
    try:
        version = read_version()
    except SystemExit:
        version = "0"

    patched = 0
    for base in (MEALS_DIR, DESSERTS_DIR):
        if not base.is_dir():
            continue
        for dish_dir in sorted(base.iterdir()):
            if not dish_dir.is_dir():
                continue
            index = dish_dir / "index.html"
            if not index.is_file():
                continue
            notes = patch_file(index, restaurants, version)
            if notes:
                patched += 1
                print(f"{dish_dir.parent.name}/{dish_dir.name}: {', '.join(notes)}")
    print(f"Done. Touched {patched} dish pages.")


if __name__ == "__main__":
    main()
