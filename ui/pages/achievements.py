# Страница достижений
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QFrame, QPushButton, QGridLayout, QProgressBar,
                              QSpacerItem, QSizePolicy, QListWidget, QListWidgetItem,
                              QScrollArea)
from PyQt6.QtCore import Qt

from config.settings import COLORS
from database.operations import (get_user, get_user_achievements,
                                  get_available_achievements, get_all_achievements)
from database.models import Achievement


class AchievementCard(QFrame):
    """Карточка достижения"""

    def __init__(self, achievement: Achievement, unlocked: bool = False, parent=None):
        super().__init__(parent)
        self.achievement = achievement
        self.unlocked = unlocked
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса карточки"""
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

        # Иконка
        icon_label = QLabel(self.achievement.icon)
        icon_label.setStyleSheet("font-size: 36px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # Название
        title_label = QLabel(self.achievement.title)
        title_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Описание
        desc_label = QLabel(self.achievement.description)
        desc_label.setStyleSheet(f"""
            font-size: 11px;
            color: {COLORS['text_secondary']};
        """)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)

        # Награда XP
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

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Профиль пользователя и прогресс
        profile_frame = self.create_profile_section()
        layout.addWidget(profile_frame)

        # Статистика
        stats_frame = self.create_stats_section()
        layout.addWidget(stats_frame)

        # Сетка достижений
        achievements_frame = self.create_achievements_grid()
        layout.addWidget(achievements_frame, stretch=1)

    def refresh(self):
        """Обновление данных страницы"""
        self.update_profile()
        self.update_stats()
        self.update_achievements()

    def create_profile_section(self) -> QFrame:
        """Создание секции профиля"""
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

        # Аватар и имя
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

        # Прогресс уровня
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
        """Создание секции статистики"""
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
        """Создание сетки достижений"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
            }}
        """)

        layout = QVBoxLayout(frame)

        title = QLabel("🏆 Все достижения")
        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)
        layout.addWidget(title)

        layout.addSpacing(12)

        # Контейнер с достижениями
        scroll_layout = QHBoxLayout()

        # Разблокированные достижения
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
        self.unlocked_scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
        """)
        self.unlocked_container = QWidget()
        self.unlocked_layout = QGridLayout(self.unlocked_container)
        self.unlocked_scroll.setWidget(self.unlocked_container)
        unlocked_layout.addWidget(self.unlocked_scroll)

        scroll_layout.addWidget(unlocked_frame)

        # Доступные достижения
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
        self.available_scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
        """)
        self.available_container = QWidget()
        self.available_layout = QGridLayout(self.available_container)
        self.available_scroll.setWidget(self.available_container)
        available_layout.addWidget(self.available_scroll)

        scroll_layout.addWidget(available_frame)

        layout.addLayout(scroll_layout)

        return frame

    def update_profile(self):
        """Обновление профиля"""
        user = self.main_window.current_user
        if not user:
            return

        self.user_name.setText(user.name)
        self.level_number.setText(str(user.level))

        # Определение звания
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

        # Прогресс XP
        xp_in_level = user.xp % 100
        self.xp_progress.setValue(xp_in_level)
        self.xp_text.setText(f"{xp_in_level} / 100 XP")

    def update_stats(self):
        """Обновление статистики"""
        user = self.main_window.current_user
        if not user:
            return

        self.stat_labels['streak_days'].setText(str(user.streak_days))

        # Количество достижений
        from database.operations import get_user_achievements
        achievements = get_user_achievements(user.id)
        self.stat_labels['achievements_count'].setText(str(len(achievements)))

        # Количество записей
        from database.operations import get_today_meals
        today_meals = get_today_meals(user.id)
        self.stat_labels['meals_count'].setText(str(len(today_meals)))

        # Вода
        self.stat_labels['water_total'].setText(str(user.water_glasses))

    def update_achievements(self):
        """Обновление списка достижений"""
        user = self.main_window.current_user
        if not user:
            return

        # Очищаем контейнеры
        while self.unlocked_layout.count():
            item = self.unlocked_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        while self.available_layout.count():
            item = self.available_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Получаем достижения
        unlocked = get_user_achievements(user.id)
        available = get_available_achievements(user.id)

        unlocked_names = {a.name for a in unlocked}
        all_achievements = get_all_achievements()

        # Разблокированные
        unlocked_count = 0
        for i, achievement in enumerate(all_achievements):
            if achievement.name in unlocked_names:
                card = AchievementCard(achievement, unlocked=True)
                self.unlocked_layout.addWidget(card, unlocked_count // 3, unlocked_count % 3)
                unlocked_count += 1

        # Если нет разблокированных
        if unlocked_count == 0:
            empty_label = QLabel("Пока нет достижений...\nНачните пользоваться приложением!")
            empty_label.setStyleSheet(f"""
                font-size: 14px;
                color: {COLORS['text_hint']};
            """)
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.unlocked_layout.addWidget(empty_label, 0, 0, 1, 3)

        # Доступные
        available_count = 0
        for i, achievement in enumerate(available):
            card = AchievementCard(achievement, unlocked=False)
            self.available_layout.addWidget(card, available_count // 3, available_count % 3)
            available_count += 1
