"""
Data Manager - Экспорт/Импорт данных (CSV, JSON, PDF)
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT


class DataManager:
    """Управление экспортом и импортом данных приложения"""
    
    def __init__(self, db_session=None):
        self.db_session = db_session
    
    # ==================== ЭКСПОРТ ====================
    
    def export_to_csv(self, data: Dict[str, List[Dict]], filepath: str) -> bool:
        """
        Экспорт данных в CSV файлы
        
        Args:
            data: Словарь {имя_таблицы: [словари_данных]}
            filepath: Путь к файлу (без расширения)
        
        Returns:
            True если успешно
        """
        try:
            for table_name, records in data.items():
                if not records:
                    continue
                
                file_path = f"{filepath}_{table_name}.csv"
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=records[0].keys())
                    writer.writeheader()
                    writer.writerows(records)
            
            return True
        except Exception as e:
            print(f"Ошибка экспорта в CSV: {e}")
            return False
    
    def export_to_json(self, data: Dict[str, Any], filepath: str, indent: int = 2) -> bool:
        """
        Экспорт данных в JSON файл
        
        Args:
            data: Данные для экспорта
            filepath: Путь к файлу
            indent: Отступ для форматирования
        
        Returns:
            True если успешно
        """
        try:
            export_data = {
                'export_date': datetime.now().isoformat(),
                'version': '1.0',
                'data': data
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=indent)
            
            return True
        except Exception as e:
            print(f"Ошибка экспорта в JSON: {e}")
            return False
    
    def export_to_pdf(self, user_profile: Dict, meals: List[Dict], 
                      weight_history: List[Dict], filepath: str) -> bool:
        """
        Экспорт отчёта в PDF
        
        Args:
            user_profile: Профиль пользователя
            meals: История питания
            weight_history: История веса
            filepath: Путь к файлу
        
        Returns:
            True если успешно
        """
        try:
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Заголовок
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#2E7D32'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            story.append(Paragraph("Отчёт по питанию HealthAI", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Информация о пользователе
            story.append(Paragraph("Профиль пользователя", styles['Heading2']))
            profile_data = [
                ['Параметр', 'Значение'],
                ['Имя', user_profile.get('name', 'N/A')],
                ['Возраст', str(user_profile.get('age', 'N/A'))],
                ['Вес', f"{user_profile.get('weight', 'N/A')} кг"],
                ['Рост', f"{user_profile.get('height', 'N/A')} см"],
                ['Цель', user_profile.get('goal', 'N/A')],
                ['Калории в день', f"{user_profile.get('daily_calories', 'N/A')} ккал"]
            ]
            
            profile_table = Table(profile_data, colWidths=[2*inch, 2.5*inch])
            profile_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(profile_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Статистика питания
            story.append(Paragraph("Статистика питания (последние 7 дней)", styles['Heading2']))
            
            if meals:
                # Агрегация данных
                daily_stats = {}
                for meal in meals:
                    date = meal.get('date', 'unknown')[:10]
                    if date not in daily_stats:
                        daily_stats[date] = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0}
                    
                    daily_stats[date]['calories'] += meal.get('calories', 0)
                    daily_stats[date]['protein'] += meal.get('protein', 0)
                    daily_stats[date]['carbs'] += meal.get('carbs', 0)
                    daily_stats[date]['fat'] += meal.get('fat', 0)
                
                # Таблица статистики
                stats_data = [['Дата', 'Ккал', 'Белки (г)', 'Углеводы (г)', 'Жиры (г)']]
                for date in sorted(daily_stats.keys())[-7:]:
                    stats = daily_stats[date]
                    stats_data.append([
                        date,
                        f"{stats['calories']:.0f}",
                        f"{stats['protein']:.1f}",
                        f"{stats['carbs']:.1f}",
                        f"{stats['fat']:.1f}"
                    ])
                
                stats_table = Table(stats_data, colWidths=[1.2*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch])
                stats_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2196F3')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(stats_table)
            else:
                story.append(Paragraph("Нет данных о питании", styles['Normal']))
            
            story.append(Spacer(1, 0.3*inch))
            
            # История веса
            story.append(Paragraph("История веса", styles['Heading2']))
            
            if weight_history:
                weight_data = [['Дата', 'Вес (кг)', 'Изменение']]
                prev_weight = None
                for record in sorted(weight_history, key=lambda x: x.get('date', ''))[-10:]:
                    date = record.get('date', 'unknown')[:10]
                    weight = record.get('weight', 0)
                    change = f"{weight - prev_weight:+.2f}" if prev_weight else '-'
                    weight_data.append([date, f"{weight:.2f}", change])
                    prev_weight = weight
                
                weight_table = Table(weight_data, colWidths=[1.5*inch, 1*inch, 1*inch])
                weight_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF9800')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(weight_table)
            else:
                story.append(Paragraph("Нет данных о весе", styles['Normal']))
            
            # Подвал
            story.append(Spacer(1, 0.5*inch))
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
            story.append(Paragraph(f"Сгенерировано: {datetime.now().strftime('%d.%m.%Y %H:%M')}", footer_style))
            story.append(Paragraph("HealthAI - Ваш персональный нутрициолог", footer_style))
            
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"Ошибка экспорта в PDF: {e}")
            return False
    
    # ==================== ИМПОРТ ====================
    
    def import_from_csv(self, filepath: str, table_name: str) -> List[Dict]:
        """
        Импорт данных из CSV файла
        
        Args:
            filepath: Путь к файлу
            table_name: Имя таблицы для импорта
        
        Returns:
            Список словарей с данными
        """
        try:
            data = []
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Конвертация числовых значений
                    converted_row = {}
                    for key, value in row.items():
                        try:
                            if '.' in value:
                                converted_row[key] = float(value)
                            else:
                                converted_row[key] = int(value)
                        except (ValueError, TypeError):
                            converted_row[key] = value
                    data.append(converted_row)
            
            return data
        except Exception as e:
            print(f"Ошибка импорта из CSV: {e}")
            return []
    
    def import_from_json(self, filepath: str) -> Optional[Dict]:
        """
        Импорт данных из JSON файла
        
        Args:
            filepath: Путь к файлу
        
        Returns:
            Словарь с данными или None при ошибке
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Проверка структуры
            if 'data' in data:
                return data['data']
            return data
        except Exception as e:
            print(f"Ошибка импорта из JSON: {e}")
            return None
    
    # ==================== УТИЛИТЫ ====================
    
    def get_user_data_for_export(self, user_id: int) -> Dict:
        """
        Получение всех данных пользователя для экспорта
        
        Args:
            user_id: ID пользователя
        
        Returns:
            Словарь со всеми данными
        """
        # Здесь должна быть логика получения данных из БД
        # Для примера возвращаем структуру
        return {
            'profile': {},
            'meals': [],
            'weight_history': [],
            'achievements': [],
            'settings': {}
        }
    
    def create_backup(self, user_id: int, backup_dir: str = 'backups') -> str:
        """
        Создание резервной копии данных пользователя
        
        Args:
            user_id: ID пользователя
            backup_dir: Директория для бэкапов
        
        Returns:
            Путь к файлу бэкапа
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"user_{user_id}_backup_{timestamp}"
        filepath = Path(backup_dir) / filename
        
        Path(backup_dir).mkdir(exist_ok=True)
        
        data = self.get_user_data_for_export(user_id)
        self.export_to_json(data, f"{filepath}.json")
        
        return f"{filepath}.json"
    
    def restore_from_backup(self, filepath: str) -> bool:
        """
        Восстановление данных из бэкапа
        
        Args:
            filepath: Путь к файлу бэкапа
        
        Returns:
            True если успешно
        """
        data = self.import_from_json(filepath)
        if data:
            # Здесь должна быть логика восстановления в БД
            return True
        return False
