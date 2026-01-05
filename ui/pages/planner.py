# Страница планировщика питания
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QFrame, QPushButton, QComboBox, QGridLayout,
                              QListWidget, QListWidgetItem, QScrollArea,
                              QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt
from datetime import date, timedelta
from typing import List

from config.settings import COLORS
from database.operations import (get_user, save_weekly_plan, get_weekly_plan,
                                  get_recipes_by_diet, get_all_recipes,
                                  get_weekly_shopping_list)
from database.models import Recipe
from core.recommender import SimpleRecommender


class PlannerPage(QWidget):
    """Страница планировщика питания на неделю"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.current_week_start = self.get_week_start(date.today())
        # Инициализация словарей для хранения компонентов
        self.day_meals = {}
        self.day_totals = {}
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Панель управления неделей
        week_frame = self.create_week_selector()
        layout.addWidget(week_frame)

        # Основной контент
        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)

        # План питания
        plan_frame = self.create_meal_plan()
        content_layout.addWidget(plan_frame, stretch=2)

        # Список покупок
        shopping_frame = self.create_shopping_list()
        content_layout.addWidget(shopping_frame, stretch=1)

        layout.addLayout(content_layout)

    def refresh(self):
        """Обновление данных страницы"""
        self.update_week_label()
        self.update_meal_plan()
        self.update_shopping_list()

    def get_week_start(self, d: date) -> date:
        """Получение понедельника недели"""
        return d - timedelta(days=d.weekday())

    def create_week_selector(self) -> QFrame:
        """Создание выбора недели"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: 12px;
                padding: 12px;
            }}
        """)

        layout = QHBoxLayout(frame)

        # Кнопка назад
        prev_btn = QPushButton("◀")
        prev_btn.setFixedSize(36, 36)
        prev_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['background']};
                border: none;
                border-radius: 8px;
                font-size: 16px;
            }}
            QPushButton:hover {{ background-color: {COLORS['border']}; }}
        """)
        prev_btn.clicked.connect(self.prev_week)
        layout.addWidget(prev_btn)

        # Текущая неделя
        self.week_label = QLabel()
        self.week_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)
        layout.addWidget(self.week_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Кнопка вперёд
        next_btn = QPushButton("▶")
        next_btn.setFixedSize(36, 36)
        next_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['background']};
                border: none;
                border-radius: 8px;
                font-size: 16px;
            }}
            QPushButton:hover {{ background-color: {COLORS['border']}; }}
        """)
        next_btn.clicked.connect(self.next_week)
        layout.addWidget(next_btn)

        layout.addStretch()

        # Текущая неделя
        today_btn = QPushButton("Эта неделя")
        today_btn.clicked.connect(self.go_to_current_week)
        layout.addWidget(today_btn)

        # Автозаполнение
        auto_fill_btn = QPushButton("✨ Автозаполнение")
        auto_fill_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['secondary']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{ background-color: #F4511E; }}
        """)
        auto_fill_btn.clicked.connect(self.auto_fill_week)
        layout.addWidget(auto_fill_btn)

        # Сохранить
        save_btn = QPushButton("💾 Сохранить")
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{ background-color: {COLORS['primary_hover']}; }}
        """)
        save_btn.clicked.connect(self.save_plan)
        layout.addWidget(save_btn)

        return frame

    def create_meal_plan(self) -> QFrame:
        """Создание сетки плана питания"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        layout = QVBoxLayout(frame)

        title = QLabel("📅 План питания на неделю")
        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)
        layout.addWidget(title)

        layout.addSpacing(12)

        # Сетка дней недели
        self.week_grid = QGridLayout()
        self.week_grid.setSpacing(8)

        # Дни недели
        days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
        self.day_frames = {}

        for i, day in enumerate(days):
            day_frame = self.create_day_card(i, day)
            self.week_grid.addWidget(day_frame, 0, i)
            self.day_frames[i] = day_frame

        layout.addLayout(self.week_grid)

        return frame

    def create_day_card(self, day_num: int, day_name: str) -> QFrame:
        """Создание карточки дня"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['background']};
                border-radius: 8px;
                padding: 8px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(4)

        # Заголовок дня
        day_label = QLabel(day_name[:3])
        day_label.setStyleSheet(f"""
            font-size: 12px;
            font-weight: bold;
            color: {COLORS['primary']};
        """)
        day_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(day_label)

        # Приёмы пищи
        meal_types = [
            ('breakfast', '🌅', 'Завтрак'),
            ('lunch', '☀️', 'Обед'),
            ('dinner', '🌙', 'Ужин'),
            ('snack', '🍪', 'Перекус'),
        ]

        self.day_meals[day_num] = {}

        for meal_type, icon, name in meal_types:
            meal_frame = self.create_meal_slot(day_num, meal_type, icon)
            layout.addWidget(meal_frame)
            self.day_meals[day_num][meal_type] = meal_frame

        # Итоги дня
        totals_label = QLabel("0 ккал")
        totals_label.setStyleSheet(f"""
            font-size: 11px;
            color: {COLORS['text_secondary']};
        """)
        totals_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.day_totals[day_num] = totals_label
        layout.addWidget(totals_label)

        return card

    def create_meal_slot(self, day_num: int, meal_type: str,
                         icon: str) -> QFrame:
        """Создание слота приёма пищи"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: 4px;
                padding: 4px;
                min-height: 40px;
            }}
            QFrame:hover {{
                border: 1px solid {COLORS['primary_light']};
            }}
        """)

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(4, 2, 4, 2)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 12px;")
        layout.addWidget(icon_label)

        meal_label = QLabel("Нажмите +")
        meal_label.setStyleSheet(f"""
            font-size: 10px;
            color: {COLORS['text_hint']};
        """)
        meal_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(meal_label, stretch=1)

        add_btn = QPushButton("+")
        add_btn.setFixedSize(18, 18)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }}
            QPushButton:hover {{ background-color: {COLORS['primary_hover']}; }}
        """)
        add_btn.clicked.connect(lambda: self.add_meal_to_day(day_num, meal_type))
        layout.addWidget(add_btn)

        return frame

    def create_shopping_list(self) -> QFrame:
        """Создание списка покупок"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        layout = QVBoxLayout(frame)

        title = QLabel("🛒 Список покупок")
        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)
        layout.addWidget(title)

        layout.addSpacing(8)

        self.shopping_list = QListWidget()
        self.shopping_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {COLORS['background']};
                border: none;
                border-radius: 8px;
                padding: 8px;
            }}
        """)
        layout.addWidget(self.shopping_list)

        # Итоговая стоимость
        self.total_cost = QLabel("Итого: 0 ₽")
        self.total_cost.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {COLORS['primary']};
            padding: 8px;
            background-color: {COLORS['primary_light']}30;
            border-radius: 8px;
        """)
        self.total_cost.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.total_cost)

        # Экспорт
        export_btn = QPushButton("📄 Экспорт в файл")
        export_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['background']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px;
            }}
            QPushButton:hover {{ background-color: {COLORS['border']}; }}
        """)
        export_btn.clicked.connect(self.export_shopping_list)
        layout.addWidget(export_btn)

        return frame

    def update_week_label(self):
        """Обновление отображения недели"""
        week_end = self.current_week_start + timedelta(days=6)
        self.week_label.setText(
            f"{self.current_week_start.strftime('%d.%m')} - {week_end.strftime('%d.%m')}"
        )

    def update_meal_plan(self):
        """Обновление плана питания"""
        user = self.main_window.current_user
        if not user:
            return

        plan = get_weekly_plan(user.id, self.current_week_start.strftime('%Y-%m-%d'))

        # Сбрасываем все слоты
        for day_num in range(7):
            for meal_type in ['breakfast', 'lunch', 'dinner', 'snack']:
                slot = self.day_meals[day_num][meal_type]
                layout = slot.layout()
                meal_label = layout.itemAt(1).widget()
                meal_label.setText("Нажмите +")
                meal_label.setStyleSheet(f"""
                    font-size: 10px;
                    color: {COLORS['text_hint']};
                """)

        # Заполняем из сохранённого плана
        day_totals = {i: 0 for i in range(7)}

        for item in plan:
            slot = self.day_meals[item.day_of_week][item.meal_type]
            layout = slot.layout()
            meal_label = layout.itemAt(1).widget()

            if item.custom_meal:
                meal_label.setText(item.custom_meal[:15] + "..." if len(item.custom_meal) > 15 else item.custom_meal)
            else:
                meal_label.setText("Рецепт")

            meal_label.setStyleSheet(f"""
                font-size: 10px;
                color: {COLORS['text_primary']};
                font-weight: 600;
            """)

            day_totals[item.day_of_week] += item.calories

        # Обновляем итоги
        for day_num in range(7):
            self.day_totals[day_num].setText(f"{int(day_totals[day_num])} ккал")

    def update_shopping_list(self):
        """Обновление списка покупок"""
        user = self.main_window.current_user
        if not user:
            return

        shopping = get_weekly_shopping_list(user.id, self.current_week_start.strftime('%Y-%m-%d'))

        self.shopping_list.clear()
        total = 0

        for item in shopping:
            item_widget = QListWidgetItem()
            item_widget.setText(f"• {item['product']}: {int(item['amount'])}г ({item['price']} ₽)")
            self.shopping_list.addItem(item_widget)
            total += item['price']

        self.total_cost.setText(f"Итого: {int(total)} ₽")

    def add_meal_to_day(self, day_num: int, meal_type: str):
        """Добавление блюда в конкретный день"""
        from ui.components.dialogs import RecipeSelectionDialog

        user = self.main_window.current_user
        if not user:
            return

        dialog = RecipeSelectionDialog(user.diet_type, self)
        if dialog.exec() == 1:
            recipe = dialog.get_selected_recipe()
            if recipe:
                self.set_meal_for_day(day_num, meal_type, recipe)

    def set_meal_for_day(self, day_num: int, meal_type: str, recipe: Recipe):
        """Установка блюда на день"""
        slot = self.day_meals[day_num][meal_type]
        layout = slot.layout()
        meal_label = layout.itemAt(1).widget()

        meal_label.setText(recipe.name[:20] + "..." if len(recipe.name) > 20 else recipe.name)
        meal_label.setStyleSheet(f"""
            font-size: 10px;
            color: {COLORS['text_primary']};
            font-weight: 600;
        """)

        # Сохраняем данные в атрибуты кнопки для экспорта
        add_btn = layout.itemAt(2).widget()
        add_btn.setProperty('recipe_id', recipe.id)
        add_btn.setProperty('calories', recipe.calories)

    def auto_fill_week(self):
        """Автозаполнение недели"""
        user = self.main_window.current_user
        if not user:
            return

        # Получаем рецепты для диеты пользователя
        recipes = SimpleRecommender.get_quick_recommendations(
            diet_type=user.diet_type,
            count=50
        )

        if not recipes:
            return

        # Распределяем рецепты по дням
        meal_types = ['breakfast', 'lunch', 'dinner', 'snack']

        for day_num in range(7):
            for meal_type in meal_types:
                # Фильтруем рецепты по типу приёма пищи
                type_recipes = [r for r in recipes if r.category in [meal_type, 'snack'] or
                               (meal_type == 'snack' and r.category in ['breakfast', 'snack'])]

                if type_recipes:
                    # Выбираем случайный рецепт
                    recipe = type_recipes[day_num % len(type_recipes)]
                    self.set_meal_for_day(day_num, meal_type, recipe)

    def save_plan(self):
        """Сохранение плана"""
        user = self.main_window.current_user
        if not user:
            return

        plan_data = []
        week_start = self.current_week_start.strftime('%Y-%m-%d')

        for day_num in range(7):
            for meal_type in ['breakfast', 'lunch', 'dinner', 'snack']:
                slot = self.day_meals[day_num][meal_type]
                layout = slot.layout()
                add_btn = layout.itemAt(2).widget()

                recipe_id = add_btn.property('recipe_id')
                calories = add_btn.property('calories')

                if recipe_id:
                    plan_data.append({
                        'day_of_week': day_num,
                        'meal_type': meal_type,
                        'recipe_id': recipe_id,
                        'calories': calories or 0,
                        'custom_meal': None,
                    })

        save_weekly_plan(user.id, week_start, plan_data)

        # Разблокируем достижение
        from database.operations import unlock_achievement
        unlock_achievement(user.id, 'meal_planner')

        from ui.components.dialogs import show_message
        show_message(self, "План сохранён", "Ваш план питания успешно сохранён!")

    def prev_week(self):
        """Предыдущая неделя"""
        self.current_week_start = self.current_week_start - timedelta(days=7)
        self.refresh()

    def next_week(self):
        """Следующая неделя"""
        self.current_week_start = self.current_week_start + timedelta(days=7)
        self.refresh()

    def go_to_current_week(self):
        """Переход к текущей неделе"""
        self.current_week_start = self.get_week_start(date.today())
        self.refresh()

    def export_shopping_list(self):
        """Экспорт списка покупок в файл"""
        user = self.main_window.current_user
        if not user:
            return

        shopping = get_weekly_shopping_list(user.id, self.current_week_start.strftime('%Y-%m-%d'))

        if not shopping:
            from ui.components.dialogs import show_message
            show_message(self, "Список пуст", "Сначала составьте план питания")
            return

        content = f"Список покупок на неделю {self.current_week_start.strftime('%d.%m.%Y')}\n"
        content += "=" * 50 + "\n\n"

        total = 0
        for item in shopping:
            content += f"• {item['product']}: {int(item['amount'])}г - {item['price']} ₽\n"
            total += item['price']

        content += "\n" + "=" * 50 + "\n"
        content += f"Итого: {int(total)} ₽"

        # Запись в файл
        from pathlib import Path
        desktop = Path.home() / "Desktop"
        file_path = desktop / f"shopping_list_{self.current_week_start.strftime('%Y%m%d')}.txt"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        from ui.components.dialogs import show_message
        show_message(self, "Файл сохранён", f"Список покупок сохранён в:\n{file_path}")
