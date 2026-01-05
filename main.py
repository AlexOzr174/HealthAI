#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HealthAI - Умный гид по здоровому питанию

Десктопное приложение для отслеживания питания,
планирования рациона и получения персональных рекомендаций.

Автор: HealthAI Team
Версия: 1.0.0
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
# from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont # QIcon

# Добавление родительской директории в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import APP_NAME, APP_VERSION, BASE_DIR
from database.init_db import init_database, populate_initial_data, get_engine
from database.operations import get_user
from ui.main_window import MainWindow


def check_first_launch():
    """Проверка первого запуска приложения"""
    db_path = os.path.join(BASE_DIR, 'database', 'healthai.db')
    is_first_launch = not os.path.exists(db_path)

    if is_first_launch:
        print("🆕 Первый запуск приложения...")
    else:
        print("🔄 Повторный запуск приложения...")

    return is_first_launch


def setup_application():
    """Настройка приложения перед запуском"""
    print(f"Инициализация {APP_NAME} v{APP_VERSION}...")
    print("-" * 40)

    # Проверяем первый запуск
    is_first_launch = check_first_launch()

    # Создание таблиц базы данных
    engine = init_database()
    print("✓ База данных инициализирована")

    # Заполнение начальными данными
    populate_initial_data()

    print("-" * 40)
    print("Готов к работе!\n")

    return is_first_launch


def main():
    """Главная функция запуска приложения"""
    # Создание приложения
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Используем современный стиль

    # Настройка приложения
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("HealthAI")

    # Настройка шрифтов для лучшей читаемости
    font = QFont()
    font.setFamily('Segoe UI, Roboto, Arial, sans-serif')
    font.setPointSize(10)
    app.setFont(font)

    # Инициализация базы данных
    is_first_launch = setup_application()

    # Создание и показ главного окна
    window = MainWindow()

    # Если первый запуск - показываем онбординг
    if is_first_launch:
        user = get_user()
        if not user:
            window.navigate_to("onboarding")

    window.show()

    # Запуск приложения
    print(f"{APP_NAME} запущено. Приятного использования!")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
