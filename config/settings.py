# Настройки приложения HealthAI
import os

# Определение корневой директории проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Пути к файлам
DATA_DIR = os.path.join(BASE_DIR, 'assets')
DB_DIR = os.path.join(BASE_DIR, 'database')
DB_PATH = os.path.join(DB_DIR, 'healthai.db')

# Создаём директорию для БД если не существует
os.makedirs(DB_DIR, exist_ok=True)

# Настройки приложения
APP_NAME = "HealthAI"
APP_VERSION = "1.0.0"

# Цветовая палитра (современный зелёный дизайн)
COLORS = {
    'primary': '#2E7D32',         # Медицинский зелёный
    'primary_light': '#81C784',    # Светло-зелёный
    'primary_dark': '#1B5E20',     # Тёмно-зелёный
    'primary_hover': '#388E3C',    # Зелёный при наведении
    'secondary': '#FF7043',        # Оранжевый для акцентов
    'secondary_light': '#FFAB91',  # Светло-оранжевый
    'background': '#F5F7FA',       # Светло-серый фон
    'surface': '#FFFFFF',          # Белый для карточек
    'error': '#E53935',            # Красный для ошибок
    'error_light': '#FFCDD2',      # Светло-красный для фона
    'warning': '#FFA726',          # Оранжевый для предупреждений
    'warning_light': '#FFE0B2',    # Светло-оранжевый для фона
    'success': '#66BB6A',          # Зелёный для успеха
    'success_light': '#C8E6C9',    # Светло-зелёный для фона
    'text_primary': '#212121',     # Основной текст
    'text_secondary': '#757575',   # Вторичный текст
    'text_hint': '#9E9E9E',        # Текст-подсказка
    'border': '#E0E0E0',           # Границы элементов
    'border_focus': '#2E7D32',     # Граница при фокусе
    'divider': '#BDBDBD',          # Разделитель
    'shadow': '#40000000',         # Тень
}

# Размеры шрифтов
FONTS = {
    'h1': 24,
    'h2': 18,
    'h3': 16,
    'body': 14,
    'caption': 12,
    'small': 10,
}

# Уровни активности (множители для TDEE)
ACTIVITY_LEVELS = {
    'sedentary': {'name': 'Малоподвижный образ жизни', 'multiplier': 1.2},
    'light': {'name': 'Лёгкая активность', 'multiplier': 1.375},
    'moderate': {'name': 'Умеренная активность', 'multiplier': 1.55},
    'active': {'name': 'Активный образ жизни', 'multiplier': 1.725},
    'very_active': {'name': 'Очень активный', 'multiplier': 1.9},
}

# Цели питания
GOALS = {
    'lose': {'name': 'Похудение', 'calorie_modifier': -0.15, 'description': 'Снижение веса'},
    'maintain': {'name': 'Поддержание веса', 'calorie_modifier': 0, 'description': 'Сохранение текущего веса'},
    'gain': {'name': 'Набор массы', 'calorie_modifier': 0.15, 'description': 'Увеличение мышечной массы'},
}

# Стандартные размеры порций (в граммах)
STANDARD_PORTIONS = {
    'small': 50,
    'medium': 100,
    'large': 200,
    'xlarge': 300,
}

# Настройки базы данных
DATABASE = {
    'path': DB_PATH,
    'echo': False,
}
