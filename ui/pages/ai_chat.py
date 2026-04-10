from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QLineEdit, QPushButton, QHBoxLayout, QScrollArea
from PyQt6.QtCore import Qt
Qt.AlignmentFlag.AlignCenter
Qt.AlignmentFlag.AlignLeft
Qt.ScrollBarPolicy.ScrollBarAlwaysOff


class AIChatPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        title = QLabel("🤖 AI Нутрициолог")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        self.chat_area = QScrollArea()
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_widget.setLayout(self.chat_layout)
        self.chat_area.setWidgetResizable(True)
        self.chat_area.setWidget(self.chat_widget)
        layout.addWidget(self.chat_area)

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

        self.add_message("AI", "Здравствуйте! Я ваш персональный нутрициолог. Чем могу помочь?")
        self.setLayout(layout)

    def add_message(self, sender, text):
        label = QLabel(f"<b>{sender}:</b> {text}")
        label.setWordWrap(True)
        label.setStyleSheet("padding: 10px; background-color: #F0F2F5; border-radius: 8px; margin: 5px;")
        self.chat_layout.addWidget(label)
        self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())

    def send_message(self):
        text = self.input_field.text()
        if not text:
            return
        self.add_message("Вы", text)
        self.input_field.clear()
        # Имитация ответа
        self.add_message("AI", "Спасибо за вопрос! В полной версии я проанализирую его с помощью AI.")