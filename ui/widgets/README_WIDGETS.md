# 🎨 UI Widgets для HealthAI

## Обзор

Созданы 4 новых современных виджета для улучшения пользовательского интерфейса HealthAI.

## 📦 Созданные виджеты

### 1. ProductCardWidget (`product_card.py`)
**Назначение:** Отображение продукта с КБЖУ в виде стильной карточки

**Особенности:**
- Иконка категории (🥬 овощи, 🍎 фрукты, 🥩 мясо и т.д.)
- Название и категория продукта
- Калорийность на 100г
- Макронутриенты (белки, жиры, углеводы) в отдельных блоках
- Hover-эффект с зелёной рамкой
- Поддержка тёмной темы

**Использование:**
```python
from ui.widgets import ProductCardWidget

product = {
    'name': 'Куриная грудка',
    'category': 'Мясо',
    'calories': 165,
    'protein': 31.0,
    'fat': 3.6,
    'carbs': 0
}

card = ProductCardWidget(product)
layout.addWidget(card)
```

---

### 2. CircularProgressWidget (`circular_progress.py`)
**Назначение:** Круговой индикатор прогресса для целей

**Особенности:**
- Плавный круговой прогресс-бар
- Настраиваемый цвет
- Отображение текущего значения и цели
- Анимация через QPainter
- Поддержка любых единиц (ккал, мл, шаги)

**Использование:**
```python
from ui.widgets import CircularProgressWidget

# Прогресс калорий
calories_widget = CircularProgressWidget(
    title="Калории",
    current=1450,
    target=2000,
    unit=" ккал",
    color="#4CAF50"
)
layout.addWidget(calories_widget)
```

---

### 3. MacroProgressWidget (`circular_progress.py`)
**Назначение:** Три линейных прогресс-бара для БЖУ

**Особенности:**
- Белки (красный #FF6B6B)
- Жиры (бирюзовый #4ECDC4)
- Углеводы (жёлтый #FFE66D)
- Процентное заполнение
- Текстовые значения

**Использование:**
```python
from ui.widgets import MacroProgressWidget

macros = MacroProgressWidget(
    protein={'current': 120, 'target': 150},
    fats={'current': 60, 'target': 80},
    carbs={'current': 180, 'target': 250}
)
layout.addWidget(macros)
```

---

### 4. AIChatWidget (`chat_widget.py`)
**Назначение:** Чат с AI нутрициологом

**Особенности:**
- Сообщения пользователя (справа, зелёные)
- Сообщения бота (слева, нейтральные)
- Отправка по Enter (Shift+Enter для новой строки)
- Автопрокрутка вниз
- Сигнал `message_sent` для интеграции с AI Engine
- Методы: `add_user_message()`, `add_bot_message()`, `clear_chat()`

**Использование:**
```python
from ui.widgets import AIChatWidget

chat = AIChatWidget()
chat.message_sent.connect(lambda msg: handle_message(msg))
layout.addWidget(chat)

# Обработка ответа от AI
def handle_message(user_message):
    response = ai_engine.chat(user_id=1, message=user_message)
    chat.add_bot_message(response)
```

---

### 5. PhotoUploadWidget (`photo_upload.py`)
**Назначение:** Загрузка и анализ фото еды

**Особенности:**
- Drag-and-drop зона (визуальная)
- Кнопка выбора файла
- Предпросмотр изображения
- Кнопка анализа
- Отображение результатов с доверием модели
- Сигнал `photo_analyzed` с результатами
- FoodAnalysisResultWidget для каждого продукта

**Использование:**
```python
from ui.widgets import PhotoUploadWidget

uploader = PhotoUploadWidget()
uploader.photo_analyzed.connect(handle_analysis)
layout.addWidget(uploader)

def handle_analysis(results):
    # results = {
    #     'products': [...],
    #     'total_calories': 485,
    #     'total_macros': {...}
    # }
    database.add_meal(user_id=1, products=results['products'])
```

---

## 🎨 Стилизация

Все виджеты используют систему тем из `ui.styles`:
- `CURRENT_THEME['bg']` - фон приложения
- `CURRENT_THEME['card_bg']` - фон карточек
- `CURRENT_THEME['text_primary']` - основной текст
- `CURRENT_THEME['text_secondary']` - вторичный текст
- `CURRENT_THEME['border']` - границы
- `CURRENT_THEME['input_bg']` - фон полей ввода

Автоматическая поддержка **тёмной темы**! 🌙

---

## 📊 Технические детали

| Виджет | Строк кода | Зависимости |
|--------|------------|-------------|
| ProductCardWidget | 127 | PyQt6.QtWidgets |
| CircularProgressWidget | 95 | PyQt6.QtGui (QPainter) |
| MacroProgressWidget | 85 | PyQt6.QtWidgets |
| AIChatWidget | 225 | PyQt6.QtCore (pyqtSignal) |
| PhotoUploadWidget | 372 | PyQt6.QtWidgets, QFileDialog |

**Всего: ~900 строк кода**

---

## 🔧 Интеграция в MainWindow

Пример добавления виджетов на главную страницу:

```python
from ui.widgets import (
    ProductCardWidget, 
    CircularProgressWidget,
    MacroProgressWidget,
    AIChatWidget,
    PhotoUploadWidget
)

# В методе create_dashboard() главной страницы:

# 1. Прогресс калорий
self.calories_progress = CircularProgressWidget(
    title="Калории сегодня",
    current=1450,
    target=2000,
    unit=" ккал",
    color="#FF9800"
)

# 2. Макронутриенты
self.macros_widget = MacroProgressWidget(
    protein={'current': 120, 'target': 150},
    fats={'current': 60, 'target': 80},
    carbs={'current': 180, 'target': 250}
)

# 3. Чат с AI
self.ai_chat = AIChatWidget()
self.ai_chat.message_sent.connect(self.handle_ai_message)

# 4. Загрузка фото
self.photo_uploader = PhotoUploadWidget()
self.photo_uploader.photo_analyzed.connect(self.handle_photo_analysis)
```

---

## ✅ Преимущества

1. **Модульность** - каждый виджет независим
2. **Переиспользуемость** - можно использовать на разных страницах
3. **Темизация** - полная поддержка светлой/тёмной темы
4. **Сигналы/слоты** - готово к интеграции с бизнес-логикой
5. **Современный дизайн** - тени, градиенты, анимации
6. **Доступность** - крупные элементы, контрастные цвета

---

## 🚀 Следующие шаги

1. Интегрировать виджеты в `main_window.py`
2. Добавить drag-and-drop поддержку для фото
3. Реализовать реальную ML модель для анализа фото
4. Добавить экспорт виджетов в PDF отчёты
5. Создать анимации появления виджетов
