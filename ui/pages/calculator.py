# ui/pages/calculator.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout, QLineEdit, QComboBox, QPushButton, QGroupBox
from PyQt6.QtCore import Qt


class CalculatorPage(QWidget):
    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setup_ui()
        self.load_user_data()  # Загружаем данные текущего пользователя

    def setup_ui(self):
        layout = QVBoxLayout()

        title = QLabel("🧮 Калькулятор калорий")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        form = QFormLayout()
        self.gender = QComboBox()
        self.gender.addItems(["Мужской", "Женский"])
        self.age = QLineEdit("30")
        self.weight = QLineEdit("70")
        self.height = QLineEdit("175")
        self.activity = QComboBox()
        self.activity.addItems(["Сидячий", "Легкий", "Средний", "Высокий", "Экстремальный"])

        form.addRow("Пол:", self.gender)
        form.addRow("Возраст:", self.age)
        form.addRow("Вес (кг):", self.weight)
        form.addRow("Рост (см):", self.height)
        form.addRow("Активность:", self.activity)

        layout.addLayout(form)

        btn = QPushButton("Рассчитать")
        btn.setObjectName("primaryBtn")
        btn.clicked.connect(self.calculate)
        layout.addWidget(btn)

        self.result = QLabel("Результат появится здесь")
        self.result.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(self.result)

        layout.addStretch()
        self.setLayout(layout)

    def load_user_data(self):
        """Загрузка данных текущего пользователя для предзаполнения полей"""
        if not self.main_window or not self.main_window.current_user:
            return
        user = self.main_window.current_user
        # Устанавливаем пол
        if user.gender == 'male':
            self.gender.setCurrentText("Мужской")
        else:
            self.gender.setCurrentText("Женский")
        # Возраст
        self.age.setText(str(user.age))
        # Вес
        self.weight.setText(str(user.weight))
        # Рост
        self.height.setText(str(user.height))
        # Уровень активности
        activity_map = {
            'sedentary': "Сидячий",
            'light': "Легкий",
            'moderate': "Средний",
            'active': "Высокий",
            'very_active': "Экстремальный"
        }
        activity_text = activity_map.get(user.activity_level, "Средний")
        self.activity.setCurrentText(activity_text)

    def calculate(self):
        try:
            weight = float(self.weight.text())
            height = float(self.height.text())
            age = int(self.age.text())
            gender = 5 if self.gender.currentText() == "Мужской" else -161
            activity_map = {"Сидячий": 1.2, "Легкий": 1.375, "Средний": 1.55, "Высокий": 1.725, "Экстремальный": 1.9}
            activity = activity_map[self.activity.currentText()]

            bmr = (10 * weight) + (6.25 * height) - (5 * age) + gender
            tdee = bmr * activity

            self.result.setText(f"BMR: {int(bmr)} ккал\nTDEE: {int(tdee)} ккал")
        except Exception as e:
            self.result.setText(f"Ошибка: {e}")
