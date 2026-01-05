# Страница главного дашборда
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QFrame, QGridLayout, QPushButton, QProgressBar,
                              QSpacerItem, QSizePolicy, QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt
from datetime import datetime, date

from config.settings import COLORS
from database.operations import (get_user, get_today_meals, get_user_stats,
                                  get_recipes_by_diet, get_user_achievements)
from core.calculator import get_calorie_category


class DashboardPage(QWidget):
    """Страница главного дашборда"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Верхняя панель с приветствием
        greeting_frame = self.create_greeting_frame()
        layout.addWidget(greeting_frame)

        # Основной контент
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        # Левая колонка - статистика
        left_layout = QVBoxLayout()
        left_layout.setSpacing(16)

        # Карточки статистики
        stats_frame = self.create_stats_cards()
        left_layout.addWidget(stats_frame)

        # График БЖУ
        macro_frame = self.create_macro_chart()
        left_layout.addWidget(macro_frame)

        content_layout.addLayout(left_layout, stretch=1)

        # Правая колонка - рекомендации и активность
        right_layout = QVBoxLayout()
        right_layout.setSpacing(16)

        # Рекомендации рецептов
        recommendations_frame = self.create_recommendations_frame()
        right_layout.addWidget(recommendations_frame, stretch=1)

        # Последние приёмы пищи
        meals_frame = self.create_recent_meals_frame()
        right_layout.addWidget(meals_frame, stretch=1)

        content_layout.addLayout(right_layout, stretch=1)

        layout.addLayout(content_layout)

    def refresh(self):
        """Обновление данных страницы"""
        user = self.main_window.current_user
        if not user:
            return

        # Обновляем приветствие
        hour = datetime.now().hour
        if 6 <= hour < 12:
            greeting = "Доброе утро"
        elif 12 <= hour < 18:
            greeting = "Добрый день"
        elif 18 <= hour < 22:
            greeting = "Добрый вечер"
        else:
            greeting = "Доброй ночи"

        self.greeting_label.setText(f"{greeting}, {user.name}! 👋")

        # Получаем статистику
        stats = get_user_stats(user.id)
        today = stats['today']

        # Обновляем калории
        self.calories_consumed.setText(f"{int(today['calories'])}")
        self.calories_target.setText(f"/ {int(user.target_calories)} ккал")

        # Прогресс калорий
        percent = min(100, (today['calories'] / user.target_calories) * 100) if user.target_calories > 0 else 0
        self.calorie_progress.setValue(int(percent))

        # Обновляем БЖУ
        self.protein_value.setText(f"{int(today['protein'])}г")
        self.fat_value.setText(f"{int(today['fat'])}г")
        self.carbs_value.setText(f"{int(today['carbs'])}г")

        # Обновляем рекомендации
        self.update_recommendations()

        # Обновляем последние приёмы пищи
        self.update_recent_meals()

    def create_greeting_frame(self) -> QFrame:
        """Создание рамки приветствия"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary']},
                    stop:1 {COLORS['primary_light']}
                );
                border-radius: 16px;
                padding: 24px;
            }}
        """)

        layout = QHBoxLayout(frame)

        self.greeting_label = QLabel("Добро пожаловать!")
        self.greeting_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: white;
        """)

        layout.addWidget(self.greeting_label)
        layout.addStretch()

        # Кнопка быстрого добавления
        add_meal_btn = QPushButton("+ Добавить еду")
        add_meal_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                color: {COLORS['primary']};
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['background']};
            }}
        """)
        add_meal_btn.clicked.connect(lambda: self.main_window.navigate_to("diary"))
        layout.addWidget(add_meal_btn)

        return frame

    def create_stats_cards(self) -> QFrame:
        """Создание карточек статистики"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        layout = QGridLayout(frame)
        layout.setSpacing(12)

        # Калории
        calories_card = self.create_stat_card(
            "🔥", "Калории", "0", COLORS['primary'], COLORS['primary_light'] + "30"
        )
        layout.addWidget(calories_card, 0, 0, 1, 2)

        # Белки
        protein_card = self.create_stat_card(
            "🥩", "Белки", "0г", COLORS['error'], COLORS['error_light']
        )
        layout.addWidget(protein_card, 1, 0)

        # Жиры
        fat_card = self.create_stat_card(
            "🥑", "Жиры", "0г", COLORS['warning'], COLORS['warning_light']
        )
        layout.addWidget(fat_card, 1, 1)

        # Углеводы
        carbs_card = self.create_stat_card(
            "🍚", "Углеводы", "0г", COLORS['secondary'], COLORS['secondary_light']
        )
        layout.addWidget(carbs_card, 1, 2)

        return frame

    def create_stat_card(self, icon: str, title: str, value: str,
                         accent_color: str, bg_color: str) -> QFrame:
        """Создание карточки статистики"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 12px;
                padding: 12px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(4)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px;")
        layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 12px;
            color: {COLORS['text_secondary']};
        """)
        layout.addWidget(title_label)

        if title == "Калории":
            self.calories_consumed = QLabel(value)
            self.calories_consumed.setStyleSheet(f"""
                font-size: 28px;
                font-weight: bold;
                color: {accent_color};
            """)
            self.calories_target = QLabel("/ 0 ккал")
            self.calories_target.setStyleSheet(f"""
                font-size: 12px;
                color: {COLORS['text_secondary']};
            """)
            calorie_layout = QVBoxLayout()
            calorie_layout.addWidget(self.calories_consumed)
            calorie_layout.addWidget(self.calories_target)
            layout.addLayout(calorie_layout)

            self.calorie_progress = QProgressBar()
            self.calorie_progress.setStyleSheet(f"""
                QProgressBar {{
                    background-color: white;
                    border: none;
                    border-radius: 6px;
                    height: 8px;
                }}
                QProgressBar::chunk {{
                    background-color: {accent_color};
                    border-radius: 6px;
                }}
            """)
            self.calorie_progress.setValue(0)
            layout.addWidget(self.calorie_progress)
        else:
            value_label = QLabel(value)
            value_label.setStyleSheet(f"""
                font-size: 20px;
                font-weight: bold;
                color: {accent_color};
            """)
            layout.addWidget(value_label)

            if title == "Белки":
                self.protein_value = value_label
            elif title == "Жиры":
                self.fat_value = value_label
            elif title == "Углеводы":
                self.carbs_value = value_label

        return card

    def create_macro_chart(self) -> QFrame:
        """Создание визуализации БЖУ"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        layout = QVBoxLayout(frame)

        title = QLabel("📊 Баланс БЖУ")
        title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)
        layout.addWidget(title)

        layout.addSpacing(12)

        # Прогресс-бары БЖУ
        macro_layout = QHBoxLayout()

        # Белки
        protein_layout = QVBoxLayout()
        protein_layout.addWidget(QLabel("Белки"))
        protein_progress = QProgressBar()
        protein_progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS['error_light']};
                border: none;
                border-radius: 6px;
                height: 10px;
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['error']};
                border-radius: 6px;
            }}
        """)
        protein_progress.setValue(0)
        protein_layout.addWidget(protein_progress)
        self.protein_progress = protein_progress

        # Жиры
        fat_layout = QVBoxLayout()
        fat_layout.addWidget(QLabel("Жиры"))
        fat_progress = QProgressBar()
        fat_progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS['warning_light']};
                border: none;
                border-radius: 6px;
                height: 10px;
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['warning']};
                border-radius: 6px;
            }}
        """)
        fat_progress.setValue(0)
        fat_layout.addWidget(fat_progress)
        self.fat_progress = fat_progress

        # Углеводы
        carbs_layout = QVBoxLayout()
        carbs_layout.addWidget(QLabel("Углеводы"))
        carbs_progress = QProgressBar()
        carbs_progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS['secondary_light']};
                border: none;
                border-radius: 6px;
                height: 10px;
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['secondary']};
                border-radius: 6px;
            }}
        """)
        carbs_progress.setValue(0)
        carbs_layout.addWidget(carbs_progress)
        self.carbs_progress = carbs_progress

        macro_layout.addLayout(protein_layout)
        macro_layout.addLayout(fat_layout)
        macro_layout.addLayout(carbs_layout)

        layout.addLayout(macro_layout)

        return frame

    def create_recommendations_frame(self) -> QFrame:
        """Создание рамки рекомендаций"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        layout = QVBoxLayout(frame)

        title = QLabel("💡 Рекомендации на сегодня")
        title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)
        layout.addWidget(title)

        layout.addSpacing(8)

        self.recommendations_list = QListWidget()
        self.recommendations_list.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                border: none;
            }}
            QListWidget::item {{
                background-color: {COLORS['background']};
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 8px;
            }}
        """)
        layout.addWidget(self.recommendations_list)

        return frame

    def create_recent_meals_frame(self) -> QFrame:
        """Создание рамки последних приёмов пищи"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        layout = QVBoxLayout(frame)

        title = QLabel("🍽️ Сегодняшние приёмы пищи")
        title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)
        layout.addWidget(title)

        layout.addSpacing(8)

        self.meals_list = QListWidget()
        self.meals_list.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                border: none;
            }}
        """)
        layout.addWidget(self.meals_list)

        # Кнопка перехода к дневнику
        view_all_btn = QPushButton("Открыть дневник →")
        view_all_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {COLORS['primary']};
                padding: 8px;
                text-align: left;
            }}
            QPushButton:hover {{
                color: {COLORS['primary_dark']};
            }}
        """)
        view_all_btn.clicked.connect(lambda: self.main_window.navigate_to("diary"))
        layout.addWidget(view_all_btn)

        return frame

    def update_recommendations(self):
        """Обновление рекомендаций"""
        self.recommendations_list.clear()
        user = self.main_window.current_user
        if not user:
            return

        from core.recommender import SimpleRecommender

        # Получаем рекомендации в зависимости от типа диеты
        recipes = SimpleRecommender.get_quick_recommendations(
            diet_type=user.diet_type,
            category='lunch',
            count=3
        )

        for recipe in recipes:
            item = QListWidgetItem()
            item.setText(f"🍳 {recipe.name}\n   {int(recipe.calories)} ккал | Б:{int(recipe.protein)} Ж:{int(recipe.fat)} У:{int(recipe.carbs)}")
            self.recommendations_list.addItem(item)

    def update_recent_meals(self):
        """Обновление списка последних приёмов пищи"""
        self.meals_list.clear()
        user = self.main_window.current_user
        if not user:
            return

        meals = get_today_meals(user.id)

        if not meals:
            item = QListWidgetItem()
            item.setText("Сегодня вы ещё не добавили ни одного приёма пищи")
            self.meals_list.addItem(item)
            return

        meal_icons = {
            'breakfast': '🌅',
            'lunch': '☀️',
            'dinner': '🌙',
            'snack': '🍪',
        }

        for meal in meals[-5:]:  # Показываем последние 5
            icon = meal_icons.get(meal.meal_type, '🍽️')
            item = QListWidgetItem()
            item.setText(f"{icon} {meal.name} - {int(meal.calories)} ккал\n   {meal.meal_time.strftime('%H:%M')}")
            self.meals_list.addItem(item)
