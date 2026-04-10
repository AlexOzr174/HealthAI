from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt
from ui.styles import Styles


class PhotoAnalysisPage(QWidget):
    """Страница анализа фото еды"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Заголовок
        title = QLabel("📸 Анализ фото еды")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Загрузите фото блюда для автоматического определения состава и калорийности")
        subtitle.setStyleSheet("color: #7F8C8D; font-size: 14px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        # Область загрузки
        upload_area = QFrame()
        upload_area.setObjectName("card")
        upload_area.setMinimumHeight(300)
        upload_area.setStyleSheet("""
            QFrame#card {
                border: 2px dashed #BDC3C7;
                border-radius: 12px;
                background-color: transparent;
            }
        """)

        area_layout = QVBoxLayout(upload_area)
        area_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_label = QLabel("📷")
        icon_label.setStyleSheet("font-size: 48px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        area_layout.addWidget(icon_label)

        text_label = QLabel("Перетащите фото сюда\nили нажмите кнопку ниже")
        text_label.setStyleSheet("font-size: 16px; color: #7F8C8D;")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        area_layout.addWidget(text_label)

        upload_btn = QPushButton("📁 Выбрать фото")
        upload_btn.setObjectName("primaryBtn")
        upload_btn.setFixedWidth(200)
        # upload_btn.clicked.connect(self.upload_photo)  # Будет реализовано позже
        area_layout.addWidget(upload_btn)

        layout.addWidget(upload_area)
        layout.addStretch()

        self.setLayout(layout)

    def upload_photo(self):
        """Загрузка и анализ фото (заглушка)"""
        print("Функция загрузки фото будет реализована в следующей версии")
