# Переключатель темы для HealthAI
from PyQt6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QLabel
from PyQt6.QtCore import pyqtSignal
from ui.styles import toggle_theme, Styles
from config.settings import COLORS


class ThemeToggle(QWidget):
    """
    Переключатель светлой/тёмной темы.
    """
    
    theme_changed = pyqtSignal(str)  # Сигнал при смене темы
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Иконка солнца
        self.sun_icon = QLabel("☀️")
        self.sun_icon.setStyleSheet("font-size: 18px;")
        layout.addWidget(self.sun_icon)
        
        # Кнопка переключения
        self.toggle_button = QPushButton()
        self.toggle_button.setFixedSize(60, 32)
        self.update_button_style()
        self.toggle_button.clicked.connect(self.on_toggle)
        layout.addWidget(self.toggle_button)
        
        # Иконка луны
        self.moon_icon = QLabel("🌙")
        self.moon_icon.setStyleSheet("font-size: 18px;")
        layout.addWidget(self.moon_icon)
        
    def update_button_style(self):
        """Обновление стиля кнопки"""
        is_dark = COLORS.get('background') == '#121212'
        
        if is_dark:
            self.toggle_button.setStyleSheet("""
                QPushButton {
                    background-color: #2E7D32;
                    border-radius: 16px;
                }
                QPushButton::handle {
                    background-color: white;
                    border-radius: 14px;
                    width: 28px;
                    height: 28px;
                    margin: 2px;
                }
            """)
        else:
            self.toggle_button.setStyleSheet("""
                QPushButton {
                    background-color: #81C784;
                    border-radius: 16px;
                }
            """)
            
    def on_toggle(self):
        """Обработка переключения темы"""
        new_theme = toggle_theme()
        self.theme_changed.emit(new_theme)
        self.update_button_style()
        
    def get_current_theme(self) -> str:
        """Получение текущей темы"""
        return 'dark' if COLORS.get('background') == '#121212' else 'light'
