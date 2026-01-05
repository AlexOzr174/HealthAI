# Модуль работы с базой данных
from .models import Base, User, Meal, Product, Recipe, Achievement, WeeklyPlan
from .init_db import init_database, populate_initial_data
from .operations import (
    get_user,
    save_user,
    add_meal,
    get_today_meals,
    get_product_by_name,
    get_recipes_by_diet,
    save_weekly_plan,
    get_weekly_plan,
    add_user_xp,
    get_user_achievements,
    unlock_achievement,
)

__all__ = [
    'Base', 'User', 'Meal', 'Product', 'Recipe', 'Achievement', 'WeeklyPlan',
    'init_database', 'populate_initial_data', 'get_user', 'save_user', 'add_meal', 'get_today_meals',
    'get_product_by_name', 'get_recipes_by_diet', 'save_weekly_plan',
    'get_weekly_plan', 'add_user_xp', 'get_user_achievements', 'unlock_achievement',
]
