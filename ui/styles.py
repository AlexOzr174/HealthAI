"""
Стили приложения HealthAI.
CURRENT_THEME — словарь цветов для виджетов; THEME_NAME — 'light' | 'dark'.
"""

from copy import deepcopy
from typing import Dict, Optional

# Резервная копия config.settings.COLORS (светлая тема) для sync_config_colors_with_theme
_CONFIG_COLORS_LIGHT_BACKUP: Optional[Dict[str, str]] = None

# Палитры для виджетов (ключи согласованы с chat_widget, photo_upload и т.д.)
LIGHT_THEME = {
    "name": "light",
    "bg": "#F0F2F5",
    "card_bg": "#FFFFFF",
    "text_primary": "#2C3E50",
    "text_secondary": "#7F8C8D",
    "border": "#E0E0E0",
    "input_bg": "#FFFFFF",
}

DARK_THEME = {
    "name": "dark",
    "bg": "#121212",
    "card_bg": "#1E1E1E",
    "text_primary": "#E0E0E0",
    "text_secondary": "#B0B0B0",
    "border": "#333333",
    "input_bg": "#2C2C2C",
}

THEME_NAME = "light"
CURRENT_THEME = deepcopy(LIGHT_THEME)

# Совместимость с theme_toggle и старым кодом
COLORS = CURRENT_THEME


def _sync_colors_alias():
    global COLORS
    COLORS = CURRENT_THEME


def sync_config_colors_with_theme() -> None:
    """
    Подставляет в config.settings.COLORS текст/фон под текущую тему,
    чтобы инлайн-стили страниц (COLORS['text_primary'] и т.д.) не давали тёмный текст на тёмном фоне.
    """
    global _CONFIG_COLORS_LIGHT_BACKUP
    try:
        from config import settings
    except ImportError:
        return
    if _CONFIG_COLORS_LIGHT_BACKUP is None:
        _CONFIG_COLORS_LIGHT_BACKUP = dict(settings.COLORS)
    if THEME_NAME == "dark":
        settings.COLORS["text_primary"] = CURRENT_THEME["text_primary"]
        settings.COLORS["text_secondary"] = CURRENT_THEME["text_secondary"]
        settings.COLORS["text_hint"] = CURRENT_THEME["text_secondary"]
        settings.COLORS["surface"] = CURRENT_THEME["card_bg"]
        settings.COLORS["background"] = CURRENT_THEME["bg"]
        settings.COLORS["border"] = CURRENT_THEME["border"]
    else:
        settings.COLORS.update(_CONFIG_COLORS_LIGHT_BACKUP)


class Styles:
    """Коллекция стилей для приложения"""

    BG_PRIMARY = "#F0F2F5"
    BG_SECONDARY = "#FFFFFF"
    TEXT_PRIMARY = "#2C3E50"
    TEXT_SECONDARY = "#7F8C8D"
    ACCENT = "#3498DB"
    ACCENT_HOVER = "#2980B9"
    SUCCESS = "#27AE60"
    WARNING = "#F39C12"
    ERROR = "#E74C3C"

    @staticmethod
    def get_stylesheet():
        if THEME_NAME == "dark":
            return Styles._get_dark_stylesheet()
        return Styles._get_light_stylesheet()

    @staticmethod
    def _get_light_stylesheet():
        return """
            QMainWindow {
                background-color: #F0F2F5;
            }
            QWidget {
                font-family: -apple-system, 'Helvetica Neue', 'Segoe UI', Arial;
                font-size: 14px;
                color: #2C3E50;
            }
            QFrame#sidebar {
                background-color: #FFFFFF;
                border-right: 1px solid #E0E0E0;
            }
            QPushButton {
                background-color: #F5F6F8;
                color: #1a1a1a;
                border: 2px solid #2C3E50;
                border-radius: 8px;
                padding: 9px 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #E8EAEF;
            }
            QPushButton:pressed {
                padding-top: 11px;
                padding-bottom: 7px;
                background-color: #D0D5DD;
                border-color: #1a1a1a;
            }
            QPushButton:disabled {
                color: #777777;
                border-color: #999999;
                background-color: #ECECEC;
            }
            QPushButton#navButton {
                background-color: transparent;
                border: none;
                text-align: left;
                padding: 12px 20px;
                border-radius: 8px;
                color: #2C3E50;
                font-weight: 500;
            }
            QPushButton#navButton:hover {
                background-color: #F0F2F5;
            }
            QPushButton#navButton:checked {
                background-color: #EBF5FB;
                color: #3498DB;
                font-weight: bold;
            }
            QPushButton#navButton:pressed {
                padding-top: 14px;
                padding-bottom: 10px;
                background-color: #E0E4E8;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QLabel#titleLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2C3E50;
            }
            QFrame#card {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E0E0E0;
            }
            QPushButton#primaryBtn {
                background-color: #FFFFFF;
                color: #1a1a1a;
                border: 2px solid #1a1a1a;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton#primaryBtn:hover {
                background-color: #F0F2F5;
            }
            QPushButton#primaryBtn:pressed {
                padding-top: 12px;
                padding-bottom: 8px;
                background-color: #D8DCE0;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #BDC3C7;
                border-radius: 6px;
                padding: 8px;
                background-color: #FFFFFF;
                color: #2C3E50;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #3498DB;
            }
            QSpinBox, QDoubleSpinBox {
                border: 1px solid #BDC3C7;
                border-radius: 6px;
                padding: 6px;
                background-color: #FFFFFF;
                color: #2C3E50;
            }
            QSpinBox:focus, QDoubleSpinBox:focus {
                border: 1px solid #3498DB;
            }
            QComboBox {
                border: 1px solid #BDC3C7;
                border-radius: 6px;
                padding: 6px 10px;
                padding-right: 30px;
                min-height: 28px;
                background-color: #FFFFFF;
                color: #2C3E50;
            }
            QComboBox:hover {
                border-color: #95A5A6;
            }
            QComboBox:focus {
                border: 1px solid #3498DB;
            }
            QComboBox:disabled {
                background-color: #ECEFF1;
                color: #95A5A6;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 28px;
                border: none;
                border-left: 1px solid #E0E0E0;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
                background-color: #F5F7FA;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #2C3E50;
                selection-background-color: #D6EAF8;
                selection-color: #1a1a1a;
                border: 1px solid #BDC3C7;
                border-radius: 6px;
                outline: none;
                padding: 4px;
            }
            QComboBox QAbstractItemView::item {
                min-height: 30px;
                padding: 6px 12px;
                color: #2C3E50;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #EBF5FB;
                color: #1a1a1a;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #D6EAF8;
                color: #1a1a1a;
            }
            QGroupBox {
                font-weight: 600;
                color: #2C3E50;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                margin-top: 12px;
                padding-top: 14px;
                background-color: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #2C3E50;
            }
            QMenuBar {
                background-color: #FFFFFF;
                color: #2C3E50;
                border-bottom: 1px solid #E0E0E0;
            }
            QMenuBar::item:selected {
                background-color: #EBF5FB;
            }
            QMenu {
                background-color: #FFFFFF;
                color: #2C3E50;
                border: 1px solid #BDC3C7;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 24px;
            }
            QMenu::item:selected {
                background-color: #EBF5FB;
                color: #1a1a1a;
            }
            QToolTip {
                background-color: #FFFFFF;
                color: #2C3E50;
                border: 1px solid #BDC3C7;
                padding: 6px 10px;
                border-radius: 4px;
            }
            QListWidget {
                background-color: #FFFFFF;
                color: #2C3E50;
                border: 1px solid #BDC3C7;
                border-radius: 6px;
            }
            QListWidget::item:selected {
                background-color: #D6EAF8;
                color: #1a1a1a;
            }
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #E0E0E0;
                height: 8px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498DB;
                border-radius: 4px;
            }
            QTableWidget {
                border: none;
                background-color: white;
                alternate-background-color: #F9F9F9;
                gridline-color: #E0E0E0;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #F0F2F5;
                padding: 8px;
                border: none;
                font-weight: bold;
                color: #2C3E50;
            }
            QMessageBox {
                background-color: #FFFFFF;
            }
            QMessageBox QLabel {
                color: #1a1a1a;
                min-width: 280px;
            }
            QMessageBox QLabel#qt_msgbox_label {
                color: #1a1a1a;
            }
            QMessageBox QDialogButtonBox {
                background-color: #FFFFFF;
            }
            QMessageBox QPushButton {
                color: #1a1a1a;
                background-color: #EEF2F5;
                border: 2px solid #2C3E50;
                border-radius: 8px;
                padding: 8px 18px;
                min-width: 96px;
                min-height: 36px;
                font-weight: 600;
            }
            QMessageBox QPushButton:hover {
                background-color: #D5DEE5;
            }
            QMessageBox QPushButton:pressed {
                padding-top: 10px;
                padding-bottom: 6px;
                background-color: #C8D0D8;
            }
            QDialog {
                background-color: #F5F6F8;
            }
            QDialog QLabel {
                color: #1a1a1a;
            }
            QDialog QLineEdit, QDialog QTextEdit, QDialog QComboBox, QDialog QComboBox QAbstractItemView {
                border: 1px solid #BDC3C7;
                border-radius: 6px;
                padding: 8px;
                background-color: #FFFFFF;
                color: #2C3E50;
            }
            QDialog QListWidget {
                background-color: #FFFFFF;
                color: #2C3E50;
            }
            QDialog QDialogButtonBox QPushButton {
                color: #1a1a1a;
                background-color: #F5F6F8;
                border: 2px solid #2C3E50;
                border-radius: 6px;
                padding: 8px 14px;
                font-weight: 600;
            }
            QDialog QDialogButtonBox QPushButton:hover {
                background-color: #E8EAEF;
            }
            QDialog QDialogButtonBox QPushButton:pressed {
                padding-top: 10px;
                padding-bottom: 6px;
                background-color: #D0D5DD;
            }
            QFileDialog {
                background-color: #F5F6F8;
            }
            QFileDialog QWidget {
                color: #1a1a1a;
            }
            QFileDialog QLabel {
                color: #1a1a1a;
                background-color: transparent;
            }
            QFileDialog QFrame {
                background-color: #F5F6F8;
                border: none;
            }
            QFileDialog QAbstractItemView {
                background-color: #FFFFFF;
                color: #1a1a1a;
                alternate-background-color: #F8F9FA;
                selection-background-color: #D6EAF8;
                selection-color: #1a1a1a;
            }
            QFileDialog QTableView {
                background-color: #FFFFFF;
                color: #1a1a1a;
                gridline-color: #BDC3C7;
                selection-background-color: #D6EAF8;
                selection-color: #1a1a1a;
            }
            QFileDialog QTreeView, QFileDialog QListView {
                background-color: #FFFFFF;
                color: #1a1a1a;
                alternate-background-color: #F8F9FA;
                border: 1px solid #BDC3C7;
                border-radius: 6px;
                selection-background-color: #D6EAF8;
                selection-color: #1a1a1a;
                outline: none;
            }
            QFileDialog QTreeView::item, QFileDialog QListView::item {
                color: #1a1a1a;
                padding: 4px 6px;
            }
            QFileDialog QTreeView::item:selected, QFileDialog QListView::item:selected {
                background-color: #D6EAF8;
                color: #1a1a1a;
            }
            QFileDialog QHeaderView::section {
                background-color: #ECEFF1;
                color: #1a1a1a;
                padding: 8px;
                border: 1px solid #BDC3C7;
                font-weight: 600;
            }
            QFileDialog QLineEdit {
                background-color: #FFFFFF;
                color: #1a1a1a;
                border: 1px solid #BDC3C7;
                border-radius: 6px;
                padding: 8px;
            }
            QFileDialog QComboBox {
                background-color: #FFFFFF;
                color: #1a1a1a;
                border: 1px solid #BDC3C7;
                border-radius: 6px;
                padding: 6px 10px;
                padding-right: 28px;
                min-height: 28px;
            }
            QFileDialog QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 26px;
                border: none;
                border-left: 1px solid #BDC3C7;
                background-color: #ECEFF1;
            }
            QFileDialog QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #1a1a1a;
                selection-background-color: #D6EAF8;
                selection-color: #1a1a1a;
                border: 1px solid #BDC3C7;
                outline: none;
            }
            QFileDialog QComboBox QAbstractItemView::item {
                min-height: 28px;
                padding: 6px 10px;
            }
            QFileDialog QPushButton {
                background-color: #F5F6F8;
                color: #1a1a1a;
                border: 2px solid #2C3E50;
                border-radius: 8px;
                padding: 8px 18px;
                min-width: 92px;
                min-height: 36px;
                font-weight: 600;
            }
            QFileDialog QPushButton:hover {
                background-color: #E8EAEF;
            }
            QFileDialog QPushButton:pressed {
                padding-top: 10px;
                padding-bottom: 6px;
                background-color: #D0D5DD;
            }
            QFileDialog QToolButton {
                background-color: #FFFFFF;
                color: #1a1a1a;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                padding: 4px;
            }
            QFileDialog QToolButton:hover {
                background-color: #E8EAEF;
            }
            QInputDialog {
                background-color: #FFFFFF;
            }
            QInputDialog QLabel {
                color: #1a1a1a;
            }
            QInputDialog QLineEdit {
                border: 1px solid #BDC3C7;
                border-radius: 6px;
                padding: 8px;
                background-color: #FFFFFF;
                color: #1a1a1a;
            }
            QScrollBar:vertical {
                background-color: #F0F2F5;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #BDC3C7;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #95A5A6;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """

    @staticmethod
    def _get_dark_stylesheet():
        return """
            QMainWindow {
                background-color: #121212;
            }
            QWidget {
                font-family: -apple-system, 'Helvetica Neue', 'Segoe UI', Arial;
                font-size: 14px;
                color: #E0E0E0;
            }
            QFrame#sidebar {
                background-color: #1E1E1E;
                border-right: 1px solid #333333;
            }
            QPushButton {
                background-color: #3A3A3A;
                color: #F5F5F5;
                border: 2px solid #BDBDBD;
                border-radius: 8px;
                padding: 9px 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #484848;
            }
            QPushButton:pressed {
                padding-top: 11px;
                padding-bottom: 7px;
                background-color: #2A2A2A;
                border-color: #E0E0E0;
            }
            QPushButton:disabled {
                color: #888888;
                border-color: #666666;
            }
            QPushButton#navButton {
                background-color: transparent;
                border: none;
                text-align: left;
                padding: 12px 20px;
                border-radius: 8px;
                color: #B0B0B0;
                font-weight: 500;
            }
            QPushButton#navButton:hover {
                background-color: #2C2C2C;
                color: #FFFFFF;
            }
            QPushButton#navButton:checked {
                background-color: #2C3E50;
                color: #4FC3F7;
                font-weight: bold;
            }
            QPushButton#navButton:pressed {
                padding-top: 14px;
                padding-bottom: 10px;
                background-color: #252525;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QLabel#titleLabel {
                font-size: 24px;
                font-weight: bold;
                color: #FFFFFF;
            }
            QFrame#card {
                background-color: #1E1E1E;
                border-radius: 12px;
                border: 1px solid #333333;
            }
            QPushButton#primaryBtn {
                background-color: #E8E8E8;
                color: #1a1a1a;
                border: 2px solid #1a1a1a;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton#primaryBtn:hover {
                background-color: #D8D8D8;
            }
            QPushButton#primaryBtn:pressed {
                padding-top: 12px;
                padding-bottom: 8px;
                background-color: #B8B8B8;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 8px;
                background-color: #2C2C2C;
                color: #E0E0E0;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #4FC3F7;
            }
            QComboBox {
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 6px 10px;
                padding-right: 30px;
                min-height: 28px;
                background-color: #2C2C2C;
                color: #ECEFF1;
            }
            QComboBox:focus {
                border: 1px solid #4FC3F7;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 28px;
                border: none;
                border-left: 1px solid #444444;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
                background-color: #333333;
            }
            QComboBox QAbstractItemView {
                background-color: #2C2C2C;
                color: #ECEFF1;
                selection-background-color: #34495E;
                selection-color: #FFFFFF;
                border: 1px solid #555555;
                border-radius: 6px;
                outline: none;
                padding: 4px;
            }
            QComboBox QAbstractItemView::item {
                min-height: 30px;
                padding: 6px 12px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #3D566E;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #34495E;
                color: #FFFFFF;
            }
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #333333;
                height: 8px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4FC3F7;
                border-radius: 4px;
            }
            QTableWidget {
                border: none;
                background-color: #1E1E1E;
                alternate-background-color: #252525;
                gridline-color: #333333;
                color: #E0E0E0;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #2C2C2C;
                padding: 8px;
                border: none;
                font-weight: bold;
                color: #FFFFFF;
            }
            QMessageBox {
                background-color: #323232;
            }
            QMessageBox QLabel {
                color: #ECEFF1;
                min-width: 280px;
            }
            QMessageBox QLabel#qt_msgbox_label {
                color: #ECEFF1;
            }
            QMessageBox QDialogButtonBox {
                background-color: #323232;
            }
            QMessageBox QPushButton {
                color: #1a1a1a;
                background-color: #B3E5FC;
                border: 2px solid #4FC3F7;
                border-radius: 8px;
                padding: 8px 18px;
                min-width: 96px;
                min-height: 36px;
                font-weight: 600;
            }
            QMessageBox QPushButton:hover {
                background-color: #81D4FA;
            }
            QMessageBox QPushButton:pressed {
                padding-top: 10px;
                padding-bottom: 6px;
                background-color: #4FC3F7;
            }
            QDialog {
                background-color: #1E1E1E;
            }
            QDialog QLabel {
                color: #F0F0F0;
            }
            QDialog QLineEdit, QDialog QTextEdit, QDialog QComboBox, QDialog QComboBox QAbstractItemView {
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 8px;
                background-color: #2C2C2C;
                color: #E0E0E0;
            }
            QDialog QListWidget {
                background-color: #1E1E1E;
                color: #E0E0E0;
            }
            QDialog QDialogButtonBox QPushButton {
                color: #1a1a1a;
                background-color: #E0E0E0;
                border: 2px solid #1a1a1a;
                border-radius: 6px;
                padding: 8px 14px;
                font-weight: 600;
            }
            QDialog QDialogButtonBox QPushButton:hover {
                background-color: #D0D0D0;
            }
            QDialog QDialogButtonBox QPushButton:pressed {
                padding-top: 10px;
                padding-bottom: 6px;
            }
            QFileDialog {
                background-color: #1E1E1E;
            }
            QFileDialog QWidget {
                color: #ECEFF1;
            }
            QFileDialog QLabel {
                color: #ECEFF1;
                background-color: transparent;
            }
            QFileDialog QFrame {
                background-color: #1E1E1E;
                border: none;
            }
            QFileDialog QAbstractItemView {
                background-color: #252525;
                color: #F0F0F0;
                alternate-background-color: #2A2A2A;
                selection-background-color: #34495E;
                selection-color: #FFFFFF;
            }
            QFileDialog QTableView {
                background-color: #252525;
                color: #F0F0F0;
                gridline-color: #444444;
                selection-background-color: #34495E;
                selection-color: #FFFFFF;
            }
            QFileDialog QTreeView, QFileDialog QListView {
                background-color: #252525;
                color: #F0F0F0;
                alternate-background-color: #2A2A2A;
                border: 1px solid #444444;
                border-radius: 6px;
                selection-background-color: #34495E;
                selection-color: #FFFFFF;
                outline: none;
            }
            QFileDialog QTreeView::item, QFileDialog QListView::item {
                color: #F0F0F0;
                padding: 4px 6px;
            }
            QFileDialog QTreeView::item:selected, QFileDialog QListView::item:selected {
                background-color: #34495E;
                color: #FFFFFF;
            }
            QFileDialog QTreeView::item:hover, QFileDialog QListView::item:hover {
                background-color: #3D566E;
            }
            QFileDialog QHeaderView::section {
                background-color: #2C2C2C;
                color: #FFFFFF;
                padding: 8px;
                border: 1px solid #444444;
                font-weight: 600;
            }
            QFileDialog QLineEdit {
                background-color: #2C2C2C;
                color: #ECEFF1;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 8px;
                selection-background-color: #34495E;
                selection-color: #FFFFFF;
            }
            QFileDialog QComboBox {
                background-color: #2C2C2C;
                color: #ECEFF1;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 6px 10px;
                padding-right: 28px;
                min-height: 28px;
            }
            QFileDialog QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 26px;
                border: none;
                border-left: 1px solid #444444;
                background-color: #333333;
            }
            QFileDialog QComboBox QAbstractItemView {
                background-color: #2C2C2C;
                color: #ECEFF1;
                selection-background-color: #34495E;
                selection-color: #FFFFFF;
                border: 1px solid #555555;
                outline: none;
            }
            QFileDialog QComboBox QAbstractItemView::item {
                min-height: 28px;
                padding: 6px 10px;
                color: #ECEFF1;
            }
            QFileDialog QComboBox QAbstractItemView::item:hover {
                background-color: #3D566E;
                color: #FFFFFF;
            }
            QFileDialog QComboBox QAbstractItemView::item:selected {
                background-color: #34495E;
                color: #FFFFFF;
            }
            QFileDialog QPushButton {
                background-color: #E0E0E0;
                color: #121212;
                border: 2px solid #9E9E9E;
                border-radius: 8px;
                padding: 8px 18px;
                min-width: 92px;
                min-height: 36px;
                font-weight: 600;
            }
            QFileDialog QPushButton:hover {
                background-color: #F5F5F5;
                border-color: #BDBDBD;
            }
            QFileDialog QPushButton:pressed {
                padding-top: 10px;
                padding-bottom: 6px;
                background-color: #BDBDBD;
            }
            QFileDialog QToolButton {
                background-color: #3A3A3A;
                color: #F5F5F5;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
            }
            QFileDialog QToolButton:hover {
                background-color: #4A4A4A;
            }
            QInputDialog {
                background-color: #2C2C2C;
            }
            QInputDialog QLabel {
                color: #F5F5F5;
            }
            QInputDialog QLineEdit {
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 8px;
                background-color: #1E1E1E;
                color: #F0F0F0;
            }
            QScrollBar:vertical {
                background-color: #121212;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #444444;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #555555;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """


def set_theme(theme_name: str):
    """Установить тему (light/dark) и обновить CURRENT_THEME для виджетов."""
    global THEME_NAME, CURRENT_THEME
    if theme_name == "dark":
        THEME_NAME = "dark"
        CURRENT_THEME = deepcopy(DARK_THEME)
    elif theme_name == "light":
        THEME_NAME = "light"
        CURRENT_THEME = deepcopy(LIGHT_THEME)
    _sync_colors_alias()
    sync_config_colors_with_theme()


def toggle_theme():
    """Переключить тему; возвращает имя новой темы."""
    global THEME_NAME, CURRENT_THEME
    if THEME_NAME == "light":
        THEME_NAME = "dark"
        CURRENT_THEME = deepcopy(DARK_THEME)
    else:
        THEME_NAME = "light"
        CURRENT_THEME = deepcopy(LIGHT_THEME)
    _sync_colors_alias()
    sync_config_colors_with_theme()
    return THEME_NAME


def get_stylesheet():
    return Styles.get_stylesheet()


def apply_app_light_palette(app) -> None:
    """
    Явная светлая палитра для Fusion.
    На macOS при системной тёмной теме Qt иначе подставляет тёмные Base/Text —
    из-за этого у QComboBox popup бывает чёрный фон и нечитаемый текст.
    """
    from PyQt6.QtGui import QColor, QPalette

    p = QPalette()
    white = QColor("#FFFFFF")
    text = QColor("#1a1a1a")
    muted_bg = QColor("#F0F2F5")
    btn = QColor("#F5F6F8")
    highlight = QColor("#3498DB")

    p.setColor(QPalette.ColorRole.Window, muted_bg)
    p.setColor(QPalette.ColorRole.WindowText, text)
    p.setColor(QPalette.ColorRole.Base, white)
    p.setColor(QPalette.ColorRole.AlternateBase, QColor("#F5F7FA"))
    p.setColor(QPalette.ColorRole.Text, text)
    p.setColor(QPalette.ColorRole.Button, btn)
    p.setColor(QPalette.ColorRole.ButtonText, text)
    p.setColor(QPalette.ColorRole.Highlight, highlight)
    p.setColor(QPalette.ColorRole.HighlightedText, white)
    p.setColor(QPalette.ColorRole.ToolTipBase, white)
    p.setColor(QPalette.ColorRole.ToolTipText, text)
    p.setColor(QPalette.ColorRole.PlaceholderText, QColor("#7F8C8D"))
    app.setPalette(p)


def apply_app_dark_palette(app) -> None:
    """Палитра для тёмной темы (если включён переключатель темы)."""
    from PyQt6.QtGui import QColor, QPalette

    p = QPalette()
    p.setColor(QPalette.ColorRole.Window, QColor("#121212"))
    p.setColor(QPalette.ColorRole.WindowText, QColor("#ECEFF1"))
    p.setColor(QPalette.ColorRole.Base, QColor("#2C2C2C"))
    p.setColor(QPalette.ColorRole.AlternateBase, QColor("#252525"))
    p.setColor(QPalette.ColorRole.Text, QColor("#E0E0E0"))
    p.setColor(QPalette.ColorRole.Button, QColor("#3A3A3A"))
    p.setColor(QPalette.ColorRole.ButtonText, QColor("#F5F5F5"))
    p.setColor(QPalette.ColorRole.Highlight, QColor("#4FC3F7"))
    p.setColor(QPalette.ColorRole.HighlightedText, QColor("#1a1a1a"))
    p.setColor(QPalette.ColorRole.ToolTipBase, QColor("#2C2C2C"))
    p.setColor(QPalette.ColorRole.ToolTipText, QColor("#ECEFF1"))
    app.setPalette(p)


_sync_colors_alias()
try:
    sync_config_colors_with_theme()
except Exception:
    pass
