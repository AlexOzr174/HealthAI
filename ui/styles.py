# Стили и темы для интерфейса HealthAI
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QPushButton, QLineEdit, QLabel, QComboBox, QTextEdit


# Цветовая палитра
COLORS = {
    'primary': '#2E7D32',           # Медицинский зелёный
    'primary_light': '#81C784',     # Светло-зелёный
    'primary_dark': '#1B5E20',      # Тёмно-зелёный
    'primary_hover': '#388E3C',     # Зелёный при наведении
    'secondary': '#FF7043',         # Оранжевый для акцентов
    'secondary_light': '#FFAB91',   # Светло-оранжевый
    'background': '#F5F7FA',        # Светло-серый фон
    'surface': '#FFFFFF',           # Белый для карточек
    'error': '#E53935',             # Красный для ошибок
    'error_light': '#FFCDD2',       # Светло-красный для фона
    'warning': '#FFA726',           # Оранжевый для предупреждений
    'warning_light': '#FFE0B2',     # Светло-оранжевый для фона
    'success': '#66BB6A',           # Зелёный для успеха
    'success_light': '#C8E6C9',     # Светло-зелёный для фона
    'text_primary': '#212121',      # Основной текст
    'text_secondary': '#757575',     # Вторичный текст
    'text_hint': '#9E9E9E',         # Текст-подсказка
    'border': '#E0E0E0',            # Границы элементов
    'border_focus': '#2E7D32',      # Граница при фокусе
    'divider': '#BDBDBD',           # Разделитель
    'shadow': '#40000000',          # Тень
}

# Размеры шрифтов
FONTS = {
    'h1': 24,
    'h2': 18,
    'h3': 16,
    'body': 14,
    'caption': 12,
    'small': 10,
}


def get_stylesheet() -> str:
    """
    Получение полной таблицы стилей для приложения.

    Returns:
        CSS стили в виде строки
    """
    return f"""
/* === Глобальные стили === */
QMainWindow {{
    background-color: {COLORS['background']};
    font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
    font-size: {FONTS['body']}px;
    color: {COLORS['text_primary']};
}}

QWidget {{
    background-color: transparent;
    color: {COLORS['text_primary']};
}}

/* === Кнопки === */
QPushButton {{
    background-color: {COLORS['primary']};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: {FONTS['body']}px;
    font-weight: 500;
    min-height: 40px;
    min-width: 100px;
}}

QPushButton:hover {{
    background-color: {COLORS['primary_hover']};
}}

QPushButton:pressed {{
    background-color: {COLORS['primary_dark']};
}}

QPushButton:disabled {{
    background-color: {COLORS['border']};
    color: {COLORS['text_hint']};
}}

QPushButton.secondary {{
    background-color: {COLORS['secondary']};
}}

QPushButton.secondary:hover {{
    background-color: #F4511E;
}}

QPushButton.outline {{
    background-color: transparent;
    border: 2px solid {COLORS['primary']};
    color: {COLORS['primary']};
}}

QPushButton.outline:hover {{
    background-color: {COLORS['primary_light']};
    color: white;
}}

QPushButton.icon-button {{
    background-color: transparent;
    border: none;
    min-width: 36px;
    min-height: 36px;
    border-radius: 18px;
}}

QPushButton.icon-button:hover {{
    background-color: {COLORS['background']};
}}

/* === Поля ввода === */
QLineEdit, QTextEdit {{
    background-color: {COLORS['surface']};
    border: 2px solid {COLORS['border']};
    border-radius: 8px;
    padding: 10px 12px;
    font-size: {FONTS['body']}px;
    selection-background-color: {COLORS['primary_light']};
}}

QLineEdit:focus, QTextEdit:focus {{
    border-color: {COLORS['border_focus']};
}}

QLineEdit:disabled, QTextEdit:disabled {{
    background-color: {COLORS['background']};
    color: {COLORS['text_hint']};
}}

/* === Выпадающие списки === */
QComboBox {{
    background-color: {COLORS['surface']};
    border: 2px solid {COLORS['border']};
    border-radius: 8px;
    padding: 10px 12px;
    font-size: {FONTS['body']}px;
    min-height: 40px;
}}

QComboBox:focus {{
    border-color: {COLORS['border_focus']};
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox::down-arrow {{
    image: none;
    border: none;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['surface']};
    border: 2px solid {COLORS['border']};
    border-radius: 8px;
    selection-background-color: {COLORS['primary_light']};
    padding: 4px;
}}

/* === Метки (Labels) === */
QLabel {{
    color: {COLORS['text_primary']};
}}

QLabel.h1 {{
    font-size: {FONTS['h1']}px;
    font-weight: bold;
    color: {COLORS['primary_dark']};
}}

QLabel.h2 {{
    font-size: {FONTS['h2']}px;
    font-weight: bold;
    color: {COLORS['text_primary']};
}}

QLabel.h3 {{
    font-size: {FONTS['h3']}px;
    font-weight: 600;
    color: {COLORS['text_primary']};
}}

QLabel.caption {{
    font-size: {FONTS['caption']}px;
    color: {COLORS['text_secondary']};
}}

QLabel.error {{
    color: {COLORS['error']};
    font-size: {FONTS['caption']}px;
}}

QLabel.success {{
    color: {COLORS['success']};
}}

QLabel.warning {{
    color: {COLORS['warning']};
}}

/* === Прогресс-бары === */
QProgressBar {{
    background-color: {COLORS['background']};
    border: none;
    border-radius: 6px;
    height: 20px;
    text-align: center;
    font-size: {FONTS['caption']}px;
    font-weight: 600;
}}

QProgressBar::chunk {{
    background-color: {COLORS['primary']};
    border-radius: 6px;
}}

QProgressBar.warning::chunk {{
    background-color: {COLORS['warning']};
}}

QProgressBar.danger::chunk {{
    background-color: {COLORS['error']};
}}

/* === Список виджетов === */
QListWidget {{
    background-color: transparent;
    border: none;
    outline: none;
}}

QListWidget::item {{
    background-color: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 8px;
}}

QListWidget::item:selected {{
    background-color: {COLORS['primary_light']};
    border-color: {COLORS['primary']};
}}

/* === Вкладки === */
QTabWidget::pane {{
    background-color: transparent;
    border: none;
}}

QTabBar::tab {{
    background-color: transparent;
    border: none;
    padding: 12px 20px;
    font-size: {FONTS['body']}px;
    color: {COLORS['text_secondary']};
}}

QTabBar::tab:selected {{
    color: {COLORS['primary']};
    border-bottom: 3px solid {COLORS['primary']};
}}

QTabBar::tab:hover:!selected {{
    color: {COLORS['primary_dark']};
}}

/* === Панели и фреймы === */
QFrame.card {{
    background-color: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
    padding: 16px;
}}

QFrame.card:hover {{
    border-color: {COLORS['primary_light']};
}}

/* === Скроллбары === */
QScrollBar:vertical {{
    background-color: transparent;
    width: 8px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['border']};
    border-radius: 4px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['text_secondary']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    background: none;
    border: none;
}}

/* === Специфические компоненты === */

/* Карточка рецепта */
.recipe-card {{
    background-color: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
    padding: 16px;
}}

.recipe-card:hover {{
    border-color: {COLORS['primary_light']};
    background-color: {COLORS['primary_light']}15;
}}

/* Карточка достижения */
.achievement-card {{
    background-color: {COLORS['surface']};
    border: 2px solid {COLORS['border']};
    border-radius: 12px;
    padding: 12px;
    min-width: 100px;
}}

.achievement-card.unlocked {{
    border-color: {COLORS['warning']};
    background-color: {COLORS['warning_light']}30;
}}

.achievement-card.locked {{
    opacity: 0.5;
}}

/* Статистическая карточка */
.stat-card {{
    background-color: {COLORS['surface']};
    border-radius: 12px;
    padding: 16px;
    min-width: 120px;
}}

.stat-card.calories {{
    border-left: 4px solid {COLORS['primary']};
}}

.stat-card.protein {{
    border-left: 4px solid {COLORS['error']};
}}

.stat-card.fat {{
    border-left: 4px solid {COLORS['warning']};
}}

.stat-card.carbs {{
    border-left: 4px solid {COLORS['secondary']};
}}

/* Индикатор прогресса дня */
.day-progress {{
    background-color: {COLORS['background']};
    border-radius: 50px;
    height: 12px;
}}

.day-progress::chunk {{
    border-radius: 50px;
}}

/* Тег диеты */
.diet-tag {{
    background-color: {COLORS['primary_light']};
    color: {COLORS['primary_dark']};
    border-radius: 4px;
    padding: 4px 8px;
    font-size: {FONTS['small']}px;
}}

.diet-tag.forbidden {{
    background-color: {COLORS['error_light']};
    color: {COLORS['error']};
}}
"""


def get_button_style(variant: str = 'primary') -> str:
    """
    Получение стиля кнопки определённого типа.

    Args:
        variant: Тип кнопки ('primary', 'secondary', 'outline', 'danger')

    Returns:
        CSS стиль кнопки
    """
    variants = {
        'primary': f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{ background-color: {COLORS['primary_hover']}; }}
        """,
        'secondary': f"""
            QPushButton {{
                background-color: {COLORS['secondary']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{ background-color: #F4511E; }}
        """,
        'outline': f"""
            QPushButton {{
                background-color: transparent;
                border: 2px solid {COLORS['primary']};
                color: {COLORS['primary']};
                border-radius: 8px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_light']};
                color: white;
            }}
        """,
        'danger': f"""
            QPushButton {{
                background-color: {COLORS['error']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{ background-color: #C62828; }}
        """,
    }
    return variants.get(variant, variants['primary'])


def get_card_style() -> str:
    """Получение стиля карточки"""
    return f"""
        QFrame {{
            background-color: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            padding: 16px;
        }}
    """


def get_progress_bar_style(color: str = 'primary') -> str:
    """
    Получение стиля прогресс-бара.

    Args:
        color: Цвет ('primary', 'warning', 'danger')
    """
    colors = {
        'primary': COLORS['primary'],
        'warning': COLORS['warning'],
        'danger': COLORS['error'],
    }
    bar_color = colors.get(color, COLORS['primary'])

    return f"""
        QProgressBar {{
            background-color: {COLORS['background']};
            border: none;
            border-radius: 6px;
            height: 16px;
            text-align: center;
        }}
        QProgressBar::chunk {{
            background-color: {bar_color};
            border-radius: 6px;
        }}
    """


class IconSize:
    """Размеры иконок для разных элементов"""
    SMALL = QSize(16, 16)
    MEDIUM = QSize(24, 24)
    LARGE = QSize(32, 32)
    XLARGE = QSize(48, 48)
    AVATAR = QSize(64, 64)
    TILE = QSize(96, 96)
