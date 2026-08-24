# -*- coding: utf-8 -*-
"""Move one-off tool scripts into tool/_jobs. Keep admin + version bump."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tool"
JOBS = TOOL / "_jobs"
KEEP_FILES = {
    "content-admin.py",
    "content-admin.bat",
    "update-version.py",
    "update-version.bat",
    "README-admin.md",
    "requirements.txt",
    "build-food-recommend-catalog.py",
    "generate-sitemap.py",
    "_organize_tools.py",
}
KEEP_DIRS = {"lib", "static", "_jobs"}


def move_item(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        if dest.is_dir():
            shutil.rmtree(dest)
        else:
            dest.unlink()
    shutil.move(str(src), str(dest))
    print(f"move {src.relative_to(ROOT)} -> {dest.relative_to(ROOT)}", flush=True)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    JOBS.mkdir(parents=True, exist_ok=True)
    (JOBS / "README.md").write_text(
        "# One-off jobs (not part of the public site)\n\n"
        "`tool/` 루트에는 로컬 관리자(`content-admin`)와 사이트 업데이트"
        "(`update-version`, `build-food-recommend-catalog`, `generate-sitemap`)만 둡니다.\n\n"
        "여기 파일은 일회성 패치·이미지 수집·마이그레이션입니다. "
        "공개 페이지 런타임에서 쓰이지 않습니다.\n\n"
        "다시 실행할 때는 `tool/`로 복사한 뒤 돌리세요. "
        "대부분의 스크립트는 `Path(__file__).parents[1]`을 프로젝트 루트로 가정합니다.\n",
        encoding="utf-8",
    )

    for item in sorted(TOOL.iterdir(), key=lambda p: p.name.lower()):
        if item.name in KEEP_FILES or item.name in KEEP_DIRS:
            continue
        if item.name.startswith(".") or item.name == "__pycache__":
            if item.name == "__pycache__":
                shutil.rmtree(item, ignore_errors=True)
            continue
        if item.name in {"_tmp", "_tmp_seoul_tr"}:
            shutil.rmtree(item)
            print(f"delete tool/{item.name}", flush=True)
            continue
        dest = JOBS / item.name
        move_item(item, dest)

    scripts = ROOT / "scripts"
    if scripts.exists():
        move_item(scripts, JOBS / "site-scripts")

    i18n = ROOT / "i18n"
    once = JOBS / "i18n-once"
    once.mkdir(parents=True, exist_ok=True)
    for f in list(i18n.glob("_*.py")):
        move_item(f, once / f.name)
    overlays = i18n / "_overlays"
    if overlays.exists():
        move_item(overlays, once / "_overlays")

    tmp_img = ROOT / "Images" / "places" / "_tmp"
    if tmp_img.exists():
        shutil.rmtree(tmp_img)
        print("delete Images/places/_tmp", flush=True)

    node = ROOT / "node_modules"
    if node.exists():
        shutil.rmtree(node)
        print("delete node_modules", flush=True)
    for extra in ("package-lock.json", "package.json"):
        p = ROOT / extra
        if p.exists():
            p.unlink()
            print("delete", extra, flush=True)

    print("DONE", flush=True)
    print("tool root", sorted(p.name for p in TOOL.iterdir()), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
