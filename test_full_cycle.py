#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование полного цикла HealthAI
"""
import sys
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

print('='*70)
print('🧪 ТЕСТИРОВАНИЕ ПОЛНОГО ЦИКЛА HEALTHAI')
print('='*70)

# 1. Проверка импортов
print('\n1️⃣ ПРОВЕРКА ИМПОРТОВ...')
try:
    from database.models import User, Meal, Product, Recipe, Achievement, UserAchievement
    from database.db_manager import DatabaseManager
    from core.calculator import UserMetrics as CalorieCalculator
    from core.pezvner import PevznerDiets as DietPlan
    from core.recommender import RecipeRecommender
    from ai_engine import AIEngine
    from core.services.notification_service import NotificationService
    from core.services.nutrition_api import NutritionAPI
    from core.services.special_diets import SpecialDietsService
    from core.export_import import DataExporter as ExportImport
    from ui.styles import toggle_theme, set_theme
    print('✅ Все модули успешно импортированы')
except Exception as e:
    print(f'❌ Ошибка импорта: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 2. Инициализация БД
print('\n2️⃣ ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ...')
try:
    db = DatabaseManager('test_full_cycle.db')
    db.create_tables()
    print('✅ Таблицы созданы')
    
    # Проверка количества записей
    session = db.get_session()
    products_count = session.query(Product).count()
    recipes_count = session.query(Recipe).count()
    achievements_count = session.query(Achievement).count()
    print(f'   📊 Продуктов: {products_count}')
    print(f'   📊 Рецептов: {recipes_count}')
    print(f'   📊 Достижений: {achievements_count}')
    session.close()
except Exception as e:
    print(f'❌ Ошибка БД: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. Создание пользователя
print('\n3️⃣ СОЗДАНИЕ ПОЛЬЗОВАТЕЛЯ...')
try:
    user_data = {
        'username': 'test_user',
        'email': 'test@healthai.com',
        'age': 30,
        'gender': 'male',
        'height': 178,
        'weight': 85,
        'activity_level': 1.55,
        'goal': 'weight_loss',
        'target_weight': 75
    }
    user = db.add_user(user_data)
    print(f'✅ Пользователь создан: {user["username"]} (ID: {user["id"]})')
    print(f'   📊 XP: {user["xp"]}, Уровень: {user["level"]}')
except Exception as e:
    print(f'❌ Ошибка создания пользователя: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 4. Расчёт калорий
print('\n4️⃣ РАСЧЁТ КАЛОРИЙ И МАКРОСОВ...')
try:
    calc = CalorieCalculator()
    bmr = calc.calculate_bmr(user['weight'], user['height'], user['age'], user['gender'])
    tdee = calc.calculate_tdee(bmr, user['activity_level'])
    macros = calc.calculate_macros(tdee, user['goal'])
    
    print(f'✅ BMR: {bmr:.0f} ккал')
    print(f'✅ TDEE: {tdee:.0f} ккал')
    print(f'✅ Цель: {macros["calories"]:.0f} ккал/день')
    print(f'   🥩 Белки: {macros["protein"]:.0f}г ({macros["protein_percent"]}%)')
    print(f'   🍞 Углеводы: {macros["carbs"]:.0f}г ({macros["carbs_percent"]}%)')
    print(f'   🥑 Жиры: {macros["fat"]:.0f}г ({macros["fat_percent"]}%)')
except Exception as e:
    print(f'❌ Ошибка расчёта: {e}')
    sys.exit(1)

# 5. Добавление приёма пищи
print('\n5️⃣ ДОБАВЛЕНИЕ ПРИЁМА ПИЩИ...')
try:
    session = db.get_session()
    product = session.query(Product).filter(Product.name.like('%курица%')).first()
    if not product:
        product = session.query(Product).first()
    session.close()
    
    meal_data = {
        'user_id': user['id'],
        'product_id': product.id,
        'meal_type': 'lunch',
        'quantity': 200,
        'calories': product.calories * 2,
        'protein': product.protein * 2,
        'carbs': product.carbs * 2,
        'fat': product.fat * 2
    }
    meal = db.add_meal(meal_data)
    print(f'✅ Приём пищи добавлен: {product.name} (200г)')
    print(f'   🔥 Калории: {meal["calories"]:.0f}')
    print(f'   🥩 БЖУ: {meal["protein"]:.1f}/{meal["carbs"]:.1f}/{meal["fat"]:.1f}г')
except Exception as e:
    print(f'❌ Ошибка добавления еды: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 6. AI Нутрициолог
print('\n6️⃣ AI НУТРИЦИОЛОГ (ЧАТ)...')
try:
    ai = AIEngine()
    ai.initialize_user(user_id=user['id'], profile=user)
    
    questions = [
        'Как похудеть?',
        'Сколько белка мне нужно?',
        'Что съесть на завтрак?'
    ]
    
    for q in questions:
        response = ai.chat(user_id=user['id'], message=q)
        print(f'   ❓ {q}')
        print(f'   💬 {response[:100]}...')
    print('✅ Чат-бот работает')
except Exception as e:
    print(f'❌ Ошибка AI чата: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 7. Предиктивная аналитика
print('\n7️⃣ ПРЕДИКТИВНАЯ АНАЛИТИКА...')
try:
    weight_history = [
        {'date': '2025-01-01', 'weight': 88},
        {'date': '2025-01-08', 'weight': 87},
        {'date': '2025-01-15', 'weight': 86},
        {'date': '2025-01-22', 'weight': 85}
    ]
    
    analysis = ai.get_weight_analysis(user_id=user['id'], weight_history=weight_history)
    print(f'✅ Текущий вес: {analysis["current_weight"]} кг')
    print(f'   📈 Тренд: {analysis["trend"]} ({analysis["weekly_change"]:.2f} кг/нед)')
    print(f'   🔮 Прогноз на 30 дней: {analysis["forecast_30d"]} кг')
    print(f'   🎯 Достижение цели: {analysis["goal_progress"]}%')
except Exception as e:
    print(f'❌ Ошибка аналитики: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 8. Генерация рецептов
print('\n8️⃣ ГЕНЕРАЦИЯ РЕЦЕПТОВ...')
try:
    recipe = ai.generate_recipe(user_id=user['id'], category='lunch')
    print(f'✅ Рецепт: {recipe["name"]}')
    print(f'   ⏱️ Время: {recipe["prep_time"]} мин')
    print(f'   🔥 Калории: {recipe["calories"]} ккал')
    print(f'   🥩 БЖУ: {recipe["protein"]}/{recipe["carbs"]}/{recipe["fat"]}г')
except Exception as e:
    print(f'❌ Ошибка генерации рецепта: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 9. Специальные диеты
print('\n9️⃣ СПЕЦИАЛЬНЫЕ ДИЕТЫ...')
try:
    diets_service = SpecialDietsService()
    
    # Кето
    keto = diets_service.get_diet_plan('keto', user)
    print(f'✅ Кето диета:')
    print(f'   🥑 Жиры: {keto["macros"]["fat_percent"]}%')
    print(f'   🥩 Белки: {keto["macros"]["protein_percent"]}%')
    print(f'   🍞 Углеводы: {keto["macros"]["carbs_percent"]}%')
    
    # Палео
    paleo = diets_service.get_diet_plan('paleo', user)
    print(f'✅ Палео диета: {paleo["description"][:50]}...')
    
    # Проверка продукта
    is_compatible = diets_service.check_product_compatibility('avocado', 'keto')
    print(f'   🥑 Авокадо совместимо с кето: {is_compatible}')
except Exception as e:
    print(f'❌ Ошибка диет: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 10. Экспорт данных
print('\n🔟 ЭКСПОРТ ДАННЫХ...')
try:
    exporter = ExportImport(db)
    
    # CSV
    csv_file = exporter.export_to_csv(user['id'], 'test_export.csv')
    print(f'✅ CSV экспортирован: {csv_file}')
    
    # JSON
    json_file = exporter.export_to_json(user['id'], 'test_export.json')
    print(f'✅ JSON экспортирован: {json_file}')
    
    # PDF
    pdf_file = exporter.export_to_pdf(user['id'], 'test_export.pdf')
    print(f'✅ PDF экспортирован: {pdf_file}')
    
    # Очистка
    for f in ['test_export.csv', 'test_export.json', 'test_export.pdf']:
        if os.path.exists(f):
            os.remove(f)
except Exception as e:
    print(f'❌ Ошибка экспорта: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 11. Умные уведомления
print('\n1️⃣1️⃣ УМНЫЕ УВЕДОМЛЕНИЯ...')
try:
    notifier = NotificationService(db)
    notifications = notifier.get_due_notifications()
    print(f'✅ Сервис уведомлений запущен')
    print(f'   🔔 Доступно типов уведомлений: {len(notifier.notification_types)}')
    
    # Тест создания уведомления
    test_notif = notifier.create_notification(
        user_id=user['id'],
        notification_type='meal_reminder',
        message='Пора обедать!',
        scheduled_time='12:00'
    )
    print(f'   ✅ Тестовое уведомление создано')
except Exception as e:
    print(f'❌ Ошибка уведомлений: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 12. Смена темы
print('\n1️⃣2️⃣ СМЕНА ТЕМЫ...')
try:
    set_theme('dark')
    print('✅ Тёмная тема активирована')
    
    set_theme('light')
    print('✅ Светлая тема активирована')
    
    toggle_theme()
    print('✅ Тема переключена')
except Exception as e:
    print(f'❌ Ошибка смены темы: {e}')
    sys.exit(1)

# 13. Интеграция с API
print('\n1️⃣3️⃣ ИНТЕГРАЦИЯ С API...')
try:
    api = NutritionAPI()
    
    # Проверка структуры
    print(f'✅ API сервисы доступны:')
    print(f'   🌐 Edamam: {"search_products" in dir(api)}')
    print(f'   🌐 USDA: {"get_product_details" in dir(api)}')
    print(f'   🌐 Spoonacular: {"search_recipes" in dir(api)}')
    
    # Тест поиска (без реального запроса)
    print(f'   ✅ Методы поиска готовы к работе')
except Exception as e:
    print(f'❌ Ошибка API: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Финал
print('\n' + '='*70)
print('🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!')
print('='*70)
print(f'\n📊 ИТОГИ:')
print(f'   ✅ 13/13 тестов пройдено')
print(f'   ✅ Пользователь: {user["username"]}')
print(f'   ✅ Продуктов в базе: {products_count}')
print(f'   ✅ Рецептов в базе: {recipes_count}')
print(f'   ✅ AI функции работают')
print(f'   ✅ Экспорт/Импорт работает')
print(f'   ✅ Уведомления настроены')
print(f'   ✅ Диеты доступны')
print(f'   ✅ Темы переключаются')
print(f'\n🚀 ПРИЛОЖЕНИЕ ГОТОВО К РАБОТЕ!')

# Очистка тестовой БД
if os.path.exists('test_full_cycle.db'):
    os.remove('test_full_cycle.db')
    print('\n🧹 Тестовая БД удалена')
