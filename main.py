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

# Добавление родительской директории в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import APP_NAME, APP_VERSION
from database.init_db import init_database, populate_initial_data
from ui.main_window import MainWindow


def setup_application():
    """Настройка приложения перед запуском"""
    # Инициализация базы данных
    print(f"Инициализация {APP_NAME} v{APP_VERSION}...")
    print("-" * 40)

    # Создание таблиц
    init_database()
    print("✓ База данных инициализирована")

    # Заполнение начальными данными
    populate_initial_data()
    print("✓ Начальные данные загружены")

    print("-" * 40)
    print("Готов к работе!\n")


def main():
    """Главная функция запуска приложения"""
    # Создание приложения
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Используем современный стиль

    # Настройка приложения
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("HealthAI")

    # Инициализация
    setup_application()

    # Создание и показ главного окна
    window = MainWindow()
    window.show()

    # Запуск приложения
    print(f"{APP_NAME} запущено. Приятного использования!")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
