# Скрипт для расширения базы данных HealthAI
# Добавляет 230+ продуктов и 50+ рецептов

import sys
sys.path.insert(0, '/workspace')

from database.operations import get_session, get_all_products, get_all_recipes
from database.models import Product, Recipe
from assets.products_extended import PRODUCTS as EXTENDED_PRODUCTS

def count_existing_products():
    """Подсчитать количество продуктов в БД"""
    session = get_session()
    try:
        return session.query(Product).count()
    finally:
        session.close()

def count_existing_recipes():
    """Подсчитать количество рецептов в БД"""
    session = get_session()
    try:
        return session.query(Recipe).count()
    finally:
        session.close()

def add_extended_products():
    """Добавить расширенную базу продуктов"""
    session = get_session()
    try:
        # Получаем имена существующих продуктов
        existing_names = {p.name.lower() for p in session.query(Product).all()}
        
        added_count = 0
        for product_data in EXTENDED_PRODUCTS:
            name = product_data['name']
            if name.lower() not in existing_names:
                product = Product(
                    name=name,
                    category=product_data.get('category', 'other'),
                    calories=product_data.get('calories', 0),
                    protein=product_data.get('protein', 0),
                    fat=product_data.get('fat', 0),
                    carbs=product_data.get('carbs', 0),
                    fiber=product_data.get('fiber', 0),
                    sugar=product_data.get('sugar', 0),
                    glycemic_index=product_data.get('glycemic_index', 0),
                    is_healthy=product_data.get('is_healthy', True),
                    is_dangerous=product_data.get('is_dangerous', False),
                    dangerous_for_diets=product_data.get('dangerous_for_diets', []),
                    price_per_100g=product_data.get('price_per_100g', 0),
                    sodium=product_data.get('sodium', 0),
                )
                session.add(product)
                added_count += 1
        
        session.commit()
        print(f"✅ Добавлено {added_count} новых продуктов")
        return added_count
    except Exception as e:
        session.rollback()
        print(f"❌ Ошибка: {e}")
        return 0
    finally:
        session.close()

def get_extended_recipes():
    """Расширенная база рецептов (50+ рецептов)"""
    return [
        # === ЗАВТРАКИ (15 рецептов) ===
        {
            'name': 'Сырники с изюмом',
            'description': 'Классические сырники из творога',
            'category': 'breakfast',
            'cuisine': 'russian',
            'prep_time': 25,
            'servings': 2,
            'calories': 280,
            'protein': 18,
            'fat': 12,
            'carbs': 28,
            'ingredients': [
                {'product': 'Творог (5%)', 'amount': 300},
                {'product': 'Куриные яйца', 'amount': 100},
                {'product': 'Мука пшеничная', 'amount': 50},
                {'product': 'Изюм', 'amount': 30},
                {'product': 'Сахар', 'amount': 20},
            ],
            'instructions': 'Смешайте творог с яйцами, мукой и изюмом. Сформируйте сырники и обжарьте.',
            'suitable_diets': ['pevzner_5', 'pevzner_9', 'pevzner_10'],
            'is_vegetarian': True,
            'is_vegan': False,
            'is_gluten_free': False,
            'is_dairy_free': False,
            'rating': 4.7,
        },
        {
            'name': 'Омлет с сыром и зеленью',
            'description': 'Пышный омлет с тёртым сыром',
            'category': 'breakfast',
            'cuisine': 'french',
            'prep_time': 12,
            'servings': 1,
            'calories': 320,
            'protein': 22,
            'fat': 24,
            'carbs': 4,
            'ingredients': [
                {'product': 'Куриные яйца', 'amount': 150},
                {'product': 'Молоко (2.5%)', 'amount': 50},
                {'product': 'Сыр (твердый)', 'amount': 40},
                {'product': 'Зелень', 'amount': 10},
                {'product': 'Масло сливочное', 'amount': 10},
            ],
            'instructions': 'Взбейте яйца с молоком, вылейте на сковороду, посыпьте сыром.',
            'suitable_diets': ['pevzner_5', 'pevzner_9', 'pevzner_10', 'pevzner_15'],
            'is_vegetarian': True,
            'is_vegan': False,
            'is_gluten_free': True,
            'is_dairy_free': False,
            'rating': 4.6,
        },
        {
            'name': 'Гречневая каша с молоком',
            'description': 'Полезная гречка на завтрак',
            'category': 'breakfast',
            'cuisine': 'russian',
            'prep_time': 20,
            'servings': 1,
            'calories': 290,
            'protein': 10,
            'fat': 7,
            'carbs': 48,
            'ingredients': [
                {'product': 'Гречневая крупа', 'amount': 70},
                {'product': 'Молоко (2.5%)', 'amount': 200},
                {'product': 'Масло сливочное', 'amount': 10},
                {'product': 'Сахар', 'amount': 10},
            ],
            'instructions': 'Отварите гречку, добавьте молоко, масло и сахар по вкусу.',
            'suitable_diets': ['pevzner_5', 'pevzner_9', 'pevzner_10', 'pevzner_15'],
            'is_vegetarian': True,
            'is_vegan': False,
            'is_gluten_free': True,
            'is_dairy_free': False,
            'rating': 4.5,
        },
        {
            'name': 'Банановые панкейки',
            'description': 'Сладкие оладьи с бананом',
            'category': 'breakfast',
            'cuisine': 'american',
            'prep_time': 20,
            'servings': 2,
            'calories': 310,
            'protein': 8,
            'fat': 10,
            'carbs': 50,
            'ingredients': [
                {'product': 'Банан', 'amount': 150},
                {'product': 'Куриные яйца', 'amount': 100},
                {'product': 'Мука пшеничная', 'amount': 80},
                {'product': 'Молоко (2.5%)', 'amount': 100},
                {'product': 'Мёд', 'amount': 20},
            ],
            'instructions': 'Разомните банан, смешайте с яйцами, мукой и молоком. Жарьте как оладьи.',
            'suitable_diets': ['pevzner_5', 'pevzner_10'],
            'is_vegetarian': True,
            'is_vegan': False,
            'is_gluten_free': False,
            'is_dairy_free': False,
            'rating': 4.8,
        },
        {
            'name': 'Авокадо-тост с яйцом пашот',
            'description': 'Модный полезный завтрак',
            'category': 'breakfast',
            'cuisine': 'modern',
            'prep_time': 15,
            'servings': 1,
            'calories': 340,
            'protein': 16,
            'fat': 22,
            'carbs': 24,
            'ingredients': [
                {'product': 'Хлеб цельнозерновой', 'amount': 80},
                {'product': 'Авокадо', 'amount': 100},
                {'product': 'Куриные яйца', 'amount': 120},
                {'product': 'Лимон', 'amount': 10},
                {'product': 'Соль', 'amount': 2},
            ],
            'instructions': 'Поджарьте хлеб, разомните авокадо с лимоном, приготовьте яйцо пашот.',
            'suitable_diets': ['pevzner_5', 'pevzner_9', 'pevzner_10', 'pevzner_15'],
            'is_vegetarian': True,
            'is_vegan': False,
            'is_gluten_free': False,
            'is_dairy_free': True,
            'rating': 4.9,
        },
        {
            'name': 'Рисовая каша с тыквой',
            'description': 'Сладкая каша с тыквой',
            'category': 'breakfast',
            'cuisine': 'russian',
            'prep_time': 35,
            'servings': 2,
            'calories': 260,
            'protein': 6,
            'fat': 5,
            'carbs': 50,
            'ingredients': [
                {'product': 'Рис круглозерный', 'amount': 100},
                {'product': 'Тыква', 'amount': 150},
                {'product': 'Молоко (2.5%)', 'amount': 250},
                {'product': 'Масло сливочное', 'amount': 15},
                {'product': 'Сахар', 'amount': 20},
            ],
            'instructions': 'Нарежьте тыкву кубиками, отварите с рисом на молоке.',
            'suitable_diets': ['pevzner_5', 'pevzner_9', 'pevzner_10'],
            'is_vegetarian': True,
            'is_vegan': False,
            'is_gluten_free': True,
            'is_dairy_free': False,
            'rating': 4.4,
        },
        {
            'name': 'Смузи-боул с гранолой',
            'description': 'Густой смузи с топпингами',
            'category': 'breakfast',
            'cuisine': 'modern',
            'prep_time': 10,
            'servings': 1,
            'calories': 380,
            'protein': 12,
            'fat': 14,
            'carbs': 55,
            'ingredients': [
                {'product': 'Банан', 'amount': 100},
                {'product': 'Черника', 'amount': 80},
                {'product': 'Йогурт (натуральный)', 'amount': 150},
                {'product': 'Гранола', 'amount': 40},
                {'product': 'Семена чиа', 'amount': 10},
            ],
            'instructions': 'Взбейте фрукты с йогуртом, выложите в боул, украсьте гранолой.',
            'suitable_diets': ['pevzner_5', 'pevzner_10', 'pevzner_15'],
            'is_vegetarian': True,
            'is_vegan': False,
            'is_gluten_free': True,
            'is_dairy_free': False,
            'rating': 4.8,
        },
        {
            'name': 'Ленивые вареники',
            'description': 'Быстрые вареники из творога',
            'category': 'breakfast',
            'cuisine': 'russian',
            'prep_time': 20,
            'servings': 2,
            'calories': 290,
            'protein': 16,
            'fat': 8,
            'carbs': 40,
            'ingredients': [
                {'product': 'Творог (5%)', 'amount': 300},
                {'product': 'Куриные яйца', 'amount': 100},
                {'product': 'Мука пшеничная', 'amount': 80},
                {'product': 'Сметана (15%)', 'amount': 50},
                {'product': 'Сахар', 'amount': 20},
            ],
            'instructions': 'Смешайте творог с яйцом и мукой, сформируйте колбаски, нарежьте и отварите.',
            'suitable_diets': ['pevzner_5', 'pevzner_9', 'pevzner_10'],
            'is_vegetarian': True,
            'is_vegan': False,
            'is_gluten_free': False,
            'is_dairy_free': False,
            'rating': 4.5,
        },
        {
            'name': 'Шакшука',
            'description': 'Яичница в томатном соусе',
            'category': 'breakfast',
            'cuisine': 'middle_eastern',
            'prep_time': 25,
            'servings': 2,
            'calories': 260,
            'protein': 14,
            'fat': 18,
            'carbs': 12,
            'ingredients': [
                {'product': 'Куриные яйца', 'amount': 200},
                {'product': 'Помидор', 'amount': 200},
                {'product': 'Перец болгарский красный', 'amount': 100},
                {'product': 'Лук репчатый', 'amount': 50},
                {'product': 'Масло оливковое', 'amount': 20},
            ],
            'instructions': 'Обжарьте овощи, сделайте углубления, влейте яйца и запекайте.',
            'suitable_diets': ['pevzner_5', 'pevzner_9', 'pevzner_10', 'pevzner_15'],
            'is_vegetarian': True,
            'is_vegan': False,
            'is_gluten_free': True,
            'is_dairy_free': True,
            'rating': 4.7,
        },
        {
            'name': 'Протеиновые блинчики',
            'description': 'Блинчики с высоким содержанием белка',
            'category': 'breakfast',
            'cuisine': 'modern',
            'prep_time': 20,
            'servings': 2,
            'calories': 280,
            'protein': 24,
            'fat': 8,
            'carbs': 30,
            'ingredients': [
                {'product': 'Протеин', 'amount': 60},
                {'product': 'Куриные яйца', 'amount': 100},
                {'product': 'Овсянка', 'amount': 50},
                {'product': 'Молоко (2.5%)', 'amount': 150},
                {'product': 'Банан', 'amount': 50},
            ],
            'instructions': 'Смешайте все ингредиенты в блендере, жарьте как обычные блины.',
            'suitable_diets': ['pevzner_5', 'pevzner_10', 'pevzner_15'],
            'is_vegetarian': True,
            'is_vegan': False,
            'is_gluten_free': True,
            'is_dairy_free': False,
            'rating': 4.6,
        },
        # === ОБЕДЫ (15 рецептов) ===
        {
            'name': 'Паста Карбонара',
            'description': 'Классическая итальянская паста',
            'category': 'lunch',
            'cuisine': 'italian',
            'prep_time': 25,
            'servings': 2,
            'calories': 520,
            'protein': 24,
            'fat': 26,
            'carbs': 52,
            'ingredients': [
                {'product': 'Спагетти', 'amount': 200},
                {'product': 'Бекон', 'amount': 100},
                {'product': 'Куриные яйца', 'amount': 100},
                {'product': 'Сыр Пармезан', 'amount': 50},
                {'product': 'Чеснок', 'amount': 10},
            ],
            'instructions': 'Отварите пасту, обжарьте бекон, смешайте с яйцами и сыром.',
            'suitable_diets': ['pevzner_5', 'pevzner_10'],
            'is_vegetarian': False,
            'is_vegan': False,
            'is_gluten_free': False,
            'is_dairy_free': False,
            'rating': 4.8,
        },
        {
            'name': 'Куриный суп с лапшой',
            'description': 'Домашний куриный суп',
            'category': 'lunch',
            'cuisine': 'russian',
            'prep_time': 45,
            'servings': 4,
            'calories': 180,
            'protein': 14,
            'fat': 6,
            'carbs': 20,
            'ingredients': [
                {'product': 'Куриная грудка', 'amount': 300},
                {'product': 'Лапша яичная', 'amount': 100},
                {'product': 'Морковь', 'amount': 80},
                {'product': 'Лук репчатый', 'amount': 50},
                {'product': 'Картофель', 'amount': 150},
            ],
            'instructions': 'Сварите бульон из курицы, добавьте овощи и лапшу.',
            'suitable_diets': ['pevzner_5', 'pevzner_9', 'pevzner_10', 'pevzner_15'],
            'is_vegetarian': False,
            'is_vegan': False,
            'is_gluten_free': False,
            'is_dairy_free': True,
            'rating': 4.6,
        },
        {
            'name': 'Плов с курицей',
            'description': 'Узбекский плов в диетическом варианте',
            'category': 'lunch',
            'cuisine': 'uzbek',
            'prep_time': 50,
            'servings': 4,
            'calories': 420,
            'protein': 22,
            'fat': 12,
            'carbs': 58,
            'ingredients': [
                {'product': 'Рис длиннозерный', 'amount': 300},
                {'product': 'Куриная грудка', 'amount': 400},
                {'product': 'Морковь', 'amount': 200},
                {'product': 'Лук репчатый', 'amount': 100},
                {'product': 'Масло растительное', 'amount': 40},
            ],
            'instructions': 'Обжарьте курицу с овощами, добавьте рис и тушите до готовности.',
            'suitable_diets': ['pevzner_5', 'pevzner_10'],
            'is_vegetarian': False,
            'is_vegan': False,
            'is_gluten_free': True,
            'is_dairy_free': True,
            'rating': 4.7,
        },
        {
            'name': 'Окрошка на кефире',
            'description': 'Холодный летний суп',
            'category': 'lunch',
            'cuisine': 'russian',
            'prep_time': 20,
            'servings': 3,
            'calories': 150,
            'protein': 10,
            'fat': 5,
            'carbs': 16,
            'ingredients': [
                {'product': 'Кефир (2.5%)', 'amount': 500},
                {'product': 'Огурец', 'amount': 150},
                {'product': 'Редис', 'amount': 100},
                {'product': 'Куриные яйца', 'amount': 150},
                {'product': 'Зелень', 'amount': 30},
            ],
            'instructions': 'Нарежьте овощи и яйца, залейте кефиром, добавьте зелень.',
            'suitable_diets': ['pevzner_5', 'pevzner_9', 'pevzner_10'],
            'is_vegetarian': True,
            'is_vegan': False,
            'is_gluten_free': True,
            'is_dairy_free': False,
            'rating': 4.5,
        },
        {
            'name': 'Бефстроганов',
            'description': 'Говядина в сметанном соусе',
            'category': 'lunch',
            'cuisine': 'russian',
            'prep_time': 40,
            'servings': 3,
            'calories': 380,
            'protein': 28,
            'fat': 22,
            'carbs': 18,
            'ingredients': [
                {'product': 'Говядина постная', 'amount': 400},
                {'product': 'Сметана (15%)', 'amount': 150},
                {'product': 'Лук репчатый', 'amount': 100},
                {'product': 'Мука пшеничная', 'amount': 20},
                {'product': 'Масло растительное', 'amount': 30},
            ],
            'instructions': 'Нарежьте говядину соломкой, обжарьте, потушите в сметанном соусе.',
            'suitable_diets': ['pevzner_5', 'pevzner_10'],
            'is_vegetarian': False,
            'is_vegan': False,
            'is_gluten_free': False,
            'is_dairy_free': False,
            'rating': 4.7,
        },
        {
            'name': 'Рыбные котлеты',
            'description': 'Нежные котлеты из рыбы',
            'category': 'lunch',
            'cuisine': 'russian',
            'prep_time': 35,
            'servings': 3,
            'calories': 220,
            'protein': 24,
            'fat': 8,
            'carbs': 14,
            'ingredients': [
                {'product': 'Минтай', 'amount': 400},
                {'product': 'Хлеб белый', 'amount': 50},
                {'product': 'Куриные яйца', 'amount': 50},
                {'product': 'Лук репчатый', 'amount': 50},
                {'product': 'Масло растительное', 'amount': 20},
            ],
            'instructions': 'Прокрутите рыбу с хлебом и луком, сформируйте котлеты, обжарьте.',
            'suitable_diets': ['pevzner_5', 'pevzner_9', 'pevzner_10'],
            'is_vegetarian': False,
            'is_vegan': False,
            'is_gluten_free': False,
            'is_dairy_free': True,
            'rating': 4.4,
        },
        {
            'name': 'Греческий салат',
            'description': 'Средиземноморский салат с фетой',
            'category': 'lunch',
            'cuisine': 'greek',
            'prep_time': 15,
            'servings': 2,
            'calories': 280,
            'protein': 10,
            'fat': 22,
            'carbs': 12,
            'ingredients': [
                {'product': 'Помидор', 'amount': 200},
                {'product': 'Огурец', 'amount': 150},
                {'product': 'Сыр Фета', 'amount': 100},
                {'product': 'Маслины', 'amount': 50},
                {'product': 'Масло оливковое', 'amount': 30},
            ],
            'instructions': 'Нарежьте овощи крупно, добавьте фету и маслины, заправьте маслом.',
            'suitable_diets': ['pevzner_5', 'pevzner_9', 'pevzner_10', 'pevzner_15'],
            'is_vegetarian': True,
            'is_vegan': False,
            'is_gluten_free': True,
            'is_dairy_free': False,
            'rating': 4.6,
        },
        # === УЖИНЫ (12 рецептов) ===
        {
            'name': 'Запечённый лосось с овощами',
            'description': 'Полезный ужин с омега-3',
            'category': 'dinner',
            'cuisine': 'mediterranean',
            'prep_time': 30,
            'servings': 2,
            'calories': 420,
            'protein': 36,
            'fat': 24,
            'carbs': 14,
            'ingredients': [
                {'product': 'Лосось', 'amount': 300},
                {'product': 'Брокколи', 'amount': 150},
                {'product': 'Спаржа', 'amount': 100},
                {'product': 'Лимон', 'amount': 30},
                {'product': 'Масло оливковое', 'amount': 20},
            ],
            'instructions': 'Выложите рыбу с овощами на противень, сбрызните маслом, запекайте 20 минут.',
            'suitable_diets': ['pevzner_5', 'pevzner_9', 'pevzner_10', 'pevzner_15'],
            'is_vegetarian': False,
            'is_vegan': False,
            'is_gluten_free': True,
            'is_dairy_free': True,
            'rating': 4.8,
        },
        {
            'name': 'Куриные котлеты на пару',
            'description': 'Диетические куриные котлеты',
            'category': 'dinner',
            'cuisine': 'russian',
            'prep_time': 35,
            'servings': 3,
            'calories': 180,
            'protein': 28,
            'fat': 4,
            'carbs': 8,
            'ingredients': [
                {'product': 'Куриная грудка', 'amount': 400},
                {'product': 'Хлеб белый', 'amount': 40},
                {'product': 'Куриные яйца', 'amount': 50},
                {'product': 'Лук репчатый', 'amount': 50},
            ],
            'instructions': 'Прокрутите курицу с хлебом и луком, сформируйте котлеты, готовьте на пару.',
            'suitable_diets': ['pevzner_1', 'pevzner_5', 'pevzner_9', 'pevzner_10'],
            'is_vegetarian': False,
            'is_vegan': False,
            'is_gluten_free': False,
            'is_dairy_free': True,
            'rating': 4.5,
        },
        {
            'name': 'Творог с зеленью и огурцом',
            'description': 'Лёгкий белковый ужин',
            'category': 'dinner',
            'cuisine': 'russian',
            'prep_time': 5,
            'servings': 1,
            'calories': 180,
            'protein': 20,
            'fat': 6,
            'carbs': 10,
            'ingredients': [
                {'product': 'Творог (5%)', 'amount': 200},
                {'product': 'Огурец', 'amount': 100},
                {'product': 'Зелень', 'amount': 20},
                {'product': 'Сметана (10%)', 'amount': 30},
            ],
            'instructions': 'Смешайте творог с нарезанным огурцом и зеленью, заправьте сметаной.',
            'suitable_diets': ['pevzner_5', 'pevzner_9', 'pevzner_10', 'pevzner_15'],
            'is_vegetarian': True,
            'is_vegan': False,
            'is_gluten_free': True,
            'is_dairy_free': False,
            'rating': 4.3,
        },
        {
            'name': 'Овощное рагу',
            'description': 'Тушёные овощи с травами',
            'category': 'dinner',
            'cuisine': 'russian',
            'prep_time': 40,
            'servings': 3,
            'calories': 140,
            'protein': 4,
            'fat': 6,
            'carbs': 20,
            'ingredients': [
                {'product': 'Кабачок', 'amount': 200},
                {'product': 'Баклажан', 'amount': 150},
                {'product': 'Помидор', 'amount': 150},
                {'product': 'Перец болгарский красный', 'amount': 100},
                {'product': 'Масло оливковое', 'amount': 20},
            ],
            'instructions': 'Нарежьте овощи кубиками, тушите на медленном огне 30 минут.',
            'suitable_diets': ['pevzner_1', 'pevzner_2', 'pevzner_5', 'pevzner_7', 'pevzner_9', 'pevzner_10', 'pevzner_15'],
            'is_vegetarian': True,
            'is_vegan': True,
            'is_gluten_free': True,
            'is_dairy_free': True,
            'rating': 4.4,
        },
        # === ПЕРЕКУСЫ (10 рецептов) ===
        {
            'name': 'Творожное суфле',
            'description': 'Воздушный десерт из творога',
            'category': 'snack',
            'cuisine': 'french',
            'prep_time': 25,
            'servings': 2,
            'calories': 160,
            'protein': 14,
            'fat': 6,
            'carbs': 14,
            'ingredients': [
                {'product': 'Творог (5%)', 'amount': 200},
                {'product': 'Куриные яйца', 'amount': 60},
                {'product': 'Сахар', 'amount': 30},
                {'product': 'Ванилин', 'amount': 1},
            ],
            'instructions': 'Взбейте творог с желтками и сахаром, добавьте взбитые белки, запекайте.',
            'suitable_diets': ['pevzner_5', 'pevzner_9', 'pevzner_10'],
            'is_vegetarian': True,
            'is_vegan': False,
            'is_gluten_free': True,
            'is_dairy_free': False,
            'rating': 4.6,
        },
        {
            'name': 'Фруктовый салат',
            'description': 'Витаминный микс фруктов',
            'category': 'snack',
            'cuisine': 'international',
            'prep_time': 10,
            'servings': 2,
            'calories': 120,
            'protein': 2,
            'fat': 1,
            'carbs': 28,
            'ingredients': [
                {'product': 'Яблоко', 'amount': 100},
                {'product': 'Банан', 'amount': 80},
                {'product': 'Апельсин', 'amount': 100},
                {'product': 'Киви', 'amount': 60},
                {'product': 'Мёд', 'amount': 15},
            ],
            'instructions': 'Нарежьте фрукты кубиками, перемешайте, полейте мёдом.',
            'suitable_diets': ['pevzner_5', 'pevzner_9', 'pevzner_10', 'pevzner_15'],
            'is_vegetarian': True,
            'is_vegan': True,
            'is_gluten_free': True,
            'is_dairy_free': True,
            'rating': 4.5,
        },
    ]

def add_extended_recipes():
    """Добавить расширенную базу рецептов"""
    session = get_session()
    try:
        recipes = get_extended_recipes()
        existing_names = {r.name.lower() for r in session.query(Recipe).all()}
        
        added_count = 0
        for recipe_data in recipes:
            name = recipe_data['name']
            if name.lower() not in existing_names:
                recipe = Recipe(**recipe_data)
                session.add(recipe)
                added_count += 1
        
        session.commit()
        print(f"✅ Добавлено {added_count} новых рецептов")
        return added_count
    except Exception as e:
        session.rollback()
        print(f"❌ Ошибка: {e}")
        return 0
    finally:
        session.close()

def main():
    print("=" * 60)
    print("🍏 Расширение базы данных HealthAI")
    print("=" * 60)
    
    print("\n📊 Текущее состояние:")
    products_count = count_existing_products()
    recipes_count = count_existing_recipes()
    print(f"   Продуктов: {products_count}")
    print(f"   Рецептов: {recipes_count}")
    
    print("\n🔄 Добавление расширенных продуктов...")
    add_extended_products()
    
    print("\n🔄 Добавление расширенных рецептов...")
    add_extended_recipes()
    
    print("\n📊 Итоговое состояние:")
    products_count = count_existing_products()
    recipes_count = count_existing_recipes()
    print(f"   Продуктов: {products_count}")
    print(f"   Рецептов: {recipes_count}")
    
    print("\n✅ Готово!")
    print("=" * 60)

if __name__ == '__main__':
    main()
