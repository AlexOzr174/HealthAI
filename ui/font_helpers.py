"""Кроссплатформенные семейства шрифтов (избегаем отсутствующего Segoe UI на macOS)."""
from __future__ import annotations

import sys


def ui_font_family() -> str:
    if sys.platform == "darwin":
        return ".AppleSystemUIFont"
    if sys.platform == "win32":
        return "Segoe UI"
    return "Helvetica Neue"


def emoji_font_family() -> str:
    if sys.platform == "darwin":
        return "Apple Color Emoji"
    return "Segoe UI Emoji"
