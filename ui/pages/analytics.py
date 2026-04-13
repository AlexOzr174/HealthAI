# ui/pages/analytics.py
# Графики: Agg + PNG → QPixmap. Matplotlib импортируется лениво при первом графике,
# чтобы не тянуть libpng/matplotlib при старте приложения (macOS + Qt).
from __future__ import annotations

import io
from datetime import datetime, timedelta

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

try:
    from config.settings import COLORS
except ImportError:
    COLORS = {
        "surface": "#FFFFFF",
        "background": "#F0F2F5",
        "primary": "#3498DB",
        "primary_dark": "#2980B9",
        "text_primary": "#2C3E50",
        "text_secondary": "#7F8C8D",
        "warning": "#F39C12",
    }

from database.operations import get_meals_by_date_range


def _calories_chart_png_bytes(
    dates: list,
    calories: list,
    target: float,
    primary_hex: str,
    warning_hex: str,
) -> bytes:
    import numpy as np
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
    try:
        fig.patch.set_facecolor("#F5F5F5")
        x = np.arange(len(dates))
        ax.bar(x, calories, color=primary_hex, alpha=0.7, label="Калории")
        ax.axhline(
            y=target,
            color=warning_hex,
            linestyle="--",
            linewidth=2,
            label=f"Цель ({target:.0f} ккал)",
        )
        date_labels = [d.strftime("%d.%m") for d in dates]
        ax.set_xticks(x)
        ax.set_xticklabels(date_labels, rotation=45, ha="right")
        ax.set_ylabel("Калории (ккал)")
        ax.set_xlabel("Дата")
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", facecolor=fig.get_facecolor())
        buf.seek(0)
        return buf.getvalue()
    finally:
        plt.close(fig)


class AnalyticsPage(QWidget):
    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.current_period = "week"
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        title = QLabel("📈 Аналитика")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        filter_frame = QFrame()
        filter_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: 12px;
                padding: 12px;
            }}
        """
        )
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

    def refresh(self, *_args):
        """*_args — слот QPushButton.clicked передаёт bool; игнорируем."""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        user = self.main_window.current_user if self.main_window else None
        if not user:
            no_data = QLabel("Нет данных о пользователе. Заполните профиль и добавьте записи.")
            no_data.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(no_data)
            return

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

        daily_data: dict = {}
        for meal in meals:
            day = meal.meal_date.date() if hasattr(meal, "meal_date") else meal.date
            if day not in daily_data:
                daily_data[day] = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}
            daily_data[day]["calories"] += meal.calories
            daily_data[day]["protein"] += meal.protein
            daily_data[day]["fat"] += meal.fat
            daily_data[day]["carbs"] += meal.carbs

        dates = sorted(daily_data.keys())
        calories = [daily_data[d]["calories"] for d in dates]

        self.add_calories_chart(dates, calories, user.target_calories)

        avg_calories = float(sum(calories) / len(calories)) if calories else 0.0
        total_calories = sum(calories)
        days_count = len(dates)

        stats_frame = QFrame()
        stats_frame.setStyleSheet(
            f"background-color: {COLORS['surface']}; border-radius: 12px; padding: 16px;"
        )
        stats_layout = QHBoxLayout(stats_frame)

        stats_items = [
            ("Средние калории", f"{avg_calories:.0f} ккал"),
            ("Всего калорий", f"{total_calories:.0f} ккал"),
            ("Дней записей", str(days_count)),
            ("Цель", f"{user.target_calories:.0f} ккал"),
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

        try:
            from ai_engine.predictive_analytics import PredictiveAnalytics

            fc = PredictiveAnalytics().forecast_from_calorie_balance(
                target_calories_per_day=float(user.target_calories),
                avg_daily_intake=avg_calories,
                current_weight_kg=float(user.weight),
                horizon_days=7,
            )
        except Exception:
            fc = {"status": "error"}
        if fc.get("status") == "success":
            dk = float(fc["estimated_delta_kg"])
            if dk > 0.01:
                ch = (
                    f"ориентировочное снижение ~{dk:.2f} кг за неделю "
                    f"(вес ~{fc['projected_weight_kg']:.1f} кг)"
                )
            elif dk < -0.01:
                ch = (
                    f"ориентировочный набор ~{abs(dk):.2f} кг за неделю "
                    f"(вес ~{fc['projected_weight_kg']:.1f} кг)"
                )
            else:
                ch = f"изменение веса за неделю ~0 кг (вес ~{fc['projected_weight_kg']:.1f} кг)"
            pred_frame = QFrame()
            pred_frame.setStyleSheet(
                f"background-color: {COLORS['surface']}; border-radius: 12px; padding: 16px;"
            )
            pred_layout = QVBoxLayout(pred_frame)
            pt = QLabel("🔮 Прогноз на 7 дней по балансу калорий (~7700 ккал ≈ 1 кг)")
            pt.setStyleSheet(
                f"font-size: 16px; font-weight: bold; color: {COLORS['text_primary']};"
            )
            pred_layout.addWidget(pt)
            body = (
                f"Среднее потребление за период: {avg_calories:.0f} ккал/день при цели {user.target_calories:.0f} ккал.\n"
                f"Средний дневной баланс: {fc['daily_balance_kcal']:+.0f} ккал ({fc['trend_hint']}).\n"
                f"{ch}.\n\n"
                f"{fc['disclaimer']}"
            )
            pl = QLabel(body)
            pl.setWordWrap(True)
            pl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
            pred_layout.addWidget(pl)
            self.content_layout.addWidget(pred_frame)

    def add_calories_chart(self, dates, calories, target):
        chart_frame = QFrame()
        chart_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: 12px;
                padding: 16px;
            }}
        """
        )
        layout = QVBoxLayout(chart_frame)
        title = QLabel("📊 Калории по дням")
        title.setStyleSheet(
            f"font-size: 16px; font-weight: bold; color: {COLORS['text_primary']};"
        )
        layout.addWidget(title)

        try:
            png = _calories_chart_png_bytes(
                dates,
                calories,
                float(target),
                COLORS["primary"],
                COLORS.get("warning", "#F39C12"),
            )
            img = QImage.fromData(png, "PNG")
            pix = QPixmap.fromImage(img)
            chart_lbl = QLabel()
            chart_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            chart_lbl.setPixmap(pix)
            chart_lbl.setMinimumSize(pix.size())
            layout.addWidget(chart_lbl)
        except Exception as e:
            err = QLabel(f"Не удалось построить график: {e}")
            err.setWordWrap(True)
            layout.addWidget(err)

        self.content_layout.addWidget(chart_frame)
