#!/usr/bin/env bash
# Запуск HealthAI (Linux): см. launch.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "${SCRIPT_DIR}"

if [ ! -f "${SCRIPT_DIR}/main.py" ]; then
  echo "Ошибка: main.py не найден в ${SCRIPT_DIR}"
  exit 1
fi

_needs_first_time_setup() {
  if [ ! -f "${SCRIPT_DIR}/.healthai_setup_complete" ]; then
    return 0
  fi
  if [ ! -d "${SCRIPT_DIR}/venv" ] && [ ! -d "${SCRIPT_DIR}/.venv" ]; then
    return 0
  fi
  return 1
}

if _needs_first_time_setup; then
  echo ""
  echo "Первый запуск: установка зависимостей, Ollama и моделей (./setup.sh)..."
  echo ""
  bash "${SCRIPT_DIR}/setup.sh" || exit 1
fi

chmod +x "${SCRIPT_DIR}/main.py" 2>/dev/null || true
chmod +x "${SCRIPT_DIR}/setup.sh" 2>/dev/null || true
chmod +x "${SCRIPT_DIR}/scripts/ensure_ollama_models.sh" 2>/dev/null || true

PYTHON_BIN=""
if [ -x "${SCRIPT_DIR}/venv/bin/python3" ]; then
  PYTHON_BIN="${SCRIPT_DIR}/venv/bin/python3"
  # shellcheck source=/dev/null
  source "${SCRIPT_DIR}/venv/bin/activate"
elif [ -x "${SCRIPT_DIR}/.venv/bin/python3" ]; then
  PYTHON_BIN="${SCRIPT_DIR}/.venv/bin/python3"
  # shellcheck source=/dev/null
  source "${SCRIPT_DIR}/.venv/bin/activate"
fi

# shellcheck source=/dev/null
source "${SCRIPT_DIR}/scripts/ensure_ollama_models.sh"

if [ -n "${PYTHON_BIN}" ]; then
  exec "${PYTHON_BIN}" "${SCRIPT_DIR}/main.py" "$@"
fi
exec python3 "${SCRIPT_DIR}/main.py" "$@"
