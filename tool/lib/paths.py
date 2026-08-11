# -*- coding: utf-8 -*-
"""Project root and common paths."""
from __future__ import annotations

from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parents[1]
ROOT = TOOL_DIR.parent

VERSION_FILE = ROOT / "js" / "cache-version.js"
I18N_DIR = ROOT / "i18n"
MEALS_DIR = ROOT / "pages" / "foods" / "meals"
DESSERTS_DIR = ROOT / "pages" / "foods" / "desserts"
TRANSPORT_DIR = ROOT / "pages" / "transportation"
PLACES_DIR = TRANSPORT_DIR / "places"
IMAGES_DISHES = ROOT / "Images" / "foods" / "dishes"
IMAGES_RESTAURANTS = ROOT / "Images" / "foods" / "restaurants"
IMAGES_BRANDS = ROOT / "Images" / "foods" / "brands"

SKIP_DIR_NAMES = {"node_modules", ".git", ".venv", "venv", "__pycache__", "tool"}
