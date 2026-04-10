"""
Чат-бот нутрициолог для HealthAI
Использует правила и контекст для умных консультаций по питанию
Работает полностью локально без внешних API
"""

import re
from typing import Dict, List, Optional
from datetime import datetime


class NutritionistChatbot:
    """
    Умный чат-бот нутрициолог с поддержкой контекста
    
    Возможности:
    - Ответы на вопросы о питании
    - Анализ рациона пользователя
    - Персонализированные рекомендации
    - Поддержка диетических ограничений
    - Контекстная память диалога
    """

    def __init__(self):
        # База знаний о питании
        self.knowledge_base = self._load_knowledge_base()
        
        # История разговора для контекста
        self.conversation_history = []
        
        # Профиль пользователя
        self.user_profile = {}
        
        # Шаблоны ответов
        self.response_templates = self._load_response_templates()

    def _load_knowledge_base(self) -> Dict:
        """Загрузка базы знаний о питании"""
        return {
            'macros': {
                'protein': {
                    'description': 'Белки - строительный материал для мышц',
                    'sources': ['мясо', 'рыба', 'яйца', 'творог', 'бобовые', 'орехи'],
                    'daily_norm_formula': 'weight_kg * 1.5-2.0',
                    'tips': [
                        'Распределяйте белок равномерно в течение дня',
                        'Оптимально 20-30г белка за приём пищи',
                        'Животные белки усваиваются лучше растительных'
                    ]
                },
                'carbs': {
                    'description': 'Углеводы - основной источник энергии',
                    'types': {
                        'simple': ['сахар', 'мёд', 'фрукты', 'выпечка'],
                        'complex': ['крупы', 'цельнозерновой хлеб', 'овощи', 'бобовые']
                    },
                    'tips': [
                        'Отдавайте предпочтение сложным углеводам',
                        'Простые углеводы лучше употреблять до 14:00',
                        'Клетчатка замедляет усвоение углеводов'
                    ]
                },
                'fats': {
                    'description': 'Жиры важны для гормонов и усвоения витаминов',
                    'types': {
                        'saturated': ['масло', 'жирное мясо', 'сливки'],
                        'unsaturated': ['рыба', 'орехи', 'авокадо', 'оливковое масло'],
                        'trans': ['маргарин', 'фастфуд', 'кондитерские изделия']
                    },
                    'tips': [
                        'Минимизируйте трансжиры',
                        'Омега-3 из рыбы полезны для сердца',
                        'Жиры должны составлять 25-35% от калорий'
                    ]
                }
            },
            'vitamins': {
                'A': {'sources': ['морковь', 'тыква', 'печень'], 'function': 'зрение, иммунитет'},
                'C': {'sources': ['цитрусовые', 'перец', 'шиповник'], 'function': 'иммунитет, коллаген'},
                'D': {'sources': ['рыба', 'яйца', 'солнце'], 'function': 'кости, иммунитет'},
                'E': {'sources': ['орехи', 'масла', 'семена'], 'function': 'антиоксидант'},
                'B12': {'sources': ['мясо', 'рыба', 'молочные'], 'function': 'нервная система, кровь'}
            },
            'diets': {
                'weight_loss': {
                    'name': 'Похудение',
                    'principles': [
                        'Дефицит калорий 10-20%',
                        'Высокий белок (1.6-2.2 г/кг)',
                        'Больше овощей и клетчатки',
                        'Контроль простых углеводов'
                    ],
                    'tips': [
                        'Пейте воду перед едой',
                        'Используйте маленькие тарелки',
                        'Ведите дневник питания',
                        'Спите 7-8 часов'
                    ]
                },
                'muscle_gain': {
                    'name': 'Набор массы',
                    'principles': [
                        'Профицит калорий 10-15%',
                        'Белок 1.6-2.2 г/кг',
                        'Углеводы вокруг тренировок',
                        'Регулярные силовые тренировки'
                    ],
                    'tips': [
                        'Ешьте каждые 3-4 часа',
                        'Добавьте протеиновый коктейль',
                        'Не забывайте про овощи',
                        'Отдыхайте между тренировками'
                    ]
                },
                'maintenance': {
                    'name': 'Поддержание веса',
                    'principles': [
                        'Калории на уровне TDEE',
                        'Сбалансированное БЖУ',
                        'Разнообразное питание',
                        'Регулярная активность'
                    ]
                }
            },
            'meal_timing': {
                'breakfast': {
                    'time': '7:00-9:00',
                    'recommendations': 'Белок + сложные углеводы + клетчатка',
                    'examples': ['овсянка с ягодами и орехами', 'омлет с овощами']
                },
                'lunch': {
                    'time': '12:00-14:00',
                    'recommendations': 'Самый большой приём пищи, белок + углеводы + овощи',
                    'examples': ['курица с гречкой и салатом', 'рыба с рисом']
                },
                'dinner': {
                    'time': '18:00-20:00',
                    'recommendations': 'Белок + овощи, меньше углеводов',
                    'examples': ['рыба с брокколи', 'творог с зеленью']
                },
                'snacks': {
                    'time': 'между основными приёмами',
                    'recommendations': 'Белок или полезные жиры',
                    'examples': ['орехи', 'йогурт', 'фрукт']
                }
            }
        }

    def _load_response_templates(self) -> Dict:
        """Загрузка шаблонов ответов"""
        return {
            'greeting': [
                "Здравствуйте! Я ваш персональный нутрициолог. Чем могу помочь?",
                "Приветствую! Готов ответить на ваши вопросы о питании.",
                "Добрый день! Давайте обсудим ваше питание и цели."
            ],
            'thanks': [
                "Всегда пожалуйста! Обращайтесь ещё.",
                "Рад был помочь! Продолжайте в том же духе!",
                "Не за что! Здоровое питание — это важно."
            ],
            'encouragement': [
                "Вы молодец! Каждый шаг важен.",
                "Продолжайте в том же духе! Результаты не заставят себя ждать.",
                "Так держать! Ваше здоровье благодарит вас."
            ]
        }

    def set_user_profile(self, profile: Dict):
        """
        Установка профиля пользователя
        
        Args:
            profile: Данные пользователя (вес, рост, возраст, цель, ограничения)
        """
        self.user_profile = profile

    def _detect_intent(self, message: str) -> str:
        """Определение намерения пользователя"""
        message_lower = message.lower()
        
        # Паттерны для различных намерений
        patterns = {
            'greeting': r'(привет|здравствуйте|добрый|хай|hello|hi)',
            'weight_loss': r'(похудеть|сбросить|вес|жир|калори|дефицит)',
            'muscle_gain': r'(набрать|мышц|масса|протеин|белок)',
            'diet_question': r'(диет|питани|рацион|меню|что есть|что кушать)',
            'macro_question': r'(белк|углевод|жир|бжу|макро|норм)',
            'vitamin_question': r'(витамин|минерал|нутриент)',
            'meal_timing': r'(когда есть|время|завтрак|обед|ужин|перекус)',
            'product_question': r'(можно ли|продукт|еда|калорийност)',
            'recipe_request': r'(рецепт|приготовить|сделать блюдо)',
            'motivation': r'(устал|не хочу|сложно|тяжело|бросить)',
            'thanks': r'(спасибо|благодарю|мерси)',
            'plateau': r'(плато|не идёт|стоит|прогресс)',
            'water': r'(вода|пить|жидкость)',
            'sleep': r'(сон|спать|усталость)',
            'exercise': r'(тренировк|спорт|физическ|упражнен)'
        }
        
        for intent, pattern in patterns.items():
            if re.search(pattern, message_lower):
                return intent
        
        return 'general'

    def _generate_response_for_intent(self, intent: str, message: str) -> Dict:
        """Генерация ответа на основе намерения"""
        
        responses = {
            'greeting': self._handle_greeting(),
            'weight_loss': self._handle_weight_loss(message),
            'muscle_gain': self._handle_muscle_gain(message),
            'diet_question': self._handle_diet_question(message),
            'macro_question': self._handle_macro_question(message),
            'vitamin_question': self._handle_vitamin_question(message),
            'meal_timing': self._handle_meal_timing(message),
            'product_question': self._handle_product_question(message),
            'recipe_request': self._handle_recipe_request(message),
            'motivation': self._handle_motivation(message),
            'thanks': self._handle_thanks(),
            'plateau': self._handle_plateau(message),
            'water': self._handle_water(message),
            'sleep': self._handle_sleep(message),
            'exercise': self._handle_exercise(message),
            'general': self._handle_general(message)
        }
        
        return responses.get(intent, responses['general'])

    def _handle_greeting(self) -> Dict:
        """Обработка приветствия"""
        import random
        return {
            'status': 'success',
            'message': random.choice(self.response_templates['greeting']),
            'suggestions': [
                'Рассчитать мою норму калорий',
                'Помочь составить план питания',
                'Ответить на вопрос о продуктах',
                'Дать совет по похудению/набору массы'
            ],
            'category': 'greeting'
        }

    def _handle_weight_loss(self, message: str) -> Dict:
        """Обработка вопросов о похудении"""
        tips = self.knowledge_base['diets']['weight_loss']['tips']
        principles = self.knowledge_base['diets']['weight_loss']['principles']
        
        response = f"""Для эффективного похудения важно соблюдать несколько принципов:

📊 Основные принципы:
{chr(10).join('• ' + p for p in principles)}

💡 Полезные советы:
{chr(10).join('• ' + t for t in tips[:3])}
"""
        
        # Персонализация если есть профиль
        if self.user_profile.get('weight') and self.user_profile.get('height'):
            weight = self.user_profile['weight']
            protein_norm = f"{weight * 1.8:.0f}-{weight * 2.0:.0f}г"
            response += f"\n\n🎯 Ваша персональная норма белка: {protein_norm}г в день"
        
        return {
            'status': 'success',
            'message': response,
            'suggestions': [
                'Рассчитать дефицит калорий',
                'Показать низкокалорийные рецепты',
                'Советы по контролю аппетита',
                'Как избежать плато'
            ],
            'category': 'weight_loss'
        }

    def _handle_muscle_gain(self, message: str) -> Dict:
        """Обработка вопросов о наборе массы"""
        principles = self.knowledge_base['diets']['muscle_gain']['principles']
        tips = self.knowledge_base['diets']['muscle_gain']['tips']
        
        response = f"""Для набора мышечной массы следуйте этим принципам:

💪 Основные принципы:
{chr(10).join('• ' + p for p in principles)}

🍽️ Советы по питанию:
{chr(10).join('• ' + t for t in tips)}
"""
        
        if self.user_profile.get('weight'):
            weight = self.user_profile['weight']
            calories = weight * 35
            protein = weight * 2.0
            response += f"\n\n📈 Примерная норма: {calories:.0f} ккал, {protein:.0f}г белка"
        
        return {
            'status': 'success',
            'message': response,
            'suggestions': [
                'Рецепты для набора массы',
                'Когда принимать протеин',
                'Лучшие источники белка',
                'План питания на день'
            ],
            'category': 'muscle_gain'
        }

    def _handle_diet_question(self, message: str) -> Dict:
        """Обработка общих вопросов о диете"""
        goal = self.user_profile.get('goal', 'maintenance')
        diet_info = self.knowledge_base['diets'].get(goal, {})
        
        response = f"""Рекомендации по питанию для вашей цели ({diet_info.get('name', 'поддержание')}):

{chr(10).join('• ' + p for p in diet_info.get('principles', ['Сбалансированное питание', 'Разнообразный рацион']))}
"""
        
        if 'tips' in diet_info:
            response += f"\n💡 Советы:\n{chr(10).join('• ' + t for t in diet_info['tips'][:3])}"
        
        return {
            'status': 'success',
            'message': response,
            'suggestions': [
                'Показать пример меню на день',
                'Список полезных продуктов',
                'Рецепты для моей цели',
                'Как считать калории'
            ],
            'category': 'diet'
        }

    def _handle_macro_question(self, message: str) -> Dict:
        """Обработка вопросов о макронутриентах"""
        macros = self.knowledge_base['macros']
        
        response = """📊 Макронутриенты - основа вашего рациона:

🥩 БЕЛКИ:
""" + macros['protein']['description'] + """
Источники: """ + ', '.join(macros['protein']['sources'][:5]) + """
Советы: """ + macros['protein']['tips'][0] + """

🍞 УГЛЕВОДЫ:
""" + macros['carbs']['description'] + """
Предпочитайте сложные: крупы, цельнозерновой хлеб, овощи

🥑 ЖИРЫ:
""" + macros['fats']['description'] + """
Полезные источники: рыба, орехи, авокадо, оливковое масло
"""
        
        if self.user_profile.get('weight'):
            weight = self.user_profile['weight']
            response += f"\n\n🎯 Ваши примерные нормы:\n"
            response += f"Белки: {weight * 1.8:.0f}-{weight * 2.0:.0f}г\n"
            response += f"Жиры: {weight * 0.9:.0f}-{weight * 1.1:.0f}г\n"
        
        return {
            'status': 'success',
            'message': response,
            'suggestions': [
                'Как распределить БЖУ по приёмам пищи',
                'Лучшие источники белка',
                'Какие жиры полезные',
                'Углеводы до и после тренировки'
            ],
            'category': 'macros'
        }

    def _handle_vitamin_question(self, message: str) -> Dict:
        """Обработка вопросов о витаминах"""
        vitamins = self.knowledge_base['vitamins']
        
        response = "🌟 Важнейшие витамины и их источники:\n\n"
        
        for vitamin, info in list(vitamins.items())[:4]:
            response += f"Витамин {vitamin}: {info['function']}\n"
            response += f"  Источники: {', '.join(info['sources'])}\n\n"
        
        response += "💡 Совет: Разнообразное питание покрывает потребность в витаминах!"
        
        return {
            'status': 'success',
            'message': response,
            'suggestions': [
                'Какие витамины нужны зимой',
                'Нужны ли витаминные добавки',
                'Признаки дефицита витаминов',
                'Лучшие источники витамина D'
            ],
            'category': 'vitamins'
        }

    def _handle_meal_timing(self, message: str) -> Dict:
        """Обработка вопросов о времени приёма пищи"""
        timing = self.knowledge_base['meal_timing']
        
        response = "⏰ Рекомендации по времени приёма пищи:\n\n"
        
        for meal, info in timing.items():
            response += f"{meal.upper()}: {info['time']}\n"
            response += f"  {info['recommendations']}\n"
            response += f"  Пример: {info['examples'][0]}\n\n"
        
        response += "💡 Главное: регулярность и баланс, а не строгое время!"
        
        return {
            'status': 'success',
            'message': response,
            'suggestions': [
                'Сколько раз в день есть',
                'Можно ли есть после 18:00',
                'Что съесть перед тренировкой',
                'Нужен ли перекус на ночь'
            ],
            'category': 'timing'
        }

    def _handle_product_question(self, message: str) -> Dict:
        """Обработка вопросов о продуктах"""
        # Простая эвристика для популярных продуктов
        product_tips = {
            'хлеб': 'Выбирайте цельнозерновой или ржаной хлеб. Избегайте белого.',
            'рис': 'Бурый рис полезнее белого (больше клетчатки и витаминов).',
            'молоко': 'Отличный источник кальция и белка. Выбирайте 1.5-2.5% жирности.',
            'яйца': 'Идеальный источник белка. Можно 1-2 яйца в день.',
            'банан': 'Хороший источник калия и быстрых углеводов. Отлично после тренировки.',
            'овсянка': 'Полезный сложный углевод. Лучше долгой варки, не мгновенную.',
            'творог': 'Отличный источник казеина (медленного белка). Идеален на ужин.'
        }
        
        response = "ℹ️ Информация о продуктах:\n\n"
        
        found = False
        for product, tip in product_tips.items():
            if product in message.lower():
                response += f"• {tip}\n"
                found = True
        
        if not found:
            response += "Уточните, какой продукт вас интересует?\n\n"
            response += "Общие рекомендации:\n"
            response += "• Отдавайте предпочтение цельным, необработанным продуктам\n"
            response += "• Читайте состав на этикетках\n"
            response += "• Избегайте продуктов с трансжирами"
        
        return {
            'status': 'success',
            'message': response,
            'suggestions': [
                'Список полезных продуктов',
                'Какие продукты избегать',
                'Как читать этикетки',
                'Полезные снеки'
            ],
            'category': 'products'
        }

    def _handle_recipe_request(self, message: str) -> Dict:
        """Обработка запроса рецепта"""
        category = 'lunch'
        if 'завтрак' in message.lower():
            category = 'breakfast'
        elif 'ужин' in message.lower():
            category = 'dinner'
        elif 'перекус' in message.lower() or 'снек' in message.lower():
            category = 'snack'
        
        return {
            'status': 'success',
            'message': f"Отличная идея! Сейчас подберу рецепт для категории '{category}'.",
            'action': 'generate_recipe',
            'action_params': {'category': category},
            'suggestions': [
                'Сгенерировать рецепт',
                'Показать мои сохранённые рецепты',
                'Рецепты с высоким белком',
                'Низкокалорийные варианты'
            ],
            'category': 'recipe'
        }

    def _handle_motivation(self, message: str) -> Dict:
        """Обработка запроса мотивации"""
        import random
        
        motivational_quotes = [
            "Каждый день — это новый шанс стать лучше!",
            "Маленькие шаги ведут к большим результатам.",
            "Ваше тело может всё. Нужно убедить в этом мозг!",
            "Не сравнивайте себя с другими. Сравнивайте с собой вчерашним.",
            "Результаты приходят к тем, кто не сдаётся."
        ]
        
        response = f"""💪 {random.choice(motivational_quotes)}

Помните:
• Прогресс не всегда линейный
• Важны постоянство, а не идеальность
• Один промах не испортит весь путь
• Вы уже сделали первый шаг — начали!

{random.choice(self.response_templates['encouragement'])}
"""
        
        return {
            'status': 'success',
            'message': response,
            'suggestions': [
                'Поставить новую мини-цель',
                'Вспомнить свои достижения',
                'Скорректировать план',
                'Найти поддержку'
            ],
            'category': 'motivation'
        }

    def _handle_thanks(self) -> Dict:
        """Обработка благодарности"""
        import random
        return {
            'status': 'success',
            'message': random.choice(self.response_templates['thanks']),
            'suggestions': [
                'Задать ещё вопрос',
                'Получить рецепт',
                'Проверить прогресс',
                'Завершить会话'
            ],
            'category': 'thanks'
        }

    def _handle_plateau(self, message: str) -> Dict:
        """Обработка вопроса о плато"""
        response = """📉 Плато — это нормально! Вот что можно сделать:

🔄 Измените подход:
• Пересчитайте калории (вес изменился — нормы тоже)
• Поменяйте соотношение БЖУ
• Добавьте кардио или измените тренировки
• Устройте рефид (день с калориями на уровне поддержки)

😴 Проверьте восстановление:
• Сон 7-8 часов?
• Уровень стресса?
• Достаточно ли отдыха?

⚖️ Помните:
• Вес может колебаться из-за воды
• Замеры объёмов важнее веса
• Фото «до/после» показывают реальнее

💡 Совет: Ведите дневник не только еды, но и самочувствия!
"""
        
        return {
            'status': 'success',
            'message': response,
            'suggestions': [
                'Пересчитать норму калорий',
                'Идеи для кардио',
                'Рецепты для рефида',
                'Как снизить стресс'
            ],
            'category': 'plateau'
        }

    def _handle_water(self, message: str) -> Dict:
        """Обработка вопроса о воде"""
        weight = self.user_profile.get('weight', 70)
        norm = weight * 0.03
        
        response = f"""💧 Вода — основа здоровья!

📊 Ваша норма: {norm:.1f}-{norm*1.2:.1f} литра в день
(расчёт: 30-35 мл на кг веса)

✅ Преимущества достаточного питья:
• Улучшение метаболизма
• Снижение аппетита
• Лучшая работоспособность
• Здоровая кожа

💡 Советы:
• Стакан воды утром натощак
• Пейте перед едой (за 20 мин)
• Держите бутылку воды на виду
• Моча должна быть светло-жёлтой

⚠️ Не пейте слишком много сразу — распределяйте в течение дня!
"""
        
        return {
            'status': 'success',
            'message': response,
            'suggestions': [
                'Напоминания о воде',
                'Влияние воды на вес',
                'Что кроме воды можно пить',
                'Кофе обезвоживает?'
            ],
            'category': 'water'
        }

    def _handle_sleep(self, message: str) -> Dict:
        """Обработка вопроса о сне"""
        response = """😴 Сон критически важен для результатов!

📊 Почему сон важен:
• Недосып повышает грелин (гормон голода)
• Снижается лептин (гормон сытости)
• Ухудшается восстановление мышц
• Падает мотивация и сила воли

🌙 Оптимальный сон:
• 7-9 часов для взрослых
• Ложиться и вставать в одно время
• Темнота и прохлада в комнате
• Без экранов за 1 час до сна

💤 Советы для лучшего сна:
• Прогулка вечером
• Тёплый душ/ванна
• Чай с ромашкой или мятой
• Медитация или дыхательные упражнения

🎯 Приоритет: Сон > Питание > Тренировки
"""
        
        return {
            'status': 'success',
            'message': response,
            'suggestions': [
                'Как улучшить качество сна',
                'Влияние сна на вес',
                'Мелатонин — стоит ли принимать',
                'Режим дня для похудения'
            ],
            'category': 'sleep'
        }

    def _handle_exercise(self, message: str) -> Dict:
        """Обработка вопроса о тренировках"""
        goal = self.user_profile.get('goal', 'maintenance')
        
        if goal == 'weight_loss':
            advice = """🏃‍♂️ Для похудения:
• Кардио 3-4 раза в неделю (30-45 мин)
• Силовые 2-3 раза (сохраняют мышцы)
• NEAT (бытовая активность) — очень важно!
• 10 000+ шагов в день"""
        elif goal == 'muscle_gain':
            advice = """💪 Для набора массы:
• Силовые 3-5 раз в неделю
• Прогрессия нагрузок обязательна
• Белок вокруг тренировок
• Избыток калорий"""
        else:
            advice = """🏋️ Для поддержания:
• Комбинация кардио и силовых
• 150+ минут активности в неделю
• Радуйтесь движению!"""
        
        response = f"""🏋️ Тренировки и питание неразрывны!

{advice}

🍽️ Питание вокруг тренировок:
• До: углеводы за 1-2 часа
• После: белок + углеводы в течение 2 часов
• Вода во время тренировки

💡 Важно: Тренировки не компенсируют плохое питание!
Сначала наладьте рацион, затем добавляйте активность.
"""
        
        return {
            'status': 'success',
            'message': response,
            'suggestions': [
                'План тренировок для дома',
                'Что есть до/после тренировки',
                'Кардио или силовые?',
                'Как начать заниматься'
            ],
            'category': 'exercise'
        }

    def _handle_general(self, message: str) -> Dict:
        """Обработка общего вопроса"""
        response = """Я могу помочь вам с:

🥗 Питание и диеты:
• Расчёт калорий и БЖУ
• Планы питания
• Советы по похудению/набору массы
• Вопросы о продуктах

💪 Тренировки и образ жизни:
• Рекомендации по активности
• Сон и восстановление
• Мотивация и привычки

🍳 Рецепты:
• Генерация рецептов под ваши цели
• Замены ингредиентов
• Планы на неделю

❓ Задайте конкретный вопрос, например:
• "Сколько калорий мне нужно?"
• "Что съесть на завтрак?"
• "Как преодолеть плато?"
• "Дай рецепт ужина с курицей"
"""
        
        return {
            'status': 'success',
            'message': response,
            'suggestions': [
                'Рассчитать мою норму калорий',
                'Помочь с планом питания',
                'Дать рецепт',
                'Совет по похудению'
            ],
            'category': 'general'
        }

    def generate_response(self, message: str, meal_history: Optional[List[Dict]] = None) -> Dict:
        """
        Генерация ответа на сообщение пользователя
        
        Args:
            message: Текст сообщения
            meal_history: История питания для контекста
        
        Returns:
            Словарь с ответом
        """
        # Сохраняем в историю
        self.conversation_history.append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Определяем намерение
        intent = self._detect_intent(message)
        
        # Генерируем ответ
        response = self._generate_response_for_intent(intent, message)
        
        # Добавляем контекст из истории питания если есть
        if meal_history and len(meal_history) > 0:
            today_meals = [m for m in meal_history if m.get('date', '')[:10] == datetime.now().strftime('%Y-%m-%d')]
            if today_meals:
                total_calories = sum(m.get('calories', 0) for m in today_meals)
                response['context'] = {
                    'today_meals': len(today_meals),
                    'today_calories': total_calories,
                    'message': f"Вы уже съели {total_calories} ккал сегодня."
                }
        
        # Сохраняем ответ в историю
        self.conversation_history.append({
            'role': 'assistant',
            'content': response.get('message', ''),
            'timestamp': datetime.now().isoformat()
        })
        
        # Ограничиваем историю
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]
        
        return response

    def get_conversation_summary(self) -> str:
        """Получение краткой сводки диалога"""
        if not self.conversation_history:
            return "Диалог ещё не начат."
        
        user_messages = [m for m in self.conversation_history if m['role'] == 'user']
        return f"В диалоге {len(user_messages)} сообщений от пользователя."

    def clear_history(self):
        """Очистка истории диалога"""
        self.conversation_history = []
