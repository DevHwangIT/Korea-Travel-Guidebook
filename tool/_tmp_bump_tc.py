from pathlib import Path
import re
import os

ver = "20260824131000"
cv = Path("js/cache-version.js")
tmp_cv = Path("js/_cache-version.tmp.js")
tmp_cv.write_text(
    "/* Single source of truth for static asset cache-busting.\n"
    " * Bump SITE_ASSET_VERSION via tool/update-version.py (or edit here),\n"
    " * then HTML ?v= is applied automatically by that tool / apply-cache-bust.\n"
    " */\n"
    f'window.SITE_ASSET_VERSION = "{ver}";\n',
    encoding="utf-8",
)
os.replace(tmp_cv, cv)

p = Path("pages/travel-courses/index.html")
t = p.read_text(encoding="utf-8")
t = re.sub(r"[?]v=\d+", f"?v={ver}", t)
t = re.sub(r"asset-v: \d+", f"asset-v: {ver}", t)
tmp = Path("_tc_tmp.html")
tmp.write_text(t, encoding="utf-8")
os.replace(tmp, p)
print("bumped", ver)
