"""
AI Recipe Generator - Генератор рецептов на основе ИИ
Создаёт персонализированные рецепты с учётом предпочтений, ограничений и доступных продуктов
"""

import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict


class RecipeGenerator:
    """
    Генератор рецептов с использованием правил и шаблонов
    Создаёт уникальные комбинации блюд на основе:
    - Предпочтений пользователя
    - Доступных продуктов
    - Диетических ограничений
    - Времени приготовления
    - Калорийности
    """
    
    def __init__(self):
        # Шаблоны рецептов по категориям
        self.recipe_templates = self._load_recipe_templates()
        
        # Кулинарные техники
        self.cooking_methods = {
            'breakfast': ['варка', 'жарка', 'запекание', 'приготовление на пару'],
            'lunch': ['запекание', 'тушение', 'жарка', 'гриль', 'варка'],
            'dinner': ['запекание', 'приготовление на пару', 'гриль', 'тушение'],
            'snack': ['без приготовления', 'смешивание', 'нарезка']
        }
        
        # Сезонные продукты
        self.seasonal_products = {
            'spring': ['спаржа', 'зелень', 'редис', 'клубника', 'ревень'],
            'summer': ['помидоры', 'огурцы', 'баклажаны', 'кабачки', 'ягоды', 'персики'],
            'autumn': ['тыква', 'яблоки', 'грибы', 'цветная капуста', 'брюссельская капуста'],
            'winter': ['корнеплоды', 'капуста', 'цитрусовые', 'замороженные ягоды']
        }
        
        # Мировые кухни
        self.cuisine_styles = {
            'european': ['оливковое масло', 'чеснок', 'базилик', 'орегано', 'пармезан'],
            'asian': ['соевый соус', 'имбирь', 'кунжут', 'рисовый уксус', 'чили'],
            'mediterranean': ['оливки', 'фета', 'лимон', 'мята', 'нут'],
            'russian': ['сметана', 'укроп', 'гречка', 'свёкла', 'капуста'],
            'american': ['бекон', 'сыр чеддер', 'кукуруза', 'фасоль', 'барбекю соус']
        }
    
    def _load_recipe_templates(self) -> Dict:
        """Загрузка шаблонов рецептов"""
        return {
            'breakfast': {
                'base_ingredients': [
                    ['яйца', 'омлет', 'скрэмбл'],
                    ['овсянка', 'гранола', 'мюсли'],
                    ['творог', 'греческий йогурт'],
                    ['блины', 'оладьи', 'панкейки']
                ],
                'proteins': ['ветчина', 'лосось', 'индейка', 'тофу', 'бобы'],
                'vegetables': ['шпинат', 'помидоры', 'авокадо', 'перец', 'грибы'],
                'toppings': ['орехи', 'семена', 'ягоды', 'фрукты', 'мёд']
            },
            'lunch': {
                'base_ingredients': [
                    ['куриная грудка', 'индейка', 'утка'],
                    ['говядина', 'телятина', 'свинина'],
                    ['лосось', 'тунец', 'треска', 'креветки'],
                    ['тофу', 'темпе', 'сейтан']
                ],
                'carbs': ['рис', 'гречка', 'киноа', 'булгур', 'паста', 'картофель'],
                'vegetables': ['брокколи', 'цветная капуста', 'стручковая фасоль', 'кабачки', 'баклажаны'],
                'sauces': ['томатный', 'сливочный', 'соевый', 'песто', 'терияки']
            },
            'dinner': {
                'base_ingredients': [
                    ['рыба', 'морепродукты'],
                    ['курица', 'индейка'],
                    ['овощи', 'тофу']
                ],
                'light_carbs': ['киноа', 'булгур', 'овощи гриль', 'салат'],
                'vegetables': ['спаржа', 'брокколи', 'цинни', 'перец', 'листовая зелень'],
                'flavorings': ['лимон', 'трава', 'специи', 'оливковое масло']
            },
            'snack': {
                'base_ingredients': [
                    ['орехи', 'смесь орехов'],
                    ['фрукты', 'сухофрукты'],
                    ['йогурт', 'творог'],
                    ['хумус', 'гуакамоле']
                ],
                'additions': ['крекеры', 'овощные палочки', 'лаваш', 'рисовые хлебцы'],
                'extras': ['мёд', 'корица', 'какао', 'кокос']
            }
        }
    
    def generate_recipe(self, 
                       category: str = 'lunch',
                       preferences: Optional[Dict] = None,
                       restrictions: Optional[List[str]] = None,
                       available_products: Optional[List[str]] = None,
                       cooking_time: int = 30,
                       difficulty: str = 'medium') -> Dict:
        """
        Генерация рецепта
        
        Args:
            category: Категория блюда (breakfast, lunch, dinner, snack)
            preferences: Предпочтения пользователя
            restrictions: Ограничения (аллергии, диеты)
            available_products: Доступные продукты
            cooking_time: Максимальное время приготовления (мин)
            difficulty: Сложность (easy, medium, hard)
        
        Returns:
            Dict с рецептом
        """
        if preferences is None:
            preferences = {}
        if restrictions is None:
            restrictions = []
        if available_products is None:
            available_products = []
        
        # Выбор базового ингредиента
        templates = self.recipe_templates.get(category, self.recipe_templates['lunch'])
        base = random.choice(templates['base_ingredients'])
        base_name = random.choice(base) if isinstance(base, list) else base
        
        # Выбор дополнительных ингредиентов
        if category == 'breakfast':
            protein = random.choice(templates.get('proteins', []))
            veggies = random.sample(templates.get('vegetables', []), min(2, len(templates.get('vegetables', []))))
            topping = random.choice(templates.get('toppings', []))
            
            ingredients = [base_name, protein] + veggies + [topping]
        elif category == 'lunch':
            carb = random.choice(templates.get('carbs', []))
            veggies = random.sample(templates.get('vegetables', []), min(3, len(templates.get('vegetables', []))))
            sauce = random.choice(templates.get('sauces', []))
            
            ingredients = [base_name, carb] + veggies + [sauce]
        elif category == 'dinner':
            light_carb = random.choice(templates.get('light_carbs', []))
            veggies = random.sample(templates.get('vegetables', []), min(3, len(templates.get('vegetables', []))))
            flavor = random.choice(templates.get('flavorings', []))
            
            ingredients = [base_name, light_carb] + veggies + [flavor]
        else:  # snack
            addition = random.choice(templates.get('additions', []))
            extra = random.choice(templates.get('extras', []))
            
            ingredients = [base_name, addition, extra]
        
        # Фильтрация по ограничениям
        filtered_ingredients = self._filter_by_restrictions(ingredients, restrictions)
        
        # Приоритизация доступных продуктов
        if available_products:
            filtered_ingredients = self._prioritize_available(filtered_ingredients, available_products)
        
        # Генерация названия
        recipe_name = self._generate_recipe_name(category, filtered_ingredients, preferences)
        
        # Расчёт питательной ценности (примерный)
        nutrition = self._calculate_nutrition(filtered_ingredients, category)
        
        # Генерация инструкций
        instructions = self._generate_instructions(category, filtered_ingredients, cooking_time, difficulty)
        
        # Метаданные
        prep_time = random.randint(10, 20)
        cook_time = max(cooking_time - prep_time, 5)
        
        return {
            'name': recipe_name,
            'category': category,
            'ingredients': filtered_ingredients,
            'instructions': instructions,
            'nutrition': nutrition,
            'time': {
                'prep': prep_time,
                'cook': cook_time,
                'total': prep_time + cook_time
            },
            'difficulty': difficulty,
            'servings': random.randint(1, 4),
            'cuisine_style': self._detect_cuisine_style(filtered_ingredients),
            'tags': self._generate_tags(filtered_ingredients, category, restrictions),
            'generated_at': datetime.now().isoformat()
        }
    
    def _filter_by_restrictions(self, ingredients: List[str], restrictions: List[str]) -> List[str]:
        """Фильтрация ингредиентов по ограничениям"""
        if not restrictions:
            return ingredients
        
        vegetarian_forbidden = ['курица', 'говядина', 'свинина', 'рыба', 'лосось', 'тунец', 'индейка', 'бекон', 'ветчина']
        restriction_map = {
            'vegetarian': vegetarian_forbidden,
            'vegan': ['яйца', 'творог', 'йогурт', 'сыр', 'мёд'] + vegetarian_forbidden,
            'gluten_free': ['паста', 'булгур', 'ячмень', 'овёс'],
            'dairy_free': ['творог', 'йогурт', 'сыр', 'пармезан', 'фета', 'сметана'],
            'low_carb': ['рис', 'паста', 'картофель', 'булгур', 'мёд', 'фрукты']
        }
        
        forbidden = []
        for restriction in restrictions:
            if restriction in restriction_map:
                forbidden.extend(restriction_map[restriction])
        
        return [ing for ing in ingredients if ing.lower() not in [f.lower() for f in forbidden]]
    
    def _prioritize_available(self, ingredients: List[str], available: List[str]) -> List[str]:
        """Приоритизация доступных продуктов"""
        available_lower = [a.lower() for a in available]
        
        # Если есть совпадения, используем их
        prioritized = []
        for ing in ingredients:
            if any(a in ing.lower() or ing.lower() in a for a in available_lower):
                prioritized.append(ing)
        
        # Добавляем остальные
        for ing in ingredients:
            if ing not in prioritized:
                prioritized.append(ing)
        
        return prioritized
    
    def _generate_recipe_name(self, category: str, ingredients: List[str], 
                              preferences: Dict) -> str:
        """Генерация названия рецепта"""
        adjectives = {
            'breakfast': ['Нежный', 'Бодрящий', 'Сытный', 'Лёгкий', 'Ароматный'],
            'lunch': ['Сочный', 'Насыщенный', 'Пикантный', 'Традиционный', 'Фирменный'],
            'dinner': ['Лёгкий', 'Изысканный', 'Утончённый', 'Полезный', 'Вечерний'],
            'snack': ['Хрустящий', 'Быстрый', 'Энергетический', 'Вкусный', 'Полезный']
        }
        
        main_ingredient = ingredients[0] if ingredients else 'Блюдо'
        adjective = random.choice(adjectives.get(category, adjectives['lunch']))
        
        # Стиль названия
        styles = [
            f"{adjective} {main_ingredient}",
            f"{main_ingredient} по-домашнему",
            f"{main_ingredient} с {ingredients[1] if len(ingredients) > 1 else 'овощами'}",
            f"Авторский {main_ingredient}"
        ]
        
        return random.choice(styles)
    
    def _calculate_nutrition(self, ingredients: List[str], category: str) -> Dict:
        """Примерный расчёт питательной ценности"""
        # Базовые значения на категорию
        base_nutrition = {
            'breakfast': {'calories': 350, 'protein': 20, 'carbs': 40, 'fat': 12},
            'lunch': {'calories': 550, 'protein': 35, 'carbs': 60, 'fat': 18},
            'dinner': {'calories': 400, 'protein': 30, 'carbs': 30, 'fat': 15},
            'snack': {'calories': 200, 'protein': 10, 'carbs': 20, 'fat': 8}
        }
        
        nutrition = base_nutrition.get(category, base_nutrition['lunch']).copy()
        
        # Корректировка по ингредиентам
        for ingredient in ingredients:
            ing_lower = ingredient.lower()
            if any(meat in ing_lower for meat in ['курица', 'говядина', 'рыба', 'лосось', 'индейка']):
                nutrition['protein'] += 10
                nutrition['calories'] += 50
            elif any(carb in ing_lower for carb in ['рис', 'паста', 'картофель', 'гречка']):
                nutrition['carbs'] += 20
                nutrition['calories'] += 80
            elif any(fat in ing_lower for fat in ['орехи', 'авокадо', 'оливковое', 'сыр']):
                nutrition['fat'] += 8
                nutrition['calories'] += 70
        
        nutrition['fiber'] = random.randint(5, 15)
        nutrition['sugar'] = random.randint(5, 20)
        
        return nutrition
    
    def _generate_instructions(self, category: str, ingredients: List[str], 
                               max_time: int, difficulty: str) -> List[str]:
        """Генерация инструкций по приготовлению"""
        instructions = []
        
        # Общие шаги
        instructions.append("1. Подготовьте все ингредиенты: вымойте, нарежьте, отмерьте.")
        
        if category in ['lunch', 'dinner']:
            instructions.append("2. Разогрейте духовку до 180°C или подготовьте плиту.")
            instructions.append(f"3. Приготовьте основной ингредиент ({ingredients[0]}) выбранным способом.")
        
        if len(ingredients) > 2:
            instructions.append(f"4. Подготовьте овощи и гарнир: {', '.join(ingredients[1:-1])}.")
        
        instructions.append(f"5. Соедините все компоненты и подавайте.")
        
        # Дополнительные шаги в зависимости от сложности
        if difficulty == 'hard':
            instructions.append("6. Украсьте блюдо свежей зеленью или специями для презентации.")
        
        return instructions
    
    def _detect_cuisine_style(self, ingredients: List[str]) -> str:
        """Определение стиля кухни по ингредиентам"""
        ingredients_str = ' '.join(ingredients).lower()
        
        if any(ing in ingredients_str for ing in ['соевый', 'имбирь', 'кунжут', 'рис']):
            return 'asian'
        elif any(ing in ingredients_str for ing in ['оливковый', 'базилик', 'пармезан', 'фета']):
            return 'mediterranean'
        elif any(ing in ingredients_str for ing in ['сметана', 'укроп', 'гречка']):
            return 'russian'
        elif any(ing in ingredients_str for ing in ['бекон', 'cheddar', 'барбекю']):
            return 'american'
        else:
            return 'european'
    
    def _generate_tags(self, ingredients: List[str], category: str, 
                       restrictions: List[str]) -> List[str]:
        """Генерация тегов для рецепта"""
        tags = [category]
        
        # Теги по ингредиентам
        if any('курица' in ing.lower() for ing in ingredients):
            tags.append('chicken')
        if any('рыба' in ing.lower() or 'лосось' in ing.lower() for ing in ingredients):
            tags.append('fish')
        if any(ing.lower() in ['тофу', 'темпе'] for ing in ingredients):
            tags.append('vegan')
        
        # Теги по времени
        tags.append('quick')
        
        # Теги по ограничениям
        if 'vegetarian' in restrictions:
            tags.append('vegetarian')
        if 'vegan' in restrictions:
            tags.append('vegan')
        if 'gluten_free' in restrictions:
            tags.append('gluten_free')
        
        return list(set(tags))
    
    def generate_weekly_plan(self, 
                            preferences: Dict,
                            restrictions: List[str],
                            days: int = 7) -> Dict:
        """
        Генерация плана питания на неделю
        
        Returns:
            Dict с планом на каждый день
        """
        weekly_plan = {}
        day_names = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
        
        for day_idx in range(min(days, 7)):
            day_name = day_names[day_idx]
            weekly_plan[day_name] = {
                'breakfast': self.generate_recipe('breakfast', preferences, restrictions),
                'lunch': self.generate_recipe('lunch', preferences, restrictions),
                'dinner': self.generate_recipe('dinner', preferences, restrictions),
                'snack': self.generate_recipe('snack', preferences, restrictions)
            }
        
        # Статистика за неделю
        total_calories = sum(
            meal['nutrition']['calories']
            for day_meals in weekly_plan.values()
            for meal in day_meals.values()
        )
        
        weekly_plan['_summary'] = {
            'avg_daily_calories': round(total_calories / days),
            'total_recipes': days * 4,
            'generated_at': datetime.now().isoformat()
        }
        
        return weekly_plan
    
    def suggest_substitutions(self, ingredient: str, restrictions: List[str] = None) -> List[str]:
        """Предложение замен для ингредиента"""
        substitutions_map = {
            'курица': ['индейка', 'тофу', 'рыба'],
            'говядина': ['телятина', 'свинина', 'сейтан'],
            'рыба': ['курица', 'тофу', 'креветки'],
            'яйца': ['тофу', 'льняное семя', 'банан'],
            'молоко': ['миндальное молоко', 'овсяное молоко', 'кокосовое молоко'],
            'сыр': ['тофу', 'пищевые дрожжи', 'веганский сыр'],
            'рис': ['киноа', 'булгур', 'гречка'],
            'паста': ['рисовая лапша', 'кабачковые нити', 'киноа']
        }
        
        all_subs = substitutions_map.get(ingredient.lower(), [])
        
        # Фильтрация по ограничениям
        if restrictions:
            if 'vegan' in restrictions or 'vegetarian' in restrictions:
                all_subs = [s for s in all_subs if s not in ['курица', 'говядина', 'рыба']]
        
        return all_subs[:3] if all_subs else ['нет подходящих замен']


# Экспорт класса
__all__ = ['RecipeGenerator']
