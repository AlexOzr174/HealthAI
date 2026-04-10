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
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
Qt.AlignmentFlag.AlignCenter
Qt.AlignmentFlag.AlignLeft
Qt.ScrollBarPolicy.ScrollBarAlwaysOff

# Добавление родительской директории в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import APP_NAME, APP_VERSION, BASE_DIR
from database.init_db import init_database, populate_initial_data
# get_user удален, так как онбординг пока отключен для стабильности
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
    try:
        init_database()
        print("✓ База данных инициализирована")

        # Заполнение начальными данными
        populate_initial_data()
    except Exception as e:
        print(f"⚠️ Ошибка инициализации БД: {e}")

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
    # Используем доступные системные шрифты
    font.setFamily('Arial')
    font.setPointSize(10)
    app.setFont(font)

    # Инициализация базы данных
    is_first_launch = setup_application()

    # Создание и показ главного окна
    try:
        window = MainWindow()
    except Exception as e:
        print(f"CRITICAL ERROR: Не удалось создать главное окно: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # --- ВРЕМЕННО ОТКЛЮЧЕНО: Онбординг ---
    # Логика онбординга требует наличия страницы OnboardingPage в main_window.py
    # и правильной передачи класса, а не строки.
    # Чтобы избежать краша при запуске, этот блок закомментирован.
    # Если онбординг нужен, раскомментируйте после добавления страницы в навигацию.

    # if is_first_launch:
    #     from database.operations import get_user
    #     user = get_user()
    #     if not user:
    #         # Требуется импорт OnboardingPage и добавление его в self.pages в main_window.py
    #         # window.navigate_to(OnboardingPage)
    #         print("ℹ️ Первый запуск: рекомендуется пройти настройку профиля вручную.")

    window.show()

    # Запуск приложения
    print(f"{APP_NAME} запущено. Приятного использования!")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()