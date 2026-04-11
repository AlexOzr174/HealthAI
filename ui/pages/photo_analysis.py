# ui/pages/photo_analysis.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt

try:
    from config.settings import COLORS
except ImportError:
    COLORS = {
        'surface': '#FFFFFF',
        'primary': '#3498DB',
        'primary_hover': '#2980B9',
        'text_primary': '#2C3E50',
        'text_secondary': '#7F8C8D',
        'border': '#BDC3C7',
    }


class PhotoAnalysisPage(QWidget):
    """Страница анализа фото еды"""

    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Заголовок
        title = QLabel("📸 Анализ фото еды")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Загрузите фото блюда для автоматического определения состава и калорийности")
        subtitle.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 14px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        # Область загрузки
        upload_area = QFrame()
        upload_area.setObjectName("card")
        upload_area.setMinimumHeight(300)
        upload_area.setStyleSheet(f"""
            QFrame#card {{
                border: 2px dashed {COLORS['border']};
                border-radius: 12px;
                background-color: {COLORS['surface']};
            }}
        """)

        area_layout = QVBoxLayout(upload_area)
        area_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_label = QLabel("📷")
        icon_label.setStyleSheet("font-size: 48px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        area_layout.addWidget(icon_label)

        text_label = QLabel("Перетащите фото сюда\nили нажмите кнопку ниже")
        text_label.setStyleSheet(f"font-size: 16px; color: {COLORS['text_secondary']};")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        area_layout.addWidget(text_label)

        upload_btn = QPushButton("📁 Выбрать фото")
        upload_btn.setObjectName("primaryBtn")
        upload_btn.setFixedWidth(200)
        upload_btn.clicked.connect(self.upload_photo)
        area_layout.addWidget(upload_btn)

        layout.addWidget(upload_area)
        layout.addStretch()

    def upload_photo(self):
        """Загрузка и анализ фото (заглушка)"""
        print("Функция загрузки фото будет реализована в следующей версии")
