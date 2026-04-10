from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QDateEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, QDate


class AnalyticsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        title = QLabel("📈 Аналитика")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        filters = QHBoxLayout()
        period = QComboBox()
        period.addItems(["Неделя", "Месяц", "Год"])
        start_date = QDateEdit()
        start_date.setDate(QDate.currentDate().addDays(-7))
        end_date = QDateEdit()
        end_date.setDate(QDate.currentDate())

        filters.addWidget(QLabel("Период:"))
        filters.addWidget(period)
        filters.addWidget(QLabel("С:"))
        filters.addWidget(start_date)
        filters.addWidget(QLabel("По:"))
        filters.addWidget(end_date)
        filters.addStretch()

        layout.addLayout(filters)

        chart_placeholder = QLabel("Здесь будут графики веса, калорий и макросов\n(Требуется matplotlib/plotly)")
        chart_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_placeholder.setStyleSheet("border: 2px dashed #CCC; padding: 50px; font-size: 16px; color: #777;")
        layout.addWidget(chart_placeholder)

        layout.addStretch()
        self.setLayout(layout)