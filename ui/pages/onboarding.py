# Страница первичной настройки (онбординг)
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QLineEdit, QComboBox, QPushButton, QFrame,
                              QSlider, QGridLayout, QButtonGroup, QRadioButton,
                              QScrollArea, QStackedWidget)
from PyQt6.QtCore import Qt, pyqtSignal

from config.settings import COLORS, ACTIVITY_LEVELS, GOALS
from core.calculator import calculate_bmr, calculate_tdee, calculate_target_calories, MacroCalculator
from core.pezvner import PevznerDiets
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
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)

        # Заголовок
        title = QLabel("Добро пожаловать в HealthAI!")
        title.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {COLORS['primary_dark']};
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Подзаголовок
        subtitle = QLabel("Давайте настроим приложение под вас")
        subtitle.setStyleSheet(f"""
            font-size: 16px;
            color: {COLORS['text_secondary']};
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        # Контейнер с формой (с прокруткой)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
        """)

        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(20)

        # Шаг 1: Основная информация
        step1_frame = self.create_step_frame("Шаг 1: Основная информация")
        step1_layout = QGridLayout(step1_frame)

        step1_layout.addWidget(QLabel("Ваше имя:"), 0, 0)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите ваше имя")
        step1_layout.addWidget(self.name_input, 0, 1)

        step1_layout.addWidget(QLabel("Пол:"), 1, 0)
        gender_layout = QHBoxLayout()
        self.gender_group = QButtonGroup()
        male_radio = QRadioButton("Мужской")
        female_radio = QRadioButton("Женский")
        self.gender_group.addButton(male_radio, 0)
        self.gender_group.addButton(female_radio, 1)
        gender_layout.addWidget(male_radio)
        gender_layout.addWidget(female_radio)
        gender_layout.addStretch()
        step1_layout.addLayout(gender_layout, 1, 1)

        step1_layout.addWidget(QLabel("Возраст (лет):"), 2, 0)
        self.age_input = QLineEdit()
        self.age_input.setPlaceholderText("Например, 30")
        step1_layout.addWidget(self.age_input, 2, 1)

        step1_layout.addWidget(QLabel("Рост (см):"), 3, 0)
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Например, 175")
        step1_layout.addWidget(self.height_input, 3, 1)

        step1_layout.addWidget(QLabel("Вес (кг):"), 4, 0)
        self.weight_input = QLineEdit()
        self.weight_input.setPlaceholderText("Например, 70")
        step1_layout.addWidget(self.weight_input, 4, 1)

        form_layout.addWidget(step1_frame)

        # Шаг 2: Активность
        step2_frame = self.create_step_frame("Шаг 2: Уровень активности")
        step2_layout = QVBoxLayout(step2_frame)

        self.activity_combo = QComboBox()
        for level_id, level_data in ACTIVITY_LEVELS.items():
            self.activity_combo.addItem(level_data['name'], level_id)
        step2_layout.addWidget(self.activity_combo)

        activity_desc = QLabel("Выберите наиболее подходящий вариант")
        activity_desc.setStyleSheet(f"""
            font-size: 12px;
            color: {COLORS['text_hint']};
        """)
        step2_layout.addWidget(activity_desc)

        form_layout.addWidget(step2_frame)

        # Шаг 3: Цель
        step3_frame = self.create_step_frame("Шаг 3: Ваша цель")
        step3_layout = QVBoxLayout(step3_frame)

        self.goal_combo = QComboBox()
        for goal_id, goal_data in GOALS.items():
            self.goal_combo.addItem(f"{goal_data['name']} - {goal_data['description']}", goal_id)
        step3_layout.addWidget(self.goal_combo)

        form_layout.addWidget(step3_frame)

        # Шаг 4: Медицинские показания (опционально)
        step4_frame = self.create_step_frame("Шаг 4: Медицинские показания (необязательно)")
        step4_layout = QVBoxLayout(step4_frame)

        self.diet_combo = QComboBox()
        self.diet_combo.addItem("Без ограничений", None)
        for diet in PevznerDiets.get_all_diets():
            self.diet_combo.addItem(f"Стол №{diet.number}: {diet.name}", diet.id)

        self.diet_combo.currentIndexChanged.connect(self.show_diet_info)
        step4_layout.addWidget(self.diet_combo)

        self.diet_info_label = QLabel("")
        self.diet_info_label.setStyleSheet(f"""
            font-size: 12px;
            color: {COLORS['text_secondary']};
            background-color: {COLORS['background']};
            border-radius: 8px;
            padding: 12px;
        """)
        self.diet_info_label.setWordWrap(True)
        step4_layout.addWidget(self.diet_info_label)

        form_layout.addWidget(step4_frame)

        form_container.setLayout(form_layout)
        scroll.setWidget(form_container)
        layout.addWidget(scroll)

        # Результат расчётов
        self.result_frame = self.create_result_frame()
        self.result_frame.setVisible(False)
        layout.addWidget(self.result_frame)

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.calc_btn = QPushButton("Рассчитать")
        self.calc_btn.clicked.connect(self.calculate_and_show)
        button_layout.addWidget(self.calc_btn)

        self.save_btn = QPushButton("Сохранить и начать")
        self.save_btn.setVisible(False)
        self.save_btn.clicked.connect(self.save_and_finish)
        button_layout.addWidget(self.save_btn)

        layout.addLayout(button_layout)

    def create_step_frame(self, title: str) -> QFrame:
        """Создание рамки для шага"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                padding: 20px;
            }}
        """)

        layout = QVBoxLayout(frame)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {COLORS['primary_dark']};
        """)
        layout.addWidget(title_label)

        layout.addSpacing(12)

        return frame

    def create_result_frame(self) -> QFrame:
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

        title = QLabel("🎯 Ваша норма калорий")
        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {COLORS['primary_dark']};
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(16)

        # Калории
        self.result_calories = QLabel("")
        self.result_calories.setStyleSheet(f"""
            font-size: 32px;
            font-weight: bold;
            color: {COLORS['primary']};
        """)
        self.result_calories.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.result_calories)

        layout.addSpacing(12)

        # БЖУ
        self.result_macros = QLabel("")
        self.result_macros.setStyleSheet(f"""
            font-size: 14px;
            color: {COLORS['text_secondary']};
        """)
        self.result_macros.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.result_macros)

        return frame

    def show_diet_info(self):
        """Показать информацию о выбранной диете"""
        diet_id = self.diet_combo.currentData()
        if diet_id:
            diet = PevznerDiets.get_diet(diet_id)
            if diet:
                info = f"""
<b>{diet.full_name}</b><br>
Показания: {', '.join(diet.indications[:2])}<br>
Длительность: {diet.duration}
"""
                self.diet_info_label.setText(info)
                self.diet_info_label.setVisible(True)
        else:
            self.diet_info_label.setVisible(False)

    def calculate_and_show(self):
        """Расчёт и показ результатов"""
        # Валидация
        if not self.validate_inputs():
            return

        # Получение данных
        name = self.name_input.text().strip()
        gender = 'male' if self.gender_group.checkedId() == 0 else 'female'
        age = int(self.age_input.text())
        height = float(self.height_input.text())
        weight = float(self.weight_input.text())
        activity_level = self.activity_combo.currentData()
        goal = self.goal_combo.currentData()
        diet_type = self.diet_combo.currentData()

        # Расчёты
        bmr = calculate_bmr(gender, age, height, weight)
        tdee = calculate_tdee(bmr, activity_level)
        target = calculate_target_calories(tdee, goal)

        # Отображение результатов
        self.result_calories.setText(f"{int(target)} ккал/день")

        macros = {
            'protein': int(target * 0.25 / 4),  # ~25% белка
            'fat': int(target * 0.25 / 9),      # ~25% жира
            'carbs': int(target * 0.50 / 4),    # ~50% углеводов
        }

        self.result_macros.setText(
            f"Белки: {macros['protein']}г | Жиры: {macros['fat']}г | Углеводы: {macros['carbs']}г"
        )

        # Сохранение расчётов для использования при сохранении
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
            'xp': 10,  # Начальный XP
        }

        # Инициализация базы данных
        populate_initial_data()

        # Сохранение пользователя
        save_user(user_data)

        # Разблокируем первое достижение
        from database.operations import get_user
        user = get_user()
        if user:
            unlock_achievement(user.id, 'first_entry')

        # Переход на главную страницу
        self.main_window.check_user()
        self.completed.emit()
