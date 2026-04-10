import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget, QFrame, \
    QSizePolicy, QApplication
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont

# Импорт стилей
from ui.styles import Styles, set_theme

# Импорт страниц
try:
    from ui.pages.dashboard import DashboardPage
    from ui.pages.calculator import CalculatorPage
    from ui.pages.diary import DiaryPage
    from ui.pages.planner import PlannerPage
    from ui.pages.recipes import RecipesPage
    from ui.pages.products import ProductsPage
    from ui.pages.ai_chat import AIChatPage
    from ui.pages.analytics import AnalyticsPage
    from ui.pages.photo_analysis import PhotoAnalysisPage
    from ui.pages.settings_notifications import SettingsNotificationsPage
    from ui.pages.settings_diets import SpecialDietsPage
    from ui.pages.settings_api import APIIntegrationPage
except ImportError as e:
    print(f"CRITICAL ERROR: Не удалось импортировать страницы: {e}")
    print("Убедитесь, что все файлы страниц существуют и классы названы правильно.")
    sys.exit(1)

# Импорт сервисов
try:
    from core.services.notification_service import NotificationService
    from core.services.special_diets import SpecialDietsService
except ImportError:
    print("WARNING: Сервисы не найдены. Приложение запустится в ограниченном режиме.")
    NotificationService = None
    SpecialDietsService = None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HealthAI - Умный помощник питания")
        self.setMinimumSize(1200, 800)

        # Инициализация сервисов
        self.notification_service = None
        if NotificationService:
            try:
                self.notification_service = NotificationService()
                self.notification_service.start()
            except Exception as e:
                print(f"Warning: Не удалось запустить сервис уведомлений: {e}")

        self.diets_service = None
        if SpecialDietsService:
            try:
                self.diets_service = SpecialDietsService()
            except Exception as e:
                print(f"Warning: Не удалось инициализировать сервис диет: {e}")

        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Сайдбар
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(280)
        sidebar.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(10)
        sidebar_layout.setContentsMargins(20, 30, 20, 30)

        # Логотип
        logo_label = QLabel("🍏 HealthAI")
        logo_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        logo_label.setStyleSheet("color: #3498DB; padding: 10px 0;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(logo_label)

        # Навигация
        self.nav_buttons = []
        pages = [
            ("📊 Дашборд", DashboardPage),
            ("🧮 Калькулятор", CalculatorPage),
            ("📔 Дневник", DiaryPage),
            ("📅 Планировщик", PlannerPage),
            ("🥗 Рецепты", RecipesPage),
            ("🍎 Продукты", ProductsPage),
            ("🤖 AI Нутрициолог", AIChatPage),
            ("📈 Аналитика", AnalyticsPage),
            ("📸 Фото еды", PhotoAnalysisPage),
            ("⚙️ Настройки", None)  # Разделитель
        ]

        for text, page_class in pages:
            if page_class is None:
                # Разделитель
                line = QFrame()
                line.setFrameShape(QFrame.Shape.HLine)
                line.setStyleSheet("background-color: #E0E0E0; margin: 10px 0;")
                line.setFixedHeight(1)
                sidebar_layout.addWidget(line)
                continue

            btn = QPushButton(text)
            btn.setObjectName("navButton")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, p=page_class: self.navigate_to(p))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append((btn, page_class))

        # Дополнительные настройки
        settings_layout = QVBoxLayout()
        settings_layout.setSpacing(5)

        settings_btns = [
            ("🔔 Уведомления", SettingsNotificationsPage),
            ("🥗 Диеты", SpecialDietsPage),
            ("🌐 API", APIIntegrationPage)
        ]

        for text, page_class in settings_btns:
            btn = QPushButton(text)
            btn.setObjectName("navButton")
            btn.setCheckable(True)
            btn.setStyleSheet("font-size: 13px; padding-left: 30px;")
            btn.clicked.connect(lambda checked, p=page_class: self.navigate_to(p))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append((btn, page_class))

        sidebar_layout.addStretch()

        # Область страниц
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: transparent;")

        # Добавление страниц
        self.pages = {}
        for _, page_class in self.nav_buttons:
            if page_class:
                try:
                    page = page_class()
                    self.stack.addWidget(page)
                    self.pages[page_class] = page
                except Exception as e:
                    print(f"Error creating page {page_class}: {e}")
                    # Создаем заглушку
                    error_page = QLabel(f"Ошибка загрузки страницы: {e}")
                    error_page.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.stack.addWidget(error_page)
                    self.pages[page_class] = error_page

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)

        # Переход на дашборд по умолчанию
        if DashboardPage in self.pages:
            self.navigate_to(DashboardPage)

    def navigate_to(self, page_class):
        """Переход на страницу"""
        if page_class not in self.pages:
            return

        # Снимаем выделение со всех кнопок
        for btn, _ in self.nav_buttons:
            btn.setChecked(False)

        # Находим кнопку и выделяем
        for btn, cls in self.nav_buttons:
            if cls == page_class:
                btn.setChecked(True)
                break

        # Переключаем страницу
        index = list(self.pages.keys()).index(page_class)
        self.stack.setCurrentIndex(index)

    def apply_styles(self):
        """Применить стили"""
        self.setStyleSheet(Styles.get_stylesheet())

    def closeEvent(self, event):
        """Корректное закрытие"""
        if self.notification_service:
            self.notification_service.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Установка стиля перед созданием окна
    set_theme("light")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())