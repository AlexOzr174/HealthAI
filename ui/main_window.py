# ui/main_window.py
import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget, QFrame, \
    QSizePolicy, QApplication
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont

# Импорт стилей
from ui.styles import Styles, set_theme

print("  [main_window] Импорт страниц...")
# Импорт страниц
try:
    from ui.pages.dashboard import DashboardPage

    print("    DashboardPage OK")
    from ui.pages.calculator import CalculatorPage

    print("    CalculatorPage OK")
    from ui.pages.diary import DiaryPage

    print("    DiaryPage OK")
    from ui.pages.planner import PlannerPage

    print("    PlannerPage OK")
    from ui.pages.recipes import RecipesPage

    print("    RecipesPage OK")
    from ui.pages.products import ProductsPage

    print("    ProductsPage OK")
    from ui.pages.ai_chat import AIChatPage

    print("    AIChatPage OK")
    # from ui.pages.analytics import AnalyticsPage  # отключено из-за segmentation fault
    # print("    AnalyticsPage OK")
    from ui.pages.photo_analysis import PhotoAnalysisPage

    print("    PhotoAnalysisPage OK")
    from ui.pages.settings_notifications import SettingsNotificationsPage

    print("    SettingsNotificationsPage OK")
    from ui.pages.settings_diets import SpecialDietsPage

    print("    SpecialDietsPage OK")
    from ui.pages.settings_api import APIIntegrationPage

    print("    APIIntegrationPage OK")
except ImportError as e:
    print(f"CRITICAL ERROR: Не удалось импортировать страницы: {e}")
    sys.exit(1)

print("  [main_window] Импорт сервисов...")
# Импорт сервисов (исправлены на существующие модули)
try:
    from core.notifications import SmartNotifications
    from core.special_diets import SpecialDiets

    print("    Сервисы импортированы")
except ImportError as e:
    print(f"WARNING: Не удалось импортировать сервисы: {e}")
    SmartNotifications = None
    SpecialDiets = None

print("  [main_window] Импорт операций БД...")
# Импорт операций с БД
try:
    from database.operations import get_user

    print("    get_user импортирован")
except ImportError:
    get_user = None
    print("WARNING: database.operations не найден. Пользователь не будет загружен.")


class MainWindow(QMainWindow):
    def __init__(self):
        print("  [MainWindow] __init__ начало")
        super().__init__()
        print("  [MainWindow] super().__init__() выполнено")
        self.setWindowTitle("HealthAI - Умный помощник питания")
        self.setMinimumSize(1200, 800)

        print("  [MainWindow] Загрузка текущего пользователя...")
        self.current_user = None
        if get_user:
            try:
                self.current_user = get_user(1)
                print(f"  [MainWindow] Пользователь: {self.current_user.name if self.current_user else 'None'}")
            except Exception as e:
                print(f"  [MainWindow] Ошибка получения пользователя: {e}")

        print("  [MainWindow] Инициализация сервисов...")
        self.notification_service = None
        if SmartNotifications and self.current_user:
            try:
                self.notification_service = SmartNotifications(self.current_user.id)
                print("  [MainWindow] SmartNotifications создан")
            except Exception as e:
                print(f"  [MainWindow] Ошибка SmartNotifications: {e}")

        self.diets_service = None
        if SpecialDiets:
            try:
                self.diets_service = SpecialDiets()
                print("  [MainWindow] SpecialDiets создан")
            except Exception as e:
                print(f"  [MainWindow] Ошибка SpecialDiets: {e}")

        print("  [MainWindow] Вызов init_ui()...")
        self.init_ui()
        print("  [MainWindow] init_ui() завершён")
        print("  [MainWindow] Вызов apply_styles()...")
        self.apply_styles()
        print("  [MainWindow] apply_styles() завершён")
        print("  [MainWindow] __init__ завершён успешно")

    def init_ui(self):
        print("    [init_ui] Начало")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        print("    [init_ui] Создание сайдбара...")
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(280)
        sidebar.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(10)
        sidebar_layout.setContentsMargins(20, 30, 20, 30)

        logo_label = QLabel("🍏 HealthAI")
        logo_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        logo_label.setStyleSheet("color: #3498DB; padding: 10px 0;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(logo_label)

        self.nav_buttons = []
        pages = [
            ("📊 Дашборд", DashboardPage),
            ("🧮 Калькулятор", CalculatorPage),
            ("📔 Дневник", DiaryPage),
            ("📅 Планировщик", PlannerPage),
            ("🥗 Рецепты", RecipesPage),
            ("🍎 Продукты", ProductsPage),
            ("🤖 AI Нутрициолог", AIChatPage),
            # ("📈 Аналитика", AnalyticsPage),  # временно отключено из-за проблем с matplotlib
            ("📸 Фото еды", PhotoAnalysisPage),
            ("⚙️ Настройки", None)
        ]

        for text, page_class in pages:
            if page_class is None:
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

        print("    [init_ui] Создание QStackedWidget...")
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: transparent;")

        print("    [init_ui] Добавление страниц...")
        self.pages = {}
        for _, page_class in self.nav_buttons:
            if page_class:
                print(f"      Создание {page_class.__name__}...")
                try:
                    page = page_class(main_window=self)
                except TypeError:
                    page = page_class()
                except Exception as e:
                    print(f"      Ошибка создания {page_class.__name__}: {e}")
                    error_page = QLabel(f"Ошибка загрузки страницы: {e}")
                    error_page.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.stack.addWidget(error_page)
                    self.pages[page_class] = error_page
                    continue
                self.stack.addWidget(page)
                self.pages[page_class] = page
                print(f"      {page_class.__name__} добавлена")

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)
        print("    [init_ui] Сайдбар и стек добавлены")

        if DashboardPage in self.pages:
            print("    [init_ui] Переход на дашборд")
            self.navigate_to(DashboardPage)

        print("    [init_ui] Конец")

    def navigate_to(self, page_class):
        if page_class not in self.pages:
            return

        for btn, _ in self.nav_buttons:
            btn.setChecked(False)

        for btn, cls in self.nav_buttons:
            if cls == page_class:
                btn.setChecked(True)
                break

        index = list(self.pages.keys()).index(page_class)
        self.stack.setCurrentIndex(index)

        page = self.pages[page_class]
        if hasattr(page, 'refresh') and callable(page.refresh):
            page.refresh()

    def update_calorie_display(self):
        dashboard = self.pages.get(DashboardPage)
        if dashboard and hasattr(dashboard, 'refresh'):
            dashboard.refresh()

    def check_user(self):
        if get_user:
            self.current_user = get_user(1)
            for page in self.pages.values():
                if hasattr(page, 'refresh') and callable(page.refresh):
                    page.refresh()

    def apply_styles(self):
        self.setStyleSheet(Styles.get_stylesheet())

    def closeEvent(self, event):
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    set_theme("light")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
