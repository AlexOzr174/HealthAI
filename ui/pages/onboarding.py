# Страница первичной настройки (онбординг)
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QLineEdit, QComboBox, QPushButton, QFrame,
                              QButtonGroup, QRadioButton,
                              QScrollArea, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal

from config.settings import COLORS, ACTIVITY_LEVELS, GOALS
from core.calculator import calculate_bmr, calculate_tdee, calculate_target_calories
from database.operations import save_user, unlock_achievement
from database.init_db import populate_initial_data


class OnboardingPage(QWidget):
    """Страница первичной настройки пользователя"""

    completed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        # Заголовок
        title = QLabel("Добро пожаловать в HealthAI!")
        title.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {COLORS['primary_dark']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        subtitle = QLabel("Давайте настроим приложение под вас")
        subtitle.setStyleSheet(f"font-size: 16px; color: {COLORS['text_secondary']};")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle)

        main_layout.addSpacing(10)

        # Скролл-область
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea {{ background-color: transparent; border: none; }}")

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(16)

        # === Шаг 1: Основная информация ===
        step1 = self._create_section_frame("Шаг 1: Основная информация")
        step1_layout = step1.layout()

        # Имя
        step1_layout.addWidget(self._create_label("Ваше имя:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите ваше имя")
        step1_layout.addWidget(self.name_input)

        # Пол
        step1_layout.addWidget(self._create_label("Пол:"))
        gender_container = self._create_gender_selector()
        step1_layout.addWidget(gender_container)

        # Возраст
        step1_layout.addWidget(self._create_label("Возраст (лет):"))
        self.age_input = QLineEdit()
        self.age_input.setPlaceholderText("Например, 30")
        step1_layout.addWidget(self.age_input)

        # Рост
        step1_layout.addWidget(self._create_label("Рост (см):"))
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Например, 175")
        step1_layout.addWidget(self.height_input)

        # Вес
        step1_layout.addWidget(self._create_label("Вес (кг):"))
        self.weight_input = QLineEdit()
        self.weight_input.setPlaceholderText("Например, 70")
        step1_layout.addWidget(self.weight_input)

        scroll_layout.addWidget(step1)

        # === Шаг 2: Активность ===
        step2 = self._create_section_frame("Шаг 2: Уровень активности")
        step2_layout = step2.layout()

        self.activity_combo = QComboBox()
        for level_id, level_data in ACTIVITY_LEVELS.items():
            self.activity_combo.addItem(level_data['name'], level_id)
        step2_layout.addWidget(self.activity_combo)

        desc = QLabel("Выберите наиболее подходящий вариант")
        desc.setStyleSheet(f"font-size: 12px; color: {COLORS['text_hint']};")
        step2_layout.addWidget(desc)

        scroll_layout.addWidget(step2)

        # === Шаг 3: Цель ===
        step3 = self._create_section_frame("Шаг 3: Ваша цель")
        step3_layout = step3.layout()

        self.goal_combo = QComboBox()
        for goal_id, goal_data in GOALS.items():
            self.goal_combo.addItem(f"{goal_data['name']} - {goal_data['description']}", goal_id)
        step3_layout.addWidget(self.goal_combo)

        scroll_layout.addWidget(step3)

        # === Шаг 4: Диета ===
        step4 = self._create_section_frame("Шаг 4: Диета (необязательно)")
        step4_layout = step4.layout()

        self.diet_combo = QComboBox()
        self.diet_combo.addItem("Без ограничений", None)
        self.diet_combo.addItem("Стол №5 - Печёночный", "pevzner_5")
        self.diet_combo.addItem("Стол №9 - Диабетический", "pevzner_9")
        self.diet_combo.addItem("Стол №1 - Язвенный", "pevzner_1")
        self.diet_combo.addItem("Стол №15 - Общий", "pevzner_15")
        self.diet_combo.currentIndexChanged.connect(self._on_diet_changed)
        step4_layout.addWidget(self.diet_combo)

        self.diet_info = QLabel("")
        self.diet_info.setStyleSheet(f"""
            font-size: 12px;
            color: {COLORS['text_secondary']};
            background-color: {COLORS['surface']};
            border-radius: 8px;
            padding: 12px;
        """)
        self.diet_info.setWordWrap(True)
        self.diet_info.setVisible(False)
        step4_layout.addWidget(self.diet_info)

        scroll_layout.addWidget(step4)

        # Устанавливаем контент в скролл
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, stretch=1)

        # === Результат ===
        self.result_frame = self._create_result_frame()
        self.result_frame.setVisible(False)
        main_layout.addWidget(self.result_frame)

        # === Кнопки ===
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.calc_btn = QPushButton("Рассчитать")
        self.calc_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 32px;
                font-size: 16px;
            }}
            QPushButton:hover {{ background-color: {COLORS['primary_hover']}; }}
        """)
        self.calc_btn.clicked.connect(self.calculate_and_show)
        btn_layout.addWidget(self.calc_btn)

        self.save_btn = QPushButton("Сохранить и начать")
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 32px;
                font-size: 16px;
            }}
            QPushButton:hover {{ background-color: {COLORS['success_hover']}; }}
        """)
        self.save_btn.setVisible(False)
        self.save_btn.clicked.connect(self.save_and_finish)
        btn_layout.addWidget(self.save_btn)

        main_layout.addLayout(btn_layout)

    def _create_label(self, text: str) -> QLabel:
        """Создание подписи"""
        label = QLabel(text)
        label.setStyleSheet(f"font-size: 14px; color: {COLORS['text_primary']};")
        return label

    def _create_section_frame(self, title: str) -> QFrame:
        """Создание секции формы"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        layout = QVBoxLayout(frame)
        layout.setSpacing(12)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['primary_dark']};")
        layout.addWidget(title_label)

        # Добавляем spacer между заголовком и контентом
        spacer = QSpacerItem(0, 8, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        layout.addSpacerItem(spacer)

        return frame

    def _create_gender_selector(self) -> QWidget:
        """Создание селектора пола"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        self.gender_group = QButtonGroup()

        male_radio = QRadioButton("Мужской")
        female_radio = QRadioButton("Женский")

        self.gender_group.addButton(male_radio, 0)
        self.gender_group.addButton(female_radio, 1)

        layout.addWidget(male_radio)
        layout.addWidget(female_radio)
        layout.addStretch()

        return container

    def _create_result_frame(self) -> QFrame:
        """Создание рамки с результатами"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['primary_light']}30;
                border: 2px solid {COLORS['primary']};
                border-radius: 12px;
                padding: 20px;
            }}
        """)

        layout = QVBoxLayout(frame)

        title = QLabel("Ваша норма калорий")
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLORS['primary_dark']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(16)

        self.result_calories = QLabel("")
        self.result_calories.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {COLORS['primary']};")
        self.result_calories.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.result_calories)

        layout.addSpacing(12)

        self.result_macros = QLabel("")
        self.result_macros.setStyleSheet(f"font-size: 14px; color: {COLORS['text_secondary']};")
        self.result_macros.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.result_macros)

        return frame

    def _on_diet_changed(self):
        """Обработчик изменения диеты"""
        diet_id = self.diet_combo.currentData()
        diet_info = {
            None: ("Без ограничений", "Можно есть всё в умеренных количествах"),
            "pevzner_5": ("Стол №5", "Для заболеваний печени и желчного пузыря"),
            "pevzner_9": ("Стол №9", "Для сахарного диабета"),
            "pevzner_1": ("Стол №1", "Для язвенной болезни желудка"),
            "pevzner_15": ("Стол №15", "Для восстановления после болезни"),
        }

        if diet_id in diet_info:
            name, desc = diet_info[diet_id]
            self.diet_info.setText(f"<b>{name}</b><br>{desc}")
            self.diet_info.setVisible(True)
        else:
            self.diet_info.setVisible(False)

    def calculate_and_show(self):
        """Расчёт и показ результатов"""
        if not self.validate_inputs():
            return

        name = self.name_input.text().strip()
        gender = 'male' if self.gender_group.checkedId() == 0 else 'female'
        age = int(self.age_input.text())
        height = float(self.height_input.text())
        weight = float(self.weight_input.text())
        activity_level = self.activity_combo.currentData()
        goal = self.goal_combo.currentData()
        diet_type = self.diet_combo.currentData()

        bmr = calculate_bmr(gender, age, height, weight)
        tdee = calculate_tdee(bmr, activity_level)
        target = calculate_target_calories(tdee, goal)

        self.result_calories.setText(f"{int(target)} ккал/день")

        macros = {
            'protein': int(target * 0.25 / 4),
            'fat': int(target * 0.25 / 9),
            'carbs': int(target * 0.50 / 4),
        }

        self.result_macros.setText(
            f"Белки: {macros['protein']}г | Жиры: {macros['fat']}г | Углеводы: {macros['carbs']}г"
        )

        self.calculation_result = {
            'bmr': bmr,
            'tdee': tdee,
            'target': target,
        }

        self.result_frame.setVisible(True)
        self.save_btn.setVisible(True)
        self.calc_btn.setVisible(False)

    def validate_inputs(self) -> bool:
        """Валидация введённых данных"""
        errors = []

        name = self.name_input.text().strip()
        if not name:
            errors.append("Введите ваше имя")

        if self.gender_group.checkedId() == -1:
            errors.append("Выберите пол")

        try:
            age = int(self.age_input.text())
            if age < 13 or age > 100:
                errors.append("Возраст должен быть от 13 до 100 лет")
        except ValueError:
            errors.append("Введите корректный возраст")

        try:
            height = float(self.height_input.text())
            if height < 100 or height > 250:
                errors.append("Рост должен быть от 100 до 250 см")
        except ValueError:
            errors.append("Введите корректный рост")

        try:
            weight = float(self.weight_input.text())
            if weight < 30 or weight > 300:
                errors.append("Вес должен быть от 30 до 300 кг")
        except ValueError:
            errors.append("Введите корректный вес")

        if errors:
            from ui.components.dialogs import show_error
            show_error(self, "Ошибка валидации", "\n".join(errors))
            return False

        return True

    def save_and_finish(self):
        """Сохранение данных и завершение онбординга"""
        name = self.name_input.text().strip()
        gender = 'male' if self.gender_group.checkedId() == 0 else 'female'
        age = int(self.age_input.text())
        height = float(self.height_input.text())
        weight = float(self.weight_input.text())
        activity_level = self.activity_combo.currentData()
        goal = self.goal_combo.currentData()
        diet_type = self.diet_combo.currentData()

        user_data = {
            'name': name,
            'gender': gender,
            'age': age,
            'height': height,
            'weight': weight,
            'activity_level': activity_level,
            'goal': goal,
            'diet_type': diet_type,
            'bmr': self.calculation_result['bmr'],
            'tdee': self.calculation_result['tdee'],
            'target_calories': self.calculation_result['target'],
            'xp': 10,
        }

        populate_initial_data()
        save_user(user_data)

        from database.operations import get_user
        user = get_user()
        if user:
            unlock_achievement(user.id, 'first_entry')

        self.main_window.check_user()
        self.completed.emit()
