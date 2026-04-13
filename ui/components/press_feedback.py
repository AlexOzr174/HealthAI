# ui/components/press_feedback.py — лёгкая визуальная отдача при нажатии кнопки
from __future__ import annotations

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QAbstractAnimation
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QPushButton


def attach_press_flash(button: QPushButton) -> None:
    """Краткое «вспыхивание» прозрачности при нажатии (дополняет QSS :pressed)."""

    def on_pressed() -> None:
        eff = QGraphicsOpacityEffect(button)
        button.setGraphicsEffect(eff)
        anim = QPropertyAnimation(eff, b"opacity")
        anim.setDuration(160)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.setStartValue(1.0)
        anim.setKeyValueAt(0.4, 0.82)
        anim.setEndValue(1.0)

        def cleanup() -> None:
            button.setGraphicsEffect(None)

        anim.finished.connect(cleanup)
        anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

    button.pressed.connect(on_pressed)
