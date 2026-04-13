# ui/pages/profile_page.py — параметры пользователя (рост, вес, активность и др.)
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QPushButton,
    QButtonGroup,
    QRadioButton,
    QHBoxLayout,
    QScrollArea,
    QFrame,
    QSizePolicy,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut

try:
    from config.settings import COLORS, ACTIVITY_LEVELS, GOALS
except ImportError:
    COLORS = {
        "primary": "#3498DB",
        "primary_dark": "#2980B9",
        "text_secondary": "#7F8C8D",
        "text_hint": "#95A5A6",
        "surface": "#FFFFFF",
    }
    ACTIVITY_LEVELS = {
        "sedentary": {"name": "Сидячий"},
        "light": {"name": "Легкий"},
        "moderate": {"name": "Средний"},
        "active": {"name": "Высокий"},
        "very_active": {"name": "Экстремальный"},
    }
    GOALS = {
        "lose": {"name": "Похудение"},
        "maintain": {"name": "Поддержание"},
        "gain": {"name": "Набор массы"},
        "healthy": {"name": "Здоровое питание"},
    }

from core.calculator import calculate_bmr, calculate_tdee, calculate_target_calories
from database.operations import update_user_fields, get_user
from ui.components.press_feedback import attach_press_flash


class ProfilePage(QWidget):
    """Редактирование профиля локального пользователя (одна запись в БД)."""

    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        title = QLabel("👤 Мой профиль")
        title.setObjectName("titleLabel")
        root.addWidget(title)

        hint = QLabel(
            "Имя, антропометрия, активность и цель влияют на норму калорий, дашборд и ответы AI-чата."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {COLORS.get('text_secondary', '#7F8C8D')}; font-size: 13px;")
        root.addWidget(hint)

        explain = QLabel(
            "<b>Как считается норма и зачем она нужна</b><br><br>"
            "• <b>BMR</b> (базальный метаболизм) — примерная суточная энергия организма в покое. "
            "Считается по формуле Миффлина — Сан Жеора с учётом пола, возраста, веса и роста.<br><br>"
            "• <b>TDEE</b> (суточный расход) — BMR, умноженный на коэффициент активности: сколько калорий "
            "вы тратите с учётом работы и движения.<br><br>"
            "• <b>Целевая калорийность</b> подбирается от TDEE в зависимости от цели (например, дефицит "
            "для похудения или профицит для набора массы).<br><br>"
            "Эти значения сохраняются в профиле и используются в дневнике, на дашборде и в подсказках "
            "AI-нутрициолога — без актуальных данных персонализация будет менее точной."
        )
        explain.setWordWrap(True)
        explain.setTextFormat(Qt.TextFormat.RichText)
        explain.setOpenExternalLinks(False)
        explain.setStyleSheet(
            f"color: {COLORS.get('text_primary', '#212121')}; font-size: 13px; "
            f"background: {COLORS.get('background', '#F5F7FA')}; border-radius: 10px; padding: 14px;"
        )
        root.addWidget(explain)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        inner = QWidget()
        form_layout = QVBoxLayout(inner)

        box = QFrame()
        box.setStyleSheet(
            f"QFrame {{ background: {COLORS.get('surface', '#fff')}; border-radius: 12px; padding: 16px; }}"
        )
        fl = QFormLayout(box)
        fl.setSpacing(12)

        self.name_input = QLineEdit()
        fl.addRow("Имя:", self.name_input)

        gender_row = QHBoxLayout()
        self.gender_group = QButtonGroup(self)
        self.rb_male = QRadioButton("Мужской")
        self.rb_female = QRadioButton("Женский")
        self.gender_group.addButton(self.rb_male, 0)
        self.gender_group.addButton(self.rb_female, 1)
        gender_row.addWidget(self.rb_male)
        gender_row.addWidget(self.rb_female)
        fl.addRow("Пол:", gender_row)

        self.age_input = QLineEdit()
        self.height_input = QLineEdit()
        self.weight_input = QLineEdit()
        fl.addRow("Возраст (лет):", self.age_input)
        fl.addRow("Рост (см):", self.height_input)
        fl.addRow("Вес (кг):", self.weight_input)

        self.activity_combo = QComboBox()
        for level_id, level_data in ACTIVITY_LEVELS.items():
            self.activity_combo.addItem(level_data["name"], level_id)
        fl.addRow("Активность:", self.activity_combo)

        self.goal_combo = QComboBox()
        for goal_id, goal_data in GOALS.items():
            self.goal_combo.addItem(goal_data["name"], goal_id)
        fl.addRow("Цель:", self.goal_combo)

        self.diet_combo = QComboBox()
        self.diet_combo.addItem("Без ограничений", None)
        self.diet_combo.addItem("Стол №5 - Печёночный", "pevzner_5")
        self.diet_combo.addItem("Стол №9 - Диабетический", "pevzner_9")
        self.diet_combo.addItem("Стол №1 - Язвенный", "pevzner_1")
        self.diet_combo.addItem("Стол №15 - Общий", "pevzner_15")
        fl.addRow("Диета (опц.):", self.diet_combo)

        form_layout.addWidget(box)

        scroll.setWidget(inner)
        scroll.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding
        )
        root.addWidget(scroll, 1)

        footer = QFrame()
        footer.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        foot_l = QVBoxLayout(footer)
        foot_l.setContentsMargins(0, 4, 0, 0)
        foot_l.setSpacing(8)
        foot_hint = QLabel(
            "Данные записываются в базу только после «Сохранить». "
            "Иначе после перезапуска останутся старые значения."
        )
        foot_hint.setWordWrap(True)
        foot_hint.setStyleSheet(
            f"color: {COLORS.get('text_secondary', '#7F8C8D')}; font-size: 12px;"
        )
        foot_l.addWidget(foot_hint)
        self.save_btn = QPushButton("Сохранить профиль")
        self.save_btn.setObjectName("primaryBtn")
        self.save_btn.setMinimumHeight(48)
        self.save_btn.setToolTip("Сохранить данные в базу (Ctrl+S)")
        self.save_btn.clicked.connect(self._save)
        attach_press_flash(self.save_btn)
        foot_l.addWidget(self.save_btn)

        root.addWidget(footer, 0)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet(f"color: {COLORS.get('text_hint', '#95A5A6')};")
        root.addWidget(self.status_label)

        QShortcut(QKeySequence.StandardKey.Save, self, self._save)

    def refresh(self):
        self.status_label.setText("")
        user = None
        if self.main_window and self.main_window.current_user:
            user = self.main_window.current_user
        elif get_user:
            user = get_user(1)
        if not user:
            self.status_label.setText("Пользователь не найден. Пройдите первичную настройку при запуске.")
            return

        self.name_input.setText(user.name or "")
        if user.gender == "female":
            self.rb_female.setChecked(True)
        else:
            self.rb_male.setChecked(True)
        self.age_input.setText(str(user.age))
        self.height_input.setText(str(user.height))
        self.weight_input.setText(str(user.weight))

        for i in range(self.activity_combo.count()):
            if self.activity_combo.itemData(i) == user.activity_level:
                self.activity_combo.setCurrentIndex(i)
                break

        for i in range(self.goal_combo.count()):
            if self.goal_combo.itemData(i) == user.goal:
                self.goal_combo.setCurrentIndex(i)
                break

        if user.diet_type:
            for i in range(self.diet_combo.count()):
                if self.diet_combo.itemData(i) == user.diet_type:
                    self.diet_combo.setCurrentIndex(i)
                    break
        else:
            self.diet_combo.setCurrentIndex(0)

    def _validate(self) -> bool:
        errors = []
        if not self.name_input.text().strip():
            errors.append("Введите имя")
        try:
            age = int(self.age_input.text())
            if age < 13 or age > 100:
                errors.append("Возраст 13–100")
        except ValueError:
            errors.append("Некорректный возраст")
        try:
            h = float(self.height_input.text())
            if h < 100 or h > 250:
                errors.append("Рост 100–250 см")
        except ValueError:
            errors.append("Некорректный рост")
        try:
            w = float(self.weight_input.text())
            if w < 30 or w > 300:
                errors.append("Вес 30–300 кг")
        except ValueError:
            errors.append("Некорректный вес")
        if errors:
            self.status_label.setText("Ошибка: " + "; ".join(errors))
            return False
        return True

    def _save(self):
        if not self._validate():
            return
        uid = 1
        if self.main_window and self.main_window.current_user:
            uid = self.main_window.current_user.id
        elif get_user:
            u = get_user(1)
            if u:
                uid = u.id

        gender = "male" if self.gender_group.checkedId() == 0 else "female"
        age = int(self.age_input.text())
        height = float(self.height_input.text())
        weight = float(self.weight_input.text())
        activity_level = self.activity_combo.currentData()
        goal = self.goal_combo.currentData()
        diet_type = self.diet_combo.currentData()

        bmr = calculate_bmr(gender, age, height, weight)
        tdee = calculate_tdee(bmr, activity_level)
        target = calculate_target_calories(tdee, goal)

        ok = update_user_fields(
            uid,
            {
                "name": self.name_input.text().strip(),
                "gender": gender,
                "age": age,
                "height": height,
                "weight": weight,
                "activity_level": activity_level,
                "goal": goal,
                "diet_type": diet_type,
                "bmr": bmr,
                "tdee": tdee,
                "target_calories": target,
            },
        )
        if not ok:
            self.status_label.setText("Не удалось сохранить (пользователь не найден в БД).")
            return

        self.status_label.setText(
            f"Сохранено. Целевая норма: ~{int(target)} ккал/день (BMR {int(bmr)}, TDEE {int(tdee)})."
        )
        if self.main_window:
            self.main_window.check_user()
