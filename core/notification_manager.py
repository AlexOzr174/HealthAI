"""
Notification Manager - Умные уведомления
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
import json
from pathlib import Path


class NotificationManager:
    """Система умных уведомлений для приложения"""
    
    def __init__(self, config_path: str = 'notifications_config.json'):
        self.config_path = Path(config_path)
        self.notifications = []
        self.config = self._load_config()
        self.callbacks = {}  # Callback функции для уведомлений
    
    def _load_config(self) -> Dict:
        """Загрузка конфигурации уведомлений"""
        default_config = {
            'enabled': True,
            'meal_reminders': {
                'breakfast': {'time': '08:00', 'enabled': True},
                'lunch': {'time': '13:00', 'enabled': True},
                'dinner': {'time': '19:00', 'enabled': True},
                'snack': {'time': '16:00', 'enabled': False}
            },
            'water_reminder': {
                'enabled': True,
                'interval_minutes': 60,
                'daily_goal_ml': 2000
            },
            'goal_reminders': {
                'enabled': True,
                'check_time': '20:00',
                'message_template': "Вы достигли {percent}% дневной цели по калориям!"
            },
            'weight_logging': {
                'enabled': True,
                'day_of_week': 0,  # Понедельник
                'time': '08:00'
            },
            'motivational': {
                'enabled': True,
                'times': ['09:00', '15:00', '21:00'],
                'messages': [
                    "Каждый шаг к здоровому питанию важен!",
                    "Вы молодец! Продолжайте в том же духе!",
                    "Здоровье - это инвестиция в будущее!",
                    "Маленькие изменения приводят к большим результатам!",
                    "Вы сильнее своих оправданий!"
                ]
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Объединение с дефолтным конфигом
                    return {**default_config, **config}
            except Exception:
                pass
        
        return default_config
    
    def save_config(self):
        """Сохранение конфигурации"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения конфига: {e}")
    
    def register_callback(self, notification_type: str, callback: Callable):
        """
        Регистрация callback функции для типа уведомления
        
        Args:
            notification_type: Тип уведомления (meal, water, goal, etc.)
            callback: Функция для вызова при уведомлении
        """
        self.callbacks[notification_type] = callback
    
    def check_and_send_notifications(self, user_data: Dict) -> List[Dict]:
        """
        Проверка и отправка уведомлений
        
        Args:
            user_data: Данные пользователя (прогресс, цели, etc.)
        
        Returns:
            Список отправленных уведомлений
        """
        if not self.config.get('enabled', True):
            return []
        
        sent_notifications = []
        current_time = datetime.now()
        current_hour = current_time.hour
        current_minute = current_time.minute
        current_time_str = f"{current_hour:02d}:{current_minute:02d}"
        
        # Проверка напоминаний о еде
        meal_notifications = self._check_meal_reminders(current_time_str, user_data)
        sent_notifications.extend(meal_notifications)
        
        # Проверка напоминаний о воде
        water_notifications = self._check_water_reminder(current_time, user_data)
        sent_notifications.extend(water_notifications)
        
        # Проверка прогресса целей
        goal_notifications = self._check_goal_progress(current_time_str, user_data)
        sent_notifications.extend(goal_notifications)
        
        # Проверка напоминания о взвешивании
        weight_notifications = self._check_weight_logging(current_time_str, current_time.weekday())
        sent_notifications.extend(weight_notifications)
        
        # Мотивационные уведомления
        motivational_notifications = self._check_motivational(current_time_str)
        sent_notifications.extend(motivational_notifications)
        
        # Отправка уведомлений через callbacks
        for notification in sent_notifications:
            notif_type = notification.get('type', 'general')
            if notif_type in self.callbacks:
                try:
                    self.callbacks[notif_type](notification)
                except Exception as e:
                    print(f"Ошибка callback для {notif_type}: {e}")
        
        return sent_notifications
    
    def _check_meal_reminders(self, current_time: str, user_data: Dict) -> List[Dict]:
        """Проверка напоминаний о приёмах пищи"""
        notifications = []
        meal_config = self.config.get('meal_reminders', {})
        
        meal_names = {
            'breakfast': 'завтрак',
            'lunch': 'обед',
            'dinner': 'ужин',
            'snack': 'перекус'
        }
        
        for meal_type, config in meal_config.items():
            if not config.get('enabled', False):
                continue
            
            scheduled_time = config.get('time', '')
            if scheduled_time == current_time:
                # Проверка, был ли уже приём пищи
                meals_today = user_data.get('meals_today', [])
                meal_logged = any(
                    m.get('meal_type') == meal_type 
                    for m in meals_today
                )
                
                if not meal_logged:
                    notifications.append({
                        'type': 'meal',
                        'title': f'Время {meal_names.get(meal_type, "приёма пищи")}!',
                        'message': f'Не забудьте отметить {meal_names.get(meal_type, "приём пищи")}.',
                        'priority': 'high',
                        'meal_type': meal_type,
                        'timestamp': datetime.now().isoformat()
                    })
        
        return notifications
    
    def _check_water_reminder(self, current_time: datetime, user_data: Dict) -> List[Dict]:
        """Проверка напоминаний о воде"""
        notifications = []
        water_config = self.config.get('water_reminder', {})
        
        if not water_config.get('enabled', False):
            return notifications
        
        interval = water_config.get('interval_minutes', 60)
        goal_ml = water_config.get('daily_goal_ml', 2000)
        
        # Проверка по интервалу
        last_notification = user_data.get('last_water_notification')
        if last_notification:
            last_time = datetime.fromisoformat(last_notification)
            if (current_time - last_time).total_seconds() < interval * 60:
                return notifications
        
        # Проверка прогресса
        water_consumed = user_data.get('water_consumed_ml', 0)
        if water_consumed < goal_ml:
            notifications.append({
                'type': 'water',
                'title': '💧 Время пить воду!',
                'message': f'Выпили {water_consumed}/{goal_ml} мл. Осталось {goal_ml - water_consumed} мл.',
                'priority': 'medium',
                'progress_percent': (water_consumed / goal_ml) * 100,
                'timestamp': datetime.now().isoformat()
            })
        
        return notifications
    
    def _check_goal_progress(self, current_time: str, user_data: Dict) -> List[Dict]:
        """Проверка прогресса целей"""
        notifications = []
        goal_config = self.config.get('goal_reminders', {})
        
        if not goal_config.get('enabled', False):
            return notifications
        
        check_time = goal_config.get('check_time', '20:00')
        if current_time != check_time:
            return notifications
        
        calories_consumed = user_data.get('calories_consumed', 0)
        calories_goal = user_data.get('calories_goal', 2000)
        
        if calories_goal > 0:
            percent = (calories_consumed / calories_goal) * 100
            
            message = goal_config.get('message_template', "").format(percent=int(percent))
            
            notifications.append({
                'type': 'goal',
                'title': '📊 Прогресс за день',
                'message': message,
                'priority': 'medium',
                'data': {
                    'calories_consumed': calories_consumed,
                    'calories_goal': calories_goal,
                    'percent': percent
                },
                'timestamp': datetime.now().isoformat()
            })
        
        return notifications
    
    def _check_weight_logging(self, current_time: str, weekday: int) -> List[Dict]:
        """Проверка напоминания о взвешивании"""
        notifications = []
        weight_config = self.config.get('weight_logging', {})
        
        if not weight_config.get('enabled', False):
            return notifications
        
        scheduled_day = weight_config.get('day_of_week', 0)
        scheduled_time = weight_config.get('time', '08:00')
        
        if weekday == scheduled_day and current_time == scheduled_time:
            notifications.append({
                'type': 'weight',
                'title': '⚖️ Время взвешивания!',
                'message': 'Не забудьте записать свой вес сегодня утром.',
                'priority': 'low',
                'timestamp': datetime.now().isoformat()
            })
        
        return notifications
    
    def _check_motivational(self, current_time: str) -> List[Dict]:
        """Проверка мотивационных уведомлений"""
        notifications = []
        motivational_config = self.config.get('motivational', {})
        
        if not motivational_config.get('enabled', False):
            return notifications
        
        times = motivational_config.get('times', [])
        messages = motivational_config.get('messages', [])
        
        if current_time in times and messages:
            import random
            message = random.choice(messages)
            
            notifications.append({
                'type': 'motivational',
                'title': '✨ Мотивация дня',
                'message': message,
                'priority': 'low',
                'timestamp': datetime.now().isoformat()
            })
        
        return notifications
    
    # ==================== Управление настройками ====================
    
    def enable_meal_reminder(self, meal_type: str):
        """Включить напоминание о приёме пищи"""
        if meal_type in self.config.get('meal_reminders', {}):
            self.config['meal_reminders'][meal_type]['enabled'] = True
            self.save_config()
    
    def disable_meal_reminder(self, meal_type: str):
        """Выключить напоминание о приёме пищи"""
        if meal_type in self.config.get('meal_reminders', {}):
            self.config['meal_reminders'][meal_type]['enabled'] = False
            self.save_config()
    
    def set_meal_time(self, meal_type: str, time: str):
        """Установить время напоминания о приёме пищи"""
        if meal_type in self.config.get('meal_reminders', {}):
            self.config['meal_reminders'][meal_type]['time'] = time
            self.save_config()
    
    def set_water_interval(self, minutes: int):
        """Установить интервал напоминаний о воде"""
        self.config['water_reminder']['interval_minutes'] = minutes
        self.save_config()
    
    def toggle_notifications(self, enabled: bool):
        """Включить/выключить все уведомления"""
        self.config['enabled'] = enabled
        self.save_config()
    
    def get_notification_stats(self, user_data: Dict) -> Dict:
        """Получение статистики уведомлений"""
        return {
            'enabled': self.config.get('enabled', True),
            'meal_reminders_enabled': sum(
                1 for m in self.config.get('meal_reminders', {}).values() 
                if m.get('enabled', False)
            ),
            'water_reminder_enabled': self.config.get('water_reminder', {}).get('enabled', False),
            'goal_reminders_enabled': self.config.get('goal_reminders', {}).get('enabled', False),
            'motivational_enabled': self.config.get('motivational', {}).get('enabled', False)
        }
