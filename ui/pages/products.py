# ui/pages/products.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
                             QTableWidget, QTableWidgetItem, QHBoxLayout)
from PyQt6.QtCore import Qt

try:
    from config.settings import COLORS
except ImportError:
    COLORS = {
        'surface': '#FFFFFF',
        'primary': '#3498DB',
        'text_primary': '#2C3E50',
        'border': '#E0E0E0',
    }

from database.operations import get_all_products, search_products


class ProductsPage(QWidget):
    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.all_products = []
        self.setup_ui()
        self.load_products()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("🍎 Продукты")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        # Панель поиска
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск продукта...")
        self.search_input.textChanged.connect(self.filter_products)
        search_btn = QPushButton("Найти")
        search_btn.setObjectName("primaryBtn")
        search_btn.clicked.connect(self.filter_products)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)

        # Таблица продуктов
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Продукт", "Ккал", "Белки", "Жиры", "Углеводы"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                gridline-color: {COLORS['border']};
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
            QHeaderView::section {{
                background-color: {COLORS['surface']};
                padding: 10px;
                border: none;
                border-bottom: 1px solid {COLORS['border']};
                font-weight: bold;
                color: {COLORS['text_primary']};
            }}
        """)
        layout.addWidget(self.table)

    def load_products(self):
        """Загрузка продуктов из базы данных"""
        self.all_products = get_all_products()
        self.display_products(self.all_products)

    def filter_products(self):
        """Фильтрация продуктов по поисковому запросу"""
        query = self.search_input.text().strip()
        if not query:
            self.display_products(self.all_products)
        else:
            filtered = search_products(query, limit=100)
            self.display_products(filtered)

    def display_products(self, products):
        """Отображение списка продуктов в таблице"""
        self.table.setRowCount(len(products))
        for i, product in enumerate(products):
            self.table.setItem(i, 0, QTableWidgetItem(product.name))
            self.table.setItem(i, 1, QTableWidgetItem(f"{int(product.calories)}"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{product.protein:.1f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{product.fat:.1f}"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{product.carbs:.1f}"))
