"""
AI Chat Widget - Интерфейс чата с нутрициологом
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QLineEdit, QPushButton, QLabel, QScrollArea, 
                             QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

class ChatMessage(QFrame):
    """Виджет отдельного сообщения в чате"""
    def __init__(self, text, is_user=True, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.setup_ui(text)
        
    def setup_ui(self, text):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Стиль сообщения
        if self.is_user:
            self.setStyleSheet("""
                QFrame {
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 15px;
                    margin-left: 50px;
                }
            """)
            alignment = Qt.AlignmentFlag.AlignRight
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #f0f0f0;
                    color: #333;
                    border-radius: 15px;
                    margin-right: 50px;
                }
            """)
            alignment = Qt.AlignmentFlag.AlignLeft
            
        # Текст сообщения
        label = QLabel(text)
        label.setWordWrap(True)
        label.setFont(QFont("Arial", 10))
        label.setAlignment(alignment | Qt.AlignmentFlag.AlignTop)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(label)
        
        # Максимальная ширина
        self.setMaximumWidth(400)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)


class AIChatWidget(QWidget):
    """Основной виджет чата с ИИ"""
    def __init__(self, ai_engine, user_id, parent=None):
        super().__init__(parent)
        self.ai_engine = ai_engine
        self.user_id = user_id
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Заголовок
        header = QLabel("🤖 AI Нутрициолог")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setStyleSheet("padding: 15px; background-color: transparent; color: #2c3e50;")
        main_layout.addWidget(header)
        
        # Область чата
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.chat_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f9f9f9;
            }
        """)
        
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setSpacing(10)
        self.chat_layout.addStretch()
        
        self.chat_scroll.setWidget(self.chat_container)
        main_layout.addWidget(self.chat_scroll, 1)
        
        # Приветственное сообщение
        self.add_message("Здравствуйте! Я ваш персональный AI-нутрициолог. Спросите меня о питании, диетах, витаминах или попросите совет по здоровью!", is_user=False)
        
        # Поле ввода
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(15, 15, 15, 15)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Введите ваш вопрос...")
        self.input_field.setFont(QFont("Arial", 11))
        self.input_field.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 25px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        
        self.send_button = QPushButton("➤")
        self.send_button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.send_button.setFixedSize(50, 50)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 25px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        main_layout.addLayout(input_layout)
        
    def add_message(self, text, is_user=True):
        """Добавить сообщение в чат"""
        message = ChatMessage(text, is_user)
        # Вставляем перед растягивающим элементом
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, message)
        
        # Прокрутка вниз
        QTimer.singleShot(100, lambda: self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()
        ))
        
    def send_message(self):
        """Отправить сообщение и получить ответ"""
        text = self.input_field.text().strip()
        if not text:
            return
            
        # Добавляем сообщение пользователя
        self.add_message(text, is_user=True)
        self.input_field.clear()
        
        # Имитация задержки ответа
        self.input_field.setEnabled(False)
        self.send_button.setEnabled(False)
        
        # Получаем ответ от AI
        try:
            response = self.ai_engine.chat(user_id=self.user_id, message=text)
            self.add_message(response, is_user=False)
        except Exception as e:
            self.add_message(f"Извините, произошла ошибка: {str(e)}", is_user=False)
        finally:
            self.input_field.setEnabled(True)
            self.send_button.setEnabled(True)
            self.input_field.setFocus()
