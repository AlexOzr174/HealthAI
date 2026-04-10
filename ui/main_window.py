# Главное окно приложения HealthAI
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QFrame, QStackedWidget,
                              QListWidget, QListWidgetItem, QSpacerItem,
                              QSizePolicy, QProgressBar, QLineEdit, QScrollArea)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QAction, QFont, QPixmap

from config.settings import APP_NAME, APP_VERSION, COLORS
from ui.styles import get_stylesheet, IconSize, set_theme, toggle_theme, CURRENT_THEME
from ui.pages.dashboard import DashboardPage
from ui.pages.onboarding import OnboardingPage
from ui.pages.diary import DiaryPage
from ui.pages.planner import PlannerPage
from ui.pages.recipes import RecipesPage
from ui.pages.achievements import AchievementsPage
from ui.pages.settings_notifications import SettingsNotificationsPage
from ui.pages.settings_diets import SettingsDietsPage
from ui.pages.settings_api import SettingsAPIPage
from database.operations import get_user, update_streak
from ui.components.search_widget import SmartSearchWidget
from ui.components.theme_toggle import ThemeToggle
from ai_engine import AIEngine
from ui.widgets import AIChatWidget, AIAnalyticsWidget, AIRecipeGeneratorWidget
from ui.dialogs.photo_upload_dialog import PhotoUploadDialog
from core.services.notification_service import NotificationService
from core.services.special_diets import SpecialDietsService


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
        
        # Инициализация AI движка
        self.ai_engine = AIEngine()
        
        # Инициализация сервисов
        self.notification_service = NotificationService()
        self.special_diets_service = SpecialDietsService()

        # Инициализация интерфейса
        self.setup_ui()

        # Проверяем, есть ли пользователь
        self.check_user()
        
        # Запуск уведомлений
        self.start_notifications()

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
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['sidebar_bg']};
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
            color: {COLORS['primary_dark'] if CURRENT_THEME == 'light' else COLORS['primary']};
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

        layout.addSpacing(8)

        # Переключатель темы
        self.theme_toggle = ThemeToggle()
        self.theme_toggle.theme_changed.connect(self.on_theme_changed)
        layout.addWidget(self.theme_toggle)

        layout.addSpacing(16)

        # Информация о пользователе
        self.user_info_frame = self.create_user_info()
        layout.addWidget(self.user_info_frame)

        layout.addSpacing(16)

        # Умный поиск
        self.search_widget = SmartSearchWidget(placeholder="Поиск...")
        self.search_widget.search_triggered.connect(self.on_search)
        layout.addWidget(self.search_widget)

        layout.addSpacing(8)

        # Кнопки навигации
        nav_buttons = [
            ("📊", "Главная", "dashboard"),
            ("🤖", "AI Ассистент", "ai_chat"),
            ("📈", "Аналитика", "ai_analytics"),
            ("👨‍🍳", "Генератор рецептов", "ai_recipes"),
            ("📸", "Фото еды", "photo_upload"),
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

        # Кнопка настроек с подменю
        settings_btn = SidebarButton("  ⚙️  Настройки")
        settings_btn.clicked.connect(self.open_settings_menu)
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

        # Стэк страниц
        self.pages = QStackedWidget()
        self.pages.setObjectName("pagesStack")

        # Добавление страниц
        self.pages.addWidget(OnboardingPage(self))           # 0 - Onboarding
        self.pages.addWidget(DashboardPage(self))            # 1 - Dashboard
        self.pages.addWidget(AIChatWidget(self.ai_engine, 1))  # 2 - AI Chat (временный user_id)
        self.pages.addWidget(AIAnalyticsWidget(self.ai_engine, 1))  # 3 - AI Analytics
        self.pages.addWidget(AIRecipeGeneratorWidget(self.ai_engine, 1))  # 4 - AI Recipes
        self.pages.addWidget(PhotoUploadDialog(self.ai_engine, self))  # 5 - Photo Upload
        self.pages.addWidget(DiaryPage(self))                # 6 - Diary
        self.pages.addWidget(PlannerPage(self))              # 7 - Planner
        self.pages.addWidget(RecipesPage(self))              # 8 - Recipes
        self.pages.addWidget(AchievementsPage(self))         # 9 - Achievements
        self.pages.addWidget(SettingsNotificationsPage(self))  # 10 - Settings Notifications
        self.pages.addWidget(SettingsDietsPage(self, self.special_diets_service))  # 11 - Settings Diets
        self.pages.addWidget(SettingsAPIPage(self))          # 12 - Settings API

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
            self.load_search_data()
            # Инициализация AI движка с данными пользователя
            self.ai_engine.initialize_user(
                user_id=self.current_user.id,
                profile={
                    'weight': self.current_user.weight,
                    'height': self.current_user.height,
                    'age': self.current_user.age,
                    'goal': self.current_user.goal,
                    'activity_level': self.current_user.activity_level,
                    'restrictions': []
                }
            )
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
            "ai_chat": 2,
            "ai_analytics": 3,
            "ai_recipes": 4,
            "photo_upload": 5,
            "diary": 6,
            "planner": 7,
            "recipes": 8,
            "achievements": 9,
            "settings_notifications": 10,
            "settings_diets": 11,
            "settings_api": 12,
        }

        page_index = page_map.get(page_id, 1)
        self.pages.setCurrentIndex(page_index)

        # Обновление кнопок
        for btn_id, btn in self.nav_buttons.items():
            btn.setChecked(btn_id == page_id)

        # Обновление заголовка
        titles = {
            "dashboard": "Главная",
            "ai_chat": "🤖 AI Нутрициолог",
            "ai_analytics": "📈 Предиктивная Аналитика",
            "ai_recipes": "👨‍🍳 Генератор Рецептов",
            "photo_upload": "📸 Анализ еды по фото",
            "diary": "Дневник питания",
            "planner": "Планировщик питания",
            "recipes": "База рецептов",
            "achievements": "Достижения",
            "settings_notifications": "🔔 Настройки уведомлений",
            "settings_diets": "🥗 Настройки диет",
            "settings_api": "🌐 Настройки API",
        }
        self.page_title.setText(titles.get(page_id, "HealthAI"))

        # Обновление данных при переходе
        if page_id == "dashboard":
            self.pages.widget(1).refresh()
        elif page_id == "ai_chat":
            pass  # Чат не требует обновления
        elif page_id == "ai_analytics":
            # Инициализация пользователя в AI движке
            if self.current_user:
                self.ai_engine.initialize_user(
                    user_id=self.current_user.id,
                    profile={
                        'weight': self.current_user.weight,
                        'height': self.current_user.height,
                        'age': self.current_user.age,
                        'goal': self.current_user.goal,
                        'activity_level': self.current_user.activity_level,
                        'restrictions': []
                    }
                )
            # Загрузка тестовых данных для аналитики
            import random
            weight_history = [85.0 + random.uniform(-1, 1) + (i * 0.1) for i in range(30)]
            widget = self.pages.widget(3)
            if hasattr(widget, 'update_predictions'):
                widget.update_predictions(weight_history)
                widget.update_graph(30)
        elif page_id == "ai_recipes":
            pass  # Генератор рецептов не требует обновления
        elif page_id == "photo_upload":
            pass  # Фото загрузка не требует обновления
        elif page_id == "diary":
            self.pages.widget(6).refresh()
        elif page_id == "planner":
            self.pages.widget(7).refresh()
        elif page_id == "recipes":
            self.pages.widget(8).refresh()
        elif page_id == "achievements":
            self.pages.widget(9).refresh()
        elif page_id == "settings_notifications":
            pass  # Настройки уведомлений
        elif page_id == "settings_diets":
            pass  # Настройки диет
        elif page_id == "settings_api":
            pass  # Настройки API

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

    def on_theme_changed(self, theme: str):
        """
        Обработка смены темы.
        
        Args:
            theme: 'light' или 'dark'
        """
        # Применяем новые стили
        self.setStyleSheet(get_stylesheet())
        
        # Обновляем все страницы
        self.refresh_all()
        
        # Сохраняем тему в настройках (будущая функциональность)
        print(f"Тема изменена на: {theme}")
        
    def on_search(self, query: str):
        """
        Обработка поиска.
        
        Args:
            query: Поисковый запрос
        """
        # Переходим на страницу рецептов и выполняем поиск
        self.navigate_to("recipes")
        recipes_page = self.pages.widget(4)
        if hasattr(recipes_page, 'perform_search'):
            recipes_page.perform_search(query)
            
    def open_settings_menu(self):
        """Открытие меню настроек с выбором раздела"""
        from PyQt6.QtWidgets import QMenu
        
        menu = QMenu(self)
        menu.setStyleSheet(get_stylesheet())
        
        # Действия меню
        notif_action = menu.addAction("🔔 Уведомления")
        diets_action = menu.addAction("🥗 Диеты и питание")
        api_action = menu.addAction("🌐 API интеграции")
        
        menu.addSeparator()
        
        # Показываем меню и получаем выбор
        action = menu.exec(self.mapToGlobal(self.nav_buttons.get('achievements', self).geometry().bottomLeft()))
        
        if action == notif_action:
            self.navigate_to("settings_notifications")
        elif action == diets_action:
            self.navigate_to("settings_diets")
        elif action == api_action:
            self.navigate_to("settings_api")
    
    def open_settings(self):
        """Открытие настроек (устаревший метод, теперь используется menu)"""
        self.open_settings_menu()
            
    def load_search_data(self):
        """Загрузка данных для поиска"""
        from database.operations import get_all_products, get_all_recipes
        
        search_data = []
        
        # Добавляем продукты
        try:
            products = get_all_products()
            for product in products:
                search_data.append({
                    'name': product.name,
                    'category': product.category,
                    'type': 'product',
                    'data': product
                })
        except Exception:
            pass
            
        # Добавляем рецепты
        try:
            recipes = get_all_recipes()
            for recipe in recipes:
                search_data.append({
                    'name': recipe.name,
                    'category': recipe.meal_type,
                    'type': 'recipe',
                    'data': recipe
                })
        except Exception:
            pass
            
        # Устанавливаем данные в виджет поиска
        if hasattr(self, 'search_widget'):
            self.search_widget.set_search_data(search_data)

    def refresh_all(self):
        """Обновление всех данных"""
        self.update_user_info()
        self.update_calorie_display()
        self.load_search_data()

    def start_notifications(self):
        """Запуск системы уведомлений"""
        if not self.current_user:
            return
        
        # Запускаем сервис уведомлений
        self.notification_service.start()
        print("✅ Система умных уведомлений запущена")
    
    def stop_notifications(self):
        """Остановка системы уведомлений"""
        if hasattr(self, 'notification_service'):
            self.notification_service.stop()
            print("🔕 Система умных уведомлений остановлена")
    
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        # Останавливаем уведомления при закрытии приложения
        self.stop_notifications()
        event.accept()
