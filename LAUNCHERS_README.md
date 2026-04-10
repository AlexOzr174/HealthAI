# 🚀 HealthAI Cross-Platform Launchers

## Обзор

Проект HealthAI теперь включает **три кроссплатформенных лаунчера** для автоматической установки, настройки и запуска приложения на разных операционных системах.

| ОС | Файл | Статус |
|---|---|---|
| **macOS** | `launch.sh` | ✅ Готово |
| **Linux** | `launch_linux.sh` | ✅ Готово |
| **Windows** | `launch.bat` | ✅ Готово |

---

## 📁 Структура файлов

```
HealthAI/
├── launch.sh              # Лаунчер для macOS
├── launch_linux.sh        # Лаунчер для Linux  
├── launch.bat             # Лаунчер для Windows
├── LAUNCHER_MACOS_README.md  # Документация для macOS
├── LAUNCHER_LINUX_README.md  # Документация для Linux (создаётся)
├── LAUNCHER_WINDOWS_README.md # Документация для Windows (создаётся)
└── ...
```

---

## 🍏 macOS: `launch.sh`

### Быстрый старт
```bash
chmod +x launch.sh
./launch.sh
```

### Особенности
- ✅ Проверка Python 3.10+
- ✅ Создание и активация venv
- ✅ Установка зависимостей из requirements.txt
- ✅ Загрузка/создание демо-моделей ИИ
- ✅ Проверка целостности проекта
- ✅ Цветной вывод с эмодзи
- ✅ Поддержка curl для загрузки реальных моделей

### Настройка URL моделей
Отредактируйте массив `MODEL_URLS` в начале скрипта:
```bash
MODEL_URLS=(
    "https://huggingface.co/your-model/pytorch_model.bin"
    "https://github.com/your-repo/releases/download/model.pt"
)
```

Раскомментируйте строку с `curl` в функции `download_models()`.

### Требования
- macOS 10.12+
- Python 3.10+
- Bash 3.2+ (встроен)
- ~500 MB свободного места

---

## 🐧 Linux: `launch_linux.sh`

### Быстрый старт
```bash
chmod +x launch_linux.sh
./launch_linux.sh
```

### Особенности
- ✅ Авто-определение дистрибутива (Ubuntu, Debian, Fedora, RHEL)
- ✅ Проверка системных пакетов (python3-tk, python3-venv)
- ✅ Подсказки по установке недостающих пакетов
- ✅ Полная совместимость с systemd/dpkg/rpm
- ✅ Цветной вывод ANSI

### Установка зависимостей на Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip python3-tk
```

### Установка зависимостей на Fedora/RHEL
```bash
sudo dnf install python3 python3-virtualenv python3-pip python3-tkinter
```

### Требования
- Любой современный дистрибутив Linux
- Python 3.10+
- Bash 4.0+
- ~500 MB свободного места

---

## 🪟 Windows: `launch.bat`

### Быстрый старт
```cmd
launch.bat
```

Или дважды кликните по файлу в Проводнике.

### Особенности
- ✅ Работает в Command Prompt и PowerShell
- ✅ Автоматическая активация виртуальной среды
- ✅ Проверка наличия Python через PATH
- ✅ Pause в конце для просмотра ошибок
- ✅ Совместимость с Windows 10/11

### Установка Python на Windows
1. Скачайте с https://www.python.org/downloads/
2. **Важно:** Отметьте галочку "Add Python to PATH"
3. Установите Python 3.10 или выше

### Требования
- Windows 10/11
- Python 3.10+
- ~500 MB свободного места
- Права администратора (для установки пакетов)

---

## 🔧 Общие функции всех лаунчеров

### 1. Проверка окружения
- Версия Python (требуется 3.10+)
- Наличие критических файлов проекта
- Свободное место на диске

### 2. Виртуальная среда
- Автоматическое создание `venv/`
- Активация перед установкой
- Изоляция зависимостей

### 3. Зависимости
- Обновление pip до последней версии
- Установка из `requirements.txt`
- Обработка ошибок установки

### 4. Модели ИИ
- Создание директорий `ai_engine/models/` и `ml/weights/`
- Проверка наличия моделей
- Создание демо-файлов если загрузка недоступна
- Поддержка загрузки по URL (настраивается)

### 5. Запуск приложения
- Поиск `main.py` или `src/main.py`
- Запуск через Python из venv
- Корректная передача кода возврата

---

## 🎨 Цветовой вывод

Все лаунчеры используют цветовую схему:

| Префикс | Цвет | Значение |
|---------|------|----------|
| `[INFO]` | 🔵 Синий | Информация |
| `[SUCCESS]` | 🟢 Зелёный | Успех |
| `[WARNING]` | 🟡 Жёлтый | Предупреждение |
| `[ERROR]` | 🔴 Красный | Ошибка |
| `[STEP]` | 🟣 Голубой | Шаг выполнения |

---

## 📊 Сравнение функций

| Функция | macOS | Linux | Windows |
|---------|-------|-------|---------|
| Проверка Python | ✅ | ✅ | ✅ |
| Создание venv | ✅ | ✅ | ✅ |
| Установка зависимостей | ✅ | ✅ | ✅ |
| Загрузка моделей | ✅ | ✅ | ✅ |
| Определение ОС | ❌ | ✅ | ❌ |
| Подсказки по пакетам | ❌ | ✅ | ❌ |
| Curl для загрузки | ✅ | ✅ | ❌ |
| Pause в конце | ❌ | ❌ | ✅ |
| Цветной вывод | ✅ | ✅ | ⚠️ Частично |

---

## 🐛 Решение проблем

### Общая ошибка: "Python не найден"
- **macOS:** `brew install python@3.12`
- **Linux:** `sudo apt install python3 python3-venv`
- **Windows:** Переустановите Python с галочкой "Add to PATH"

### Общая ошибка: "No space left on device"
```bash
# Проверка места
df -h  # Linux/macOS
dir    # Windows

# Очистка кэша pip
pip cache purge
```

### Общая ошибка: "Permission denied"
```bash
# Linux/macOS
chmod +x launch.sh
chmod +x launch_linux.sh

# Windows
Запуск от имени администратора
```

### Общая ошибка: "ModuleNotFoundError"
```bash
# Удалить venv и создать заново
rm -rf venv  # Linux/macOS
rmdir /s venv  # Windows

# Запустить лаунчер заново
./launch.sh  # или аналог для вашей ОС
```

---

## 🔄 Обновление лаунчеров

При обновлении проекта:

1. Сохраните свои настройки URL моделей
2. Скопируйте новые версии лаунчеров
3. Запустите с флагом переустановки:
   ```bash
   rm -rf venv && ./launch.sh
   ```

---

## 📝 Логирование

Для сохранения логов запуска:

### macOS/Linux
```bash
./launch.sh > launch_log.txt 2>&1
# или
./launch_linux.sh 2>&1 | tee launch_log.txt
```

### Windows
```cmd
launch.bat > launch_log.txt 2>&1
```

---

## 🎯 Рекомендации по использованию

### Для разработки
Используйте лаунчер вашей ОС для быстрого развёртывания:
```bash
# Первый запуск
./launch.sh  # macOS
./launch_linux.sh  # Linux
launch.bat  # Windows

# Последующие запуски (venv уже создан)
source venv/bin/activate && python main.py  # macOS/Linux
venv\Scripts\activate && python main.py  # Windows
```

### Для демонстрации
Лаунчеры идеально подходят для:
- Первого запуска проекта
- Демонстрации на презентациях
- Тестирования на чистых системах
- CI/CD пайплайнов

### Для продакшена
Настройте URL реальных моделей:
1. Загрузите модели на хостинг (HuggingFace, GitHub Releases)
2. Обновите `MODEL_URLS` в лаунчере
3. Раскомментируйте команды загрузки

---

## 📞 Поддержка

При возникновении проблем:

1. Проверьте версию Python:
   ```bash
   python3 --version  # macOS/Linux
   python --version   # Windows
   ```

2. Проверьте логи лаунчера

3. Убедитесь в наличии интернета

4. Проверьте место на диске:
   ```bash
   df -h  # macOS/Linux
   dir    # Windows
   ```

5. Попробуйте запустить вручную:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python main.py
   ```

---

## 📄 Лицензия

MIT License — используйте свободно в своих проектах.

---

**Версия лаунчеров:** 1.0.0  
**Дата создания:** 2024  
**Поддерживаемые ОС:** macOS 10.12+, Linux (любые), Windows 10/11  
**Требуемая версия Python:** 3.10+
