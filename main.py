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

from ui.styles import Styles, sync_config_colors_with_theme, set_theme, apply_app_light_palette

# Добавление родительской директории в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.app_logging import setup_logging

setup_logging()

import logging

_log = logging.getLogger(__name__)

from core.config import apply_default_ollama_env, describe_model_paths
from core.qt_lifecycle import (
    exit_after_qt_exec,
    pyqt6_disable_sip_destroy_on_exit,
    qt_safe_teardown,
)

apply_default_ollama_env()

from config.settings import APP_NAME, APP_VERSION, BASE_DIR, APP_ICON_PATH
from database.init_db import init_database, populate_initial_data
from database.operations import get_user

# MainWindow и OnboardingPage НЕ импортировать на уровне модуля: внутри тянется
# страница «Аналитика» с matplotlib/Qt — бэкенд требует существующий QApplication (иначе segfault на macOS).


def check_first_launch():
    """Проверка первого запуска приложения"""
    db_path = os.path.join(BASE_DIR, 'database', 'healthai.db')
    is_first_launch = not os.path.exists(db_path)

    if is_first_launch:
        _log.info("Первый запуск приложения")
    else:
        _log.info("Повторный запуск приложения")

    return is_first_launch


def setup_application():
    """Настройка приложения перед запуском"""
    _log.info("Инициализация %s v%s", APP_NAME, APP_VERSION)

    # Проверяем первый запуск
    is_first_launch = check_first_launch()

    # Создание таблиц базы данных
    try:
        init_database()
        _log.info("База данных инициализирована")

        # Заполнение начальными данными
        populate_initial_data()
    except Exception as e:
        _log.exception("Ошибка инициализации БД: %s", e)
        _log.error("Приложение не может работать без базы данных. Завершение.")
        sys.exit(1)

    _log.info("Пути моделей:\n%s", describe_model_paths())
    _log.info("Готов к работе")

    return is_first_launch


def main():
    """Главная функция запуска приложения"""
    # Несколько нативных библиотек (numpy/OpenMP, torch) на macOS иногда конфликтуют и падают при старте.
    os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
    os.environ.setdefault("OMP_NUM_THREADS", "1")

    # Единый стиль диалогов (иначе на macOS QMessageBox может быть «нативным» с плохим контрастом)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_DontUseNativeDialogs, True)
    # Создание приложения
    app = QApplication(sys.argv)
    pyqt6_disable_sip_destroy_on_exit()
    app.setStyle('Fusion')  # Используем современный стиль

    # Единая светлая тема (на macOS иначе системная тёмная палитра портит выпадающие списки и popup)
    set_theme('light')
    sync_config_colors_with_theme()
    apply_app_light_palette(app)
    app.setStyleSheet(Styles.get_stylesheet())

    # Настройка приложения
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("HealthAI")

    if os.path.isfile(APP_ICON_PATH):
        app.setWindowIcon(QIcon(APP_ICON_PATH))

    # Настройка шрифтов для лучшей читаемости
    font = QFont()
    font.setFamily('Arial')
    font.setPointSize(10)
    app.setFont(font)

    # Инициализация базы данных
    is_first_launch = setup_application()

    from ui.main_window import MainWindow
    from ui.pages.onboarding import OnboardingPage

    # Создание главного окна
    try:
        window = MainWindow()
    except Exception as e:
        _log.critical("Не удалось создать главное окно: %s", e, exc_info=True)
        sys.exit(1)

    # Проверка, есть ли пользователь в базе
    user = get_user(1)  # предполагаем, что первый пользователь имеет id=1

    if is_first_launch or not user:
        # Запускаем онбординг
        _log.info("Запуск онбординга для нового пользователя")
        onboarding = OnboardingPage(main_window=window)
        onboarding.completed.connect(lambda: finish_onboarding(window))
        onboarding.show()
        # Главное окно пока не показываем
    else:
        # Пользователь уже существует, показываем главное окно
        window.show()

    # Остановку потоков чата и ML — в MainWindow.closeEvent (пока виджеты ещё живы).
    # aboutToQuit: только «сухая» уборка без обращения к окнам (иначе use-after-free).

    app.aboutToQuit.connect(qt_safe_teardown)

    # Запуск приложения
    _log.info("%s запущено", APP_NAME)
    rc = app.exec()
    # После return из exec цикл Qt уже остановлен; см. core.qt_lifecycle.exit_after_qt_exec
    exit_after_qt_exec(rc)


def finish_onboarding(window: "MainWindow"):
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
