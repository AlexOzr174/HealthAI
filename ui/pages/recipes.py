# ui/pages/recipes.py
# Страница базы рецептов
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QPushButton, QLineEdit, QComboBox,
                             QListWidget, QListWidgetItem, QGridLayout,
                             QScrollArea, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt

try:
    from config.settings import COLORS
except ImportError:
    COLORS = {
        'surface': '#FFFFFF', 'primary': '#3498DB', 'primary_dark': '#2980B9',
        'primary_light': '#5DADE2', 'text_primary': '#2C3E50',
        'text_secondary': '#7F8C8D', 'warning': '#F39C12', 'border': '#E0E0E0',
        'background': '#F0F2F5'
    }

from database.operations import (get_all_recipes, get_recipes_by_diet,
                                 search_recipes, get_user)
from database.models import Recipe


class RecipeCard(QFrame):
    """Карточка рецепта"""

    def __init__(self, recipe: Recipe, parent=None):
        super().__init__(parent)
        self.recipe = recipe
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                padding: 16px;
            }}
            QFrame:hover {{
                border-color: {COLORS['primary_light']};
                background-color: {COLORS['primary_light']}10;
            }}
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        header_layout = QHBoxLayout()
        icon_label = QLabel(self.get_category_icon())
        icon_label.setStyleSheet("font-size: 32px;")
        header_layout.addWidget(icon_label)

        info_layout = QVBoxLayout()
        name_label = QLabel(self.recipe.name)
        name_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['text_primary']};")
        name_label.setWordWrap(True)
        info_layout.addWidget(name_label)

        if self.recipe.suitable_diets:
            tags_layout = QHBoxLayout()
            for diet in self.recipe.suitable_diets[:3]:
                tag = QLabel(f"#{diet.replace('pevzner_', '')}")
                tag.setStyleSheet(
                    f"font-size: 10px; color: {COLORS['primary']}; background-color: {COLORS['primary_light']}30; padding: 2px 6px; border-radius: 4px;")
                tags_layout.addWidget(tag)
            info_layout.addLayout(tags_layout)

        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        if self.recipe.description:
            desc_label = QLabel(self.recipe.description[:100] + "..." if len(
                self.recipe.description) > 100 else self.recipe.description)
            desc_label.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']};")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        macros_layout = QHBoxLayout()
        macros_layout.setSpacing(16)
        macro_items = [
            ("🔥", f"{int(self.recipe.calories)} ккал"),
            ("🥩", f"Б: {int(self.recipe.protein)}г"),
            ("🥑", f"Ж: {int(self.recipe.fat)}г"),
            ("🍚", f"У: {int(self.recipe.carbs)}г"),
        ]
        for icon, text in macro_items:
            macro_layout = QVBoxLayout()
            macro_layout.setSpacing(0)
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 14px;")
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            text_lbl = QLabel(text)
            text_lbl.setStyleSheet(f"font-size: 11px; color: {COLORS['text_secondary']};")
            text_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            macro_layout.addWidget(icon_lbl)
            macro_layout.addWidget(text_lbl)
            macros_layout.addLayout(macro_layout)
        layout.addLayout(macros_layout)

        footer_layout = QHBoxLayout()
        if self.recipe.prep_time:
            time_label = QLabel(f"⏱️ {self.recipe.prep_time} мин")
            time_label.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']};")
            footer_layout.addWidget(time_label)
        footer_layout.addStretch()
        rating_layout = QHBoxLayout()
        rating_layout.setSpacing(4)
        star_label = QLabel("⭐")
        star_label.setStyleSheet("font-size: 14px;")
        rating_value = QLabel(f"{self.recipe.rating:.1f}")
        rating_value.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {COLORS['warning']};")
        rating_layout.addWidget(star_label)
        rating_layout.addWidget(rating_value)
        footer_layout.addLayout(rating_layout)
        layout.addLayout(footer_layout)

    def get_category_icon(self) -> str:
        icons = {'breakfast': '🌅', 'lunch': '☀️', 'dinner': '🌙', 'snack': '🍪'}
        return icons.get(self.recipe.category, '🍽️')


class RecipesPage(QWidget):
    """Страница базы рецептов"""

    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window  # <-- ВАЖНО: сохраняем ссылку
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        search_frame = self.create_search_panel()
        layout.addWidget(search_frame)

        recipes_frame = self.create_recipes_grid()
        layout.addWidget(recipes_frame, stretch=1)

    def refresh(self):
        self.update_recipes_list()

    def create_search_panel(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(f"background-color: {COLORS['surface']}; border-radius: 12px; padding: 16px;")
        layout = QHBoxLayout(frame)
        layout.setSpacing(12)

        search_layout = QHBoxLayout()
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("font-size: 16px;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск рецептов...")
        self.search_input.setMinimumWidth(250)
        self.search_input.textChanged.connect(self.filter_recipes)
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        layout.addWidget(QLabel("Диета:"))
        self.diet_combo = QComboBox()
        self.diet_combo.addItem("Все диеты", None)
        diets = [("Стол №5", "pevzner_5"), ("Стол №9 (Диабет)", "pevzner_9"), ("Стол №8 (Похудение)", "pevzner_8"),
                 ("Стол №7 (Почки)", "pevzner_7"), ("Стол №10 (Сердце)", "pevzner_10")]
        for diet_name, diet_id in diets:
            self.diet_combo.addItem(diet_name, diet_id)
        self.diet_combo.currentIndexChanged.connect(self.filter_recipes)
        layout.addWidget(self.diet_combo)

        layout.addWidget(QLabel("Приём пищи:"))
        self.category_combo = QComboBox()
        categories = [("Все", None), ("🌅 Завтрак", "breakfast"), ("☀️ Обед", "lunch"), ("🌙 Ужин", "dinner"),
                      ("🍪 Перекус", "snack")]
        for cat_name, cat_id in categories:
            self.category_combo.addItem(cat_name, cat_id)
        self.category_combo.currentIndexChanged.connect(self.filter_recipes)
        layout.addWidget(self.category_combo)

        layout.addStretch()
        reset_btn = QPushButton("Сбросить")
        reset_btn.setStyleSheet(
            f"background-color: {COLORS['background']}; border: 1px solid {COLORS['border']}; border-radius: 8px; padding: 8px 16px;")
        reset_btn.clicked.connect(self.reset_filters)
        layout.addWidget(reset_btn)

        return frame

    def create_recipes_grid(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(frame)

        self.recipes_count = QLabel("Все рецепты")
        self.recipes_count.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['text_primary']};")
        layout.addWidget(self.recipes_count)
        layout.addSpacing(8)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: transparent; border: none;")
        self.recipes_container = QWidget()
        self.recipes_layout = QGridLayout(self.recipes_container)
        self.recipes_layout.setSpacing(12)
        scroll.setWidget(self.recipes_container)
        layout.addWidget(scroll)

        return frame

    def update_recipes_list(self, recipes: list = None):
        while self.recipes_layout.count():
            item = self.recipes_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if recipes is None:
            user = self.main_window.current_user if self.main_window else None
            if user and user.diet_type:
                recipes = get_recipes_by_diet(user.diet_type)
            else:
                recipes = get_all_recipes()

        self.recipes_count.setText(f"Найдено рецептов: {len(recipes)}")
        for i, recipe in enumerate(recipes):
            card = RecipeCard(recipe)
            self.recipes_layout.addWidget(card, i // 2, i % 2)

    def filter_recipes(self):
        query = self.search_input.text().strip()
        diet = self.diet_combo.currentData()
        category = self.category_combo.currentData()
        if not query and not diet and not category:
            self.update_recipes_list()
            return
        recipes = search_recipes(query, diet_type=diet, category=category)
        self.update_recipes_list(recipes)

    def reset_filters(self):
        self.search_input.clear()
        self.diet_combo.setCurrentIndex(0)
        self.category_combo.setCurrentIndex(0)
        self.update_recipes_list()
