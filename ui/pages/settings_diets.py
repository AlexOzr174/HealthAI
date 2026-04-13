"""
Страница настроек специальных диет (Кето, Палео, Интервальное голодание).
Позволяет включать/настраивать режимы питания и отслеживать макросы.
"""

import logging

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QSlider, QProgressBar, QScrollArea, QFrame, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPainter, QColor, QPen

from ui.font_helpers import emoji_font_family, ui_font_family

_log = logging.getLogger(__name__)


class MacroCircleWidget(QWidget):
    """Виджет кругового прогресс-бара для макросов"""

    def __init__(self, label: str, value: int, max_value: int, color: str, parent=None):
        super().__init__(parent)
        self.label = label
        self.value = value
        self.max_value = max_value
        self.color = QColor(color)
        self.setFixedSize(120, 120)

    def set_value(self, value: int) -> None:
        self.value = int(value)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Центр и радиус
        center = self.width() / 2
        radius = 45

        # Фон круга
        painter.setPen(QPen(QColor("#eee"), 8))
        painter.drawEllipse(int(center - radius), int(center - radius), int(radius * 2), int(radius * 2))

        # Прогресс
        if self.max_value > 0:
            span_angle = int(360 * (self.value / self.max_value) * 16)  # 16 единиц на градус

            painter.setPen(QPen(self.color, 8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawArc(int(center - radius), int(center - radius), int(radius * 2), int(radius * 2),
                            90 * 16, -span_angle)

        # Текст в центре
        painter.setPen(QColor("#333"))
        font = QFont(ui_font_family(), 14, QFont.Weight.Bold)
        painter.setFont(font)
        percent = int((self.value / self.max_value) * 100) if self.max_value > 0 else 0
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"{percent}%")

        # Подпись снизу
        font = QFont(ui_font_family(), 9)
        painter.setFont(font)
        painter.setPen(QColor("#777"))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, self.label)


class DietModeCard(QWidget):
    """Карточка режима диеты с переключателем и настройками"""

    toggle_changed = pyqtSignal(str, bool)

    def __init__(self, diet_id: str, title: str, description: str, icon: str, parent=None):
        super().__init__(parent)
        self.diet_id = diet_id
        self.setFixedHeight(140)
        self.setStyleSheet("""
            DietModeCard {
                background-color: #fff;
                border-radius: 15px;
                border: 1px solid #eee;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(20)

        # Иконка
        icon_label = QLabel(icon)
        icon_label.setFont(QFont(emoji_font_family(), 32))
        icon_label.setFixedWidth(60)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # Информация
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)

        title_label = QLabel(title)
        title_label.setFont(QFont(ui_font_family(), 14, QFont.Weight.Bold))
        info_layout.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setFont(QFont(ui_font_family(), 10))
        desc_label.setStyleSheet("color: #666;")
        desc_label.setWordWrap(True)
        info_layout.addWidget(desc_label)

        layout.addLayout(info_layout, 1)

        # Переключатель (крупная зона нажатия + явный индикатор — на macOS мелкий QCheckBox часто «не кликается»)
        self.checkbox = QCheckBox()
        self.checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        self.checkbox.setMinimumSize(48, 48)
        self.checkbox.setStyleSheet(
            """
            QCheckBox { spacing: 8px; padding: 6px; }
            QCheckBox::indicator {
                width: 26px;
                height: 26px;
                border: 2px solid #7F8C8D;
                border-radius: 6px;
                background: #FFFFFF;
            }
            QCheckBox::indicator:hover { border-color: #3498DB; background: #F7FBFF; }
            QCheckBox::indicator:checked {
                background: #3498DB;
                border-color: #2980B9;
            }
            """
        )
        self.checkbox.toggled.connect(lambda on: self.toggle_changed.emit(self.diet_id, on))
        layout.addWidget(self.checkbox, alignment=Qt.AlignmentFlag.AlignVCenter)


class SpecialDietsPage(QWidget):
    """Сигнал для других частей приложения (дашборд, рекомендации), если подключат позже."""
    diet_settings_changed = pyqtSignal(dict)

    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setObjectName("specialDietsPage")
        self.init_ui()
        self.refresh()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Заголовок
        header = QLabel("🥗 Специальные диеты")
        header.setFont(QFont(ui_font_family(), 24, QFont.Weight.Bold))
        layout.addWidget(header)

        subtitle = QLabel(
            "Выберите режим питания. Кето / палео / веган / вегетарианство — по одному основному режиму; "
            "интервальное голодание можно добавить отдельно. Изменения сохраняются в профиль автоматически "
            "после переключения (или кнопкой «Сохранить»).")
        subtitle.setFont(QFont(ui_font_family(), 11))
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #666; margin-bottom: 20px;")
        layout.addWidget(subtitle)

        # Скролл область
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("border: none; background: transparent;")

        container = QWidget()
        content_layout = QVBoxLayout(container)
        content_layout.setSpacing(20)

        # Карточки диет
        self.diet_cards = {}

        diets = [
            ("keto", "🥑 Кето-диета",
             "Высокое содержание жиров, умеренное белков, минимум углеводов (<50г). Кетоз для жиросжигания.",
             "#f39c12"),
            ("paleo", "🍖 Палео-диета",
             "Питание как у предков: мясо, рыба, овощи, фрукты, орехи. Без зерновых, сахара и молочных продуктов.",
             "#e74c3c"),
            ("if", "⏰ Интервальное голодание",
             "Циклы питания и голодания. Популярная схема 16/8 (16 часов голода, 8 часов окно питания).", "#3498db"),
            ("vegan", "🌱 Веганство", "Только растительная пища. Исключены все продукты животного происхождения.",
             "#27ae60"),
            ("vegetarian", "🥦 Вегетарианство", "Без мяса и рыбы. Допускаются молочные продукты и яйца.", "#1abc9c"),
        ]

        for diet_id, title, desc, color in diets:
            card = DietModeCard(diet_id, title, desc, title.split()[0])
            card.toggle_changed.connect(self.handle_diet_toggle)
            self.diet_cards[diet_id] = card
            content_layout.addWidget(card)

        # Настройки интервального голодания (скрыты по умолчанию)
        self.if_settings_group = QGroupBox("⏰ Настройки интервального голодания")
        self.if_settings_group.setFont(QFont(ui_font_family(), 12, QFont.Weight.Bold))
        self.if_settings_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #3498db;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: #f8fbff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px;
                color: #3498db;
            }
        """)
        self.if_settings_group.setVisible(False)

        if_layout = QVBoxLayout()

        # Слайдер окна питания
        if_layout.addWidget(QLabel("Окно питания (часов):"))
        self.if_slider = QSlider(Qt.Orientation.Horizontal)
        self.if_slider.setMinimum(6)
        self.if_slider.setMaximum(12)
        self.if_slider.setValue(8)
        self.if_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.if_slider.setTickInterval(1)
        self.if_slider.valueChanged.connect(self._on_if_window_changed)
        if_layout.addWidget(self.if_slider)

        self.if_label = QLabel("Текущий режим: 16/8 (16 часов голода, 8 часов питания)")
        self.if_label.setFont(QFont(ui_font_family(), 10))
        self.if_label.setStyleSheet("color: #3498db; font-weight: bold;")
        if_layout.addWidget(self.if_label)

        self.if_settings_group.setLayout(if_layout)
        content_layout.addWidget(self.if_settings_group)

        # Цели по макросам для выбранной диеты
        macros_group = QGroupBox("📊 Целевые макронутриенты")
        macros_group.setFont(QFont(ui_font_family(), 12, QFont.Weight.Bold))
        macros_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #ddd;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: #fff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px;
                color: #333;
            }
        """)

        macros_layout = QHBoxLayout()
        macros_layout.setSpacing(30)

        self.fat_circle = MacroCircleWidget("Жиры", 70, 100, "#f39c12")
        self.protein_circle = MacroCircleWidget("Белки", 25, 100, "#e74c3c")
        self.carbs_circle = MacroCircleWidget("Углеводы", 5, 100, "#3498db")

        macros_layout.addWidget(self.fat_circle)
        macros_layout.addWidget(self.protein_circle)
        macros_layout.addWidget(self.carbs_circle)
        macros_layout.addStretch()

        macros_group.setLayout(macros_layout)
        content_layout.addWidget(macros_group)

        content_layout.addStretch()

        scroll.setWidget(container)
        layout.addWidget(scroll, 1)

        # Кнопка сохранения
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        save_btn = QPushButton("💾 Сохранить режим")
        save_btn.setFixedHeight(45)
        save_btn.setFixedWidth(200)
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

        self._status_label = QLabel("")
        self._status_label.setWordWrap(True)
        self._status_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self._status_label)

        self._autosave_timer = QTimer(self)
        self._autosave_timer.setSingleShot(True)
        self._autosave_timer.timeout.connect(self._flush_autosave)

    def _user_id(self) -> int:
        try:
            from database.operations import get_user
        except ImportError:
            return 1
        uid = 1
        if self.main_window and self.main_window.current_user:
            uid = self.main_window.current_user.id
        elif get_user:
            u = get_user(1)
            if u:
                uid = u.id
        return uid

    def _collect_settings(self) -> dict:
        settings = {
            "active_diets": [],
            "if_window": self.if_slider.value() if self.if_settings_group.isVisible() else None,
        }
        for diet_id, card in self.diet_cards.items():
            if card.checkbox.isChecked():
                settings["active_diets"].append(diet_id)
        return settings

    def refresh(self):
        """Подтянуть сохранённые режимы из БД в форму."""
        try:
            from database.operations import load_special_diets_settings
        except ImportError:
            return

        uid = self._user_id()

        data = load_special_diets_settings(uid)
        active = list(data.get("active_diets") or [])
        if_window = data.get("if_window")

        for did, card in self.diet_cards.items():
            card.checkbox.blockSignals(True)
            card.checkbox.setChecked(did in active)
            card.checkbox.blockSignals(False)

        self.if_settings_group.setVisible("if" in active)
        if if_window is not None:
            try:
                w = int(if_window)
                w = max(self.if_slider.minimum(), min(self.if_slider.maximum(), w))
                self.if_slider.setValue(w)
            except (TypeError, ValueError):
                pass
        self.update_if_label(self.if_slider.value())
        self._apply_macro_preview(active)

    def _apply_macro_preview(self, active_diets: list) -> None:
        """Обновить круги БЖУ по выбранным режимам (без сохранения в БД)."""
        if "keto" in active_diets:
            self.fat_circle.set_value(70)
            self.protein_circle.set_value(25)
            self.carbs_circle.set_value(5)
        elif "paleo" in active_diets:
            self.fat_circle.set_value(40)
            self.protein_circle.set_value(35)
            self.carbs_circle.set_value(25)
        elif "vegan" in active_diets:
            self.fat_circle.set_value(30)
            self.protein_circle.set_value(20)
            self.carbs_circle.set_value(50)
        elif "vegetarian" in active_diets:
            self.fat_circle.set_value(35)
            self.protein_circle.set_value(25)
            self.carbs_circle.set_value(40)
        else:
            self.fat_circle.set_value(35)
            self.protein_circle.set_value(30)
            self.carbs_circle.set_value(35)

    def _schedule_autosave(self) -> None:
        """Отложенная запись в БД, чтобы галочка не терялась при смене раздела."""
        self._autosave_timer.stop()
        self._autosave_timer.start(450)

    def _flush_autosave(self) -> None:
        try:
            from database.operations import save_special_diets_settings
        except ImportError:
            return
        uid = self._user_id()
        settings = self._collect_settings()
        self._apply_macro_preview(settings["active_diets"])
        if not save_special_diets_settings(uid, settings):
            self._status_label.setText("Не удалось сохранить настройки диет в базу.")
            return
        self.diet_settings_changed.emit(settings)
        self._status_label.setText(
            "Сохранено. Активные режимы: "
            + (", ".join(settings["active_diets"]) if settings["active_diets"] else "нет")
        )
        if self.main_window:
            self.main_window.check_user()

    def handle_diet_toggle(self, diet_id: str, is_enabled: bool):
        """Обработка переключения диеты"""
        # Если включили IF, показываем настройки
        if diet_id == "if" and is_enabled:
            self.if_settings_group.setVisible(True)
        elif diet_id == "if" and not is_enabled:
            self.if_settings_group.setVisible(False)

        # Одна основная диета (кето/палео/веган/вегетарианец); ИФ можно совместить
        if is_enabled and diet_id != "if":
            for d_id, card in self.diet_cards.items():
                if d_id != diet_id and d_id != "if":
                    card.checkbox.blockSignals(True)
                    card.checkbox.setChecked(False)
                    card.checkbox.blockSignals(False)

        # Превью макросов по текущему набору галочек
        active = [d for d, c in self.diet_cards.items() if c.checkbox.isChecked()]
        self._apply_macro_preview(active)
        self._schedule_autosave()

    def update_if_label(self, value: int):
        """Обновление подписи интервального голодания"""
        fasting = 24 - value
        self.if_label.setText(f"Текущий режим: {fasting}/{value} ({fasting} часов голода, {value} часов питания)")

    def _on_if_window_changed(self, value: int) -> None:
        self.update_if_label(value)
        self._schedule_autosave()

    def save_settings(self, *_args):
        """Сбор и сохранение настроек в БД."""
        try:
            from database.operations import save_special_diets_settings
        except ImportError:
            self._status_label.setText("Ошибка: модуль базы данных недоступен.")
            return

        uid = self._user_id()

        settings = self._collect_settings()

        self._apply_macro_preview(settings["active_diets"])

        ok = save_special_diets_settings(uid, settings)
        if not ok:
            self._status_label.setText("Не удалось сохранить: пользователь не найден в базе.")
            _log.warning("save_special_diets_settings failed for uid=%s", uid)
            return

        self.diet_settings_changed.emit(settings)
        self._status_label.setText(
            "Сохранено в профиле. Активные режимы: "
            + (", ".join(settings["active_diets"]) if settings["active_diets"] else "нет (обычное питание)")
        )

        if self.main_window:
            self.main_window.check_user()

        # Визуальный эффект
        btn = self.findChild(QPushButton, "primaryButton")
        if not btn:
            return
        original_text = btn.text()
        btn.setText("✅ Сохранено!")
        btn.setStyleSheet(
            "background-color: #E8F5E9; color: #1a1a1a; border: 2px solid #1B5E20; font-weight: bold;"
        )

        from PyQt6.QtCore import QTimer

        QTimer.singleShot(1600, lambda: self.reset_save_button(btn, original_text))

    def reset_save_button(self, btn, original_text):
        btn.setText(original_text)
        btn.setStyleSheet("")
