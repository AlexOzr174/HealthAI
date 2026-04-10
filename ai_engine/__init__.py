"""
AI Engine for HealthAI - Центральный модуль ИИ
Объединяет все ИИ-компоненты: чат-бот, аналитику, генератор рецептов
"""

from ai_engine.nutritionist_chatbot import NutritionistChatbot
from ai_engine.predictive_analytics import PredictiveAnalytics
from ai_engine.recipe_generator import RecipeGenerator
from typing import Dict, List, Optional


class AIEngine:
    """
    Единый интерфейс для всех ИИ-функций приложения HealthAI
    
    Компоненты:
    - NutritionistChatbot: Умный чат-бот нутрициолог
    - PredictiveAnalytics: Предиктивная аналитика и прогнозы
    - RecipeGenerator: Генератор персонализированных рецептов
    """
    
    def __init__(self):
        self.chatbot = NutritionistChatbot()
        self.analytics = PredictiveAnalytics()
        self.recipe_generator = RecipeGenerator()
        
        # Кэш пользовательских данных
        self.user_contexts = {}
    
    def initialize_user(self, user_id: int, profile: Dict) -> Dict:
        """
        Инициализация пользователя в ИИ-системе
        
        Args:
            user_id: ID пользователя
            profile: Профиль пользователя (вес, рост, возраст, цель и т.д.)
        
        Returns:
            Подтверждение инициализации
        """
        self.user_contexts[user_id] = {
            'profile': profile,
            'meal_history': [],
            'weight_history': [],
            'preferences': profile.get('preferences', {}),
            'restrictions': profile.get('restrictions', [])
        }
        
        # Установка профиля в чат-бот
        self.chatbot.set_user_profile(profile)
        
        return {
            'status': 'success',
            'message': f'Пользователь {user_id} успешно инициализирован в ИИ-системе',
            'components_ready': ['chatbot', 'analytics', 'recipe_generator']
        }
    
    def chat(self, user_id: int, message: str) -> Dict:
        """
        Отправка сообщения чат-боту нутрициологу
        
        Args:
            user_id: ID пользователя
            message: Текст сообщения
        
        Returns:
            Ответ чат-бота
        """
        context = self.user_contexts.get(user_id, {})
        meal_history = context.get('meal_history', [])
        
        response = self.chatbot.generate_response(message, meal_history)
        
        return response
    
    def get_weight_analysis(self, user_id: int, weight_history: List[Dict]) -> Dict:
        """
        Анализ тренда веса и прогноз
        
        Args:
            user_id: ID пользователя
            weight_history: История взвешиваний
        
        Returns:
            Аналитика веса с прогнозом
        """
        analysis = self.analytics.analyze_weight_trend(weight_history)
        
        if analysis.get('status') == 'success':
            # Добавляем инсайты
            insights = self.analytics.generate_insights(analysis)
            analysis['insights'] = insights
        
        return analysis
    
    def predict_goal_achievement(self, user_id: int, goal_weight: float, 
                                  daily_calorie_deficit: int) -> Dict:
        """
        Прогноз достижения цели по весу
        
        Args:
            user_id: ID пользователя
            goal_weight: Целевой вес
            daily_calorie_deficit: Ежедневный дефицит/профицит калорий
        
        Returns:
            Прогноз достижения цели
        """
        context = self.user_contexts.get(user_id, {})
        profile = context.get('profile', {})
        current_weight = profile.get('weight', 70)
        
        prediction = self.analytics.predict_goal_achievement(
            current_weight, goal_weight, daily_calorie_deficit
        )
        
        return prediction
    
    def optimize_nutrition(self, user_id: int, goal: Dict) -> Dict:
        """
        Оптимизация калорийности и БЖУ для цели
        
        Args:
            user_id: ID пользователя
            goal: Цель (target_weight, timeframe_weeks)
        
        Returns:
            Оптимальная калорийность и БЖУ
        """
        context = self.user_contexts.get(user_id, {})
        profile = context.get('profile', {})
        
        optimization = self.analytics.optimize_calories_for_goal(profile, goal)
        
        return optimization
    
    def detect_plateau(self, user_id: int, weight_history: List[Dict]) -> Dict:
        """
        Обнаружение плато в прогрессе
        
        Args:
            user_id: ID пользователя
            weight_history: История взвешиваний
        
        Returns:
            Информация о плато и рекомендации
        """
        plateau_info = self.analytics.detect_plateau(weight_history)
        
        return plateau_info
    
    def generate_recipe(self, user_id: int, category: str = 'lunch',
                        cooking_time: int = 30) -> Dict:
        """
        Генерация персонализированного рецепта
        
        Args:
            user_id: ID пользователя
            category: Категория блюда
            cooking_time: Время приготовления
        
        Returns:
            Рецепт
        """
        context = self.user_contexts.get(user_id, {})
        preferences = context.get('preferences', {})
        restrictions = context.get('restrictions', [])
        
        recipe = self.recipe_generator.generate_recipe(
            category=category,
            preferences=preferences,
            restrictions=restrictions,
            cooking_time=cooking_time
        )
        
        return recipe
    
    def generate_weekly_plan(self, user_id: int, days: int = 7) -> Dict:
        """
        Генерация плана питания на неделю
        
        Args:
            user_id: ID пользователя
            days: Количество дней
        
        Returns:
            План питания
        """
        context = self.user_contexts.get(user_id, {})
        preferences = context.get('preferences', {})
        restrictions = context.get('restrictions', [])
        
        weekly_plan = self.recipe_generator.generate_weekly_plan(
            preferences=preferences,
            restrictions=restrictions,
            days=days
        )
        
        return weekly_plan
    
    def suggest_substitutions(self, ingredient: str, user_id: Optional[int] = None) -> List[str]:
        """
        Предложение замен для ингредиента
        
        Args:
            ingredient: Исходный ингредиент
            user_id: ID пользователя (для учёта ограничений)
        
        Returns:
            Список замен
        """
        restrictions = []
        if user_id:
            context = self.user_contexts.get(user_id, {})
            restrictions = context.get('restrictions', [])
        
        substitutions = self.recipe_generator.suggest_substitutions(ingredient, restrictions)
        
        return substitutions
    
    def add_meal_to_history(self, user_id: int, meal_data: Dict):
        """Добавление приёма пищи в историю"""
        if user_id in self.user_contexts:
            self.user_contexts[user_id]['meal_history'].append(meal_data)
            
            # Ограничиваем историю последними 100 записями
            if len(self.user_contexts[user_id]['meal_history']) > 100:
                self.user_contexts[user_id]['meal_history'] = \
                    self.user_contexts[user_id]['meal_history'][-100:]
    
    def add_weight_measurement(self, user_id: int, weight: float, date: str):
        """Добавление замера веса"""
        if user_id in self.user_contexts:
            self.user_contexts[user_id]['weight_history'].append({
                'date': date,
                'weight': weight
            })
            
            # Сортировка по дате
            self.user_contexts[user_id]['weight_history'].sort(key=lambda x: x['date'])
    
    def get_ai_summary(self, user_id: int) -> Dict:
        """
        Получение сводки от ИИ-системы
        
        Returns:
            Общая сводка по всем компонентам
        """
        context = self.user_contexts.get(user_id, {})
        profile = context.get('profile', {})
        weight_history = context.get('weight_history', [])
        meal_history = context.get('meal_history', [])
        
        summary = {
            'user_status': 'initialized' if context else 'not_initialized',
            'profile': profile,
            'statistics': {
                'weight_measurements': len(weight_history),
                'meals_logged': len(meal_history),
                'conversation_messages': len(self.chatbot.conversation_history)
            }
        }
        
        # Если есть данные о весе, добавляем анализ
        if len(weight_history) >= 3:
            weight_analysis = self.analytics.analyze_weight_trend(weight_history)
            if weight_analysis.get('status') == 'success':
                summary['weight_trend'] = weight_analysis['trend']
        
        return summary
    
    def get_recommendations(self, user_id: int) -> List[Dict]:
        """
        Получение персональных рекомендаций от ИИ
        
        Returns:
            Список рекомендаций
        """
        recommendations = []
        context = self.user_contexts.get(user_id, {})
        profile = context.get('profile', {})
        weight_history = context.get('weight_history', [])
        
        # Рекомендации по весу
        if len(weight_history) >= 3:
            plateau = self.analytics.detect_plateau(weight_history)
            if plateau.get('plateau_detected'):
                recommendations.append({
                    'type': 'plateau_alert',
                    'priority': 'high',
                    'title': 'Обнаружено плато',
                    'message': 'Ваш вес стабилизировался. Пора внести изменения!',
                    'actions': plateau.get('recommendations', [])
                })
        
        # Рекомендации по питанию
        if profile.get('goal') == 'weight_loss':
            recommendations.append({
                'type': 'nutrition_tip',
                'priority': 'medium',
                'title': 'Совет для похудения',
                'message': 'Увеличьте потребление белка и добавьте больше овощей',
                'actions': ['Посмотреть рецепты с высоким белком', 'Список низкокалорийных продуктов']
            })
        
        # Мотивационная рекомендация
        recommendations.append({
            'type': 'motivation',
            'priority': 'low',
            'title': 'Вы молодец!',
            'message': 'Продолжайте в том же духе! Каждый день — шаг к цели.',
            'actions': ['Записать сегодняшние успехи']
        })
        
        return recommendations


# Экспорт класса
__all__ = ['AIEngine']
