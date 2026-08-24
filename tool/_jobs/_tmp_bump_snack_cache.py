# -*- coding: utf-8 -*-
from datetime import datetime
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ver = datetime.now().strftime("%Y%m%d%H%M%S")
print("new version", ver)

(ROOT / "js" / "cache-version.js").write_text(
    "/* Single source of truth for static asset cache-busting.\n"
    " * Bump SITE_ASSET_VERSION via tool/update-version.py (or edit here),\n"
    " * then HTML ?v= is applied automatically by that tool / apply-cache-bust.\n"
    " */\n"
    f'window.SITE_ASSET_VERSION = "{ver}";\n',
    encoding="utf-8",
    newline="\n",
)

targets = [ROOT / "pages" / "buy" / "index.html"]
souvenir = ROOT / "pages" / "souvenir"
for d in souvenir.iterdir():
    if d.is_dir():
        idx = d / "index.html"
        if idx.is_file():
            targets.append(idx)

pat_qv = re.compile(r"(\?v=)\d{14}")
pat_av = re.compile(r"(<!-- asset-v:\s*)\d{14}(\s*-->)")
updated = 0
for p in targets:
    try:
        text = p.read_text(encoding="utf-8")
    except OSError as e:
        print("skip", p, e)
        continue
    new = pat_qv.sub(rf"\g<1>{ver}", text)
    new = pat_av.sub(rf"\g<1>{ver}\2", new)
    if new != text:
        try:
            p.write_text(new, encoding="utf-8", newline="\n")
            updated += 1
        except OSError as e:
            print("write fail", p, e)
print("updated html files", updated, "of", len(targets))
