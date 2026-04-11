# core/nutrition_api.py
"""
Nutrition API - Интеграция с внешними API питания
Поддержка: Edamam, USDA, Spoonacular
"""

import json
import importlib.util
from typing import Dict, List, Optional, Any
from datetime import datetime

# Проверка наличия requests
REQUESTS_AVAILABLE = importlib.util.find_spec("requests") is not None
if REQUESTS_AVAILABLE:
    import requests
else:
    print("Библиотека 'requests' не установлена. Будет использоваться только демо-режим.")


class NutritionAPI:
    """Клиент для работы с внешними API питания"""

    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        """
        Инициализация API клиентов
        
        Args:
            api_keys: Словарь {api_name: api_key}
                Пример: {'edamam_id': '...', 'edamam_key': '...', 'usda': '...', 'spoonacular': '...'}
        """
        self.api_keys = api_keys or {}

        # Конфигурация API
        self.edamam_app_id = self.api_keys.get('edamam_id', '')
        self.edamam_app_key = self.api_keys.get('edamam_key', '')
        self.usda_api_key = self.api_keys.get('usda', '')
        self.spoonacular_api_key = self.api_keys.get('spoonacular', '')

        # Базовые URL
        self.edamam_base_url = "https://api.edamam.com/api/food-database/v2/parser"
        self.usda_base_url = "https://api.nal.usda.gov/fdc/v1/foods/search"
        self.spoonacular_base_url = "https://api.spoonacular.com"

    # ==================== EDAMAM API ====================

    def search_food_edamam(self, query: str, nutrition_type: str = 'cooking') -> List[Dict]:
        """
        Поиск продуктов через Edamam API
        
        Args:
            query: Поисковый запрос (название продукта)
            nutrition_type: Тип питания ('cooking', 'restaurant')
        
        Returns:
            Список найденных продуктов с нутриентами
        """
        if not REQUESTS_AVAILABLE:
            return self._mock_search_food(query)

        if not self.edamam_app_id or not self.edamam_app_key:
            print("Edamam API ключи не настроены. Используются mock-данные.")
            return self._mock_search_food(query)

        try:
            params = {
                'app_id': self.edamam_app_id,
                'app_key': self.edamam_app_key,
                'ingr': query,
                'nutrition-type': nutrition_type
            }

            response = requests.get(self.edamam_base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for hint in data.get('hints', []):
                food = hint.get('food', {})
                nutrients = food.get('nutrients', {})

                results.append({
                    'food_id': food.get('foodId', ''),
                    'label': food.get('label', ''),
                    'known_as': food.get('knownAs', ''),
                    'nutrients': {
                        'calories': nutrients.get('ENERC_KCAL', 0),
                        'protein': nutrients.get('PROCNT', 0),
                        'carbs': nutrients.get('CHOCDF', 0),
                        'fat': nutrients.get('FAT', 0),
                        'fiber': nutrients.get('FIBTG', 0)
                    },
                    'category': food.get('category', 'Generic foods'),
                    'image': food.get('image', '')
                })

            return results[:10]  # Возвращаем топ-10 результатов

        except Exception as e:
            print(f"Ошибка Edamam API: {e}")
            return self._mock_search_food(query)

    def parse_recipe_edamam(self, ingredients: List[str]) -> Dict:
        """
        Анализ рецепта и расчёт нутриентов
        
        Args:
            ingredients: Список ингредиентов (например, ["1 cup flour", "2 eggs"])
        
        Returns:
            Данные о нутриентах рецепта
        """
        if not REQUESTS_AVAILABLE:
            return self._mock_parse_recipe(ingredients)

        if not self.edamam_app_id or not self.edamam_app_key:
            return self._mock_parse_recipe(ingredients)

        try:
            url = "https://api.edamam.com/api/food-database/v2/parser"
            params = {
                'app_id': self.edamam_app_id,
                'app_key': self.edamam_app_key,
                'ingr': ingredients
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            total_nutrients = {
                'calories': 0,
                'protein': 0,
                'carbs': 0,
                'fat': 0,
                'fiber': 0
            }

            parsed_ingredients = []
            for ingredient in data.get('parsed', []):
                food = ingredient.get('food', {})
                nutrients = food.get('nutrients', {})

                parsed_ingredients.append({
                    'name': food.get('label', ''),
                    'quantity': ingredient.get('quantity', 0),
                    'measure': ingredient.get('measure', {})
                })

                total_nutrients['calories'] += nutrients.get('ENERC_KCAL', 0)
                total_nutrients['protein'] += nutrients.get('PROCNT', 0)
                total_nutrients['carbs'] += nutrients.get('CHOCDF', 0)
                total_nutrients['fat'] += nutrients.get('FAT', 0)
                total_nutrients['fiber'] += nutrients.get('FIBTG', 0)

            return {
                'ingredients': parsed_ingredients,
                'total_nutrients': total_nutrients,
                'servings': 1
            }

        except Exception as e:
            print(f"Ошибка анализа рецепта Edamam: {e}")
            return self._mock_parse_recipe(ingredients)

    # ==================== USDA API ====================

    def search_food_usda(self, query: str, page_size: int = 10) -> List[Dict]:
        """
        Поиск продуктов через USDA FoodData Central API
        
        Args:
            query: Поисковый запрос
            page_size: Количество результатов
        
        Returns:
            Список найденных продуктов
        """
        if not REQUESTS_AVAILABLE:
            return self._mock_search_food(query)

        if not self.usda_api_key:
            print("USDA API ключ не настроен. Используются mock-данные.")
            return self._mock_search_food(query)

        try:
            params = {
                'api_key': self.usda_api_key,
                'query': query,
                'pageSize': page_size
            }

            response = requests.get(self.usda_base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for food in data.get('foods', []):
                results.append({
                    'fdc_id': food.get('fdcId', ''),
                    'description': food.get('description', ''),
                    'brand_owner': food.get('brandOwner', ''),
                    'ingredients': food.get('ingredients', ''),
                    'serving_size': food.get('servingSize', 100),
                    'serving_size_unit': food.get('servingSizeUnit', 'g')
                })

            return results

        except Exception as e:
            print(f"Ошибка USDA API: {e}")
            return self._mock_search_food(query)

    def get_food_details_usda(self, fdc_id: int) -> Optional[Dict]:
        """
        Получение детальной информации о продукте
        
        Args:
            fdc_id: ID продукта в базе USDA
        
        Returns:
            Детальная информация о продукте
        """
        if not REQUESTS_AVAILABLE:
            return None

        if not self.usda_api_key:
            return None

        try:
            url = f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}"
            params = {
                'api_key': self.usda_api_key,
                'nutrients': ['203', '204', '205', '208', '269']  # Protein, Fat, Carbs, Calories, Fiber
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            nutrients = {n['nutrientId']: n['value'] for n in data.get('foodNutrients', [])}

            return {
                'description': data.get('description', ''),
                'brand_owner': data.get('brandOwner', ''),
                'serving_size': data.get('servingSize', 100),
                'nutrients': {
                    'protein': nutrients.get(203, 0),
                    'fat': nutrients.get(204, 0),
                    'carbs': nutrients.get(205, 0),
                    'calories': nutrients.get(208, 0),
                    'fiber': nutrients.get(269, 0)
                }
            }

        except Exception as e:
            print(f"Ошибка получения деталей USDA: {e}")
            return None

    # ==================== SPOONACULAR API ====================

    def search_recipes_spoonacular(self, query: str, number: int = 5) -> List[Dict]:
        """
        Поиск рецептов через Spoonacular API
        
        Args:
            query: Поисковый запрос
            number: Количество результатов
        
        Returns:
            Список рецептов
        """
        if not REQUESTS_AVAILABLE:
            return self._mock_search_recipes(query)

        if not self.spoonacular_api_key:
            print("Spoonacular API ключ не настроен. Используются mock-данные.")
            return self._mock_search_recipes(query)

        try:
            url = f"{self.spoonacular_base_url}/recipes/complexSearch"
            params = {
                'apiKey': self.spoonacular_api_key,
                'query': query,
                'number': number,
                'addRecipeInformation': True,
                'addRecipeNutrition': True
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for recipe in data.get('results', []):
                results.append({
                    'id': recipe.get('id', ''),
                    'title': recipe.get('title', ''),
                    'image': recipe.get('image', ''),
                    'ready_in_minutes': recipe.get('readyInMinutes', 0),
                    'servings': recipe.get('servings', 1),
                    'health_score': recipe.get('healthScore', 0),
                    'nutrition': recipe.get('nutrition', {}),
                    'url': recipe.get('sourceUrl', '')
                })

            return results

        except Exception as e:
            print(f"Ошибка Spoonacular API: {e}")
            return self._mock_search_recipes(query)

    def analyze_recipe_spoonacular(self, ingredients: str) -> Dict:
        """
        Анализ рецепта по ингредиентам
        
        Args:
            ingredients: Строка с ингредиентами (через запятую)
        
        Returns:
            Анализ рецепта
        """
        if not REQUESTS_AVAILABLE:
            return self._mock_analyze_recipe(ingredients)

        if not self.spoonacular_api_key:
            return self._mock_analyze_recipe(ingredients)

        try:
            url = f"{self.spoonacular_base_url}/recipes/analyze"
            params = {
                'apiKey': self.spoonacular_api_key,
                'ingredientList': ingredients
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            return {
                'calories': data.get('calories', 0),
                'carbs': data.get('carbs', 0),
                'fat': data.get('fat', 0),
                'protein': data.get('protein', 0),
                'recipes_used': data.get('recipesUsed', []),
                'ingredients': data.get('ingredients', [])
            }

        except Exception as e:
            print(f"Ошибка анализа рецепта Spoonacular: {e}")
            return self._mock_analyze_recipe(ingredients)

    # ==================== MOCK ДАННЫЕ (когда нет API ключей) ====================

    def _mock_search_food(self, query: str) -> List[Dict]:
        """Фейковые данные для поиска продуктов"""
        mock_data = {
            'яблоко': [
                {'food_id': 'apple_1', 'label': 'Яблоко',
                 'nutrients': {'calories': 52, 'protein': 0.3, 'carbs': 14, 'fat': 0.2, 'fiber': 2.4}},
                {'food_id': 'apple_2', 'label': 'Яблоко красное',
                 'nutrients': {'calories': 55, 'protein': 0.4, 'carbs': 15, 'fat': 0.3, 'fiber': 2.5}}
            ],
            'курица': [
                {'food_id': 'chicken_1', 'label': 'Куриная грудка',
                 'nutrients': {'calories': 165, 'protein': 31, 'carbs': 0, 'fat': 3.6, 'fiber': 0}},
                {'food_id': 'chicken_2', 'label': 'Куриное филе',
                 'nutrients': {'calories': 170, 'protein': 32, 'carbs': 0, 'fat': 4, 'fiber': 0}}
            ],
            'рис': [
                {'food_id': 'rice_1', 'label': 'Рис белый',
                 'nutrients': {'calories': 130, 'protein': 2.7, 'carbs': 28, 'fat': 0.3, 'fiber': 0.4}},
                {'food_id': 'rice_2', 'label': 'Рис бурый',
                 'nutrients': {'calories': 112, 'protein': 2.6, 'carbs': 24, 'fat': 0.9, 'fiber': 1.8}}
            ]
        }

        # Поиск по частичному совпадению
        results = []
        query_lower = query.lower()
        for key, value in mock_data.items():
            if key in query_lower or query_lower in key:
                results.extend(value)

        return results if results else [{'food_id': 'unknown', 'label': query,
                                         'nutrients': {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'fiber': 0}}]

    def _mock_parse_recipe(self, ingredients: List[str]) -> Dict:
        """Фейковые данные для анализа рецепта"""
        return {
            'ingredients': [{'name': ing, 'quantity': 1, 'measure': {'unit': 'piece'}} for ing in ingredients],
            'total_nutrients': {'calories': 500, 'protein': 25, 'carbs': 60, 'fat': 15, 'fiber': 8},
            'servings': 2
        }

    def _mock_search_recipes(self, query: str) -> List[Dict]:
        """Фейковые данные для поиска рецептов"""
        return [
            {
                'id': 1,
                'title': f'Рецепт с {query}',
                'image': '',
                'ready_in_minutes': 30,
                'servings': 4,
                'health_score': 75,
                'nutrition': {},
                'url': ''
            }
        ]

    def _mock_analyze_recipe(self, ingredients: str) -> Dict:
        """Фейковые данные для анализа рецепта"""
        return {
            'calories': 400,
            'carbs': 45,
            'fat': 12,
            'protein': 25,
            'recipes_used': [],
            'ingredients': [{'name': ing.strip(), 'amount': 1} for ing in ingredients.split(',')]
        }

    # ==================== УНИВЕРСАЛЬНЫЙ ПОИСК ====================

    def search_food(self, query: str, source: str = 'auto') -> List[Dict]:
        """
        Универсальный поиск продуктов
        
        Args:
            query: Поисковый запрос
            source: Источник ('edamam', 'usda', 'auto')
        
        Returns:
            Список найденных продуктов
        """
        if source == 'auto':
            # Пробуем Edamam, если нет - USDA, если нет - mock
            if self.edamam_app_id and self.edamam_app_key:
                return self.search_food_edamam(query)
            elif self.usda_api_key:
                return self.search_food_usda(query)
            else:
                return self._mock_search_food(query)
        elif source == 'edamam':
            return self.search_food_edamam(query)
        elif source == 'usda':
            return self.search_food_usda(query)
        else:
            return self._mock_search_food(query)

    def get_api_status(self) -> Dict:
        """Получение статуса подключений к API"""
        return {
            'edamam': bool(self.edamam_app_id and self.edamam_app_key),
            'usda': bool(self.usda_api_key),
            'spoonacular': bool(self.spoonacular_api_key)
        }
