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
from PyQt6.QtGui import QFont

# Добавление родительской директории в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import APP_NAME, APP_VERSION, BASE_DIR
from database.init_db import init_database, populate_initial_data
from database.operations import get_user
from ui.main_window import MainWindow
from ui.pages.onboarding import OnboardingPage


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
    font.setFamily('Arial')
    font.setPointSize(10)
    app.setFont(font)

    # Инициализация базы данных
    is_first_launch = setup_application()

    # Создание главного окна
    try:
        window = MainWindow()
    except Exception as e:
        print(f"CRITICAL ERROR: Не удалось создать главное окно: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Проверка, есть ли пользователь в базе
    user = get_user(1)  # предполагаем, что первый пользователь имеет id=1

    if is_first_launch or not user:
        # Запускаем онбординг
        print("🆕 Запуск онбординга для нового пользователя...")
        onboarding = OnboardingPage(main_window=window)
        onboarding.completed.connect(lambda: finish_onboarding(window))
        onboarding.show()
        # Главное окно пока не показываем
    else:
        # Пользователь уже существует, показываем главное окно
        window.show()

    # Запуск приложения
    print(f"{APP_NAME} запущено. Приятного использования!")
    sys.exit(app.exec())


def finish_onboarding(window: MainWindow):
    """Действия после завершения онбординга"""
    # Обновляем информацию о текущем пользователе в главном окне
    user = get_user(1)  # после сохранения онбордингом пользователь будет с id=1
    if user:
        window.current_user = user
        # Обновляем все страницы
        window.check_user()
    # Показываем главное окно
    window.show()


if __name__ == "__main__":
    main()
