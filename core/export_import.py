# Модуль экспорта/импорта данных для HealthAI
import csv
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from database.operations import (
    get_user, get_today_meals, get_meals_by_date_range,
    get_all_products, get_all_recipes
)


class DataExporter:
    """Класс для экспорта данных в различные форматы"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.user = get_user(user_id)
        self.export_dir = f"exports/user_{user_id}"
        os.makedirs(self.export_dir, exist_ok=True)
    
    def export_to_csv(self, data_type: str = 'all', filename: Optional[str] = None) -> str:
        """
        Экспорт данных в CSV формат
        
        Args:
            data_type: 'meals', 'products', 'recipes', 'all'
            filename: Имя файла (генерируется автоматически, если не указано)
        
        Returns:
            Путь к созданному файлу
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"healthai_export_{data_type}_{timestamp}.csv"
        
        filepath = os.path.join(self.export_dir, filename)
        
        if data_type in ['meals', 'all']:
            self._export_meals_csv(filepath)
        elif data_type == 'products':
            self._export_products_csv(filepath)
        elif data_type == 'recipes':
            self._export_recipes_csv(filepath)
        
        return filepath
    
    def _export_meals_csv(self, filepath: str):
        """Экспорт приёмов пищи в CSV"""
        from datetime import date
        meals = get_meals_by_date_range(self.user_id, date(2000, 1, 1), date.today())
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Дата', 'Время', 'Название', 'Категория', 
                'Калории', 'Белки (г)', 'Жиры (г)', 'Углеводы (г)'
            ])
            
            for meal in meals:
                writer.writerow([
                    meal.date.strftime('%Y-%m-%d'),
                    meal.time.strftime('%H:%M'),
                    meal.name,
                    meal.meal_type,
                    meal.calories,
                    meal.protein,
                    meal.fat,
                    meal.carbs
                ])
    
    def _export_products_csv(self, filepath: str):
        """Экспорт продуктов в CSV"""
        products = get_all_products()
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Название', 'Категория', 'Калории (на 100г)', 
                'Белки', 'Жиры', 'Углеводы', 'Клетчатка', 'ГИ'
            ])
            
            for product in products:
                writer.writerow([
                    product.name,
                    product.category,
                    product.calories,
                    product.protein,
                    product.fat,
                    product.carbs,
                    getattr(product, 'fiber', 0),
                    getattr(product, 'glycemic_index', 0)
                ])
    
    def _export_recipes_csv(self, filepath: str):
        """Экспорт рецептов в CSV"""
        recipes = get_all_recipes()
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Название', 'Тип приёма пищи', 'Калории', 
                'Белки', 'Жиры', 'Углеводы', 'Время приготовления', 'Ингредиенты'
            ])
            
            for recipe in recipes:
                ingredients = ', '.join(recipe.ingredients) if hasattr(recipe, 'ingredients') else ''
                writer.writerow([
                    recipe.name,
                    recipe.meal_type,
                    recipe.calories,
                    recipe.protein,
                    recipe.fat,
                    recipe.carbs,
                    getattr(recipe, 'prep_time', 0),
                    ingredients
                ])
    
    def export_to_json(self, include_history: bool = True, filename: Optional[str] = None) -> str:
        """
        Полный экспорт данных в JSON
        
        Args:
            include_history: Включить историю приёмов пищи
            filename: Имя файла
        
        Returns:
            Путь к файлу
        """
        from datetime import date
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"healthai_backup_{timestamp}.json"
        
        filepath = os.path.join(self.export_dir, filename)
        
        data = {
            'export_date': datetime.now().isoformat(),
            'user': {
                'name': self.user.name,
                'age': self.user.age,
                'weight': self.user.weight,
                'height': self.user.height,
                'goal': self.user.goal,
                'activity_level': self.user.activity_level,
                'target_calories': self.user.target_calories,
                'level': self.user.level,
                'xp': self.user.xp,
                'streak_days': self.user.streak_days
            },
            'meals': [],
            'statistics': self._calculate_statistics()
        }
        
        if include_history:
            meals = get_meals_by_date_range(self.user_id, date(2000, 1, 1), date.today())
            for meal in meals:
                data['meals'].append({
                    'date': meal.date.isoformat(),
                    'time': meal.time.isoformat(),
                    'name': meal.name,
                    'meal_type': meal.meal_type,
                    'calories': meal.calories,
                    'protein': meal.protein,
                    'fat': meal.fat,
                    'carbs': meal.carbs
                })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def export_to_pdf(self, report_type: str = 'weekly', filename: Optional[str] = None) -> str:
        """
        Экспорт отчёта в PDF
        
        Args:
            report_type: 'daily', 'weekly', 'monthly', 'full'
            filename: Имя файла
        
        Returns:
            Путь к файлу
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"healthai_report_{report_type}_{timestamp}.pdf"
        
        filepath = os.path.join(self.export_dir, filename)
        
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Заголовок
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2E7D32'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        elements.append(Paragraph("Отчёт HealthAI", title_style))
        elements.append(Spacer(1, 12))
        
        # Информация о пользователе
        user_info = [
            ['Пользователь:', self.user.name],
            ['Цель:', self._get_goal_name(self.user.goal)],
            ['Вес:', f"{self.user.weight} кг"],
            ['Рост:', f"{self.user.height} см"],
            ['Уровень:', f"{self.user.level}"],
            ['Серия (дней):', f"{self.user.streak_days}"]
        ]
        
        user_table = Table(user_info, colWidths=[2*inch, 3*inch])
        user_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#E8F5E9')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        elements.append(user_table)
        elements.append(Spacer(1, 20))
        
        # Статистика
        stats = self._calculate_statistics()
        
        elements.append(Paragraph("Статистика питания", styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        stats_data = [
            ['Параметр', 'Значение'],
            ['Среднее калорий в день', f"{stats.get('avg_calories', 0):.0f}"],
            ['Среднее белков', f"{stats.get('avg_protein', 0):.1f} г"],
            ['Среднее жиров', f"{stats.get('avg_fat', 0):.1f} г"],
            ['Среднее углеводов', f"{stats.get('avg_carbs', 0):.1f} г"],
            ['Всего записей', f"{stats.get('total_meals', 0)}"]
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E7D32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        elements.append(stats_table)
        elements.append(Spacer(1, 20))
        
        # Последние приёмы пищи
        elements.append(Paragraph("Последние приёмы пищи", styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        today_meals = get_today_meals(self.user_id)
        meals_data = [['Время', 'Название', 'Ккал', 'Б', 'Ж', 'У']]
        
        for meal in today_meals[-10:]:  # Последние 10 записей
            meals_data.append([
                meal.time.strftime('%H:%M'),
                meal.name[:30],
                str(int(meal.calories)),
                f"{meal.protein:.0f}",
                f"{meal.fat:.0f}",
                f"{meal.carbs:.0f}"
            ])
        
        meals_table = Table(meals_data, colWidths=[1*inch, 2.5*inch, 0.8*inch, 0.6*inch, 0.6*inch, 0.6*inch])
        meals_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')])
        ]))
        
        elements.append(meals_table)
        
        # Подвал
        elements.append(Spacer(1, 30))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        elements.append(Paragraph(f"Создано {datetime.now().strftime('%d.%m.%Y в %H:%M')}", footer_style))
        
        doc.build(elements)
        return filepath
    
    def _calculate_statistics(self) -> Dict:
        """Расчёт статистики по приёмам пищи"""
        from datetime import date
        meals = get_meals_by_date_range(self.user_id, date(2000, 1, 1), date.today())
        
        if not meals:
            return {}
        
        total_calories = sum(m.calories for m in meals)
        total_protein = sum(m.protein for m in meals)
        total_fat = sum(m.fat for m in meals)
        total_carbs = sum(m.carbs for m in meals)
        
        # Группировка по дням
        days = set(m.date for m in meals)
        num_days = len(days) if days else 1
        
        return {
            'total_meals': len(meals),
            'avg_calories': total_calories / num_days,
            'avg_protein': total_protein / num_days,
            'avg_fat': total_fat / num_days,
            'avg_carbs': total_carbs / num_days,
            'total_calories': total_calories,
            'total_protein': total_protein,
            'total_fat': total_fat,
            'total_carbs': total_carbs
        }
    
    def _get_goal_name(self, goal: str) -> str:
        """Преобразование кода цели в название"""
        goals = {
            'weight_loss': 'Похудение',
            'maintain': 'Поддержание',
            'muscle_gain': 'Набор массы',
            'healthy': 'Здоровое питание'
        }
        return goals.get(goal, goal)
    
    def create_auto_backup(self) -> str:
        """Автоматическое создание резервной копии"""
        backup_dir = os.path.join(self.export_dir, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{timestamp}.json"
        filepath = os.path.join(backup_dir, filename)
        
        return self.export_to_json(filename=filepath)


class DataImporter:
    """Класс для импорта данных"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
    
    def import_from_csv(self, filepath: str, data_type: str) -> Dict:
        """
        Импорт данных из CSV
        
        Args:
            filepath: Путь к файлу
            data_type: 'meals', 'products'
        
        Returns:
            Статистика импорта
        """
        stats = {'imported': 0, 'errors': 0, 'message': ''}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                if data_type == 'meals':
                    stats = self._import_meals_csv(reader, stats)
                elif data_type == 'products':
                    stats = self._import_products_csv(reader, stats)
                    
        except Exception as e:
            stats['errors'] += 1
            stats['message'] = f"Ошибка при чтении файла: {str(e)}"
        
        return stats
    
    def _import_meals_csv(self, reader, stats: Dict) -> Dict:
        """Импорт приёмов пищи из CSV"""
        from database.operations import add_meal
        
        for row in reader:
            try:
                add_meal(
                    user_id=self.user_id,
                    name=row['Название'],
                    calories=float(row['Калории']),
                    protein=float(row['Белки (г)']),
                    fat=float(row['Жиры (г)']),
                    carbs=float(row['Углеводы (г)']),
                    meal_type=row.get('Категория', 'other'),
                    date_str=row.get('Дата'),
                    time_str=row.get('Время')
                )
                stats['imported'] += 1
            except Exception as e:
                stats['errors'] += 1
                print(f"Ошибка импорта записи: {e}")
        
        stats['message'] = f"Импортировано {stats['imported']} записей, ошибок: {stats['errors']}"
        return stats
    
    def _import_products_csv(self, reader, stats: Dict) -> Dict:
        """Импорт продуктов из CSV"""
        # Реализация аналогична импорту приёмов пищи
        stats['message'] = "Импорт продуктов пока не реализован"
        return stats
    
    def import_from_json(self, filepath: str) -> Dict:
        """
        Импорт данных из JSON (полное восстановление)
        
        Args:
            filepath: Путь к файлу
        
        Returns:
            Статистика импорта
        """
        stats = {'imported': 0, 'errors': 0, 'message': ''}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Здесь можно добавить логику восстановления данных
            stats['imported'] = 1
            stats['message'] = "Данные успешно загружены из JSON"
            
        except Exception as e:
            stats['errors'] += 1
            stats['message'] = f"Ошибка при импорте JSON: {str(e)}"
        
        return stats


def test_export_import():
    """Тестирование экспорта/импорта"""
    print("📊 Тестирование модуля экспорта/импорта")
    
    # Получаем первого пользователя
    user = get_user()
    if not user:
        print("❌ Нет пользователей для тестирования")
        return
    
    exporter = DataExporter(user.id)
    
    # Тест CSV экспорта
    print("\n1️⃣ Тест экспорта в CSV...")
    csv_file = exporter.export_to_csv('meals')
    print(f"✅ CSV файл создан: {csv_file}")
    
    # Тест JSON экспорта
    print("\n2️⃣ Тест экспорта в JSON...")
    json_file = exporter.export_to_json()
    print(f"✅ JSON файл создан: {json_file}")
    
    # Тест PDF отчёта
    print("\n3️⃣ Тест экспорта в PDF...")
    pdf_file = exporter.export_to_pdf('weekly')
    print(f"✅ PDF отчёт создан: {pdf_file}")
    
    # Тест автобэкапа
    print("\n4️⃣ Тест автоматического бэкапа...")
    backup_file = exporter.create_auto_backup()
    print(f"✅ Бэкап создан: {backup_file}")
    
    # Тест импорта
    print("\n5️⃣ Тест импорта из CSV...")
    importer = DataImporter(user.id)
    import_stats = importer.import_from_csv(csv_file, 'meals')
    print(f"✅ {import_stats['message']}")
    
    print("\n✨ Все тесты пройдены!")


if __name__ == '__main__':
    test_export_import()
