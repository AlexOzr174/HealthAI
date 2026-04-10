#!/bin/bash

###############################################################################
# HealthAI Launcher для Linux
# Версия: 1.0.0
# Описание: Полная проверка окружения, установка зависимостей, загрузка моделей
#           и запуск приложения HealthAI на Linux.
###############################################################################

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Логирование
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${CYAN}[STEP]${NC} $1"; }

# Конфигурация
PROJECT_NAME="HealthAI"
PYTHON_VERSION_REQUIRED="3.10"
VENV_DIR="venv"
REQUIREMENTS_FILE="requirements.txt"
MODELS_DIR="ai_engine/models"
WEIGHTS_DIR="ml/weights"

# Функция проверки наличия команды
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Функция проверки версии Python
check_python_version() {
    log_step "Проверка версии Python..."
    
    if ! command_exists python3; then
        log_error "Python3 не найден. Установите Python 3.10+ (apt install python3 python3-venv python3-pip)"
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    log_info "Найдена версия Python: $PYTHON_VERSION"

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
            log_error "Не удалось создать виртуальную среду. Установите: apt install python3-venv"
            exit 1
        fi
        log_success "Виртуальная среда создана."
    else
        log_success "Виртуальная среда найдена."
    fi

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
    mkdir -p "$WEIGHTS_DIR"
    log_success "Директории созданы."
}

# Функция загрузки моделей
download_models() {
    log_step "Проверка и загрузка моделей ИИ..."

    create_directories

    local model_file="$MODELS_DIR/nutritionist_model.pkl"
    
    if [ ! -f "$model_file" ]; then
        log_info "Модель не найдена. Создаем демо-модель..."
        touch "$model_file"
        echo "DEMO_MODEL_DATA" > "$model_file"
        
        if [ -f "$model_file" ]; then
            log_success "Демо-модель создана: $model_file"
        else
            log_error "Не удалось создать демо-модель."
        fi
    else
        log_success "Модель уже существует: $model_file"
    fi

    local weights_file="$WEIGHTS_DIR/recommender_weights.h5"
    if [ ! -f "$weights_file" ]; then
        log_warning "Веса не найдены. Создаем демо-веса..."
        touch "$weights_file"
        echo "DEMO_WEIGHTS_DATA" > "$weights_file"
        log_success "Демо-веса созданы: $weights_file"
    else
        log_success "Веса уже существуют: $weights_file"
    fi
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

# Проверка дистрибутива (для подсказок)
check_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        log_info "Дистрибутив Linux: $NAME $VERSION_ID"
        
        # Проверка необходимых пакетов для Debian/Ubuntu
        if [[ "$ID" == "ubuntu" || "$ID" == "debian" ]]; then
            if ! dpkg -l | grep -q python3-tk; then
                log_warning "Рекомендуется установить python3-tk: sudo apt install python3-tk"
            fi
            if ! dpkg -l | grep -q python3-pyqt6; then
                log_info "PyQt6 будет установлен через pip"
            fi
        fi
        
        # Проверка для Fedora/RHEL
        if [[ "$ID" == "fedora" || "$ID_LIKE" == *"rhel"* ]]; then
            if ! rpm -qa | grep -q python3-tkinter; then
                log_warning "Рекомендуется установить python3-tkinter: sudo dnf install python3-tkinter"
            fi
        fi
    fi
}

# Основная функция
main() {
    echo ""
    echo "=========================================="
    echo "   $PROJECT_NAME Launcher для Linux"
    echo "   Версия: 1.0.0"
    echo "=========================================="
    echo ""

    check_distro
    check_python_version
    setup_venv
    install_dependencies
    check_project_integrity
    download_models
    run_application

    echo ""
    log_success "Сеанс работы завершен."
    echo "=========================================="
}

main "$@"
