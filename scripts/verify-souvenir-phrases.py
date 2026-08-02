# -*- coding: utf-8 -*-
import json
import re
from pathlib import Path

r = Path(__file__).resolve().parents[1]
text = (r / "js" / "korean-phrases-data.js").read_text(encoding="utf-8")
ids = re.findall(r'"id":\s*"([^"]+)"', text)
audio = {p.stem for p in (r / "audio" / "korean").glob("*.mp3")}
missing = sorted(set(ids) - audio)
extra = sorted(audio - set(ids))
print("phrase ids", len(ids), "unique", len(set(ids)))
print("missing audio", missing)
print("extra audio", extra)
for p in sorted((r / "pages" / "souvenir").iterdir()):
    if p.is_dir():
        html = p / "index.html"
        img = r / "Images" / "souvenir" / f"{p.name}.jpg"
        print(p.name, "html", html.exists(), "img", img.exists(), img.stat().st_size if img.exists() else 0)
for lang in ["ko", "en", "ja"]:
    d = json.loads((r / "i18n" / f"{lang}.json").read_text(encoding="utf-8"))
    s = d["souvenir"]
    need = ["maskBody1", "maskTip", "readMore", "tapHint", "kpopTip"]
    print(lang, all(k in s for k in need), "count", len(s))
