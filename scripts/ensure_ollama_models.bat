@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0\.."

rem Ollama по умолчанию: HTTP API на localhost:11434 (OLLAMA_HOST). См. https://ollama.com
rem HealthAI: отдельный порт 11435 и OLLAMA_MODELS в каталоге проекта.

set "ROOT=%CD%"
set "OLLAMA_MODELS=%ROOT%\models\ollama"
set "OLLAMA_HOST=127.0.0.1:11435"
set "HEALTHAI_OLLAMA_HOST=http://127.0.0.1:11435"

if not exist "%OLLAMA_MODELS%" mkdir "%OLLAMA_MODELS%"

if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (
  set "PATH=%LOCALAPPDATA%\Programs\Ollama;%PATH%"
)

where ollama >nul 2>&1
if errorlevel 1 (
  echo [HealthAI] Ollama не найдена. Официальный API по умолчанию: http://127.0.0.1:11434
  echo [HealthAI] Запуск установщика: irm https://ollama.com/install.ps1 ^| iex
  powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://ollama.com/install.ps1 | iex"
  if errorlevel 1 (
    echo [HealthAI] Установите вручную: https://ollama.com/download
    exit /b 1
  )
  timeout /t 3 /nobreak >nul
  if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" set "PATH=%LOCALAPPDATA%\Programs\Ollama;%PATH%"
)

where ollama >nul 2>&1
if errorlevel 1 (
  echo [HealthAI] Перезапустите терминал после установки Ollama и запустите launch.bat снова.
  exit /b 1
)

curl -s -o nul --max-time 3 http://127.0.0.1:11435/api/tags 2>nul
if errorlevel 1 (
  echo [HealthAI] Запуск Ollama: OLLAMA_MODELS=%OLLAMA_MODELS% OLLAMA_HOST=%OLLAMA_HOST%
  start /B ollama serve >> "%ROOT%\models\ollama-serve.log" 2>&1
  timeout /t 4 /nobreak >nul
)

echo [HealthAI] Проверка моделей Ollama в %OLLAMA_MODELS% ...
echo [HealthAI] После 100%% может идти распаковка без новых строк — это нормально.
echo [HealthAI] Загрузка qwen2.5:3b ...
ollama pull qwen2.5:3b
if errorlevel 1 (
  echo [HealthAI] Ошибка загрузки qwen2.5:3b
  exit /b 1
)
echo [HealthAI] Готово: qwen2.5:3b
echo [HealthAI] Загрузка llama3.2:3b ...
ollama pull llama3.2:3b
if errorlevel 1 (
  echo [HealthAI] Ошибка загрузки llama3.2:3b
  exit /b 1
)
echo [HealthAI] Готово: llama3.2:3b

echo [HealthAI] Ollama: %HEALTHAI_OLLAMA_HOST%
