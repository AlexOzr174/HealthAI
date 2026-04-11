# ui/components/dialogs.py
# Диалоговые окна и утилиты
from PyQt6.QtWidgets import (QDialog, QDialogButtonBox, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QComboBox,
                             QListWidget, QListWidgetItem, QFrame, QMessageBox,
                             QGridLayout, QDoubleSpinBox)
from PyQt6.QtCore import Qt

# Импорт конфигурации с fallback
try:
    from config.settings import COLORS, GOALS, ACTIVITY_LEVELS
except ImportError:
    COLORS = {
        'primary': '#3498DB', 'primary_light': '#5DADE2', 'primary_dark': '#2980B9',
        'primary_hover': '#2980B9', 'surface': '#FFFFFF', 'background': '#F0F2F5',
        'text_primary': '#2C3E50', 'text_secondary': '#7F8C8D', 'text_hint': '#95A5A6',
        'error': '#E74C3C', 'error_light': '#FADBD8', 'warning': '#F39C12',
        'warning_light': '#FDEBD0', 'secondary': '#27AE60', 'secondary_light': '#D5F5E3',
        'border': '#E0E0E0', 'success': '#27AE60', 'success_hover': '#229954'
    }
    GOALS = {
        'lose': {'name': 'Похудение'},
        'maintain': {'name': 'Поддержание'},
        'gain': {'name': 'Набор массы'},
        'healthy': {'name': 'Здоровое питание'}
    }
    ACTIVITY_LEVELS = {
        'sedentary': {'name': 'Сидячий'},
        'light': {'name': 'Легкий'},
        'moderate': {'name': 'Средний'},
        'active': {'name': 'Высокий'},
        'very_active': {'name': 'Экстремальный'}
    }

from database.operations import save_user, get_user
from database.models import Recipe
from core.pezvner import PevznerDiets


def show_message(parent, title: str, text: str):
    """Показать информационное сообщение"""
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.exec()


def show_error(parent, title: str, text: str):
    """Показать сообщение об ошибке"""
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.exec()


class SettingsDialog(QDialog):
    """Диалог настроек"""

    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("Настройки профиля")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)

        # Имя
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Имя:"))
        self.name_input = QLineEdit(self.user.name if self.user else "")
        self.name_input.setPlaceholderText("Введите ваше имя")
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Цель
        goal_layout = QHBoxLayout()
        goal_layout.addWidget(QLabel("Цель:"))
        self.goal_combo = QComboBox()
        for goal_id, goal_data in GOALS.items():
            self.goal_combo.addItem(f"{goal_data['name']}", goal_id)
        if self.user and self.user.goal:
            index = self.goal_combo.findData(self.user.goal)
            if index >= 0:
                self.goal_combo.setCurrentIndex(index)
        goal_layout.addWidget(self.goal_combo)
        layout.addLayout(goal_layout)

        # Уровень активности
        activity_layout = QHBoxLayout()
        activity_layout.addWidget(QLabel("Уровень активности:"))
        self.activity_combo = QComboBox()
        for level_id, level_data in ACTIVITY_LEVELS.items():
            self.activity_combo.addItem(level_data['name'], level_id)
        if self.user and self.user.activity_level:
            index = self.activity_combo.findData(self.user.activity_level)
            if index >= 0:
                self.activity_combo.setCurrentIndex(index)
        activity_layout.addWidget(self.activity_combo)
        layout.addLayout(activity_layout)

        # Диета
        diet_layout = QHBoxLayout()
        diet_layout.addWidget(QLabel("Тип диеты:"))
        self.diet_combo = QComboBox()
        self.diet_combo.addItem("Без ограничений", None)
        for diet in PevznerDiets.get_all_diets():
            self.diet_combo.addItem(f"Стол №{diet.number}: {diet.name}", diet.id)
        if self.user and self.user.diet_type:
            index = self.diet_combo.findData(self.user.diet_type)
            if index >= 0:
                self.diet_combo.setCurrentIndex(index)
        diet_layout.addWidget(self.diet_combo)
        layout.addLayout(diet_layout)

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['border']};
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                min-width: 100px;
            }}
            QPushButton:hover {{ background-color: {COLORS['text_hint']}; }}
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        ok_btn = QPushButton("OK")
        ok_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                min-width: 100px;
            }}
            QPushButton:hover {{ background-color: {COLORS['primary_hover']}; }}
        """)
        ok_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)

    def save_settings(self):
        """Сохранение настроек"""
        name = self.name_input.text().strip()
        if not name:
            show_error(self, "Ошибка", "Введите ваше имя")
            return

        user_data = {
            'name': name,
            'goal': self.goal_combo.currentData(),
            'activity_level': self.activity_combo.currentData(),
            'diet_type': self.diet_combo.currentData(),
        }

        # Если пользователя нет (новый пользователь), добавляем обязательные поля
        if not self.user:
            user_data['age'] = 25
            user_data['height'] = 170
            user_data['weight'] = 70
            user_data['gender'] = 'male'
            user_data['bmr'] = 0
            user_data['tdee'] = 0
            user_data['target_calories'] = 0
            user_data['xp'] = 10

        save_user(user_data)
        self.accept()


class RecipeSelectionDialog(QDialog):
    """Диалог выбора рецепта"""

    def __init__(self, diet_type: str = None, parent=None):
        super().__init__(parent)
        self.diet_type = diet_type
        self.selected_recipe = None
        self.setWindowTitle("Выберите блюдо")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)

        # Список рецептов
        self.recipes_list = QListWidget()
        self.recipes_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
            QListWidget::item {{
                padding: 12px;
                border-bottom: 1px solid {COLORS['border']};
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['primary_light']};
            }}
        """)
        self.recipes_list.itemClicked.connect(self.select_recipe)
        layout.addWidget(self.recipes_list)

        # Информация о рецепте
        self.recipe_info = QLabel("Выберите блюдо из списка")
        self.recipe_info.setStyleSheet(f"""
            font-size: 14px;
            padding: 12px;
            background-color: {COLORS['background']};
            border-radius: 8px;
        """)
        layout.addWidget(self.recipe_info)

        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept_selection)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.load_recipes()

    def load_recipes(self):
        """Загрузка рецептов"""
        from database.operations import get_all_recipes, get_recipes_by_diet

        if self.diet_type:
            recipes = get_recipes_by_diet(self.diet_type)
        else:
            recipes = get_all_recipes()

        for recipe in recipes:
            item = QListWidgetItem()
            item.setText(f"{recipe.name}\n   🔥 {int(recipe.calories)} ккал | ⏱️ {recipe.prep_time} мин")
            item.setData(Qt.ItemDataRole.UserRole, recipe)
            self.recipes_list.addItem(item)

    def select_recipe(self, item):
        """Выбор рецепта"""
        recipe = item.data(Qt.ItemDataRole.UserRole)
        self.selected_recipe = recipe

        info = f"""
<b>{recipe.name}</b><br>
Калории: {int(recipe.calories)} ккал<br>
Белки: {int(recipe.protein)}г | Жиры: {int(recipe.fat)}г | Углеводы: {int(recipe.carbs)}г<br>
Время приготовления: {recipe.prep_time} мин<br>
{recipe.description or ''}
"""
        self.recipe_info.setText(info)

    def accept_selection(self):
        """Подтверждение выбора"""
        if self.selected_recipe:
            self.accept()

    def get_selected_recipe(self) -> Recipe:
        """Получение выбранного рецепта"""
        return self.selected_recipe
