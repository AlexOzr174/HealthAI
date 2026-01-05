# Главное окно приложения HealthAI
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QFrame, QStackedWidget,
                              QListWidget, QListWidgetItem, QSpacerItem,
                              QSizePolicy, QProgressBar, QLineEdit)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction, QFont, QPixmap

from config.settings import APP_NAME, APP_VERSION, COLORS
from ui.styles import get_stylesheet, IconSize
from ui.pages.dashboard import DashboardPage
from ui.pages.onboarding import OnboardingPage
from ui.pages.diary import DiaryPage
from ui.pages.planner import PlannerPage
from ui.pages.recipes import RecipesPage
from ui.pages.achievements import AchievementsPage
from database.operations import get_user, update_streak


class SidebarButton(QPushButton):
    """Кнопка боковой панели навигации"""

    def __init__(self, text: str, icon: str = None, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setChecked(False)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Стилизация кнопки
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 8px;
                padding: 12px 16px;
                text-align: left;
                font-size: 14px;
                color: {COLORS['text_secondary']};
                min-height: 44px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_light']}30;
                color: {COLORS['text_primary']};
            }}
            QPushButton:checked {{
                background-color: {COLORS['primary_light']}50;
                color: {COLORS['primary']};
                font-weight: 600;
                border-left: 3px solid {COLORS['primary']};
            }}
        """)


class MainWindow(QMainWindow):
    """Главное окно приложения"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} - Умный гид по здоровому питанию")
        self.setMinimumSize(1024, 768)
        self.resize(1280, 800)

        # Применяем стили
        self.setStyleSheet(get_stylesheet())

        # Текущий пользователь
        self.current_user = None

        # Инициализация интерфейса
        self.setup_ui()

        # Проверяем, есть ли пользователь
        self.check_user()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Главный layout (горизонтальный)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Создаём боковую панель
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)

        # Создаём рабочую область
        self.content_area = self.create_content_area()
        main_layout.addWidget(self.content_area, stretch=1)

    def create_sidebar(self) -> QFrame:
        """Создание боковой панели навигации"""
        sidebar = QFrame()
        sidebar.setFixedWidth(260)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-right: 1px solid {COLORS['border']};
            }}
        """)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # Логотип и название
        logo_layout = QHBoxLayout()

        logo_icon = QLabel("🍎")
        logo_icon.setStyleSheet("font-size: 32px;")
        logo_layout.addWidget(logo_icon)

        title_layout = QVBoxLayout()
        app_title = QLabel(APP_NAME)
        app_title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {COLORS['primary_dark']};
        """)
        version_label = QLabel(f"v{APP_VERSION}")
        version_label.setStyleSheet(f"""
            font-size: 11px;
            color: {COLORS['text_hint']};
        """)
        title_layout.addWidget(app_title)
        title_layout.addWidget(version_label)
        title_layout.addStretch()

        logo_layout.addLayout(title_layout)
        layout.addLayout(logo_layout)

        layout.addSpacing(16)

        # Информация о пользователе
        self.user_info_frame = self.create_user_info()
        layout.addWidget(self.user_info_frame)

        layout.addSpacing(16)

        # Кнопки навигации
        nav_buttons = [
            ("📊", "Главная", "dashboard"),
            ("📔", "Дневник питания", "diary"),
            ("📅", "Планировщик", "planner"),
            ("📚", "Рецепты", "recipes"),
            ("🏆", "Достижения", "achievements"),
        ]

        self.nav_buttons = {}
        for icon, text, page_id in nav_buttons:
            btn = SidebarButton(f"  {icon}  {text}")
            btn.clicked.connect(lambda checked, pid=page_id: self.navigate_to(pid))
            layout.addWidget(btn)
            self.nav_buttons[page_id] = btn

        layout.addStretch()

        # Кнопка настроек
        settings_btn = SidebarButton("  ⚙️  Настройки")
        settings_btn.clicked.connect(self.open_settings)
        layout.addWidget(settings_btn)

        return sidebar

    def create_user_info(self) -> QFrame:
        """Создание блока информации о пользователе"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['background']};
                border-radius: 12px;
                padding: 12px;
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Аватар и имя пользователя
        header_layout = QHBoxLayout()

        self.avatar_label = QLabel("👤")
        self.avatar_label.setStyleSheet("font-size: 36px;")
        header_layout.addWidget(self.avatar_label)

        user_info_layout = QVBoxLayout()

        self.user_name_label = QLabel("Гость")
        self.user_name_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 600;
            color: {COLORS['text_primary']};
        """)

        self.user_level_label = QLabel("Уровень 1")
        self.user_level_label.setStyleSheet(f"""
            font-size: 12px;
            color: {COLORS['primary']};
        """)

        user_info_layout.addWidget(self.user_name_label)
        user_info_layout.addWidget(self.user_level_label)
        user_info_layout.addStretch()

        header_layout.addLayout(user_info_layout)
        layout.addLayout(header_layout)

        # Прогресс уровня
        layout.addWidget(QLabel("Прогресс уровня"))

        self.xp_progress = QProgressBar()
        self.xp_progress.setStyleSheet(get_stylesheet())
        self.xp_progress.setValue(0)
        self.xp_progress.setMaximum(100)
        layout.addWidget(self.xp_progress)

        return frame

    def create_content_area(self) -> QFrame:
        """Создание рабочей области"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['background']};
            }}
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Заголовок страницы
        self.page_title = QLabel("Главная")
        self.page_title.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)
        layout.addWidget(self.page_title)

        # Статус-бар с калориями
        self.calorie_bar = self.create_calorie_status_bar()
        layout.addWidget(self.calorie_bar)

        # Стек страниц
        self.pages = QStackedWidget()
        self.pages.setObjectName("pagesStack")

        # Добавление страниц
        self.pages.addWidget(OnboardingPage(self))      # 0
        self.pages.addWidget(DashboardPage(self))        # 1
        self.pages.addWidget(DiaryPage(self))            # 2
        self.pages.addWidget(PlannerPage(self))          # 3
        self.pages.addWidget(RecipesPage(self))          # 4
        self.pages.addWidget(AchievementsPage(self))     # 5

        layout.addWidget(self.pages, stretch=1)

        return frame

    def create_calorie_status_bar(self) -> QFrame:
        """Создание статус-бара с калориями"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: 12px;
                padding: 12px;
            }}
        """)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)

        # Калории
        calories_layout = QVBoxLayout()
        calories_layout.setSpacing(2)

        calories_label = QLabel("Калории сегодня")
        calories_label.setStyleSheet(f"""
            font-size: 12px;
            color: {COLORS['text_secondary']};
        """)

        self.calorie_value = QLabel("0 / 2000 ккал")
        self.calorie_value.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)

        calories_layout.addWidget(calories_label)
        calories_layout.addWidget(self.calorie_value)
        layout.addLayout(calories_layout)

        # Прогресс-бар калорий
        self.calorie_progress = QProgressBar()
        self.calorie_progress.setFixedWidth(200)
        self.calorie_progress.setValue(0)
        self.calorie_progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS['background']};
                border: none;
                border-radius: 8px;
                height: 12px;
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['primary']};
                border-radius: 8px;
            }}
        """)
        layout.addWidget(self.calorie_progress)

        layout.addStretch()

        # Вода
        water_layout = QHBoxLayout()
        water_layout.setSpacing(8)

        water_icon = QLabel("💧")
        water_icon.setStyleSheet("font-size: 20px;")

        self.water_count = QLabel("0/8")
        self.water_count.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 600;
            color: {COLORS['primary']};
        """)

        water_add_btn = QPushButton("+")
        water_add_btn.setFixedSize(28, 28)
        water_add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 14px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {COLORS['primary_hover']}; }}
        """)
        water_add_btn.clicked.connect(self.add_water)

        water_layout.addWidget(water_icon)
        water_layout.addWidget(self.water_count)
        water_layout.addWidget(water_add_btn)
        layout.addLayout(water_layout)

        # День streak
        streak_layout = QHBoxLayout()
        streak_layout.setSpacing(8)

        streak_icon = QLabel("🔥")
        streak_icon.setStyleSheet("font-size: 20px;")

        self.streak_label = QLabel("0 дней")
        self.streak_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 600;
            color: {COLORS['secondary']};
        """)

        streak_layout.addWidget(streak_icon)
        streak_layout.addWidget(self.streak_label)
        layout.addLayout(streak_layout)

        return frame

    def check_user(self):
        """Проверка наличия пользователя и переход на нужную страницу"""
        self.current_user = get_user()

        if self.current_user:
            self.update_user_info()
            self.navigate_to("dashboard")
        else:
            self.navigate_to("onboarding")

    def update_user_info(self):
        """Обновление информации о пользователе"""
        if not self.current_user:
            return

        self.user_name_label.setText(self.current_user.name)
        self.user_level_label.setText(f"Уровень {self.current_user.level}")

        # Прогресс XP
        xp_in_level = self.current_user.xp % 100
        self.xp_progress.setValue(xp_in_level)

        # Калории
        self.update_calorie_display()

        # Вода
        self.water_count.setText(f"{self.current_user.water_glasses}/8")

        # Streak
        self.streak_label.setText(f"{self.current_user.streak_days} дней")

    def update_calorie_display(self):
        """Обновление отображения калорий"""
        if not self.current_user:
            return

        from database.operations import get_today_meals
        today_meals = get_today_meals(self.current_user.id)
        consumed = sum(m.calories for m in today_meals)
        target = self.current_user.target_calories

        self.calorie_value.setText(f"{int(consumed)} / {int(target)} ккал")

        # Цвет прогресс-бара в зависимости от прогресса
        percent = min(100, (consumed / target) * 100) if target > 0 else 0
        self.calorie_progress.setValue(int(percent))

        if percent > 100:
            color = COLORS['error']
        elif percent > 85:
            color = COLORS['warning']
        else:
            color = COLORS['primary']

        self.calorie_progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS['background']};
                border: none;
                border-radius: 8px;
                height: 12px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 8px;
            }}
        """)

    def navigate_to(self, page_id: str):
        """Переход на страницу"""
        page_map = {
            "onboarding": 0,
            "dashboard": 1,
            "diary": 2,
            "planner": 3,
            "recipes": 4,
            "achievements": 5,
        }

        page_index = page_map.get(page_id, 1)
        self.pages.setCurrentIndex(page_index)

        # Обновление кнопок
        for btn_id, btn in self.nav_buttons.items():
            btn.setChecked(btn_id == page_id)

        # Обновление заголовка
        titles = {
            "dashboard": "Главная",
            "diary": "Дневник питания",
            "planner": "Планировщик питания",
            "recipes": "База рецептов",
            "achievements": "Достижения",
        }
        self.page_title.setText(titles.get(page_id, "HealthAI"))

        # Обновление данных при переходе
        if page_id == "dashboard":
            self.pages.widget(1).refresh()
        elif page_id == "diary":
            self.pages.widget(2).refresh()
        elif page_id == "planner":
            self.pages.widget(3).refresh()
        elif page_id == "recipes":
            self.pages.widget(4).refresh()
        elif page_id == "achievements":
            self.pages.widget(5).refresh()

        # Обновляем статус-бар
        self.update_calorie_display()

    def add_water(self):
        """Добавление стакана воды"""
        if not self.current_user:
            return

        from database.operations import update_water_glasses

        self.current_user.water_glasses += 1
        update_water_glasses(self.current_user.id, self.current_user.water_glasses)
        self.water_count.setText(f"{self.current_user.water_glasses}/8")

    def open_settings(self):
        """Открытие настроек"""
        # В будущем можно добавить страницу настроек
        from ui.components.dialogs import SettingsDialog
        dialog = SettingsDialog(self.current_user, self)
        if dialog.exec():
            self.current_user = get_user()
            self.update_user_info()

    def refresh_all(self):
        """Обновление всех данных"""
        self.update_user_info()
        self.update_calorie_display()
