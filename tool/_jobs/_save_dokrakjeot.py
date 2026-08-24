# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib.util
import sys
import time

ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("fill_ph", ROOT / "tool" / "_fill_placeholder_photos.py")
fill = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fill)

from tool._fill_from_cha import image_list, pick_image  # noqa: E402


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    hashes = fill.type_hashes()
    # 나성 독락정 = Sejong Dokrakjeong
    images = image_list("31", "0000080000000", "45")
    print(f"images {len(images)}")
    for im in images:
        print(im["nuri"], im["desc"], im["url"])
    im = pick_image("dokrakjeot", "나성 독락정", images)
    if not im:
        print("no image")
        return 1
    url = im["url"].replace("http://", "https://")
    time.sleep(1.5)
    ok = fill.try_save(url, fill.dest_path("dokrakjeot"), hashes, "cha:나성 독락정")
    if ok:
        fill.copy_to("dokrakjeot", "sejot-dokrakjeot")
        print("copied sejot-dokrakjeot")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
