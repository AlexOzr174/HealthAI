"""
Виджет чата с AI нутрициологом
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QPushButton, QLabel, QScrollArea, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from ui.styles import CURRENT_THEME


class ChatMessageWidget(QFrame):
    """Одиночное сообщение в чате"""
    
    def __init__(self, message: str, is_user: bool = True, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.init_ui(message)
        
    def init_ui(self, message):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setMaximumWidth(500)
        self.setMinimumWidth(200)
        
        # Стили для пользователя и бота
        if self.is_user:
            bg_color = "#4CAF50"
            text_color = "#FFFFFF"
            alignment = Qt.AlignmentFlag.AlignRight
        else:
            bg_color = CURRENT_THEME['card_bg']
            text_color = CURRENT_THEME['text_primary']
            alignment = Qt.AlignmentFlag.AlignLeft
            
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 15px;
                padding: 12px;
                margin: 5px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Текст сообщения
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        message_label.setStyleSheet(f"""
            color: {text_color};
            font-size: 14px;
            line-height: 1.5;
        """)
        message_label.setFont(QFont('Arial', 13))
        layout.addWidget(message_label)


class AIChatWidget(QWidget):
    """Основной виджет чата с AI нутрициологом"""
    
    message_sent = pyqtSignal(str)  # Сигнал при отправке сообщения
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Заголовок
        header = QLabel("🤖 AI Нутрициолог")
        header.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: %s;
            padding: 15px;
            background-color: %s;
            border-bottom: 2px solid %s;
        """ % (
            CURRENT_THEME['text_primary'],
            CURRENT_THEME['card_bg'],
            CURRENT_THEME['border']
        ))
        layout.addWidget(header)
        
        # Область сообщений
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: %s;
            }
        """ % CURRENT_THEME['bg'])
        
        # Контейнер для сообщений
        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setSpacing(10)
        self.messages_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Добавляем начальные сообщения
        self.add_bot_message("Привет! Я ваш персональный AI нутрициолог. "
                           "Задавайте мне любые вопросы о питании, диетах, продуктах "
                           "или попросите составить план питания! 🥗")
        
        self.scroll_area.setWidget(self.messages_container)
        layout.addWidget(self.scroll_area, 1)
        
        # Поле ввода
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background-color: %s;
                border-top: 1px solid %s;
                padding: 10px;
            }
        """ % (CURRENT_THEME['card_bg'], CURRENT_THEME['border']))
        
        input_layout = QHBoxLayout(input_frame)
        input_layout.setSpacing(10)
        
        # Текстовое поле
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("Введите ваш вопрос...")
        self.input_field.setMaximumHeight(80)
        self.input_field.setMinimumHeight(50)
        self.input_field.setStyleSheet("""
            QTextEdit {
                background-color: %s;
                color: %s;
                border: 2px solid %s;
                border-radius: 20px;
                padding: 10px 15px;
                font-size: 14px;
            }
            QTextEdit:focus {
                border: 2px solid #4CAF50;
            }
        """ % (
            CURRENT_THEME['input_bg'],
            CURRENT_THEME['text_primary'],
            CURRENT_THEME['border']
        ))
        self.input_field.setFont(QFont('Arial', 13))
        
        # Обработка Enter для отправки
        self.input_field.installEventFilter(self)
        
        input_layout.addWidget(self.input_field, 1)
        
        # Кнопка отправки
        send_button = QPushButton("➤")
        send_button.setFixedSize(50, 50)
        send_button.setCursor(Qt.CursorShape.PointingHandCursor)
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #1a1a1a;
                border: 2px solid #1a1a1a;
                border-radius: 25px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E8F5E9;
            }
            QPushButton:pressed {
                background-color: #C8E6C9;
            }
        """)
        send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(send_button)
        layout.addWidget(input_frame)
        
    def eventFilter(self, obj, event):
        """Перехват нажатия Enter"""
        from PyQt6.QtCore import QEvent
        from PyQt6.QtGui import QKeyEvent
        
        if obj == self.input_field and event.type() == QEvent.Type.KeyPress:
            key_event = QKeyEvent(event)
            if key_event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                if not (key_event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
                    self.send_message()
                    return True
        return super().eventFilter(obj, event)
    
    def send_message(self):
        """Отправить сообщение"""
        message = self.input_field.toPlainText().strip()
        if message:
            self.add_user_message(message)
            self.message_sent.emit(message)
            self.input_field.clear()
            
    def add_user_message(self, message: str):
        """Добавить сообщение пользователя"""
        widget = ChatMessageWidget(message, is_user=True)
        self.messages_layout.addWidget(widget, alignment=Qt.AlignmentFlag.AlignRight)
        self.scroll_to_bottom()
        
    def add_bot_message(self, message: str):
        """Добавить ответ бота"""
        widget = ChatMessageWidget(message, is_user=False)
        self.messages_layout.addWidget(widget, alignment=Qt.AlignmentFlag.AlignLeft)
        self.scroll_to_bottom()
        
    def scroll_to_bottom(self):
        """Прокрутить вниз"""
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def clear_chat(self):
        """Очистить чат"""
        while self.messages_layout.count():
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
