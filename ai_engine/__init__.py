"""
AI Engine for HealthAI - Центральный модуль ИИ
Объединяет все ИИ-компоненты: чат-бот, аналитику, генератор рецептов
"""

import logging

from ai_engine.nutritionist_chatbot import NutritionistChatbot
from ai_engine.recipe_generator import RecipeGenerator
from ai_engine.llm_chat_backend import LLMChatBackend
from typing import Dict, Generator, List, Optional

_log = logging.getLogger(__name__)

# Сколько последних реплик держать в RAM (пары user+assistant считаются по 2 сообщения)
_OLLAMA_CHAT_MEMORY_CAP = 50


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
        self._analytics = None
        self.recipe_generator = RecipeGenerator()
        self._llm = LLMChatBackend()

        # Кэш пользовательских данных
        self.user_contexts = {}

    @property
    def analytics(self):
        """sklearn подгружается только при первом обращении к аналитике (macOS/Qt)."""
        if self._analytics is None:
            from ai_engine.predictive_analytics import PredictiveAnalytics

            self._analytics = PredictiveAnalytics()
        return self._analytics

    @staticmethod
    def _profile_context(profile: Dict) -> str:
        if not profile:
            return "Данные профиля не заполнены."
        parts = []
        for k in (
            "name",
            "weight",
            "height",
            "age",
            "gender",
            "goal",
            "activity_level",
            "diet_type",
            "target_calories",
        ):
            if k in profile and profile.get(k) is not None:
                parts.append(f"{k}: {profile[k]}")
        return "; ".join(parts) if parts else "Профиль минимальный."
    
    def initialize_user(self, user_id: int, profile: Dict) -> Dict:
        """
        Инициализация пользователя в ИИ-системе
        
        Args:
            user_id: ID пользователя
            profile: Профиль пользователя (вес, рост, возраст, цель и т.д.)
        
        Returns:
            Подтверждение инициализации
        """
        prev = self.user_contexts.get(user_id, {})
        try:
            from database.operations import load_chat_history

            ollama_messages = load_chat_history(user_id, limit=_OLLAMA_CHAT_MEMORY_CAP)
        except Exception:
            _log.debug("История чата из БД недоступна", exc_info=True)
            ollama_messages = list(prev.get("ollama_messages", []))

        self.user_contexts[user_id] = {
            "profile": profile,
            "meal_history": prev.get("meal_history", []),
            "weight_history": prev.get("weight_history", []),
            "preferences": profile.get("preferences", {}),
            "restrictions": profile.get("restrictions", []),
            "ollama_messages": ollama_messages,
        }

        self.chatbot.set_user_profile(profile)
        
        return {
            'status': 'success',
            'message': f'Пользователь {user_id} успешно инициализирован в ИИ-системе',
            'components_ready': ['chatbot', 'analytics', 'recipe_generator']
        }

    def _append_ollama_history(
        self, user_id: int, user_plain: str, assistant_plain: str
    ) -> None:
        """Добавить пару реплик в память диалога (Ollama/правила) и в SQLite."""
        u = (user_plain or "").strip()
        a = (assistant_plain or "").strip()
        if not u or not a:
            return
        ctx = self.user_contexts.get(user_id)
        if ctx is None:
            ctx = {"ollama_messages": []}
            self.user_contexts[user_id] = ctx
        hist = ctx.setdefault("ollama_messages", [])
        hist.append({"role": "user", "content": u})
        hist.append({"role": "assistant", "content": a})
        if len(hist) > _OLLAMA_CHAT_MEMORY_CAP:
            hist[:] = hist[-_OLLAMA_CHAT_MEMORY_CAP:]
        try:
            from database.operations import append_chat_turn

            append_chat_turn(user_id, u, a)
        except Exception:
            _log.warning("Не удалось сохранить историю чата в БД", exc_info=True)
    
    def chat(self, user_id: int, message: str) -> Dict:
        """
        Отправка сообщения чат-боту нутрициологу
        
        Args:
            user_id: ID пользователя
            message: Текст сообщения
        
        Returns:
            Ответ чат-бота (ключи text, message, source: llm | rules)
        """
        context = self.user_contexts.get(user_id, {})
        meal_history = context.get('meal_history', [])
        profile = context.get('profile', {})
        pc = self._profile_context(profile)
        hist = context.get("ollama_messages", [])

        ollama_text = self._llm.try_ollama_chat(message, pc, history=hist)
        if ollama_text:
            self._append_ollama_history(user_id, message.strip(), ollama_text.strip())
            return {
                "text": ollama_text,
                "message": ollama_text,
                "source": "llm",
                "intent": "llm",
            }

        response = self.chatbot.generate_response(message, meal_history)
        text = response.get("text", "")
        response["message"] = text
        response["source"] = "rules"
        if text:
            self._append_ollama_history(user_id, message.strip(), text.strip())
        return response

    def chat_stream(self, user_id: int, message: str) -> Generator[str, None, None]:
        """
        Потоковый ответ: при доступной Ollama — куски из /api/chat stream=True;
        иначе один блок текста из правил NutritionistChatbot.
        """
        context = self.user_contexts.get(user_id, {})
        meal_history = context.get("meal_history", [])
        profile = context.get("profile", {})
        pc = self._profile_context(profile)
        hist = context.get("ollama_messages", [])

        stream_it = self._llm.iter_ollama_chat(
            message.strip(), pc, history=hist
        )
        if stream_it is not None:
            buf: List[str] = []
            try:
                for part in stream_it:
                    buf.append(part)
                    yield part
            finally:
                full = "".join(buf).strip()
                if full:
                    self._append_ollama_history(user_id, message.strip(), full)
            return

        response = self.chatbot.generate_response(message, meal_history)
        text = response.get("text", "")
        if text:
            t = text.strip()
            self._append_ollama_history(user_id, message.strip(), t)
            yield t

    def chat_stream_welcome(self, user_id: int) -> Generator[str, None, None]:
        """
        Приветствие при открытии чата: стриминг от Ollama; в историю диалога не пишется.
        """
        from core.ollama_prompts import CHAT_WELCOME_USER_PROMPT

        context = self.user_contexts.get(user_id, {})
        profile = context.get("profile", {})
        pc = self._profile_context(profile)

        stream_it = self._llm.iter_ollama_chat(
            CHAT_WELCOME_USER_PROMPT.strip(), pc, history=[]
        )
        if stream_it is not None:
            yield from stream_it
            return

        name = (profile or {}).get("name") or ""
        if name:
            yield (
                f"Здравствуйте, {name}! Я ИИ-нутрициолог HealthAI. "
                "Спрашивайте о питании, калориях и привычках — подскажу с учётом вашего профиля."
            )
        else:
            yield (
                "Здравствуйте! Я ИИ-нутрициолог HealthAI. "
                "Задайте вопрос о питании, калориях или режиме — разберёмся вместе."
            )
    
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
