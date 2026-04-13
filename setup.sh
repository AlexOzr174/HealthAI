#!/usr/bin/env bash
# Единая первоначальная установка HealthAI (macOS / Linux):
#   Python venv → pip install → settings.env → Ollama + модели в models/ollama
# Запуск: ./setup.sh   — либо автоматически при первом ./launch.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "${ROOT}"

echo ""
echo "=========================================="
echo "  HealthAI — установка окружения"
echo "=========================================="
echo ""

if ! command -v python3 >/dev/null 2>&1; then
  echo "Ошибка: не найден python3. Установите Python 3.10 или новее." >&2
  exit 1
fi

if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
  echo "Ошибка: нужен Python 3.10 или новее." >&2
  exit 1
fi

VENV_DIR="${ROOT}/venv"
if [ ! -d "${VENV_DIR}" ]; then
  echo "[1/4] Создание виртуального окружения: ${VENV_DIR}"
  python3 -m venv "${VENV_DIR}"
else
  echo "[1/4] Виртуальное окружение уже есть."
fi

# shellcheck source=/dev/null
source "${VENV_DIR}/bin/activate"

echo "[2/4] Установка зависимостей Python (pip)..."
python -m pip install --upgrade pip
# only-if-needed: не перекачивать torch и др. при повторном setup
python -m pip install -r "${ROOT}/requirements.txt" --upgrade-strategy only-if-needed

if [ ! -f "${ROOT}/settings.env" ]; then
  echo "[3/4] Создание settings.env из settings.env.example"
  cp "${ROOT}/settings.env.example" "${ROOT}/settings.env"
else
  echo "[3/4] Файл settings.env уже существует — не перезаписываем."
fi

echo "[4/4] Ollama и модели (локально в models/ollama)..."
chmod +x "${ROOT}/scripts/ensure_ollama_models.sh" 2>/dev/null || true
# shellcheck source=/dev/null
source "${ROOT}/scripts/ensure_ollama_models.sh"

touch "${ROOT}/.healthai_setup_complete"
echo ""
echo "Установка завершена."
echo "Запуск приложения: ./launch.sh"
echo ""
