"""
UI пакет приложения HealthAI
"""

from ui.main_window import MainWindow
from ui.styles import Styles, set_theme, toggle_theme, CURRENT_THEME

__all__ = [
    'MainWindow',
    'Styles',
    'set_theme',
    'toggle_theme',
    'CURRENT_THEME'
]
