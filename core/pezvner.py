# Система лечебных диет по Певзнеру
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional
from enum import Enum


class DietType(Enum):
    """Типы диет по Певзнеру"""
    PEVZNER_1 = "pevzner_1"
    PEVZNER_2 = "pevzner_2"
    PEVZNER_3 = "pevzner_3"
    PEVZNER_4 = "pevzner_4"
    PEVZNER_5 = "pevzner_5"
    PEVZNER_6 = "pevzner_6"
    PEVZNER_7 = "pevzner_7"
    PEVZNER_8 = "pevzner_8"
    PEVZNER_9 = "pevzner_9"
    PEVZNER_10 = "pevzner_10"
    PEVZNER_11 = "pevzner_11"
    PEVZNER_12 = "pevzner_12"
    PEVZNER_13 = "pevzner_13"
    PEVZNER_14 = "pevzner_14"
    PEVZNER_15 = "pevzner_15"


@dataclass
class DietRule:
    """Правило диеты"""
    name: str
    allowed: List[str]  # Разрешённые продукты/категории
    forbidden: List[str]  # Запрещённые
    restrictions: List[str]  # Текстовые ограничения
    calories_limit: int  # Лимит калорий (0 = без лимита)
    cooking_methods: List[str]  # Разрешённые способы приготовления


@dataclass
class PevznerDiet:
    """Описание диеты по Певзнеру"""
    id: str
    number: int
    name: str
    full_name: str
    description: str
    indications: List[str]  # Показания к применению
    duration: str  # Рекомендуемая длительность
    principles: List[str]  # Основные принципы
    allowed_products: List[str]
    forbidden_products: List[str]
    cooking_rules: List[str]
    menu_features: List[str]

    # Дополнительные ограничения
    max_salt: Optional[int] = None  # грамм
    max_fluid: Optional[int] = None  # литры
    temperature_restriction: Optional[str] = None  # Температура пищи
    meal_frequency: Optional[int] = None  # Приёмов пищи в день


class PevznerDiets:
    """База данных диет по Певзнеру"""

    # Кэш диет
    _diets: Dict[str, PevznerDiet] = {}

    @classmethod
    def get_diet(cls, diet_id: str) -> Optional[PevznerDiet]:
        """Получение диеты по ID"""
        if not cls._diets:
            cls._initialize_diets()
        return cls._diets.get(diet_id)

    @classmethod
    def get_all_diets(cls) -> List[PevznerDiet]:
        """Получение всех диет"""
        if not cls._diets:
            cls._initialize_diets()
        return list(cls._diets.values())

    @classmethod
    def get_diets_for_condition(cls, condition: str) -> List[PevznerDiet]:
        """Получение диет, подходящих для определённого состояния"""
        if not cls._diets:
            cls._initialize_diets()

        condition_lower = condition.lower()
        suitable = []

        for diet in cls._diets.values():
            # Проверяем показания
            for indication in diet.indications:
                if condition_lower in indication.lower():
                    suitable.append(diet)
                    break

        return suitable

    @classmethod
    def _initialize_diets(cls):
        """Инициализация всех диет"""
        cls._diets = {
            'pevzner_1': PevznerDiet(
                id='pevzner_1',
                number=1,
                name='Стол №1',
                full_name='Диета №1 (язвенная болезнь)',
                description='Щадящая диета для лечения язвенной болезни желудка и 12-перстной кишки',
                indications=['Язвенная болезнь желудка', 'Язвенная болезнь 12-перстной кишки', 'Гастрит'],
                duration='2-4 месяца',
                principles=[
                    'Исключение механических и химических раздражителей',
                    'Исключение продуктов, вызывающих усиление секреции',
                    'Частое дробное питание',
                ],
                allowed_products=['Молочные продукты', 'Каши', 'Отварные овощи', 'Нежирное мясо', 'Рыба'],
                forbidden_products=['Жареные блюда', 'Копчёности', 'Острые специи', 'Грибы', 'Бобовые'],
                cooking_rules=['Варка', 'Приготовление на пару', 'Запекание'],
                menu_features='5-6 приёмов пищи в день',
                max_salt=8,
                max_fluid=1.5,
                temperature_restriction='Пища должна быть тёплой (40-50°C)',
                meal_frequency=5,
            ),
            'pevzner_2': PevznerDiet(
                id='pevzner_2',
                number=2,
                name='Стол №2',
                full_name='Диета №2 (гастрит с пониженной кислотностью)',
                description='Диета для лечения гастрита с пониженной кислотностью',
                indications=['Гастрит с пониженной кислотностью', 'Атрофический гастрит'],
                duration='Постоянно или длительно',
                principles=[
                    'Умеренная стимуляция секреции',
                    'Полноценное питание с достаточным количеством белка',
                ],
                allowed_products=['Мясные и рыбные бульоны', 'Кисломолочные продукты', 'Каши'],
                forbidden_products=['Очень горячие блюда', 'Газированные напитки'],
                cooking_rules=['Варка', 'Запекание', 'Лёгкое обжаривание'],
                menu_features='4-5 приёмов пищи',
                max_salt=10,
                meal_frequency=4,
            ),
            'pevzner_3': PevznerDiet(
                id='pevzner_3',
                number=3,
                name='Стол №3',
                full_name='Диета №3 (запоры)',
                description='Диета для лечения хронических запоров',
                indications=['Хронические запоры', 'Атонический колит'],
                duration='До нормализации стула',
                principles=[
                    'Продукты, усиливающие перистальтику',
                    'Богатые пищевыми волокнами',
                    'Тёплые напитки',
                ],
                allowed_products=['Сырые и варёные овощи', 'Фрукты', 'Крупы', 'Кисломолочные продукты'],
                forbidden_products=['Шоколад', 'Какао', 'Крепкий чай'],
                cooking_rules='Любые, кроме жарения в жире',
                menu_features='4-6 приёмов пищи с упором на утро',
                meal_frequency=5,
            ),
            'pevzner_4': PevznerDiet(
                id='pevzner_4',
                number=4,
                name='Стол №4',
                full_name='Диета №4 (острые кишечные заболевания)',
                description='Щадящая диета при острых кишечных заболеваниях',
                indications=['Острый энтерит', 'Острый колит', 'Обострение хронических заболеваний кишечника'],
                duration='Непродолжительно (до 5-7 дней)',
                principles=[
                    'Максимальное механическое и химическое щажение',
                    'Исключение продуктов, усиливающих перистальтику',
                ],
                allowed_products=['Слизистые супы', 'Каши', 'Кисели', 'Сухари'],
                forbidden_products=['Свежие овощи и фрукты', 'Молоко', 'Жареные блюда'],
                cooking_rules=['Варка', 'Приготовление на пару'],
                menu_features='Дробное питание небольшими порциями',
                meal_frequency=6,
            ),
            'pevzner_5': PevznerDiet(
                id='pevzner_5',
                number=5,
                name='Стол №5',
                full_name='Диета №5 (заболевания печени и желчевыводящих путей)',
                description='Основная диета при заболеваниях печени и желчного пузыря',
                indications=['Хронический гепатит', 'Желчнокаменная болезнь', 'Холецистит', 'Цирроз печени'],
                duration='От нескольких месяцев до нескольких лет',
                principles=[
                    'Нормализация функций печени',
                    'Улучшение желчеотделения',
                    'Щажение желудочно-кишечного тракта',
                ],
                allowed_products=['Нежирное мясо', 'Рыба', 'Молочные продукты', 'Каши', 'Овощи и фрукты'],
                forbidden_products=['Жареные блюда', 'Копчёности', 'Острые специи', 'Алкоголь', 'Шоколад'],
                cooking_rules=['Варка', 'Запекание', 'Приготовление на пару'],
                menu_features='5 приёмов пищи в день',
                max_salt=10,
                meal_frequency=5,
            ),
            'pevzner_6': PevznerDiet(
                id='pevzner_6',
                number=6,
                name='Стол №6',
                full_name='Диета №6 (подагра)',
                description='Диета для лечения подагры и мочекислого диатеза',
                indications=['Подагра', 'Мочекислый диатез', 'Оксалурия'],
                duration='Длительно, часто пожизненно',
                principles=[
                    'Исключение продуктов с высоким содержанием пуринов',
                    'Ощелачивание организма',
                    'Обильное питьё',
                ],
                allowed_products=['Молочные продукты', 'Крупы', 'Яйца', 'Овощи (кроме запрещённых)', 'Фрукты'],
                forbidden_products=['Мясные бульоны', 'Субпродукты', 'Сардины', 'Щавель', 'Шпинат'],
                cooking_rules='Любые',
                menu_features='Обильное питьё (до 2-2.5 литров)',
                max_fluid=2.5,
                meal_frequency=5,
            ),
            'pevzner_7': PevznerDiet(
                id='pevzner_7',
                number=7,
                name='Стол №7',
                full_name='Диета №7 (заболевания почек)',
                description='Диета при острых и хронических нефритах',
                indications=['Острый нефрит', 'Хронический нефрит', 'Нефротический синдром'],
                duration='В период обострения - строгая, затем расширенная',
                principles=[
                    'Ограничение соли и белка',
                    'Щажение почек',
                    'Уменьшение отёков',
                ],
                allowed_products=['Молочные продукты', 'Крупы', 'Овощи', 'Фрукты', 'Нежирное мясо (ограниченно)'],
                forbidden_products=['Поваренная соль', 'Копчёности', 'Консервы', 'Грибы'],
                cooking_rules=['Варка', 'Запекание'],
                menu_features='5 приёмов пищи в день',
                max_salt=2,
                max_fluid=0.8,
                meal_frequency=5,
            ),
            'pevzner_8': PevznerDiet(
                id='pevzner_8',
                number=8,
                name='Стол №8',
                full_name='Диета №8 (ожирение)',
                description='Низкокалорийная диета для лечения ожирения',
                indications=['Ожирение', 'Избыточный вес'],
                duration='Длительно, до достижения нормального веса',
                principles=[
                    'Снижение калорийности рациона',
                    'Ограничение углеводов и жиров',
                    'Увеличение объёма пищи за счёт низкокалорийных продуктов',
                ],
                allowed_products=['Нежирное мясо', 'Рыба', 'Морепродукты', 'Овощи', 'Фрукты'],
                forbidden_products=['Сахар', 'Мучные изделия', 'Жирное мясо', 'Алкоголь'],
                cooking_rules=['Варка', 'Запекание', 'Приготовление на пару'],
                menu_features='5-6 приёмов пищи',
                max_salt=6,
            ),
            'pevzner_9': PevznerDiet(
                id='pevzner_9',
                number=9,
                name='Стол №9',
                full_name='Диета №9 (сахарный диабет)',
                description='Диета для лечения сахарного диабета средней и лёгкой тяжести',
                indications=['Сахарный диабет 2 типа', 'Нарушение толерантности к глюкозе'],
                duration='Пожизненно или длительно',
                principles=[
                    'Исключение простых углеводов',
                    'Дробное питание',
                    'Контроль гликемического индекса',
                ],
                allowed_products=['Нежирное мясо', 'Рыба', 'Яйца', 'Молочные продукты', 'Крупы', 'Овощи'],
                forbidden_products=['Сахар', 'Мёд', 'Варенье', 'Выпечка', 'Виноград', 'Бананы'],
                cooking_rules=['Варка', 'Запекание', 'Приготовление на пару'],
                menu_features='5-6 приёмов пищи',
                max_salt=6,
            ),
            'pevzner_10': PevznerDiet(
                id='pevzner_10',
                number=10,
                name='Стол №10',
                full_name='Диета №10 (заболевания сердечно-сосудистой системы)',
                description='Диета при заболеваниях сердца и сосудов',
                indications=['Ишемическая болезнь сердца', 'Гипертоническая болезнь', 'Сердечная недостаточность'],
                duration='Длительно',
                principles=[
                    'Ограничение соли',
                    'Уменьшение нагрузки на сердечно-сосудистую систему',
                    'Нормализация обмена веществ',
                ],
                allowed_products=['Нежирное мясо', 'Рыба', 'Молочные продукты', 'Крупы', 'Овощи', 'Фрукты'],
                forbidden_products=['Крепкий чай', 'Кофе', 'Какао', 'Шоколад', 'Острые блюда'],
                cooking_rules=['Варка', 'Запекание', 'Приготовление на пару'],
                menu_features='5 приёмов пищи в день',
                max_salt=5,
                max_fluid=1.2,
                meal_frequency=5,
            ),
            'pevzner_11': PevznerDiet(
                id='pevzner_11',
                number=11,
                name='Стол №11',
                full_name='Диета №11 (туберкулёз)',
                description='Диета для больных туберкулёзом',
                indications=['Туберкулёз лёгких', 'Истощение после инфекций'],
                duration='До выздоровления',
                principles=[
                    'Повышенная калорийность',
                    'Богатое белками и витаминами питание',
                ],
                allowed_products=['Мясо', 'Рыба', 'Яйца', 'Молоко', 'Сыр', 'Крупы', 'Фрукты'],
                forbidden_products=['Острые специи', 'Алкоголь'],
                cooking_rules='Любые, предпочтительно с сохранением питательных веществ',
                menu_features='5 приёмов пищи',
            ),
            'pevzner_12': PevznerDiet(
                id='pevzner_12',
                number=12,
                name='Стол №12',
                full_name='Диета №12 (заболевания нервной системы)',
                description='Диета при функциональных заболеваниях нервной системы',
                indications=['Функциональные расстройства нервной системы', 'Неврастения'],
                duration='Периодически',
                principles=[
                    'Исключение возбуждающих продуктов',
                    'Полноценное питание',
                ],
                allowed_products=['Молочные продукты', 'Мясо', 'Крупы', 'Овощи', 'Фрукты'],
                forbidden_products=['Крепкий чай', 'Кофе', 'Алкоголь', 'Острые блюда'],
                cooking_rules='Любые',
                menu_features='4-5 приёмов пищи в день',
            ),
            'pevzner_13': PevznerDiet(
                id='pevzner_13',
                number=13,
                name='Стол №13',
                full_name='Диета №13 (острые инфекционные заболевания)',
                description='Диета при острых инфекционных заболеваниях',
                indications=['ОРВИ', 'Грипп', 'Пневмония', 'Другие инфекции'],
                duration='На период заболевания',
                principles=[
                    'Щадящее питание',
                    'Повышенное употребление жидкости',
                    'Витаминизация',
                ],
                allowed_products=['Лёгкие супы', 'Каши', 'Молочные продукты', 'Овощи', 'Фрукты'],
                forbidden_products=['Жареные блюда', 'Тяжёлая пища'],
                cooking_rules=['Варка', 'Приготовление на пару'],
                menu_features='5-6 приёмов пищи небольшими порциями',
                max_fluid=2.0,
            ),
            'pevzner_14': PevznerDiet(
                id='pevzner_14',
                number=14,
                name='Стол №14',
                full_name='Диета №14 (фосфатурия)',
                description='Диета при фосфатурии и мочекаменной болезни с образованием фосфатных камней',
                indications=['Фосфатурия', 'Фосфатные камни в почках'],
                duration='Длительно',
                principles=[
                    'Кислая реакция мочи',
                    'Ограничение продуктов, богатых кальцием и фосфором',
                ],
                allowed_products=['Мясо', 'Рыба', 'Крупы', 'Макароны', 'Хлеб', 'Яйца'],
                forbidden_products=['Молоко', 'Сыр', 'Творог', 'Овощи', 'Фрукты (кроме клюквы)'],
                cooking_rules='Любые',
                menu_features='4-5 приёмов пищи в день',
            ),
            'pevzner_15': PevznerDiet(
                id='pevzner_15',
                number=15,
                name='Стол №15',
                full_name='Диета №15 (общий стол)',
                description='Полноценное питание для выздоравливающих и при переходе к обычному рациону',
                indications=['Период выздоровления', 'Переход к обычному питанию'],
                duration='Временный переходный период',
                principles=[
                    'Полноценное сбалансированное питание',
                    'Разнообразие рациона',
                ],
                allowed_products='Практически все продукты (кроме острых и тяжёлых)',
                forbidden_products=['Алкоголь', 'Очень острые блюда'],
                cooking_rules='Любые',
                menu_features='4 приёма пищи в день',
            ),
        }

    @classmethod
    def check_product_suitability(cls, product: dict, diet_id: str) -> dict:
        """
        Проверка пригодности продукта для диеты.

        Args:
            product: Словарь с данными о продукте
            diet_id: ID диеты

        Returns:
            Словарь с результатом проверки
        """
        diet = cls.get_diet(diet_id)
        if not diet:
            return {'suitable': True, 'reason': 'Диета не найдена'}

        product_name = product.get('name', '').lower()
        category = product.get('category', '')

        # Проверка на опасные продукты
        dangerous_for = product.get('dangerous_for_diets', [])
        if diet_id in dangerous_for:
            return {
                'suitable': False,
                'reason': f'Продукт {product["name"]} запрещён при диете №{diet.number}'
            }

        # Проверка по категориям
        forbidden_categories = {
            'pevzner_1': ['fried', 'smoked', 'spicy', 'canned'],
            'pevzner_5': ['fried', 'smoked', 'fatty', 'alcohol'],
            'pevzner_7': ['salted', 'canned', 'smoked'],
            'pevzner_8': ['sweets', 'bakery', 'alcohol', 'fatty'],
            'pevzner_9': ['sweets', 'high_gi'],
        }

        forbidden_cats = forbidden_categories.get(diet_id, [])
        if category in forbidden_cats:
            return {
                'suitable': False,
                'reason': f'Продукты категории {category} запрещены'
            }

        return {'suitable': True, 'reason': ''}

    @classmethod
    def get_diet_summary(cls, diet_id: str) -> str:
        """Получение краткой сводки по диете"""
        diet = cls.get_diet(diet_id)
        if not diet:
            return ''

        summary = f"""
## {diet.full_name}

**Показания:** {', '.join(diet.indications)}
**Длительность:** {diet.duration}

### Основные принципы:
{chr(10).join(f'- {p}' for p in diet.principles)}

### Разрешённые продукты:
{', '.join(diet.allowed_products)}

### Запрещённые продукты:
{', '.join(diet.forbidden_products)}

### Правила приготовления:
{', '.join(diet.cooking_rules) if isinstance(diet.cooking_rules, list) else diet.cooking_rules}
"""
        return summary


def get_diet_recommendations(diet_id: str) -> dict:
    """
    Получение рекомендаций по питанию для диеты.

    Args:
        diet_id: ID диеты

    Returns:
        Словарь с рекомендациями
    """
    diet = PevznerDiets.get_diet(diet_id)
    if not diet:
        return {}

    return {
        'name': diet.name,
        'full_name': diet.full_name,
        'description': diet.description,
        'indications': diet.indications,
        'principles': diet.principles,
        'allowed_products': diet.allowed_products,
        'forbidden_products': diet.forbidden_products,
        'cooking_rules': diet.cooking_rules,
        'max_salt': diet.max_salt,
        'max_fluid': diet.max_fluid,
        'temperature_restriction': diet.temperature_restriction,
        'meal_frequency': diet.meal_frequency,
    }
