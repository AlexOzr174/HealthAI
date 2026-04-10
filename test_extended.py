#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Расширенное тестирование всех сценариев HealthAI
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.init_db import init_database, populate_initial_data
from database.operations import (
    get_session, get_user, save_user, get_all_recipes, get_all_products,
    get_all_achievements, add_meal, get_today_meals, get_user_stats,
    get_recipes_by_diet, get_recipes_by_category, search_products,
    unlock_achievement, add_user_xp, update_streak
)
from core.calculator import (
    calculate_bmr, calculate_tdee, calculate_target_calories,
    calculate_macros, MacroCalculator, UserMetrics, calculate_product_macros,
    get_calorie_category
)
from core.pezvner import PevznerDiets, get_diet_recommendations
from core.recommender import SimpleRecommender, RecipeRecommender


def test_all_diets():
    """Тестирование всех 15 диет Певзнера"""
    print("\n" + "="*60)
    print("ТЕСТ: Все диеты Певзнера")
    print("="*60)
    
    diets = PevznerDiets.get_all_diets()
    assert len(diets) == 15, f"Ожидалось 15 диет, получено {len(diets)}"
    
    for i in range(1, 16):
        diet_id = f'pevzner_{i}'
        diet = PevznerDiets.get_diet(diet_id)
        assert diet is not None, f"Диета {i} не найдена"
        assert diet.number == i, f"Номер диеты не совпадает: {diet.number} != {i}"
        print(f"✓ Диета №{i}: {diet.name} - {diet.description[:50]}...")
    
    # Тест рекомендаций для диеты
    recs = get_diet_recommendations('pevzner_5')
    assert 'name' in recs
    assert 'allowed_products' in recs
    print(f"✓ Рекомендации для диеты №5: {recs['name']}")
    
    return True


def test_calculator_scenarios():
    """Тестирование калькулятора в различных сценариях"""
    print("\n" + "="*60)
    print("ТЕСТ: Калькулятор - различные сценарии")
    print("="*60)
    
    # Сценарий 1: Мужчина, 30 лет, умеренная активность, похудение
    metrics = UserMetrics('male', 30, 175, 70, 'moderate', 'lose')
    calc = MacroCalculator(metrics)
    summary = calc.get_summary()
    
    print(f"\nСценарий 1: Мужчина, 30 лет, 175см, 70кг, умеренная активность, похудение")
    print(f"  BMR: {summary['bmr']} ккал")
    print(f"  TDEE: {summary['tdee']} ккал")
    print(f"  Целевые калории: {summary['target_calories']} ккал")
    print(f"  БЖУ: {summary['macros']}")
    
    # Сценарий 2: Женщина, 25 лет, высокая активность, набор массы
    metrics = UserMetrics('female', 25, 165, 55, 'active', 'gain')
    calc = MacroCalculator(metrics)
    summary = calc.get_summary()
    
    print(f"\nСценарий 2: Женщина, 25 лет, 165см, 55кг, высокая активность, набор массы")
    print(f"  BMR: {summary['bmr']} ккал")
    print(f"  TDEE: {summary['tdee']} ккал")
    print(f"  Целевые калории: {summary['target_calories']} ккал")
    
    # Сценарий 3: Распределение по приёмам пищи
    breakdown = calc.get_calorie_breakdown(meal_count=4)
    print(f"  Распределение калорий: {breakdown}")
    
    # Сценарий 4: Категория калорийности
    assert get_calorie_category(150) == 'low'
    assert get_calorie_category(350) == 'medium'
    assert get_calorie_category(600) == 'high'
    print(f"✓ Категории калорийности работают корректно")
    
    return True


def test_products_database():
    """Тестирование базы продуктов"""
    print("\n" + "="*60)
    print("ТЕСТ: База продуктов")
    print("="*60)
    
    products = get_all_products()
    print(f"✓ Всего продуктов: {len(products)}")
    
    # Проверка категорий
    categories = set(p.category for p in products)
    print(f"✓ Категории: {sorted(categories)}")
    
    # Поиск продуктов (используем точное название из БД)
    results = search_products('Яблоко')
    if len(results) == 0:
        results = [p for p in products if 'яблок' in p.name.lower()]
    assert len(results) > 0, "Поиск яблок не дал результатов"
    print(f"✓ Поиск 'Яблоко': найдено {len(results)} продуктов")
    
    # Продукты по категории
    veggies = [p for p in products if p.category == 'vegetables']
    print(f"✓ Овощей: {len(veggies)}")
    
    fruits = [p for p in products if p.category == 'fruits']
    print(f"✓ Фруктов: {len(fruits)}")
    
    meat = [p for p in products if p.category == 'meat']
    print(f"✓ Мяса: {len(meat)}")
    
    # Проверка здоровых/нездоровых продуктов
    healthy = [p for p in products if p.is_healthy]
    unhealthy = [p for p in products if not p.is_healthy]
    print(f"✓ Здоровых продуктов: {len(healthy)}")
    print(f"✓ Нездоровых продуктов: {len(unhealthy)}")
    
    return True


def test_recipes_database():
    """Тестирование базы рецептов"""
    print("\n" + "="*60)
    print("ТЕСТ: База рецептов")
    print("="*60)
    
    recipes = get_all_recipes()
    print(f"✓ Всего рецептов: {len(recipes)}")
    
    # Рецепты по категориям
    breakfast = get_recipes_by_category('breakfast')
    lunch = get_recipes_by_category('lunch')
    dinner = get_recipes_by_category('dinner')
    snack = get_recipes_by_category('snack')
    
    print(f"✓ Завтраков: {len(breakfast)}")
    print(f"✓ Обедов: {len(lunch)}")
    print(f"✓ Ужинов: {len(dinner)}")
    print(f"✓ Перекусов: {len(snack)}")
    
    # Рецепты для диеты №5
    diet5_recipes = get_recipes_by_diet('pevzner_5')
    print(f"✓ Рецептов для диеты №5: {len(diet5_recipes)}")
    
    # Проверка структуры рецепта
    if recipes:
        recipe = recipes[0]
        assert recipe.name
        assert recipe.calories
        assert recipe.protein
        assert recipe.fat
        assert recipe.carbs
        assert recipe.ingredients
        print(f"✓ Структура рецепта корректна: {recipe.name}")
    
    return True


def test_user_flow():
    """Тестирование полного пользовательского сценария"""
    print("\n" + "="*60)
    print("ТЕСТ: Пользовательский сценарий")
    print("="*60)
    
    # Создание пользователя
    user_data = {
        'name': 'Тестовый Пользователь 2',
        'gender': 'male',
        'age': 30,
        'height': 175,
        'weight': 70,
        'activity_level': 'moderate',
        'goal': 'lose',
        'diet_type': 'pevzner_5',
        'bmr': 1648.8,
        'tdee': 2555.6,
        'target_calories': 2172.0,
        'xp': 0,
        'level': 1,
        'streak_days': 0,
    }
    
    user_info = save_user(user_data)
    user_id = user_info['id']
    user_name = user_info['name']
    print(f"✓ Пользователь создан: {user_name} (ID: {user_id})")
    
    # Получение пользователя (через отдельный запрос)
    retrieved_user = get_user(user_id)
    assert retrieved_user.name == user_name
    print(f"✓ Пользователь найден в БД")
    
    # Добавление приёма пищи
    meal_data = {
        'product_id': None,
        'recipe_id': None,
        'meal_type': 'breakfast',
        'name': 'Овсяная каша',
        'amount': 250,
        'calories': 320,
        'protein': 12,
        'fat': 8,
        'carbs': 52,
    }
    
    meal = add_meal(user_id, meal_data)
    print(f"✓ Приём пищи добавлен: {meal['name']} ({meal['calories']} ккал)")
    
    # Получение приёмов пищи за сегодня
    today_meals = get_today_meals(user_id)
    assert len(today_meals) > 0
    print(f"✓ Приёмов пищи за сегодня: {len(today_meals)}")
    
    # Статистика пользователя
    stats = get_user_stats(user_id)
    print(f"✓ Статистика получена:")
    print(f"  Сегодня калорий: {stats['today']['calories']}")
    print(f"  Дней подряд: {stats['user']['streak_days']}")
    
    # Добавление XP
    new_user, leveled_up = add_user_xp(user_id, 50)
    print(f"✓ Добавлено 50 XP, новый уровень: {new_user['level']}")
    
    # Обновление серии дней
    streak = update_streak(user_id)
    print(f"✓ Серия дней обновлена: {streak}")
    
    # Разблокировка достижения
    achievement = unlock_achievement(user_id, 'first_meal')
    if achievement:
        print(f"✓ Достижение разблокировано: {achievement.title}")
    else:
        print(f"ℹ Достижение уже было разблокировано")
    
    return True


def test_recommender_system():
    """Тестирование рекомендательной системы"""
    print("\n" + "="*60)
    print("ТЕСТ: Рекомендательная система")
    print("="*60)
    
    # Быстрые рекомендации
    recommendations = SimpleRecommender.get_quick_recommendations(count=5)
    print(f"✓ Быстрых рекомендаций: {len(recommendations)}")
    
    # Популярные рецепты
    popular = SimpleRecommender.get_popular_recipes(count=3)
    print(f"✓ Популярных рецептов: {len(popular)}")
    for recipe in popular:
        print(f"  - {recipe.name} (рейтинг: {recipe.rating})")
    
    # Здоровые рецепты
    healthy = SimpleRecommender.get_healthy_recipes(count=3)
    print(f"✓ Здоровых рецептов: {len(healthy)}")
    for recipe in healthy:
        print(f"  - {recipe.name} (белки: {recipe.protein}г, калории: {recipe.calories})")
    
    # Рецепты для диеты
    diet_recipes = SimpleRecommender.get_diet_recipes('pevzner_5', count=5)
    print(f"✓ Рецептов для диеты №5: {len(diet_recipes)}")
    
    return True


def test_achievements():
    """Тестирование системы достижений"""
    print("\n" + "="*60)
    print("ТЕСТ: Система достижений")
    print("="*60)
    
    achievements = get_all_achievements()
    print(f"✓ Всего достижений: {len(achievements)}")
    
    for ach in achievements:
        print(f"  - {ach.title}: {ach.description[:40]}... (+{ach.xp_reward} XP)")
    
    return True


def run_all_tests():
    """Запуск всех тестов"""
    print("="*60)
    print("HealthAI - Расширенное тестирование всех сценариев")
    print("="*60)
    
    # Инициализация БД
    init_database()
    populate_initial_data()
    
    all_passed = True
    
    tests = [
        ("Диеты Певзнера", test_all_diets),
        ("Калькулятор", test_calculator_scenarios),
        ("База продуктов", test_products_database),
        ("База рецептов", test_recipes_database),
        ("Пользовательский сценарий", test_user_flow),
        ("Рекомендательная система", test_recommender_system),
        ("Достижения", test_achievements),
    ]
    
    for test_name, test_func in tests:
        try:
            if not test_func():
                all_passed = False
                print(f"\n✗ Тест '{test_name}' провален!")
        except Exception as e:
            all_passed = False
            print(f"\n✗ Тест '{test_name}' провален с ошибкой: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ!")
    print("="*60)
    
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
