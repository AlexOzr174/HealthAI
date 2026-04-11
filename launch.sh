#!/bin/bash

# ==============================================================================
# HealthAI Launcher for macOS & Linux
# Версия: 2.2 (Полная загрузка конфигураций для NLP и Vision моделей)
# ==============================================================================

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Пути
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_ROOT/.venv"
MODELS_DIR="$PROJECT_ROOT/models"
REQUIREMENTS_FILE="$PROJECT_ROOT/requirements.txt"

# ==============================================================================
# Ссылки на модели и конфигурационные файлы
# ==============================================================================

# 1. NLP модель для чат-бота (sentence-transformers/all-MiniLM-L6-v2)
NLP_MODEL_DIR="$MODELS_DIR/nlp"
# Веса модели
NLP_MODEL_URL="https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/pytorch_model.bin"
NLP_MODEL_PATH="$NLP_MODEL_DIR/pytorch_model.bin"
# Конфигурационные файлы (необходимы для работы модели)
NLP_CONFIG_URL="https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/raw/main/config.json"
NLP_CONFIG_PATH="$NLP_MODEL_DIR/config.json"
NLP_TOKENIZER_URL="https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/raw/main/tokenizer.json"
NLP_TOKENIZER_PATH="$NLP_MODEL_DIR/tokenizer.json"
NLP_TOKENIZER_CONFIG_URL="https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/raw/main/tokenizer_config.json"
NLP_TOKENIZER_CONFIG_PATH="$NLP_MODEL_DIR/tokenizer_config.json"
NLP_MODULES_URL="https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/raw/main/modules.json"
NLP_MODULES_PATH="$NLP_MODEL_DIR/modules.json"
NLP_SENTENCE_CONFIG_URL="https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/raw/main/sentence_bert_config.json"
NLP_SENTENCE_CONFIG_PATH="$NLP_MODEL_DIR/sentence_bert_config.json"
NLP_CONFIG_ST_URL="https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/raw/main/config_sentence_transformers.json"
NLP_CONFIG_ST_PATH="$NLP_MODEL_DIR/config_sentence_transformers.json"
NLP_VOCAB_URL="https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/raw/main/vocab.txt"
NLP_VOCAB_PATH="$NLP_MODEL_DIR/vocab.txt"

# 2. Vision модель для распознавания еды (ResNet-50)
VISION_MODEL_DIR="$MODELS_DIR/vision"
VISION_MODEL_URL="https://download.pytorch.org/models/resnet50-0676ba61.pth"
VISION_MODEL_PATH="$VISION_MODEL_DIR/resnet50.pth"
# Файл с метками классов ImageNet (нужен для интерпретации результатов)
VISION_CLASSES_URL="https://raw.githubusercontent.com/Lasagne/Recipes/master/examples/resnet50/imagenet_classes.txt"
VISION_CLASSES_PATH="$VISION_MODEL_DIR/imagenet_classes.txt"

# Флаги
FORCE_REINSTALL=false
SKIP_MODELS=false

# ==============================================================================
# Функции логирования
# ==============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "\n${CYAN}>>> $1${NC}"
}

# ==============================================================================
# Проверка системы
# ==============================================================================

check_os() {
    log_step "Определение операционной системы..."

    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS_NAME="macOS"
        log_info "Обнаружена система: macOS"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS_NAME="Linux"
        log_info "Обнаружена система: Linux"
    else
        log_warning "Неизвестная ОС: $OSTYPE. Попытка запуска как Linux/macOS."
        OS_NAME="Unknown"
    fi
}

# ==============================================================================
# Проверка Python
# ==============================================================================

check_python() {
    log_step "Проверка версии Python..."

    # Ищем python3
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        # Проверка, что это не python 2
        if python --version 2>&1 | grep -q "Python 3"; then
            PYTHON_CMD="python"
        else
            log_error "Найден Python 2. Требуется Python 3.9+."
            exit 1
        fi
    else
        log_error "Python не найден. Пожалуйста, установите Python 3.9 или выше."
        exit 1
    fi

    VERSION=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    log_info "Найден Python версии: $VERSION"

    # Простая проверка версии (минимум 3.9)
    REQUIRED="3.9"
    if [ "$(printf '%s\n' "$REQUIRED" "$VERSION" | sort -V | head -n1)" != "$REQUIRED" ]; then
        log_error "Требуется Python 3.9+, а у вас $VERSION"
        exit 1
    fi

    log_success "Версия Python подходит."
}

# ==============================================================================
# Виртуальное окружение
# ==============================================================================

setup_venv() {
    log_step "Настройка виртуального окружения..."

    if [ ! -d "$VENV_DIR" ]; then
        log_info "Создание виртуального окружения в .venv..."
        $PYTHON_CMD -m venv "$VENV_DIR"
        if [ $? -ne 0 ]; then
            log_error "Не удалось создать виртуальное окружение."
            exit 1
        fi
        log_success "Виртуальное окружение создано."
    else
        log_info "Виртуальное окружение уже существует."
    fi

    # Активация
    log_info "Активация виртуального окружения..."
    source "$VENV_DIR/bin/activate"

    if [ $? -ne 0 ]; then
        log_error "Не удалось активировать виртуальное окружение."
        exit 1
    fi

    log_success "Виртуальное окружение активно."
}

# ==============================================================================
# Зависимости
# ==============================================================================

install_dependencies() {
    log_step "Установка зависимостей..."

    if [ ! -f "$REQUIREMENTS_FILE" ]; then
        log_warning "Файл requirements.txt не найден. Пропускаем установку пакетов."
        return
    fi

    log_info "Обновление pip..."
    pip install --upgrade pip --quiet

    log_info "Установка пакетов из requirements.txt..."
    # Используем флаги для тихой установки, но показываем ошибки
    pip install -r "$REQUIREMENTS_FILE" --quiet

    if [ $? -eq 0 ]; then
        log_success "Зависимости установлены."
    else
        log_error "Ошибка при установке зависимостей. Проверьте логи выше."
        # Не выходим, пробуем продолжить
    fi
}

# ==============================================================================
# Загрузка моделей и конфигураций
# ==============================================================================

download_file() {
    local url=$1
    local output=$2
    local filename=$(basename "$output")

    log_info "Загрузка: $filename..."

    # Создаем директорию
    mkdir -p "$(dirname "$output")"

    # Пробуем curl, если нет - wget
    if command -v curl &> /dev/null; then
        curl -L -o "$output" "$url" --progress-bar
    elif command -v wget &> /dev/null; then
        wget -O "$output" "$url" --show-progress
    else
        log_error "Не найдены ни curl, ни wget. Невозможно скачать модели."
        return 1
    fi

    if [ $? -eq 0 ] && [ -f "$output" ]; then
        # Проверка размера файла (не должен быть 0 или очень маленьким для html ошибки)
        size=$(stat -f%z "$output" 2>/dev/null || stat -c%s "$output" 2>/dev/null)
        if [ "$size" -lt 1000 ]; then
             log_warning "Файл слишком маленький ($size байт). Возможно, ссылка невалидна."
             return 1
        fi
        log_success "Файл загружен: $output"
        return 0
    else
        log_error "Ошибка загрузки файла."
        return 1
    fi
}

setup_models() {
    log_step "Проверка и загрузка AI моделей и конфигураций..."

    mkdir -p "$NLP_MODEL_DIR"
    mkdir -p "$VISION_MODEL_DIR"

    # --- NLP Модель и конфигурации ---
    log_info "Настройка NLP модели (sentence-transformers/all-MiniLM-L6-v2)..."

    # Основные веса модели
    if [ ! -f "$NLP_MODEL_PATH" ]; then
        log_info "NLP модель не найдена. Начинаем загрузку (~80MB)..."
        download_file "$NLP_MODEL_URL" "$NLP_MODEL_PATH"
        if [ $? -ne 0 ]; then
            log_warning "Не удалось загрузить NLP модель. Приложение запустится в ограниченном режиме."
        fi
    else
        log_success "NLP веса модели уже присутствуют."
    fi

    # Конфигурационные файлы (загружаем, если отсутствуют)
    local nlp_files=(
        "$NLP_CONFIG_URL|$NLP_CONFIG_PATH"
        "$NLP_TOKENIZER_URL|$NLP_TOKENIZER_PATH"
        "$NLP_TOKENIZER_CONFIG_URL|$NLP_TOKENIZER_CONFIG_PATH"
        "$NLP_MODULES_URL|$NLP_MODULES_PATH"
        "$NLP_SENTENCE_CONFIG_URL|$NLP_SENTENCE_CONFIG_PATH"
        "$NLP_CONFIG_ST_URL|$NLP_CONFIG_ST_PATH"
        "$NLP_VOCAB_URL|$NLP_VOCAB_PATH"
    )

    for file_pair in "${nlp_files[@]}"; do
        IFS='|' read -r url path <<< "$file_pair"
        if [ ! -f "$path" ]; then
            download_file "$url" "$path"
        else
            log_success "Файл $(basename "$path") уже присутствует."
        fi
    done

    # --- Vision Модель и классы ---
    log_info "Настройка Vision модели (ResNet-50)..."

    if [ ! -f "$VISION_MODEL_PATH" ]; then
        log_info "Vision модель не найдена. Начинаем загрузку (~100MB)..."
        download_file "$VISION_MODEL_URL" "$VISION_MODEL_PATH"
        if [ $? -ne 0 ]; then
            log_warning "Не удалось загрузить Vision модель. Анализ фото будет недоступен."
        fi
    else
        log_success "Vision модель уже присутствует."
    fi

    # Файл с классами ImageNet
    if [ ! -f "$VISION_CLASSES_PATH" ]; then
        log_info "Файл классов ImageNet не найден. Загружаем..."
        download_file "$VISION_CLASSES_URL" "$VISION_CLASSES_PATH"
        if [ $? -ne 0 ]; then
            log_warning "Не удалось загрузить классы ImageNet. Результаты распознавания могут быть некорректны."
        fi
    else
        log_success "Файл классов ImageNet уже присутствует."
    fi
}

# ==============================================================================
# Запуск приложения
# ==============================================================================

run_app() {
    log_step "Запуск приложения HealthAI..."

    cd "$PROJECT_ROOT"

    # Проверка главного файла
    if [ ! -f "main.py" ]; then
        # Пробуем найти любой файл main.*.py или entry point
        if [ -f "src/main.py" ]; then
            MAIN_FILE="src/main.py"
        elif [ -f "app/main.py" ]; then
            MAIN_FILE="app/main.py"
        else
            log_error "Главный файл приложения (main.py) не найден в корне."
            exit 1
        fi
    else
        MAIN_FILE="main.py"
    fi

    log_info "Запуск $MAIN_FILE..."

    # Запуск с обработкой сигналов
    $PYTHON_CMD "$MAIN_FILE"

    EXIT_CODE=$?
    if [ $EXIT_CODE -ne 0 ]; then
        log_error "Приложение завершилось с кодом ошибки: $EXIT_CODE"
    else
        log_success "Приложение завершено корректно."
    fi
}

# ==============================================================================
# Основная логика
# ==============================================================================

main() {
    echo -e "${CYAN}"
    echo "=========================================="
    echo "   HealthAI Launcher v2.1 (macOS/Linux)   "
    echo "=========================================="
    echo -e "${NC}"

    check_os
    check_python
    setup_venv
    install_dependencies
    setup_models
    run_app

    log_info "Сессия завершена."
}

# Запуск
main "$@"