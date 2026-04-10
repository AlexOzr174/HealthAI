"""
Special Diets - Кето, Палео, Интервальное голодание
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta


class SpecialDiets:
    """Менеджер специальных диет"""
    
    def __init__(self):
        self.diet_types = {
            'keto': self._get_keto_config(),
            'paleo': self._get_paleo_config(),
            'intermittent_fasting': self._get_if_config()
        }
    
    def _get_keto_config(self) -> Dict:
        """Конфигурация кето диеты"""
        return {
            'name': 'Кето диета',
            'description': 'Высокожировая, низкоуглеводная диета для входа в кетоз',
            'macros': {
                'carbs_percent': 5,      # 5-10%
                'protein_percent': 20,   # 20-25%
                'fat_percent': 75        # 70-75%
            },
            'daily_carb_limit_g': 20,    # грамм углеводов в день
            'allowed_foods': [
                'мясо', 'рыба', 'яйца', 'масло', 'сливки', 'сыр',
                'авокадо', 'орехи', 'оливковое масло', 'кокосовое масло',
                'зелень', 'шпинат', 'брокколи', 'цветная капуста'
            ],
            'forbidden_foods': [
                'сахар', 'хлеб', 'паста', 'рис', 'картофель', 'фрукты',
                'зерновые', 'бобовые', 'сладости', 'газировка'
            ],
            'tips': [
                'Пейте достаточно воды (2-3 литра в день)',
                'Увеличьте потребление соли для предотвращения "кето гриппа"',
                'Избегайте скрытых углеводов в продуктах',
                'Первые дни возможны головная боль и усталость'
            ]
        }
    
    def _get_paleo_config(self) -> Dict:
        """Конфигурация палео диеты"""
        return {
            'name': 'Палео диета',
            'description': 'Диета каменного века - только натуральные продукты',
            'macros': {
                'carbs_percent': 30,
                'protein_percent': 30,
                'fat_percent': 40
            },
            'allowed_foods': [
                'мясо', 'рыба', 'яйца', 'овощи', 'фрукты', 'орехи',
                'семена', 'мёд', 'оливковое масло', 'кокосовое масло'
            ],
            'forbidden_foods': [
                'зерновые', 'бобовые', 'молочные продукты', 'сахар',
                'обработанные продукты', 'рафинированные масла', 'соль'
            ],
            'tips': [
                'Ешьте мясо травяного откорма',
                'Выбирайте органические овощи и фрукты',
                'Избегайте обработанных продуктов',
                'Фокусируйтесь на цельных продуктах'
            ]
        }
    
    def _get_if_config(self) -> Dict:
        """Конфигурация интервального голодания"""
        return {
            'name': 'Интервальное голодание',
            'description': 'Чередование периодов питания и голодания',
            'schemes': {
                '16_8': {
                    'name': '16/8',
                    'fasting_hours': 16,
                    'eating_window_hours': 8,
                    'description': '16 часов голода, 8 часов окно питания'
                },
                '18_6': {
                    'name': '18/6',
                    'fasting_hours': 18,
                    'eating_window_hours': 6,
                    'description': '18 часов голода, 6 часов окно питания'
                },
                '20_4': {
                    'name': '20/4',
                    'fasting_hours': 20,
                    'eating_window_hours': 4,
                    'description': '20 часов голода, 4 часа окно питания (Warrior Diet)'
                },
                '5_2': {
                    'name': '5:2',
                    'fasting_days': 2,
                    'normal_days': 5,
                    'description': '5 дней нормальное питание, 2 дня ограничение калорий (500-600)'
                }
            },
            'tips': [
                'Начинайте с схемы 16/8',
                'Пейте воду, чай или чёрный кофе во время голодания',
                'Избегайте интенсивных тренировок в период голодания',
                'Слушайте своё тело и при необходимости прекратите'
            ],
            'benefits': [
                'Улучшение чувствительности к инсулину',
                'Снижение веса',
                'Улучшение когнитивных функций',
                'Аутофагия (очищение клеток)'
            ]
        }
    
    def get_diet_info(self, diet_type: str) -> Optional[Dict]:
        """Получение информации о диете"""
        return self.diet_types.get(diet_type)
    
    def check_food_compatibility(self, diet_type: str, food_name: str) -> Dict:
        """
        Проверка совместимости продукта с диетой
        
        Args:
            diet_type: Тип диеты (keto, paleo)
            food_name: Название продукта
        
        Returns:
            Словарь с результатом проверки
        """
        diet_config = self.diet_types.get(diet_type)
        if not diet_config:
            return {'compatible': False, 'reason': 'Неизвестная диета'}
        
        food_lower = food_name.lower()
        
        # Проверка запрещённых продуктов
        for forbidden in diet_config.get('forbidden_foods', []):
            if forbidden.lower() in food_lower:
                return {
                    'compatible': False,
                    'reason': f'Продукт содержит запрещённый ингредиент: {forbidden}',
                    'alternatives': self._get_alternatives(diet_type, food_name)
                }
        
        # Проверка разрешённых продуктов
        for allowed in diet_config.get('allowed_foods', []):
            if allowed.lower() in food_lower:
                return {
                    'compatible': True,
                    'reason': f'Продукт соответствует диете: {allowed}',
                    'macros_hint': diet_config.get('macros', {})
                }
        
        # Если не найдено точных совпадений
        return {
            'compatible': None,
            'reason': 'Требуется ручная проверка нутриентов',
            'macros_target': diet_config.get('macros', {})
        }
    
    def _get_alternatives(self, diet_type: str, food_name: str) -> List[str]:
        """Получение альтернатив продукту"""
        alternatives_map = {
            'keto': {
                'хлеб': ['миндальная мука', 'кокосовая мука', 'льняная мука'],
                'рис': ['цветная капуста рис', 'конжак рис'],
                'паста': ['кабачковые спагетти', 'ширатаки лапша'],
                'картофель': ['репа', 'сельдерей корневой'],
                'сахар': ['стевия', 'эритрит', 'ксилит']
            },
            'paleo': {
                'хлеб': ['миндальный хлеб', 'батат'],
                'молоко': ['миндальное молоко', 'кокосовое молоко'],
                'сахар': ['мёд', 'кокосовый сахар', 'финики'],
                'рис': ['цветная капуста рис', 'брокколи рис']
            }
        }
        
        diet_alternatives = alternatives_map.get(diet_type, {})
        
        for key, values in diet_alternatives.items():
            if key in food_name.lower():
                return values
        
        return ['Посмотрите разрешённые продукты для этой диеты']
    
    def calculate_keto_macros(self, daily_calories: int) -> Dict:
        """
        Расчёт макронутриентов для кето диеты
        
        Args:
            daily_calories: Дневная норма калорий
        
        Returns:
            Словарь с граммами БЖУ
        """
        config = self._get_keto_config()
        macros = config['macros']
        
        fat_g = (daily_calories * macros['fat_percent'] / 100) / 9
        protein_g = (daily_calories * macros['protein_percent'] / 100) / 4
        carbs_g = (daily_calories * macros['carbs_percent'] / 100) / 4
        
        # Ограничение углеводов
        carbs_g = min(carbs_g, config['daily_carb_limit_g'])
        
        return {
            'calories': daily_calories,
            'fat_g': round(fat_g, 1),
            'protein_g': round(protein_g, 1),
            'carbs_g': round(carbs_g, 1),
            'net_carbs_g': round(carbs_g * 0.8, 1)  # Чистые углеводы
        }
    
    def calculate_paleo_macros(self, daily_calories: int) -> Dict:
        """
        Расчёт макронутриентов для палео диеты
        
        Args:
            daily_calories: Дневная норма калорий
        
        Returns:
            Словарь с граммами БЖУ
        """
        config = self._get_paleo_config()
        macros = config['macros']
        
        fat_g = (daily_calories * macros['fat_percent'] / 100) / 9
        protein_g = (daily_calories * macros['protein_percent'] / 100) / 4
        carbs_g = (daily_calories * macros['carbs_percent'] / 100) / 4
        
        return {
            'calories': daily_calories,
            'fat_g': round(fat_g, 1),
            'protein_g': round(protein_g, 1),
            'carbs_g': round(carbs_g, 1),
            'fiber_g': round(carbs_g * 0.15, 1)  # Примерное содержание клетчатки
        }
    
    def get_fasting_schedule(self, scheme: str = '16_8', wake_time: str = '07:00') -> Dict:
        """
        Получение расписания интервального голодания
        
        Args:
            scheme: Схема голодания (16_8, 18_6, 20_4)
            wake_time: Время подъёма
        
        Returns:
            Расписание приёма пищи
        """
        if_config = self._get_if_config()
        scheme_config = if_config['schemes'].get(scheme)
        
        if not scheme_config:
            return {'error': 'Неверная схема'}
        
        # Парсинг времени подъёма
        wake_hour, wake_minute = map(int, wake_time.split(':'))
        wake_dt = datetime.now().replace(hour=wake_hour, minute=wake_minute)
        
        fasting_hours = scheme_config.get('fasting_hours', 16)
        eating_window = scheme_config.get('eating_window_hours', 8)
        
        # Расчёт окна питания
        eating_start = wake_dt + timedelta(hours=4)  # Начинаем есть через 4 часа после подъёма
        eating_end = eating_start + timedelta(hours=eating_window)
        
        return {
            'scheme': scheme_config['name'],
            'description': scheme_config['description'],
            'fasting_start': eating_end.strftime('%H:%M'),
            'fasting_end': eating_start.strftime('%H:%M'),
            'eating_window_start': eating_start.strftime('%H:%M'),
            'eating_window_end': eating_end.strftime('%H:%M'),
            'next_meal_allowed': eating_start.strftime('%H:%M'),
            'last_meal_by': eating_end.strftime('%H:%M')
        }
    
    def get_all_diets(self) -> List[Dict]:
        """Получение списка всех доступных диет"""
        return [
            {
                'type': 'keto',
                'name': self._get_keto_config()['name'],
                'description': self._get_keto_config()['description']
            },
            {
                'type': 'paleo',
                'name': self._get_paleo_config()['name'],
                'description': self._get_paleo_config()['description']
            },
            {
                'type': 'intermittent_fasting',
                'name': self._get_if_config()['name'],
                'description': self._get_if_config()['description']
            }
        ]
    
    def generate_meal_plan(self, diet_type: str, days: int = 7) -> List[Dict]:
        """
        Генерация примерного плана питания
        
        Args:
            diet_type: Тип диеты
            days: Количество дней
        
        Returns:
            Список планов питания по дням
        """
        # Заглушка для генерации плана
        # В реальной версии здесь была бы интеграция с рецептами
        return [
            {
                'day': i + 1,
                'diet': diet_type,
                'meals': [],
                'total_calories': 0,
                'note': 'План генерируется на основе разрешённых продуктов'
            }
            for i in range(days)
        ]
