# 🚀 HealthAI Launcher - Универсальный скрипт запуска

## Описание

`launch_healthai.py` - это интеллектуальный скрипт для автоматической проверки среды, установки зависимостей, загрузки ML-моделей и запуска приложения HealthAI.

## Возможности

### ✅ Автоматические проверки

1. **Проверка версии Python**
   - Требуется Python 3.10+ (минимум 3.9)
   - Вывод текущей версии и рекомендаций

2. **Проверка виртуальной среды**
   - Определяет активность venv/conda
   - Подсказки по активации для Windows/macOS/Linux

3. **Проверка зависимостей**
   - Сканирует requirements.txt
   - Проверяет установленные пакеты
   - Автоматически устанавливает отсутствующие

4. **Проверка ML моделей**
   - Food Classifier (ONNX) - 45 MB
   - Nutrition Recommender (Pickle) - 12 MB
   - Recipe Generator (HDF5) - 28 MB
   - Автозагрузка с Hugging Face при отсутствии

5. **Комплексное тестирование**
   - Запуск test_app.py
   - Запуск test_extended.py
   - Запуск test_full_cycle.py

6. **Запуск приложения**
   - Корректный запуск main.py
   - Обработка ошибок
   - Graceful shutdown

### 🌍 Кроссплатформенность

Поддерживаемые операционные системы:
- **Windows** (10/11)
- **macOS** (Intel/Apple Silicon)
- **Linux** (Ubuntu, Debian, Fedora, Arch)

Автоматическое определение ОС и адаптация команд.

## Использование

### Быстрый старт

```bash
# Активация виртуальной среды (рекомендуется)
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

# Запуск лаунчера
python launch_healthai.py
```

### Прямой запуск (без виртуальной среды)

```bash
python launch_healthai.py
```

### Из терминала (Linux/macOS)

```bash
chmod +x launch_healthai.py
./launch_healthai.py
```

## Структура отчёта

После каждого запуска создаётся файл `startup_report.json`:

```json
{
  "timestamp": "2024-04-10T17:00:00",
  "project_name": "HealthAI",
  "os_type": "linux",
  "python_version": "3.12.0",
  "python_executable": "/usr/bin/python",
  "virtual_env": true,
  "models_dir": "/workspace/assets/models",
  "models_status": {
    "food_classifier.onnx": {
      "status": "present",
      "size_mb": 45.2
    },
    "nutrition_recommender.pkl": {
      "status": "present",
      "size_mb": 12.1
    },
    "recipe_generator.h5": {
      "status": "present",
      "size_mb": 28.3
    }
  }
}
```

## Этапы работы

```
┌─────────────────────────────────────────┐
│  1. Проверка версии Python              │
├─────────────────────────────────────────┤
│  2. Проверка виртуальной среды          │
├─────────────────────────────────────────┤
│  3. Проверка и установка зависимостей   │
├─────────────────────────────────────────┤
│  4. Проверка и загрузка ML моделей      │
├─────────────────────────────────────────┤
│  5. Комплексное тестирование            │
├─────────────────────────────────────────┤
│  6. Запуск приложения                   │
├─────────────────────────────────────────┤
│  7. Генерация отчёта                    │
└─────────────────────────────────────────┘
```

## Цветовая индикация

- 🟢 **Зелёный** - Успешное завершение этапа
- 🟡 **Жёлтый** - Предупреждение (не критично)
- 🔴 **Красный** - Ошибка (критично для некоторых этапов)
- 🔵 **Синий** - Информация

## Требования

- Python 3.9+ (рекомендуется 3.10+)
- pip (менеджер пакетов)
- Доступ в Интернет (для загрузки зависимостей и моделей)
- 100 MB свободного места (для моделей)

## Решение проблем

### Ошибка: "Python version too old"

```bash
# Обновите Python до версии 3.10 или новее
# macOS:
brew install python@3.12

# Ubuntu/Debian:
sudo apt update
sudo apt install python3.12

# Windows:
# Скачайте с python.org
```

### Ошибка: "Virtual environment not activated"

```bash
# Создайте и активируйте виртуальную среду
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### Ошибка загрузки моделей

Если модели не загружаются автоматически:

1. Проверьте подключение к Интернету
2. Попробуйте скачать вручную с Hugging Face:
   - https://huggingface.co/healthai/food-classifier
   - https://huggingface.co/healthai/nutrition-recommender
   - https://huggingface.co/healthai/recipe-generator

3. Поместите файлы в папку `assets/models/`

### Ошибка установки зависимостей

```bash
# Обновите pip
python -m pip install --upgrade pip

# Установите зависимости вручную
pip install -r requirements.txt
```

## Для разработчиков

### Добавление новых моделей

Отредактируйте словарь `REQUIRED_MODELS` в начале скрипта:

```python
REQUIRED_MODELS = {
    "new_model.onnx": {
        "url": "https://huggingface.co/.../new_model.onnx",
        "size_mb": 50,
        "description": "Описание модели"
    },
    # ... существующие модели
}
```

### Отключение тестирования

Закомментируйте этап тестирования в списке `stages`:

```python
stages = [
    ("Проверка Python", check_python_version),
    ("Виртуальная среда", check_virtual_environment),
    ("Зависимости", check_and_install_dependencies),
    ("ML модели", check_and_download_models),
    # ("Тестирование", run_comprehensive_tests),  # Закомментировано
    ("Запуск приложения", launch_application),
]
```

## Лицензия

MIT License - HealthAI Team

## Поддержка

При возникновении проблем:
1. Проверьте файл `startup_report.json`
2. Изучите логи в консоли
3. Откройте issue на GitHub

---

**HealthAI** - Умный гид по здоровому питанию 🏥
