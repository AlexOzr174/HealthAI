@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

echo.
echo ==========================================
echo   HealthAI - установка окружения
echo ==========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
  echo Ошибка: установите Python 3.10+ с https://www.python.org/downloads/
  pause
  exit /b 1
)

if not exist "venv" (
  echo [1/4] Создание виртуального окружения venv...
  python -m venv venv
  if errorlevel 1 (
    echo Не удалось создать venv.
    pause
    exit /b 1
  )
) else (
  echo [1/4] Папка venv уже есть.
)

call venv\Scripts\activate.bat
if errorlevel 1 (
  echo Не удалось активировать venv.
  pause
  exit /b 1
)

echo [2/4] Установка зависимостей Python...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt --upgrade-strategy only-if-needed
if errorlevel 1 (
  echo Ошибка pip install.
  pause
  exit /b 1
)

if not exist "settings.env" (
  echo [3/4] Создание settings.env из примера...
  copy /Y settings.env.example settings.env >nul
) else (
  echo [3/4] settings.env уже существует.
)

echo [4/4] Ollama и модели...
call "%~dp0scripts\ensure_ollama_models.bat"
if errorlevel 1 (
  echo Ошибка подготовки Ollama.
  pause
  exit /b 1
)

echo.> ".healthai_setup_complete"
echo.
echo Установка завершена. Запуск: launch.bat
echo.
exit /b 0
