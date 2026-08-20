# -*- coding: utf-8 -*-
"""Regenerate i18n/messages.js from locale JSON sources.

Merge order (per language):
  1. i18n/{lang}.json          — residual / assembled fallback (if present)
  2. i18n/common/{lang}.json   — shared keys
  3. i18n/pages/**/{lang}.json — page-group locales

Also writes the merged result back to i18n/{lang}.json as the canonical
assembled mirror (CMS / tooling can keep reading that path).

Runtime contract: window.__I18N_MESSAGES__ in messages.js (unchanged).

Supported: ko, en, ja, zh, zh-Hant, vi, th, ru (keep in sync with js/i18n.js GUIDE_LANGS).
See i18n/README-locales.md and i18n/locale_routing.py.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from locale_routing import (  # noqa: E402
    LANGS,
    load_merged_lang,
    write_assembled_lang,
)

messages = {}
for lang in LANGS:
    merged = load_merged_lang(lang)
    write_assembled_lang(lang, merged)
    messages[lang] = merged

import os
import tempfile

payload = (
    "window.__I18N_MESSAGES__ = "
    + json.dumps(messages, ensure_ascii=False, indent=2)
    + ";\n"
)
target = ROOT / "messages.js"
# Atomic replace avoids Windows EINVAL when messages.js is open in the IDE.
fd, tmp_name = tempfile.mkstemp(prefix="messages-", suffix=".js", dir=str(ROOT))
try:
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        f.write(payload)
    os.replace(tmp_name, target)
finally:
    if os.path.exists(tmp_name):
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
print("updated messages.js (" + ", ".join(LANGS) + ")")
