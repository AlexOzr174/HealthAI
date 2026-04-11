# ui/pages/ai_chat.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTextEdit, QLineEdit,
                             QPushButton, QHBoxLayout, QScrollArea, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

try:
    from config.settings import COLORS
except ImportError:
    COLORS = {
        'surface': '#FFFFFF',
        'background': '#F0F2F5',
        'primary': '#3498DB',
        'primary_dark': '#2980B9',
        'text_primary': '#2C3E50',
        'text_secondary': '#7F8C8D',
    }

# Импорт AI-движка
try:
    from ai_engine import AIEngine
except ImportError:
    AIEngine = None
    print("WARNING: AI Engine не найден. Чат будет работать в ограниченном режиме.")


class MessageBubble(QFrame):
    """Виджет сообщения в чате"""

    def __init__(self, sender: str, text: str, is_user: bool = False):
        super().__init__()
        self.setup_ui(sender, text, is_user)

    def setup_ui(self, sender, text, is_user):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        bubble = QLabel(f"<b>{sender}:</b><br>{text}")
        bubble.setWordWrap(True)
        bubble.setTextFormat(Qt.TextFormat.RichText)
        bubble.setMaximumWidth(500)

        if is_user:
            bubble.setStyleSheet(f"""
                background-color: {COLORS['primary']};
                color: white;
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 13px;
            """)
            layout.addStretch()
            layout.addWidget(bubble)
        else:
            bubble.setStyleSheet(f"""
                background-color: {COLORS['surface']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border'] if 'border' in COLORS else '#E0E0E0'};
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 13px;
            """)
            layout.addWidget(bubble)
            layout.addStretch()


class AIChatPage(QWidget):
    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window

        # Инициализация AI
        self.ai_engine = None
        if AIEngine:
            self.ai_engine = AIEngine()
            # Если есть пользователь, инициализируем контекст
            if self.main_window and self.main_window.current_user:
                user = self.main_window.current_user
                profile = {
                    'name': user.name,
                    'weight': user.weight,
                    'height': user.height,
                    'age': user.age,
                    'gender': user.gender,
                    'goal': user.goal,
                    'activity_level': user.activity_level,
                    'diet_type': user.diet_type
                }
                self.ai_engine.initialize_user(user.id, profile)

        self.setup_ui()
        self.add_welcome_message()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("🤖 AI Нутрициолог")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        # Область чата
        self.chat_area = QScrollArea()
        self.chat_area.setWidgetResizable(True)
        self.chat_area.setStyleSheet("border: none; background-color: transparent;")

        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setSpacing(10)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)

        self.chat_area.setWidget(self.chat_container)
        layout.addWidget(self.chat_area)

        # Поле ввода
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Задайте вопрос о питании...")
        self.input_field.returnPressed.connect(self.send_message)

        send_btn = QPushButton("Отправить")
        send_btn.setObjectName("primaryBtn")
        send_btn.clicked.connect(self.send_message)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(send_btn)
        layout.addLayout(input_layout)

    def add_welcome_message(self):
        """Добавление приветственного сообщения"""
        welcome_text = "Здравствуйте! Я ваш персональный ИИ-нутрициолог. Задайте мне вопрос о питании, расчёте калорий или получите персональные рекомендации."
        self.add_message("AI", welcome_text, is_user=False)

    def add_message(self, sender: str, text: str, is_user: bool = False):
        """Добавление сообщения в чат"""
        bubble = MessageBubble(sender, text, is_user)
        self.chat_layout.addWidget(bubble)
        # Прокрутка вниз
        QTimer.singleShot(50, lambda: self.chat_area.verticalScrollBar().setValue(
            self.chat_area.verticalScrollBar().maximum()
        ))

    def send_message(self):
        """Отправка сообщения"""
        text = self.input_field.text().strip()
        if not text:
            return

        # Добавляем сообщение пользователя
        self.add_message("Вы", text, is_user=True)
        self.input_field.clear()

        # Получаем ответ от AI
        if self.ai_engine and self.main_window and self.main_window.current_user:
            user_id = self.main_window.current_user.id
            response = self.ai_engine.chat(user_id, text)
            ai_response = response.get('message', 'Извините, произошла ошибка.')
        else:
            # Заглушка если AI не доступен
            ai_response = self.get_mock_response(text)

        # Имитация задержки ответа
        QTimer.singleShot(500, lambda: self.add_message("AI", ai_response, is_user=False))

    def get_mock_response(self, user_message: str) -> str:
        """Заглушка ответа, если AI не инициализирован"""
        msg_lower = user_message.lower()
        if 'привет' in msg_lower:
            return "Здравствуйте! Чем могу помочь?"
        elif 'калори' in msg_lower:
            return "Для расчёта нормы калорий мне нужны ваши данные (вес, рост, возраст, активность). Введите их в профиле."
        elif 'белок' in msg_lower or 'протеин' in msg_lower:
            return "Рекомендуемая норма белка: 1.2-2.0 г на кг веса в зависимости от целей."
        elif 'вода' in msg_lower:
            return "Рекомендуется выпивать около 30 мл воды на 1 кг веса в день."
        else:
            return "Интересный вопрос! В полной версии я смогу дать более точный ответ с учётом вашего профиля."