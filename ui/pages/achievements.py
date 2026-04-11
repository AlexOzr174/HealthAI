# ui/pages/achievements.py
# Страница достижений
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QPushButton, QGridLayout, QProgressBar,
                             QSpacerItem, QSizePolicy, QListWidget, QListWidgetItem,
                             QScrollArea)
from PyQt6.QtCore import Qt

try:
    from config.settings import COLORS
except ImportError:
    COLORS = {
        'primary': '#3498DB',
        'primary_dark': '#2980B9',
        'primary_light': '#5DADE2',
        'surface': '#FFFFFF',
        'background': '#F0F2F5',
        'text_primary': '#2C3E50',
        'text_secondary': '#7F8C8D',
        'text_hint': '#95A5A6',
        'warning': '#F39C12',
        'warning_light': '#FDEBD0',
        'success': '#27AE60',
        'border': '#E0E0E0',
    }

from database.operations import (get_user, get_user_achievements,
                                 get_available_achievements, get_all_achievements,
                                 get_today_meals)
from database.models import Achievement


class AchievementCard(QFrame):
    """Карточка достижения"""

    def __init__(self, achievement: Achievement, unlocked: bool = False, parent=None):
        super().__init__(parent)
        self.achievement = achievement
        self.unlocked = unlocked
        self.setup_ui()

    def setup_ui(self):
        self.setMinimumSize(140, 160)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        if self.unlocked:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['warning_light']}40;
                    border: 2px solid {COLORS['warning']};
                    border-radius: 12px;
                    padding: 12px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['surface']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 12px;
                    padding: 12px;
                    opacity: 0.6;
                }}
            """)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_label = QLabel(self.achievement.icon)
        icon_label.setStyleSheet("font-size: 36px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        title_label = QLabel(self.achievement.title)
        title_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        desc_label = QLabel(self.achievement.description)
        desc_label.setStyleSheet(f"""
            font-size: 11px;
            color: {COLORS['text_secondary']};
        """)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)

        if self.unlocked:
            xp_label = QLabel(f"+{self.achievement.xp_reward} XP")
            xp_label.setStyleSheet(f"""
                font-size: 12px;
                font-weight: bold;
                color: {COLORS['primary']};
            """)
            xp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(xp_label)
        else:
            lock_label = QLabel("🔒")
            lock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(lock_label)


class AchievementsPage(QWidget):
    """Страница достижений"""

    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        profile_frame = self.create_profile_section()
        layout.addWidget(profile_frame)

        stats_frame = self.create_stats_section()
        layout.addWidget(stats_frame)

        achievements_frame = self.create_achievements_grid()
        layout.addWidget(achievements_frame, stretch=1)

    def refresh(self):
        """Обновление данных страницы"""
        self.update_profile()
        self.update_stats()
        self.update_achievements()

    def create_profile_section(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary_dark']},
                    stop:1 {COLORS['primary']}
                );
                border-radius: 16px;
                padding: 20px;
            }}
        """)

        layout = QHBoxLayout(frame)

        profile_layout = QVBoxLayout()
        avatar_label = QLabel("👤")
        avatar_label.setStyleSheet("font-size: 48px;")

        self.user_name = QLabel("Пользователь")
        self.user_name.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: white;
        """)

        self.user_title = QLabel("Начинающий")
        self.user_title.setStyleSheet("""
            font-size: 14px;
            color: rgba(255,255,255,0.8);
        """)

        profile_layout.addWidget(avatar_label)
        profile_layout.addWidget(self.user_name)
        profile_layout.addWidget(self.user_title)
        layout.addLayout(profile_layout)
        layout.addStretch()

        level_layout = QVBoxLayout()
        level_layout.setSpacing(8)

        level_title = QLabel("Уровень")
        level_title.setStyleSheet("""
            font-size: 14px;
            color: rgba(255,255,255,0.8);
        """)

        self.level_number = QLabel("1")
        self.level_number.setStyleSheet("""
            font-size: 48px;
            font-weight: bold;
            color: white;
        """)

        self.xp_progress = QProgressBar()
        self.xp_progress.setFixedWidth(200)
        self.xp_progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: rgba(255,255,255,0.3);
                border: none;
                border-radius: 8px;
                height: 12px;
            }}
            QProgressBar::chunk {{
                background-color: white;
                border-radius: 8px;
            }}
        """)
        self.xp_progress.setValue(0)

        self.xp_text = QLabel("0 / 100 XP")
        self.xp_text.setStyleSheet("""
            font-size: 12px;
            color: rgba(255,255,255,0.8);
        """)

        level_layout.addWidget(level_title)
        level_layout.addWidget(self.level_number)
        level_layout.addWidget(self.xp_progress)
        level_layout.addWidget(self.xp_text)

        layout.addLayout(level_layout)

        return frame

    def create_stats_section(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        layout = QHBoxLayout(frame)
        layout.setSpacing(24)

        stats_items = [
            ("🔥", "Дней подряд", "streak_days", "0"),
            ("🏆", "Достижений", "achievements_count", "0"),
            ("📔", "Записей в дневнике", "meals_count", "0"),
            ("💧", "Стаканов воды", "water_total", "0"),
        ]

        self.stat_labels = {}

        for icon, name, key, default in stats_items:
            stat_layout = QVBoxLayout()
            stat_layout.setSpacing(4)

            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 24px;")

            value_label = QLabel(default)
            value_label.setStyleSheet(f"""
                font-size: 28px;
                font-weight: bold;
                color: {COLORS['primary']};
            """)
            self.stat_labels[key] = value_label

            name_label = QLabel(name)
            name_label.setStyleSheet(f"""
                font-size: 12px;
                color: {COLORS['text_secondary']};
            """)

            stat_layout.addWidget(icon_label)
            stat_layout.addWidget(value_label)
            stat_layout.addWidget(name_label)
            layout.addLayout(stat_layout)

        return frame

    def create_achievements_grid(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet("background-color: transparent;")

        layout = QVBoxLayout(frame)

        title = QLabel("🏆 Все достижения")
        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)
        layout.addWidget(title)
        layout.addSpacing(12)

        scroll_layout = QVBoxLayout()
        scroll_layout.setSpacing(16)

        # Разблокированные
        unlocked_frame = QFrame()
        unlocked_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['primary_light']}20;
                border-radius: 12px;
                padding: 16px;
            }}
        """)
        unlocked_layout = QVBoxLayout(unlocked_frame)
        unlocked_title = QLabel("✅ Разблокировано")
        unlocked_title.setStyleSheet(f"""
            font-size: 14px;
            font-weight: bold;
            color: {COLORS['success']};
        """)
        unlocked_layout.addWidget(unlocked_title)

        self.unlocked_scroll = QScrollArea()
        self.unlocked_scroll.setWidgetResizable(True)
        self.unlocked_scroll.setStyleSheet("background-color: transparent; border: none;")
        self.unlocked_scroll.setMinimumHeight(200)
        self.unlocked_container = QWidget()
        self.unlocked_container.setStyleSheet("background-color: transparent;")
        self.unlocked_layout_grid = QGridLayout(self.unlocked_container)
        self.unlocked_layout_grid.setSpacing(12)
        self.unlocked_scroll.setWidget(self.unlocked_container)
        unlocked_layout.addWidget(self.unlocked_scroll)
        scroll_layout.addWidget(unlocked_frame)

        # Доступные
        available_frame = QFrame()
        available_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['background']};
                border-radius: 12px;
                padding: 16px;
            }}
        """)
        available_layout = QVBoxLayout(available_frame)
        available_title = QLabel("🎯 Доступные")
        available_title.setStyleSheet(f"""
            font-size: 14px;
            font-weight: bold;
            color: {COLORS['text_secondary']};
        """)
        available_layout.addWidget(available_title)

        self.available_scroll = QScrollArea()
        self.available_scroll.setWidgetResizable(True)
        self.available_scroll.setStyleSheet("background-color: transparent; border: none;")
        self.available_scroll.setMinimumHeight(200)
        self.available_container = QWidget()
        self.available_container.setStyleSheet("background-color: transparent;")
        self.available_layout_grid = QGridLayout(self.available_container)
        self.available_layout_grid.setSpacing(12)
        self.available_scroll.setWidget(self.available_container)
        available_layout.addWidget(self.available_scroll)
        scroll_layout.addWidget(available_frame)

        layout.addLayout(scroll_layout)
        return frame

    def update_profile(self):
        user = self.main_window.current_user if self.main_window else None
        if not user:
            return

        self.user_name.setText(user.name)
        self.level_number.setText(str(user.level))

        if user.level < 5:
            title = "Начинающий"
        elif user.level < 10:
            title = "Любитель"
        elif user.level < 15:
            title = "Знаток"
        elif user.level < 20:
            title = "Эксперт"
        else:
            title = "Мастер"
        self.user_title.setText(title)

        xp_in_level = user.xp % 100
        self.xp_progress.setValue(xp_in_level)
        self.xp_text.setText(f"{xp_in_level} / 100 XP")

    def update_stats(self):
        user = self.main_window.current_user if self.main_window else None
        if not user:
            return

        self.stat_labels['streak_days'].setText(str(user.streak_days))

        achievements = get_user_achievements(user.id)
        self.stat_labels['achievements_count'].setText(str(len(achievements)))

        today_meals = get_today_meals(user.id)
        self.stat_labels['meals_count'].setText(str(len(today_meals)))

        self.stat_labels['water_total'].setText(str(user.water_glasses))

    def update_achievements(self):
        # Очистка
        while self.unlocked_layout_grid.count():
            item = self.unlocked_layout_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        while self.available_layout_grid.count():
            item = self.available_layout_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        user = self.main_window.current_user if self.main_window else None
        if not user:
            return

        unlocked = get_user_achievements(user.id)
        available = get_available_achievements(user.id)

        unlocked_names = {a.name for a in unlocked}
        all_achievements = get_all_achievements()

        # Разблокированные
        unlocked_count = 0
        for achievement in all_achievements:
            if achievement.name in unlocked_names:
                card = AchievementCard(achievement, unlocked=True)
                self.unlocked_layout_grid.addWidget(card, unlocked_count // 3, unlocked_count % 3)
                unlocked_count += 1

        if unlocked_count == 0:
            empty_label = QLabel("Пока нет достижений...\nНачните пользоваться приложением!")
            empty_label.setStyleSheet(f"font-size: 14px; color: {COLORS['text_hint']};")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.unlocked_layout_grid.addWidget(empty_label, 0, 0, 1, 3)

        # Доступные
        available_count = 0
        for achievement in available:
            card = AchievementCard(achievement, unlocked=False)
            self.available_layout_grid.addWidget(card, available_count // 3, available_count % 3)
            available_count += 1
