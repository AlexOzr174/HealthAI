"""
AI Recipe Generator Widget - Генератор рецептов с ИИ
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QScrollArea, QGridLayout,
                             QComboBox, QTextEdit, QLineEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class RecipeCard(QFrame):
    """Карточка рецепта"""
    def __init__(self, recipe_data, parent=None):
        super().__init__(parent)
        self.recipe = recipe_data
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #e0e0e0;
            }
            QFrame:hover {
                border: 2px solid #4CAF50;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Название
        title = QLabel(f"🍽️ {self.recipe.get('name', 'Рецепт')}")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        # Информация (калории, время, сложность)
        info_layout = QHBoxLayout()
        info_layout.setSpacing(20)
        
        calories = self.recipe.get('calories', 0)
        time = self.recipe.get('time', 0)
        difficulty = self.recipe.get('difficulty', 'Средняя')
        
        info_layout.addWidget(QLabel(f"🔥 {calories} ккал"))
        info_layout.addWidget(QLabel(f"⏱️ {time} мин"))
        info_layout.addWidget(QLabel(f"📊 {difficulty}"))
        
        for label in info_layout.children():
            if isinstance(label, QLabel):
                label.setStyleSheet("color: #666; font-size: 12px;")
        
        layout.addLayout(info_layout)
        
        # Ингредиенты
        ingredients_label = QLabel("🛒 Ингредиенты:")
        ingredients_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        ingredients_label.setStyleSheet("color: #2c3e50; margin-top: 10px;")
        layout.addWidget(ingredients_label)
        
        ingredients = self.recipe.get('ingredients', [])
        ingredients_text = "\n".join(f"• {ing}" for ing in ingredients[:5])
        if len(ingredients) > 5:
            ingredients_text += f"\n... и ещё {len(ingredients) - 5}"
            
        ingredients_display = QLabel(ingredients_text)
        ingredients_display.setWordWrap(True)
        ingredients_display.setStyleSheet("color: #555; padding: 5px;")
        layout.addWidget(ingredients_display)
        
        # Инструкция
        instructions_label = QLabel("📝 Приготовление:")
        instructions_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        instructions_label.setStyleSheet("color: #2c3e50; margin-top: 10px;")
        layout.addWidget(instructions_label)
        
        instructions = self.recipe.get('instructions', '')
        instructions_display = QLabel(instructions[:200] + "..." if len(instructions) > 200 else instructions)
        instructions_display.setWordWrap(True)
        instructions_display.setStyleSheet("color: #555; padding: 5px; background-color: #f9f9f9; border-radius: 8px;")
        layout.addWidget(instructions_display)
        
        # Макросы
        macros = self.recipe.get('macros', {})
        if macros:
            macros_layout = QHBoxLayout()
            macros_layout.setSpacing(15)
            
            for macro, value in macros.items():
                macro_label = QLabel(f"{macro.upper()}: {value}г")
                macro_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
                macros_layout.addWidget(macro_label)
            
            layout.addLayout(macros_layout)


class AIRecipeGeneratorWidget(QWidget):
    """Виджет генератора рецептов"""
    def __init__(self, ai_engine, user_id, parent=None):
        super().__init__(parent)
        self.ai_engine = ai_engine
        self.user_id = user_id
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Заголовок
        header = QLabel("👨‍🍳 AI Генератор Рецептов")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header.setStyleSheet("color: #2c3e50;")
        main_layout.addWidget(header)
        
        # Фильтры
        filters_layout = QGridLayout()
        filters_layout.setSpacing(15)
        
        # Категория блюда
        filters_layout.addWidget(QLabel("🍽️ Категория:"), 0, 0)
        self.category_combo = QComboBox()
        self.category_combo.addItems(["breakfast", "lunch", "dinner", "snack"])
        self.category_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 8px;
                background-color: white;
            }
        """)
        filters_layout.addWidget(self.category_combo, 0, 1)
        
        # Диетические ограничения
        filters_layout.addWidget(QLabel("🚫 Ограничения:"), 1, 0)
        self.restrictions_combo = QComboBox()
        self.restrictions_combo.addItems(["none", "lactose_free", "gluten_free", "vegan", "vegetarian"])
        self.restrictions_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 8px;
                background-color: white;
            }
        """)
        filters_layout.addWidget(self.restrictions_combo, 1, 1)
        
        # Предпочтения
        filters_layout.addWidget(QLabel("❤️ Предпочтения:"), 2, 0)
        self.preferences_input = QLineEdit()
        self.preferences_input.setPlaceholderText("Например: курица, овощи, без риса")
        self.preferences_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 8px;
            }
        """)
        filters_layout.addWidget(self.preferences_input, 2, 1)
        
        main_layout.addLayout(filters_layout)
        
        # Кнопка генерации
        generate_btn = QPushButton("✨ Сгенерировать рецепт")
        generate_btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        generate_btn.setFixedHeight(50)
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #1a1a1a;
                border: 2px solid #1a1a1a;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #E8F5E9;
            }
        """)
        generate_btn.clicked.connect(self.generate_recipe)
        main_layout.addWidget(generate_btn)
        
        # Область результатов
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setSpacing(20)
        
        # Приветственное сообщение
        welcome = QLabel("Нажмите кнопку для генерации персонального рецепта")
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome.setStyleSheet("color: #999; font-size: 14px; padding: 50px;")
        self.results_layout.addWidget(welcome)
        
        scroll.setWidget(self.results_container)
        main_layout.addWidget(scroll, 1)
        
        # Кнопки действий
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(15)
        
        save_btn = QPushButton("💾 Сохранить")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #1a1a1a;
                border: 2px solid #1a1a1a;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
            }
        """)
        
        share_btn = QPushButton("📤 Поделиться")
        share_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFF3E0;
                color: #1a1a1a;
                border: 2px solid #E65100;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
            }
        """)
        
        actions_layout.addWidget(save_btn)
        actions_layout.addWidget(share_btn)
        actions_layout.addStretch()
        
        main_layout.addLayout(actions_layout)
        
    def generate_recipe(self):
        """Сгенерировать рецепт"""
        category = self.category_combo.currentText()
        restrictions = self.restrictions_combo.currentText()
        preferences = self.preferences_input.text().strip()
        
        # Преобразование ограничений
        restriction_list = []
        if restrictions != "none":
            restriction_list = [restrictions]
        
        try:
            # Генерация через AI
            recipe = self.ai_engine.generate_recipe(
                user_id=self.user_id,
                category=category,
                restrictions=restriction_list
            )
            
            # Очистка предыдущих результатов
            while self.results_layout.count():
                item = self.results_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # Добавление карточки рецепта
            if recipe:
                recipe_card = RecipeCard(recipe)
                self.results_layout.addWidget(recipe_card)
            else:
                error_label = QLabel("❌ Не удалось сгенерировать рецепт")
                error_label.setStyleSheet("color: #f44336; padding: 20px;")
                self.results_layout.addWidget(error_label)
                
        except Exception as e:
            error_label = QLabel(f"❌ Ошибка: {str(e)}")
            error_label.setStyleSheet("color: #f44336; padding: 20px;")
            self.results_layout.addWidget(error_label)
