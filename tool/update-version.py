# -*- coding: utf-8 -*-
"""Bump SITE_ASSET_VERSION (YYYYMMDDHHMMSS) and apply ?v= to all HTML.

Usage:
  python tool/update-version.py
  double-click tool/update-version.bat
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from lib.cache_bust import apply_cache_bust, read_version, write_version  # noqa: E402
from lib.paths import ROOT, VERSION_FILE  # noqa: E402


def new_version() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S")


def main() -> int:
    old = None
    try:
        old = read_version()
    except SystemExit:
        pass

    version = new_version()
    write_version(version)
    print(f"Wrote {VERSION_FILE.relative_to(ROOT).as_posix()}: {old!r} → {version!r}")

    summary = apply_cache_bust(version)
    for rel in summary["files"]:
        print(f"updated: {rel}")
    print(
        f"Done. version={version!r} files_updated={summary['files_updated']} "
        f"replacements~={summary['replacements']}"
    )
    print("\n다음: 변경을 커밋·푸시하면 GitHub Pages 캐시가 새 ?v= 로 갱신됩니다.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        if sys.stdin.isatty() or sys.platform == "win32":
            input("\nEnter 키를 누르면 종료합니다...")
        raise SystemExit(1)
