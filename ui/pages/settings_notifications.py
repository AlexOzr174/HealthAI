"""
UI Компоненты для настроек умных уведомлений.
Позволяет пользователю настраивать время напоминаний, типы уведомлений и частоту.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QPushButton, QTimeEdit, QCheckBox, QScrollArea, QFrame, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QTime, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from ui.styles import Styles


class NotificationSettingItem(QWidget):
    """Один элемент настройки уведомления (чекбокс + время + описание)"""
    
    state_changed = pyqtSignal(str, bool, QTime)
    
    def __init__(self, notify_id: str, title: str, description: str, default_time: QTime, parent=None):
        super().__init__(parent)
        self.notify_id = notify_id
        self.setFixedHeight(80)
        
        # Основной лейаут
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)
        
        # Чекбокс
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(True)
        self.checkbox.stateChanged.connect(self._on_state_change)
        layout.addWidget(self.checkbox)
        
        # Контейнер для текста и времени
        content_layout = QVBoxLayout()
        content_layout.setSpacing(5)
        
        # Заголовок
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        content_layout.addWidget(title_label)
        
        # Описание
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Segoe UI", 9))
        desc_label.setStyleSheet("color: #777;")
        content_layout.addWidget(desc_label)
        
        layout.addLayout(content_layout, 1)
        
        # Редактор времени
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(default_time)
        self.time_edit.setDisplayFormat("HH:mm")
        self.time_edit.setCalendarPopup(False)
        self.time_edit.setFixedWidth(100)
        self.time_edit.timeChanged.connect(self._on_state_change)
        layout.addWidget(self.time_edit)
        
    def _on_state_change(self):
        """Эмит сигнала об изменении"""
        self.state_changed.emit(self.notify_id, self.checkbox.isChecked(), self.time_edit.time())


class NotificationsSettingsPage(QWidget):
    """Страница настроек уведомлений"""
    
    settings_saved = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("notificationsPage")
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Заголовок
        header = QLabel("🔔 Умные уведомления")
        header.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        layout.addWidget(header)
        
        subtitle = QLabel("Настройте время и типы напоминаний, чтобы не пропускать приемы пищи и воду.")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #666; margin-bottom: 20px;")
        layout.addWidget(subtitle)
        
        # Скролл область для настроек
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        container = QWidget()
        self.settings_layout = QVBoxLayout(container)
        self.settings_layout.setSpacing(15)
        
        # Группы настроек
        self.settings_widgets = {}
        
        # 1. Приемы пищи
        meal_group = self.create_group("Приемы пищи")
        meal_layout = QVBoxLayout()
        
        meals = [
            ("breakfast", "Завтрак", "Пора позавтракать и зарядиться энергией!", QTime(8, 0)),
            ("lunch", "Обед", "Время полноценного обеда. Не забудьте про белок!", QTime(13, 0)),
            ("dinner", "Ужин", "Легкий ужин за 3 часа до сна.", QTime(19, 0)),
            ("snack", "Перекус", "Время для полезного перекуса.", QTime(16, 0)),
        ]
        
        for m_id, title, desc, time in meals:
            item = NotificationSettingItem(m_id, title, desc, time)
            item.state_changed.connect(self.handle_setting_change)
            self.settings_widgets[m_id] = item
            meal_layout.addWidget(item)
            
        meal_group.setLayout(meal_layout)
        self.settings_layout.addWidget(meal_group)
        
        # 2. Вода и здоровье
        health_group = self.create_group("Вода и здоровье")
        health_layout = QVBoxLayout()
        
        health_items = [
            ("water", "Пить воду", "Напоминание пить стакан воды каждые 2 часа.", QTime(10, 0)),
            ("weigh_in", "Взвешивание", "Ежедневное взвешивание утром натощак.", QTime(8, 30)),
            ("sleep", "Отбой", "Пора готовиться ко сну для качественного восстановления.", QTime(22, 30)),
        ]
        
        for h_id, title, desc, time in health_items:
            item = NotificationSettingItem(h_id, title, desc, time)
            item.state_changed.connect(self.handle_setting_change)
            self.settings_widgets[h_id] = item
            health_layout.addWidget(item)
            
        health_group.setLayout(health_layout)
        self.settings_layout.addWidget(health_group)
        
        # 3. Мотивация
        motiv_group = self.create_group("Мотивация")
        motiv_layout = QVBoxLayout()
        
        motiv_items = [
            ("motivation_daily", "Дневная мотивация", "Получать вдохновляющую цитату дня.", QTime(9, 0)),
            ("goal_progress", "Прогресс цели", "Еженедельный отчет о достижении целей.", QTime(20, 0)),
        ]
        
        for m_id, title, desc, time in motiv_items:
            item = NotificationSettingItem(m_id, title, desc, time)
            item.state_changed.connect(self.handle_setting_change)
            self.settings_widgets[m_id] = item
            motiv_layout.addWidget(item)
            
        motiv_group.setLayout(motiv_layout)
        self.settings_layout.addWidget(motiv_group)
        
        self.settings_layout.addStretch()
        
        scroll.setWidget(container)
        layout.addWidget(scroll, 1)
        
        # Кнопка сохранения
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        save_btn = QPushButton("💾 Сохранить настройки")
        save_btn.setFixedHeight(45)
        save_btn.setFixedWidth(200)
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        
    def create_group(self, title: str) -> QGroupBox:
        group = QGroupBox(title)
        group.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        group.setStyleSheet("""
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
        return group
        
    def handle_setting_change(self, notify_id: str, is_enabled: bool, time: QTime):
        """Обрабатывает изменения в реальном времени (можно использовать для превью)"""
        pass
        
    def save_settings(self):
        """Собирает все настройки и отправляет сигнал"""
        settings = {}
        for n_id, widget in self.settings_widgets.items():
            settings[n_id] = {
                'enabled': widget.checkbox.isChecked(),
                'time': widget.time_edit.time().toString("HH:mm")
            }
        self.settings_saved.emit(settings)
        
        # Визуальный эффект сохранения
        btn = self.findChild(QPushButton, "primaryButton")
        original_text = btn.text()
        btn.setText("✅ Сохранено!")
        btn.setStyleSheet("background-color: #2ecc71; color: white;")
        
        # Возврат через 1 сек
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1000, lambda: self.reset_save_button(btn, original_text))
        
    def reset_save_button(self, btn, original_text):
        btn.setText(original_text)
        btn.setStyleSheet("")
