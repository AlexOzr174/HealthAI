# Модуль экспорта/импорта данных для HealthAI
# Поддержка CSV, JSON, PDF отчётов

import sys
sys.path.insert(0, '/workspace')

from datetime import datetime, date, timedelta
from database.operations import get_meals_by_date_range, get_user, get_all_products, get_all_recipes
import json
import csv
import io

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    print("⚠️ ReportLab не установлен. Установите: pip install reportlab")


class DataExporter:
    """Класс для экспорта данных в различные форматы"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.user = get_user(user_id)
        
    def export_to_csv(self, days=30, output_path='/workspace/export_import/meals_export.csv'):
        """Экспорт приёмов пищи в CSV"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        meals = get_meals_by_date_range(self.user_id, start_date, end_date)
        
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            
            # Заголовок
            writer.writerow([
                'Дата', 'Время', 'Тип приёма пищи', 'Название',
                'Вес (г)', 'Калории', 'Белки (г)', 'Жиры (г)', 'Углеводы (г)'
            ])
            
            # Данные
            for meal in meals:
                writer.writerow([
                    meal.meal_date.strftime('%Y-%m-%d'),
                    meal.meal_time.strftime('%H:%M'),
                    meal.meal_type,
                    meal.name,
                    meal.amount,
                    meal.calories,
                    meal.protein,
                    meal.fat,
                    meal.carbs,
                ])
        
        return output_path
    
    def export_to_json_full(self, output_path='/workspace/export_import/full_export.json'):
        """Полный экспорт всех данных пользователя в JSON"""
        end_date = date.today()
        start_date = date(2020, 1, 1)  # Все данные
        
        meals = get_meals_by_date_range(self.user_id, start_date, end_date)
        
        data = {
            'export_info': {
                'date': datetime.now().isoformat(),
                'version': '1.0',
                'app': 'HealthAI',
            },
            'user': {
                'id': self.user.id,
                'name': self.user.name,
                'gender': self.user.gender,
                'age': self.user.age,
                'height': self.user.height,
                'weight': self.user.weight,
                'activity_level': self.user.activity_level,
                'goal': self.user.goal,
                'target_calories': self.user.target_calories,
                'xp': self.user.xp,
                'level': self.user.level,
            } if self.user else None,
            'meals': [
                {
                    'id': m.id,
                    'name': m.name,
                    'meal_type': m.meal_type,
                    'amount': m.amount,
                    'calories': m.calories,
                    'protein': m.protein,
                    'fat': m.fat,
                    'carbs': m.carbs,
                    'meal_date': m.meal_date.isoformat(),
                    'meal_time': m.meal_time.strftime('%H:%M'),
                }
                for m in meals
            ],
            'statistics': {
                'total_meals': len(meals),
                'total_calories': sum(m.calories for m in meals),
                'avg_daily_calories': sum(m.calories for m in meals) / max(1, (end_date - start_date).days),
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return output_path
    
    def export_products_to_csv(self, output_path='/workspace/export_import/products_export.csv'):
        """Экспорт всех продуктов в CSV"""
        products = get_all_products()
        
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            
            writer.writerow([
                'ID', 'Название', 'Категория', 'Калории', 'Белки', 'Жиры',
                'Углеводы', 'Клетчатка', 'Сахар', 'ГИ', 'Здоровый'
            ])
            
            for product in products:
                writer.writerow([
                    product.id,
                    product.name,
                    product.category,
                    product.calories,
                    product.protein,
                    product.fat,
                    product.carbs,
                    product.fiber,
                    product.sugar,
                    product.glycemic_index,
                    'Да' if product.is_healthy else 'Нет',
                ])
        
        return output_path
    
    def export_recipes_to_csv(self, output_path='/workspace/export_import/recipes_export.csv'):
        """Экспорт всех рецептов в CSV"""
        recipes = get_all_recipes()
        
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            
            writer.writerow([
                'ID', 'Название', 'Категория', 'Кухня', 'Время (мин)',
                'Порции', 'Калории', 'Белки', 'Жиры', 'Углеводы', 'Рейтинг'
            ])
            
            for recipe in recipes:
                writer.writerow([
                    recipe.id,
                    recipe.name,
                    recipe.category,
                    recipe.cuisine,
                    recipe.prep_time,
                    recipe.servings,
                    recipe.calories,
                    recipe.protein,
                    recipe.fat,
                    recipe.carbs,
                    recipe.rating,
                ])
        
        return output_path
    
    def create_pdf_report(self, days=7, output_path='/workspace/export_import/nutrition_report.pdf'):
        """Создание PDF отчёта о питании"""
        if not HAS_REPORTLAB:
            print("❌ ReportLab не установлен")
            return None
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        meals = get_meals_by_date_range(self.user_id, start_date, end_date)
        
        # Группировка по дням
        daily_data = {}
        for meal in meals:
            day = meal.meal_date.date()
            if day not in daily_data:
                daily_data[day] = {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0, 'meals': []}
            daily_data[day]['calories'] += meal.calories
            daily_data[day]['protein'] += meal.protein
            daily_data[day]['fat'] += meal.fat
            daily_data[day]['carbs'] += meal.carbs
            daily_data[day]['meals'].append(meal)
        
        # Создание PDF
        doc = SimpleDocTemplate(
            output_path,
            pagesize=landscape(A4),
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm,
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Заголовок
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=20,
        )
        
        elements.append(Paragraph(f"📊 Отчёт о питании", title_style))
        elements.append(Paragraph(f"Пользователь: {self.user.name if self.user else 'Неизвестно'}", styles['Normal']))
        elements.append(Paragraph(f"Период: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}", styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Сводная таблица за период
        total_calories = sum(d['calories'] for d in daily_data.values())
        total_protein = sum(d['protein'] for d in daily_data.values())
        total_fat = sum(d['fat'] for d in daily_data.values())
        total_carbs = sum(d['carbs'] for d in daily_data.values())
        avg_calories = total_calories / max(1, len(daily_data))
        
        summary_data = [
            ['Показатель', 'Значение'],
            ['Всего калорий', f'{int(total_calories)} ккал'],
            ['Среднее в день', f'{int(avg_calories)} ккал'],
            ['Всего белков', f'{int(total_protein)} г'],
            ['Всего жиров', f'{int(total_fat)} г'],
            ['Всего углеводов', f'{int(total_carbs)} г'],
            ['Дней записей', str(len(daily_data))],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Таблица по дням
        elements.append(Paragraph("📅 Детализация по дням", styles['Heading2']))
        elements.append(Spacer(1, 0.2*inch))
        
        day_data = [['Дата', 'Калории', 'Белки (г)', 'Жиры (г)', 'Углеводы (г)', 'Приёмов пищи']]
        for day in sorted(daily_data.keys()):
            data = daily_data[day]
            day_data.append([
                day.strftime('%d.%m.%Y'),
                int(data['calories']),
                int(data['protein']),
                int(data['fat']),
                int(data['carbs']),
                len(data['meals']),
            ])
        
        # Добавляем итоговую строку
        day_data.append([
            'ИТОГО',
            int(total_calories),
            int(total_protein),
            int(total_fat),
            int(total_carbs),
            len(meals),
        ])
        
        days_table = Table(day_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1*inch])
        days_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(days_table)
        
        # Построение документа
        doc.build(elements)
        
        return output_path


class DataImporter:
    """Класс для импорта данных"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        
    def import_from_json(self, json_path):
        """Импорт данных из JSON (для будущего расширения)"""
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Здесь будет логика импорта
        # Пока просто возвращаем структуру
        return {
            'status': 'success',
            'message': 'Функция импорта в разработке',
            'data_preview': data.get('user', {}) if data else {},
        }


def run_export_demo():
    """Демо-запуск экспорта"""
    print("=" * 60)
    print("💾 Экспорт данных HealthAI")
    print("=" * 60)
    
    user = get_user()
    if not user:
        print("❌ Пользователь не найден")
        return
    
    exporter = DataExporter(user.id)
    
    print(f"\n👤 Пользователь: {user.name}")
    
    # Экспорт в CSV
    print("\n📄 Экспорт в CSV...")
    csv_path = exporter.export_to_csv(days=30)
    print(f"   ✅ Приёмы пищи: {csv_path}")
    
    products_csv = exporter.export_products_to_csv()
    print(f"   ✅ Продукты: {products_csv}")
    
    recipes_csv = exporter.export_recipes_to_csv()
    print(f"   ✅ Рецепты: {recipes_csv}")
    
    # Экспорт в JSON
    print("\n📋 Экспорт в JSON...")
    json_path = exporter.export_to_json_full()
    print(f"   ✅ Полный экспорт: {json_path}")
    
    # PDF отчёт
    print("\n📑 Создание PDF отчёта...")
    if HAS_REPORTLAB:
        pdf_path = exporter.create_pdf_report(days=7)
        if pdf_path:
            print(f"   ✅ PDF отчёт: {pdf_path}")
    else:
        print("   ⚠️ ReportLab не установлен")
    
    print("\n✅ Готово!")
    print("=" * 60)


if __name__ == '__main__':
    run_export_demo()
