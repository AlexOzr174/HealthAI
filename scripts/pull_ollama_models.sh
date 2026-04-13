#!/usr/bin/env bash
# Скачивает модели в каталог проекта: models/ollama (см. .gitignore).
# API Ollama: по умолчанию http://127.0.0.1:11434; здесь OLLAMA_HOST=127.0.0.1:11435 для весов проекта.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
export OLLAMA_MODELS="${OLLAMA_MODELS:-${ROOT}/models/ollama}"
export OLLAMA_HOST="${OLLAMA_HOST:-127.0.0.1:11435}"

mkdir -p "${OLLAMA_MODELS}"

# shellcheck source=install_ollama_if_missing.sh
source "${SCRIPT_DIR}/install_ollama_if_missing.sh"
install_ollama_if_missing

echo "OLLAMA_MODELS=${OLLAMA_MODELS}"
echo "Загрузка qwen2.5:3b (~1.9 GB)..."
ollama pull qwen2.5:3b

echo "Загрузка llama3.2:3b (~2 GB)..."
ollama pull llama3.2:3b

echo "Готово. Список моделей:"
ollama list
