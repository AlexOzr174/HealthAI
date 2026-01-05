#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый файл для проверки структуры приложения HealthAI
"""

import sys
import os

from core import get_diet_recommendations

# Добавление пути к модулям
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Тест импорта всех модулей"""
    print("Тестирование импортов модулей...")

    try:
        from config.settings import APP_NAME, APP_VERSION, COLORS, GOALS
        print(f"✓ config: {APP_NAME} v{APP_VERSION}")
    except Exception as e:
        print(f"✗ config: {e}")
        return False

    try:
        from database.models import User, Product, Recipe, Meal
        print("✓ database.models: Модели загружены")
    except Exception as e:
        print(f"✗ database.models: {e}")
        return False

    try:
        from database.operations import get_session, get_user, get_all_recipes
        print("✓ database.operations: Операции загружены")
    except Exception as e:
        print(f"✗ database.operations: {e}")
        return False

    try:
        from core.calculator import calculate_bmr, calculate_tdee, calculate_target_calories
        print("✓ core.calculator: Калькулятор загружен")
    except Exception as e:
        print(f"✗ core.calculator: {e}")
        return False

    try:
        from core.pezvner import PevznerDiets, get_diet_recommendations
        print("✓ core.pezvner: Диеты Певзнера загружены")
    except Exception as e:
        print(f"✗ core.pezvner: {e}")
        return False

    try:
        from core.recommender import RecipeRecommender, SimpleRecommender
        print("✓ core.recommender: Рекомендательная система загружена")
    except Exception as e:
        print(f"✗ core.recommender: {e}")
        return False

    return True


def test_calculator():
    """Тест функций калькулятора"""
    print("\nТестирование калькулятора...")

    from core.calculator import calculate_bmr, calculate_tdee, calculate_target_calories

    # Тест расчёта BMR
    bmr = calculate_bmr('male', 30, 175, 70)
    expected = (10 * 70) + (6.25 * 175) - (5 * 30) + 5
    assert abs(bmr - expected) < 0.1, f"BMR mismatch: {bmr} != {expected}"
    print(f"✓ BMR (мужчина, 30 лет, 175см, 70кг): {bmr} ккал")

    bmr = calculate_bmr('female', 25, 165, 55)
    expected = (10 * 55) + (6.25 * 165) - (5 * 25) - 161
    assert abs(bmr - expected) < 0.1, f"BMR mismatch: {bmr} != {expected}"
    print(f"✓ BMR (женщина, 25 лет, 165см, 55ккг): {bmr} ккал")

    # Тест расчёта TDEE
    tdee = calculate_tdee(1700, 'moderate')
    expected = 1700 * 1.55
    assert abs(tdee - expected) < 0.1, f"TDEE mismatch: {tdee} != {expected}"
    print(f"✓ TDEE (BMR=1700, умеренная активность): {tdee} ккал")

    # Тест целевых калорий
    target = calculate_target_calories(2000, 'lose')
    expected = 2000 * 0.85
    assert abs(target - expected) < 0.1, f"Target calories mismatch: {target} != {expected}"
    print(f"✓ Target (TDEE=2000, похудение): {target} ккал")

    return True


def test_pezvner():
    """Тест диет Певзнера"""
    print("\nТестирование диет Певзнера...")

    from core.pezvner import PevznerDiets

    # Получение всех диет
    diets = PevznerDiets.get_all_diets()
    assert len(diets) == 15, f"Expected 15 diets, got {len(diets)}"
    print(f"✓ Загружено диет: {len(diets)}")

    # Тест конкретной диеты
    diet_5 = PevznerDiets.get_diet('pevzner_5')
    assert diet_5 is not None, "Diet 5 not found"
    assert diet_5.number == 5, "Diet number mismatch"
    print(f"✓ Диета №5: {diet_5.name}")

    # Тест получения рекомендаций
    recs = get_diet_recommendations('pevzner_5')
    assert 'name' in recs, "Recommendations missing 'name'"
    assert 'allowed_products' in recs, "Recommendations missing 'allowed_products'"
    print(f"✓ Рекомендации для диеты №5 получены")

    return True


def test_recommender():
    """Тест рекомендательной системы"""
    print("\nТестирование рекомендательной системы...")

    from core.recommender import SimpleRecommender

    # Тест получения рекомендаций
    recipes = SimpleRecommender.get_quick_recommendations(count=5)
    print(f"✓ Получено рекомендаций: {len(recipes)}")

    # Тест популярных рецептов
    popular = SimpleRecommender.get_popular_recipes(count=3)
    print(f"✓ Популярных рецептов: {len(popular)}")

    # Тест здоровых рецептов
    healthy = SimpleRecommender.get_healthy_recipes(count=3)
    print(f"✓ Здоровых рецептов: {len(healthy)}")

    return True


def test_database():
    """Тест базы данных"""
    print("\nТестирование базы данных...")

    from database.init_db import init_database, populate_initial_data
    from database.operations import get_session, get_all_recipes, get_all_achievements

    # Инициализация БД
    init_database()
    print("✓ База данных инициализирована")

    # Заполнение данными
    populate_initial_data()
    print("✓ Начальные данные загружены")

    # Проверка рецептов
    recipes = get_all_recipes()
    assert len(recipes) > 0, "No recipes loaded"
    print(f"✓ Рецептов в базе: {len(recipes)}")

    # Проверка достижений
    achievements = get_all_achievements()
    assert len(achievements) > 0, "No achievements loaded"
    print(f"✓ Достижений в базе: {len(achievements)}")

    return True


def run_tests():
    """Запуск всех тестов"""
    print("=" * 60)
    print("HealthAI - Тестирование структуры приложения")
    print("=" * 60)

    all_passed = True

    # Тест импортов
    if not test_imports():
        all_passed = False
        print("\n✗ Тесты импортов провалены!")

    # Тест калькулятора
    if not test_calculator():
        all_passed = False
        print("\n✗ Тесты калькулятора провалены!")

    # Тест диет Певзнера
    if not test_pezvner():
        all_passed = False
        print("\n✗ Тесты диет Певзнера провалены!")

    # Тест рекомендательной системы
    if not test_recommender():
        all_passed = False
        print("\n✗ Тесты рекомендательной системы провалены!")

    # Тест базы данных
    if not test_database():
        all_passed = False
        print("\n✗ Тесты базы данных провалены!")

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ Все тесты пройдены успешно!")
    else:
        print("✗ Некоторые тесты провалены!")
    print("=" * 60)

    return all_passed


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
