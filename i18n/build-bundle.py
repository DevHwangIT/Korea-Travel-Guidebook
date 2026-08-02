# -*- coding: utf-8 -*-
"""Regenerate i18n/messages.js from ko.json / en.json / ja.json"""
import json
from pathlib import Path

root = Path(__file__).resolve().parent
messages = {
    lang: json.loads((root / f"{lang}.json").read_text(encoding="utf-8"))
    for lang in ("ko", "en", "ja")
}
(root / "messages.js").write_text(
    "window.__I18N_MESSAGES__ = "
    + json.dumps(messages, ensure_ascii=False, indent=2)
    + ";\n",
    encoding="utf-8",
)
print("updated messages.js")
