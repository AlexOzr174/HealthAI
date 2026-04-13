#!/usr/bin/env bash
# Вызывается из launch.sh / launch_linux.sh (source …) или вручную.
# Кладёт веса Ollama в <корень проекта>/models/ollama (см. .gitignore).
#
# Ollama по документации: HTTP API на localhost, по умолчанию 127.0.0.1:11434
# (см. https://ollama.com и FAQ). Переменные: OLLAMA_HOST (bind), OLLAMA_MODELS (каталог весов).
# HealthAI поднимает отдельный процесс на 127.0.0.1:11435 + OLLAMA_MODELS в проекте,
# чтобы не мешать системному Ollama на 11434.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export OLLAMA_MODELS="${ROOT}/models/ollama"
export OLLAMA_HOST="${OLLAMA_HOST:-127.0.0.1:11435}"
export HEALTHAI_OLLAMA_HOST="${HEALTHAI_OLLAMA_HOST:-http://127.0.0.1:11435}"

mkdir -p "${OLLAMA_MODELS}"

# shellcheck source=install_ollama_if_missing.sh
source "$(dirname "${BASH_SOURCE[0]}")/install_ollama_if_missing.sh"
if ! install_ollama_if_missing; then
  exit 1
fi

HOST_ONLY=$(echo "${OLLAMA_HOST}" | cut -d: -f1)
HOST_PORT=$(echo "${OLLAMA_HOST}" | cut -d: -f2)
if [[ -z "$HOST_PORT" || "$HOST_PORT" == "$HOST_ONLY" ]]; then
  HOST_PORT="11435"
fi
if [[ -z "$HOST_ONLY" ]]; then
  HOST_ONLY="127.0.0.1"
fi

_ollama_http_ok() {
  curl -s -o /dev/null -w "%{http_code}" --max-time 3 "http://${HOST_ONLY}:${HOST_PORT}/api/tags" 2>/dev/null | grep -q 200
}

if ! _ollama_http_ok; then
  echo "[HealthAI] Запуск Ollama: OLLAMA_MODELS=${OLLAMA_MODELS} OLLAMA_HOST=${OLLAMA_HOST}"
  # shellcheck disable=SC2091
  ( export OLLAMA_MODELS OLLAMA_HOST; ollama serve >>"${ROOT}/models/ollama-serve.log" 2>&1 & )
  for _ in $(seq 1 15); do
    if _ollama_http_ok; then break; fi
    sleep 1
  done
  if ! _ollama_http_ok; then
    echo "[HealthAI] Не удалось достучаться до http://${HOST_ONLY}:${HOST_PORT} — см. ${ROOT}/models/ollama-serve.log" >&2
    exit 1
  fi
fi

_have_model() {
  local want="$1"
  ollama list 2>/dev/null | awk 'NR>1 {print $1}' | grep -Fxq "$want"
}

for m in qwen2.5:3b llama3.2:3b; do
  if _have_model "$m"; then
    echo "[HealthAI] Модель $m уже загружена."
  else
    echo "[HealthAI] Загрузка $m в ${OLLAMA_MODELS} (первый раз может занять несколько минут)..."
    echo "[HealthAI] После 100% на экране ещё может идти распаковка на диск — без новых строк, это нормально."
    ollama pull "$m"
    echo "[HealthAI] Готово: $m"
  fi
done

echo "[HealthAI] Ollama: ${HEALTHAI_OLLAMA_HOST}, каталог весов: ${OLLAMA_MODELS}"
