"""
UI Widgets Package - Экспорт всех виджетов
"""
from .ai_chat_widget import AIChatWidget
from .ai_analytics_widget import AIAnalyticsWidget
from .ai_recipe_widget import AIRecipeGeneratorWidget

__all__ = [
    'AIChatWidget',
    'AIAnalyticsWidget', 
    'AIRecipeGeneratorWidget'
]
