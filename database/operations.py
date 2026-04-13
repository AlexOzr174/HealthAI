# Операции с базой данных (CRUD)
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, func
from datetime import datetime, date, timedelta
from .models import (
    User,
    Meal,
    Product,
    Recipe,
    Achievement,
    UserAchievement,
    WeeklyPlan,
    ChatMessage,
)
from .init_db import get_engine

def get_session():
    """Получение сессии базы данных"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

# === Операции с пользователем ===

def get_user(user_id=None):
    """Получение пользователя по ID или первого пользователя"""
    session = get_session()
    try:
        if user_id:
            return session.query(User).filter(User.id == user_id).first()
        return session.query(User).first()
    finally:
        session.close()

def save_user(user_data):
    """Сохранение или создание пользователя"""
    session = get_session()
    try:
        user = session.query(User).first()
        if user:
            # Обновление существующего пользователя
            for key, value in user_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            user.updated_at = datetime.now()
        else:
            # Создание нового пользователя
            user = User(**user_data)
            session.add(user)
        session.commit()
        # Возвращаем ID и имя перед закрытием сессии
        result = {'id': user.id, 'name': user.name}
        return result
    finally:
        session.close()

def delete_user(user_id):
    """Удаление пользователя (для тестирования)"""
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            session.delete(user)
            session.commit()
    finally:
        session.close()


def update_user_fields(user_id: int, fields: dict):
    """Частичное обновление полей пользователя по id (без сброса непереданных колонок)."""
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        skip = {"id", "created_at"}
        for key, value in fields.items():
            if key in skip or not hasattr(user, key):
                continue
            setattr(user, key, value)
        user.updated_at = datetime.now()
        session.commit()
        return True
    finally:
        session.close()


# === Специальные диеты (кето, ИФ и т.д., JSON в users.special_diets_json) ===


def _default_special_diets_dict():
    return {"active_diets": [], "if_window": None}


def load_special_diets_settings(user_id: int) -> dict:
    """Загрузить сохранённые режимы спец. диет."""
    import json

    user = get_user(user_id)
    if not user:
        return _default_special_diets_dict()
    raw = getattr(user, "special_diets_json", None)
    if not raw:
        return _default_special_diets_dict()
    try:
        data = json.loads(raw)
        if not isinstance(data, dict):
            return _default_special_diets_dict()
        data.setdefault("active_diets", [])
        data.setdefault("if_window", None)
        return data
    except Exception:
        return _default_special_diets_dict()


def save_special_diets_settings(user_id: int, settings: dict) -> bool:
    """Сохранить режимы спец. диет в БД."""
    import json

    payload = json.dumps(settings, ensure_ascii=False)
    return update_user_fields(user_id, {"special_diets_json": payload})


# === История чата с AI (память для Ollama) ===

CHAT_HISTORY_MAX_ROWS = 120  # user+assistant пары; при превышении удаляются старые


def load_chat_history(user_id: int, limit: int = 50) -> list:
    """Последние сообщения по времени (по возрастанию), для передачи в LLM."""
    session = get_session()
    try:
        rows = (
            session.query(ChatMessage)
            .filter(ChatMessage.user_id == user_id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )
        if len(rows) > limit:
            rows = rows[-limit:]
        return [{"role": r.role, "content": r.content} for r in rows]
    finally:
        session.close()


def append_chat_turn(user_id: int, user_content: str, assistant_content: str) -> None:
    """Сохранить пару реплик; обрезать хвост, если слишком длинная история."""
    session = get_session()
    try:
        session.add(
            ChatMessage(user_id=user_id, role="user", content=user_content)
        )
        session.add(
            ChatMessage(user_id=user_id, role="assistant", content=assistant_content)
        )
        session.commit()

        total = (
            session.query(ChatMessage)
            .filter(ChatMessage.user_id == user_id)
            .count()
        )
        if total > CHAT_HISTORY_MAX_ROWS:
            excess = total - CHAT_HISTORY_MAX_ROWS
            old = (
                session.query(ChatMessage)
                .filter(ChatMessage.user_id == user_id)
                .order_by(ChatMessage.created_at.asc())
                .limit(excess)
                .all()
            )
            for m in old:
                session.delete(m)
            session.commit()
    finally:
        session.close()


def clear_chat_history(user_id: int) -> None:
    """Очистить историю диалога пользователя."""
    session = get_session()
    try:
        session.query(ChatMessage).filter(ChatMessage.user_id == user_id).delete(
            synchronize_session=False
        )
        session.commit()
    finally:
        session.close()


# === Операции с приёмами пищи ===

def add_meal(user_id, meal_data):
    """Добавление приёма пищи"""
    session = get_session()
    try:
        meal = Meal(user_id=user_id, **meal_data)
        session.add(meal)
        session.commit()
        # Возвращаем данные перед закрытием сессии
        result = {
            'id': meal.id,
            'name': meal.name,
            'calories': meal.calories,
            'protein': meal.protein,
            'fat': meal.fat,
            'carbs': meal.carbs,
            'meal_type': meal.meal_type,
            'amount': meal.amount,
        }
        return result
    finally:
        session.close()

def get_today_meals(user_id, meal_date=None):
    """Получение приёмов пищи за определённый день"""
    session = get_session()
    try:
        if meal_date is None:
            meal_date = date.today()
        elif isinstance(meal_date, str):
            meal_date = datetime.strptime(meal_date, '%Y-%m-%d').date()

        meals = session.query(Meal).filter(
            and_(
                Meal.user_id == user_id,
                func.date(Meal.meal_date) == meal_date
            )
        ).order_by(Meal.meal_time).all()
        return meals
    finally:
        session.close()

def get_meals_by_date_range(user_id, start_date, end_date):
    """Получение приёмов пищи за период"""
    session = get_session()
    try:
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        meals = session.query(Meal).filter(
            and_(
                Meal.user_id == user_id,
                func.date(Meal.meal_date) >= start_date,
                func.date(Meal.meal_date) <= end_date
            )
        ).order_by(Meal.meal_date).all()
        return meals
    finally:
        session.close()

def delete_meal(meal_id):
    """Удаление приёма пищи"""
    session = get_session()
    try:
        meal = session.query(Meal).filter(Meal.id == meal_id).first()
        if meal:
            session.delete(meal)
            session.commit()
    finally:
        session.close()

# === Операции с продуктами ===

def get_product_by_name(name):
    """Поиск продукта по названию"""
    session = get_session()
    try:
        product = session.query(Product).filter(
            Product.name.ilike(f'%{name}%')
        ).first()
        return product
    finally:
        session.close()

def search_products(query, limit=20):
    """Поиск продуктов по названию"""
    session = get_session()
    try:
        products = session.query(Product).filter(
            Product.name.ilike(f'%{query}%')
        ).limit(limit).all()
        return products
    finally:
        session.close()

def get_products_by_category(category):
    """Получение продуктов по категории"""
    session = get_session()
    try:
        products = session.query(Product).filter(
            Product.category == category
        ).all()
        return products
    finally:
        session.close()

def get_all_products():
    """Получение всех продуктов"""
    session = get_session()
    try:
        return session.query(Product).all()
    finally:
        session.close()

# === Операции с рецептами ===

def get_recipe_by_id(recipe_id):
    """Получение рецепта по ID"""
    session = get_session()
    try:
        return session.query(Recipe).filter(Recipe.id == recipe_id).first()
    finally:
        session.close()

def get_recipes_by_category(category):
    """Получение рецептов по категории (breakfast, lunch, dinner, snack)"""
    session = get_session()
    try:
        recipes = session.query(Recipe).filter(
            Recipe.category == category
        ).all()
        return recipes
    finally:
        session.close()

def get_recipes_by_diet(diet_type):
    """Получение рецептов, подходящих для определённой диеты"""
    session = get_session()
    try:
        recipes = session.query(Recipe).filter(
            Recipe.suitable_diets.contains([diet_type])
        ).all()
        return recipes
    finally:
        session.close()

def get_all_recipes():
    """Получение всех рецептов"""
    session = get_session()
    try:
        return session.query(Recipe).all()
    finally:
        session.close()

def search_recipes(query, diet_type=None, category=None):
    """Поиск рецептов с фильтрами"""
    session = get_session()
    try:
        recipes = session.query(Recipe).filter(
            Recipe.name.ilike(f'%{query}%')
        )
        if diet_type:
            recipes = recipes.filter(
                Recipe.suitable_diets.contains([diet_type])
            )
        if category:
            recipes = recipes.filter(Recipe.category == category)
        return recipes.all()
    finally:
        session.close()

# === Операции с планом питания ===

def save_weekly_plan(user_id, week_start_date, plan_data):
    """Сохранение плана питания на неделю"""
    session = get_session()
    try:
        # Удаление существующего плана на эту неделю
        session.query(WeeklyPlan).filter(
            and_(
                WeeklyPlan.user_id == user_id,
                WeeklyPlan.week_start_date == week_start_date
            )
        ).delete()

        # Добавление нового плана
        for item in plan_data:
            plan_item = WeeklyPlan(
                user_id=user_id,
                week_start_date=week_start_date,
                **item
            )
            session.add(plan_item)

        session.commit()
    finally:
        session.close()

def get_weekly_plan(user_id, week_start_date):
    """Получение плана питания на неделю"""
    session = get_session()
    try:
        plan = session.query(WeeklyPlan).filter(
            and_(
                WeeklyPlan.user_id == user_id,
                WeeklyPlan.week_start_date == week_start_date
            )
        ).all()
        return plan
    finally:
        session.close()

def get_weekly_shopping_list(user_id, week_start_date):
    """Генерация списка покупок на неделю"""
    session = get_session()
    try:
        plan = get_weekly_plan(user_id, week_start_date)
        shopping_list = {}

        for item in plan:
            if item.recipe_id:
                recipe = get_recipe_by_id(item.recipe_id)
                if recipe and recipe.ingredients:
                    for ing in recipe.ingredients:
                        product_name = ing['product']
                        amount = ing['amount']

                        if product_name in shopping_list:
                            shopping_list[product_name] += amount
                        else:
                            shopping_list[product_name] = amount

        # Конвертация в список с сортировкой
        result = []
        for product_name, amount in shopping_list.items():
            product = get_product_by_name(product_name)
            price = product.price_per_100g * amount / 100 if product else 0
            result.append({
                'product': product_name,
                'amount': round(amount, 1),
                'price': round(price, 2)
            })

        result.sort(key=lambda x: x['product'])
        return result
    finally:
        session.close()

# === Операции с достижениями ===

def get_all_achievements():
    """Получение всех достижений"""
    session = get_session()
    try:
        return session.query(Achievement).all()
    finally:
        session.close()

def get_user_achievements(user_id):
    """Получение достижений пользователя"""
    session = get_session()
    try:
        achievements = session.query(UserAchievement).filter(
            UserAchievement.user_id == user_id
        ).all()
        return [ua.achievement for ua in achievements]
    finally:
        session.close()

def unlock_achievement(user_id, achievement_name):
    """Разблокировка достижения"""
    session = get_session()
    try:
        # Проверяем, есть ли уже это достижение
        existing = session.query(UserAchievement).join(Achievement).filter(
            and_(
                UserAchievement.user_id == user_id,
                Achievement.name == achievement_name
            )
        ).first()

        if existing:
            return None  # Достижение уже разблокировано

        # Получаем достижение
        achievement = session.query(Achievement).filter(
            Achievement.name == achievement_name
        ).first()

        if not achievement:
            return None

        # Разблокируем достижение
        user_achievement = UserAchievement(
            user_id=user_id,
            achievement_id=achievement.id
        )
        session.add(user_achievement)

        # Добавляем XP пользователю
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            user.xp += achievement.xp_reward
            # Проверяем повышение уровня
            new_level = 1 + user.xp // 100
            if new_level > user.level:
                user.level = new_level

        session.commit()
        return achievement
    finally:
        session.close()

def get_available_achievements(user_id):
    """Получение доступных (неразблокированных) достижений"""
    session = get_session()
    try:
        # Получаем ID разблокированных достижений как список
        unlocked_ids = session.query(UserAchievement.achievement_id).filter(
            UserAchievement.user_id == user_id
        ).all()
        unlocked_list = [id[0] for id in unlocked_ids]

        if unlocked_list:
            achievements = session.query(Achievement).filter(
                ~Achievement.id.in_(unlocked_list)
            ).all()
        else:
            achievements = session.query(Achievement).all()
        return achievements
    finally:
        session.close()

# === Операции с XP и уровнем ===

def add_user_xp(user_id, xp_amount):
    """Добавление опыта пользователю"""
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            user.xp += xp_amount
            new_level = 1 + user.xp // 100
            leveled_up = new_level > user.level
            user.level = new_level
            session.commit()
            # Возвращаем данные перед закрытием сессии
            result = {'id': user.id, 'level': user.level, 'xp': user.xp}
            return result, leveled_up
    finally:
        session.close()

def update_streak(user_id):
    """Обновление серии дней"""
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            today = date.today()
            if user.updated_at.date() == today:
                return user.streak_days

            if user.updated_at.date() == today - timedelta(days=1):
                user.streak_days += 1
            else:
                user.streak_days = 1

            session.commit()
        return user.streak_days if user else 0
    finally:
        session.close()

def update_water_glasses(user_id, glasses):
    """Обновление количества выпитой воды"""
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            today = date.today()
            # Сбрасываем счётчик, если новый день
            if user.updated_at.date() < today:
                user.water_glasses = glasses
            else:
                user.water_glasses = glasses
            session.commit()
    finally:
        session.close()

# === Статистика ===

def get_user_stats(user_id):
    """Получение статистики пользователя"""
    session = get_session()
    try:
        today = date.today()
        week_ago = today - timedelta(days=7)

        user = session.query(User).filter(User.id == user_id).first()
        today_meals = get_today_meals(user_id, today)
        week_meals = get_meals_by_date_range(user_id, week_ago, today)

        # Статистика за сегодня
        today_totals = {
            'calories': sum(m.calories for m in today_meals),
            'protein': sum(m.protein for m in today_meals),
            'fat': sum(m.fat for m in today_meals),
            'carbs': sum(m.carbs for m in today_meals),
        }

        # Статистика за неделю
        week_totals = {
            'calories': sum(m.calories for m in week_meals),
            'protein': sum(m.protein for m in week_meals),
            'fat': sum(m.fat for m in week_meals),
            'carbs': sum(m.carbs for m in week_meals),
            'days_logged': len(set(m.meal_date.date() for m in week_meals)),
        }

        return {
            'user': user.to_dict() if user else None,
            'today': today_totals,
            'week': week_totals,
            'today_meals_count': len(today_meals),
        }
    finally:
        session.close()
