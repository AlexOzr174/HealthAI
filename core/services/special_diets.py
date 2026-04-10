"""
Сервис специальных диет для HealthAI
Поддержка: Кето, Палео, Интервальное голодание, Веганство, Вегетарианство
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class DietType(Enum):
    """Типы диет"""
    KETO = "keto"
    PALEO = "paleo"
    INTERMITTENT_FASTING = "intermittent_fasting"
    VEGAN = "vegan"
    VEGETARIAN = "vegetarian"
    GLUTEN_FREE = "gluten_free"
    LOW_CARB = "low_carb"
    MEDITERRANEAN = "mediterranean"


@dataclass
class MacroTargets:
    """Целевые макронутриенты"""
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float = 25
    sugar_g: float = 50


@dataclass
class DietProfile:
    """Профиль диеты пользователя"""
    diet_type: DietType
    daily_calories: int
    macros: MacroTargets
    restrictions: List[str]
    fasting_window: Tuple[int, int] = (8, 16)  # eating, fasting hours
    allowed_foods: List[str] = None
    forbidden_foods: List[str] = None


class SpecialDietsService:
    """Сервис управления специальными диетами"""
    
    # Запрещённые продукты для каждой диеты
    FORBIDDEN_FOODS = {
        DietType.KETO: [
            'sugar', 'bread', 'pasta', 'rice', 'potato', 'banana', 
            'grapes', 'mango', 'juice', 'soda', 'candy', 'cake',
            'beer', 'sweet wine', 'corn', 'beans', 'lentils'
        ],
        DietType.PALEO: [
            'bread', 'pasta', 'rice', 'cereals', 'legumes', 'beans',
            'lentils', 'peanuts', 'soy', 'tofu', 'milk', 'cheese',
            'yogurt', 'sugar', 'processed food', 'salt', 'potato'
        ],
        DietType.VEGAN: [
            'meat', 'beef', 'pork', 'chicken', 'fish', 'seafood',
            'egg', 'milk', 'cheese', 'yogurt', 'butter', 'honey',
            'gelatin', 'whey', 'casein'
        ],
        DietType.VEGETARIAN: [
            'beef', 'pork', 'chicken', 'fish', 'seafood', 'bacon',
            'ham', 'sausage', 'gelatin'
        ],
        DietType.GLUTEN_FREE: [
            'wheat', 'barley', 'rye', 'bread', 'pasta', 'cereals',
            'beer', 'soy sauce', 'malt', 'brewer yeast'
        ]
    }
    
    # Разрешённые продукты для каждой диеты
    ALLOWED_FOODS = {
        DietType.KETO: [
            'avocado', 'olive oil', 'coconut oil', 'butter', 'cream',
            'cheese', 'eggs', 'bacon', 'salmon', 'tuna', 'chicken',
            'beef', 'pork', 'spinach', 'kale', 'broccoli', 'cauliflower',
            'zucchini', 'asparagus', 'lettuce', 'cucumber', 'celery',
            'almonds', 'walnuts', 'macadamia', 'chia seeds', 'flax seeds'
        ],
        DietType.PALEO: [
            'meat', 'beef', 'pork', 'chicken', 'turkey', 'lamb',
            'fish', 'salmon', 'tuna', 'shrimp', 'eggs',
            'vegetables', 'fruits', 'nuts', 'seeds',
            'olive oil', 'coconut oil', 'avocado oil',
            'sweet potato', 'carrots', 'berries', 'apples'
        ],
        DietType.VEGAN: [
            'tofu', 'tempeh', 'seitan', 'legumes', 'beans', 'lentils',
            'chickpeas', 'quinoa', 'rice', 'oats', 'nuts', 'seeds',
            'vegetables', 'fruits', 'plant milk', 'nutritional yeast'
        ],
        DietType.VEGETARIAN: [
            'eggs', 'milk', 'cheese', 'yogurt', 'tofu', 'tempeh',
            'legumes', 'beans', 'lentils', 'quinoa', 'rice', 'oats',
            'nuts', 'seeds', 'vegetables', 'fruits'
        ]
    }
    
    # Рекомендуемые макросы для каждой диеты (% от калорий)
    MACRO_RATIOS = {
        DietType.KETO: {'protein': 20, 'carbs': 5, 'fat': 75},
        DietType.PALEO: {'protein': 30, 'carbs': 40, 'fat': 30},
        DietType.VEGAN: {'protein': 15, 'carbs': 55, 'fat': 30},
        DietType.VEGETARIAN: {'protein': 20, 'carbs': 50, 'fat': 30},
        DietType.GLUTEN_FREE: {'protein': 20, 'carbs': 50, 'fat': 30},
        DietType.LOW_CARB: {'protein': 30, 'carbs': 20, 'fat': 50},
        DietType.MEDITERRANEAN: {'protein': 20, 'carbs': 45, 'fat': 35}
    }
    
    def __init__(self):
        self.active_diets: Dict[int, DietProfile] = {}
    
    def create_diet_profile(self, user_id: int, diet_type: DietType,
                            daily_calories: int, 
                            restrictions: List[str] = None) -> DietProfile:
        """Создание профиля диеты для пользователя"""
        
        # Расчёт макросов на основе типа диеты
        ratios = self.MACRO_RATIOS.get(diet_type, {'protein': 20, 'carbs': 50, 'fat': 30})
        
        # 1г белка = 4 ккал, 1г углеводов = 4 ккал, 1г жира = 9 ккал
        protein_g = (daily_calories * ratios['protein'] / 100) / 4
        carbs_g = (daily_calories * ratios['carbs'] / 100) / 4
        fat_g = (daily_calories * ratios['fat'] / 100) / 9
        
        macros = MacroTargets(
            calories=daily_calories,
            protein_g=round(protein_g, 1),
            carbs_g=round(carbs_g, 1),
            fat_g=round(fat_g, 1)
        )
        
        # Получение списков продуктов
        allowed = self.ALLOWED_FOODS.get(diet_type, [])
        forbidden = self.FORBIDDEN_FOODS.get(diet_type, [])
        
        profile = DietProfile(
            diet_type=diet_type,
            daily_calories=daily_calories,
            macros=macros,
            restrictions=restrictions or [],
            allowed_foods=allowed,
            forbidden_foods=forbidden
        )
        
        self.active_diets[user_id] = profile
        return profile
    
    def get_diet_profile(self, user_id: int) -> Optional[DietProfile]:
        """Получение профиля диеты пользователя"""
        return self.active_diets.get(user_id)
    
    def is_food_allowed(self, user_id: int, food_name: str) -> Tuple[bool, str]:
        """Проверка совместимости продукта с диетой"""
        profile = self.active_diets.get(user_id)
        
        if not profile:
            return True, "Диета не активна"
        
        food_lower = food_name.lower()
        
        # Проверка запрещённых продуктов
        for forbidden in profile.forbidden_foods:
            if forbidden in food_lower:
                return False, f"Продукт не совместим с диетой {profile.diet_type.value}"
        
        # Проверка персональных ограничений
        for restriction in profile.restrictions:
            if restriction.lower() in food_lower:
                return False, f"Продукт не совместим с ограничением: {restriction}"
        
        return True, "Продукт разрешён"
    
    def suggest_substitutes(self, user_id: int, food_name: str) -> List[str]:
        """Предложение замены неподходящего продукта"""
        profile = self.active_diets.get(user_id)
        
        if not profile:
            return []
        
        substitutes = {
            'bread': ['keto bread', 'lettuce wrap', 'cloud bread'],
            'pasta': ['zucchini noodles', 'shirataki noodles', 'spaghetti squash'],
            'rice': ['cauliflower rice', 'quinoa', 'broccoli rice'],
            'potato': ['cauliflower', 'turnip', 'radish'],
            'sugar': ['stevia', 'erythritol', 'monk fruit'],
            'milk': ['almond milk', 'coconut milk', 'oat milk'],
            'cheese': ['nutritional yeast', 'cashew cheese', 'tofu'],
            'meat': ['tofu', 'tempeh', 'seitan', 'jackfruit'],
            'fish': ['tofu', 'tempeh', 'algae'],
            'egg': ['tofu scramble', 'chia egg', 'flax egg'],
            'bread wheat': ['rice bread', 'corn tortilla', 'lettuce wrap']
        }
        
        food_lower = food_name.lower()
        
        for key, subs in substitutes.items():
            if key in food_lower:
                # Фильтрация замен по диете
                if profile.diet_type == DietType.KETO:
                    subs = [s for s in subs if 'rice' not in s and 'corn' not in s and 'oat' not in s]
                elif profile.diet_type == DietType.PALEO:
                    subs = [s for s in subs if 'tofu' not in s and 'seitan' not in s and 'oat' not in s]
                elif profile.diet_type == DietType.VEGAN:
                    subs = [s for s in subs if 'cheese' not in s and 'egg' not in s]
                
                return subs[:3]
        
        return []
    
    def is_fasting_time(self, user_id: int, current_hour: int) -> bool:
        """Проверка, является ли текущее время временем голодания"""
        profile = self.active_diets.get(user_id)
        
        if not profile or profile.diet_type != DietType.INTERMITTENT_FASTING:
            return False
        
        eating_start = 12  # Полдень по умолчанию
        eating_end = eating_start + profile.fasting_window[0]
        
        return current_hour < eating_start or current_hour >= eating_end
    
    def get_eating_window(self, user_id: int) -> Optional[Tuple[int, int]]:
        """Получение окна приёма пищи"""
        profile = self.active_diets.get(user_id)
        
        if not profile or profile.diet_type != DietType.INTERMITTENT_FASTING:
            return None
        
        eating_start = 12
        eating_end = eating_start + profile.fasting_window[0]
        
        return (eating_start, eating_end)
    
    def calculate_meal_macros(self, user_id: int, meal_type: str) -> MacroTargets:
        """Расчёт макросов для конкретного приёма пищи"""
        profile = self.active_diets.get(user_id)
        
        if not profile:
            return None
        
        # Распределение калорий по приёмам пищи
        meal_ratios = {
            'breakfast': 0.25,
            'lunch': 0.35,
            'dinner': 0.30,
            'snack': 0.10
        }
        
        ratio = meal_ratios.get(meal_type, 0.25)
        macros = profile.macros
        
        return MacroTargets(
            calories=int(macros.calories * ratio),
            protein_g=round(macros.protein_g * ratio, 1),
            carbs_g=round(macros.carbs_g * ratio, 1),
            fat_g=round(macros.fat_g * ratio, 1)
        )
    
    def get_diet_info(self, diet_type: DietType) -> Dict:
        """Получение информации о диете"""
        diet_info = {
            DietType.KETO: {
                'name': 'Кетогенная диета',
                'description': 'Высокожировая диета с минимальным количеством углеводов',
                'benefits': ['Похудение', 'Улучшение ментальной фокусировки', 'Стабильная энергия'],
                'tips': ['Пейте больше воды', 'Следите за электролитами', 'Избегайте скрытых углеводов']
            },
            DietType.PALEO: {
                'name': 'Палео диета',
                'description': 'Питание как у древних людей: мясо, рыба, овощи, фрукты',
                'benefits': ['Улучшение пищеварения', 'Снижение воспаления', 'Натуральные продукты'],
                'tips': ['Выбирайте органическое мясо', 'Ешьте разнообразные овощи', 'Избегайте обработанных продуктов']
            },
            DietType.INTERMITTENT_FASTING: {
                'name': 'Интервальное голодание',
                'description': 'Чередование периодов еды и голодания',
                'benefits': ['Аутофагия', 'Улучшение метаболизма', 'Простота'],
                'tips': ['Начинайте с 12/12', 'Пейте воду во время голодания', 'Не переедайте в окно питания']
            },
            DietType.VEGAN: {
                'name': 'Веганство',
                'description': 'Полный отказ от продуктов животного происхождения',
                'benefits': ['Этичность', 'Экологичность', 'Снижение рисков заболеваний'],
                'tips': ['Следите за B12', 'Комбинируйте белки', 'Ешьте разнообразные продукты']
            },
            DietType.VEGETARIAN: {
                'name': 'Вегетарианство',
                'description': 'Отказ от мяса с возможностью употребления молочных продуктов и яиц',
                'benefits': ['Здоровье сердца', 'Снижение веса', 'Этичность'],
                'tips': ['Следите за железом', 'Ешьте достаточно белка', 'Разнообразьте рацион']
            }
        }
        
        return diet_info.get(diet_type, {})
    
    def generate_meal_plan(self, user_id: int, days: int = 7) -> List[Dict]:
        """Генерация плана питания на несколько дней"""
        profile = self.active_diets.get(user_id)
        
        if not profile:
            return []
        
        # Упрощённая генерация (в реальности нужна интеграция с рецептами)
        meal_plan = []
        
        for day in range(days):
            day_plan = {
                'day': day + 1,
                'breakfast': self._suggest_meal(profile, 'breakfast'),
                'lunch': self._suggest_meal(profile, 'lunch'),
                'dinner': self._suggest_meal(profile, 'dinner'),
                'snack': self._suggest_meal(profile, 'snack')
            }
            meal_plan.append(day_plan)
        
        return meal_plan
    
    def _suggest_meal(self, profile: DietProfile, meal_type: str) -> str:
        """Предложение блюда для приёма пищи"""
        # Заглушка - в реальности нужно подбирать из базы рецептов
        suggestions = {
            DietType.KETO: {
                'breakfast': 'Омлет с авокадо и беконом',
                'lunch': 'Салат с курицей и оливковым маслом',
                'dinner': 'Лосось со спаржей',
                'snack': 'Горсть орехов'
            },
            DietType.PALEO: {
                'breakfast': 'Яйца с овощами',
                'lunch': 'Стейк с салатом',
                'dinner': 'Курица с бататом',
                'snack': 'Фрукты и орехи'
            },
            DietType.VEGAN: {
                'breakfast': 'Овсянка с растительным молоком',
                'lunch': 'Боул с киноа и овощами',
                'dinner': 'Тофу с брокколи',
                'snack': 'Хумус с овощами'
            }
        }
        
        diet_suggestions = suggestions.get(profile.diet_type, {})
        return diet_suggestions.get(meal_type, 'Сбалансированное блюдо')


# Глобальный экземпляр
_special_diets_service: Optional[SpecialDietsService] = None

def get_special_diets_service() -> SpecialDietsService:
    """Получение экземпляра сервиса специальных диет"""
    global _special_diets_service
    if _special_diets_service is None:
        _special_diets_service = SpecialDietsService()
    return _special_diets_service
