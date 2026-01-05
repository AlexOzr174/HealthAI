# Расчёт калорий и БЖУ по формулам
from dataclasses import dataclass
from typing import Optional

@dataclass
class UserMetrics:
    """Метрики пользователя для расчётов"""
    gender: str  # 'male' или 'female'
    age: int
    height: float  # в см
    weight: float  # в кг
    activity_level: str
    goal: str

# Коэффициенты активности
ACTIVITY_MULTIPLIERS = {
    'sedentary': 1.2,      # Минимальная активность (сидячая работа)
    'light': 1.375,        # Лёгкая активность (1-3 тренировки в неделю)
    'moderate': 1.55,      # Умеренная активность (3-5 тренировок)
    'active': 1.725,       # Высокая активность (6-7 тренировок)
    'very_active': 1.9,    # Очень высокая активность (тяжёлый труд/спорт)
}

# Модификаторы цели
GOAL_MODIFIERS = {
    'lose': -0.15,     # Похудение: -15% от TDEE
    'maintain': 0.0,   # Поддержание
    'gain': 0.15,      # Набор массы: +15% от TDEE
}

# Рекомендуемые пропорции БЖУ
MACRO_RATIOS = {
    'balanced': {'protein': 0.25, 'fat': 0.25, 'carbs': 0.50},
    'low_carb': {'protein': 0.35, 'fat': 0.35, 'carbs': 0.30},
    'high_carb': {'protein': 0.20, 'fat': 0.20, 'carbs': 0.60},
    'high_protein': {'protein': 0.40, 'fat': 0.20, 'carbs': 0.40},
}

# Калорийность на грамм макронутриента
MACRO_CALORIES = {
    'protein': 4.0,    # Белки: 4 ккал/г
    'fat': 9.0,        # Жиры: 9 ккал/г
    'carbs': 4.0,      # Углеводы: 4 ккал/г
}


def calculate_bmr(gender: str, age: int, height: float, weight: float) -> float:
    """
    Расчёт базального метаболизма по формуле Миффлина-Сан Жеора.

    Формула:
    - Мужчины: BMR = 10 × вес(кг) + 6.25 × рост(см) - 5 × возраст + 5
    - Женщины: BMR = 10 × вес(кг) + 6.25 × рост(см) - 5 × возраст - 161

    Args:
        gender: Пол ('male' или 'female')
        age: Возраст в годах
        height: Рост в сантиметрах
        weight: Вес в килограммах

    Returns:
        Базальный метаболизм в ккал/день
    """
    bmr = (10 * weight) + (6.25 * height) - (5 * age)

    if gender.lower() == 'male':
        bmr += 5
    else:
        bmr -= 161

    return round(bmr, 1)


def calculate_tdee(bmr: float, activity_level: str) -> float:
    """
    Расчёт суточного расхода энергии (TDEE).

    TDEE = BMR × коэффициент активности

    Args:
        bmr: Базальный метаболизм
        activity_level: Уровень активности

    Returns:
        Суточный расход энергии в ккал
    """
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
    return round(bmr * multiplier, 1)


def calculate_target_calories(tdee: float, goal: str) -> float:
    """
    Расчёт целевого количества калорий с учётом цели.

    Args:
        tdee: Суточный расход энергии
        goal: Цель ('lose', 'maintain', 'gain')

    Returns:
        Целевые калории
    """
    modifier = GOAL_MODIFIERS.get(goal, 0.0)
    target = tdee * (1 + modifier)
    return round(target, 0)


def calculate_macros(target_calories: float, ratio_name: str = 'balanced') -> dict:
    """
    Расчёт рекомендуемого количества БЖУ.

    Args:
        target_calories: Целевые калории
        ratio_name: Название пропорции ('balanced', 'low_carb', 'high_carb', 'high_protein')

    Returns:
        Словарь с граммами белков, жиров и углеводов
    """
    ratios = MACRO_RATIOS.get(ratio_name, MACRO_RATIOS['balanced'])

    protein_grams = (target_calories * ratios['protein']) / MACRO_CALORIES['protein']
    fat_grams = (target_calories * ratios['fat']) / MACRO_CALORIES['fat']
    carbs_grams = (target_calories * ratios['carbs']) / MACRO_CALORIES['carbs']

    return {
        'protein': round(protein_grams, 1),
        'fat': round(fat_grams, 1),
        'carbs': round(carbs_grams, 1),
        'protein_pct': round(ratios['protein'] * 100, 1),
        'fat_pct': round(ratios['fat'] * 100, 1),
        'carbs_pct': round(ratios['carbs'] * 100, 1),
    }


class MacroCalculator:
    """Класс для расчёта макронутриентов"""

    def __init__(self, user_metrics: UserMetrics):
        self.metrics = user_metrics
        self.bmr = calculate_bmr(
            user_metrics.gender,
            user_metrics.age,
            user_metrics.height,
            user_metrics.weight
        )
        self.tdee = calculate_tdee(self.bmr, user_metrics.activity_level)
        self.target_calories = calculate_target_calories(self.tdee, user_metrics.goal)
        self.macros = calculate_macros(self.target_calories)

    def get_summary(self) -> dict:
        """Получение полной сводки расчётов"""
        return {
            'bmr': self.bmr,
            'tdee': self.tdee,
            'target_calories': self.target_calories,
            'macros': self.macros,
            'activity_level': self.metrics.activity_level,
            'goal': self.metrics.goal,
        }

    def get_calorie_breakdown(self, meal_count: int = 4) -> dict:
        """
        Получение распределения калорий по приёмам пищи.

        Args:
            meal_count: Количество приёмов пищи

        Returns:
            Словарь с распределением калорий
        """
        # Типичное распределение: завтрак 25%, обед 35%, ужин 30%, перекусы 10%
        if meal_count == 3:
            ratios = {'breakfast': 0.30, 'lunch': 0.40, 'dinner': 0.30}
        elif meal_count == 5:
            ratios = {'breakfast': 0.25, 'lunch': 0.30, 'dinner': 0.25, 'snack_1': 0.10, 'snack_2': 0.10}
        else:
            # 4 приёма пищи
            ratios = {'breakfast': 0.25, 'lunch': 0.35, 'dinner': 0.30, 'snack': 0.10}

        return {
            meal: round(self.target_calories * ratio, 0)
            for meal, ratio in ratios.items()
        }


def calculate_product_macros(product: dict, amount_grams: float) -> dict:
    """
    Расчёт калорийности продукта на основе количества.

    Args:
        product: Словарь с данными о продукте (calories, protein, fat, carbs на 100г)
        amount_grams: Количество в граммах

    Returns:
        Словарь с рассчитанными значениями
    """
    factor = amount_grams / 100

    return {
        'calories': round(product['calories'] * factor, 1),
        'protein': round(product['protein'] * factor, 1),
        'fat': round(product['fat'] * factor, 1),
        'carbs': round(product['carbs'] * factor, 1),
        'amount': amount_grams,
        'name': product['name'],
    }


def get_calorie_category(calories: int) -> str:
    """
    Определение категории калорийности блюда.

    Args:
        calories: Количество калорий

    Returns:
        Категория: 'low', 'medium', 'high'
    """
    if calories < 200:
        return 'low'      # Низкокалорийное
    elif calories < 500:
        return 'medium'   # Среднекалорийное
    else:
        return 'high'     # Высококалорийное
