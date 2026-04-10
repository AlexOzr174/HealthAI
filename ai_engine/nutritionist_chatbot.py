"""
AI Nutritionist Chatbot - Умный чат-бот нутрициолог
Использует локальные модели и правила для персонализированных рекомендаций
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import re

class NutritionistChatbot:
    """
    Интеллектуальный чат-бот нутрициолог с поддержкой контекста
    Анализирует профиль пользователя, историю питания и даёт рекомендации
    """
    
    def __init__(self):
        self.context = {}
        self.user_profile = None
        self.conversation_history = []
        
        # Паттерны для распознавания намерений
        self.intents = {
            'greeting': ['привет', 'здравствуйте', 'добрый день', 'доброе утро', 'добрый вечер', 'хай', 'hello', 'hi'],
            'weight_loss': ['похудеть', 'сбросить вес', 'убрать живот', 'сжечь жир', 'минус кг', 'потерять вес'],
            'weight_gain': ['набрать вес', 'накачаться', 'набрать массу', 'увеличить вес'],
            'maintain': ['поддерживать вес', 'остаться в форме', 'не менять вес'],
            'diet_advice': ['что есть', 'рекомендации', 'советы', 'как питаться', 'меню', 'рацион'],
            'calorie_question': ['калории', 'ккал', 'энергия', 'сколько калорий', 'норма калорий'],
            'protein_question': ['белок', 'протеин', 'сколько белка', 'норма белка'],
            'water_question': ['вода', 'пить', 'сколько пить', 'норма воды', 'гидратация'],
            'meal_plan': ['план питания', 'меню на день', 'что приготовить', 'рецепты'],
            'problem': ['проблема', 'не получается', 'трудность', 'сложно', 'не знаю как'],
            'motivation': ['мотивация', 'устал', 'нет сил', 'опустились руки', 'хочу бросить'],
            'progress': ['прогресс', 'результаты', 'как дела', 'динамика', 'изменения'],
            'goodbye': ['пока', 'до свидания', 'спасибо', 'всего хорошего', 'завершить']
        }
        
        # База знаний нутрициолога
        self.knowledge_base = self._load_knowledge_base()
        
    def _load_knowledge_base(self) -> Dict:
        """Загрузка базы знаний о питании"""
        return {
            'weight_loss': {
                'calorie_deficit': 0.85,  # 85% от нормы
                'protein_multiplier': 1.6,  # 1.6г на кг веса
                'tips': [
                    "Создайте дефицит калорий 15-20% от вашей нормы",
                    "Увеличьте потребление белка до 1.6-2.0г на кг веса",
                    "Добавьте больше овощей и клетчатки в рацион",
                    "Пейте воду за 20 минут до еды",
                    "Избегайте жидких калорий (соки, газировки)",
                    "Спите 7-8 часов для нормализации гормонов"
                ],
                'foods_to_limit': ['сахар', 'белый хлеб', 'фастфуд', 'сладкие напитки', 'алкоголь'],
                'foods_to_increase': ['овощи', 'нежирное мясо', 'рыба', 'яйца', 'творог', 'бобовые']
            },
            'weight_gain': {
                'calorie_surplus': 1.15,  # 115% от нормы
                'protein_multiplier': 2.0,  # 2.0г на кг веса
                'tips': [
                    "Создайте профицит калорий 15% от вашей нормы",
                    "Потребляйте 2.0г белка на кг веса для роста мышц",
                    "Добавьте сложные углеводы: рис, гречку, овсянку",
                    "Ешьте каждые 3-4 часа",
                    "Используйте протеиновые коктейли между приёмами пищи",
                    "Тренируйтесь с отягощениями 3-4 раза в неделю"
                ],
                'foods_to_increase': ['рис', 'гречка', 'овсянка', 'бананы', 'орехи', 'авокадо', 'лосось']
            },
            'maintain': {
                'calorie_factor': 1.0,
                'protein_multiplier': 1.4,
                'tips': [
                    "Поддерживайте баланс КБЖУ согласно вашей норме",
                    "Разнообразьте рацион разными группами продуктов",
                    "Следите за качеством сна и уровнем стресса",
                    "Регулярно взвешивайтесь и корректируйте питание"
                ]
            },
            'general_advice': {
                'water_formula': '30мл на 1кг веса',
                'meal_frequency': '4-5 приёмов пищи в день',
                'sleep_hours': '7-8 часов',
                'fiber_norm': '25-30г в день'
            }
        }
    
    def set_user_profile(self, profile: Dict):
        """Установка профиля пользователя"""
        self.user_profile = profile
        self.context['goal'] = profile.get('goal', 'maintain')
        self.context['weight'] = profile.get('weight', 70)
        self.context['height'] = profile.get('height', 170)
        self.context['age'] = profile.get('age', 30)
        self.context['gender'] = profile.get('gender', 'female')
        self.context['activity'] = profile.get('activity_level', 1.2)
        
    def detect_intent(self, message: str) -> Tuple[str, float]:
        """Распознавание намерения пользователя"""
        message_lower = message.lower()
        best_intent = 'unknown'
        best_score = 0.0
        
        for intent, keywords in self.intents.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > best_score:
                best_score = score
                best_intent = intent
                
        # Нормализация уверенности
        confidence = min(best_score / 3.0, 1.0) if best_score > 0 else 0.0
        return best_intent, confidence
    
    def extract_entities(self, message: str) -> Dict:
        """Извлечение сущностей из сообщения"""
        entities = {}
        
        # Извлечение чисел (вес, калории, время)
        numbers = re.findall(r'\d+(?:\.\d+)?', message)
        if numbers:
            if any(word in message.lower() for word in ['кг', 'килограмм', 'вес']):
                entities['weight'] = float(numbers[0])
            elif any(word in message.lower() for word in ['см', 'сантиметр', 'рост']):
                entities['height'] = float(numbers[0])
            elif any(word in message.lower() for word in ['лет', 'год', 'возраст']):
                entities['age'] = int(numbers[0])
            elif any(word in message.lower() for word in ['калорий', 'ккал', 'калории']):
                entities['calories'] = int(numbers[0])
                
        return entities
    
    def generate_response(self, message: str, meal_history: Optional[List] = None) -> Dict:
        """Генерация ответа чат-бота"""
        
        # Добавляем сообщение в историю
        self.conversation_history.append({
            'role': 'user',
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Распознаём намерение
        intent, confidence = self.detect_intent(message)
        entities = self.extract_entities(message)
        
        # Обновляем профиль если есть новые данные
        if entities:
            for key, value in entities.items():
                if hasattr(self, 'context') and key in self.context:
                    self.context[key] = value
        
        # Генерируем ответ в зависимости от намерения
        response_data = self._generate_intent_response(intent, confidence, message, meal_history)
        
        # Добавляем ответ в историю
        self.conversation_history.append({
            'role': 'assistant',
            'message': response_data['text'],
            'timestamp': datetime.now().isoformat(),
            'intent': intent,
            'confidence': confidence
        })
        
        return response_data
    
    def _generate_intent_response(self, intent: str, confidence: float, 
                                  message: str, meal_history: Optional[List]) -> Dict:
        """Генерация ответа на основе намерения"""
        
        responses = {
            'greeting': self._handle_greeting(),
            'weight_loss': self._handle_weight_goal('weight_loss'),
            'weight_gain': self._handle_weight_goal('weight_gain'),
            'maintain': self._handle_weight_goal('maintain'),
            'diet_advice': self._handle_diet_advice(meal_history),
            'calorie_question': self._handle_calorie_question(),
            'protein_question': self._handle_protein_question(),
            'water_question': self._handle_water_question(),
            'meal_plan': self._handle_meal_plan(),
            'problem': self._handle_problem(message),
            'motivation': self._handle_motivation(),
            'progress': self._handle_progress(),
            'goodbye': self._handle_goodbye(),
            'unknown': self._handle_unknown()
        }
        
        return responses.get(intent, responses['unknown'])
    
    def _handle_greeting(self) -> Dict:
        """Обработка приветствия"""
        hour = datetime.now().hour
        if hour < 12:
            greeting = "Доброе утро! ☀️"
        elif hour < 18:
            greeting = "Добрый день! 🌤️"
        else:
            greeting = "Добрый вечер! 🌙"
            
        name = ""
        if self.user_profile and self.user_profile.get('name'):
            name = f", {self.user_profile['name']}!"
            
        return {
            'text': f"{greeting}{name} Я ваш персональный ИИ-нутрициолог. Готов помочь вам достичь ваших целей в питании! Чем могу быть полезен?",
            'suggestions': ['Рассчитать норму калорий', 'Получить план питания', 'Советы по похудению'],
            'type': 'greeting'
        }
    
    def _handle_weight_goal(self, goal: str) -> Dict:
        """Обработка целей по весу"""
        if not self.user_profile:
            return {
                'text': "Чтобы дать точные рекомендации, мне нужно знать ваш профиль. Пожалуйста, укажите ваш текущий вес, рост, возраст и уровень активности.",
                'suggestions': ['Ввести данные профиля', 'Рассчитать калории'],
                'type': 'info_request'
            }
        
        kb = self.knowledge_base[goal]
        weight = self.context.get('weight', 70)
        
        # Расчёт рекомендаций
        if goal == 'weight_loss':
            target = f"снизить вес до {weight * 0.9:.1f} кг"
            timeframe = "8-12 недель"
        elif goal == 'weight_gain':
            target = f"набрать вес до {weight * 1.1:.1f} кг"
            timeframe = "12-16 недель"
        else:
            target = "поддерживать текущий вес"
            timeframe = "постоянно"
        
        tips = random.sample(kb['tips'], min(3, len(kb['tips'])))
        
        response_text = f"Отличная цель! Для того чтобы {target}, я рекомендую:\n\n"
        for i, tip in enumerate(tips, 1):
            response_text += f"{i}. {tip}\n"
        
        response_text += f"\n📊 Ориентировочный срок достижения цели: {timeframe}"
        
        return {
            'text': response_text,
            'suggestions': ['Показать расчёт калорий', 'Составить меню на день', 'Узнать про белки'],
            'type': 'advice',
            'goal': goal
        }
    
    def _handle_diet_advice(self, meal_history: Optional[List]) -> Dict:
        """Обработка запроса советов по питанию"""
        if not self.user_profile:
            return {
                'text': "Для персональных рекомендаций расскажите немного о себе: ваш вес, рост, возраст и цель.",
                'suggestions': ['Заполнить профиль', 'Общие советы'],
                'type': 'info_request'
            }
        
        advice_parts = []
        
        # Анализ текущего рациона если есть история
        if meal_history and len(meal_history) > 0:
            advice_parts.append("📈 На основе вашего рациона:")
            
            # Простой анализ
            total_calories = sum(meal.get('calories', 0) for meal in meal_history[-7:])
            avg_calories = total_calories / max(len(meal_history), 1)
            
            if avg_calories > 0:
                advice_parts.append(f"• Средняя калорийность: {avg_calories:.0f} ккал")
        
        # Общие рекомендации
        goal = self.context.get('goal', 'maintain')
        kb = self.knowledge_base.get(goal, self.knowledge_base['maintain'])
        
        advice_parts.append("\n💡 Мои рекомендации:")
        tips = random.sample(kb['tips'], min(4, len(kb['tips'])))
        advice_parts.extend([f"• {tip}" for tip in tips])
        
        return {
            'text': '\n'.join(advice_parts),
            'suggestions': ['План питания на неделю', 'Рецепты для моей цели', 'Норма воды'],
            'type': 'advice'
        }
    
    def _handle_calorie_question(self) -> Dict:
        """Ответ на вопрос о калориях"""
        if not self.user_profile:
            base_calories = 2000
        else:
            # Формула Миффлина-Сан Жеора
            weight = self.context.get('weight', 70)
            height = self.context.get('height', 170)
            age = self.context.get('age', 30)
            gender = self.context.get('gender', 'female')
            activity = self.context.get('activity', 1.2)
            
            if gender == 'male':
                bmr = 10 * weight + 6.25 * height - 5 * age + 5
            else:
                bmr = 10 * weight + 6.25 * height - 5 * age - 161
            
            tdee = bmr * activity
            base_calories = tdee
        
        goal = self.context.get('goal', 'maintain')
        if goal == 'weight_loss':
            recommended = base_calories * 0.85
            text = f"Для похудения ваша норма: {recommended:.0f} ккал/день (дефицит 15%)\nБазовый обмен: {base_calories:.0f} ккал"
        elif goal == 'weight_gain':
            recommended = base_calories * 1.15
            text = f"Для набора массы ваша норма: {recommended:.0f} ккал/день (профицит 15%)\nБазовый обмен: {base_calories:.0f} ккал"
        else:
            recommended = base_calories
            text = f"Для поддержания веса ваша норма: {recommended:.0f} ккал/день"
        
        return {
            'text': text,
            'suggestions': ['Рассчитать БЖУ', 'Примеры продуктов на эту калорийность', 'План питания'],
            'type': 'calculation',
            'calories': recommended
        }
    
    def _handle_protein_question(self) -> Dict:
        """Ответ на вопрос о белке"""
        weight = self.context.get('weight', 70)
        goal = self.context.get('goal', 'maintain')
        
        kb = self.knowledge_base.get(goal, self.knowledge_base['maintain'])
        multiplier = kb.get('protein_multiplier', 1.4)
        
        protein_norm = weight * multiplier
        
        response = f"🥩 Ваша норма белка: {protein_norm:.1f}г в день ({multiplier}г на кг веса)\n\n"
        response += "Источники белка:\n"
        response += "• Куриная грудка: 23г белка на 100г\n"
        response += "• Творог: 18г белка на 100г\n"
        response += "• Рыба: 20г белка на 100г\n"
        response += "• Яйца: 13г белка на 2 яйца\n"
        response += "• Чечевица: 9г белка на 100г"
        
        return {
            'text': response,
            'suggestions': ['Норма жиров и углеводов', 'Рецепты богатые белком', 'Когда лучше есть белок'],
            'type': 'info'
        }
    
    def _handle_water_question(self) -> Dict:
        """Ответ на вопрос о воде"""
        weight = self.context.get('weight', 70)
        water_norm = weight * 0.03  # 30мл на кг
        
        response = f"💧 Ваша норма воды: {water_norm:.2f}л в день ({water_norm*1000:.0f}мл)\n\n"
        response += "Советы по гидратации:\n"
        response += "• Пейте стакан воды утром натощак\n"
        response += "• Выпивайте стакан за 20 мин до еды\n"
        response += "• Держите бутылку воды на рабочем столе\n"
        response += "• Контролируйте цвет мочи (должна быть светлой)"
        
        return {
            'text': response,
            'suggestions': ['Напоминания о воде', 'Как пить больше воды', 'Влияние воды на метаболизм'],
            'type': 'info'
        }
    
    def _handle_meal_plan(self) -> Dict:
        """Генерация плана питания"""
        plans = {
            'breakfast': [
                "Овсянка с ягодами и орехами",
                "Омлет с овощами и цельнозерновой хлеб",
                "Творог с фруктами и мёдом",
                "Греческий йогурт с гранолой"
            ],
            'lunch': [
                "Куриная грудка с гречкой и салатом",
                "Лосось с рисом и запечёнными овощами",
                "Индейка с киноа и авокадо",
                "Говядина с булгуром и овощным рагу"
            ],
            'dinner': [
                "Запечённая рыба с овощами",
                "Куриное филе с салатом из свежих овощей",
                "Творог с зеленью и огурцом",
                "Омлет со шпинатом и помидорами"
            ],
            'snack': [
                "Яблоко с миндалём",
                "Протеиновый батончик",
                "Греческий йогурт",
                "Морковные палочки с хумусом"
            ]
        }
        
        response = "🍽️ Пример плана питания на день:\n\n"
        response += f"🌅 Завтрак: {random.choice(plans['breakfast'])}\n"
        response += f"☀️ Обед: {random.choice(plans['lunch'])}\n"
        response += f"🌇 Ужин: {random.choice(plans['dinner'])}\n"
        response += f"🍪 Перекус: {random.choice(plans['snack'])}\n\n"
        response += "Хотите подробный рецепт любого блюда или план на неделю?"
        
        return {
            'text': response,
            'suggestions': ['Рецепт завтрака', 'План на неделю', 'Альтернативные варианты'],
            'type': 'meal_plan'
        }
    
    def _handle_problem(self, message: str) -> Dict:
        """Обработка проблем пользователя"""
        problems = {
            'срыв': "Срывы — это нормально! Главное не опускать руки. Проанализируйте триггеры и продолжайте дальше.",
            'голод': "Чувство голода может означать недостаток белка или клетчатки. Попробуйте добавить больше овощей.",
            'усталость': "Усталость часто связана с недостатком калорий или железа. Проверьте свой рацион.",
            'плато': "Плато в весе — естественный этап. Попробуйте изменить тип тренировок или пересчитать калории."
        }
        
        # Поиск ключевых слов проблемы
        found_problem = None
        for key in problems.keys():
            if key in message.lower():
                found_problem = key
                break
        
        if found_problem:
            advice = problems[found_problem]
        else:
            advice = "Расскажите подробнее о вашей проблеме, чтобы я мог дать точный совет."
        
        return {
            'text': f"Понимаю вашу ситуацию. {advice}\n\nХотите, составим план действий?",
            'suggestions': ['План действий', 'Изменить рацион', 'Поговорить подробнее'],
            'type': 'support'
        }
    
    def _handle_motivation(self) -> Dict:
        """Мотивационная поддержка"""
        motivations = [
            "Каждый маленький шаг ведёт к большой цели! Вы уже молодец, что заботитесь о своём здоровье.",
            "Помните: прогресс не всегда виден сразу. Доверяйте процессу!",
            "Ваше будущее «я» скажет вам спасибо за усилия сегодня!",
            "Не сравнивайте себя с другими. Сравнивайте себя с собой вчерашним!",
            "Один пропущенный приём пищи не испортит прогресс, как и один полезный не сделает вас здоровым. Важна система!"
        ]
        
        return {
            'text': random.choice(motivations) + "\n\nРасскажите, что именно вызывает трудности? Вместе найдём решение!",
            'suggestions': ['Рассказать о проблеме', 'Получить совет', 'Скорректировать план'],
            'type': 'motivation'
        }
    
    def _handle_progress(self) -> Dict:
        """Анализ прогресса"""
        if len(self.conversation_history) < 3:
            return {
                'text': "Мы только начали общение! Давайте регулярно отслеживать ваши результаты. Записывайте вес, замеры и самочувствие.",
                'suggestions': ['Записать текущий вес', 'Поставить цель', 'Начать дневник питания'],
                'type': 'info'
            }
        
        return {
            'text': "Отслеживание прогресса — ключ к успеху! 📊\n\nРекомендую:\n• Взвешиваться 1-2 раза в неделю утром натощак\n• Делать замеры талии, бёдер, груди\n• Фотографироваться раз в 2 недели\n• Отслеживать энергию и качество сна",
            'suggestions': ['Записать замеры', 'Посмотреть статистику', 'Поставить новую цель'],
            'type': 'tracking'
        }
    
    def _handle_goodbye(self) -> Dict:
        """Прощание"""
        farewells = [
            "Было приятно помочь! Возвращайтесь, если возникнут вопросы. Здоровья вам! 💚",
            "Удачи на пути к целям! Я всегда на связи. До встречи! 👋",
            "Помните: вы делаете отличную работу! Заходите за новыми советами. Всего доброго! ✨"
        ]
        
        return {
            'text': random.choice(farewells),
            'suggestions': [],
            'type': 'farewell'
        }
    
    def _handle_unknown(self) -> Dict:
        """Обработка неизвестных запросов"""
        return {
            'text': "Интересный вопрос! Я специализируюсь на питании, здоровье и фитнесе. Спросите меня о:\n• Расчёте калорий и БЖУ\n• Планах питания и диетах\n• Рекомендациях по продуктам\n• Мотивации и советах",
            'suggestions': ['Рассчитать калории', 'План питания', 'Советы по похудению', 'Норма белка'],
            'type': 'clarification'
        }
    
    def get_conversation_summary(self) -> Dict:
        """Получение сводки по разговору"""
        intents_count = {}
        for msg in self.conversation_history:
            if msg['role'] == 'user':
                intent = msg.get('intent', 'unknown')
                intents_count[intent] = intents_count.get(intent, 0) + 1
        
        return {
            'total_messages': len(self.conversation_history),
            'user_messages': sum(1 for m in self.conversation_history if m['role'] == 'user'),
            'topics_discussed': list(intents_count.keys()),
            'last_interaction': self.conversation_history[-1]['timestamp'] if self.conversation_history else None
        }


# Экспорт класса
__all__ = ['NutritionistChatbot']
