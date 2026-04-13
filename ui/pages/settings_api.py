"""
Страница интеграции с внешними API питания.
Позволяет подключать сервисы (Edamam, USDA, Spoonacular) для расширения базы продуктов и рецептов.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QLineEdit, QScrollArea, QFrame, QCheckBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ui.font_helpers import emoji_font_family, ui_font_family
from ui.styles import Styles
from ui.components.dialogs import show_error, show_message, show_warning


class APIServiceCard(QWidget):
    """Карточка сервиса API с настройками подключения"""

    connection_tested = pyqtSignal(str, bool)
    settings_saved = pyqtSignal(str, dict)

    def __init__(self, service_id: str, name: str, description: str, icon: str,
                 api_key_label: str, docs_url: str, parent=None):
        super().__init__(parent)
        self.service_id = service_id
        self.docs_url = docs_url

        self.setFixedHeight(180)
        self.setStyleSheet("""
            APIServiceCard {
                background-color: #fff;
                border-radius: 15px;
                border: 1px solid #eee;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)

        # Заголовок с иконкой
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        icon_label = QLabel(icon)
        icon_label.setFont(QFont(emoji_font_family(), 24))
        header_layout.addWidget(icon_label)

        title_label = QLabel(name)
        title_label.setFont(QFont(ui_font_family(), 14, QFont.Weight.Bold))
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Статус подключения
        self.status_label = QLabel("❌ Не подключено")
        self.status_label.setFont(QFont(ui_font_family(), 9))
        self.status_label.setStyleSheet("color: #e74c3c;")
        header_layout.addWidget(self.status_label)

        layout.addLayout(header_layout)

        # Описание
        desc_label = QLabel(description)
        desc_label.setFont(QFont(ui_font_family(), 10))
        desc_label.setStyleSheet("color: #666;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # Поле API ключа
        key_layout = QHBoxLayout()
        key_layout.setSpacing(10)

        key_label = QLabel(api_key_label + ":")
        key_label.setFont(QFont(ui_font_family(), 10))
        key_layout.addWidget(key_label)

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Введите API ключ...")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setFont(QFont("Consolas", 10))
        key_layout.addWidget(self.api_key_input, 1)

        # Кнопка показать/скрыть
        self.show_btn = QPushButton("👁️")
        self.show_btn.setFixedSize(40, 30)
        self.show_btn.clicked.connect(self.toggle_key_visibility)
        key_layout.addWidget(self.show_btn)

        layout.addLayout(key_layout)

        # Кнопки действий
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        # Тест подключения
        test_btn = QPushButton("🔍 Проверить")
        test_btn.setFixedHeight(35)
        test_btn.clicked.connect(self.test_connection)
        btn_layout.addWidget(test_btn)

        # Документация
        docs_btn = QPushButton("📖 Документация")
        docs_btn.setFixedHeight(35)
        docs_btn.clicked.connect(self.open_docs)
        btn_layout.addWidget(docs_btn)

        btn_layout.addStretch()

        # Сохранить
        save_btn = QPushButton("💾 Сохранить")
        save_btn.setFixedHeight(35)
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def toggle_key_visibility(self):
        """Переключить видимость API ключа"""
        if self.api_key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_btn.setText("🙈")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_btn.setText("👁️")

    def test_connection(self):
        """Тест подключения к API (симуляция)"""
        api_key = self.api_key_input.text().strip()

        if not api_key:
            show_warning(self, "Проверка API", "Введите API ключ для проверки!")
            return

        # Симуляция проверки (в реальности здесь будет запрос к API)
        self.status_label.setText("⏳ Проверка...")
        self.status_label.setStyleSheet("color: #f39c12;")

        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1500, lambda: self._simulate_test_result(api_key))

    def _simulate_test_result(self, api_key: str):
        """Симуляция результата теста"""
        # Для демо считаем valid ключи длиной > 10 символов
        is_valid = len(api_key) > 10

        if is_valid:
            self.status_label.setText("✅ Подключено")
            self.status_label.setStyleSheet("color: #2ecc71;")
            self.connection_tested.emit(self.service_id, True)
            show_message(self, "Успех", f"Подключение к {self.service_id} успешно!")
        else:
            self.status_label.setText("❌ Ошибка")
            self.status_label.setStyleSheet("color: #e74c3c;")
            self.connection_tested.emit(self.service_id, False)
            show_error(self, "Ошибка", "Неверный API ключ или сеть недоступна.")

    def open_docs(self):
        """Открыть документацию"""
        import webbrowser
        webbrowser.open(self.docs_url)

    def save_settings(self):
        """Сохранение настроек"""
        api_key = self.api_key_input.text().strip()

        if not api_key:
            show_warning(self, "Сохранение", "Введите API ключ!")
            return

        settings = {
            'api_key': api_key,
            'enabled': True
        }

        self.settings_saved.emit(self.service_id, settings)

        # Визуальный эффект
        self.status_label.setText("✅ Сохранено")
        self.status_label.setStyleSheet("color: #2ecc71;")


class APIIntegrationPage(QWidget):
    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setObjectName("apiIntegrationPage")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Заголовок
        header = QLabel("🌐 Интеграция с API")
        header.setFont(QFont(ui_font_family(), 24, QFont.Weight.Bold))
        layout.addWidget(header)

        subtitle = QLabel(
            "Подключите внешние сервисы для расширения базы продуктов и рецептов. Получайте актуальную нутрициологическую информацию.")
        subtitle.setFont(QFont(ui_font_family(), 11))
        subtitle.setStyleSheet("color: #666; margin-bottom: 20px;")
        layout.addWidget(subtitle)

        # Предупреждение
        info_box = QFrame()
        info_box.setStyleSheet("""
            QFrame {
                background-color: #e8f4fd;
                border-left: 4px solid #3498db;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        info_layout = QVBoxLayout(info_box)
        info_layout.setSpacing(5)

        info_title = QLabel("ℹ️ Как получить API ключи?")
        info_title.setFont(QFont(ui_font_family(), 11, QFont.Weight.Bold))
        info_title.setStyleSheet("color: #2980b9;")
        info_layout.addWidget(info_title)

        info_text = QLabel(
            "Зарегистрируйтесь на сайтах сервисов и получите бесплатные API ключи в разделе разработчика. Большинство сервисов предоставляют бесплатный тариф с лимитами.")
        info_text.setFont(QFont(ui_font_family(), 10))
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)

        layout.addWidget(info_box)

        # Скролл область
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("border: none; background: transparent;")

        container = QWidget()
        self.services_layout = QVBoxLayout(container)
        self.services_layout.setSpacing(20)

        # Сервисы
        self.service_cards = {}

        services = [
            (
                "edamam",
                "Edamam Nutrition API",
                "Одна из крупнейших баз продуктов с подробной информацией о нутриентах, витаминах и минералах. Более 1M продуктов.",
                "🥗",
                "API Key & App ID",
                "https://developer.edamam.com/"
            ),
            (
                "usda",
                "USDA FoodData Central",
                "Официальная база данных Министерства сельского хозяйства США. Бесплатный доступ к детальной информации о продуктах.",
                "🇺🇸",
                "API Key",
                "https://fdc.nal.usda.gov/api-key-request.html"
            ),
            (
                "spoonacular",
                "Spoonacular Food API",
                "База рецептов с возможностью поиска по ингредиентам, анализом рецептов и планированием питания. 500K+ рецептов.",
                "🍳",
                "API Key",
                "https://spoonacular.com/food-api"
            ),
            (
                "nutritionix",
                "Nutritionix API",
                "Крупнейшая в мире база продуктов с данными от ресторанов и брендов. Удобный поиск по названиям и штрих-кодам.",
                "🏪",
                "App ID & API Key",
                "https://developer.nutritionix.com/"
            ),
        ]

        for serv_id, name, desc, icon, key_label, docs_url in services:
            card = APIServiceCard(serv_id, name, desc, icon, key_label, docs_url)
            card.connection_tested.connect(self.handle_connection_test)
            card.settings_saved.connect(self.handle_settings_save)
            self.service_cards[serv_id] = card
            self.services_layout.addWidget(card)

        self.services_layout.addStretch()

        scroll.setWidget(container)
        layout.addWidget(scroll, 1)

        # Глобальные настройки
        global_group = QGroupBox("⚙️ Глобальные настройки API")
        global_group.setFont(QFont(ui_font_family(), 12, QFont.Weight.Bold))
        global_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #ddd;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: #fff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px;
                color: #333;
            }
        """)

        global_layout = QVBoxLayout()

        # Авто-синхронизация
        auto_sync_check = QCheckBox("Автоматически синхронизировать данные при запуске приложения")
        auto_sync_check.setChecked(True)
        auto_sync_check.setFont(QFont(ui_font_family(), 10))
        global_layout.addWidget(auto_sync_check)

        # Кэширование
        cache_check = QCheckBox("Кэшировать результаты запросов (рекомендуется для экономии лимитов)")
        cache_check.setChecked(True)
        cache_check.setFont(QFont(ui_font_family(), 10))
        global_layout.addWidget(cache_check)

        # Приоритет источников
        priority_label = QLabel("Приоритет источников (перетаскивайте для изменения):")
        priority_label.setFont(QFont(ui_font_family(), 10))
        global_layout.addWidget(priority_label)

        priority_list = QLabel("1. Edamam → 2. USDA → 3. Spoonacular → 4. Nutritionix")
        priority_list.setFont(QFont("Consolas", 10))
        priority_list.setStyleSheet("background-color: #f5f5f5; padding: 10px; border-radius: 5px;")
        global_layout.addWidget(priority_list)

        global_group.setLayout(global_layout)
        layout.addWidget(global_group)

    def handle_connection_test(self, service_id: str, success: bool):
        """Обработка результата теста подключения"""
        pass

    def handle_settings_save(self, service_id: str, settings: dict):
        """Обработка сохранения настроек"""
        # Здесь можно сохранить в конфиг или БД
        print(f"Saved settings for {service_id}: {settings}")
