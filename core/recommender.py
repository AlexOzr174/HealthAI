# Рекомендательная система на основе контента
from typing import List, Dict, Optional
from collections import Counter
import random

from database.operations import (
    get_all_recipes, get_recipes_by_diet, get_product_by_name,
    get_today_meals, get_user
)
from database.models import Recipe


class RecipeRecommender:
    """
    Рекомендательная система на основе контента (Content-Based Filtering).

    Алгоритм анализирует предпочтения пользователя и рекомендует рецепты,
    похожие на те, которые пользователь часто выбирает.
    """

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.user = get_user(user_id)
        self.all_recipes = get_all_recipes()
        self._initialize_user_preferences()

    def _initialize_user_preferences(self):
        """Инициализация предпочтений пользователя на основе истории"""
        if not self.user:
            self.preferred_categories = []
            self.preferred_ingredients = []
            self.avoid_ingredients = []
            return

        # Получаем историю приёмов пищи
        today_meals = get_today_meals(self.user_id)
        meal_names = [m.name for m in today_meals]

        # Анализируем категории
        category_counter = Counter()
        ingredient_counter = Counter()

        for meal in today_meals:
            # Ищем рецепт с похожим названием
            for recipe in self.all_recipes:
                if recipe.name.lower() in meal.name.lower() or meal.name.lower() in recipe.name.lower():
                    category_counter[recipe.category] += 1
                    # Подсчёт ингредиентов
                    if recipe.ingredients:
                        for ing in recipe.ingredients:
                            ingredient_counter[ing['product']] += 1

        self.preferred_categories = [cat for cat, count in category_counter.most_common(3)]
        self.preferred_ingredients = [ing for ing, count in ingredient_counter.most_common(10)]

    def get_recommendations(self, count: int = 5, category: str = None) -> List[Recipe]:
        """
        Получение рекомендаций рецептов.

        Args:
            count: Количество рекомендаций
            category: Фильтр по категории (breakfast, lunch, dinner, snack)

        Returns:
            Список рекомендованных рецептов
        """
        # Получаем подходящие рецепты
        if self.user and self.user.diet_type:
            suitable_recipes = get_recipes_by_diet(self.user.diet_type)
        else:
            suitable_recipes = self.all_recipes

        # Фильтруем по категории
        if category:
            suitable_recipes = [r for r in suitable_recipes if r.category == category]

        if not suitable_recipes:
            return []

        # Ранжируем рецепты
        scored_recipes = []
        for recipe in suitable_recipes:
            score = self._calculate_recipe_score(recipe)
            scored_recipes.append((recipe, score))

        # Сортируем по убыванию score
        scored_recipes.sort(key=lambda x: x[1], reverse=True)

        # Возвращаем топ-N рецептов
        return [r[0] for r in scored_recipes[:count]]

    def _calculate_recipe_score(self, recipe: Recipe) -> float:
        """
        Расчёт score рецепта на основе предпочтений пользователя.

        Args:
            recipe: Рецепт для оценки

        Returns:
            Score рецепта (0-10)
        """
        score = 5.0  # Базовый score

        # Бонус за предпочитаемые категории
        if recipe.category in self.preferred_categories:
            score += 2.0

        # Бонус за предпочитаемые ингредиенты
        if recipe.ingredients:
            for ing in recipe.ingredients:
                if ing['product'] in self.preferred_ingredients:
                    score += 0.5

        # Рейтинг рецепта
        score += (recipe.rating - 3.0)  # Нормализация рейтинга

        # Бонус за полезность
        if recipe.is_vegetarian:
            score += 0.3
        if recipe.is_gluten_free:
            score += 0.3

        # Штраф за неподходящие ингредиенты
        if recipe.ingredients:
            for ing in recipe.ingredients:
                product = get_product_by_name(ing['product'])
                if product and not product.is_healthy:
                    score -= 0.2

        return score

    def get_similar_recipes(self, recipe_id: int, count: int = 3) -> List[Recipe]:
        """
        Получение похожих рецептов.

        Args:
            recipe_id: ID рецепта, для которого ищем похожие
            count: Количество похожих рецептов

        Returns:
            Список похожих рецептов
        """
        target_recipe = None
        for recipe in self.all_recipes:
            if recipe.id == recipe_id:
                target_recipe = recipe
                break

        if not target_recipe:
            return []

        # Собираем ингредиенты целевого рецепта
        target_ingredients = set()
        if target_recipe.ingredients:
            for ing in target_recipe.ingredients:
                target_ingredients.add(ing['product'].lower())

        # Ищем рецепты с похожими ингредиентами
        scored_recipes = []
        for recipe in self.all_recipes:
            if recipe.id == recipe_id:
                continue

            recipe_ingredients = set()
            if recipe.ingredients:
                for ing in recipe.ingredients:
                    recipe_ingredients.add(ing['product'].lower())

            # Коэффициент Жаккара
            if target_ingredients or recipe_ingredients:
                intersection = len(target_ingredients & recipe_ingredients)
                union = len(target_ingredients | recipe_ingredients)
                similarity = intersection / union if union > 0 else 0
            else:
                similarity = 0

            scored_recipes.append((recipe, similarity))

        scored_recipes.sort(key=lambda x: x[1], reverse=True)
        return [r[0] for r in scored_recipes[:count]]

    def get_daily_recommendation(self, meal_type: str) -> Optional[Recipe]:
        """
        Получение рекомендации для конкретного приёма пищи.

        Args:
            meal_type: Тип приёма пищи (breakfast, lunch, dinner, snack)

        Returns:
            Рекомендованный рецепт
        """
        category_map = {
            'breakfast': ['breakfast', 'snack'],
            'lunch': ['lunch', 'dinner'],
            'dinner': ['lunch', 'dinner'],
            'snack': ['snack', 'breakfast'],
        }

        allowed_categories = category_map.get(meal_type, ['snack'])

        for category in allowed_categories:
            recommendations = self.get_recommendations(count=10, category=category)
            if recommendations:
                # Возвращаем случайный рецепт из топ-рекомендаций для разнообразия
                return random.choice(recommendations[:5])

        return None

    def analyze_nutritional_gaps(self, today_totals: dict) -> Dict[str, List[str]]:
        """
        Анализ недостающих питательных веществ.

        Args:
            today_totals: Словарь с сегодняшними показателями

        Returns:
            Словарь с рекомендациями по категориям
        """
        if not self.user:
            return {}

        # Целевые значения (упрощённо)
        if today_totals['protein'] < 50:
            protein_recommendations = self.get_recommendations(category='lunch', count=3)
            return {
                'protein_sources': [r.name for r in protein_recommendations if r.protein > 20]
            }

        if today_totals['carbs'] > 200:
            return {
                'low_carb_options': [r.name for r in
                                     self.get_recommendations(count=3) if r.carbs < 30]
            }

        return {}

    def get_healthy_substitutes(self, unhealthy_product: str) -> List[Dict]:
        """
        Получение здоровых заменителей для вредного продукта.

        Args:
            unhealthy_product: Название вредного продукта

        Returns:
            Список заменителей с информацией
        """
        substitutes = {
            'сахар': [
                {'name': 'Стевия', 'benefit': 'Нулевые калории'},
                {'name': 'Мёд', 'benefit': 'Натуральный, содержит витамины'},
            ],
            'белый хлеб': [
                {'name': 'Хлеб ржаной', 'benefit': 'Больше клетчатки, ниже гликемический индекс'},
                {'name': 'Цельнозерновой хлеб', 'benefit': 'Больше питательных веществ'},
            ],
            'масло сливочное': [
                {'name': 'Растительное масло', 'benefit': 'Нет холестерина'},
                {'name': 'Авокадо', 'benefit': 'Полезные жиры'},
            ],
            'свинина': [
                {'name': 'Куриная грудка', 'benefit': 'Меньше жира, больше белка'},
                {'name': 'Индейка', 'benefit': 'Диетическое мясо'},
            ],
            'картофель фри': [
                {'name': 'Печёный картофель', 'benefit': 'Меньше жира'},
                {'name': 'Овощное рагу', 'benefit': 'Больше клетчатки'},
            ],
        }

        # Поиск заменителей (нечувствительный к регистру)
        unhealthy_lower = unhealthy_product.lower()
        for key, subs in substitutes.items():
            if key in unhealthy_lower or unhealthy_lower in key:
                return subs

        return []


class SimpleRecommender:
    """
    Упрощённая рекомендательная система для быстрых рекомендаций.
    Не требует загрузки полной истории.
    """

    @staticmethod
    def get_quick_recommendations(
        diet_type: str = None,
        category: str = None,
        count: int = 5
    ) -> List[Recipe]:
        """
        Быстрые рекомендации без учёта истории пользователя.

        Args:
            diet_type: Тип диеты для фильтрации
            category: Категория рецепта
            count: Количество рекомендаций

        Returns:
            Список рекомендованных рецептов
        """
        recipes = get_all_recipes()

        # Фильтр по диете
        if diet_type:
            recipes = [r for r in recipes if diet_type in (r.suitable_diets or [])]

        # Фильтр по категории
        if category:
            recipes = [r for r in recipes if r.category == category]

        # Сортируем по рейтингу
        recipes.sort(key=lambda x: x.rating, reverse=True)

        return recipes[:count]

    @staticmethod
    def get_popular_recipes(count: int = 5) -> List[Recipe]:
        """
        Получение самых популярных рецептов (по рейтингу).

        Args:
            count: Количество рецептов

        Returns:
            Список популярных рецептов
        """
        recipes = get_all_recipes()
        recipes.sort(key=lambda x: x.rating, reverse=True)
        return recipes[:count]

    @staticmethod
    def get_healthy_recipes(count: int = 5) -> List[Recipe]:
        """
        Получение самых полезных рецептов.

        Args:
            count: Количество рецептов

        Returns:
            Список полезных рецептов
        """
        recipes = get_all_recipes()

        # Фильтруем рецепты с высоким содержанием белка и низким жира
        healthy_recipes = []
        for r in recipes:
            if r.protein > r.fat * 2 and r.calories < 500:
                healthy_recipes.append(r)

        # Сортируем по соотношению белка к калориям
        healthy_recipes.sort(key=lambda x: x.protein / max(x.calories, 1), reverse=True)

        return healthy_recipes[:count]

    @staticmethod
    def get_diet_recipes(diet_type: str, count: int = 10) -> List[Recipe]:
        """
        Получение рецептов для конкретной диеты.

        Args:
            diet_type: Тип диеты
            count: Количество рецептов

        Returns:
            Список рецептов для диеты
        """
        recipes = get_recipes_by_diet(diet_type)
        return recipes[:count]
