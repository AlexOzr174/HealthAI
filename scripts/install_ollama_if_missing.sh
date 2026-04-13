#!/usr/bin/env bash
# Если CLI ollama отсутствует — официальная установка (macOS/Linux):
#   curl -fsSL https://ollama.com/install.sh | sh
# Документация: https://ollama.com — сервер по умолчанию http://127.0.0.1:11434 (OLLAMA_HOST).

install_ollama_if_missing() {
  if command -v ollama >/dev/null 2>&1; then
    return 0
  fi
  echo "[HealthAI] Команда ollama не найдена в PATH."
  echo "[HealthAI] Ollama по умолчанию слушает localhost:11434 (переменная OLLAMA_HOST)."
  if ! command -v curl >/dev/null 2>&1; then
    echo "[HealthAI] Для автоустановки нужен curl. Вручную: https://ollama.com/download" >&2
    return 1
  fi
  echo "[HealthAI] Установка: curl -fsSL https://ollama.com/install.sh | sh"
  curl -fsSL https://ollama.com/install.sh | sh
  # Добавляем в конец PATH, не в начало — иначе после activate venv системный/Homebrew
  # python окажется раньше venv/bin (см. launch.sh → ensure_ollama_models.sh).
  export PATH="${PATH:-}:/usr/local/bin:/opt/homebrew/bin"
  hash -r 2>/dev/null || true
  if ! command -v ollama >/dev/null 2>&1; then
    echo "[HealthAI] Откройте новый терминал или добавьте /usr/local/bin в PATH." >&2
    return 1
  fi
  echo "[HealthAI] Ollama: $(command -v ollama)"
  return 0
}
