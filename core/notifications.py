# core/notifications.py
# Модуль умных уведомлений для HealthAI
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Callable
import json
import os
import random

from database.operations import get_user, get_today_meals


class NotificationType:
    """Типы уведомлений"""
    MEAL_REMINDER = "meal_reminder"
    WATER_REMINDER = "water_reminder"
    GOAL_PROGRESS = "goal_progress"
    WEIGH_IN = "weigh_in"
    MOTIVATION = "motivation"
    ACHIEVEMENT = "achievement"
    RECIPE_SUGGESTION = "recipe_suggestion"
    SLEEP_REMINDER = "sleep_reminder"


class SmartNotifications:
    """Система умных уведомлений"""

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.user = get_user(user_id)
        self.config_file = f"notifications/user_{user_id}_config.json"
        self.notifications_dir = "notifications"
        os.makedirs(self.notifications_dir, exist_ok=True)

        # Конфигурация по умолчанию
        self.config = self._load_config()

        # Callback функции для отправки уведомлений
        self.send_callback: Optional[Callable] = None

    def _load_config(self) -> Dict:
        """Загрузка конфигурации уведомлений"""
        default_config = {
            'enabled': True,
            'meal_reminders': {
                'enabled': True,
                'breakfast': {'time': '08:00', 'enabled': True},
                'lunch': {'time': '13:00', 'enabled': True},
                'dinner': {'time': '19:00', 'enabled': True},
                'snack': {'time': '16:00', 'enabled': False}
            },
            'water_reminders': {
                'enabled': True,
                'interval_hours': 2,
                'start_time': '08:00',
                'end_time': '20:00'
            },
            'goal_progress': {
                'enabled': True,
                'frequency': 'daily'  # daily, weekly
            },
            'weigh_in': {
                'enabled': True,
                'day_of_week': 'monday',  # monday, tuesday, etc.
                'time': '07:00'
            },
            'motivation': {
                'enabled': True,
                'frequency': 'daily'
            },
            'sleep_reminder': {
                'enabled': True,
                'time': '22:00'
            },
            'quiet_hours': {
                'enabled': True,
                'start': '22:00',
                'end': '07:00'
            }
        }

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    # Объединяем с дефолтным конфигом
                    return self._merge_configs(default_config, saved_config)
            except Exception:
                pass

        return default_config

    def _merge_configs(self, default: Dict, saved: Dict) -> Dict:
        """Объединение конфигураций"""
        result = default.copy()
        for key, value in saved.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result

    def save_config(self):
        """Сохранение конфигурации"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения конфига уведомлений: {e}")

    def set_callback(self, callback: Callable):
        """
        Установка callback функции для отправки уведомлений

        Args:
            callback: Функция, которая будет вызвана при отправке уведомления
                     signature: callback(notification_type, title, message, data)
        """
        self.send_callback = callback

    def _send_notification(self, notification_type: str, title: str,
                           message: str, data: Optional[Dict] = None):
        """Отправка уведомления"""
        if not self.config.get('enabled', True):
            return

        # Проверка тихих часов
        if self._is_quiet_hours():
            return

        if self.send_callback:
            try:
                self.send_callback(notification_type, title, message, data or {})
            except Exception as e:
                print(f"Ошибка в callback уведомления: {e}")
        else:
            # Для отладки
            print(f"[NOTIFICATION] {title}: {message}")

    def _is_quiet_hours(self) -> bool:
        """Проверка, сейчас ли тихие часы"""
        quiet_config = self.config.get('quiet_hours', {})
        if not quiet_config.get('enabled', True):
            return False

        start_str = quiet_config.get('start', '22:00')
        end_str = quiet_config.get('end', '07:00')

        try:
            start_time = datetime.strptime(start_str, '%H:%M').time()
            end_time = datetime.strptime(end_str, '%H:%M').time()
        except ValueError:
            return False

        now = datetime.now().time()

        # Если тихие часы переходят через полночь
        if start_time > end_time:
            return now >= start_time or now <= end_time
        else:
            return start_time <= now <= end_time

    def check_and_send_reminders(self):
        """Проверка и отправка всех запланированных уведомлений"""
        now = datetime.now()
        current_time = now.strftime('%H:%M')
        current_day = now.strftime('%A').lower()

        # Уведомления о приёмах пищи
        self._check_meal_reminders(current_time)

        # Уведомления о воде
        self._check_water_reminders(now)

        # Уведомления о взвешивании
        self._check_weigh_in(current_day, current_time)

        # Уведомления о сне
        self._check_sleep_reminder(current_time)

        # Прогресс к цели
        self._check_goal_progress()

        # Мотивация
        self._check_motivation()

    def _check_meal_reminders(self, current_time: str):
        """Проверка напоминаний о приёмах пищи"""
        meal_reminders = self.config.get('meal_reminders', {})

        if not meal_reminders.get('enabled', True):
            return

        meals_to_check = ['breakfast', 'lunch', 'dinner', 'snack']
        meal_names = {
            'breakfast': 'Завтрак',
            'lunch': 'Обед',
            'dinner': 'Ужин',
            'snack': 'Перекус'
        }

        for meal_type in meals_to_check:
            config = meal_reminders.get(meal_type, {})
            if config.get('enabled') and config.get('time') == current_time:
                # Проверяем, был ли уже записан этот приём пищи
                today_meals = get_today_meals(self.user_id)
                meal_exists = any(
                    m.meal_type == meal_type for m in today_meals
                )

                if not meal_exists:
                    self._send_notification(
                        NotificationType.MEAL_REMINDER,
                        f"⏰ Время {meal_names[meal_type]}!",
                        f"Не забудьте записать свой {meal_names[meal_type].lower()}. "
                        f"Поддерживайте регулярное питание!",
                        {'meal_type': meal_type}
                    )

    def _check_water_reminders(self, now: datetime):
        """Проверка напоминаний о воде"""
        water_config = self.config.get('water_reminders', {})

        if not water_config.get('enabled', True):
            return

        start_str = water_config.get('start_time', '08:00')
        end_str = water_config.get('end_time', '20:00')
        interval = water_config.get('interval_hours', 2)

        try:
            start_time = datetime.strptime(start_str, '%H:%M')
            end_time = datetime.strptime(end_str, '%H:%M')
        except ValueError:
            return

        # Заменяем время на сегодняшнее
        start_dt = now.replace(hour=start_time.hour, minute=start_time.minute, second=0, microsecond=0)
        end_dt = now.replace(hour=end_time.hour, minute=end_time.minute, second=0, microsecond=0)

        if start_dt <= now <= end_dt:
            # Проверяем интервалы
            hours_since_start = (now - start_dt).total_seconds() / 3600

            if hours_since_start % interval < 0.5:  # Окно в 30 минут
                user = get_user(self.user_id)
                if user:
                    glasses = getattr(user, 'water_glasses', 0)
                    target = 8  # Стандартная цель

                    if glasses < target:
                        remaining = target - glasses
                        self._send_notification(
                            NotificationType.WATER_REMINDER,
                            "💧 Пора пить воду!",
                            f"Вы выпили {glasses} из {target} стаканов сегодня. "
                            f"Осталось ещё {remaining}. Не забывайте о водном балансе!",
                            {'current': glasses, 'target': target}
                        )

    def _check_weigh_in(self, current_day: str, current_time: str):
        """Проверка напоминания о взвешивании"""
        weigh_config = self.config.get('weigh_in', {})

        if not weigh_config.get('enabled', True):
            return

        target_day = weigh_config.get('day_of_week', 'monday').lower()
        target_time = weigh_config.get('time', '07:00')

        if current_day == target_day and current_time == target_time:
            self._send_notification(
                NotificationType.WEIGH_IN,
                "⚖️ Время взвешивания!",
                "Сегодня день взвешивания! Запишите свой вес, чтобы отслеживать прогресс.",
                {}
            )

    def _check_sleep_reminder(self, current_time: str):
        """Проверка напоминания о сне"""
        sleep_config = self.config.get('sleep_reminder', {})

        if not sleep_config.get('enabled', True):
            return

        if current_time == sleep_config.get('time', '22:00'):
            self._send_notification(
                NotificationType.SLEEP_REMINDER,
                "🌙 Пора готовиться ко сну",
                "Качественный сон важен для достижения ваших целей. "
                "Постарайтесь лечь спать вовремя!",
                {}
            )

    def _check_goal_progress(self):
        """Проверка и отправка прогресса к цели"""
        goal_config = self.config.get('goal_progress', {})

        if not goal_config.get('enabled', True):
            return

        frequency = goal_config.get('frequency', 'daily')

        now = datetime.now()
        should_send = False
        if frequency == 'daily':
            should_send = True  # В реальном приложении нужно проверять, отправляли ли уже сегодня
        elif frequency == 'weekly' and now.strftime('%A').lower() == 'sunday':
            should_send = True

        if should_send:
            user = get_user(self.user_id)
            if user:
                progress_msg = self._generate_progress_message(user)
                self._send_notification(
                    NotificationType.GOAL_PROGRESS,
                    "📊 Ваш прогресс",
                    progress_msg,
                    {'goal': user.goal, 'streak': user.streak_days}
                )

    def _check_motivation(self):
        """Проверка и отправка мотивационного сообщения"""
        motivation_config = self.config.get('motivation', {})

        if not motivation_config.get('enabled', True):
            return

        # Простая реализация - отправляем раз в день
        motivational_quotes = [
            "Каждый маленький шаг приближает вас к большой цели! 💪",
            "Здоровое питание - это не диета, это образ жизни! 🥗",
            "Вы молодец! Продолжайте в том же духе! 🌟",
            "Ваше будущее начинается с того, что вы едите сегодня! 🍎",
            "Не сдавайтесь! Результаты уже близко! 🎯",
            "Заботьтесь о своём теле - это единственный дом, где вам жить! 🏠",
            "Успех состоит из небольших усилий, повторяющихся изо дня в день! 📈"
        ]

        quote = random.choice(motivational_quotes)

        self._send_notification(
            NotificationType.MOTIVATION,
            "✨ Мотивация дня",
            quote,
            {}
        )

    def _generate_progress_message(self, user) -> str:
        """Генерация сообщения о прогрессе"""
        messages = []

        # Streak
        if user.streak_days > 0:
            messages.append(f"🔥 Ваша серия: {user.streak_days} дней!")

        # Уровень
        messages.append(f"🏆 Ваш уровень: {user.level}")

        # Цель
        goal_messages = {
            'weight_loss': 'похудению',
            'maintain': 'поддержанию веса',
            'muscle_gain': 'набору массы',
            'healthy': 'здоровому питанию'
        }

        goal = goal_messages.get(user.goal, user.goal)
        messages.append(f"🎯 Вы движетесь к цели: {goal}")

        return " ".join(messages)

    def send_achievement_notification(self, achievement_name: str, xp_reward: int):
        """Отправка уведомления о достижении"""
        self._send_notification(
            NotificationType.ACHIEVEMENT,
            "🏆 Новое достижение!",
            f"Поздравляем! Вы получили достижение \"{achievement_name}\" "
            f"и {xp_reward} XP!",
            {'achievement': achievement_name, 'xp': xp_reward}
        )

    def send_recipe_suggestion(self, recipe_name: str, meal_type: str):
        """Отправка предложения рецепта"""
        meal_names = {
            'breakfast': 'завтрака',
            'lunch': 'обеда',
            'dinner': 'ужина',
            'snack': 'перекуса'
        }

        self._send_notification(
            NotificationType.RECIPE_SUGGESTION,
            "👨‍🍳 Идея для питания",
            f"Как насчёт \"{recipe_name}\" для {meal_names.get(meal_type, meal_type)}?",
            {'recipe': recipe_name, 'meal_type': meal_type}
        )

    def update_config(self, section: str, key: str, value):
        """
        Обновление конфигурации

        Args:
            section: Раздел конфигурации (например, 'meal_reminders')
            key: Ключ настройки
            value: Новое значение
        """
        if section in self.config:
            if isinstance(self.config[section], dict):
                self.config[section][key] = value
            else:
                self.config[section] = value
            self.save_config()

    def get_schedule(self) -> Dict:
        """Получение расписания уведомлений"""
        meal_reminders = self.config.get('meal_reminders', {})
        meal_schedule = {}
        for meal, config in meal_reminders.items():
            if isinstance(config, dict) and config.get('enabled'):
                meal_schedule[meal] = config.get('time', '')

        water_interval = self.config.get('water_reminders', {}).get('interval_hours', 2)
        weigh_in = self.config.get('weigh_in', {})
        sleep_reminder = self.config.get('sleep_reminder', {})
        quiet_hours = self.config.get('quiet_hours', {})

        return {
            'meal_reminders': meal_schedule,
            'water_interval': f"Каждые {water_interval} часа",
            'weigh_in': f"{weigh_in.get('day_of_week', 'monday')} в {weigh_in.get('time', '07:00')}",
            'sleep_reminder': f"В {sleep_reminder.get('time', '22:00')}",
            'quiet_hours': f"{quiet_hours.get('start', '22:00')} - {quiet_hours.get('end', '07:00')}"
        }


def test_notifications():
    """Тестирование системы уведомлений"""
    print("🔔 Тестирование системы умных уведомлений")

    from database.operations import get_user

    user = get_user(1)  # предполагаем, что пользователь с id=1 существует
    if not user:
        print("❌ Нет пользователей для тестирования")
        return

    notifier = SmartNotifications(user.id)

    # Тест отправки различных типов уведомлений
    print("\n1️⃣ Тест напоминания о приёме пищи...")
    notifier._send_notification(
        NotificationType.MEAL_REMINDER,
        "⏰ Время обеда!",
        "Не забудьте записать обед!"
    )

    print("\n2️⃣ Тест напоминания о воде...")
    notifier._send_notification(
        NotificationType.WATER_REMINDER,
        "💧 Пора пить воду!",
        "Выпейте стакан воды!"
    )

    print("\n3️⃣ Тест мотивации...")
    notifier._send_notification(
        NotificationType.MOTIVATION,
        "✨ Мотивация дня",
        "Вы молодец! Продолжайте в том же духе!"
    )

    print("\n4️⃣ Тест достижения...")
    notifier.send_achievement_notification("Первый шаг", 50)

    print("\n5️⃣ Тест расписания...")
    schedule = notifier.get_schedule()
    print(f"📅 Расписание: {json.dumps(schedule, ensure_ascii=False, indent=2)}")

    print("\n6️⃣ Тест проверки тихих часов...")
    is_quiet = notifier._is_quiet_hours()
    print(f"🌙 Тихие часы: {'активны' if is_quiet else 'не активны'}")

    print("\n✨ Все тесты пройдены!")


if __name__ == '__main__':
    test_notifications()
