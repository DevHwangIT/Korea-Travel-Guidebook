# -*- coding: utf-8 -*-
"""Apply ?v=VERSION to local CSS/JS references in all HTML files.

Reads the version from js/cache-version.js (window.SITE_ASSET_VERSION).
Idempotent: re-running with the same version is safe.
Does not modify external CDN URLs (http/https/protocol-relative).

Coverage: every *.html under the repo root except SKIP_DIR_NAMES
(node_modules, .git, venv, tool, …) — includes nested pages/, templates/,
components/. Used by tool/update-version.py and CMS refresh_public_assets().
"""
from __future__ import annotations

import re
from datetime import datetime
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
ASSET_COMMENT_VERSION_RE = re.compile(r"""<!--\s*asset-v:\s*(\S+)\s*-->""")
V_QUERY_RE = re.compile(r"""[?&]v=([^"'&\s]+)""")


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
    """Ensure every asset-v comment matches version; insert one in <head> if missing."""
    comment = f"<!-- asset-v: {version} -->"
    if ASSET_COMMENT_RE.search(html):
        # Replace ALL occurrences so nested snippets cannot leave a stale marker.
        return ASSET_COMMENT_RE.sub(comment, html)

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
    if updated != before_comment:
        changes += 1
    return updated, changes


def iter_html_files(root: Path | None = None):
    base = root or ROOT
    for path in sorted(base.rglob("*.html")):
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        yield path


def collect_html_version_issues(
    version: str | None = None, root: Path | None = None
) -> list[dict]:
    """Return per-file problems when HTML is not fully on ``version``."""
    ver = version or read_version()
    base = root or ROOT
    expected_comment = f"<!-- asset-v: {ver} -->"
    issues: list[dict] = []

    for html_path in iter_html_files(base):
        text = html_path.read_text(encoding="utf-8")
        rel = html_path.relative_to(base).as_posix()
        problems: list[str] = []

        comments = ASSET_COMMENT_VERSION_RE.findall(text)
        if not comments:
            # Snippets without <head> still get a leading comment from sync;
            # flag only if the file references versioned site assets.
            has_site_asset = False
            for m in ATTR_RE.finditer(text):
                url = m.group("url")
                if is_external(url):
                    continue
                if is_local_site_asset(url.split("?", 1)[0]):
                    has_site_asset = True
                    break
            if has_site_asset:
                problems.append("missing asset-v comment")
        else:
            for c in comments:
                if c != ver:
                    problems.append(f"stale asset-v comment: {c}")
            # Also catch malformed comments that ASSET_COMMENT_RE matches but
            # version extract missed — compare raw comment text.
            for raw in ASSET_COMMENT_RE.findall(text):
                if raw != expected_comment and ver not in raw:
                    problems.append(f"unexpected asset-v markup: {raw}")

        for m in ATTR_RE.finditer(text):
            url = m.group("url")
            if is_external(url):
                continue
            path = url.split("?", 1)[0]
            if not is_local_site_asset(path):
                continue
            vm = V_QUERY_RE.search(url)
            if not vm:
                problems.append(f"missing ?v= on {url}")
            elif vm.group(1) != ver:
                problems.append(f"stale ?v={vm.group(1)} on {url}")

        if problems:
            issues.append({"file": rel, "problems": problems})

    return issues


def verify_asset_versions(
    version: str | None = None, root: Path | None = None
) -> dict:
    """Raise SystemExit if any public HTML is out of sync with the version."""
    ver = version or read_version()
    base = root or ROOT
    scanned = sum(1 for _ in iter_html_files(base))
    issues = collect_html_version_issues(ver, root=base)
    summary = {
        "version": ver,
        "files_scanned": scanned,
        "files_ok": scanned - len(issues),
        "files_bad": len(issues),
        "issues": issues,
    }
    if issues:
        lines = [
            f"Cache version mismatch: expected {ver!r}, "
            f"{len(issues)}/{scanned} HTML file(s) out of sync."
        ]
        for item in issues[:40]:
            detail = "; ".join(item["problems"][:5])
            lines.append(f"  - {item['file']}: {detail}")
        if len(issues) > 40:
            lines.append(f"  ... +{len(issues) - 40} more")
        lines.append(
            "Fix: python tool/update-version.py "
            "(or python scripts/apply-cache-bust.py)"
        )
        raise SystemExit("\n".join(lines))
    return summary


def apply_cache_bust(version: str | None = None, root: Path | None = None) -> dict:
    """Apply version query strings to all HTML. Returns a summary dict."""
    ver = version or read_version()
    base = root or ROOT
    updated_files = 0
    total_attr_changes = 0
    files: list[str] = []
    scanned = 0

    for html_path in iter_html_files(base):
        scanned += 1
        original = html_path.read_text(encoding="utf-8")
        new_text, n = process_html(original, ver)
        if new_text != original:
            html_path.write_text(new_text, encoding="utf-8", newline="\n")
            updated_files += 1
            total_attr_changes += n
            files.append(html_path.relative_to(base).as_posix())

    # Re-read disk and fail loudly if anything was skipped (partial write / regex miss).
    verify = verify_asset_versions(ver, root=base)

    return {
        "version": ver,
        "files_scanned": scanned,
        "files_updated": updated_files,
        "replacements": total_attr_changes,
        "files": files,
        "files_ok": verify["files_ok"],
    }


def new_asset_version() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S")


def bump_asset_version(root: Path | None = None) -> dict:
    """Write a fresh SITE_ASSET_VERSION and apply ?v= to all HTML.

    Order: write version file first, then patch every HTML, then verify.
    If a previous run died mid-apply, re-running apply_cache_bust() (or this
    bump) finishes remaining files against js/cache-version.js.

    Used by update-version.py and by the local CMS after content/media saves
    so viewers pick up rebuilt i18n/messages.js and other assets.
    """
    old = None
    try:
        old = read_version()
    except SystemExit:
        pass
    version = new_asset_version()
    # Avoid colliding with a bump in the same second
    if old == version:
        version = str(int(version) + 1) if version.isdigit() else version + "1"
    write_version(version)
    summary = apply_cache_bust(version, root=root)
    summary["old_version"] = old
    return summary


def main() -> int:
    summary = apply_cache_bust()
    for rel in summary["files"]:
        print(f"updated: {rel}")
    print(
        f"Done. version={summary['version']!r} "
        f"files_scanned={summary['files_scanned']} "
        f"files_updated={summary['files_updated']} "
        f"replacements~={summary['replacements']}"
    )
    return 0
