"""Тесты для NutritionistChatbot"""

import pytest
from ai_engine.nutritionist_chatbot import NutritionistChatbot


def test_detect_intent_greeting():
    """Intent greet должен распознавать короткие приветствия"""
    bot = NutritionistChatbot()
    # Проверяем несколько вариантов «привет».
    greetings = ['Привет', 'здравствуйте', 'добрый день']
    for msg in greetings:
        intent, confidence = bot.detect_intent(msg)
        assert intent == 'greeting'
        assert confidence > 0.0


def test_detect_intent_weight_loss():
    """Должен распознавать цели снижения веса"""
    bot = NutritionistChatbot()
    intents = [
        'хочу похудеть',
        'нужно сбросить вес',
        'помогите убрать жир',
    ]
    for msg in intents:
        intent, confidence = bot.detect_intent(msg)
        assert intent == 'weight_loss'
        assert confidence > 0.0


def test_detect_intent_calorie_question():
    """Вопросы о калориях должны отображаться как 'calorie_question'"""
    bot = NutritionistChatbot()
    questions = ['Сколько калорий в сутки?', 'калории в день', 'сколько ккал в сутки']
    for msg in questions:
        intent, confidence = bot.detect_intent(msg)
        assert intent == 'calorie_question'
        assert confidence > 0.0