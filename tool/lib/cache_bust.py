# -*- coding: utf-8 -*-
"""Apply ?v=VERSION to local CSS/JS references in all HTML files.

Reads the version from js/cache-version.js (window.SITE_ASSET_VERSION).
Idempotent: re-running with the same version is safe.
Does not modify external CDN URLs (http/https/protocol-relative).
"""
from __future__ import annotations

import re
from pathlib import Path

from .paths import ROOT, SKIP_DIR_NAMES, VERSION_FILE

VERSION_RE = re.compile(
    r"""window\.SITE_ASSET_VERSION\s*=\s*["']([^"']+)["']""",
)
ATTR_RE = re.compile(
    r"""(?P<prefix>\b(?:href|src)\s*=\s*["'])"""
    r"""(?P<url>[^"'#]+?\.(?:css|js)(?:\?[^"']*)?)"""
    r"""(?P<suffix>["'])""",
    re.IGNORECASE,
)
ASSET_COMMENT_RE = re.compile(r"""<!--\s*asset-v:\s*[^>]*-->""")


def read_version(version_file: Path | None = None) -> str:
    path = version_file or VERSION_FILE
    text = path.read_text(encoding="utf-8")
    match = VERSION_RE.search(text)
    if not match:
        raise SystemExit(f"Could not find window.SITE_ASSET_VERSION in {path}")
    version = match.group(1).strip()
    if not version:
        raise SystemExit("SITE_ASSET_VERSION is empty")
    return version


def write_version(version: str, version_file: Path | None = None) -> None:
    path = version_file or VERSION_FILE
    path.write_text(
        "/* Single source of truth for static asset cache-busting.\n"
        " * Bump SITE_ASSET_VERSION via tool/update-version.py (or edit here),\n"
        " * then HTML ?v= is applied automatically by that tool / apply-cache-bust.\n"
        " */\n"
        f'window.SITE_ASSET_VERSION = "{version}";\n',
        encoding="utf-8",
        newline="\n",
    )


def is_external(url: str) -> bool:
    lower = url.lower()
    return (
        lower.startswith("http://")
        or lower.startswith("https://")
        or lower.startswith("//")
        or lower.startswith("data:")
    )


def is_local_site_asset(url_path: str) -> bool:
    """Relative site CSS/JS under styles.css, js/, i18n/, data/."""
    normalized = url_path.replace("\\", "/")
    bare = normalized
    while bare.startswith("./"):
        bare = bare[2:]
    while bare.startswith("../"):
        bare = bare[3:]

    if bare == "styles.css" or bare.endswith("/styles.css"):
        return True
    if bare.startswith("js/") or "/js/" in normalized:
        return True
    if bare.startswith("i18n/") or "/i18n/" in normalized:
        return True
    if bare.startswith("data/") or "/data/" in normalized:
        return True
    return False


def with_version(url: str, version: str) -> str:
    path = url.split("?", 1)[0]
    return f"{path}?v={version}"


def sync_asset_comment(html: str, version: str) -> str:
    comment = f"<!-- asset-v: {version} -->"
    if ASSET_COMMENT_RE.search(html):
        return ASSET_COMMENT_RE.sub(comment, html, count=1)

    head_match = re.search(r"<head[^>]*>", html, re.IGNORECASE)
    if head_match:
        idx = head_match.end()
        return html[:idx] + "\n  " + comment + html[idx:]
    return comment + "\n" + html


def process_html(text: str, version: str) -> tuple[str, int]:
    changes = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal changes
        url = match.group("url")
        if is_external(url):
            return match.group(0)
        path = url.split("?", 1)[0]
        if not is_local_site_asset(path):
            return match.group(0)
        new_url = with_version(url, version)
        if new_url != url:
            changes += 1
        return f"{match.group('prefix')}{new_url}{match.group('suffix')}"

    updated = ATTR_RE.sub(repl, text)
    before_comment = updated
    updated = sync_asset_comment(updated, version)
    if updated != before_comment and not ASSET_COMMENT_RE.search(text):
        changes += 1
    elif ASSET_COMMENT_RE.search(text):
        old = ASSET_COMMENT_RE.search(text)
        if old and old.group(0) != f"<!-- asset-v: {version} -->":
            changes += 1
    return updated, changes


def iter_html_files(root: Path | None = None):
    base = root or ROOT
    for path in sorted(base.rglob("*.html")):
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        yield path


def apply_cache_bust(version: str | None = None, root: Path | None = None) -> dict:
    """Apply version query strings to all HTML. Returns a summary dict."""
    ver = version or read_version()
    base = root or ROOT
    updated_files = 0
    total_attr_changes = 0
    files: list[str] = []

    for html_path in iter_html_files(base):
        original = html_path.read_text(encoding="utf-8")
        new_text, n = process_html(original, ver)
        if new_text != original:
            html_path.write_text(new_text, encoding="utf-8", newline="\n")
            updated_files += 1
            total_attr_changes += n
            files.append(html_path.relative_to(base).as_posix())

    return {
        "version": ver,
        "files_updated": updated_files,
        "replacements": total_attr_changes,
        "files": files,
    }


def main() -> int:
    summary = apply_cache_bust()
    for rel in summary["files"]:
        print(f"updated: {rel}")
    print(
        f"Done. version={summary['version']!r} "
        f"files_updated={summary['files_updated']} "
        f"replacements~={summary['replacements']}"
    )
    return 0
