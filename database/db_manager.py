# Database Manager - совместимый интерфейс для HealthAI
import logging
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, func
from datetime import datetime, date, timedelta

_log = logging.getLogger(__name__)
from .models import User, Meal, Product, Recipe, Achievement, UserAchievement, WeeklyPlan
from .init_db import get_engine, init_database

class DatabaseManager:
    """Универсальный менеджер базы данных"""
    
    def __init__(self, db_path=None):
        """Инициализация менеджера БД"""
        self.db_path = db_path
        self.engine = get_engine()
        
    def create_tables(self):
        """Создание таблиц"""
        init_database()
        
    def get_session(self):
        """Получение сессии"""
        Session = sessionmaker(bind=self.engine)
        return Session()
    
    # === Пользователь ===
    
    def add_user(self, user_data):
        """Добавление/обновление пользователя"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(email=user_data.get('email')).first()
            if user:
                for key, value in user_data.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                user.updated_at = datetime.now()
            else:
                user = User(**user_data)
                session.add(user)
            
            session.commit()
            session.refresh(user)
            
            result = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'age': user.age,
                'gender': user.gender,
                'height': user.height,
                'weight': user.weight,
                'activity_level': user.activity_level,
                'goal': user.goal,
                'target_weight': user.target_weight,
                'xp': user.xp,
                'level': user.level,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
            return result
        finally:
            session.close()
    
    def get_user(self, user_id=None):
        """Получение пользователя"""
        session = self.get_session()
        try:
            if user_id:
                user = session.query(User).filter(User.id == user_id).first()
            else:
                user = session.query(User).first()
            
            if user:
                return {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'age': user.age,
                    'gender': user.gender,
                    'height': user.height,
                    'weight': user.weight,
                    'activity_level': user.activity_level,
                    'goal': user.goal,
                    'target_weight': user.target_weight,
                    'xp': user.xp,
                    'level': user.level
                }
            return None
        finally:
            session.close()
    
    # === Приёмы пищи ===
    
    def add_meal(self, meal_data):
        """Добавление приёма пищи"""
        session = self.get_session()
        try:
            meal = Meal(**meal_data)
            session.add(meal)
            session.commit()
            session.refresh(meal)
            
            # Обновление XP пользователя
            user = session.query(User).first()
            if user:
                user.xp += 10
                user.level = user.xp // 100 + 1
            
            session.commit()
            
            return {
                'id': meal.id,
                'user_id': meal.user_id,
                'product_id': meal.product_id,
                'meal_type': meal.meal_type,
                'quantity': meal.quantity,
                'calories': meal.calories,
                'protein': meal.protein,
                'carbs': meal.carbs,
                'fat': meal.fat,
                'timestamp': meal.timestamp.isoformat() if meal.timestamp else None
            }
        finally:
            session.close()
    
    def get_meals(self, user_id, date_filter=None):
        """Получение приёмов пищи"""
        session = self.get_session()
        try:
            query = session.query(Meal).filter(Meal.user_id == user_id)
            if date_filter:
                query = query.filter(func.date(Meal.timestamp) == date_filter)
            meals = query.all()
            
            return [{
                'id': m.id,
                'product_id': m.product_id,
                'meal_type': m.meal_type,
                'quantity': m.quantity,
                'calories': m.calories,
                'protein': m.protein,
                'carbs': m.carbs,
                'fat': m.fat,
                'timestamp': m.timestamp.isoformat() if m.timestamp else None
            } for m in meals]
        finally:
            session.close()
    
    # === Продукты ===
    
    def get_products(self, limit=100):
        """Получение списка продуктов"""
        session = self.get_session()
        try:
            products = session.query(Product).limit(limit).all()
            return [{
                'id': p.id,
                'name': p.name,
                'category': p.category,
                'calories': p.calories,
                'protein': p.protein,
                'carbs': p.carbs,
                'fat': p.fat,
                'fiber': p.fiber,
                'sugar': p.sugar,
                'glycemic_index': p.glycemic_index,
                'health_score': p.health_score
            } for p in products]
        finally:
            session.close()
    
    # === Рецепты ===
    
    def get_recipes(self, limit=50):
        """Получение списка рецептов"""
        session = self.get_session()
        try:
            recipes = session.query(Recipe).limit(limit).all()
            return [{
                'id': r.id,
                'name': r.name,
                'category': r.category,
                'prep_time': r.prep_time,
                'cook_time': r.cook_time,
                'servings': r.servings,
                'calories': r.calories,
                'protein': r.protein,
                'carbs': r.carbs,
                'fat': r.fat,
                'ingredients': r.ingredients,
                'instructions': r.instructions,
                'difficulty': r.difficulty
            } for r in recipes]
        finally:
            session.close()
    
    # === Достижения ===
    
    def get_achievements(self):
        """Получение всех достижений"""
        session = self.get_session()
        try:
            achievements = session.query(Achievement).all()
            return [{
                'id': a.id,
                'name': a.name,
                'description': a.description,
                'xp_reward': a.xp_reward,
                'icon': a.icon
            } for a in achievements]
        finally:
            session.close()
    
    def add_achievement(self, user_id, achievement_id):
        """Добавление достижения пользователю"""
        session = self.get_session()
        try:
            user_achievement = UserAchievement(user_id=user_id, achievement_id=achievement_id)
            session.add(user_achievement)
            
            achievement = session.query(Achievement).get(achievement_id)
            user = session.query(User).get(user_id)
            if user and achievement:
                user.xp += achievement.xp_reward
                user.level = user.xp // 100 + 1
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            _log.warning("add_achievement: не удалось сохранить: %s", e, exc_info=True)
            return False
        finally:
            session.close()
