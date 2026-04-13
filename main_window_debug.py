# main_window_debug.py
import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from config.settings import APP_NAME, APP_VERSION
from database.init_db import init_database, populate_initial_data
from database.operations import get_user

print("=== ЗАПУСК ОТЛАДОЧНОГО РЕЖИМА ===")

# Инициализация БД
init_database()
populate_initial_data()
print("✓ БД инициализирована")

# Пытаемся получить пользователя
user = get_user(1)
print(f"✓ Пользователь: {user.name if user else 'не найден'}")

# Импортируем главное окно ПОСЛЕ инициализации, чтобы видеть, где именно падает
print("\n--- Импорт MainWindow ---")
try:
    from ui.main_window import MainWindow

    print("✓ MainWindow импортирован")
except Exception as e:
    print(f"✗ Ошибка импорта MainWindow: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n--- Создание QApplication ---")
QApplication.setAttribute(Qt.ApplicationAttribute.AA_DontUseNativeDialogs, True)
app = QApplication(sys.argv)
app.setStyle('Fusion')
print("✓ QApplication создан")

print("\n--- Создание главного окна ---")
try:
    window = MainWindow()
    print("✓ Главное окно создано")
except Exception as e:
    print(f"✗ Ошибка создания окна: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n--- Показ окна ---")
window.show()
print("✓ Окно показано")

print("\n=== ЗАПУСК ЦИКЛА ОБРАБОТКИ СОБЫТИЙ ===")
sys.exit(app.exec())
