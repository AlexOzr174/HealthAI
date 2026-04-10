# Умный поиск для HealthAI
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QLineEdit, QPushButton, 
                             QLabel, QCompleter, QVBoxLayout, QListWidget,
                             QFrame, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

from config.settings import COLORS
from ui.styles import Styles


class SmartSearchWidget(QWidget):
    """
    Виджет умного поиска с автодополнением и фильтрацией.
    Поддерживает поиск продуктов, рецептов и категорий.
    """
    
    search_triggered = pyqtSignal(str)  # Сигнал при поиске
    item_selected = pyqtSignal(dict)    # Сигнал при выборе элемента
    
    def __init__(self, parent=None, placeholder: str = "Поиск продуктов, рецептов..."):
        super().__init__(parent)
        
        self.search_data = []  # Данные для поиска
        self.filtered_data = []
        
        self.setup_ui(placeholder)
        self.setup_completer()
        self.setup_shadow()
        
    def setup_ui(self, placeholder: str):
        """Настройка интерфейса"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Иконка поиска
        self.search_icon = QLabel("🔍")
        self.search_icon.setStyleSheet("""
            font-size: 18px;
            padding: 4px;
        """)
        layout.addWidget(self.search_icon)
        
        # Поле ввода
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(placeholder)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                border: 2px solid #E0E0E0;
                border-radius: 25px;
                padding: 12px 16px;
                font-size: 14px;
                selection-background-color: #81C784;
            }
            QLineEdit:focus {
                border-color: #2E7D32;
            }
        """)
        self.search_input.textChanged.connect(self.on_search_changed)
        self.search_input.returnPressed.connect(self.on_search_triggered)
        layout.addWidget(self.search_input, stretch=1)
        
        # Кнопка очистки
        self.clear_button = QPushButton("✕")
        self.clear_button.setFixedSize(32, 32)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 16px;
                color: #9E9E9E;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #F5F7FA;
                color: #212121;
            }
        """)
        self.clear_button.clicked.connect(self.clear_search)
        self.clear_button.setVisible(False)
        layout.addWidget(self.clear_button)
        
        # Кнопка поиска
        self.search_button = QPushButton("Найти")
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #2E7D32;
                color: white;
                border: none;
                border-radius: 20px;
                padding: 10px 20px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)
        self.search_button.clicked.connect(self.on_search_triggered)
        layout.addWidget(self.search_button)
        
    def setup_completer(self):
        """Настройка автодополнения"""
        self.completer = QCompleter(self)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setMaxVisibleItems(10)
        
        # Стиль для выпадающего списка
        self.completer.popup().setStyleSheet("""
            QListView {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 4px;
            }
            QListView::item {
                padding: 8px 12px;
                border-radius: 4px;
            }
            QListView::item:selected {
                background-color: #81C784;
                color: white;
            }
            QListView::item:hover {
                background-color: #E8F5E9;
            }
        """)
        
        self.search_input.setCompleter(self.completer)
        
    def setup_shadow(self):
        """Добавление тени"""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(Qt.GlobalColor.black)
        self.setGraphicsEffect(shadow)
        
    def set_search_data(self, data: list):
        """
        Установка данных для поиска.
        
        Args:
            data: Список словарей с ключами 'name', 'category', 'type'
        """
        self.search_data = data
        self.update_completer()
        
    def update_completer(self):
        """Обновление списка автодополнения"""
        names = [item['name'] for item in self.search_data]
        self.completer.setModel(strings=names)
        
    def on_search_changed(self, text: str):
        """Обработка изменения текста поиска"""
        self.clear_button.setVisible(bool(text))
        
        if len(text) < 2:
            self.filtered_data = []
            return
            
        # Фильтрация данных
        text_lower = text.lower()
        self.filtered_data = [
            item for item in self.search_data
            if text_lower in item['name'].lower() or
               text_lower in item.get('category', '').lower()
        ]
        
        # Обновление автодополнения
        matches = [item['name'] for item in self.filtered_data[:10]]
        self.completer.setModel(strings=matches)
        
    def on_search_triggered(self):
        """Обработка нажатия кнопки поиска"""
        query = self.search_input.text().strip()
        if query:
            self.search_triggered.emit(query)
            
    def clear_search(self):
        """Очистка поиска"""
        self.search_input.clear()
        self.clear_button.setVisible(False)
        self.filtered_data = []
        
    def get_filtered_results(self) -> list:
        """Получение отфильтрованных результатов"""
        return self.filtered_data


class SearchSuggestionsPopup(QFrame):
    """Всплывающее окно с подсказками поиска"""
    
    item_selected = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup)
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
        """)
        
        self.suggestions_list = QListWidget()
        self.suggestions_list.setStyleSheet("""
            QListWidget {
                border: none;
                outline: none;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #81C784;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #E8F5E9;
            }
        """)
        self.suggestions_list.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.suggestions_list)
        
        self.setMaximumHeight(300)
        self.setMinimumWidth(300)
        
    def show_suggestions(self, suggestions: list, position):
        """
        Показать подсказки.
        
        Args:
            suggestions: Список словарей с данными
            position: Позиция для отображения
        """
        self.suggestions_list.clear()
        
        for item in suggestions[:8]:  # Максимум 8 подсказок
            display_text = f"{item['name']} ({item.get('category', '')})"
            self.suggestions_list.addItem(display_text)
            self.suggestions_list.item(self.suggestions_list.count() - 1).setData(
                Qt.ItemDataRole.UserRole, item
            )
        
        self.move(position)
        self.show()
        
    def on_item_clicked(self, item):
        """Обработка клика по элементу"""
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            self.item_selected.emit(data)
            self.hide()
