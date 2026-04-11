# ui/pages/settings_notifications.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QCheckBox, QTimeEdit, QFrame, QScrollArea,
                             QPushButton, QGroupBox, QSizePolicy)
from PyQt6.QtCore import Qt, QTime

try:
    from config.settings import COLORS
except ImportError:
    COLORS = {}


class SettingsNotificationsPage(QWidget):
    """Страница настроек уведомлений"""

    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("🔔 Настройки уведомлений")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        subtitle = QLabel("Настройте время и типы напоминаний для здорового образа жизни")
        subtitle.setStyleSheet("color: #7F8C8D; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(subtitle)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(15)

        self.meal_group = self.create_notification_group(
            "Приёмы пищи",
            [
                ("Завтрак", "08:00"),
                ("Обед", "13:00"),
                ("Ужин", "19:00"),
                ("Перекус", "16:00")
            ]
        )
        content_layout.addWidget(self.meal_group)

        self.water_group = self.create_notification_group(
            "Водный баланс",
            [
                ("Пить воду утром", "08:30"),
                ("Пить воду днем", "12:00"),
                ("Пить воду вечером", "18:00")
            ]
        )
        content_layout.addWidget(self.water_group)

        self.health_group = self.create_notification_group(
            "Здоровье и активность",
            [
                ("Взвешивание", "09:00"),
                ("Прогулка", "18:30"),
                ("Сон", "22:30")
            ]
        )
        content_layout.addWidget(self.health_group)

        self.motivation_group = self.create_notification_group(
            "Мотивация",
            [
                ("Утреннее вдохновение", "07:30"),
                ("Итоги дня", "21:00")
            ]
        )
        content_layout.addWidget(self.motivation_group)

        content_layout.addStretch()
        content_widget.setLayout(content_layout)
        scroll.setWidget(content_widget)

        layout.addWidget(scroll)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        save_btn = QPushButton("💾 Сохранить настройки")
        save_btn.setObjectName("primaryBtn")
        save_btn.setFixedWidth(200)
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def create_notification_group(self, title, items):
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                margin-top: 15px;
                padding-top: 15px;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(10)

        for label_text, default_time in items:
            row = QHBoxLayout()

            check = QCheckBox(label_text)
            check.setChecked(True)
            check.setStyleSheet("font-weight: normal; font-size: 14px;")

            time_edit = QTimeEdit()
            h, m = map(int, default_time.split(':'))
            time_edit.setTime(QTime(h, m))
            time_edit.setDisplayFormat("HH:mm")
            time_edit.setFixedWidth(100)

            row.addWidget(check)
            row.addStretch()
            row.addWidget(time_edit)

            layout.addLayout(row)

        group.setLayout(layout)
        return group

    def save_settings(self):
        print("Настройки уведомлений сохранены!")
