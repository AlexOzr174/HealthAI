# ui/pages/photo_analysis.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
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
    """Страница анализа фото еды — виджет загрузки и распознавания."""

    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("📸 Анализ фото еды")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel(
            "Загрузите фото: ResNet50 + ImageNet. Названия в карточках — на русском "
            "(словарь приложения; при включённой Ollama уточняются по англ. подписи классификатора). "
            "Развёрнутый разбор — через Ollama."
        )
        subtitle.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        from ui.widgets.photo_upload import PhotoUploadWidget

        self.uploader = PhotoUploadWidget(self, main_window=self.main_window)
        layout.addWidget(self.uploader, 1)
