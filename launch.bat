@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

if not exist "main.py" (
  echo Ошибка: main.py не найден в %CD%
  pause
  exit /b 1
)

if not exist ".healthai_setup_complete" goto do_setup
if not exist "venv\Scripts\activate.bat" if not exist ".venv\Scripts\activate.bat" goto do_setup
goto after_setup

:do_setup
echo.
echo Первый запуск: установка зависимостей, Ollama и моделей ^(setup.bat^)...
echo.
call "%~dp0setup.bat"
if errorlevel 1 (
  echo [HealthAI] Установка прервана.
  pause
  exit /b 1
)

:after_setup
call "%~dp0scripts\ensure_ollama_models.bat"
if errorlevel 1 (
  echo [HealthAI] Не удалось подготовить Ollama.
  pause
  exit /b 1
)

set "OLLAMA_MODELS=%CD%\models\ollama"
set "OLLAMA_HOST=127.0.0.1:11435"
set "HEALTHAI_OLLAMA_HOST=http://127.0.0.1:11435"

if exist "venv\Scripts\activate.bat" (
  call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
  call .venv\Scripts\activate.bat
)

python main.py %*
set "EXITCODE=%ERRORLEVEL%"
if not "%EXITCODE%"=="0" pause
exit /b %EXITCODE%
