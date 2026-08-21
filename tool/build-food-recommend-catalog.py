# -*- coding: utf-8 -*-
"""Scan meal/dessert hubs + convenience products → data/food/recommend-catalog.js

Usage:
  python tool/build-food-recommend-catalog.py

After adding pages/foods/meals/{slug}/ or pages/foods/desserts/{slug}/,
re-run this script (CMS create_dish also calls it). Tune tags in
data/food/recommend-tags.json when heuristics are wrong.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from lib.paths import DESSERTS_DIR, MEALS_DIR, ROOT  # noqa: E402

CONV_DIR = ROOT / "pages" / "convenience-store"
TAGS_PATH = ROOT / "data" / "food" / "recommend-tags.json"
OUT_PATH = ROOT / "data" / "food" / "recommend-catalog.js"

TITLE_RE = re.compile(
    r'data-i18n-title\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE
)

REDIRECT_MARKERS = (
    'http-equiv="refresh"',
    "http-equiv='refresh'",
    "location.replace(",
)


def _is_redirect_page(html_path: Path) -> bool:
    try:
        head = html_path.read_text(encoding="utf-8", errors="ignore")[:4000].lower()
    except OSError:
        return False
    return any(m.lower() in head for m in REDIRECT_MARKERS)

# (slug substring regex, tags) — applied in order; union of matches.
MEAL_HEURISTICS: list[tuple[re.Pattern[str], list[str]]] = [
    (re.compile(r"malatang|tteokbokki|dakgalbi|jjimdak|yangnyeom|budae|sundubu|gamjatang|dakbokkeum|jeyuk|jjolmyeon|nakgopsae"), ["spicy"]),
    (re.compile(r"gukbap|gomtang|samgyetang|kalguksu|sundubu|malatang|dakhanmari|budae|kongguksu|naengmyeon|gamjatang|dakbokkeum"), ["soup"]),
    (re.compile(r"samgyeopsal|gopchang|tangsuyuk|korean-chinese|bulgogi|bossam|tteokgalbi|jeyuk|galbijjim|jokbal"), ["meat", "nosoup"]),
    (re.compile(r"jogae-gui"), ["seafood", "grill", "warm", "nosoup"]),
    (re.compile(r"korean-pasta"), ["noodles", "mild", "nosoup", "warm"]),
    (re.compile(r"dak|chicken|samgyetang|dakgangjeong"), ["chicken"]),
    (re.compile(r"dakgangjeong|yangnyeom-chicken"), ["spicy", "nosoup", "quickbite"]),
    (re.compile(r"doenjang"), ["soup", "warm", "mild"]),
    (re.compile(r"kimbap|bibimbap|jeon|kongguksu|naengmyeon|ganjang|makguksu"), ["light"]),
    (re.compile(r"kimbap"), ["portable", "roll", "quickbite", "nosoup"]),
    (re.compile(r"naengmyeon|kongguksu|makguksu|jjolmyeon|milmyeon"), ["cold"]),
    (re.compile(r"gukbap|gomtang|samgyetang|dakhanmari|kalguksu|sundubu|budae|gamjatang|dakbokkeum"), ["warm"]),
    (re.compile(r"bibimbap|jeon"), ["veggie", "mild", "nosoup"]),
    (re.compile(r"jajang|tangsuyuk|korean-chinese|bulgogi|bossam|tteokgalbi|galbijjim"), ["mild", "nosoup"]),
    (re.compile(r"kalguksu|kongguksu|naengmyeon|jajang|korean-chinese|makguksu|jjolmyeon|milmyeon"), ["noodles"]),
    (re.compile(r"samgyeopsal|gopchang|bulgogi|tteokgalbi"), ["grill", "warm"]),
    (re.compile(r"ganjang|gejang|nakgopsae"), ["seafood", "nosoup"]),
    (re.compile(r"tteokbokki"), ["street", "quickbite"]),
]

DESSERT_HEURISTICS: list[tuple[re.Pattern[str], list[str]]] = [
    (re.compile(r"bingsu|yogurt|ice"), ["icy", "cold"]),
    (re.compile(r"bread|butter|sandwich|cookie|bungeoppang|yakgwa"), ["bakery"]),
    (re.compile(r"cafe"), ["coffee"]),
    (re.compile(r"tanghulu|bungeoppang|dalgona|hotteok|eomuk"), ["street"]),
    (re.compile(r"bungeoppang|hotteok|eomuk"), ["warm"]),
    (re.compile(r"tteok|sipwon"), ["bakery", "sweet"]),
]

QUICK_HEURISTICS: list[tuple[re.Pattern[str], list[str]]] = [
    (re.compile(r"ramyeon|gongganchun|markjeongsik|carbonara|jikgguri"), ["noodles", "quickbite"]),
    (re.compile(r"kimbap"), ["roll", "portable", "quickbite"]),
    (re.compile(r"chicken"), ["chicken", "quickbite"]),
    (re.compile(r"coffee|americano|latte|yakgwa|melona|eolbaksa|lemonade|milkis"), ["drink", "combo"]),
    (re.compile(r"melona|biyott|ice-cup|ade"), ["sweet", "cold"]),
    (re.compile(r"gongganchun|markjeongsik|ramyeon|jikgguri"), ["combo"]),
]


def _load_overrides() -> dict:
    if not TAGS_PATH.is_file():
        return {}
    data = json.loads(TAGS_PATH.read_text(encoding="utf-8"))
    items = data.get("items") or {}
    return items if isinstance(items, dict) else {}


def _read_title_key(html_path: Path) -> str | None:
    try:
        text = html_path.read_text(encoding="utf-8")
    except OSError:
        return None
    m = TITLE_RE.search(text)
    return m.group(1) if m else None


def _heuristic_tags(slug: str, rules: list[tuple[re.Pattern[str], list[str]]]) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for pat, tags in rules:
        if pat.search(slug):
            for t in tags:
                if t not in seen:
                    seen.add(t)
                    found.append(t)
    return found


def _dedupe_tags(tags: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for t in tags:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def _merge_tags(base: list[str], override: dict | None) -> list[str]:
    if not override:
        return _dedupe_tags(list(base))
    if "tags" in override and isinstance(override["tags"], list):
        tags = [str(t) for t in override["tags"]]
    else:
        tags = list(base)
    extra = override.get("extraTags")
    if isinstance(extra, list):
        for t in extra:
            ts = str(t)
            if ts not in tags:
                tags.append(ts)
    return _dedupe_tags(tags)


def _convenience_sections() -> dict[str, str]:
    """Map slug → product|combo from pages/convenience-store/index.html cards."""
    index = CONV_DIR / "index.html"
    if not index.is_file():
        return {}
    try:
        text = index.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return {}
    out: dict[str, str] = {}
    for m in re.finditer(
        r'data-section\s*=\s*["\'](product|combo)["\'][^>]*href\s*=\s*["\']\./([^/"\']+)/',
        text,
        re.IGNORECASE,
    ):
        out[m.group(2)] = m.group(1).lower()
    for m in re.finditer(
        r'href\s*=\s*["\']\./([^/"\']+)/[^"\']*["\'][^>]*data-section\s*=\s*["\'](product|combo)["\']',
        text,
        re.IGNORECASE,
    ):
        out[m.group(1)] = m.group(2).lower()
    return out


def _category_entries(
    kind: str,
    root: Path,
    href_prefix: str,
    default_title_prefix: str,
    heuristics: list[tuple[re.Pattern[str], list[str]]],
    base_tags: list[str],
    overrides: dict,
    section_map: dict[str, str] | None = None,
) -> list[dict]:
    out: list[dict] = []
    if not root.is_dir():
        return out
    for child in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        if not child.is_dir():
            continue
        index = child / "index.html"
        if not index.is_file():
            continue
        slug = child.name
        ov = overrides.get(slug) if isinstance(overrides.get(slug), dict) else None
        if ov and ov.get("exclude"):
            continue
        # Skip obsolete redirect stubs (e.g. gomtang → gukbap) even without tags exclude.
        if _is_redirect_page(index):
            continue
        item_base = list(base_tags)
        if section_map is not None:
            section = section_map.get(slug, "combo")
            if section == "product":
                item_base = ["quickbite"]
            else:
                item_base = ["quickbite", "combo"]
        tags = _merge_tags(item_base + _heuristic_tags(slug, heuristics), ov)
        title_key = None
        if ov and ov.get("titleKey"):
            title_key = str(ov["titleKey"])
        else:
            title_key = _read_title_key(index) or f"{default_title_prefix}.{slug}.title"
        entry: dict = {
            "id": slug,
            "href": f"{href_prefix}/{slug}/index.html",
            "kind": kind,
            "tags": tags,
            "titleKey": title_key,
        }
        if ov and ov.get("reasonKey"):
            entry["reasonKey"] = str(ov["reasonKey"])
        out.append(entry)
    return out


def build_catalog() -> list[dict]:
    overrides = _load_overrides()
    catalog: list[dict] = []

    catalog.extend(
        _category_entries(
            "meal",
            MEALS_DIR,
            "../foods/meals",
            "dishes",
            MEAL_HEURISTICS,
            ["hearty"],
            overrides,
        )
    )
    catalog.extend(
        _category_entries(
            "dessert",
            DESSERTS_DIR,
            "../foods/desserts",
            "dishes",
            DESSERT_HEURISTICS,
            ["sweet"],
            overrides,
        )
    )

    # Convenience hub (always)
    hub_ov = overrides.get("convenience") if isinstance(overrides.get("convenience"), dict) else {}
    if not hub_ov.get("exclude"):
        hub_tags = _merge_tags(["combo", "quickbite", "portable"], hub_ov)
        hub: dict = {
            "id": "convenience",
            "href": "../convenience-store/index.html",
            "kind": "quick",
            "tags": hub_tags,
            "titleKey": str(hub_ov.get("titleKey") or "home.menuConvenience"),
        }
        if hub_ov.get("reasonKey"):
            hub["reasonKey"] = str(hub_ov["reasonKey"])
        catalog.append(hub)

    catalog.extend(
        _category_entries(
            "quick",
            CONV_DIR,
            "../convenience-store",
            "convenience",
            QUICK_HEURISTICS,
            ["quickbite", "combo"],
            overrides,
            section_map=_convenience_sections(),
        )
    )
    return catalog


def write_catalog(catalog: list[dict]) -> Path:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = (
        "/** Auto-generated by tool/build-food-recommend-catalog.py — do not edit by hand. */\n"
        "window.FOOD_RECOMMEND_CATALOG = "
        + json.dumps(catalog, ensure_ascii=False, indent=2)
        + ";\n"
    )
    OUT_PATH.write_text(payload, encoding="utf-8", newline="\n")
    return OUT_PATH


def main() -> int:
    catalog = build_catalog()
    path = write_catalog(catalog)
    by_kind: dict[str, int] = {}
    for item in catalog:
        k = str(item.get("kind") or "?")
        by_kind[k] = by_kind.get(k, 0) + 1
    summary = ", ".join(f"{k}={n}" for k, n in sorted(by_kind.items()))
    print(f"Wrote {path.relative_to(ROOT).as_posix()} ({len(catalog)} items: {summary})")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
