"""
Сервис уведомлений для HealthAI
Реализует фоновые уведомления с использованием QTimer
"""

from PyQt6.QtCore import QObject, QTimer, QTime, pyqtSignal
from datetime import datetime, time
from typing import Dict, List, Optional
import json


class NotificationService(QObject):
    """Сервис управления умными уведомлениями"""
    
    notification_triggered = pyqtSignal(str, str)  # title, message
    
    def __init__(self, db_session=None):
        super().__init__()
        self.db_session = db_session
        self.timers: Dict[str, QTimer] = {}
        self.active_notifications: List[Dict] = []
        self.settings = self._load_default_settings()
        
    def _load_default_settings(self) -> Dict:
        """Загрузка настроек уведомлений по умолчанию"""
        return {
            'breakfast': {'enabled': True, 'time': '08:00', 'message': 'Пора завтракать! 🍳'},
            'lunch': {'enabled': True, 'time': '13:00', 'message': 'Обеденное время! 🥗'},
            'dinner': {'enabled': True, 'time': '19:00', 'message': 'Время ужина! 🍽️'},
            'snack': {'enabled': False, 'time': '16:00', 'message': 'Перекусить не помешает! 🍎'},
            'water_morning': {'enabled': True, 'time': '09:00', 'message': 'Выпейте стакан воды! 💧'},
            'water_afternoon': {'enabled': True, 'time': '15:00', 'message': 'Не забывайте пить воду! 💧'},
            'water_evening': {'enabled': True, 'time': '20:00', 'message': 'Вечерний стакан воды! 💧'},
            'weigh_in': {'enabled': False, 'time': '08:00', 'message': 'Пора взвеситься! ⚖️'},
            'log_meal': {'enabled': True, 'time': '21:00', 'message': 'Не забудьте записать ужин! 📝'},
            'motivation': {'enabled': True, 'time': '12:00', 'message': 'Вы отлично справляетесь! 💪'}
        }
    
    def load_settings(self, user_id: int = 1):
        """Загрузка настроек из БД"""
        if self.db_session:
            try:
                from database.models import UserSettings
                settings_obj = self.db_session.query(UserSettings).filter(
                    UserSettings.user_id == user_id,
                    UserSettings.key == 'notifications'
                ).first()
                
                if settings_obj and settings_obj.value:
                    self.settings = json.loads(settings_obj.value)
            except Exception as e:
                print(f"Error loading notification settings: {e}")
        
        return self.settings
    
    def save_settings(self, user_id: int = 1):
        """Сохранение настроек в БД"""
        if self.db_session:
            try:
                from database.models import UserSettings
                settings_obj = self.db_session.query(UserSettings).filter(
                    UserSettings.user_id == user_id,
                    UserSettings.key == 'notifications'
                ).first()
                
                if not settings_obj:
                    settings_obj = UserSettings(
                        user_id=user_id,
                        key='notifications',
                        value=json.dumps(self.settings)
                    )
                    self.db_session.add(settings_obj)
                else:
                    settings_obj.value = json.dumps(self.settings)
                
                self.db_session.commit()
                return True
            except Exception as e:
                print(f"Error saving notification settings: {e}")
                self.db_session.rollback()
                return False
        return True
    
    def start_all_timers(self):
        """Запуск всех активных таймеров"""
        self.stop_all_timers()
        
        for key, config in self.settings.items():
            if config.get('enabled', False):
                self._create_timer(key, config['time'])
    
    def _create_timer(self, key: str, time_str: str):
        """Создание таймера для конкретного уведомления"""
        try:
            hours, minutes = map(int, time_str.split(':'))
            target_time = QTime(hours, minutes)
            
            timer = QTimer()
            timer.setSingleShot(False)
            
            # Проверка каждую минуту
            timer.timeout.connect(lambda k=key, t=target_time: self._check_notification(k, t))
            timer.start(60000)  # 1 минута
            
            self.timers[key] = timer
            print(f"Timer started for {key} at {time_str}")
        except Exception as e:
            print(f"Error creating timer for {key}: {e}")
    
    def _check_notification(self, key: str, target_time: QTime):
        """Проверка необходимости отправки уведомления"""
        current_time = QTime.currentTime()
        
        # Уведомление если время совпадает (с точностью до минуты)
        if current_time.hour() == target_time.hour() and \
           current_time.minute() == target_time.minute():
            
            # Проверка чтобы не спамить (не чаще раза в час)
            last_sent = None
            for notif in self.active_notifications:
                if notif['key'] == key:
                    last_sent = notif['time']
            
            if last_sent:
                from datetime import timedelta
                if datetime.now() - last_sent < timedelta(hours=1):
                    return
            
            config = self.settings.get(key, {})
            message = config.get('message', 'Уведомление')
            
            self.notification_triggered.emit(
                f"HealthAI - {key.replace('_', ' ').title()}",
                message
            )
            
            self.active_notifications.append({
                'key': key,
                'time': datetime.now(),
                'message': message
            })
            
            # Очистка старых записей
            self.active_notifications = [
                n for n in self.active_notifications 
                if datetime.now() - n['time'] < timedelta(hours=2)
            ]
    
    def stop_all_timers(self):
        """Остановка всех таймеров"""
        for timer in self.timers.values():
            timer.stop()
        self.timers.clear()
    
    def stop_timer(self, key: str):
        """Остановка конкретного таймера"""
        if key in self.timers:
            self.timers[key].stop()
            del self.timers[key]
    
    def test_notification(self, key: str):
        """Тестовое уведомление"""
        config = self.settings.get(key, {})
        message = config.get('message', 'Тестовое уведомление')
        self.notification_triggered.emit(
            f"HealthAI - Тест ({key})",
            message
        )
    
    def get_active_timers(self) -> List[str]:
        """Список активных таймеров"""
        return [key for key, config in self.settings.items() if config.get('enabled', False)]
    
    def update_setting(self, key: str, enabled: bool = None, time: str = None, message: str = None):
        """Обновление настройки уведомления"""
        if key not in self.settings:
            return False
        
        if enabled is not None:
            self.settings[key]['enabled'] = enabled
        if time is not None:
            self.settings[key]['time'] = time
        if message is not None:
            self.settings[key]['message'] = message
        
        # Пересоздать таймер если изменилось время или статус
        if enabled is not None or time is not None:
            if self.settings[key]['enabled']:
                self._create_timer(key, self.settings[key]['time'])
            else:
                self.stop_timer(key)
        
        return True


# Глобальный экземпляр сервиса
_notification_service: Optional[NotificationService] = None

def get_notification_service(db_session=None) -> NotificationService:
    """Получение экземпляра сервиса уведомлений"""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService(db_session)
    elif db_session and _notification_service.db_session is None:
        _notification_service.db_session = db_session
    return _notification_service
