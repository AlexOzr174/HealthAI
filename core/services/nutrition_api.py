"""
Сервис интеграции с внешними API питания
Поддержка: Edamam, USDA FoodData Central, Spoonacular, Nutritionix
"""

import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json


@dataclass
class FoodItem:
    """Модель пищевого продукта"""
    name: str
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: float = 0.0
    sugar: float = 0.0
    serving_size: str = "100g"
    source: str = ""


@dataclass
class RecipeItem:
    """Модель рецепта"""
    title: str
    calories: float
    protein: float
    carbs: float
    fat: float
    ingredients: List[str]
    instructions: str
    image_url: str = ""
    prep_time: int = 0
    cook_time: int = 0
    servings: int = 1
    source: str = ""


class NutritionAPI:
    """Клиент для работы с API питания"""
    
    def __init__(self, api_keys: Dict[str, str] = None):
        self.api_keys = api_keys or {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'HealthAI/1.0'
        })
    
    def test_connection(self, service: str) -> bool:
        """Тест подключения к сервису"""
        try:
            if service == 'edamam':
                return self._test_edamam()
            elif service == 'usda':
                return self._test_usda()
            elif service == 'spoonacular':
                return self._test_spoonacular()
            elif service == 'nutritionix':
                return self._test_nutritionix()
            return False
        except Exception as e:
            print(f"Connection test failed for {service}: {e}")
            return False
    
    def _test_edamam(self) -> bool:
        """Тест подключения к Edamam"""
        app_id = self.api_keys.get('edamam_app_id')
        app_key = self.api_keys.get('edamam_key')
        
        if not app_id or not app_key:
            return False
        
        url = "https://api.edamam.com/api/food-database/v2/parser"
        params = {
            'app_id': app_id,
            'app_key': app_key,
            'ingr': 'apple'
        }
        
        response = self.session.get(url, params=params, timeout=5)
        return response.status_code == 200
    
    def _test_usda(self) -> bool:
        """Тест подключения к USDA"""
        api_key = self.api_keys.get('usda_key')
        
        if not api_key:
            return False
        
        url = "https://api.nal.usda.gov/fdc/v1/foods/search"
        params = {
            'api_key': api_key,
            'query': 'apple',
            'pageSize': 1
        }
        
        response = self.session.get(url, params=params, timeout=5)
        return response.status_code == 200
    
    def _test_spoonacular(self) -> bool:
        """Тест подключения к Spoonacular"""
        api_key = self.api_keys.get('spoonacular_key')
        
        if not api_key:
            return False
        
        url = "https://api.spoonacular.com/food/ingredients/search"
        params = {
            'apiKey': api_key,
            'query': 'apple',
            'number': 1
        }
        
        response = self.session.get(url, params=params, timeout=5)
        return response.status_code == 200
    
    def _test_nutritionix(self) -> bool:
        """Тест подключения к Nutritionix"""
        app_id = self.api_keys.get('nutritionix_app_id')
        app_key = self.api_keys.get('nutritionix_key')
        
        if not app_id or not app_key:
            return False
        
        url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
        headers = {
            'x-app-id': app_id,
            'x-app-key': app_key,
            'Content-Type': 'application/json'
        }
        data = {'query': 'apple'}
        
        response = self.session.post(url, json=data, headers=headers, timeout=5)
        return response.status_code == 200
    
    def search_food(self, query: str, service: str = 'auto') -> List[FoodItem]:
        """Поиск продуктов по названию"""
        if service == 'auto':
            # Пробуем сервисы по порядку
            for svc in ['edamam', 'usda', 'spoonacular']:
                results = self._search_food_service(query, svc)
                if results:
                    return results
            return []
        else:
            return self._search_food_service(query, service)
    
    def _search_food_service(self, query: str, service: str) -> List[FoodItem]:
        """Поиск продуктов в конкретном сервисе"""
        try:
            if service == 'edamam':
                return self._search_edamam(query)
            elif service == 'usda':
                return self._search_usda(query)
            elif service == 'spoonacular':
                return self._search_spoonacular(query)
            return []
        except Exception as e:
            print(f"Search failed for {service}: {e}")
            return []
    
    def _search_edamam(self, query: str) -> List[FoodItem]:
        """Поиск в Edamam"""
        app_id = self.api_keys.get('edamam_app_id')
        app_key = self.api_keys.get('edamam_key')
        
        if not app_id or not app_key:
            return []
        
        url = "https://api.edamam.com/api/food-database/v2/parser"
        params = {
            'app_id': app_id,
            'app_key': app_key,
            'ingr': query
        }
        
        response = self.session.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return []
        
        data = response.json()
        foods = []
        
        for item in data.get('hints', [])[:10]:
            food = item.get('food', {})
            nutrients = food.get('nutrients', {})
            
            foods.append(FoodItem(
                name=food.get('label', ''),
                calories=nutrients.get('ENERC_KCAL', 0),
                protein=nutrients.get('PROCNT', 0),
                carbs=nutrients.get('CHOCDF', 0),
                fat=nutrients.get('FAT', 0),
                fiber=nutrients.get('FIBTG', 0),
                sugar=nutrients.get('SUGAR', 0),
                serving_size="100g",
                source='Edamam'
            ))
        
        return foods
    
    def _search_usda(self, query: str) -> List[FoodItem]:
        """Поиск в USDA"""
        api_key = self.api_keys.get('usda_key')
        
        if not api_key:
            return []
        
        url = "https://api.nal.usda.gov/fdc/v1/foods/search"
        params = {
            'api_key': api_key,
            'query': query,
            'pageSize': 10
        }
        
        response = self.session.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return []
        
        data = response.json()
        foods = []
        
        for item in data.get('foods', [])[:10]:
            nutrients = {n['name']: n['value'] for n in item.get('foodNutrients', [])}
            
            foods.append(FoodItem(
                name=item.get('description', ''),
                calories=nutrients.get('Energy', 0),
                protein=nutrients.get('Protein', 0),
                carbs=nutrients.get('Carbohydrate, by difference', 0),
                fat=nutrients.get('Total lipid (fat)', 0),
                fiber=nutrients.get('Fiber, total dietary', 0),
                sugar=nutrients.get('Sugars, total including NLEA', 0),
                serving_size="100g",
                source='USDA'
            ))
        
        return foods
    
    def _search_spoonacular(self, query: str) -> List[FoodItem]:
        """Поиск в Spoonacular"""
        api_key = self.api_keys.get('spoonacular_key')
        
        if not api_key:
            return []
        
        url = "https://api.spoonacular.com/food/ingredients/search"
        params = {
            'apiKey': api_key,
            'query': query,
            'number': 10
        }
        
        response = self.session.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return []
        
        data = response.json()
        foods = []
        
        for item in data.get('results', [])[:10]:
            foods.append(FoodItem(
                name=item.get('name', ''),
                calories=item.get('calories', 0) or 0,
                protein=0,  # Spoonacular не всегда возвращает макросы в поиске
                carbs=0,
                fat=0,
                serving_size=item.get('amount', 1),
                source='Spoonacular'
            ))
        
        return foods
    
    def search_recipes(self, query: str, calories_min: int = None, 
                       calories_max: int = None, diet: str = None,
                       service: str = 'spoonacular') -> List[RecipeItem]:
        """Поиск рецептов"""
        try:
            if service == 'spoonacular':
                return self._search_recipes_spoonacular(
                    query, calories_min, calories_max, diet
                )
            elif service == 'edamam':
                return self._search_recipes_edamam(
                    query, calories_min, calories_max, diet
                )
            return []
        except Exception as e:
            print(f"Recipe search failed: {e}")
            return []
    
    def _search_recipes_spoonacular(self, query: str, calories_min: int = None,
                                     calories_max: int = None, 
                                     diet: str = None) -> List[RecipeItem]:
        """Поиск рецептов в Spoonacular"""
        api_key = self.api_keys.get('spoonacular_key')
        
        if not api_key:
            return []
        
        url = "https://api.spoonacular.com/recipes/complexSearch"
        params = {
            'apiKey': api_key,
            'query': query,
            'number': 10,
            'addRecipeInformation': True
        }
        
        if calories_min:
            params['minCalories'] = calories_min
        if calories_max:
            params['maxCalories'] = calories_max
        if diet:
            diet_map = {
                'keto': 'ketogenic',
                'paleo': 'paleolithic',
                'vegan': 'vegan',
                'vegetarian': 'vegetarian',
                'gluten_free': 'gluten-free'
            }
            params['diet'] = diet_map.get(diet, diet)
        
        response = self.session.get(url, params=params, timeout=15)
        if response.status_code != 200:
            return []
        
        data = response.json()
        recipes = []
        
        for item in data.get('results', [])[:10]:
            recipes.append(RecipeItem(
                title=item.get('title', ''),
                calories=item.get('calories', 0) or 0,
                protein=item.get('protein', 0) or 0,
                carbs=item.get('carbs', 0) or 0,
                fat=item.get('fat', 0) or 0,
                ingredients=[],
                instructions='',
                image_url=item.get('image', ''),
                prep_time=item.get('preparationMinutes', 0) or 0,
                cook_time=item.get('cookingMinutes', 0) or 0,
                servings=item.get('servings', 1),
                source='Spoonacular'
            ))
        
        return recipes
    
    def _search_recipes_edamam(self, query: str, calories_min: int = None,
                                calories_max: int = None,
                                diet: str = None) -> List[RecipeItem]:
        """Поиск рецептов в Edamam"""
        app_id = self.api_keys.get('edamam_app_id')
        app_key = self.api_keys.get('edamam_key')
        
        if not app_id or not app_key:
            return []
        
        url = "https://api.edamam.com/search"
        params = {
            'app_id': app_id,
            'app_key': app_key,
            'q': query,
            'to': 10
        }
        
        if calories_min and calories_max:
            params['calories'] = f'{calories_min}-{calories_max}'
        
        if diet:
            diet_map = {
                'keto': 'keto-friendly',
                'paleo': 'paleo',
                'vegan': 'vegan',
                'vegetarian': 'vegetarian',
                'gluten_free': 'gluten-free'
            }
            params['health'] = diet_map.get(diet, diet)
        
        response = self.session.get(url, params=params, timeout=15)
        if response.status_code != 200:
            return []
        
        data = response.json()
        recipes = []
        
        for item in data.get('hits', [])[:10]:
            recipe = item.get('recipe', {})
            nutrients = recipe.get('totalNutrients', {})
            
            recipes.append(RecipeItem(
                title=recipe.get('label', ''),
                calories=nutrients.get('ENERC_KCAL', {}).get('quantity', 0),
                protein=nutrients.get('PROCNT', {}).get('quantity', 0),
                carbs=nutrients.get('CHOCDF', {}).get('quantity', 0),
                fat=nutrients.get('FAT', {}).get('quantity', 0),
                ingredients=[ing.get('text', '') for ing in recipe.get('ingredientLines', [])],
                instructions='',
                image_url=recipe.get('image', ''),
                prep_time=0,
                cook_time=int(recipe.get('totalTime', 0)),
                servings=recipe.get('yield', 1),
                source='Edamam'
            ))
        
        return recipes
    
    def analyze_image(self, image_path: str) -> Optional[Dict]:
        """Анализ изображения еды (требует отдельного API)"""
        # Заглушка для будущего расширения
        # Можно интегрировать с Clarifai, Google Vision, или локальной ML моделью
        print(f"Image analysis not yet implemented for: {image_path}")
        return None


# Глобальный экземпляр
_nutrition_api: Optional[NutritionAPI] = None

def get_nutrition_api(api_keys: Dict[str, str] = None) -> NutritionAPI:
    """Получение экземпляра API клиента"""
    global _nutrition_api
    if _nutrition_api is None:
        _nutrition_api = NutritionAPI(api_keys)
    return _nutrition_api
