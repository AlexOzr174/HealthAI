# Модели данных SQLAlchemy для HealthAI
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime, date
import os

Base = declarative_base()

class User(Base):
    """Модель пользователя"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    gender = Column(String(10), nullable=False)  # 'male' или 'female'
    age = Column(Integer, nullable=False)
    height = Column(Float, nullable=False)  # в см
    weight = Column(Float, nullable=False)  # в кг
    activity_level = Column(String(20), nullable=False)
    goal = Column(String(20), nullable=False)  # 'lose', 'maintain', 'gain'
    diet_type = Column(String(50), nullable=True)  # 'pevzner_1' - 'pevzner_15' или None
    # JSON: {"active_diets": ["keto", "if"], "if_window": 8} — спец. диеты (кето, палео, ИФ и т.д.)
    special_diets_json = Column(Text, nullable=True)
    bmr = Column(Float, nullable=False)  # Базальный метаболизм
    tdee = Column(Float, nullable=False)  # Суточная норма калорий
    target_calories = Column(Float, nullable=False)  # Целевые калории с учётом цели
    xp = Column(Integer, default=0)  # Опыт для геймификации
    level = Column(Integer, default=1)
    streak_days = Column(Integer, default=0)  # Дней подряд
    water_glasses = Column(Integer, default=0)  # Стаканы воды сегодня
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Связи
    meals = relationship("Meal", back_populates="user", order_by="Meal.meal_time")
    achievements = relationship("UserAchievement", back_populates="user")
    chat_messages = relationship(
        "ChatMessage",
        back_populates="user",
        order_by="ChatMessage.created_at",
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'gender': self.gender,
            'age': self.age,
            'height': self.height,
            'weight': self.weight,
            'activity_level': self.activity_level,
            'goal': self.goal,
            'diet_type': self.diet_type,
            'bmr': self.bmr,
            'tdee': self.tdee,
            'target_calories': self.target_calories,
            'xp': self.xp,
            'level': self.level,
            'streak_days': self.streak_days,
        }


class Product(Base):
    """Модель продукта питания"""
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    category = Column(String(50), nullable=False)  # 'vegetables', 'fruits', 'meat', 'dairy', etc.
    calories = Column(Float, nullable=False)  # на 100г
    protein = Column(Float, nullable=False)  # на 100г
    fat = Column(Float, nullable=False)  # на 100г
    carbs = Column(Float, nullable=False)  # на 100г
    fiber = Column(Float, default=0)  # на 100г
    sugar = Column(Float, default=0)  # на 100г
    sodium = Column(Float, default=0)  # на 100г
    price_per_100g = Column(Float, default=0)  # Средняя цена
    is_dangerous = Column(Boolean, default=False)  # Опасный при некоторых диетах
    dangerous_for_diets = Column(JSON, default=list)  # Список диет, для которых опасен
    is_healthy = Column(Boolean, default=True)  # Здоровый продукт
    glycemic_index = Column(Integer, default=0)  # Гликемический индекс

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'calories': self.calories,
            'protein': self.protein,
            'fat': self.fat,
            'carbs': self.carbs,
            'fiber': self.fiber,
            'sugar': self.sugar,
            'sodium': self.sodium,
            'price_per_100g': self.price_per_100g,
            'is_healthy': self.is_healthy,
            'glycemic_index': self.glycemic_index,
        }


class Recipe(Base):
    """Модель рецепта"""
    __tablename__ = 'recipes'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)  # breakfast, lunch, dinner, snack
    cuisine = Column(String(50), default='general')  # cuisine type
    prep_time = Column(Integer, default=0)  # минуты
    servings = Column(Integer, default=1)
    calories = Column(Float, nullable=False)  # на порцию
    protein = Column(Float, nullable=False)  # на порцию
    fat = Column(Float, nullable=False)  # на порцию
    carbs = Column(Float, nullable=False)  # на порцию
    ingredients = Column(JSON, nullable=False)  # Список ингредиентов
    instructions = Column(Text, nullable=True)
    suitable_diets = Column(JSON, default=list)  # Подходящие диеты по Певзнеру
    is_vegetarian = Column(Boolean, default=False)
    is_vegan = Column(Boolean, default=False)
    is_gluten_free = Column(Boolean, default=False)
    is_dairy_free = Column(Boolean, default=False)
    rating = Column(Float, default=5.0)
    image_path = Column(String(500), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'calories': self.calories,
            'protein': self.protein,
            'fat': self.fat,
            'carbs': self.carbs,
            'suitable_diets': self.suitable_diets,
            'rating': self.rating,
        }


class Meal(Base):
    """Модель приёма пищи"""
    __tablename__ = 'meals'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'), nullable=True)
    meal_type = Column(String(20), nullable=False)  # breakfast, lunch, dinner, snack
    name = Column(String(200), nullable=False)  # Название блюда/продукта
    amount = Column(Float, nullable=False)  # в граммах
    calories = Column(Float, nullable=False)
    protein = Column(Float, nullable=False)
    fat = Column(Float, nullable=False)
    carbs = Column(Float, nullable=False)
    meal_date = Column(DateTime, default=datetime.now)
    meal_time = Column(DateTime, default=datetime.now)
    notes = Column(Text, nullable=True)

    # Связи
    user = relationship("User", back_populates="meals")
    product = relationship("Product")
    recipe = relationship("Recipe")

    def to_dict(self):
        return {
            'id': self.id,
            'meal_type': self.meal_type,
            'name': self.name,
            'amount': self.amount,
            'calories': self.calories,
            'protein': self.protein,
            'fat': self.fat,
            'carbs': self.carbs,
            'meal_time': self.meal_time.strftime('%H:%M'),
            'meal_date': self.meal_date.strftime('%Y-%m-%d'),
        }


class Achievement(Base):
    """Модель достижения"""
    __tablename__ = 'achievements'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String(100), nullable=False)
    xp_reward = Column(Integer, default=10)
    category = Column(String(50), default='general')  # nutrition, activity, streak, special

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'title': self.title,
            'description': self.description,
            'icon': self.icon,
            'xp_reward': self.xp_reward,
            'category': self.category,
        }


class ChatMessage(Base):
    """Сообщения чата с AI (память диалога для Ollama и контекста)."""

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' | 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="chat_messages")


class UserAchievement(Base):
    """Связь пользователей и достижений"""
    __tablename__ = 'user_achievements'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    achievement_id = Column(Integer, ForeignKey('achievements.id'), nullable=False)
    unlocked_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement")


class WeeklyPlan(Base):
    """Модель недельного плана питания"""
    __tablename__ = 'weekly_plans'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    week_start_date = Column(String(20), nullable=False)  # Формат 'YYYY-MM-DD'
    day_of_week = Column(Integer, nullable=False)  # 0 = Понедельник
    meal_type = Column(String(20), nullable=False)
    recipe_id = Column(Integer, ForeignKey('recipes.id'), nullable=True)
    custom_meal = Column(Text, nullable=True)  # Если рецепт не из базы
    calories = Column(Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'day_of_week': self.day_of_week,
            'meal_type': self.meal_type,
            'recipe_id': self.recipe_id,
            'custom_meal': self.custom_meal,
            'calories': self.calories,
        }
