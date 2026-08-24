# -*- coding: utf-8 -*-
from pathlib import Path
import io
import ssl
import shutil
import urllib.parse
import urllib.request
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "Images" / "places"
UA = "KoreaTravelGuidebook/1.0 (course photo audit; educational; rate-limited)"
CTX = ssl._create_unverified_context()
TITLE = "N-Seoul-Tower and Namsan Park (26876783888).jpg"


def main() -> None:
    url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(
        TITLE.replace(" ", "_")
    )
    print("GET", url, flush=True)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Referer": "https://commons.wikimedia.org/"},
    )
    with urllib.request.urlopen(req, timeout=90, context=CTX) as r:
        data = r.read()
    print("bytes", len(data), data[:4], flush=True)
    im = Image.open(io.BytesIO(data)).convert("RGB")
    print("src", im.size, flush=True)
    im.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
    tmp = P / "_n-seoul-tower-new.jpg"
    final = P / "n-seoul-tower.jpg"
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=86, optimize=True)
    raw = buf.getvalue()
    tmp.write_bytes(raw)
    print("tmp", tmp.stat().st_size, im.size, flush=True)
    shutil.copyfile(tmp, final)
    print("final", final.stat().st_size, Image.open(final).size, flush=True)


if __name__ == "__main__":
    main()
