# -*- coding: utf-8 -*-
"""Regenerate i18n/messages.js from locale JSON files.

To add a language (e.g. zh):
  1. Add code to LANGS below and create i18n/zh.json
  2. Uncomment the entry in js/i18n.js GUIDE_LANGS
  3. See i18n/README-locales.md
"""
import json
from pathlib import Path

# Data-driven locale list — keep in sync with js/i18n.js GUIDE_LANGS
LANGS = ("ko", "en", "ja")
# LANGS = ("ko", "en", "ja", "zh")

root = Path(__file__).resolve().parent
messages = {
    lang: json.loads((root / f"{lang}.json").read_text(encoding="utf-8"))
    for lang in LANGS
}
(root / "messages.js").write_text(
    "window.__I18N_MESSAGES__ = "
    + json.dumps(messages, ensure_ascii=False, indent=2)
    + ";\n",
    encoding="utf-8",
)
print("updated messages.js (" + ", ".join(LANGS) + ")")
