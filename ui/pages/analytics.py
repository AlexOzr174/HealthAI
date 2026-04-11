# ui/pages/analytics.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QPushButton, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime, timedelta
import numpy as np

# ---------- ВАЖНО: настройка matplotlib ДО импорта pyplot ----------
import matplotlib

matplotlib.use('Qt5Agg')  # Используем бэкенд, совместимый с PyQt6
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# --------------------------------------------------------------------

try:
    from config.settings import COLORS
except ImportError:
    COLORS = {
        'surface': '#FFFFFF',
        'background': '#F0F2F5',
        'primary': '#3498DB',
        'primary_dark': '#2980B9',
        'text_primary': '#2C3E50',
        'text_secondary': '#7F8C8D',
        'warning': '#F39C12',
    }

from database.operations import get_user_stats, get_meals_by_date_range
from core.calculator import calculate_bmr, calculate_tdee


class MatplotlibCanvas(FigureCanvas):
    """Холст для отображения matplotlib графиков"""

    def __init__(self, parent=None, width=8, height=4, dpi=100):
        self.fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        self.fig.patch.set_facecolor('#F5F5F5')


class AnalyticsPage(QWidget):
    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.current_period = "week"  # week, month, all
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        title = QLabel("📈 Аналитика")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        # Панель фильтров
        filter_frame = QFrame()
        filter_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: 12px;
                padding: 12px;
            }}
        """)
        filter_layout = QHBoxLayout(filter_frame)

        filter_layout.addWidget(QLabel("Период:"))
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Неделя", "Месяц", "Всё время"])
        self.period_combo.setCurrentText("Неделя")
        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        filter_layout.addWidget(self.period_combo)

        self.date_range_label = QLabel("")
        filter_layout.addWidget(self.date_range_label)
        filter_layout.addStretch()

        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.setObjectName("primaryBtn")
        refresh_btn.clicked.connect(self.refresh)
        filter_layout.addWidget(refresh_btn)

        layout.addWidget(filter_frame)

        # Скролл область для графиков
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: transparent;")

        container = QWidget()
        self.content_layout = QVBoxLayout(container)
        self.content_layout.setSpacing(20)

        scroll.setWidget(container)
        layout.addWidget(scroll)

    def on_period_changed(self, text):
        period_map = {"Неделя": "week", "Месяц": "month", "Всё время": "all"}
        self.current_period = period_map.get(text, "week")
        self.refresh()

    def refresh(self):
        """Загрузка данных и обновление графиков"""
        # Очистка старых графиков
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        user = self.main_window.current_user if self.main_window else None
        if not user:
            no_data = QLabel("Нет данных о пользователе. Заполните профиль и добавьте записи.")
            no_data.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(no_data)
            return

        # Получение данных за период
        end_date = datetime.now().date()
        if self.current_period == "week":
            start_date = end_date - timedelta(days=7)
            self.date_range_label.setText(f"{start_date.strftime('%d.%m')} – {end_date.strftime('%d.%m')}")
        elif self.current_period == "month":
            start_date = end_date - timedelta(days=30)
            self.date_range_label.setText(f"{start_date.strftime('%d.%m')} – {end_date.strftime('%d.%m')}")
        else:
            start_date = datetime(2020, 1, 1).date()
            self.date_range_label.setText("Вся история")

        meals = get_meals_by_date_range(user.id, start_date, end_date)

        if not meals:
            no_data = QLabel("Нет данных о питании за выбранный период")
            no_data.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(no_data)
            return

        # Группировка по дням
        daily_data = {}
        for meal in meals:
            day = meal.meal_date.date() if hasattr(meal, 'meal_date') else meal.date
            if day not in daily_data:
                daily_data[day] = {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0}
            daily_data[day]['calories'] += meal.calories
            daily_data[day]['protein'] += meal.protein
            daily_data[day]['fat'] += meal.fat
            daily_data[day]['carbs'] += meal.carbs

        dates = sorted(daily_data.keys())
        calories = [daily_data[d]['calories'] for d in dates]

        # График калорий
        self.add_calories_chart(dates, calories, user.target_calories)

        # Сводка по калориям
        avg_calories = np.mean(calories) if calories else 0
        total_calories = sum(calories)
        days_count = len(dates)

        stats_frame = QFrame()
        stats_frame.setStyleSheet(f"background-color: {COLORS['surface']}; border-radius: 12px; padding: 16px;")
        stats_layout = QHBoxLayout(stats_frame)

        stats_items = [
            ("Средние калории", f"{avg_calories:.0f} ккал"),
            ("Всего калорий", f"{total_calories:.0f} ккал"),
            ("Дней записей", str(days_count)),
            ("Цель", f"{user.target_calories:.0f} ккал")
        ]
        for label, value in stats_items:
            item_layout = QVBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
            val = QLabel(value)
            val.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {COLORS['primary']};")
            item_layout.addWidget(lbl)
            item_layout.addWidget(val)
            stats_layout.addLayout(item_layout)
        self.content_layout.addWidget(stats_frame)

    def add_calories_chart(self, dates, calories, target):
        """Добавление графика калорий"""
        chart_frame = QFrame()
        chart_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: 12px;
                padding: 16px;
            }}
        """)
        layout = QVBoxLayout(chart_frame)
        title = QLabel("📊 Калории по дням")
        title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['text_primary']};")
        layout.addWidget(title)

        canvas = MatplotlibCanvas(self, width=8, height=4)
        ax = canvas.ax

        # Преобразование дат для оси X
        x = np.arange(len(dates))
        ax.bar(x, calories, color=COLORS['primary'], alpha=0.7, label='Калории')
        ax.axhline(y=target, color=COLORS.get('warning', '#F39C12'), linestyle='--', linewidth=2,
                   label=f'Цель ({target:.0f} ккал)')

        # Форматирование дат
        date_labels = [d.strftime('%d.%m') for d in dates]
        ax.set_xticks(x)
        ax.set_xticklabels(date_labels, rotation=45, ha='right')
        ax.set_ylabel('Калории (ккал)')
        ax.set_xlabel('Дата')
        ax.legend()
        ax.grid(True, alpha=0.3)

        canvas.fig.tight_layout()
        layout.addWidget(canvas)
        self.content_layout.addWidget(chart_frame)
