from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, \
    QHBoxLayout
from PyQt6.QtCore import Qt
Qt.AlignmentFlag.AlignCenter
Qt.AlignmentFlag.AlignLeft
Qt.ScrollBarPolicy.ScrollBarAlwaysOff


class ProductsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        title = QLabel("🍎 Продукты")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        search_layout = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Поиск продукта...")
        search_btn = QPushButton("Найти")
        search_layout.addWidget(self.search)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Продукт", "Ккал", "Белки", "Жиры", "Углеводы"])
        layout.addWidget(self.table)

        self.load_products()
        self.setLayout(layout)

    def load_products(self):
        # Заглушка данных
        products = [
            ("Яблоко", 52, 0.3, 0.2, 14),
            ("Банан", 89, 1.1, 0.3, 23),
            ("Куриная грудка", 165, 31, 3.6, 0),
            ("Рис", 130, 2.7, 0.3, 28),
        ]
        self.table.setRowCount(len(products))
        for i, (name, cal, p, f, c) in enumerate(products):
            self.table.setItem(i, 0, QTableWidgetItem(name))
            self.table.setItem(i, 1, QTableWidgetItem(str(cal)))
            self.table.setItem(i, 2, QTableWidgetItem(str(p)))
            self.table.setItem(i, 3, QTableWidgetItem(str(f)))
            self.table.setItem(i, 4, QTableWidgetItem(str(c)))