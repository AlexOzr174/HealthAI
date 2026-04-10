"""
Стили приложения HealthAI
Поддержка светлой и тёмной темы
"""

# Текущая тема
CURRENT_THEME = "light"


class Styles:
    """Коллекция стилей для приложения"""

    # Базовые цвета (Светлая тема по умолчанию)
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
        """Возвращает полный CSS stylesheet в зависимости от текущей темы"""
        if CURRENT_THEME == "dark":
            return Styles._get_dark_stylesheet()
        return Styles._get_light_stylesheet()

    @staticmethod
    def _get_light_stylesheet():
        return """
            QMainWindow {
                background-color: #F0F2F5;
            }
            QWidget {
                font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
                font-size: 14px;
                color: #2C3E50;
            }
            QFrame#sidebar {
                background-color: #FFFFFF;
                border-right: 1px solid #E0E0E0;
            }
            QPushButton#navButton {
                background-color: transparent;
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
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QLabel#titleLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2C3E50;
            }
            /* Карточки */
            QFrame#card {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E0E0E0;
            }
            /* Кнопки */
            QPushButton#primaryBtn {
                background-color: #3498DB;
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton#primaryBtn:hover {
                background-color: #2980B9;
            }
            /* Поля ввода */
            QLineEdit, QTextEdit, QComboBox {
                border: 1px solid #BDC3C7;
                border-radius: 6px;
                padding: 8px;
                background-color: white;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 1px solid #3498DB;
            }
            /* Прогресс бары */
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
            /* Таблицы */
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
            /* Скроллбары */
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
                font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
                font-size: 14px;
                color: #E0E0E0;
            }
            QFrame#sidebar {
                background-color: #1E1E1E;
                border-right: 1px solid #333333;
            }
            QPushButton#navButton {
                background-color: transparent;
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
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QLabel#titleLabel {
                font-size: 24px;
                font-weight: bold;
                color: #FFFFFF;
            }
            /* Карточки */
            QFrame#card {
                background-color: #1E1E1E;
                border-radius: 12px;
                border: 1px solid #333333;
            }
            /* Кнопки */
            QPushButton#primaryBtn {
                background-color: #4FC3F7;
                color: #121212;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton#primaryBtn:hover {
                background-color: #29B6F6;
            }
            /* Поля ввода */
            QLineEdit, QTextEdit, QComboBox {
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 8px;
                background-color: #2C2C2C;
                color: #E0E0E0;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 1px solid #4FC3F7;
            }
            /* Прогресс бары */
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
            /* Таблицы */
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
            /* Скроллбары */
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


def set_theme(theme_name):
    """Установить тему (light/dark)"""
    global CURRENT_THEME
    if theme_name in ["light", "dark"]:
        CURRENT_THEME = theme_name


def toggle_theme():
    """Переключить тему на противоположную"""
    global CURRENT_THEME
    CURRENT_THEME = "dark" if CURRENT_THEME == "light" else "light"
    return CURRENT_THEME