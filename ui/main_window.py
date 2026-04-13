# ui/main_window.py
import logging
import os
import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget, QFrame, \
    QSizePolicy, QApplication, QMenuBar, QMenu
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QAction, QKeySequence

# Импорт стилей
from ui.styles import Styles, set_theme

_log = logging.getLogger(__name__)

# Импорт страниц
try:
    from ui.pages.dashboard import DashboardPage
    from ui.pages.profile_page import ProfilePage
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
    logging.getLogger(__name__).critical("Не удалось импортировать страницы: %s", e)
    sys.exit(1)

_log.debug("Страницы UI импортированы")

# Импорт сервисов (исправлены на существующие модули)
try:
    from core.notifications import SmartNotifications
    from core.special_diets import SpecialDiets
except ImportError as e:
    _log.warning("Сервисы уведомлений/диет недоступны: %s", e)
    SmartNotifications = None
    SpecialDiets = None

# Импорт операций с БД
try:
    from config.settings import APP_ICON_PATH
except ImportError:
    APP_ICON_PATH = ""

try:
    from database.operations import get_user
except ImportError:
    get_user = None
    _log.warning("database.operations не найден — пользователь не будет загружен из БД")


class MainWindow(QMainWindow):
    def __init__(self):
        _log.debug("MainWindow: init")
        super().__init__()
        self.setWindowTitle("HealthAI - Умный помощник питания")
        self.setMinimumSize(1200, 800)
        if APP_ICON_PATH and os.path.isfile(APP_ICON_PATH):
            self.setWindowIcon(QIcon(APP_ICON_PATH))

        self.current_user = None
        if get_user:
            try:
                self.current_user = get_user(1)
                _log.info("Текущий пользователь: %s", getattr(self.current_user, "name", None))
            except Exception as e:
                _log.warning("Ошибка получения пользователя: %s", e)

        self.notification_service = None
        if SmartNotifications and self.current_user:
            try:
                self.notification_service = SmartNotifications(self.current_user.id)
            except Exception as e:
                _log.warning("SmartNotifications: %s", e)

        self.diets_service = None
        if SpecialDiets:
            try:
                self.diets_service = SpecialDiets()
            except Exception as e:
                _log.warning("SpecialDiets: %s", e)

        self._chat_shutdown_done = False
        self._photo_ml_shutdown_done = False

        self._setup_menu_bar()
        self.init_ui()
        self.apply_styles()
        _log.debug("MainWindow: готов")

    def _shutdown_chat_workers_once(self) -> None:
        """Один раз при закрытии главного окна — до разрушения дочерних виджетов."""
        if self._chat_shutdown_done:
            return
        self._chat_shutdown_done = True
        try:
            chat_page = self.pages.get(AIChatPage)
            if chat_page is not None and hasattr(chat_page, "shutdown_background_threads"):
                chat_page.shutdown_background_threads()
        except Exception as e:
            _log.warning("Остановка потоков чата при выходе: %s", e)

    def _shutdown_photo_ml_once(self) -> None:
        if self._photo_ml_shutdown_done:
            return
        self._photo_ml_shutdown_done = True
        try:
            photo_page = self.pages.get(PhotoAnalysisPage)
            if photo_page is not None:
                uploader = getattr(photo_page, "uploader", None)
                if uploader is not None and hasattr(uploader, "release_ml_resources"):
                    uploader.release_ml_resources()
        except Exception as e:
            _log.warning("Освобождение ML при выходе (фото): %s", e)

    def _setup_menu_bar(self):
        """Файл: выход; Справка: о программе и про регистрацию."""
        from config.settings import APP_NAME, APP_VERSION

        bar = QMenuBar(self)
        self.setMenuBar(bar)

        file_menu = bar.addMenu("Файл")
        act_quit = QAction("Выход", self)
        act_quit.setShortcut(QKeySequence.StandardKey.Quit)
        # Не вызывать QApplication.quit() напрямую: тогда не приходит closeEvent,
        # потоки чата (QThread) уничтожаются «на лету» → abort.
        act_quit.triggered.connect(self.close)
        file_menu.addAction(act_quit)

        help_menu = bar.addMenu("Справка")
        act_about = QAction("О программе…", self)
        act_about.triggered.connect(self._show_about)
        help_menu.addAction(act_about)
        act_reg = QAction("Учётная запись…", self)
        act_reg.triggered.connect(self._show_account_info)
        help_menu.addAction(act_reg)

    def _show_about(self):
        from config.settings import APP_NAME, APP_VERSION
        from PyQt6.QtWidgets import QMessageBox

        from ui.components.dialogs import show_rich_message

        show_rich_message(
            self,
            f"О {APP_NAME}",
            f"<b>{APP_NAME}</b> v{APP_VERSION}<br><br>"
            "Приложение для учёта питания и рекомендаций.<br><br>"
            "© HealthAI Team",
            QMessageBox.Icon.NoIcon,
        )

    def _show_account_info(self):
        from PyQt6.QtWidgets import QMessageBox

        from ui.components.dialogs import show_rich_message

        show_rich_message(
            self,
            "Учётная запись",
            "<b>Профиль</b><br>"
            "Параметры (рост, вес, активность, цель) можно изменить в любой момент в боковом меню "
            "«Профиль».<br><br>"
            "<b>Первый запуск</b><br>"
            "Мастер настройки заполняет ту же запись в локальной базе.<br><br>"
            "<b>Выход</b><br>"
            "«Файл» → «Выход» или Cmd+Q (macOS). Отдельного входа по паролю нет — один локальный пользователь.",
            QMessageBox.Icon.Information,
        )

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

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
            ("👤 Профиль", ProfilePage),
            ("🧮 Калькулятор", CalculatorPage),
            ("📔 Дневник", DiaryPage),
            ("📅 Планировщик", PlannerPage),
            ("🥗 Рецепты", RecipesPage),
            ("🍎 Продукты", ProductsPage),
            ("🤖 AI Нутрициолог", AIChatPage),
            ("📈 Аналитика", AnalyticsPage),
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

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: transparent;")

        # Ленивая загрузка: тяжёлые страницы (matplotlib, torch, AIEngine) создаются при первом входе,
        # а не при старте — меньше конфликтов нативных библиотек с Qt на macOS.
        self.pages: dict = {}

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)

        self.navigate_to(DashboardPage)

    def _ensure_page(self, page_class):
        if page_class in self.pages:
            return self.pages[page_class]
        try:
            try:
                page = page_class(main_window=self)
            except TypeError:
                page = page_class()
        except Exception as e:
            _log.exception("Ошибка создания страницы %s", page_class.__name__)
            err = QLabel(f"Ошибка загрузки страницы: {e}")
            err.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.stack.addWidget(err)
            self.pages[page_class] = err
            return err
        self.stack.addWidget(page)
        self.pages[page_class] = page
        _log.debug("Страница создана: %s", page_class.__name__)
        return page

    def navigate_to(self, page_class):
        page = self._ensure_page(page_class)

        for btn, _ in self.nav_buttons:
            btn.setChecked(False)

        for btn, cls in self.nav_buttons:
            if cls == page_class:
                btn.setChecked(True)
                break

        self.stack.setCurrentIndex(self.stack.indexOf(page))

        if hasattr(page, "refresh") and callable(page.refresh):
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
        from ui.styles import (
            Styles,
            sync_config_colors_with_theme,
            THEME_NAME,
            apply_app_light_palette,
            apply_app_dark_palette,
        )

        sync_config_colors_with_theme()
        app = QApplication.instance()
        if app:
            if THEME_NAME == "light":
                apply_app_light_palette(app)
            else:
                apply_app_dark_palette(app)
            app.setStyleSheet(Styles.get_stylesheet())
        self.setStyleSheet("")

    def closeEvent(self, event):
        self._shutdown_chat_workers_once()
        self._shutdown_photo_ml_once()
        super().closeEvent(event)


if __name__ == "__main__":
    import os

    # Запуск из корня проекта: python ui/main_window.py
    _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _root not in sys.path:
        sys.path.insert(0, _root)

    os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
    os.environ.setdefault("OMP_NUM_THREADS", "1")

    from core.app_logging import setup_logging
    from core.qt_lifecycle import (
        exit_after_qt_exec,
        pyqt6_disable_sip_destroy_on_exit,
        qt_safe_teardown,
    )

    setup_logging()
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_DontUseNativeDialogs, True)
    app = QApplication(sys.argv)
    pyqt6_disable_sip_destroy_on_exit()
    set_theme("light")
    window = MainWindow()
    window.show()
    app.aboutToQuit.connect(qt_safe_teardown)
    rc = app.exec()
    exit_after_qt_exec(rc)
