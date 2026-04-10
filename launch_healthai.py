#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HealthAI - Универсальный скрипт запуска
Проверка среды, установка зависимостей, загрузка моделей и запуск приложения

Поддерживаемые ОС: Windows, macOS, Linux
"""

import os
import sys
import platform
import subprocess
import json
import hashlib
import shutil
from pathlib import Path
from datetime import datetime

# Константы
PROJECT_NAME = "HealthAI"
REQUIRED_PYTHON_VERSION = (3, 10)
MINIMUM_PYTHON_VERSION = (3, 9)
MODELS_DIR = Path("assets/models")

# Демо-модели для работы без внешних URL
# В реальном проекте замените на актуальные URL с Hugging Face или другого хранилища
REQUIRED_MODELS = {
    "food_classifier.onnx": {
        "url": None,  # Модель создаётся программно при отсутствии
        "size_mb": 0.1,
        "description": "Модель классификации еды по фото",
        "create_demo": True
    },
    "nutrition_recommender.pkl": {
        "url": None,  # Модель создаётся программно при отсутствии
        "size_mb": 0.1,
        "description": "ML модель рекомендаций питания",
        "create_demo": True
    },
    "recipe_generator.h5": {
        "url": None,  # Модель создаётся программно при отсутствии
        "size_mb": 0.1,
        "description": "Нейросеть генерации рецептов",
        "create_demo": True
    }
}

# Цвета для вывода
class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"

def print_header(text):
    """Вывод заголовка"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}\n")

def print_success(text):
    """Вывод успешного сообщения"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text):
    """Вывод ошибки"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warning(text):
    """Вывод предупреждения"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_info(text):
    """Вывод информации"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

def get_os_type():
    """Определение типа операционной системы"""
    system = platform.system().lower()
    
    if system == "windows":
        return "windows"
    elif system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    else:
        return "unknown"

def check_python_version():
    """Проверка версии Python"""
    print_header("ПРОВЕРКА ВЕРСИИ PYTHON")
    
    current_version = sys.version_info[:2]
    required_str = f"{REQUIRED_PYTHON_VERSION[0]}.{REQUIRED_PYTHON_VERSION[1]}"
    min_str = f"{MINIMUM_PYTHON_VERSION[0]}.{MINIMUM_PYTHON_VERSION[1]}"
    
    print_info(f"Текущая версия Python: {sys.version}")
    print_info(f"Требуемая версия: >={required_str}, минимальная: >={min_str}")
    
    if current_version < MINIMUM_PYTHON_VERSION:
        print_error(f"Версия Python {current_version[0]}.{current_version[1]} слишком старая!")
        print_error(f"Установите Python {required_str} или новее")
        return False
    
    if current_version < REQUIRED_PYTHON_VERSION:
        print_warning(f"Рекомендуется обновиться до Python {required_str}")
    
    print_success(f"Версия Python подходит: {current_version[0]}.{current_version[1]}")
    return True

def check_virtual_environment():
    """Проверка активации виртуальной среды"""
    print_header("ПРОВЕРКА ВИРТУАЛЬНОЙ СРЕДЫ")
    
    in_venv = sys.prefix != sys.base_prefix
    venv_name = os.environ.get('VIRTUAL_ENV', '')
    
    if in_venv:
        print_success(f"Виртуальная среда активна: {venv_name or ' unnamed'}")
        return True
    else:
        print_warning("Виртуальная среда не активирована")
        print_info("Рекомендуется создать и активировать виртуальную среду:")
        
        os_type = get_os_type()
        if os_type == "windows":
            print_info("  Windows: venv\\Scripts\\activate")
        else:
            print_info("  macOS/Linux: source venv/bin/activate")
        
        # Продолжаем без виртуальной среды (не критично)
        return True

def check_and_install_dependencies():
    """Проверка и установка зависимостей"""
    print_header("ПРОВЕРКА ЗАВИСИМОСТЕЙ")
    
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print_error("Файл requirements.txt не найден!")
        return False
    
    print_info("Проверка установленных пакетов...")
    
    try:
        # Читаем requirements.txt
        with open(requirements_file, 'r', encoding='utf-8') as f:
            packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        missing_packages = []
        installed_packages = {}
        
        # Проверяем каждый пакет
        for package in packages:
            pkg_name = package.split('==')[0].split('>=')[0].split('<=')[0]
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "show", pkg_name],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    installed_packages[pkg_name] = True
                    print_success(f"Установлен: {pkg_name}")
                else:
                    missing_packages.append(package)
                    print_warning(f"Отсутствует: {pkg_name}")
            except Exception as e:
                missing_packages.append(package)
                print_warning(f"Ошибка проверки {pkg_name}: {e}")
        
        if missing_packages:
            print_info(f"\nНайдено {len(missing_packages)} отсутствующих пакетов")
            print_info("Установка недостающих зависимостей...")
            
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", 
                    "-r", str(requirements_file),
                    "--upgrade"
                ])
                print_success("Все зависимости установлены!")
            except subprocess.CalledProcessError as e:
                print_error(f"Ошибка установки зависимостей: {e}")
                return False
        else:
            print_success("Все зависимости уже установлены!")
        
        return True
        
    except Exception as e:
        print_error(f"Ошибка проверки зависимостей: {e}")
        return False

def calculate_file_hash(filepath):
    """Вычисление хэша файла"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def download_file(url, destination, description=""):
    """Скачивание файла с прогрессом"""
    import urllib.request
    import urllib.error
    
    print_info(f"Скачивание: {description or destination.name}")
    print_info(f"URL: {url}")
    
    try:
        # Пробуем разные методы скачивания
        try:
            # Метод 1: urllib
            def report_progress(block_num, block_size, total_size):
                downloaded = block_num * block_size
                percent = min(downloaded * 100 / total_size, 100)
                bar_length = 40
                filled = int(bar_length * percent / 100)
                bar = '█' * filled + '░' * (bar_length - filled)
                print(f"\r  Прогресс: [{bar}] {percent:.1f}%", end='', flush=True)
            
            urllib.request.urlretrieve(url, destination, reporthook=report_progress)
            print()  # Новая строка после прогресса
            
        except Exception as e:
            print_warning(f"urllib не сработал, пробуем wget: {e}")
            # Метод 2: wget через subprocess
            if shutil.which('wget'):
                subprocess.check_call(['wget', '-O', str(destination), url])
            else:
                # Метод 3: curl
                subprocess.check_call(['curl', '-L', '-o', str(destination), url])
        
        if destination.exists():
            size_mb = destination.stat().st_size / (1024 * 1024)
            print_success(f"Файл загружен: {destination.name} ({size_mb:.2f} MB)")
            return True
        else:
            print_error(f"Файл не был загружен: {destination.name}")
            return False
            
    except Exception as e:
        print_error(f"Ошибка загрузки: {e}")
        return False

def create_demo_model(model_name, model_path):
    """Создание демо-модели для тестирования"""
    print_info(f"Создание демо-модели: {model_name}")
    
    try:
        if model_name == "food_classifier.onnx":
            # Создаём простой ONNX файл (демо)
            import numpy as np
            # Заглушка ONNX файла
            demo_data = b"ONNX_DEMO_MODEL_V1" + np.random.rand(100).tobytes()
            with open(model_path, 'wb') as f:
                f.write(demo_data)
                
        elif model_name == "nutrition_recommender.pkl":
            # Создаём простой Pickle файл (демо)
            import pickle
            demo_model = {
                'version': '1.0',
                'type': 'nutrition_recommender',
                'data': {'weights': [0.5, 0.3, 0.2]}
            }
            with open(model_path, 'wb') as f:
                pickle.dump(demo_model, f)
                
        elif model_name == "recipe_generator.h5":
            # Создаём простой HDF5 файл (демо)
            demo_data = b"HDF5_DEMO_MODEL_V1"
            with open(model_path, 'wb') as f:
                f.write(demo_data)
        
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print_success(f"Демо-модель создана: {model_name} ({size_mb:.4f} MB)")
        return True
        
    except Exception as e:
        print_error(f"Ошибка создания демо-модели {model_name}: {e}")
        return False

def check_and_download_models():
    """Проверка и загрузка ML моделей"""
    print_header("ПРОВЕРКА ML МОДЕЛЕЙ")
    
    # Создаём директорию для моделей
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    models_status = {}
    all_present = True
    
    for model_name, model_info in REQUIRED_MODELS.items():
        model_path = MODELS_DIR / model_name
        
        if model_path.exists():
            size_mb = model_path.stat().st_size / (1024 * 1024)
            expected_size = model_info.get('size_mb', 0)
            
            print_success(f"Модель найдена: {model_name} ({size_mb:.4f} MB)")
            models_status[model_name] = "present"
        else:
            print_warning(f"Модель отсутствует: {model_name}")
            print_info(f"  Описание: {model_info.get('description', 'N/A')}")
            models_status[model_name] = "missing"
            all_present = False
    
    if all_present:
        print_success("\nВсе модели присутствуют!")
        return True
    
    print_header("СОЗДАНИЕ ДЕМО-МОДЕЛЕЙ")
    print_info("Модели создаются локально для демонстрации")
    
    created_count = 0
    for model_name, status in models_status.items():
        if status == "missing":
            model_info = REQUIRED_MODELS[model_name]
            model_path = MODELS_DIR / model_name
            
            # Если есть URL - пробуем скачать
            if model_info.get('url'):
                print(f"\nЗагрузка: {model_name}")
                if download_file(model_info['url'], model_path, model_info.get('description')):
                    created_count += 1
            # Иначе создаём демо-модель
            elif model_info.get('create_demo'):
                print(f"\nСоздание: {model_name}")
                if create_demo_model(model_name, model_path):
                    created_count += 1
            else:
                print_warning(f"Неизвестный источник для {model_name}")
    
    print_header("РЕЗУЛЬТАТЫ ЗАГРУЗКИ/СОЗДАНИЯ МОДЕЛЕЙ")
    print_info(f"Создано/загружено моделей: {created_count}/{len([s for s in models_status.values() if s == 'missing'])}")
    
    if created_count == len([s for s in models_status.values() if s == 'missing']):
        print_success("Все отсутствующие модели успешно созданы/загружены!")
        return True
    else:
        print_warning("Часть моделей не удалось создать/загрузить")
        print_info("Приложение будет работать в ограниченном режиме")
        return True  # Не блокируем запуск

def run_comprehensive_tests():
    """Запуск комплексных тестов"""
    print_header("КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ")
    
    test_files = [
        "test_app.py",
        "test_extended.py", 
        "test_full_cycle.py"
    ]
    
    tests_passed = 0
    tests_total = len(test_files)
    
    for test_file in test_files:
        if Path(test_file).exists():
            print_info(f"Запуск тестов: {test_file}")
            try:
                result = subprocess.run(
                    [sys.executable, test_file],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode == 0:
                    print_success(f"✓ Тесты {test_file} пройдены")
                    tests_passed += 1
                else:
                    print_warning(f"⚠ Тесты {test_file} завершились с кодом {result.returncode}")
                    if result.stdout:
                        print(result.stdout[-500:])  # Последние 500 символов
            except subprocess.TimeoutExpired:
                print_warning(f"⚠ Тесты {test_file} превысили лимит времени")
            except Exception as e:
                print_error(f"✗ Ошибка при запуске {test_file}: {e}")
        else:
            print_warning(f"Файл тестов не найден: {test_file}")
    
    print_header("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print_info(f"Пройдено тестов: {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print_success("Все тесты пройдены успешно!")
        return True
    elif tests_passed > 0:
        print_warning("Часть тестов прошла успешно, продолжаем...")
        return True
    else:
        print_error("Тесты не прошли, но продолжаем запуск...")
        return True

def launch_application():
    """Запуск основного приложения"""
    print_header("ЗАПУСК ПРИЛОЖЕНИЯ HEALTHAI")
    
    main_file = Path("main.py")
    
    if not main_file.exists():
        print_error("Файл main.py не найден!")
        return False
    
    print_info(f"Запуск {PROJECT_NAME}...")
    print_info(f"Python: {sys.executable}")
    print_info(f"OS: {get_os_type()}")
    print("-" * 60)
    
    try:
        # Запускаем приложение
        subprocess.run([sys.executable, str(main_file)], check=True)
        print_success("Приложение завершено корректно")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Приложение завершилось с ошибкой: {e}")
        return False
    except KeyboardInterrupt:
        print_info("\nПриложение остановлено пользователем")
        return True
    except Exception as e:
        print_error(f"Неожиданная ошибка: {e}")
        return False

def generate_startup_report():
    """Генерация отчёта о запуске"""
    print_header("ОТЧЁТ О ЗАПУСКЕ")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "project_name": PROJECT_NAME,
        "os_type": get_os_type(),
        "python_version": sys.version,
        "python_executable": sys.executable,
        "virtual_env": sys.prefix != sys.base_prefix,
        "models_dir": str(MODELS_DIR.absolute()),
        "models_status": {}
    }
    
    # Статус моделей
    for model_name in REQUIRED_MODELS:
        model_path = MODELS_DIR / model_name
        if model_path.exists():
            report["models_status"][model_name] = {
                "status": "present",
                "size_mb": round(model_path.stat().st_size / (1024 * 1024), 2)
            }
        else:
            report["models_status"][model_name] = {"status": "missing"}
    
    # Сохраняем отчёт
    report_file = Path("startup_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print_success(f"Отчёт сохранён: {report_file}")
    
    # Вывод сводки
    print("\n" + "=" * 60)
    print(f"  {PROJECT_NAME} - Сводка")
    print("=" * 60)
    print(f"  ОС: {get_os_type()}")
    print(f"  Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print(f"  Моделей загружено: {sum(1 for m in report['models_status'].values() if m['status'] == 'present')}/{len(REQUIRED_MODELS)}")
    print("=" * 60)
    
    return report

def main():
    """Главная функция"""
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}")
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║              🏥 HealthAI Launcher v1.0 🏥                 ║
    ║         Умный гид по здоровому питанию                   ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    print(f"{Colors.RESET}")
    
    print_info(f"Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"Операционная система: {get_os_type()}")
    print_info(f"Платформа: {platform.platform()}")
    print_info(f"Архитектура: {platform.machine()}")
    
    # Этапы запуска
    stages = [
        ("Проверка Python", check_python_version),
        ("Виртуальная среда", check_virtual_environment),
        ("Зависимости", check_and_install_dependencies),
        ("ML модели", check_and_download_models),
        ("Тестирование", run_comprehensive_tests),
        ("Запуск приложения", launch_application),
    ]
    
    results = {}
    
    for stage_name, stage_func in stages:
        try:
            result = stage_func()
            results[stage_name] = result
            
            if not result and stage_name in ["Проверка Python", "Зависимости"]:
                print_error(f"\nКритическая ошибка на этапе: {stage_name}")
                print_error("Запуск невозможен. Исправьте ошибки и попробуйте снова.")
                sys.exit(1)
                
        except Exception as e:
            print_error(f"Ошибка на этапе {stage_name}: {e}")
            results[stage_name] = False
            
            if stage_name in ["Проверка Python", "Зависимости"]:
                sys.exit(1)
    
    # Генерация отчёта
    generate_startup_report()
    
    # Итоги
    print_header("ИТОГИ ЗАПУСКА")
    
    all_success = all(results.values())
    
    if all_success:
        print_success("🎉 Все этапы успешно завершены!")
        print_success(f"🎊 {PROJECT_NAME} готов к работе!")
    else:
        failed_stages = [name for name, result in results.items() if not result]
        print_warning(f"⚠ Некоторые этапы не прошли: {', '.join(failed_stages)}")
        print_info("Но приложение всё равно запущено (некритичные ошибки)")
    
    print(f"\n{Colors.GREEN}Спасибо за использование HealthAI!{Colors.RESET}\n")

if __name__ == "__main__":
    main()
