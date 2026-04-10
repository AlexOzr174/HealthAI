# ML-рекомендательная система для HealthAI
# Расширенная версия с Collaborative Filtering и персонализацией

from typing import List, Dict, Optional, Tuple
import numpy as np
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import pickle

from database.operations import (
    get_all_recipes, get_recipes_by_diet, get_product_by_name,
    get_today_meals, get_user, get_meals_by_date_range, get_all_products
)
from database.models import Recipe, Product


class AdvancedRecipeRecommender:
    """
    Продвинутая рекомендательная система с использованием:
    1. Content-Based Filtering (на основе характеристик рецептов)
    2. Collaborative Filtering (на основе поведения похожих пользователей)
    3. Hybrid Approach (комбинация подходов)
    4. Temporal Patterns (учёт времени и сезонности)
    """

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.user = get_user(user_id)
        self.all_recipes = get_all_recipes()
        self.all_products = get_all_products()
        
        # Векторы признаков для рецептов
        self.recipe_vectors = {}
        self.product_vectors = {}
        
        # История пользователя
        self.user_history = []
        self.user_preferences = {}
        
        # Инициализация
        self._build_recipe_vectors()
        self._build_product_vectors()
        self._load_user_history()
        self._analyze_user_preferences()

    def _build_recipe_vectors(self):
        """Построение векторов признаков для каждого рецепта"""
        for recipe in self.all_recipes:
            # Признаки: [белки, жиры, углеводы, калории, рейтинг, is_vegetarian, is_gluten_free]
            vector = np.array([
                recipe.protein / 50.0,  # Нормализация
                recipe.fat / 30.0,
                recipe.carbs / 100.0,
                recipe.calories / 500.0,
                recipe.rating / 5.0,
                1.0 if recipe.is_vegetarian else 0.0,
                1.0 if recipe.is_gluten_free else 0.0,
            ])
            self.recipe_vectors[recipe.id] = vector

    def _build_product_vectors(self):
        """Построение векторов признаков для продуктов"""
        for product in self.all_products:
            vector = np.array([
                product.protein / 50.0,
                product.fat / 30.0,
                product.carbs / 100.0,
                product.calories / 500.0,
                product.fiber / 10.0,
                product.glycemic_index / 100.0,
                1.0 if product.is_healthy else 0.0,
            ])
            self.product_vectors[product.id] = vector

    def _load_user_history(self):
        """Загрузка истории приёмов пищи пользователя"""
        if not self.user:
            return
        
        # Загружаем историю за последние 30 дней
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        meals = get_meals_by_date_range(self.user_id, start_date, end_date)
        self.user_history = meals

    def _analyze_user_preferences(self):
        """Анализ предпочтений пользователя"""
        if not self.user_history:
            self.user_preferences = {
                'preferred_categories': [],
                'preferred_ingredients': [],
                'avoid_ingredients': [],
                'preferred_calories_range': (0, 1000),
                'preferred_protein_level': 'medium',
            }
            return
        
        # Анализ категорий
        category_counter = Counter()
        ingredient_counter = Counter()
        calorie_list = []
        
        for meal in self.user_history:
            # Поиск соответствующего рецепта
            for recipe in self.all_recipes:
                if recipe.name.lower() in meal.name.lower():
                    category_counter[recipe.category] += 1
                    if recipe.ingredients:
                        for ing in recipe.ingredients:
                            ingredient_counter[ing['product']] += 1
                    calorie_list.append(recipe.calories)
                    break
            
            # Прямой анализ ингредиентов
            if meal.product_id:
                product = next((p for p in self.all_products if p.id == meal.product_id), None)
                if product:
                    ingredient_counter[product.name] += 1
        
        # Топ категории
        self.user_preferences['preferred_categories'] = [
            cat for cat, count in category_counter.most_common(3)
        ]
        
        # Топ ингредиенты
        self.user_preferences['preferred_ingredients'] = [
            ing for ing, count in ingredient_counter.most_common(10)
        ]
        
        # Диапазон калорий
        if calorie_list:
            avg_calories = np.mean(calorie_list)
            self.user_preferences['preferred_calories_range'] = (
                max(0, avg_calories - 100),
                avg_calories + 150
            )
        
        # Уровень белка
        protein_total = sum(m.protein for m in self.user_history)
        if protein_total > 100:
            self.user_preferences['preferred_protein_level'] = 'high'
        elif protein_total < 50:
            self.user_preferences['preferred_protein_level'] = 'low'
        else:
            self.user_preferences['preferred_protein_level'] = 'medium'

    def get_personalized_recommendations(
        self, 
        count: int = 5, 
        category: str = None,
        meal_time: str = None
    ) -> List[Recipe]:
        """
        Получение персонализированных рекомендаций с использованием гибридного подхода.
        
        Args:
            count: Количество рекомендаций
            category: Фильтр по категории
            meal_time: Время приёма пищи (для учёта временных паттернов)
        
        Returns:
            Список рекомендованных рецептов
        """
        if not self.all_recipes:
            return []
        
        # Фильтрация по диете
        if self.user and self.user.diet_type:
            suitable_recipes = get_recipes_by_diet(self.user.diet_type)
        else:
            suitable_recipes = self.all_recipes
        
        # Фильтрация по категории
        if category:
            suitable_recipes = [r for r in suitable_recipes if r.category == category]
        
        if not suitable_recipes:
            return []
        
        # Расчёт scores для каждого рецепта
        scored_recipes = []
        for recipe in suitable_recipes:
            content_score = self._calculate_content_score(recipe)
            collaborative_score = self._calculate_collaborative_score(recipe)
            temporal_score = self._calculate_temporal_score(recipe, meal_time)
            
            # Гибридный score (взвешенная сумма)
            hybrid_score = (
                0.5 * content_score +
                0.3 * collaborative_score +
                0.2 * temporal_score
            )
            
            scored_recipes.append((recipe, hybrid_score))
        
        # Сортировка по убыванию
        scored_recipes.sort(key=lambda x: x[1], reverse=True)
        
        # Добавление разнообразия (diversification)
        diversified = self._diversify_recommendations(scored_recipes, count)
        
        return [r[0] for r in diversified[:count]]

    def _calculate_content_score(self, recipe: Recipe) -> float:
        """Расчёт score на основе контента (предпочтения пользователя)"""
        score = 5.0
        
        # Бонус за предпочитаемые категории
        if recipe.category in self.user_preferences.get('preferred_categories', []):
            score += 2.0
        
        # Бонус за предпочитаемые ингредиенты
        if recipe.ingredients:
            for ing in recipe.ingredients:
                if ing['product'] in self.user_preferences.get('preferred_ingredients', []):
                    score += 0.5
        
        # Соответствие диапазону калорий
        min_cal, max_cal = self.user_preferences.get('preferred_calories_range', (0, 1000))
        if min_cal <= recipe.calories <= max_cal:
            score += 1.0
        
        # Рейтинг рецепта
        score += (recipe.rating - 3.0)
        
        # Бонус за полезность
        if recipe.is_vegetarian:
            score += 0.3
        if recipe.is_gluten_free:
            score += 0.3
        
        return score

    def _calculate_collaborative_score(self, recipe: Recipe) -> float:
        """
        Расчёт collaborative score на основе похожих пользователей.
        Упрощённая версия (в полной версии нужна БД с несколькими пользователями)
        """
        # Если нет истории, возвращаем средний score
        if not self.user_history:
            return recipe.rating
        
        # Находим рецепты, похожие на те, что пользователь уже ел
        recipe_vector = self.recipe_vectors.get(recipe.id)
        if recipe_vector is None:
            return 3.0
        
        similarities = []
        for meal in self.user_history[-10:]:  # Последние 10 приёмов пищи
            for hist_recipe in self.all_recipes:
                if hist_recipe.name.lower() in meal.name.lower():
                    hist_vector = self.recipe_vectors.get(hist_recipe.id)
                    if hist_vector is not None:
                        sim = cosine_similarity(
                            [recipe_vector], 
                            [hist_vector]
                        )[0][0]
                        similarities.append(sim)
                        break
        
        if similarities:
            return np.mean(similarities) * 5.0  # Масштабирование до 0-5
        
        return 3.0

    def _calculate_temporal_score(self, recipe: Recipe, meal_time: str = None) -> float:
        """Учёт временных паттернов (время суток, день недели, сезон)"""
        score = 3.0
        
        current_hour = datetime.now().hour
        
        # Время суток
        if meal_time == 'breakfast' or (6 <= current_hour < 12):
            if recipe.category == 'breakfast':
                score += 2.0
            elif recipe.calories < 400:
                score += 1.0
        
        elif meal_time == 'lunch' or (12 <= current_hour < 16):
            if recipe.category == 'lunch':
                score += 2.0
            elif recipe.protein > 20:
                score += 1.0
        
        elif meal_time == 'dinner' or (18 <= current_hour < 22):
            if recipe.category == 'dinner':
                score += 2.0
            elif recipe.calories < 500 and recipe.fat < 20:
                score += 1.0
        
        elif meal_time == 'snack':
            if recipe.category == 'snack':
                score += 2.0
            elif recipe.calories < 200:
                score += 1.0
        
        return score

    def _diversify_recommendations(
        self, 
        scored_recipes: List[Tuple[Recipe, float]], 
        count: int
    ) -> List[Tuple[Recipe, float]]:
        """Добавление разнообразия в рекомендации (избегаем однотипных рецептов)"""
        if len(scored_recipes) <= count:
            return scored_recipes
        
        diversified = []
        used_categories = set()
        used_ingredients = set()
        
        # Берём топ-N с разнообразием
        for recipe, score in scored_recipes:
            if len(diversified) >= count:
                break
            
            # Проверяем разнообразие
            category_overlap = recipe.category in used_categories
            
            ingredients = set()
            if recipe.ingredients:
                ingredients = {ing['product'] for ing in recipe.ingredients}
            ingredient_overlap = len(ingredients & used_ingredients) > 3
            
            # Добавляем рецепт, если он достаточно отличается
            if not category_overlap or not ingredient_overlap:
                diversified.append((recipe, score))
                used_categories.add(recipe.category)
                if recipe.ingredients:
                    used_ingredients.update(ing['product'] for ing in recipe.ingredients)
        
        # Если не набрали enough, добавляем остальные по score
        if len(diversified) < count:
            for recipe, score in scored_recipes:
                if len(diversified) >= count:
                    break
                if (recipe, score) not in diversified:
                    diversified.append((recipe, score))
        
        return diversified

    def get_similar_recipes(self, recipe_id: int, count: int = 5) -> List[Recipe]:
        """Поиск похожих рецептов на основе косинусного сходства"""
        target_vector = self.recipe_vectors.get(recipe_id)
        if target_vector is None:
            return []
        
        similarities = []
        for rid, vector in self.recipe_vectors.items():
            if rid == recipe_id:
                continue
            
            sim = cosine_similarity([target_vector], [vector])[0][0]
            recipe = next((r for r in self.all_recipes if r.id == rid), None)
            if recipe:
                similarities.append((recipe, sim))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [r[0] for r in similarities[:count]]

    def analyze_nutritional_gaps(self, days: int = 7) -> Dict[str, any]:
        """Анализ недостающих питательных веществ и рекомендации"""
        if not self.user_history:
            return {'status': 'no_data', 'recommendations': []}
        
        # Агрегация данных за период
        total_protein = sum(m.protein for m in self.user_history)
        total_fat = sum(m.fat for m in self.user_history)
        total_carbs = sum(m.carbs for m in self.user_history)
        total_calories = sum(m.calories for m in self.user_history)
        
        days_count = max(1, len(set(m.meal_date.date() for m in self.user_history)))
        
        avg_daily = {
            'calories': total_calories / days_count,
            'protein': total_protein / days_count,
            'fat': total_fat / days_count,
            'carbs': total_carbs / days_count,
        }
        
        recommendations = []
        
        # Целевые значения (упрощённо)
        target = self.user.target_calories if self.user else 2000
        target_protein = (self.user.weight * 1.5) if self.user else 90  # 1.5г на кг веса
        
        if avg_daily['protein'] < target_protein * 0.8:
            recommendations.append({
                'type': 'increase_protein',
                'message': f"Недостаток белка! Сейчас: {avg_daily['protein']:.0f}г, цель: {target_protein:.0f}г",
                'recipes': [r.name for r in self.get_personalized_recommendations(count=3, category='lunch') if r.protein > 25]
            })
        
        if avg_daily['calories'] > target * 1.1:
            recommendations.append({
                'type': 'reduce_calories',
                'message': f"Превышение калорий! Сейчас: {avg_daily['calories']:.0f}, цель: {target:.0f}",
                'recipes': [r.name for r in self.get_personalized_recommendations(count=3) if r.calories < 400]
            })
        
        return {
            'status': 'success',
            'averages': avg_daily,
            'targets': {'calories': target, 'protein': target_protein},
            'recommendations': recommendations
        }

    def get_healthy_substitutes(self, product_name: str) -> List[Dict]:
        """Поиск здоровых заменителей для продукта"""
        product = get_product_by_name(product_name)
        if not product or product.is_healthy:
            return []
        
        # Ищем похожие продукты в той же категории, но более полезные
        similar_category = [
            p for p in self.all_products 
            if p.category == product.category 
            and p.is_healthy 
            and p.id != product.id
        ]
        
        # Сортируем по полезности (меньше калорий, больше белка)
        similar_category.sort(key=lambda p: p.calories - p.protein * 2)
        
        substitutes = []
        for p in similar_category[:5]:
            substitutes.append({
                'name': p.name,
                'calories': p.calories,
                'protein': p.protein,
                'benefit': f"Меньше калорий ({p.calories} vs {product.calories}), "
                          f"больше белка ({p.protein}г)" if p.protein > product.protein 
                          else f"Меньше калорий: {p.calories} vs {product.calories}"
            })
        
        return substitutes

    def predict_weekly_plan(self) -> Dict[str, List[Recipe]]:
        """Предсказание плана питания на неделю"""
        week_plan = {
            'monday': {},
            'tuesday': {},
            'wednesday': {},
            'thursday': {},
            'friday': {},
            'saturday': {},
            'sunday': {},
        }
        
        days = list(week_plan.keys())
        meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
        
        for i, day in enumerate(days):
            for meal_type in meal_types:
                recipes = self.get_personalized_recommendations(
                    count=3,
                    category=meal_type,
                    meal_time=meal_type
                )
                week_plan[day][meal_type] = recipes[0] if recipes else None
        
        return week_plan


class UserClusterAnalyzer:
    """
    Кластеризация пользователей для улучшения collaborative filtering.
    В полной версии требует базу данных с множеством пользователей.
    """
    
    def __init__(self):
        self.user_profiles = {}
        self.clusters = {}
    
    def create_user_profile(self, user_id: int, preferences: Dict) -> Dict:
        """Создание профиля пользователя на основе предпочтений"""
        profile = {
            'user_id': user_id,
            'avg_calories': preferences.get('avg_calories', 2000),
            'protein_preference': preferences.get('protein_level', 'medium'),
            'diet_type': preferences.get('diet_type', 'none'),
            'goal': preferences.get('goal', 'maintain'),
            'preferred_categories': preferences.get('categories', []),
            'activity_level': preferences.get('activity', 'moderate'),
        }
        self.user_profiles[user_id] = profile
        return profile
    
    def find_similar_users(self, user_id: int, top_n: int = 5) -> List[int]:
        """Поиск похожих пользователей"""
        if user_id not in self.user_profiles:
            return []
        
        target_profile = self.user_profiles[user_id]
        similarities = []
        
        for uid, profile in self.user_profiles.items():
            if uid == user_id:
                continue
            
            # Простое сравнение профилей
            similarity = 0
            if profile['diet_type'] == target_profile['diet_type']:
                similarity += 0.3
            if profile['goal'] == target_profile['goal']:
                similarity += 0.3
            if profile['protein_preference'] == target_profile['protein_preference']:
                similarity += 0.2
            
            # overlap категорий
            common_cats = set(profile['preferred_categories']) & set(target_profile['preferred_categories'])
            similarity += 0.2 * len(common_cats) / max(len(target_profile['preferred_categories']), 1)
            
            similarities.append((uid, similarity))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [uid for uid, sim in similarities[:top_n]]
