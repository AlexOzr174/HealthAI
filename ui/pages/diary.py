# Страница дневника питания
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QFrame, QPushButton, QLineEdit, QComboBox,
                              QListWidget, QListWidgetItem, QGridLayout,
                              QDoubleSpinBox, QSpacerItem, QSizePolicy,
                              QDialog, QDialogButtonBox, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal
from datetime import datetime, date

from config.settings import COLORS
from database.operations import (get_today_meals, add_meal, delete_meal,
                                  search_products, get_user)
from database.models import Meal


class AddMealDialog(QDialog):
    """Диалог добавления приёма пищи"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить приём пищи")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса диалога"""
        layout = QVBoxLayout(self)

        # Тип приёма пищи
        layout.addWidget(QLabel("Тип приёма пищи:"))
        self.meal_type_combo = QComboBox()
        meal_types = [
            ("Завтрак", "breakfast"),
            ("Обед", "lunch"),
            ("Ужин", "dinner"),
            ("Перекус", "snack"),
        ]
        for meal_name, meal_id in meal_types:
            self.meal_type_combo.addItem(meal_name, meal_id)
        layout.addWidget(self.meal_type_combo)

        layout.addSpacing(12)

        # Поиск продукта
        layout.addWidget(QLabel("Продукт или блюдо:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Начните вводить название...")
        self.search_input.textChanged.connect(self.search_products)
        layout.addWidget(self.search_input)

        # Список найденных продуктов
        self.products_list = QListWidget()
        self.products_list.setMaximumHeight(150)
        self.products_list.itemClicked.connect(self.select_product)
        layout.addWidget(self.products_list)

        layout.addSpacing(12)

        # Выбранный продукт
        self.selected_product_label = QLabel("Выбранный продукт: -")
        layout.addWidget(self.selected_product_label)

        layout.addSpacing(12)

        # Количество
        amount_layout = QHBoxLayout()
        amount_layout.addWidget(QLabel("Количество (г):"))
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(1, 5000)
        self.amount_spin.setValue(100)
        self.amount_spin.setSuffix(" г")
        amount_layout.addWidget(self.amount_spin)
        layout.addLayout(amount_layout)

        # Информация о калориях
        self.calorie_info = QLabel("Калории: 0 ккал")
        self.calorie_info.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {COLORS['primary']};
        """)
        layout.addWidget(self.calorie_info)

        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.selected_product = None

    def search_products(self, query):
        """Поиск продуктов"""
        if len(query) < 2:
            self.products_list.clear()
            return

        products = search_products(query, limit=10)
        self.products_list.clear()

        for product in products:
            item = QListWidgetItem()
            item.setText(f"{product.name} ({int(product.calories)} ккал/100г)")
            item.setData(Qt.ItemDataRole.UserRole, product)
            self.products_list.addItem(item)

    def select_product(self, item):
        """Выбор продукта"""
        self.selected_product = item.data(Qt.ItemDataRole.UserRole)
        self.selected_product_label.setText(
            f"Выбранный продукт: {self.selected_product.name}"
        )
        self.update_calorie_info()

    def update_calorie_info(self):
        """Обновление информации о калориях"""
        if not self.selected_product:
            return

        amount = self.amount_spin.value()
        factor = amount / 100
        calories = self.selected_product.calories * factor

        self.calorie_info.setText(
            f"Калории: {int(calories)} ккал | "
            f"Б: {int(self.selected_product.protein * factor)}г "
            f"Ж: {int(self.selected_product.fat * factor)}г "
            f"У: {int(self.selected_product.carbs * factor)}г"
        )

    def get_meal_data(self) -> dict:
        """Получение данных о приёме пищи"""
        if not self.selected_product:
            return None

        amount = self.amount_spin.value()
        factor = amount / 100

        return {
            'meal_type': self.meal_type_combo.currentData(),
            'name': self.selected_product.name,
            'amount': amount,
            'calories': self.selected_product.calories * factor,
            'protein': self.selected_product.protein * factor,
            'fat': self.selected_product.fat * factor,
            'carbs': self.selected_product.carbs * factor,
        }


class DiaryPage(QWidget):
    """Страница дневника питания"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.current_date = date.today()
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Панель выбора даты
        date_frame = self.create_date_selector()
        layout.addWidget(date_frame)

        # Статистика за день
        stats_frame = self.create_day_stats()
        layout.addWidget(stats_frame)

        # Список приёмов пищи
        meals_frame = self.create_meals_list()
        layout.addWidget(meals_frame, stretch=1)

    def refresh(self):
        """Обновление данных страницы"""
        self.update_date()
        self.update_meals_list()
        self.update_stats()

    def create_date_selector(self) -> QFrame:
        """Создание выбора даты"""
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
        prev_btn.clicked.connect(self.prev_day)
        layout.addWidget(prev_btn)

        # Текущая дата
        self.date_label = QLabel()
        self.date_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)
        layout.addWidget(self.date_label, alignment=Qt.AlignmentFlag.AlignCenter)

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
        next_btn.clicked.connect(self.next_day)
        layout.addWidget(next_btn)

        layout.addStretch()

        # Кнопка "Сегодня"
        today_btn = QPushButton("Сегодня")
        today_btn.clicked.connect(self.go_to_today)
        layout.addWidget(today_btn)

        # Кнопка добавления
        add_btn = QPushButton("+ Добавить")
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{ background-color: {COLORS['primary_hover']}; }}
        """)
        add_btn.clicked.connect(self.add_meal)
        layout.addWidget(add_btn)

        return frame

    def create_day_stats(self) -> QFrame:
        """Создание статистики за день"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary']},
                    stop:1 {COLORS['primary_light']}
                );
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        layout = QHBoxLayout(frame)

        # Калории
        calories_layout = QVBoxLayout()
        calories_layout.setSpacing(4)

        calories_title = QLabel("Калории")
        calories_title.setStyleSheet("color: white; font-size: 14px;")

        self.day_calories = QLabel("0")
        self.day_calories.setStyleSheet("""
            color: white;
            font-size: 32px;
            font-weight: bold;
        """)

        self.day_calories_target = QLabel("/ 0 ккал")
        self.day_calories_target.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 14px;")

        calories_layout.addWidget(calories_title)
        calories_layout.addWidget(self.day_calories)
        calories_layout.addWidget(self.day_calories_target)
        layout.addLayout(calories_layout)

        layout.addStretch()

        # БЖУ
        macros_layout = QHBoxLayout()
        macros_layout.setSpacing(24)

        macro_items = [
            ("🥩", "Белки", "protein"),
            ("🥑", "Жиры", "fat"),
            ("🍚", "Углеводы", "carbs"),
        ]

        for icon, name, attr in macro_items:
            macro_layout = QVBoxLayout()
            macro_layout.setSpacing(2)

            macro_icon = QLabel(icon)
            macro_icon.setStyleSheet("font-size: 20px;")

            macro_value = QLabel("0г")
            macro_value.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
            setattr(self, f"day_{attr}_label", macro_value)

            macro_name = QLabel(name)
            macro_name.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 12px;")

            macro_layout.addWidget(macro_icon)
            macro_layout.addWidget(macro_value)
            macro_layout.addWidget(macro_name)
            macros_layout.addLayout(macro_layout)

        layout.addLayout(macros_layout)

        return frame

    def create_meals_list(self) -> QFrame:
        """Создание списка приёмов пищи"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        layout = QVBoxLayout(frame)

        title = QLabel("🍽️ Приёмы пищи")
        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)
        layout.addWidget(title)

        layout.addSpacing(12)

        # Список по категориям
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
        """)

        meals_container = QWidget()
        self.meals_layout = QVBoxLayout(meals_container)
        self.meals_layout.setSpacing(12)

        scroll.setWidget(meals_container)
        layout.addWidget(scroll)

        return frame

    def update_date(self):
        """Обновление отображения даты"""
        if self.current_date == date.today():
            self.date_label.setText("Сегодня")
        else:
            self.date_label.setText(self.current_date.strftime("%d %B %Y"))

    def update_meals_list(self):
        """Обновление списка приёмов пищи"""
        # Очищаем текущий список
        while self.meals_layout.count():
            item = self.meals_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        user = self.main_window.current_user
        if not user:
            return

        meals = get_today_meals(user.id, self.current_date)

        # Группируем по типам
        meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
        meal_names = {'breakfast': '🌅 Завтрак', 'lunch': '☀️ Обед', 'dinner': '🌙 Ужин', 'snack': '🍪 Перекус'}

        for meal_type in meal_types:
            type_meals = [m for m in meals if m.meal_type == meal_type]

            # Заголовок типа
            type_frame = QFrame()
            type_layout = QVBoxLayout(type_frame)

            type_title = QLabel(meal_names[meal_type])
            type_title.setStyleSheet(f"""
                font-size: 14px;
                font-weight: bold;
                color: {COLORS['primary_dark']};
            """)
            type_layout.addWidget(type_title)

            # Продукты этого типа
            for meal in type_meals:
                meal_item = self.create_meal_item(meal)
                type_layout.addWidget(meal_item)

            if type_meals:
                self.meals_layout.addWidget(type_frame)

    def create_meal_item(self, meal: Meal) -> QFrame:
        """Создание элемента приёма пищи"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['background']};
                border-radius: 8px;
                padding: 12px;
            }}
        """)

        layout = QHBoxLayout(frame)

        # Информация о продукте
        info_layout = QVBoxLayout()

        name_label = QLabel(meal.name)
        name_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 600;
            color: {COLORS['text_primary']};
        """)
        info_layout.addWidget(name_label)

        macros_label = QLabel(
            f"Б: {int(meal.protein)}г | Ж: {int(meal.fat)}г | У: {int(meal.carbs)}г"
        )
        macros_label.setStyleSheet(f"""
            font-size: 12px;
            color: {COLORS['text_secondary']};
        """)
        info_layout.addWidget(macros_label)

        layout.addLayout(info_layout)

        layout.addStretch()

        # Калории
        calories_label = QLabel(f"{int(meal.calories)} ккал")
        calories_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {COLORS['primary']};
        """)
        layout.addWidget(calories_label)

        # Время
        time_label = QLabel(meal.meal_time.strftime('%H:%M'))
        time_label.setStyleSheet(f"""
            font-size: 12px;
            color: {COLORS['text_hint']};
        """)
        layout.addWidget(time_label)

        # Кнопка удаления
        delete_btn = QPushButton("×")
        delete_btn.setFixedSize(24, 24)
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['error_light']};
                color: {COLORS['error']};
                border: none;
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['error']};
                color: white;
            }}
        """)
        delete_btn.clicked.connect(lambda: self.delete_meal(meal))
        layout.addWidget(delete_btn)

        return frame

    def update_stats(self):
        """Обновление статистики"""
        user = self.main_window.current_user
        if not user:
            return

        meals = get_today_meals(user.id, self.current_date)

        totals = {
            'calories': sum(m.calories for m in meals),
            'protein': sum(m.protein for m in meals),
            'fat': sum(m.fat for m in meals),
            'carbs': sum(m.carbs for m in meals),
        }

        self.day_calories.setText(f"{int(totals['calories'])}")
        self.day_calories_target.setText(f"/ {int(user.target_calories)} ккал")

        self.day_protein_label.setText(f"{int(totals['protein'])}г")
        self.day_fat_label.setText(f"{int(totals['fat'])}г")
        self.day_carbs_label.setText(f"{int(totals['carbs'])}г")

    def add_meal(self):
        """Добавление приёма пищи"""
        user = self.main_window.current_user
        if not user:
            return

        dialog = AddMealDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            meal_data = dialog.get_meal_data()
            if meal_data:
                add_meal(user.id, meal_data)

                # Разблокируем достижение за первый приём пищи
                from database.operations import unlock_achievement
                unlock_achievement(user.id, 'first_entry')

                self.refresh()
                self.main_window.update_calorie_display()

    def delete_meal(self, meal: Meal):
        """Удаление приёма пищи"""
        delete_meal(meal.id)
        self.refresh()
        self.main_window.update_calorie_display()

    def prev_day(self):
        """Переход к предыдущему дню"""
        self.current_date = self.current_date.replace(day=self.current_date.day - 1)
        self.refresh()

    def next_day(self):
        """Переход к следующему дню"""
        if self.current_date < date.today():
            self.current_date = self.current_date.replace(day=self.current_date.day + 1)
            self.refresh()

    def go_to_today(self):
        """Переход к сегодняшнему дню"""
        self.current_date = date.today()
        self.refresh()
