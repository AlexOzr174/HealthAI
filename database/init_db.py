# Инициализация базы данных и начальные данные
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from .models import Base, Product, Recipe, Achievement
from config.settings import DB_PATH
import json
import os

def get_engine():
    """Создание движка базы данных"""
    engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
    return engine


def _ensure_users_special_diets_column(engine):
    """Миграция SQLite: колонка special_diets_json для страницы «Специальные диеты»."""
    try:
        insp = inspect(engine)
        cols = [c["name"] for c in insp.get_columns("users")]
        if "special_diets_json" not in cols:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN special_diets_json TEXT"))
    except Exception:
        pass


def init_database():
    """Инициализация базы данных с созданием таблиц"""
    engine = get_engine()
    Base.metadata.create_all(engine)
    _ensure_users_special_diets_column(engine)
    return engine

def get_session():
    """Получение сессии базы данных"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def populate_initial_data():
    """Заполнение базы данных начальными данными"""
    session = get_session()

    try:
        # Проверяем, есть ли уже данные
        if session.query(Product).count() > 0:
            print("База данных уже содержит данные")
            return

        # Добавление продуктов
        products = get_default_products()
        for product_data in products:
            product = Product(**product_data)
            session.add(product)

        # Добавление рецептов
        recipes = get_default_recipes()
        for recipe_data in recipes:
            recipe = Recipe(**recipe_data)
            session.add(recipe)

        # Добавление достижений
        achievements = get_default_achievements()
        for achievement_data in achievements:
            achievement = Achievement(**achievement_data)
            session.add(achievement)

        session.commit()
        print("База данных успешно заполнена начальными данными")

    except Exception as e:
        session.rollback()
        print(f"Ошибка при заполнении базы данных: {e}")
    finally:
        session.close()

def get_default_products():
    """База продуктов по категориям (100г)"""
    return [
        # Овощи
        {'name': 'Морковь', 'category': 'vegetables', 'calories': 32, 'protein': 1.3, 'fat': 0.1, 'carbs': 8.0, 'fiber': 2.8, 'sugar': 4.9, 'price_per_100g': 0.50, 'is_healthy': True, 'glycemic_index': 35},
        {'name': 'Помидор', 'category': 'vegetables', 'calories': 18, 'protein': 0.9, 'fat': 0.2, 'carbs': 3.9, 'fiber': 1.2, 'sugar': 2.6, 'price_per_100g': 0.80, 'is_healthy': True, 'glycemic_index': 15},
        {'name': 'Огурец', 'category': 'vegetables', 'calories': 15, 'protein': 0.7, 'fat': 0.1, 'carbs': 3.6, 'fiber': 0.5, 'sugar': 1.7, 'price_per_100g': 0.60, 'is_healthy': True, 'glycemic_index': 15},
        {'name': 'Капуста', 'category': 'vegetables', 'calories': 25, 'protein': 1.3, 'fat': 0.1, 'carbs': 5.8, 'fiber': 2.5, 'sugar': 3.2, 'price_per_100g': 0.40, 'is_healthy': True, 'glycemic_index': 10},
        {'name': 'Лук репчатый', 'category': 'vegetables', 'calories': 41, 'protein': 1.1, 'fat': 0.1, 'carbs': 9.5, 'fiber': 1.7, 'sugar': 4.2, 'price_per_100g': 0.35, 'is_healthy': True, 'glycemic_index': 10},
        {'name': 'Брокколи', 'category': 'vegetables', 'calories': 34, 'protein': 2.8, 'fat': 0.4, 'carbs': 7.0, 'fiber': 2.6, 'sugar': 1.7, 'price_per_100g': 1.20, 'is_healthy': True, 'glycemic_index': 10},
        {'name': 'Шпинат', 'category': 'vegetables', 'calories': 23, 'protein': 2.9, 'fat': 0.4, 'carbs': 3.6, 'fiber': 2.2, 'sugar': 0.4, 'price_per_100g': 1.50, 'is_healthy': True, 'glycemic_index': 15},
        {'name': 'Болгарский перец', 'category': 'vegetables', 'calories': 31, 'protein': 1.0, 'fat': 0.3, 'carbs': 6.0, 'fiber': 2.1, 'sugar': 4.2, 'price_per_100g': 1.00, 'is_healthy': True, 'glycemic_index': 15},
        {'name': 'Тыква', 'category': 'vegetables', 'calories': 26, 'protein': 1.0, 'fat': 0.1, 'carbs': 6.5, 'fiber': 0.5, 'sugar': 3.0, 'price_per_100g': 0.45, 'is_healthy': True, 'glycemic_index': 50},
        {'name': 'Кабачок', 'category': 'vegetables', 'calories': 17, 'protein': 1.2, 'fat': 0.3, 'carbs': 3.1, 'fiber': 1.0, 'sugar': 2.5, 'price_per_100g': 0.55, 'is_healthy': True, 'glycemic_index': 15},

        # Фрукты
        {'name': 'Яблоко', 'category': 'fruits', 'calories': 52, 'protein': 0.3, 'fat': 0.2, 'carbs': 14.0, 'fiber': 2.4, 'sugar': 10.0, 'price_per_100g': 0.70, 'is_healthy': True, 'glycemic_index': 36},
        {'name': 'Банан', 'category': 'fruits', 'calories': 89, 'protein': 1.1, 'fat': 0.3, 'carbs': 23.0, 'fiber': 2.6, 'sugar': 12.0, 'price_per_100g': 0.65, 'is_healthy': True, 'glycemic_index': 51},
        {'name': 'Апельсин', 'category': 'fruits', 'calories': 47, 'protein': 0.9, 'fat': 0.1, 'carbs': 12.0, 'fiber': 2.4, 'sugar': 9.0, 'price_per_100g': 0.80, 'is_healthy': True, 'glycemic_index': 35},
        {'name': 'Клубника', 'category': 'fruits', 'calories': 32, 'protein': 0.7, 'fat': 0.3, 'carbs': 8.0, 'fiber': 2.0, 'sugar': 4.9, 'price_per_100g': 2.00, 'is_healthy': True, 'glycemic_index': 40},
        {'name': 'Виноград', 'category': 'fruits', 'calories': 69, 'protein': 0.7, 'fat': 0.2, 'carbs': 18.0, 'fiber': 0.9, 'sugar': 16.0, 'price_per_100g': 1.50, 'is_healthy': False, 'glycemic_index': 50},
        {'name': 'Грейпфрут', 'category': 'fruits', 'calories': 42, 'protein': 0.8, 'fat': 0.1, 'carbs': 11.0, 'fiber': 1.6, 'sugar': 7.0, 'price_per_100g': 0.90, 'is_healthy': True, 'glycemic_index': 25},
        {'name': 'Мандарин', 'category': 'fruits', 'calories': 53, 'protein': 0.8, 'fat': 0.3, 'carbs': 13.0, 'fiber': 1.8, 'sugar': 10.0, 'price_per_100g': 0.75, 'is_healthy': True, 'glycemic_index': 30},
        {'name': 'Груша', 'category': 'fruits', 'calories': 57, 'protein': 0.4, 'fat': 0.1, 'carbs': 15.0, 'fiber': 3.1, 'sugar': 10.0, 'price_per_100g': 0.85, 'is_healthy': True, 'glycemic_index': 38},
        {'name': 'Персик', 'category': 'fruits', 'calories': 39, 'protein': 0.9, 'fat': 0.3, 'carbs': 10.0, 'fiber': 1.5, 'sugar': 8.0, 'price_per_100g': 1.10, 'is_healthy': True, 'glycemic_index': 42},
        {'name': 'Арбуз', 'category': 'fruits', 'calories': 30, 'protein': 0.6, 'fat': 0.2, 'carbs': 8.0, 'fiber': 0.4, 'sugar': 6.0, 'price_per_100g': 0.50, 'is_healthy': True, 'glycemic_index': 72},

        # Мясо и птица
        {'name': 'Куриная грудка', 'category': 'meat', 'calories': 165, 'protein': 31.0, 'fat': 3.6, 'carbs': 0.0, 'fiber': 0.0, 'sugar': 0.0, 'price_per_100g': 2.50, 'is_healthy': True, 'glycemic_index': 0},
        {'name': 'Говядина (нежирная)', 'category': 'meat', 'calories': 250, 'protein': 26.0, 'fat': 15.0, 'carbs': 0.0, 'fiber': 0.0, 'sugar': 0.0, 'price_per_100g': 3.50, 'is_healthy': True, 'glycemic_index': 0},
        {'name': 'Свинина (нежирная)', 'category': 'meat', 'calories': 242, 'protein': 27.0, 'fat': 14.0, 'carbs': 0.0, 'fiber': 0.0, 'sugar': 0.0, 'price_per_100g': 2.80, 'is_healthy': True, 'glycemic_index': 0},
        {'name': 'Индейка', 'category': 'meat', 'calories': 135, 'protein': 30.0, 'fat': 1.0, 'carbs': 0.0, 'fiber': 0.0, 'sugar': 0.0, 'price_per_100g': 3.00, 'is_healthy': True, 'glycemic_index': 0},
        {'name': 'Куриные яйца', 'category': 'meat', 'calories': 155, 'protein': 13.0, 'fat': 11.0, 'carbs': 1.1, 'fiber': 0.0, 'sugar': 1.1, 'price_per_100g': 1.20, 'is_healthy': True, 'glycemic_index': 0},
        {'name': 'Бекон', 'category': 'meat', 'calories': 541, 'protein': 37.0, 'fat': 42.0, 'carbs': 1.4, 'fiber': 0.0, 'sugar': 0.0, 'price_per_100g': 4.00, 'is_healthy': False, 'glycemic_index': 0},
        {'name': 'Колбаса вареная', 'category': 'meat', 'calories': 250, 'protein': 12.0, 'fat': 22.0, 'carbs': 2.0, 'fiber': 0.0, 'sugar': 1.5, 'price_per_100g': 2.00, 'is_healthy': False, 'glycemic_index': 0},

        # Молочные продукты
        {'name': 'Молоко (2.5%)', 'category': 'dairy', 'calories': 52, 'protein': 3.3, 'fat': 2.5, 'carbs': 4.8, 'fiber': 0.0, 'sugar': 4.8, 'price_per_100g': 0.60, 'is_healthy': True, 'glycemic_index': 30},
        {'name': 'Творог (5%)', 'category': 'dairy', 'calories': 121, 'protein': 17.0, 'fat': 5.0, 'carbs': 3.0, 'fiber': 0.0, 'sugar': 3.0, 'price_per_100g': 1.50, 'is_healthy': True, 'glycemic_index': 35},
        {'name': 'Сыр (твердый)', 'category': 'dairy', 'calories': 370, 'protein': 25.0, 'fat': 30.0, 'carbs': 1.3, 'fiber': 0.0, 'sugar': 0.5, 'price_per_100g': 4.50, 'is_healthy': True, 'glycemic_index': 0},
        {'name': 'Йогурт (натуральный)', 'category': 'dairy', 'calories': 59, 'protein': 10.0, 'fat': 0.7, 'carbs': 3.6, 'fiber': 0.0, 'sugar': 3.2, 'price_per_100g': 1.00, 'is_healthy': True, 'glycemic_index': 35},
        {'name': 'Сметана (15%)', 'category': 'dairy', 'calories': 158, 'protein': 2.4, 'fat': 15.0, 'carbs': 3.0, 'fiber': 0.0, 'sugar': 2.5, 'price_per_100g': 1.20, 'is_healthy': True, 'glycemic_index': 35},
        {'name': 'Масло сливочное', 'category': 'dairy', 'calories': 717, 'protein': 0.9, 'fat': 81.0, 'carbs': 0.1, 'fiber': 0.0, 'sugar': 0.1, 'price_per_100g': 2.00, 'is_healthy': False, 'glycemic_index': 0},

        # Зерновые и крупы
        {'name': 'Гречневая крупа', 'category': 'grains', 'calories': 343, 'protein': 13.0, 'fat': 3.5, 'carbs': 72.0, 'fiber': 10.0, 'sugar': 0.0, 'price_per_100g': 0.80, 'is_healthy': True, 'glycemic_index': 40},
        {'name': 'Рис (белый)', 'category': 'grains', 'calories': 365, 'protein': 7.0, 'fat': 0.7, 'carbs': 80.0, 'fiber': 1.3, 'sugar': 0.1, 'price_per_100g': 0.50, 'is_healthy': True, 'glycemic_index': 73},
        {'name': 'Овсянка', 'category': 'grains', 'calories': 367, 'protein': 13.0, 'fat': 6.5, 'carbs': 68.0, 'fiber': 10.0, 'sugar': 1.0, 'price_per_100g': 0.70, 'is_healthy': True, 'glycemic_index': 55},
        {'name': 'Макароны', 'category': 'grains', 'calories': 371, 'protein': 13.0, 'fat': 1.5, 'carbs': 75.0, 'fiber': 3.0, 'sugar': 2.5, 'price_per_100g': 0.45, 'is_healthy': True, 'glycemic_index': 50},
        {'name': 'Хлеб (ржаной)', 'category': 'grains', 'calories': 259, 'protein': 8.5, 'fat': 3.0, 'carbs': 48.0, 'fiber': 6.0, 'sugar': 2.5, 'price_per_100g': 0.50, 'is_healthy': True, 'glycemic_index': 65},
        {'name': 'Хлеб (пшеничный)', 'category': 'grains', 'calories': 265, 'protein': 9.0, 'fat': 3.0, 'carbs': 49.0, 'fiber': 2.5, 'sugar': 3.0, 'price_per_100g': 0.45, 'is_healthy': True, 'glycemic_index': 75},
        {'name': 'Кукурузная крупа', 'category': 'grains', 'calories': 337, 'protein': 8.0, 'fat': 2.5, 'carbs': 74.0, 'fiber': 7.0, 'sugar': 1.5, 'price_per_100g': 0.55, 'is_healthy': True, 'glycemic_index': 70},

        # Бобовые
        {'name': 'Фасоль (красная)', 'category': 'legumes', 'calories': 347, 'protein': 21.0, 'fat': 1.5, 'carbs': 63.0, 'fiber': 16.0, 'sugar': 2.0, 'price_per_100g': 1.00, 'is_healthy': True, 'glycemic_index': 35},
        {'name': 'Чечевица', 'category': 'legumes', 'calories': 358, 'protein': 24.0, 'fat': 1.5, 'carbs': 60.0, 'fiber': 15.0, 'sugar': 4.0, 'price_per_100g': 1.20, 'is_healthy': True, 'glycemic_index': 32},
        {'name': 'Горох', 'category': 'legumes', 'calories': 324, 'protein': 21.0, 'fat': 2.0, 'carbs': 54.0, 'fiber': 16.0, 'sugar': 5.0, 'price_per_100g': 0.80, 'is_healthy': True, 'glycemic_index': 35},

        # Орехи и семена
        {'name': 'Грецкие орехи', 'category': 'nuts', 'calories': 654, 'protein': 15.0, 'fat': 65.0, 'carbs': 14.0, 'fiber': 7.0, 'sugar': 2.5, 'price_per_100g': 4.00, 'is_healthy': True, 'glycemic_index': 15},
        {'name': 'Миндаль', 'category': 'nuts', 'calories': 579, 'protein': 21.0, 'fat': 50.0, 'carbs': 22.0, 'fiber': 12.0, 'sugar': 4.0, 'price_per_100g': 5.00, 'is_healthy': True, 'glycemic_index': 0},
        {'name': 'Арахис', 'category': 'nuts', 'calories': 567, 'protein': 26.0, 'fat': 49.0, 'carbs': 16.0, 'fiber': 8.5, 'sugar': 4.0, 'price_per_100g': 2.50, 'is_healthy': True, 'glycemic_index': 13},
        {'name': 'Семена подсолнечника', 'category': 'nuts', 'calories': 584, 'protein': 21.0, 'fat': 51.0, 'carbs': 20.0, 'fiber': 8.5, 'sugar': 2.5, 'price_per_100g': 1.50, 'is_healthy': True, 'glycemic_index': 35},

        # Напитки
        {'name': 'Чай (без сахара)', 'category': 'drinks', 'calories': 1, 'protein': 0.0, 'fat': 0.0, 'carbs': 0.3, 'fiber': 0.0, 'sugar': 0.0, 'price_per_100g': 0.10, 'is_healthy': True, 'glycemic_index': 0},
        {'name': 'Кофе (без сахара)', 'category': 'drinks', 'calories': 2, 'protein': 0.3, 'fat': 0.0, 'carbs': 0.0, 'fiber': 0.0, 'sugar': 0.0, 'price_per_100g': 0.15, 'is_healthy': True, 'glycemic_index': 0},
        {'name': 'Сок яблочный', 'category': 'drinks', 'calories': 46, 'protein': 0.1, 'fat': 0.1, 'carbs': 11.0, 'fiber': 0.2, 'sugar': 10.0, 'price_per_100g': 0.80, 'is_healthy': False, 'glycemic_index': 42},
        {'name': 'Газировка', 'category': 'drinks', 'calories': 42, 'protein': 0.0, 'fat': 0.0, 'carbs': 11.0, 'fiber': 0.0, 'sugar': 10.0, 'price_per_100g': 0.50, 'is_healthy': False, 'glycemic_index': 60},
        {'name': 'Вода', 'category': 'drinks', 'calories': 0, 'protein': 0.0, 'fat': 0.0, 'carbs': 0.0, 'fiber': 0.0, 'sugar': 0.0, 'price_per_100g': 0.01, 'is_healthy': True, 'glycemic_index': 0},

        # Добавки и приправы
        {'name': 'Мёд', 'category': 'sweets', 'calories': 304, 'protein': 0.3, 'fat': 0.0, 'carbs': 82.0, 'fiber': 0.2, 'sugar': 82.0, 'price_per_100g': 5.00, 'is_healthy': False, 'glycemic_index': 55},
        {'name': 'Сахар', 'category': 'sweets', 'calories': 387, 'protein': 0.0, 'fat': 0.0, 'carbs': 100.0, 'fiber': 0.0, 'sugar': 100.0, 'price_per_100g': 0.50, 'is_healthy': False, 'glycemic_index': 65},
        {'name': 'Шоколад (молочный)', 'category': 'sweets', 'calories': 535, 'protein': 8.0, 'fat': 30.0, 'carbs': 59.0, 'fiber': 2.0, 'sugar': 52.0, 'price_per_100g': 3.00, 'is_healthy': False, 'glycemic_index': 49},
        {'name': 'Соль', 'category': 'other', 'calories': 0, 'protein': 0.0, 'fat': 0.0, 'carbs': 0.0, 'fiber': 0.0, 'sugar': 0.0, 'price_per_100g': 0.10, 'is_healthy': False, 'glycemic_index': 0, 'is_dangerous': True, 'dangerous_for_diets': ['pevzner_1', 'pevzner_5', 'pevzner_7']},
        {'name': 'Растительное масло', 'category': 'other', 'calories': 884, 'protein': 0.0, 'fat': 100.0, 'carbs': 0.0, 'fiber': 0.0, 'sugar': 0.0, 'price_per_100g': 1.00, 'is_healthy': True, 'glycemic_index': 0},
    ]

def get_default_recipes():
    """База рецептов с расчётом на 1 порцию"""
    return [
        {
            'name': 'Овсяная каша с ягодами',
            'description': 'Полезная и сытная каша для здорового завтрака',
            'category': 'breakfast',
            'prep_time': 15,
            'servings': 1,
            'calories': 320,
            'protein': 12,
            'fat': 8,
            'carbs': 52,
            'ingredients': [
                {'product': 'Овсянка', 'amount': 50},
                {'product': 'Молоко (2.5%)', 'amount': 150},
                {'product': 'Клубника', 'amount': 50},
                {'product': 'Мёд', 'amount': 10},
            ],
            'instructions': 'Сварите овсянку на молоке, добавьте ягоды и мёд',
            'suitable_diets': ['pevzner_5', 'pevzner_9', 'pevzner_10', 'pevzner_15'],
            'is_vegetarian': True,
            'is_vegan': False,
            'is_gluten_free': False,
            'rating': 4.8,
        },
        {
            'name': 'Яичница с овощами',
            'description': 'Белковый завтрак с полезными овощами',
            'category': 'breakfast',
            'prep_time': 10,
            'servings': 1,
            'calories': 280,
            'protein': 18,
            'fat': 20,
            'carbs': 8,
            'ingredients': [
                {'product': 'Куриные яйца', 'amount': 150},
                {'product': 'Помидор', 'amount': 50},
                {'product': 'Болгарский перец', 'amount': 30},
                {'product': 'Растительное масло', 'amount': 10},
            ],
            'instructions': 'Обжарьте яйца с овощами на растительном масле',
            'suitable_diets': ['pevzner_5', 'pevzner_9', 'pevzner_10', 'pevzner_15'],
            'is_vegetarian': True,
            'is_vegan': False,
            'is_gluten_free': True,
            'rating': 4.6,
        },
        {
            'name': 'Творожная запеканка',
            'description': 'Нежная запеканка из творога с изюмом',
            'category': 'breakfast',
            'prep_time': 40,
            'servings': 2,
            'calories': 350,
            'protein': 28,
            'fat': 10,
            'carbs': 38,
            'ingredients': [
                {'product': 'Творог (5%)', 'amount': 300},
                {'product': 'Куриные яйца', 'amount': 100},
                {'product': 'Манная крупа', 'amount': 30},
                {'product': 'Сахар', 'amount': 20},
            ],
            'instructions': 'Смешайте творог с яйцами и манкой, запекайте 30 минут',
            'suitable_diets': ['pevzner_5', 'pevzner_9', 'pevzner_10', 'pevzner_15'],
            'is_vegetarian': True,
            'is_vegan': False,
            'is_gluten_free': False,
            'rating': 4.5,
        },
        {
            'name': 'Куриная грудка с гречкой',
            'description': 'Классическое блюдо для правильного питания',
            'category': 'lunch',
            'prep_time': 35,
            'servings': 1,
            'calories': 450,
            'protein': 42,
            'fat': 8,
            'carbs': 52,
            'ingredients': [
                {'product': 'Куриная грудка', 'amount': 150},
                {'product': 'Гречневая крупа', 'amount': 80},
                {'product': 'Огурец', 'amount': 50},
                {'product': 'Растительное масло', 'amount': 10},
            ],
            'instructions': 'Отварите гречку, пожарьте курицу, подайте с салатом',
            'suitable_diets': ['pevzner_5', 'pevzner_9', 'pevzner_10', 'pevzner_15'],
            'is_vegetarian': False,
            'is_vegan': False,
            'is_gluten_free': True,
            'rating': 4.7,
        },
        {
            'name': 'Салат Цезарь с курицей',
            'description': 'Популярный салат с курицей и соусом',
            'category': 'lunch',
            'prep_time': 20,
            'servings': 1,
            'calories': 380,
            'protein': 32,
            'fat': 22,
            'carbs': 18,
            'ingredients': [
                {'product': 'Куриная грудка', 'amount': 120},
                {'product': 'Салат', 'amount': 50},
                {'product': 'Помидор', 'amount': 50},
                {'product': 'Сыр (твердый)', 'amount': 30},
                {'product': 'Растительное масло', 'amount': 15},
            ],
            'instructions': 'Нарежьте курицу и овощи, заправьте маслом, посыпьте сыром',
            'suitable_diets': ['pevzner_5', 'pevzner_9', 'pevzner_10', 'pevzner_15'],
            'is_vegetarian': False,
            'is_vegan': False,
            'is_gluten_free': True,
            'rating': 4.4,
        },
        {
            'name': 'Борщ диетический',
            'description': 'Лёгкий борщ без зажарки',
            'category': 'lunch',
            'prep_time': 50,
            'servings': 4,
            'calories': 180,
            'protein': 8,
            'fat': 5,
            'carbs': 26,
            'ingredients': [
                {'product': 'Свекла', 'amount': 150},
                {'product': 'Капуста', 'amount': 100},
                {'product': 'Морковь', 'amount': 50},
                {'product': 'Лук репчатый', 'amount': 30},
                {'product': 'Картофель', 'amount': 100},
                {'product': 'Сметана (15%)', 'amount': 30},
            ],
            'instructions': 'Сварите овощи в бульоне, подайте со сметаной',
            'suitable_diets': ['pevzner_5', 'pevzner_9', 'pevzner_10', 'pevzner_15'],
            'is_vegetarian': True,
            'is_vegan': False,
            'is_gluten_free': True,
            'rating': 4.6,
        },
        {
            'name': 'Уха из рыбы',
            'description': 'Лёгкая рыбный суп',
            'category': 'lunch',
            'prep_time': 35,
            'servings': 3,
            'calories': 150,
            'protein': 15,
            'fat': 6,
            'carbs': 8,
            'ingredients': [
                {'product': 'Рыба (филе)', 'amount': 200},
                {'product': 'Картофель', 'amount': 100},
                {'product': 'Морковь', 'amount': 50},
                {'product': 'Лук репчатый', 'amount': 30},
            ],
            'instructions': 'Сварите рыбу с овощами, приправьте зеленью',
            'suitable_diets': ['pevzner_5', 'pevzner_9', 'pevzner_10', 'pevzner_15'],
            'is_vegetarian': False,
            'is_vegan': False,
            'is_gluten_free': True,
            'rating': 4.5,
        },
        {
            'name': 'Паровые котлеты с овощами',
            'description': 'Диетические котлеты на пару',
            'category': 'dinner',
            'prep_time': 40,
            'servings': 2,
            'calories': 320,
            'protein': 35,
            'fat': 12,
            'carbs': 20,
            'ingredients': [
                {'product': 'Говядина (нежирная)', 'amount': 200},
                {'product': 'Хлеб (ржаной)', 'amount': 30},
                {'product': 'Морковь', 'amount': 50},
                {'product': 'Брокколи', 'amount': 80},
            ],
            'instructions': 'Сделайте фарш, сформируйте котлеты, готовьте на пару 25 минут',
            'suitable_diets': ['pevzner_5', 'pevzner_9', 'pevzner_10', 'pevzner_15'],
            'is_vegetarian': False,
            'is_vegan': False,
            'is_gluten_free': False,
            'rating': 4.3,
        },
        {
            'name': 'Запечённая индейка с овощами',
            'description': 'Сочное мясо индейки с запечёнными овощами',
            'category': 'dinner',
            'prep_time': 50,
            'servings': 2,
            'calories': 380,
            'protein': 40,
            'fat': 14,
            'carbs': 22,
            'ingredients': [
                {'product': 'Индейка', 'amount': 200},
                {'product': 'Кабачок', 'amount': 80},
                {'product': 'Помидор', 'amount': 60},
                {'product': 'Болгарский перец', 'amount': 50},
                {'product': 'Растительное масло', 'amount': 15},
            ],
            'instructions': 'Запекайте индейку с овощами при 180°C 35 минут',
            'suitable_diets': ['pevzner_5', 'pevzner_9', 'pevzner_10', 'pevzner_15'],
            'is_vegetarian': False,
            'is_vegan': False,
            'is_gluten_free': True,
            'rating': 4.7,
        },
        {
            'name': 'Тушёные овощи',
            'description': 'Смесь полезных овощей на ужин',
            'category': 'dinner',
            'prep_time': 25,
            'servings': 2,
            'calories': 180,
            'protein': 6,
            'fat': 8,
            'carbs': 24,
            'ingredients': [
                {'product': 'Морковь', 'amount': 80},
                {'product': 'Капуста', 'amount': 100},
                {'product': 'Тыква', 'amount': 80},
                {'product': 'Растительное масло', 'amount': 15},
            ],
            'instructions': 'Тушите овощи на медленном огне 20 минут',
            'suitable_diets': ['pevzner_1', 'pevzner_2', 'pevzner_3', 'pevzner_4', 'pevzner_5', 'pevzner_7', 'pevzner_9', 'pevzner_10', 'pevzner_15'],
            'is_vegetarian': True,
            'is_vegan': True,
            'is_gluten_free': True,
            'rating': 4.4,
        },
        {
            'name': 'Смузи из фруктов',
            'description': 'Витаминный напиток для перекуса',
            'category': 'snack',
            'prep_time': 5,
            'servings': 1,
            'calories': 150,
            'protein': 3,
            'fat': 1,
            'carbs': 35,
            'ingredients': [
                {'product': 'Яблоко', 'amount': 100},
                {'product': 'Банан', 'amount': 50},
                {'product': 'Йогурт (натуральный)', 'amount': 100},
            ],
            'instructions': 'Взбейте все ингредиенты в блендере',
            'suitable_diets': ['pevzner_5', 'pevzner_9', 'pevzner_10', 'pevzner_15'],
            'is_vegetarian': True,
            'is_vegan': False,
            'is_gluten_free': True,
            'rating': 4.6,
        },
        {
            'name': 'Ореховая смесь',
            'description': 'Полезный перекус из орехов',
            'category': 'snack',
            'prep_time': 1,
            'servings': 1,
            'calories': 200,
            'protein': 5,
            'fat': 18,
            'carbs': 8,
            'ingredients': [
                {'product': 'Грецкие орехи', 'amount': 25},
                {'product': 'Миндаль', 'amount': 25},
            ],
            'instructions': 'Смешайте орехи в нужных пропорциях',
            'suitable_diets': ['pevzner_5', 'pevzner_9', 'pevzner_10', 'pevzner_15'],
            'is_vegetarian': True,
            'is_vegan': True,
            'is_gluten_free': True,
            'rating': 4.2,
        },
        {
            'name': 'Греческий йогурт с мёдом',
            'description': 'Простой и полезный перекус',
            'category': 'snack',
            'prep_time': 2,
            'servings': 1,
            'calories': 180,
            'protein': 15,
            'fat': 5,
            'carbs': 18,
            'ingredients': [
                {'product': 'Йогурт (натуральный)', 'amount': 150},
                {'product': 'Мёд', 'amount': 15},
            ],
            'instructions': 'Полейте йогурт мёдом',
            'suitable_diets': ['pevzner_5', 'pevzner_9', 'pevzner_10', 'pevzner_15'],
            'is_vegetarian': True,
            'is_vegan': False,
            'is_gluten_free': True,
            'rating': 4.5,
        },
        {
            'name': 'Овощной салат с оливковым маслом',
            'description': 'Лёгкий салат для любого приёма пищи',
            'category': 'snack',
            'prep_time': 10,
            'servings': 1,
            'calories': 120,
            'protein': 3,
            'fat': 10,
            'carbs': 8,
            'ingredients': [
                {'product': 'Огурец', 'amount': 80},
                {'product': 'Помидор', 'amount': 80},
                {'product': 'Растительное масло', 'amount': 15},
            ],
            'instructions': 'Нарежьте овощи, заправьте маслом',
            'suitable_diets': ['pevzner_1', 'pevzner_2', 'pevzner_3', 'pevzner_4', 'pevzner_5', 'pevzner_7', 'pevzner_9', 'pevzner_10', 'pevzner_15'],
            'is_vegetarian': True,
            'is_vegan': True,
            'is_gluten_free': True,
            'rating': 4.3,
        },
    ]

def get_default_achievements():
    """Список достижений для геймификации"""
    return [
        {
            'name': 'first_entry',
            'title': 'Первый шаг',
            'description': 'Добавьте первый приём пищи в дневник',
            'icon': '🏅',
            'xp_reward': 10,
            'category': 'nutrition',
        },
        {
            'name': 'week_streak',
            'title': 'Неделя совместно',
            'description': 'Пользуйтесь приложением 7 дней подряд',
            'icon': '🔥',
            'xp_reward': 50,
            'category': 'streak',
        },
        {
            'name': 'water_master',
            'title': 'Водный баланс',
            'description': 'Выпейте 8 стаканов воды за день',
            'icon': '💧',
            'xp_reward': 20,
            'category': 'nutrition',
        },
        {
            'name': 'calorie_goal',
            'title': 'В цель',
            'description': 'Достигните дневной нормы калорий (±10%)',
            'icon': '🎯',
            'xp_reward': 30,
            'category': 'nutrition',
        },
        {
            'name': 'balanced_diet',
            'title': 'Сбалансированное питание',
            'description': 'Соблюдайте норму БЖУ 3 дня подряд',
            'icon': '⚖️',
            'xp_reward': 40,
            'category': 'nutrition',
        },
        {
            'name': 'meal_planner',
            'title': 'Планировщик',
            'description': 'Составьте план питания на неделю',
            'icon': '📅',
            'xp_reward': 35,
            'category': 'special',
        },
        {
            'name': 'healthy_choice',
            'title': 'Здоровый выбор',
            'description': 'Добавьте 10 полезных продуктов',
            'icon': '🥗',
            'xp_reward': 25,
            'category': 'nutrition',
        },
        {
            'name': 'early_bird',
            'title': 'Ранняя пташка',
            'description': 'Добавьте завтрак до 8:00',
            'icon': '🌅',
            'xp_reward': 15,
            'category': 'nutrition',
        },
        {
            'name': 'level_5',
            'title': 'Новичок',
            'description': 'Достигните 5 уровня',
            'icon': '⭐',
            'xp_reward': 50,
            'category': 'special',
        },
        {
            'name': 'level_10',
            'title': 'Любитель',
            'description': 'Достигните 10 уровня',
            'icon': '🌟',
            'xp_reward': 100,
            'category': 'special',
        },
    ]
