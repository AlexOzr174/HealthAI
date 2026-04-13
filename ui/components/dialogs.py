# ui/components/dialogs.py
# Диалоговые окна и утилиты
from PyQt6.QtWidgets import (QDialog, QDialogButtonBox, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QComboBox,
                             QListWidget, QListWidgetItem, QFrame, QMessageBox,
                             QGridLayout, QDoubleSpinBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette


def _apply_msgbox_contrast(msg: QMessageBox) -> None:
    """Фикс контраста: Qt иногда красит текст предупреждений тёмно-красным на тёмном фоне."""
    msg.setTextFormat(Qt.TextFormat.PlainText)


class StyledMessageBox(QMessageBox):
    """
    QMessageBox с явным светлым/тёмным оформлением: на macOS глобальный QSS иногда не
    подхватывается, из‑за чего остаётся тёмный фон и тёмный текст.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def apply_readable_style(self) -> None:
        try:
            from ui.styles import THEME_NAME
        except ImportError:
            THEME_NAME = "light"
        dark = THEME_NAME == "dark"
        bg = QColor("#2E2E2E") if dark else QColor("#FFFFFF")
        fg = QColor("#ECEFF1") if dark else QColor("#1a1a1a")
        btn_face = QColor("#B3E5FC") if dark else QColor("#E8EDF2")

        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, bg)
        pal.setColor(QPalette.ColorRole.Base, bg)
        pal.setColor(QPalette.ColorRole.WindowText, fg)
        pal.setColor(QPalette.ColorRole.Text, fg)
        pal.setColor(QPalette.ColorRole.Button, btn_face)
        pal.setColor(QPalette.ColorRole.ButtonText, QColor("#1a1a1a"))
        self.setPalette(pal)

        qss_bg = bg.name()
        qss_fg = fg.name()
        qss_btn = btn_face.name()
        self.setStyleSheet(
            f"""
            QMessageBox {{ background-color: {qss_bg}; }}
            QMessageBox QLabel {{ color: {qss_fg}; background-color: {qss_bg}; }}
            QMessageBox QPushButton {{
                color: #1a1a1a;
                background-color: {qss_btn};
                border: 2px solid #34495e;
                border-radius: 8px;
                min-width: 100px;
                min-height: 36px;
                padding: 6px 16px;
                font-weight: 600;
            }}
            QMessageBox QPushButton:hover {{ background-color: #D6EAF8; }}
            QMessageBox QPushButton:pressed {{ padding-top: 8px; padding-bottom: 4px; }}
            """
        )

        for lab in self.findChildren(QLabel):
            lab.setAutoFillBackground(True)
            lab.setPalette(pal)
            lab.setForegroundRole(QPalette.ColorRole.WindowText)
            lab.setStyleSheet(f"color: {qss_fg}; background-color: {qss_bg};")

        for btn in self.findChildren(QPushButton):
            btn.setPalette(pal)
            btn.setStyleSheet(
                f"color: #1a1a1a; background-color: {qss_btn}; border: 2px solid #2C3E50; "
                "border-radius: 8px; min-height: 34px; padding: 6px 16px; font-weight: 600;"
            )

    def showEvent(self, event):
        super().showEvent(event)
        self.apply_readable_style()

    def exec(self) -> int:
        self.apply_readable_style()
        ret = super().exec()
        return ret

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

from ui.dialog_chrome import STANDARD_LIGHT_FORM_DIALOG_QSS, apply_light_dialog_chrome

from ui.components.press_feedback import attach_press_flash


def show_message(parent, title: str, text: str):
    """Показать информационное сообщение"""
    msg = StyledMessageBox(parent)
    _apply_msgbox_contrast(msg)
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.exec()


def show_error(parent, title: str, text: str):
    """Показать сообщение об ошибке"""
    msg = StyledMessageBox(parent)
    _apply_msgbox_contrast(msg)
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.exec()


def show_warning(parent, title: str, text: str):
    """Предупреждение с читаемым текстом (без «невидимого» красного на тёмном фоне)."""
    msg = StyledMessageBox(parent)
    _apply_msgbox_contrast(msg)
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.exec()


def show_rich_message(
    parent,
    title: str,
    html: str,
    icon: QMessageBox.Icon = QMessageBox.Icon.Information,
) -> None:
    """Сообщение с разметкой RichText (как «О программе»), в том же StyledMessageBox."""
    msg = StyledMessageBox(parent)
    msg.setTextFormat(Qt.TextFormat.RichText)
    msg.setIcon(icon)
    msg.setWindowTitle(title)
    msg.setText(html)
    msg.exec()


class SettingsDialog(QDialog):
    """Диалог настроек"""

    def __init__(self, user, parent=None):
        super().__init__(parent)
        apply_light_dialog_chrome(self)
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
                background-color: {COLORS['surface']};
                color: #1a1a1a;
                border: 2px solid #2C3E50;
                border-radius: 8px;
                padding: 10px 24px;
                min-width: 100px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: {COLORS['border']}; }}
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        ok_btn = QPushButton("OK")
        ok_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFFFFF;
                color: #1a1a1a;
                border: 2px solid #1a1a1a;
                border-radius: 8px;
                padding: 10px 24px;
                min-width: 100px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #F0F2F5; }}
        """)
        ok_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)

        attach_press_flash(cancel_btn)
        attach_press_flash(ok_btn)
        self.setStyleSheet(STANDARD_LIGHT_FORM_DIALOG_QSS)

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
        apply_light_dialog_chrome(self)
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
            background-color: {COLORS['surface']};
            border-radius: 8px;
            border: 1px solid {COLORS['border']};
            color: {COLORS['text_primary']};
        """)
        layout.addWidget(self.recipe_info)

        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept_selection)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        for btn in buttons.findChildren(QPushButton):
            attach_press_flash(btn)
        self.setStyleSheet(STANDARD_LIGHT_FORM_DIALOG_QSS)

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
