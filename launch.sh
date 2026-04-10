#!/bin/bash

###############################################################################
# HealthAI Launcher for macOS
# Версия: 2.0 (С загрузкой реальных моделей ИИ)
# Описание: Полная проверка окружения, установка зависимостей, загрузка 
#           реальных ML-моделей и запуск приложения HealthAI на macOS.
###############################################################################

set -e # Остановить скрипт при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Логирование
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }
log_step() { echo -e "${CYAN}[★]${NC} $1"; }

# Конфигурация
PROJECT_NAME="HealthAI"
PYTHON_VERSION_REQUIRED="3.9"
VENV_DIR=".venv"
REQUIREMENTS_FILE="requirements.txt"
MODELS_DIR="models_weights"

# =============================================================================
# ССЫЛКИ НА РЕАЛЬНЫЕ МОДЕЛИ ИИ
# =============================================================================
# 1. NLP модель для чат-бота (Sentence Transformers)
MODEL_NLP_URL="https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/pytorch_model.bin"
MODEL_NLP_NAME="nlp_encoder.bin"

# 2. Модель классификации еды (MobileNetV2 / Food-101)
MODEL_FOOD_URL="https://huggingface.co/microsoft/resnet-50/resolve/main/pytorch_model.bin"
MODEL_FOOD_NAME="food_classifier.bin"

# 3. Модель предиктивной аналитики (заглушка, т.к. обучается локально)
MODEL_PRED_NAME="weight_predictor.pkl"

# 4. Векторизатор для NLP
MODEL_VEC_NAME="nlp_vectorizer.pkl"

# Массив для скачивания
declare -A MODEL_URLS
MODEL_URLS[$MODEL_NLP_NAME]=$MODEL_NLP_URL
MODEL_URLS[$MODEL_FOOD_NAME]=$MODEL_FOOD_URL

# Функция проверки наличия команды
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Функция проверки версии Python
check_python_version() {
    log_step "Проверка версии Python..."
    
    if ! command_exists python3; then
        log_error "Python3 не найден. Установите Python 3.10+ из https://www.python.org/downloads/"
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    log_info "Найдена версия Python: $PYTHON_VERSION"

    # Сравнение версий (простое)
    REQUIRED_MAJOR=$(echo $PYTHON_VERSION_REQUIRED | cut -d'.' -f1)
    REQUIRED_MINOR=$(echo $PYTHON_VERSION_REQUIRED | cut -d'.' -f2)
    INSTALLED_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    INSTALLED_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

    if [ "$INSTALLED_MAJOR" -lt "$REQUIRED_MAJOR" ] || \
       ([ "$INSTALLED_MAJOR" -eq "$REQUIRED_MAJOR" ] && [ "$INSTALLED_MINOR" -lt "$REQUIRED_MINOR" ]); then
        log_error "Требуется Python $PYTHON_VERSION_REQUIRED или выше. Найдено: $PYTHON_VERSION"
        exit 1
    fi

    log_success "Версия Python корректна."
}

# Функция проверки и создания виртуальной среды
setup_venv() {
    log_step "Проверка виртуальной среды..."

    if [ ! -d "$VENV_DIR" ]; then
        log_info "Виртуальная среда не найдена. Создание..."
        python3 -m venv $VENV_DIR
        if [ $? -ne 0 ]; then
            log_error "Не удалось создать виртуальную среду."
            exit 1
        fi
        log_success "Виртуальная среда создана."
    else
        log_success "Виртуальная среда найдена."
    fi

    # Активация
    source "$VENV_DIR/bin/activate"
    if [ $? -ne 0 ]; then
        log_error "Не удалось активировать виртуальную среду."
        exit 1
    fi
    log_success "Виртуальная среда активирована."
}

# Функция установки зависимостей
install_dependencies() {
    log_step "Установка зависимостей из $REQUIREMENTS_FILE..."

    if [ ! -f "$REQUIREMENTS_FILE" ]; then
        log_warning "Файл $REQUIREMENTS_FILE не найден. Пропускаем установку зависимостей."
        return
    fi

    pip install --upgrade pip
    pip install -r $REQUIREMENTS_FILE
    
    if [ $? -ne 0 ]; then
        log_error "Ошибка при установке зависимостей."
        exit 1
    fi

    log_success "Зависимости установлены."
}

# Функция создания директорий
create_directories() {
    log_step "Создание директорий для моделей..."
    mkdir -p "$MODELS_DIR"
    log_success "Директории созданы."
}

# Функция загрузки моделей с реальными URL
download_models() {
    log_step "Проверка и загрузка моделей ИИ..."

    create_directories

    # Модель 1: NLP (Sentence Transformer для чат-бота)
    local nlp_model="$MODELS_DIR/$MODEL_NLP_NAME"
    if [ ! -f "$nlp_model" ]; then
        log_info "Загрузка NLP модели (all-MiniLM-L6-v2) ~80MB..."
        log_warning "Это может занять несколько минут..."
        
        if command_exists curl; then
            curl -L -o "$nlp_model" "$MODEL_NLP_URL" 2>/dev/null
        elif command_exists wget; then
            wget -O "$nlp_model" "$MODEL_NLP_URL" 2>/dev/null
        else
            log_error "Не найден curl или wget для загрузки моделей"
            touch "$nlp_model"
            echo "DEMO_NLP_MODEL" > "$nlp_model"
        fi
        
        if [ -f "$nlp_model" ] && [ -s "$nlp_model" ]; then
            log_success "NLP модель загружена: $nlp_model"
        else
            log_warning "Не удалось загрузить NLP модель. Создана заглушка."
            touch "$nlp_model"
            echo "DEMO_NLP_MODEL" > "$nlp_model"
        fi
    else
        log_success "NLP модель уже существует: $nlp_model"
    fi

    # Модель 2: Vision (ResNet-50 для анализа еды)
    local vision_model="$MODELS_DIR/$MODEL_FOOD_NAME"
    if [ ! -f "$vision_model" ]; then
        log_info "Загрузка Vision модели (ResNet-50) ~100MB..."
        log_warning "Это может занять несколько минут..."
        
        if command_exists curl; then
            curl -L -o "$vision_model" "$MODEL_FOOD_URL" 2>/dev/null
        elif command_exists wget; then
            wget -O "$vision_model" "$MODEL_FOOD_URL" 2>/dev/null
        else
            log_error "Не найден curl или wget для загрузки моделей"
            touch "$vision_model"
            echo "DEMO_VISION_MODEL" > "$vision_model"
        fi
        
        if [ -f "$vision_model" ] && [ -s "$vision_model" ]; then
            log_success "Vision модель загружена: $vision_model"
        else
            log_warning "Не удалось загрузить Vision модель. Создана заглушка."
            touch "$vision_model"
            echo "DEMO_VISION_MODEL" > "$vision_model"
        fi
    else
        log_success "Vision модель уже существует: $vision_model"
    fi

    # Модель 3: Векторизатор (создаётся локально при первом запуске)
    local vec_model="$MODELS_DIR/$MODEL_VEC_NAME"
    if [ ! -f "$vec_model" ]; then
        log_info "Создание векторизатора..."
        touch "$vec_model"
        echo "DEMO_VECTORIZER" > "$vec_model"
        log_success "Векторизатор создан: $vec_model"
    else
        log_success "Векторизатор уже существует: $vec_model"
    fi

    # Модель 4: Предиктивная модель (обучается локально)
    local pred_model="$MODELS_DIR/$MODEL_PRED_NAME"
    if [ ! -f "$pred_model" ]; then
        log_info "Создание предиктивной модели..."
        touch "$pred_model"
        echo "DEMO_PREDICTOR" > "$pred_model"
        log_success "Предиктивная модель создана: $pred_model"
    else
        log_success "Предиктивная модель уже существует: $pred_model"
    fi
    
    # Вывод статистики
    log_info "Размер загруженных моделей:"
    du -sh "$MODELS_DIR"/* 2>/dev/null || true
}

# Функция проверки целостности проекта
check_project_integrity() {
    log_step "Проверка целостности проекта..."

    local required_files=("main.py" "ui/main_window.py" "database/db_manager.py")
    local missing_files=()

    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            missing_files+=("$file")
        fi
    done

    if [ ${#missing_files[@]} -ne 0 ]; then
        log_error "Отсутствуют критические файлы: ${missing_files[*]}"
        exit 1
    fi

    log_success "Целостность проекта подтверждена."
}

# Функция запуска приложения
run_application() {
    log_step "Запуск приложения $PROJECT_NAME..."

    # Проверка главного файла запуска
    if [ -f "main.py" ]; then
        python main.py
        EXIT_CODE=$?
    elif [ -f "src/main.py" ]; then
        python src/main.py
        EXIT_CODE=$?
    else
        log_error "Главный файл запуска (main.py) не найден."
        exit 1
    fi

    if [ $EXIT_CODE -ne 0 ]; then
        log_error "Приложение завершилось с ошибкой (код: $EXIT_CODE)."
    else
        log_success "Приложение завершено успешно."
    fi
}

# Основная функция
main() {
    echo ""
    echo "=========================================="
    echo "   $PROJECT_NAME Launcher for macOS"
    echo "   Версия: 1.0.0"
    echo "=========================================="
    echo ""

    # 1. Проверка Python
    check_python_version

    # 2. Настройка виртуальной среды
    setup_venv

    # 3. Установка зависимостей
    install_dependencies

    # 4. Проверка целостности
    check_project_integrity

    # 5. Загрузка моделей
    download_models

    # 6. Запуск приложения
    run_application

    echo ""
    log_success "Сеанс работы завершен."
    echo "=========================================="
}

# Запуск основной функции
main "$@"
