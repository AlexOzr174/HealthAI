# 🤖 AI Engine для HealthAI — Документация

## Обзор

Модуль `ai_engine` предоставляет интеллектуальные функции для приложения HealthAI:

### Компоненты

1. **NutritionistChatbot** — Умный чат-бот нутрициолог
2. **PredictiveAnalytics** — Предиктивная аналитика и прогнозирование
3. **RecipeGenerator** — Генератор персонализированных рецептов
4. **AIEngine** — Единый интерфейс ко всем компонентам

---

## 📋 Установка

Все зависимости уже установлены в проекте:
```bash
pip install scikit-learn numpy pandas
```

---

## 🚀 Быстрый старт

### 1. Инициализация ИИ-движка

```python
from ai_engine import AIEngine

# Создание экземпляра
ai = AIEngine()

# Инициализация пользователя
profile = {
    'name': 'Алексей',
    'weight': 85,
    'height': 178,
    'age': 32,
    'gender': 'male',
    'activity_level': 1.55,
    'goal': 'weight_loss',
    'target_weight': 75,
    'restrictions': []  # vegetarian, vegan, gluten_free и т.д.
}

ai.initialize_user(user_id=1, profile=profile)
```

### 2. Чат с нутрициологом

```python
# Отправка сообщения
response = ai.chat(1, "Сколько калорий мне нужно?")

print(response['text'])          # Текстовый ответ
print(response['suggestions'])   # Подсказки для продолжения
print(response['type'])          # Тип ответа
```

**Примеры запросов:**
- "Хочу похудеть на 5 кг"
- "Сколько белка мне нужно?"
- "Дай план питания на день"
- "У меня плато, что делать?"
- "Нет мотивации продолжать"

### 3. Анализ веса и прогнозы

```python
# Добавление замеров веса
ai.add_weight_measurement(1, 85.0, '2024-01-01')
ai.add_weight_measurement(1, 84.5, '2024-01-08')
ai.add_weight_measurement(1, 84.0, '2024-01-15')

# Получение анализа
analysis = ai.get_weight_analysis(1, weight_history)

print(analysis['trend']['description'])      # "Вес снижается"
print(analysis['trend']['weekly_change'])    # -0.57 кг
print(analysis['forecast']['week_1'])        # Прогноз на неделю
print(analysis['model_quality']['r2_score']) # Точность модели
```

**Прогноз достижения цели:**
```python
prediction = ai.predict_goal_achievement(
    user_id=1,
    goal_weight=75,
    daily_calorie_deficit=500
)

print(prediction['prediction']['days_to_goal'])           # 154 дня
print(prediction['prediction']['estimated_completion_date'])  # Дата
print(prediction['optimal_strategy'])  # Оптимальная стратегия
```

### 4. Генерация рецептов

```python
#单个 рецепт
recipe = ai.generate_recipe(
    user_id=1,
    category='lunch',      # breakfast, lunch, dinner, snack
    cooking_time=30        # минут
)

print(recipe['name'])           # Название
print(recipe['ingredients'])    # Ингредиенты
print(recipe['nutrition'])      # КБЖУ
print(recipe['instructions'])   # Инструкции
```

**План питания на неделю:**
```python
weekly_plan = ai.generate_weekly_plan(user_id=1, days=7)

for day, meals in weekly_plan.items():
    if day == '_summary':
        continue
    print(f"{day}:")
    for meal_type, recipe in meals.items():
        print(f"  {meal_type}: {recipe['name']}")
```

### 5. Персональные рекомендации

```python
recommendations = ai.get_recommendations(1)

for rec in recommendations:
    print(f"{rec['title']}: {rec['message']}")
    print(f"  Приоритет: {rec['priority']}")
    print(f"  Действия: {rec['actions']}")
```

---

## 📊 API Reference

### AIEngine

| Метод | Описание | Возвращает |
|-------|----------|------------|
| `initialize_user(user_id, profile)` | Инициализация пользователя | Dict со статусом |
| `chat(user_id, message)` | Сообщение чат-боту | Dict с ответом |
| `get_weight_analysis(user_id, history)` | Анализ тренда веса | Dict с анализом |
| `predict_goal_achievement(user_id, goal_weight, deficit)` | Прогноз цели | Dict с прогнозом |
| `optimize_nutrition(user_id, goal)` | Оптимизация КБЖУ | Dict с макросами |
| `detect_plateau(user_id, history)` | Обнаружение плато | Dict с рекомендациями |
| `generate_recipe(user_id, category, time)` | Генерация рецепта | Dict с рецептом |
| `generate_weekly_plan(user_id, days)` | План на неделю | Dict с планом |
| `suggest_substitutions(ingredient, user_id)` | Замены продуктов | List[str] |
| `get_recommendations(user_id)` | Персональные рекомендации | List[Dict] |
| `get_ai_summary(user_id)` | Общая сводка | Dict со статистикой |

### NutritionistChatbot

**Распознаваемые намерения:**
- `greeting` — Приветствие
- `weight_loss` / `weight_gain` / `maintain` — Цели по весу
- `diet_advice` — Советы по питанию
- `calorie_question` / `protein_question` / `water_question` — Вопросы о нутриентах
- `meal_plan` — План питания
- `problem` — Проблемы и трудности
- `motivation` — Мотивация
- `progress` — Прогресс

### PredictiveAnalytics

**Методы:**
- `analyze_weight_trend(history)` — Линейная/полиномиальная регрессия
- `predict_goal_achievement(...)` — Расчёт времени до цели
- `optimize_calories_for_goal(profile, goal)` — Оптимизация КБЖУ
- `detect_plateau(history, days_window)` — Статистическое обнаружение плато
- `generate_insights(analytics_data)` — Генерация инсайтов

### RecipeGenerator

**Параметры генерации:**
- `category` — Тип блюда
- `preferences` — Предпочтения (любимые продукты)
- `restrictions` — Ограничения (vegetarian, vegan, gluten_free, dairy_free, low_carb)
- `available_products` — Доступные продукты дома
- `cooking_time` — Максимальное время
- `difficulty` — Сложность (easy, medium, hard)

---

## 💡 Примеры использования

### Сценарий 1: Консультация нутрициолога

```python
ai = AIEngine()
ai.initialize_user(1, profile)

# Диалог
messages = [
    "Привет! Я хочу похудеть",
    "Сколько калорий мне нужно?",
    "Какой должен быть белок?",
    "Дай план питания на сегодня"
]

for msg in messages:
    response = ai.chat(1, msg)
    print(f"Бот: {response['text']}\n")
```

### Сценарий 2: Аналитика прогресса

```python
# Загрузка истории веса
weight_history = [
    {'date': '2024-01-01', 'weight': 85.0},
    {'date': '2024-01-08', 'weight': 84.5},
    {'date': '2024-01-15', 'weight': 84.0},
    {'date': '2024-01-22', 'weight': 83.2},
    {'date': '2024-01-29', 'weight': 82.8}
]

analysis = ai.get_weight_analysis(1, weight_history)

if analysis['status'] == 'success':
    print(f"Тренд: {analysis['trend']['description']}")
    print(f"R² точность: {analysis['model_quality']['r2_score']}")
    print(f"Прогноз через 4 недели: {analysis['forecast']['week_4']} кг")
    
    # Проверка плато
    plateau = ai.detect_plateau(1, weight_history)
    if plateau.get('plateau_detected'):
        print("⚠️ Обнаружено плато!")
        for rec in plateau['recommendations']:
            print(f"  - {rec}")
```

### Сценарий 3: Генерация меню

```python
# План на 3 дня
plan = ai.generate_weekly_plan(1, days=3)

print(f"Средняя калорийность: {plan['_summary']['avg_daily_calories']} ккал")
print(f"Всего рецептов: {plan['_summary']['total_recipes']}")

# Замена ингредиента
substitutes = ai.suggest_substitutions('курица', user_id=1)
print(f"Чем заменить курицу: {substitutes}")
```

---

## 🔧 Расширение функциональности

### Добавление новых намерений чат-бота

```python
# В файле nutritionist_chatbot.py
self.intents['new_intent'] = ['ключевое слово 1', 'ключевое слово 2']

# Добавить обработчик
def _handle_new_intent(self) -> Dict:
    return {
        'text': 'Ответ на новое намерение',
        'suggestions': ['Подсказка 1', 'Подсказка 2'],
        'type': 'new_type'
    }
```

### Добавление шаблонов рецептов

```python
# В файле recipe_generator.py
self.recipe_templates['new_category'] = {
    'base_ingredients': [...],
    'proteins': [...],
    'vegetables': [...]
}
```

---

## 📈 Производительность

- **Чат-бот**: ~10-50ms на ответ
- **Анализ веса**: ~50-100ms (с обучением модели)
- **Генерация рецепта**: ~5-20ms
- **План на неделю**: ~100-200ms

---

## 🛡️ Безопасность данных

- Все данные хранятся в памяти (не персистентны)
- Для сохранения интегрируйтесь с базой данных проекта
- Не храните персональные данные в логах

---

## 📝 Лицензия

Модуль является частью проекта HealthAI.
