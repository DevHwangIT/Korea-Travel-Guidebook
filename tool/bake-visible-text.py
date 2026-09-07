# -*- coding: utf-8 -*-
"""Fill empty data-i18n / content-body mounts with Korean so crawlers see text."""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from lib.i18n_store import load_lang  # noqa: E402

SKIP_DIR_NAMES = {
    "node_modules",
    ".git",
    "tool",
    "i18n",
    "Images",
    "images",
    "media",
    "components",
    "templates",
}

I18N_TAG = re.compile(
    r"<(?P<tag>p|span|h1|h2|h3|h4|dd|dt|li|strong|em|a|button|label|figcaption|title)"
    r"(?P<attrs>[^>]*?\sdata-i18n=\"(?P<key>[^\"]+)\"[^>]*)>"
    r"(?P<body>.*?)"
    r"</(?P=tag)>",
    re.I | re.S,
)
BODY_MOUNT = re.compile(
    r"<div(?P<attrs>[^>]*data-content-body[^>]*)>(?P<body>.*?)</div>",
    re.I | re.S,
)
TITLE_TAG = re.compile(r"<title>(.*?)</title>", re.I | re.S)
HTML_TITLE_KEY = re.compile(r'data-i18n-title="([^"]+)"', re.I)
SHOP_ABOUT_ROW = re.compile(
    r'(<div class="shop-info__row[^"]*about[^"]*"[^>]*data-shop-info-row="about")(\s+hidden)?',
    re.I,
)
ADS_META = (
    '<meta name="google-adsense-account" content="ca-pub-7139367317436403">'
)
ADS_SCRIPT = (
    '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'
    '?client=ca-pub-7139367317436403" crossorigin="anonymous"></script>'
)


def ensure_ads_head(html_text: str, rel_posix: str) -> tuple[str, bool]:
    """Publisher meta + adsbygoogle.js in <head> so crawlers see them without JS."""
    changed = False
    is_privacy = "/privacy" in ("/" + rel_posix.lower())
    is_shop = "data-shop-detail" in html_text
    if "google-adsense-account" not in html_text:
        inserted = False

        def after_viewport(match: re.Match) -> str:
            nonlocal inserted
            inserted = True
            return match.group(0) + "\n  " + ADS_META

        next_text = re.sub(
            r"<meta[^>]+name=\"viewport\"[^>]*>",
            after_viewport,
            html_text,
            count=1,
            flags=re.I,
        )
        if inserted:
            html_text = next_text
            changed = True
        else:
            html_text = html_text.replace("<head>", "<head>\n  " + ADS_META, 1)
            changed = True
    if is_privacy or is_shop:
        html_text2, n = re.subn(
            r"\s*<script[^>]+pagead2\.googlesyndication\.com/pagead/js/adsbygoogle\.js[^>]*>\s*</script>",
            "",
            html_text,
            count=1,
            flags=re.I,
        )
        if n:
            html_text = html_text2
            changed = True
        return html_text, changed
    if "pagead2.googlesyndication.com/pagead/js/adsbygoogle.js" not in html_text:
        html_text2, n = re.subn(
            r"<meta[^>]+name=\"google-adsense-account\"[^>]*>",
            lambda m: m.group(0) + "\n  " + ADS_SCRIPT,
            html_text,
            count=1,
            flags=re.I,
        )
        if n:
            html_text = html_text2
            changed = True
    return html_text, changed


def lookup(root: dict, dotted: str):
    cur = root
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def is_placeholder(text: str, key: str) -> bool:
    raw = re.sub(r"<[^>]+>", "", text or "")
    raw = re.sub(r"\s+", " ", raw).strip()
    if not raw:
        return True
    leaf = key.split(".")[-1]
    if raw.lower() == leaf.lower():
        return True
    if re.fullmatch(r"[a-z0-9._-]{2,40}", raw, re.I) and raw.isascii():
        return True
    return False


def text_from_block(block: dict) -> str:
    if not isinstance(block, dict):
        return ""
    kind = block.get("type") or ""
    if kind not in ("text", "callout", "checklist"):
        return ""
    value = block.get("ko") or block.get("en") or ""
    return str(value).strip()


def render_body_html(blocks) -> str:
    if not isinstance(blocks, list):
        return ""
    parts = []
    for block in blocks:
        text = text_from_block(block)
        if not text:
            continue
        paras = [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]
        if not paras:
            continue
        kind = (block.get("type") or "text") if isinstance(block, dict) else "text"
        if kind == "callout":
            parts.append(
                '<aside class="guide-callout content-body__callout" data-baked-body="1">'
                f'<p class="content-body__text">{html.escape(paras[0]).replace(chr(10), "<br>")}</p>'
                "</aside>"
            )
            continue
        if kind == "checklist" and isinstance(block, dict):
            items = block.get("items") or []
            lis = []
            for item in items:
                item_text = ""
                if isinstance(item, dict):
                    item_text = str(item.get("ko") or item.get("en") or "").strip()
                else:
                    item_text = str(item).strip()
                if item_text:
                    lis.append(f"<li>{html.escape(item_text)}</li>")
            if lis:
                title = html.escape(paras[0]) if paras else ""
                heading = f'<h2 class="content-body__heading">{title}</h2>' if title else ""
                parts.append(
                    f'<div class="content-body__checklist" data-baked-body="1">{heading}'
                    f'<ul class="prep-check-list">{"".join(lis)}</ul></div>'
                )
            continue
        for idx, para in enumerate(paras):
            esc = html.escape(para).replace("\n", "<br>")
            if idx == 0 and len(para) < 48 and "\n" not in para:
                parts.append(f'<h2 class="content-body__heading" data-baked-body="1">{esc}</h2>')
            else:
                parts.append(
                    f'<p class="content-body__text" data-baked-body="1">{esc}</p>'
                )
    return "\n        ".join(parts)


def bake_file(path: Path, ko: dict) -> bool:
    original = path.read_text(encoding="utf-8")
    html_text = original
    changed = False

    def repl_i18n(match: re.Match) -> str:
        nonlocal changed
        key = match.group("key")
        body = match.group("body")
        value = lookup(ko, key)
        if not isinstance(value, str) or not value.strip():
            return match.group(0)
        if not is_placeholder(body, key):
            return match.group(0)
        changed = True
        return (
            f"<{match.group('tag')}{match.group('attrs')}>"
            f"{html.escape(value.strip())}"
            f"</{match.group('tag')}>"
        )

    html_text = I18N_TAG.sub(repl_i18n, html_text)

    title_key_m = HTML_TITLE_KEY.search(html_text)
    if title_key_m:
        title_val = lookup(ko, title_key_m.group(1))
        if isinstance(title_val, str) and title_val.strip():
            def repl_title(match: re.Match) -> str:
                nonlocal changed
                current = re.sub(r"\s+", " ", match.group(1)).strip()
                if current and "Korea Travel Guide" in current and not re.search(
                    r"^[a-z0-9._-]+(\s\|)", current, re.I
                ):
                    if not is_placeholder(current.split("|")[0].strip(), title_key_m.group(1)):
                        return match.group(0)
                pretty = title_val.strip()
                if "Korea Travel Guide" not in pretty:
                    pretty = pretty + " | Korea Travel Guide"
                if current == pretty:
                    return match.group(0)
                changed = True
                return f"<title>{html.escape(pretty)}</title>"

            html_text = TITLE_TAG.sub(repl_title, html_text, count=1)

    def repl_body(match: re.Match) -> str:
        nonlocal changed
        attrs = match.group("attrs")
        inner = match.group("body")
        if "data-baked-body" in inner or len(re.sub(r"\s+", "", inner)) > 40:
            return match.group(0)
        path_m = re.search(r'data-body-path="([^"]+)"', attrs)
        if not path_m:
            return match.group(0)
        blocks = lookup(ko, path_m.group(1))
        baked = render_body_html(blocks)
        if not baked:
            return match.group(0)
        changed = True
        return f"<div{attrs}>\n        {baked}\n      </div>"

    html_text = BODY_MOUNT.sub(repl_body, html_text)
    if "data-baked-body" in html_text and "data-content-body-fallback" in html_text:
        next_text = html_text.replace(
            "<div data-content-body-fallback>",
            "<div hidden data-content-body-fallback>",
        )
        next_text = next_text.replace(
            "<div data-content-body-fallback ",
            "<div hidden data-content-body-fallback ",
        )
        if next_text != html_text:
            html_text = next_text
            changed = True

    if 'data-shop-info-row="about"' in html_text:
        about_key_m = re.search(
            r'data-shop-info-row="about"[\s\S]{0,400}?data-i18n="([^"]+\.about)"',
            html_text,
        )
        if about_key_m:
            about_val = lookup(ko, about_key_m.group(1))
            if isinstance(about_val, str) and about_val.strip():
                html_text2, n = SHOP_ABOUT_ROW.subn(r"\1", html_text, count=1)
                if n:
                    html_text = html_text2
                    changed = True

    html_text, ads_changed = ensure_ads_head(
        html_text, path.relative_to(ROOT).as_posix()
    )
    if ads_changed:
        changed = True

    if html_text != original:
        path.write_text(html_text, encoding="utf-8", newline="\n")
        return True
    return changed


def iter_html() -> list[Path]:
    out = []
    for path in ROOT.rglob("*.html"):
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        out.append(path)
    return out


def main() -> int:
    ko = load_lang("ko")
    if not isinstance(ko, dict) or not ko:
        ko = json.loads((ROOT / "i18n" / "ko.json").read_text(encoding="utf-8"))
    updated = 0
    scanned = 0
    for path in iter_html():
        scanned += 1
        try:
            if bake_file(path, ko):
                updated += 1
                print(f"baked: {path.relative_to(ROOT).as_posix()}")
        except Exception as exc:  # noqa: BLE001
            print(f"skip {path}: {exc}", file=sys.stderr)
    print(f"Done. scanned={scanned} updated={updated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
