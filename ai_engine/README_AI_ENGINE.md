# 🤖 AI Engine для HealthAI

## Обзор

AI Engine — это центральный модуль искусственного интеллекта для приложения HealthAI, который объединяет три основных компонента:

1. **Чат-бот нутрициолог** — умный помощник для консультаций по питанию
2. **Предиктивная аналитика** — прогнозирование веса и обнаружение плато
3. **Генератор рецептов** — создание персонализированных рецептов

Все модели работают **локально**, без необходимости внешних API.

---

## 📁 Структура

```
ai_engine/
├── __init__.py              # Основной класс AIEngine
├── nutritionist_chatbot.py  # Чат-бот нутрициолог
├── predictive_analytics.py  # Предиктивная аналитика
└── recipe_generator.py      # Генератор рецептов
```

---

## 🚀 Быстрый старт

### Инициализация

```python
from ai_engine import AIEngine

# Создание экземпляра
engine = AIEngine()

# Инициализация пользователя
profile = {
    'weight': 80,              # кг
    'height': 175,             # см
    'age': 30,                 # лет
    'gender': 'male',          # 'male' или 'female'
    'activity_level': 1.55,    # коэффициент активности
    'goal': 'weight_loss',     # 'weight_loss', 'muscle_gain', 'maintenance'
    'target_weight': 70,       # целевой вес
    'preferences': {'cuisine': ['european']},
    'restrictions': ['lactose'] # ограничения (lactose, gluten, etc.)
}

engine.initialize_user(user_id=1, profile=profile)
```

---

## 💬 Чат-бот нутрициолог

### Возможности
- Ответы на вопросы о питании
- Персонализированные рекомендации
- Поддержка диетических ограничений
- Контекстная память диалога

### Примеры использования

```python
# Вопрос о похудении
response = engine.chat(user_id=1, message="Как похудеть?")
print(response['text'])

# Вопрос о воде
response = engine.chat(user_id=1, message="Сколько пить воды в день?")
print(response['text'])

# Вопрос о завтраке
response = engine.chat(user_id=1, message="Что есть на завтрак?")
print(response['text'])
```

### Формат ответа
```python
{
    'text': 'Текст ответа...',
    'suggestions': ['Предложение 1', 'Предложение 2'],
    'type': 'advice|info|motivation',
    'goal': 'weight_loss'  # если применимо
}
```

---

## 📊 Предиктивная аналитика

### Анализ тренда веса

```python
from datetime import datetime, timedelta

weight_history = [
    {'date': (datetime.now() - timedelta(days=i*7)).strftime('%Y-%m-%d'), 
     'weight': 88.0 - i*0.7}
    for i in range(5)
]

analysis = engine.get_weight_analysis(user_id=1, weight_history=weight_history)

print(f"Текущий вес: {analysis['current_weight']} кг")
print(f"Тренд: {analysis['trend_description']}")
print(f"Изменение за неделю: {analysis['weekly_change']} кг")
print(f"Прогноз на 30 дней: {analysis['forecast']['30_days']} кг")
```

### Прогноз достижения цели

```python
prediction = engine.predict_goal_achievement(
    user_id=1,
    goal_weight=75.0,
    daily_calorie_deficit=500
)

print(f"Недель до цели: {prediction['weeks_to_goal']}")
print(f"Дата достижения: {prediction['estimated_goal_date']}")
print(f"Реалистично: {prediction['is_realistic']}")
```

### Обнаружение плато

```python
plateau_history = [
    {'date': (datetime.now() - timedelta(days=i*2)).strftime('%Y-%m-%d'), 
     'weight': 82.0 + (i%2)*0.1}
    for i in range(8)
]

plateau = engine.detect_plateau(user_id=1, weight_history=plateau_history)

if plateau['plateau_detected']:
    print("⚠️ Обнаружено плато!")
    print("Рекомендации:", plateau['recommendations'])
```

---

## 🍳 Генератор рецептов

### Генерация рецепта

```python
# Завтрак
recipe = engine.generate_recipe(user_id=1, category='breakfast')
print(f"Название: {recipe['name']}")
print(f"Калории: {recipe['nutrition']['calories']} ккал")
print(f"БЖУ: Б={recipe['nutrition']['protein']}г, Ж={recipe['nutrition']['fat']}г, У={recipe['nutrition']['carbs']}г")
print(f"Ингредиенты: {recipe['ingredients']}")
print(f"Инструкции: {recipe['instructions']}")
```

### Категории рецептов
- `breakfast` — завтрак
- `lunch` — обед
- `dinner` — ужин
- `snack` — перекус

### Замены ингредиентов

```python
substitutions = engine.suggest_substitutions(
    ingredient='молоко',
    user_id=1  # учтёт ограничения пользователя
)
print(f"Замены для молока: {substitutions}")
# Вывод: ['миндальное молоко', 'овсяное молоко', 'кокосовое молоко']
```

### План питания на неделю

```python
weekly_plan = engine.generate_weekly_plan(user_id=1, days=7)
for day, meals in weekly_plan.items():
    print(f"{day}:")
    for meal_type, recipe in meals.items():
        print(f"  {meal_type}: {recipe['name']}")
```

---

## 📈 Рекомендации

### Получение персональных рекомендаций

```python
recommendations = engine.get_recommendations(user_id=1)

for rec in recommendations:
    print(f"[{rec['priority']}] {rec['title']}")
    print(f"  {rec['message']}")
```

### Типы рекомендаций
- `plateau_alert` — предупреждение о плато
- `nutrition_tip` — совет по питанию
- `motivation` — мотивационное сообщение

---

## 📋 Общая сводка

```python
summary = engine.get_ai_summary(user_id=1)

print(f"Статус: {summary['user_status']}")
print(f"Замеров веса: {summary['statistics']['weight_measurements']}")
print(f"Приёмов пищи: {summary['statistics']['meals_logged']}")
print(f"Сообщений в чате: {summary['statistics']['conversation_messages']}")

if 'weight_trend' in summary:
    print(f"Тренд веса: {summary['weight_trend']}")
```

---

## 🔧 Дополнительные функции

### Добавление данных в историю

```python
# Добавить приём пищи
engine.add_meal_to_history(user_id=1, meal_data={
    'date': datetime.now().isoformat(),
    'calories': 450,
    'protein': 30,
    'carbs': 45,
    'fat': 15
})

# Добавить замер веса
engine.add_weight_measurement(
    user_id=1,
    weight=79.5,
    date=datetime.now().strftime('%Y-%m-%d')
)
```

### Оптимизация калорий для цели

```python
optimization = engine.optimize_nutrition(
    user_id=1,
    goal={
        'target_weight': 70,
        'timeframe_weeks': 12
    }
)

print(f"Оптимальные калории: {optimization['optimal_calories']}")
print(f"БЖУ: {optimization['macros']}")
```

---

## 🎯 Особенности реализации

### Чат-бот
- Распознавание намерений через паттерны
- База знаний о макронутриентах, витаминах, диетах
- Персонализация на основе профиля пользователя
- Контекстная память (последние 50 сообщений)

### Предиктивная аналитика
- Линейная регрессия для анализа трендов
- Статистический анализ (scipy.stats)
- Прогнозирование с оценкой уверенности
- Обнаружение плато через анализ вариативности

### Генератор рецептов
- Учёт диетических ограничений
- Персонализация по предпочтениям
- Баланс макронутриентов
- Разнообразие ингредиентов

---

## 📝 Примечания

1. **Все данные хранятся локально** — не требуется интернет
2. **Многопользовательская поддержка** — каждый пользователь имеет свой контекст
3. **Автоматическая очистка** — история ограничена последними записями
4. **Расширяемость** — легко добавить новые типы рекомендаций или шаблоны

---

## 🔮 Планы развития

- [ ] Интеграция с распознаванием еды по фото
- [ ] Более сложные ML-модели для рекомендаций
- [ ] Адаптивное обучение на основе обратной связи
- [ ] Интеграция с носимыми устройствами
- [ ] Социальные функции (семейные аккаунты)

---

## 📄 Лицензия

Часть проекта HealthAI
