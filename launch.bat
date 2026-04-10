#!/bin/bash

###############################################################################
# HealthAI Launcher для Windows (Batch + PowerShell)
# Версия: 1.0.0
# Описание: Полная проверка окружения, установка зависимостей, загрузка моделей
#           и запуск приложения HealthAI на Windows.
###############################################################################

@echo off
setlocal enabledelayedexpansion

:: Цвета (работают в PowerShell и современных терминалах Windows)
set "BLUE=[INFO]"
set "GREEN=[SUCCESS]"
set "YELLOW=[WARNING]"
set "RED=[ERROR]"
set "CYAN=[STEP]"

:: Конфигурация
set "PROJECT_NAME=HealthAI"
set "PYTHON_VERSION_REQUIRED=3.10"
set "VENV_DIR=venv"
set "REQUIREMENTS_FILE=requirements.txt"
set "MODELS_DIR=ai_engine\models"
set "WEIGHTS_DIR=ml\weights"

echo.
echo ==========================================
echo    %PROJECT_NAME% Launcher для Windows
echo    Версия: 1.0.0
echo ==========================================
echo.

:: Проверка Python
echo %CYAN% Проверка версии Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED% Python не найден. Установите Python 3.10+ из https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo %BLUE% Найдена версия Python: %PYTHON_VERSION%

:: Создание виртуальной среды
echo %CYAN% Проверка виртуальной среды...
if not exist "%VENV_DIR%" (
    echo %BLUE% Виртуальная среда не найдена. Создание...
    python -m venv %VENV_DIR%
    if errorlevel 1 (
        echo %RED% Не удалось создать виртуальную среду.
        pause
        exit /b 1
    )
    echo %GREEN% Виртуальная среда создана.
) else (
    echo %GREEN% Виртуальная среда найдена.
)

:: Активация виртуальной среды
echo %CYAN% Активация виртуальной среды...
call %VENV_DIR%\Scripts\activate.bat
if errorlevel 1 (
    echo %RED% Не удалось активировать виртуальную среду.
    pause
    exit /b 1
)
echo %GREEN% Виртуальная среда активирована.

:: Установка зависимостей
echo %CYAN% Установка зависимостей из %REQUIREMENTS_FILE%...
if not exist "%REQUIREMENTS_FILE%" (
    echo %YELLOW% Файл %REQUIREMENTS_FILE% не найден. Пропускаем установку зависимостей.
    goto :check_integrity
)

python -m pip install --upgrade pip
pip install -r %REQUIREMENTS_FILE%
if errorlevel 1 (
    echo %RED% Ошибка при установке зависимостей.
    pause
    exit /b 1
)
echo %GREEN% Зависимости установлены.

:check_integrity
:: Проверка целостности проекта
echo %CYAN% Проверка целостности проекта...
set "MISSING_FILES="

if not exist "main.py" set "MISSING_FILES=%MISSING_FILES% main.py"
if not exist "ui\main_window.py" set "MISSING_FILES=%MISSING_FILES% ui\main_window.py"
if not exist "database\db_manager.py" set "MISSING_FILES=%MISSING_FILES% database\db_manager.py"

if not "%MISSING_FILES%"=="" (
    echo %RED% Отсутствуют критические файлы:%MISSING_FILES%
    pause
    exit /b 1
)
echo %GREEN% Целостность проекта подтверждена.

:: Создание директорий для моделей
echo %CYAN% Создание директорий для моделей...
if not exist "%MODELS_DIR%" mkdir "%MODELS_DIR%"
if not exist "%WEIGHTS_DIR%" mkdir "%WEIGHTS_DIR%"
echo %GREEN% Директории созданы.

:: Загрузка моделей (демо-режим)
echo %CYAN% Проверка и загрузка моделей ИИ...
set "MODEL_FILE=%MODELS_DIR%\nutritionist_model.pkl"
if not exist "%MODEL_FILE%" (
    echo %YELLOW% Модель не найдена. Создаем демо-модель...
    echo DEMO_MODEL_DATA > "%MODEL_FILE%"
    echo %GREEN% Демо-модель создана: %MODEL_FILE%
) else (
    echo %GREEN% Модель уже существует: %MODEL_FILE%
)

set "WEIGHTS_FILE=%WEIGHTS_DIR%\recommender_weights.h5"
if not exist "%WEIGHTS_FILE%" (
    echo %YELLOW% Веса не найдены. Создаем демо-веса...
    echo DEMO_WEIGHTS_DATA > "%WEIGHTS_FILE%"
    echo %GREEN% Демо-веса созданы: %WEIGHTS_FILE%
) else (
    echo %GREEN% Веса уже существуют: %WEIGHTS_FILE%
)

:: Запуск приложения
echo %CYAN% Запуск приложения %PROJECT_NAME%...
if exist "main.py" (
    python main.py
) else if exist "src\main.py" (
    python src\main.py
) else (
    echo %RED% Главный файл запуска (main.py) не найден.
    pause
    exit /b 1
)

echo.
echo %GREEN% Сеанс работы завершен.
echo ==========================================
pause
