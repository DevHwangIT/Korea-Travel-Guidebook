# -*- coding: utf-8 -*-
"""Rename nature→야외명소 (label only) and add mountain + beach place types."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def patch_html() -> None:
    p = ROOT / "pages" / "transportation" / "index.html"
    text = p.read_text(encoding="utf-8")
    text = text.replace(
        'data-i18n="transport.legendNature">자연</span>',
        'data-i18n="transport.legendNature">야외명소</span>',
    )
    if 'data-places-type-filter="mountain"' not in text:
        insert = """
            <li class="places-map-legend__item">
              <label class="places-map-legend__label">
                <input type="checkbox" class="places-map-legend__check" data-places-type-filter="mountain" checked>
                <span class="places-map-legend__swatch places-map-legend__swatch--mountain" aria-hidden="true"></span>
                <span data-i18n="transport.legendMountain">산</span>
              </label>
            </li>
            <li class="places-map-legend__item">
              <label class="places-map-legend__label">
                <input type="checkbox" class="places-map-legend__check" data-places-type-filter="beach" checked>
                <span class="places-map-legend__swatch places-map-legend__swatch--beach" aria-hidden="true"></span>
                <span data-i18n="transport.legendBeach">해수욕장</span>
              </label>
            </li>
"""
        # Insert mountain/beach before market (or after heritage if no market)
        if 'data-places-type-filter="market"' in text:
            text = text.replace(
                """            <li class="places-map-legend__item">
              <label class="places-map-legend__label">
                <input type="checkbox" class="places-map-legend__check" data-places-type-filter="market" checked>""",
                insert
                + """            <li class="places-map-legend__item">
              <label class="places-map-legend__label">
                <input type="checkbox" class="places-map-legend__check" data-places-type-filter="market" checked>""",
                1,
            )
        else:
            text = text.replace(
                """                <span data-i18n="transport.legendHeritage">문화재</span>
              </label>
            </li>
          </ul>""",
                """                <span data-i18n="transport.legendHeritage">문화재</span>
              </label>
            </li>"""
                + insert
                + """          </ul>""",
                1,
            )
    p.write_text(text, encoding="utf-8", newline="\n")
    print("patched index.html")


def patch_js() -> None:
    p = ROOT / "js" / "places-map.js"
    text = p.read_text(encoding="utf-8")

    def add_type_after(block: str, after_key: str, new_line: str) -> str:
        needle = f"    {after_key}: true,\n"
        if new_line.strip() in block:
            return block
        return block.replace(needle, needle + new_line, 1)

    # DEFAULT_TYPES
    if "mountain:" not in text.split("DEFAULT_TYPES")[1][:400]:
        text = text.replace(
            "  var DEFAULT_TYPES = {\n    city: true,\n    nature: true,\n    heritage: true,\n    market: true,",
            "  var DEFAULT_TYPES = {\n    city: true,\n    nature: true,\n    heritage: true,\n    mountain: true,\n    beach: true,\n    market: true,",
            1,
        )
    text = text.replace(
        'places: { types: ["city", "nature", "heritage", "market"], metro: false },',
        'places: { types: ["city", "nature", "heritage", "mountain", "beach", "market"], metro: false },',
    )
    # PLACE_TYPES
    text = text.replace(
        "  var PLACE_TYPES = {\n    city: true,\n    nature: true,\n    heritage: true,\n    market: true,",
        "  var PLACE_TYPES = {\n    city: true,\n    nature: true,\n    heritage: true,\n    mountain: true,\n    beach: true,\n    market: true,",
        1,
    )
    # BADGE_MARKER_KINDS
    text = text.replace(
        "  var BADGE_MARKER_KINDS = {\n    city: true,\n    nature: true,\n    heritage: true,\n    market: true,",
        "  var BADGE_MARKER_KINDS = {\n    city: true,\n    nature: true,\n    heritage: true,\n    mountain: true,\n    beach: true,\n    market: true,",
        1,
    )
    # glyphClass chain
    text = text.replace(
        """          : kind === "city" ||
              kind === "nature" ||
              kind === "heritage" ||
              kind === "market" ||
              kind === "locker" ||
              kind === "port"
            ? kind
            : null;""",
        """          : kind === "city" ||
              kind === "nature" ||
              kind === "heritage" ||
              kind === "mountain" ||
              kind === "beach" ||
              kind === "market" ||
              kind === "locker" ||
              kind === "port"
            ? kind
            : null;""",
        1,
    )
    # MARKER_GLYPHS — mountain distinct peaks + beach waves
    if "mountain:" not in text[text.find("MARKER_GLYPHS") : text.find("MARKER_GLYPHS") + 2500]:
        text = text.replace(
            """    // Twin mountain peaks
    nature:
      '<svg viewBox="0 0 24 24" width="16" height="16" focusable="false" aria-hidden="true">' +
      '<path fill="currentColor" d="M2 19L8.5 7.5 11.8 13l2.7-4.8L22 19H2z"/>' +
      "</svg>",
    // Pagoda: roof tiers + base pillar
    heritage:""",
            """    // Twin mountain peaks (outdoor / scenic nature)
    nature:
      '<svg viewBox="0 0 24 24" width="16" height="16" focusable="false" aria-hidden="true">' +
      '<path fill="currentColor" d="M2 19L8.5 7.5 11.8 13l2.7-4.8L22 19H2z"/>' +
      "</svg>",
    // Mountain summit / ridge
    mountain:
      '<svg viewBox="0 0 24 24" width="16" height="16" focusable="false" aria-hidden="true">' +
      '<path fill="currentColor" d="M12 3L2 20h6.5l3.5-6 3.5 6H22L12 3zm0 5.2L17.2 18h-2.1L12 12.8 8.9 18H6.8L12 8.2z"/>' +
      "</svg>",
    // Beach / waves
    beach:
      '<svg viewBox="0 0 24 24" width="16" height="16" focusable="false" aria-hidden="true">' +
      '<path fill="currentColor" d="M12 3a4 4 0 0 1 4 4c0 1.5-.8 2.8-2 3.5V13h2.5A3.5 3.5 0 0 1 20 16.5V19H4v-2.5A3.5 3.5 0 0 1 7.5 13H10V10.5C8.8 9.8 8 8.5 8 7a4 4 0 0 1 4-4zm-6.5 17c.9-.6 1.9-1 3-1s2.1.4 3 1c.9-.6 1.9-1 3-1s2.1.4 3 1c.9-.6 1.9-1 3-1v2c-1.1 0-2.1.4-3 1-.9-.6-1.9-1-3-1s-2.1.4-3 1c-.9-.6-1.9-1-3-1s-2.1.4-3 1c-.9-.6-1.9-1-3-1v-2c1.1 0 2.1.4 3 1z"/>' +
      "</svg>",
    // Pagoda: roof tiers + base pillar
    heritage:""",
            1,
        )
    p.write_text(text, encoding="utf-8", newline="\n")
    print("patched places-map.js")


def patch_css() -> None:
    p = ROOT / "styles.css"
    text = p.read_text(encoding="utf-8")
    if "swatch--mountain" not in text:
        text = text.replace(
            ".places-map-legend__swatch--heritage,\n.places-map-legend__swatch--market,",
            ".places-map-legend__swatch--heritage,\n.places-map-legend__swatch--mountain,\n.places-map-legend__swatch--beach,\n.places-map-legend__swatch--market,",
            1,
        )
        text = text.replace(
            """.places-map-legend__swatch--heritage {
  border-radius: 50%;
  background-color: #d44a3c;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23fff' d='M12 2.2L4 7.2v1.6h16V7.2L12 2.2zM5.5 10.2v1.5h13V10.2h-13zm2 3v1.5h9V13.2h-9zm2 3v1.4h5V16.2h-5zm1.2 2.8v2.5h-1.4V22h5.4v-1.5h-1.4v-2.5h-2.6z'/%3E%3C/svg%3E");
}

.places-map-legend__swatch--market {""",
            """.places-map-legend__swatch--heritage {
  border-radius: 50%;
  background-color: #d44a3c;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23fff' d='M12 2.2L4 7.2v1.6h16V7.2L12 2.2zM5.5 10.2v1.5h13V10.2h-13zm2 3v1.5h9V13.2h-9zm2 3v1.4h5V16.2h-5zm1.2 2.8v2.5h-1.4V22h5.4v-1.5h-1.4v-2.5h-2.6z'/%3E%3C/svg%3E");
}

.places-map-legend__swatch--mountain {
  border-radius: 50%;
  background-color: #5a8a4a;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23fff' d='M12 3L2 20h6.5l3.5-6 3.5 6H22L12 3z'/%3E%3C/svg%3E");
}

.places-map-legend__swatch--beach {
  border-radius: 50%;
  background-color: #3aa0c8;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23fff' d='M12 3a4 4 0 0 1 4 4c0 1.5-.8 2.8-2 3.5V13h2.5A3.5 3.5 0 0 1 20 16.5V19H4v-2.5A3.5 3.5 0 0 1 7.5 13H10V10.5C8.8 9.8 8 8.5 8 7a4 4 0 0 1 4-4z'/%3E%3C/svg%3E");
}

.places-map-legend__swatch--market {""",
            1,
        )
    if "marker__mountain" not in text:
        text = text.replace(
            ".places-map-marker__heritage,\n.places-map-marker__market,",
            ".places-map-marker__heritage,\n.places-map-marker__mountain,\n.places-map-marker__beach,\n.places-map-marker__market,",
            1,
        )
        text = text.replace(
            ".places-map-marker__heritage svg,\n.places-map-marker__market svg,",
            ".places-map-marker__heritage svg,\n.places-map-marker__mountain svg,\n.places-map-marker__beach svg,\n.places-map-marker__market svg,",
            1,
        )
        text = text.replace(
            """.places-map-marker__heritage {
  background: linear-gradient(145deg, #f0786a 0%, #d44a3c 100%);
  box-shadow: 0 2px 10px rgba(180, 60, 50, 0.5);
}

.places-map-marker__market {""",
            """.places-map-marker__heritage {
  background: linear-gradient(145deg, #f0786a 0%, #d44a3c 100%);
  box-shadow: 0 2px 10px rgba(180, 60, 50, 0.5);
}

.places-map-marker__mountain {
  background: linear-gradient(145deg, #7ab05e 0%, #5a8a4a 100%);
  box-shadow: 0 2px 10px rgba(60, 110, 50, 0.5);
}

.places-map-marker__beach {
  background: linear-gradient(145deg, #5ec4e8 0%, #3aa0c8 100%);
  box-shadow: 0 2px 10px rgba(30, 120, 160, 0.5);
}

.places-map-marker__market {""",
            1,
        )
        text = text.replace(
            """.places-map-marker--heritage .places-map-marker__pulse {
  background: rgba(212, 74, 60, 0.4);
  top: 12px;
}

.places-map-marker--market .places-map-marker__pulse {""",
            """.places-map-marker--heritage .places-map-marker__pulse {
  background: rgba(212, 74, 60, 0.4);
  top: 12px;
}

.places-map-marker--mountain .places-map-marker__pulse {
  background: rgba(90, 138, 74, 0.4);
  top: 12px;
}

.places-map-marker--beach .places-map-marker__pulse {
  background: rgba(58, 160, 200, 0.4);
  top: 12px;
}

.places-map-marker--market .places-map-marker__pulse {""",
            1,
        )
        text = text.replace(
            """.places-map-marker--heritage.is-active .places-map-marker__heritage,
.places-map-marker--heritage.is-hover .places-map-marker__heritage,
.places-map-marker--market.is-active .places-map-marker__market,
.places-map-marker--market.is-hover .places-map-marker__market,""",
            """.places-map-marker--heritage.is-active .places-map-marker__heritage,
.places-map-marker--heritage.is-hover .places-map-marker__heritage,
.places-map-marker--mountain.is-active .places-map-marker__mountain,
.places-map-marker--mountain.is-hover .places-map-marker__mountain,
.places-map-marker--beach.is-active .places-map-marker__beach,
.places-map-marker--beach.is-hover .places-map-marker__beach,
.places-map-marker--market.is-active .places-map-marker__market,
.places-map-marker--market.is-hover .places-map-marker__market,""",
            1,
        )
        text = text.replace(
            """.places-map-drawer__swatch--heritage {
  border-radius: 50%;
  background: #d44a3c;
}

.places-map-drawer__swatch--market {""",
            """.places-map-drawer__swatch--heritage {
  border-radius: 50%;
  background: #d44a3c;
}

.places-map-drawer__swatch--mountain {
  border-radius: 50%;
  background: #5a8a4a;
}

.places-map-drawer__swatch--beach {
  border-radius: 50%;
  background: #3aa0c8;
}

.places-map-drawer__swatch--market {""",
            1,
        )
    p.write_text(text, encoding="utf-8", newline="\n")
    print("patched styles.css")


def patch_coords_comment() -> None:
    p = ROOT / "data" / "places" / "places-coords.js"
    text = p.read_text(encoding="utf-8")
    if '"mountain"' not in text[:800]:
        text = text.replace(
            ' * type: "city" | "nature" | "heritage" | "airport" | "info" | "locker" | "port" | "bus-terminal" | "market"',
            ' * type: "city" | "nature" | "heritage" | "mountain" | "beach" | "airport" | "info" | "locker" | "port" | "bus-terminal" | "market"',
        )
        text = text.replace(
            " *   nature   — mountains, beaches, parks, scenic outdoors",
            " *   nature   — outdoor scenic spots / parks / coasts (야외명소)\n"
            " *   mountain — mountains / hiking peaks\n"
            " *   beach    — swimming beaches / seaside resorts",
        )
        text = text.replace(
            " *   market     — traditional markets / night markets / fish markets",
            " *   market   — traditional markets / night markets / fish markets",
        )
    p.write_text(text, encoding="utf-8", newline="\n")
    print("patched places-coords.js header")


def patch_i18n() -> None:
    sys.path.insert(0, str(ROOT / "tool"))
    from lib import i18n_store  # noqa: WPS433

    keys = {
        "legendNature": {
            "ko": "야외명소",
            "en": "Outdoor",
            "ja": "屋外名所",
            "zh": "户外景点",
            "zh-Hant": "戶外景點",
            "vi": "Ngoài trời",
            "th": "สถานที่กลางแจ้ง",
            "ru": "На природе",
        },
        "legendMountain": {
            "ko": "산",
            "en": "Mountain",
            "ja": "山",
            "zh": "山",
            "zh-Hant": "山",
            "vi": "Núi",
            "th": "ภูเขา",
            "ru": "Горы",
        },
        "legendBeach": {
            "ko": "해수욕장",
            "en": "Beach",
            "ja": "海水浴場",
            "zh": "海水浴场",
            "zh-Hant": "海水浴場",
            "vi": "Bãi biển",
            "th": "ชายหาด",
            "ru": "Пляж",
        },
    }
    bundle = i18n_store.load_all()
    for lang in i18n_store.LANGS:
        tr = bundle[lang].setdefault("transport", {})
        for key, locales in keys.items():
            tr[key] = locales.get(lang) or locales["en"]
    i18n_store.save_all(bundle)
    print(i18n_store.build_bundle())


def main() -> int:
    patch_html()
    patch_js()
    patch_css()
    patch_coords_comment()
    patch_i18n()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
