"""
Русские названия внутренних классов еды для карточек UI (без сети).
Совпадает с ключами class_labels / nutrition_database в food_recognition.
"""

from __future__ import annotations

DISPLAY_NAME_RU: dict[str, str] = {
    "apple": "Яблоко",
    "banana": "Банан",
    "orange": "Апельсин",
    "grapes": "Виноград",
    "strawberry": "Клубника",
    "chicken_breast": "Куриная грудка",
    "beef_steak": "Говяжий стейк",
    "pork_chop": "Свиная отбивная",
    "salmon": "Лосось",
    "tuna": "Тунец",
    "rice_white": "Белый рис",
    "rice_brown": "Бурый рис",
    "pasta": "Паста",
    "bread_white": "Белый хлеб",
    "bread_whole": "Цельнозерновой хлеб",
    "egg_boiled": "Яйцо варёное",
    "egg_fried": "Яичница",
    "cheese": "Сыр",
    "milk": "Молоко",
    "yogurt": "Йогурт",
    "broccoli": "Брокколи",
    "carrot": "Морковь",
    "tomato": "Помидор",
    "cucumber": "Огурец",
    "lettuce": "Салат (латук)",
    "spinach": "Шпинат",
    "potato": "Картофель",
    "sweet_potato": "Батат",
    "avocado": "Авокадо",
    "nuts_mix": "Орехи (ассорти)",
    "almonds": "Миндаль",
    "oatmeal": "Овсянка",
    "cereal": "Хлопья / завтрак",
    "pancake": "Блины",
    "waffle": "Вафли",
    "pizza": "Пицца",
    "burger": "Бургер",
    "fries": "Картофель фри",
    "salad_caesar": "Салат Цезарь",
    "salad_greek": "Греческий салат",
    "soup": "Суп",
    "ice_cream": "Мороженое",
    "cake": "Торт",
    "cookie": "Печенье",
    "chocolate": "Шоколад",
    "donut": "Пончик",
    "unknown": "Продукт",
}


def food_name_ru(food_class: str) -> str:
    key = (food_class or "").strip().lower()
    if not key:
        return "Продукт"
    return DISPLAY_NAME_RU.get(key, food_class.replace("_", " ").title())
