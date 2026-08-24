from pathlib import Path
import datetime
import re

p = Path(__file__).resolve().parents[1] / "js" / "cache-version.js"
t = p.read_text(encoding="utf-8")
v = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
t2 = re.sub(r'SITE_ASSET_VERSION\s*=\s*"[^"]+"', f'SITE_ASSET_VERSION = "{v}"', t)
p.write_text(t2, encoding="utf-8")
print("cache version", v)
