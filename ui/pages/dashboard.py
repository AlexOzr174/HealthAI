# ui/pages/dashboard.py
# Страница главного дашборда
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QGridLayout, QPushButton, QProgressBar,
                             QSpacerItem, QSizePolicy, QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt
from datetime import datetime, date

# Импорт конфигурации (если COLORS нет, создадим fallback)
try:
    from config.settings import COLORS
except ImportError:
    COLORS = {
        'primary': '#3498DB',
        'primary_light': '#5DADE2',
        'primary_dark': '#2980B9',
        'primary_hover': '#2980B9',
        'surface': '#FFFFFF',
        'background': '#F0F2F5',
        'text_primary': '#2C3E50',
        'text_secondary': '#7F8C8D',
        'text_hint': '#95A5A6',
        'error': '#E74C3C',
        'error_light': '#FADBD8',
        'warning': '#F39C12',
        'warning_light': '#FDEBD0',
        'secondary': '#27AE60',
        'secondary_light': '#D5F5E3',
        'border': '#E0E0E0',
        'success': '#27AE60',
        'success_hover': '#229954'
    }

from database.operations import get_today_meals, get_user_stats, get_recipes_by_diet


class DashboardPage(QWidget):
    """Страница главного дашборда"""

    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window  # Сохраняем ссылку на главное окно
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
        # Получаем пользователя из главного окна
        user = self.main_window.current_user if self.main_window else None
        if not user:
            # Если нет пользователя, показываем заглушку
            self.greeting_label.setText("Добро пожаловать в HealthAI!")
            self.calories_consumed.setText("0")
            self.calories_target.setText("/ 0 ккал")
            self.calorie_progress.setValue(0)
            self.protein_value.setText("0г")
            self.fat_value.setText("0г")
            self.carbs_value.setText("0г")
            self.recommendations_list.clear()
            self.meals_list.clear()
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
        today = stats.get('today', {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0})

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

        # Прогресс-бары БЖУ (можно добавить логику на основе целей)
        # Пока оставим заглушки
        self.protein_progress.setValue(min(100, int((today['protein'] / 50) * 100)))  # примерная цель 50г
        self.fat_progress.setValue(min(100, int((today['fat'] / 40) * 100)))  # 40г
        self.carbs_progress.setValue(min(100, int((today['carbs'] / 200) * 100)))  # 200г

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
        # Переход к странице дневника (используем навигацию главного окна)
        if self.main_window:
            add_meal_btn.clicked.connect(lambda: self.main_window.navigate_to(
                type(self.main_window).__dict__.get('DiaryPage')  # небольшой хак, лучше импортировать явно
            ))
        else:
            add_meal_btn.setEnabled(False)
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
        self.protein_progress = QProgressBar()
        self.protein_progress.setStyleSheet(f"""
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
        self.protein_progress.setValue(0)
        protein_layout.addWidget(self.protein_progress)

        # Жиры
        fat_layout = QVBoxLayout()
        fat_layout.addWidget(QLabel("Жиры"))
        self.fat_progress = QProgressBar()
        self.fat_progress.setStyleSheet(f"""
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
        self.fat_progress.setValue(0)
        fat_layout.addWidget(self.fat_progress)

        # Углеводы
        carbs_layout = QVBoxLayout()
        carbs_layout.addWidget(QLabel("Углеводы"))
        self.carbs_progress = QProgressBar()
        self.carbs_progress.setStyleSheet(f"""
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
        self.carbs_progress.setValue(0)
        carbs_layout.addWidget(self.carbs_progress)

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
        if self.main_window:
            # Импортируем DiaryPage для навигации (чтобы избежать циклического импорта, делаем локально)
            try:
                from ui.pages.diary import DiaryPage
                view_all_btn.clicked.connect(lambda: self.main_window.navigate_to(DiaryPage))
            except ImportError:
                view_all_btn.setEnabled(False)
        else:
            view_all_btn.setEnabled(False)
        layout.addWidget(view_all_btn)

        return frame

    def update_recommendations(self):
        """Обновление рекомендаций"""
        self.recommendations_list.clear()
        user = self.main_window.current_user if self.main_window else None
        if not user:
            self.recommendations_list.addItem("Войдите или создайте профиль")
            return

        try:
            from core.recommender import SimpleRecommender
        except ImportError:
            self.recommendations_list.addItem("Модуль рекомендаций недоступен")
            return

        # Получаем рекомендации в зависимости от типа диеты
        recipes = SimpleRecommender.get_quick_recommendations(
            diet_type=user.diet_type,
            category='lunch',
            count=3
        )

        if not recipes:
            self.recommendations_list.addItem("Рекомендации пока отсутствуют")
            return

        for recipe in recipes:
            item = QListWidgetItem()
            item.setText(
                f"🍳 {recipe.name}\n   {int(recipe.calories)} ккал | Б:{int(recipe.protein)} Ж:{int(recipe.fat)} У:{int(recipe.carbs)}")
            self.recommendations_list.addItem(item)

    def update_recent_meals(self):
        """Обновление списка последних приёмов пищи"""
        self.meals_list.clear()
        user = self.main_window.current_user if self.main_window else None
        if not user:
            self.meals_list.addItem("Нет данных о пользователе")
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
