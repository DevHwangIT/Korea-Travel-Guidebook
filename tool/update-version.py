# -*- coding: utf-8 -*-
"""Bump SITE_ASSET_VERSION (YYYYMMDDHHMMSS) and apply ?v= to all HTML.

Usage:
  python tool/update-version.py
  double-click tool/update-version.bat
"""
from __future__ import annotations

import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from lib.cache_bust import bump_asset_version, read_version  # noqa: E402
from lib.paths import ROOT, VERSION_FILE  # noqa: E402


def main() -> int:
    old = None
    try:
        old = read_version()
    except SystemExit:
        pass

    summary = bump_asset_version()
    version = summary["version"]
    print(
        f"Wrote {VERSION_FILE.relative_to(ROOT).as_posix()}: "
        f"{old!r} → {version!r}"
    )
    for rel in summary["files"]:
        print(f"updated: {rel}")
    print(
        f"Done. version={version!r} "
        f"files_scanned={summary['files_scanned']} "
        f"files_updated={summary['files_updated']} "
        f"verified_ok={summary['files_ok']} "
        f"replacements~={summary['replacements']}"
    )
    print(
        "\n다음: 변경을 커밋·푸시하면 GitHub Pages가 새 HTML/?v= 를 배포합니다.\n"
        "HTML은 Pages에서 약 10분(max-age=600) 캐시될 수 있으니, "
        "확인 시 Ctrl+F5(강력 새로고침)를 사용하세요."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        if sys.stdin.isatty() or sys.platform == "win32":
            input("\nEnter 키를 누르면 종료합니다...")
        raise SystemExit(1)
