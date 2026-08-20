# -*- coding: utf-8 -*-
"""Add convenience brand filter tabs + data-brand on combo cards."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from lib import i18n_store  # noqa: E402
from lib.cache_bust import read_version  # noqa: E402

# Brand tags: common = sold across chains; others = exclusive / PB-famous.
# Combos that only need widely available SKUs stay "common".
PRODUCT_BRANDS: dict[str, str] = {
    # Popular products
    "biyott": "common",
    "store-kimbap": "common",
    "banana-milk": "common",
    "yonsei-cream-bread": "cu",  # CU signature cream bread
    "buldak-bokkeum-myeon": "common",
    "ice-cup-ade": "gs",  # GS25 ice-cup drinks
    # Combos / recipes
    "gongganchun": "common",
    "markjeongsik": "common",
    "carbonara": "common",
    "eolbaksa": "common",
    "jikgguri": "common",
    "melona": "common",
    "blue-lemonade-milkis": "common",
    "choco-banana-latte": "common",
    "banana-americano": "common",
    "banana-coffee": "common",
    "kimbap-milk": "common",
    "melona-coffee": "common",
    "yakgwa-coffee": "common",
    "chicken-beer": "common",
    "ramyeon-egg": "common",
}

BRAND_LABEL_KEYS = {
    "common": "convenience.brandTabCommon",
    "cu": "convenience.brandTabCu",
    "gs": "convenience.brandTabGs",
    "seven": "convenience.brandTabSeven",
    "emart24": "convenience.brandTabEmart24",
}

BRAND_FALLBACKS = {
    "common": "공통",
    "cu": "CU",
    "gs": "GS25",
    "seven": "세븐일레븐",
    "emart24": "이마트24",
}

I18N_KEYS = {
    "ko": {
        "brandTabCommon": "공통",
        "brandTabCu": "CU",
        "brandTabGs": "GS25",
        "brandTabSeven": "세븐일레븐",
        "brandTabEmart24": "이마트24",
        "brandFilterEmpty": "이 브랜드에 해당하는 항목이 없습니다.",
        "brandTabsHelp": "공통은 여러 편의점에서 살 수 있는 제품·조합입니다. 브랜드 탭은 공통 + 해당 브랜드 상품을 보여 줍니다.",
    },
    "en": {
        "brandTabCommon": "Common",
        "brandTabCu": "CU",
        "brandTabGs": "GS25",
        "brandTabSeven": "7-Eleven",
        "brandTabEmart24": "Emart24",
        "brandFilterEmpty": "No items for this brand.",
        "brandTabsHelp": "Common = sold at most chains. Brand tabs show common items plus that chain’s exclusives.",
    },
    "ja": {
        "brandTabCommon": "共通",
        "brandTabCu": "CU",
        "brandTabGs": "GS25",
        "brandTabSeven": "セブンイレブン",
        "brandTabEmart24": "イーマート24",
        "brandFilterEmpty": "このブランドの項目はありません。",
        "brandTabsHelp": "共通は多くのコンビニで買える商品・組み合わせです。ブランドタブは共通＋その店舗限定を表示します。",
    },
    "zh": {
        "brandTabCommon": "共通",
        "brandTabCu": "CU",
        "brandTabGs": "GS25",
        "brandTabSeven": "7-Eleven",
        "brandTabEmart24": "Emart24",
        "brandFilterEmpty": "该品牌暂无项目。",
        "brandTabsHelp": "共通为多数便利店都有的商品/组合。品牌页签显示共通＋该品牌专属。",
    },
    "zh-Hant": {
        "brandTabCommon": "共通",
        "brandTabCu": "CU",
        "brandTabGs": "GS25",
        "brandTabSeven": "7-Eleven",
        "brandTabEmart24": "Emart24",
        "brandFilterEmpty": "此品牌尚無項目。",
        "brandTabsHelp": "共通是多數超商都買得到的商品／組合。品牌分頁會顯示共通＋該品牌專屬。",
    },
    "vi": {
        "brandTabCommon": "Chung",
        "brandTabCu": "CU",
        "brandTabGs": "GS25",
        "brandTabSeven": "7-Eleven",
        "brandTabEmart24": "Emart24",
        "brandFilterEmpty": "Không có mục cho thương hiệu này.",
        "brandTabsHelp": "Chung = bán ở hầu hết chuỗi. Tab thương hiệu gồm mục chung + độc quyền của chuỗi đó.",
    },
    "th": {
        "brandTabCommon": "ทั่วไป",
        "brandTabCu": "CU",
        "brandTabGs": "GS25",
        "brandTabSeven": "7-Eleven",
        "brandTabEmart24": "Emart24",
        "brandFilterEmpty": "ไม่มีรายการสำหรับแบรนด์นี้",
        "brandTabsHelp": "ทั่วไป = มีในหลายร้านสะดวกซื้อ แท็บแบรนด์แสดงรายการทั่วไป + ของเฉพาะแบรนด์นั้น",
    },
    "ru": {
        "brandTabCommon": "Общие",
        "brandTabCu": "CU",
        "brandTabGs": "GS25",
        "brandTabSeven": "7-Eleven",
        "brandTabEmart24": "Emart24",
        "brandFilterEmpty": "Нет позиций для этого бренда.",
        "brandTabsHelp": "Общие — товары/комбо в большинстве сетей. Вкладка бренда: общие + эксклюзивы сети.",
    },
}


def write_brand_data() -> Path:
    out = ROOT / "data" / "convenience" / "product-brands.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(PRODUCT_BRANDS, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return out


def update_i18n() -> None:
    bundle = i18n_store.load_all()
    for lang, keys in I18N_KEYS.items():
        conv = bundle[lang].setdefault("convenience", {})
        for k, v in keys.items():
            conv[k] = v
    i18n_store.save_all(bundle)
    print(i18n_store.build_bundle())


def brand_tabs_html(brands_present: list[str]) -> str:
    # Always common first; then exclusives found on page
    order = ["common"] + [b for b in ("cu", "gs", "seven", "emart24") if b in brands_present]
    buttons = []
    for i, b in enumerate(order):
        active = " is-active" if i == 0 else ""
        sel = "true" if i == 0 else "false"
        key = BRAND_LABEL_KEYS[b]
        fb = BRAND_FALLBACKS[b]
        buttons.append(
            f'        <button type="button" class="tab-btn tab-btn-sm{active}" role="tab" '
            f'data-brand-tab="{b}" aria-selected="{sel}" data-i18n="{key}">{fb}</button>'
        )
    return (
        '    <div class="brand-filter">\n'
        '      <p class="tabs-help" data-i18n="convenience.brandTabsHelp"></p>\n'
        '      <div class="tab-list tab-list-sm" role="tablist" aria-label="Store brand">\n'
        + "\n".join(buttons)
        + "\n      </div>\n"
        "    </div>\n"
    )


def patch_index(html: str, version: str) -> str:
    def tag_one(m: re.Match[str]) -> str:
        attrs = m.group(1) or ""
        href = m.group(2)
        slug = m.group(3)
        if re.search(r"\bdata-brand\s*=", attrs):
            return m.group(0)
        brand = PRODUCT_BRANDS.get(slug, "common")
        return f'<a class="combo-card" data-brand="{brand}"{attrs} href="{href}">'

    html = re.sub(
        r'<a class="combo-card"([^>]*)\shref="(\./([^"/]+)/index\.html)">',
        tag_one,
        html,
    )

    exclusives = sorted(
        {
            b
            for b in re.findall(r'data-brand="([^"]+)"', html)
            if b and b != "common"
        }
    )

    # Put filter attrs on list-pager scope so querySelector finds all combo-cards
    if "data-convenience-brand-filter" not in html:
        html = re.sub(
            r'(<div\s+data-list-pager)([^>]*>)',
            r'\1 data-convenience-brand-filter data-brand-active="common" data-brand-item="a.combo-card"\2',
            html,
            count=1,
            flags=re.IGNORECASE,
        )
        tabs = brand_tabs_html(exclusives)
        m = re.search(r'(<div[^>]*data-list-pager[^>]*>\s*)', html, re.IGNORECASE)
        if m:
            html = html[: m.end(1)] + tabs + html[m.end(1) :]
        else:
            m2 = re.search(r'(<h2 class="section-heading"[^>]*>)', html)
            if m2:
                html = html[: m2.start(1)] + tabs + html[m2.start(1) :]

    if "js/convenience-brand-filter.js" not in html:
        tag = f'  <script src="../../js/convenience-brand-filter.js?v={version}"></script>\n'
        html2 = re.sub(
            r'(<script src="\.\./\.\./js/list-pager\.js\?v=[^"]+"></script>\s*)',
            r"\1" + tag,
            html,
            count=1,
        )
        if html2 != html:
            html = html2
        else:
            html = re.sub(r"</body>", tag + "</body>", html, count=1, flags=re.IGNORECASE)

    return html


def main() -> None:
    write_brand_data()
    update_i18n()
    try:
        version = read_version()
    except SystemExit:
        version = "0"
    path = ROOT / "pages" / "convenience-store" / "index.html"
    html = path.read_text(encoding="utf-8")
    new_html = patch_index(html, version)
    path.write_text(new_html, encoding="utf-8", newline="\n")
    print(f"Updated {path}")


if __name__ == "__main__":
    main()
