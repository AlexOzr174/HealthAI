# ui/dialog_chrome.py
# Единая светлая «оболочка» для окон, которые иначе наследуют системную тёмную палитру (macOS).
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QWidget


def light_dialog_palette() -> QPalette:
    p = QPalette()
    p.setColor(QPalette.ColorRole.Window, QColor("#F5F7FA"))
    p.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
    p.setColor(QPalette.ColorRole.WindowText, QColor("#2C3E50"))
    p.setColor(QPalette.ColorRole.Text, QColor("#2C3E50"))
    p.setColor(QPalette.ColorRole.Button, QColor("#F5F6F8"))
    p.setColor(QPalette.ColorRole.ButtonText, QColor("#1a1a1a"))
    p.setColor(QPalette.ColorRole.Highlight, QColor("#3498DB"))
    p.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    p.setColor(QPalette.ColorRole.PlaceholderText, QColor("#7F8C8D"))
    return p


def apply_light_dialog_chrome(widget: QWidget) -> None:
    """Палитра + фон через QSS (WA_StyledBackground), чтобы не зависеть от системной тёмной темы."""
    widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    widget.setPalette(light_dialog_palette())


# Общий QSS для модальных форм (QComboBox popup, списки, поля, стандартные кнопки диалога).
STANDARD_LIGHT_FORM_DIALOG_QSS = """
    QDialog {
        background-color: #F5F7FA;
    }
    QDialog > QWidget {
        background-color: transparent;
    }
    QDialog QLabel {
        color: #2C3E50;
        background-color: transparent;
    }
    QDialog QLineEdit {
        background-color: #FFFFFF;
        color: #2C3E50;
        border: 1px solid #BDC3C7;
        border-radius: 6px;
        padding: 8px;
    }
    QDialog QLineEdit:focus {
        border: 1px solid #3498DB;
    }
    QDialog QTextEdit {
        background-color: #FFFFFF;
        color: #2C3E50;
        border: 1px solid #BDC3C7;
        border-radius: 6px;
        padding: 8px;
    }
    QDialog QTextEdit:focus {
        border: 1px solid #3498DB;
    }
    QDialog QComboBox {
        background-color: #FFFFFF;
        color: #2C3E50;
        border: 1px solid #BDC3C7;
        border-radius: 6px;
        padding: 6px 10px;
        padding-right: 30px;
        min-height: 30px;
    }
    QDialog QComboBox:hover {
        border-color: #95A5A6;
    }
    QDialog QComboBox:focus {
        border: 1px solid #3498DB;
    }
    QDialog QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: center right;
        width: 28px;
        border: none;
        border-left: 1px solid #E0E0E0;
        border-top-right-radius: 5px;
        border-bottom-right-radius: 5px;
        background-color: #F0F2F5;
    }
    QDialog QComboBox QAbstractItemView {
        background-color: #FFFFFF;
        color: #2C3E50;
        selection-background-color: #D6EAF8;
        selection-color: #1a1a1a;
        border: 1px solid #BDC3C7;
        border-radius: 6px;
        outline: none;
        padding: 4px;
    }
    QDialog QComboBox QAbstractItemView::item {
        min-height: 28px;
        padding: 6px 10px;
    }
    QDialog QSpinBox, QDialog QDoubleSpinBox {
        background-color: #FFFFFF;
        color: #2C3E50;
        border: 1px solid #BDC3C7;
        border-radius: 6px;
        padding: 6px;
    }
    QDialog QSpinBox:focus, QDialog QDoubleSpinBox:focus {
        border: 1px solid #3498DB;
    }
    QDialog QListWidget {
        background-color: #FFFFFF;
        color: #2C3E50;
        border: 1px solid #BDC3C7;
        border-radius: 6px;
    }
    QDialog QListWidget::item {
        padding: 8px;
    }
    QDialog QListWidget::item:selected {
        background-color: #D6EAF8;
        color: #1a1a1a;
    }
    QDialog QListWidget::item:hover {
        background-color: #EBF5FB;
    }
    QDialog QProgressBar {
        border: 1px solid #BDC3C7;
        border-radius: 6px;
        background-color: #ECEFF1;
        text-align: center;
        color: #2C3E50;
    }
    QDialog QProgressBar::chunk {
        background-color: #3498DB;
        border-radius: 5px;
    }
    QDialog QDialogButtonBox QPushButton {
        color: #1a1a1a;
        background-color: #F5F6F8;
        border: 2px solid #2C3E50;
        border-radius: 8px;
        padding: 8px 18px;
        min-width: 96px;
        min-height: 36px;
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
"""
