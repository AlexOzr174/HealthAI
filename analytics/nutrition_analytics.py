# Модуль аналитики и визуализации для HealthAI
# Графики, тренды и прогнозы питания

import sys
sys.path.insert(0, '/workspace')

from datetime import datetime, date, timedelta
from database.operations import get_meals_by_date_range, get_user, get_today_meals
from database.models import Meal
import json

try:
    import matplotlib
    matplotlib.use('Agg')  # Для работы без GUI
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Patch
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("⚠️ Matplotlib не установлен. Установите: pip install matplotlib")

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("⚠️ Pandas не установлен. Установите: pip install pandas")


class NutritionAnalytics:
    """Класс для аналитики питания"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.user = get_user(user_id)
        
    def get_daily_stats(self, target_date=None):
        """Получить статистику за день"""
        if target_date is None:
            target_date = date.today()
        
        meals = get_today_meals(self.user_id, target_date)
        
        totals = {
            'calories': sum(m.calories for m in meals),
            'protein': sum(m.protein for m in meals),
            'fat': sum(m.fat for m in meals),
            'carbs': sum(m.carbs for m in meals),
            'fiber': sum(getattr(m, 'fiber', 0) for m in meals),
        }
        
        # Распределение по приёмам пищи
        by_meal_type = {}
        for meal in meals:
            if meal.meal_type not in by_meal_type:
                by_meal_type[meal.meal_type] = {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0}
            by_meal_type[meal.meal_type]['calories'] += meal.calories
            by_meal_type[meal.meal_type]['protein'] += meal.protein
            by_meal_type[meal.meal_type]['fat'] += meal.fat
            by_meal_type[meal.meal_type]['carbs'] += meal.carbs
        
        return {
            'date': target_date,
            'totals': totals,
            'by_meal_type': by_meal_type,
            'meals_count': len(meals),
        }
    
    def get_weekly_stats(self, end_date=None):
        """Получить статистику за неделю"""
        if end_date is None:
            end_date = date.today()
        start_date = end_date - timedelta(days=6)
        
        meals = get_meals_by_date_range(self.user_id, start_date, end_date)
        
        # Группировка по дням
        daily_data = {}
        for meal in meals:
            day = meal.meal_date.date()
            if day not in daily_data:
                daily_data[day] = {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0}
            daily_data[day]['calories'] += meal.calories
            daily_data[day]['protein'] += meal.protein
            daily_data[day]['fat'] += meal.fat
            daily_data[day]['carbs'] += meal.carbs
        
        # Заполняем пропущенные дни
        current = start_date
        while current <= end_date:
            if current not in daily_data:
                daily_data[current] = {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0}
            current += timedelta(days=1)
        
        # Сортировка по датам
        sorted_days = sorted(daily_data.keys())
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'daily_data': {day: daily_data[day] for day in sorted_days},
            'averages': {
                'calories': sum(d['calories'] for d in daily_data.values()) / 7,
                'protein': sum(d['protein'] for d in daily_data.values()) / 7,
                'fat': sum(d['fat'] for d in daily_data.values()) / 7,
                'carbs': sum(d['carbs'] for d in daily_data.values()) / 7,
            },
            'totals': {
                'calories': sum(d['calories'] for d in daily_data.values()),
                'protein': sum(d['protein'] for d in daily_data.values()),
                'fat': sum(d['fat'] for d in daily_data.values()),
                'carbs': sum(d['carbs'] for d in daily_data.values()),
            }
        }
    
    def get_monthly_trend(self, months=3):
        """Получить тренд за несколько месяцев"""
        end_date = date.today()
        start_date = end_date - timedelta(days=months*30)
        
        meals = get_meals_by_date_range(self.user_id, start_date, end_date)
        
        # Группировка по неделям
        weekly_data = {}
        for meal in meals:
            week_start = meal.meal_date.date() - timedelta(days=meal.meal_date.weekday())
            if week_start not in weekly_data:
                weekly_data[week_start] = {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0, 'days': set()}
            weekly_data[week_start]['calories'] += meal.calories
            weekly_data[week_start]['protein'] += meal.protein
            weekly_data[week_start]['fat'] += meal.fat
            weekly_data[week_start]['carbs'] += meal.carbs
            weekly_data[week_start]['days'].add(meal.meal_date.date())
        
        # Рассчитываем среднее за неделю
        for week in weekly_data:
            days_count = len(weekly_data[week]['days'])
            if days_count > 0:
                weekly_data[week]['avg_calories'] = weekly_data[week]['calories'] / days_count
            else:
                weekly_data[week]['avg_calories'] = 0
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'weekly_data': dict(sorted(weekly_data.items())),
        }
    
    def get_macros_distribution(self, days=7):
        """Распределение макронутриентов"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        meals = get_meals_by_date_range(self.user_id, start_date, end_date)
        
        total_protein = sum(m.protein for m in meals) * 4  # калории из белка
        total_fat = sum(m.fat for m in meals) * 9  # калории из жира
        total_carbs = sum(m.carbs for m in meals) * 4  # калории из углеводов
        
        total_calories = total_protein + total_fat + total_carbs
        
        if total_calories == 0:
            return {'protein': 0, 'fat': 0, 'carbs': 0}
        
        return {
            'protein_percent': round(total_protein / total_calories * 100, 1),
            'fat_percent': round(total_fat / total_calories * 100, 1),
            'carbs_percent': round(total_carbs / total_calories * 100, 1),
            'protein_g': round(sum(m.protein for m in meals), 1),
            'fat_g': round(sum(m.fat for m in meals), 1),
            'carbs_g': round(sum(m.carbs for m in meals), 1),
        }
    
    def get_progress_to_goal(self):
        """Прогресс к цели по калориям сегодня"""
        today_stats = self.get_daily_stats()
        target_calories = self.user.target_calories if self.user else 2000
        
        consumed = today_stats['totals']['calories']
        remaining = target_calories - consumed
        percent = round(consumed / target_calories * 100, 1) if target_calories > 0 else 0
        
        return {
            'target': target_calories,
            'consumed': consumed,
            'remaining': remaining,
            'percent': min(percent, 100),
            'macros': {
                'protein': today_stats['totals']['protein'],
                'fat': today_stats['totals']['fat'],
                'carbs': today_stats['totals']['carbs'],
            }
        }
    
    def create_weekly_chart(self, output_path='/workspace/analytics/weekly_calories.png'):
        """Создать график калорий за неделю"""
        if not HAS_MATPLOTLIB or not HAS_PANDAS:
            return None
        
        stats = self.get_weekly_stats()
        
        dates = list(stats['daily_data'].keys())
        calories = [stats['daily_data'][d]['calories'] for d in dates]
        
        # Создаём фигуру
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # График калорий
        bars = ax.bar(range(len(dates)), calories, color='steelblue', alpha=0.8, label='Калории')
        
        # Линия цели
        if self.user:
            target = self.user.target_calories
            ax.axhline(y=target, color='red', linestyle='--', linewidth=2, label=f'Цель: {target} ккал')
        
        # Форматирование
        ax.set_xlabel('День', fontsize=12)
        ax.set_ylabel('Калории', fontsize=12)
        ax.set_title(f'📊 Потребление калорий за неделю\n{self.user.name if self.user else "Пользователь"}', fontsize=14, fontweight='bold')
        ax.set_xticks(range(len(dates)))
        ax.set_xticklabels([d.strftime('%d.%m') for d in dates], rotation=45)
        ax.legend(loc='upper right')
        ax.grid(axis='y', alpha=0.3)
        
        # Добавляем значения на столбцы
        for i, (bar, cal) in enumerate(zip(bars, calories)):
            height = bar.get_height()
            ax.annotate(f'{int(cal)}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def create_macros_pie_chart(self, output_path='/workspace/analytics/macros_pie.png'):
        """Создать круговую диаграмму макронутриентов"""
        if not HAS_MATPLOTLIB:
            return None
        
        macros = self.get_macros_distribution(days=7)
        
        fig, ax = plt.subplots(figsize=(8, 8))
        
        labels = [f'Белки\n{macros["protein_g"]}г ({macros["protein_percent"]}%)',
                 f'Жиры\n{macros["fat_g"]}г ({macros["fat_percent"]}%)',
                 f'Углеводы\n{macros["carbs_g"]}г ({macros["carbs_percent"]}%)']
        sizes = [macros['protein_percent'], macros['fat_percent'], macros['carbs_percent']]
        colors = ['#FF6B6B', '#FFD93D', '#6BCB77']
        
        wedges, texts = ax.pie(sizes, labels=labels, colors=colors, startangle=90, 
                              explode=(0.05, 0.05, 0.05))
        
        ax.set_title('🥗 Распределение макронутриентов (за 7 дней)', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def create_weight_projection_chart(self, current_weight, target_weight, days=30, output_path='/workspace/analytics/weight_projection.png'):
        """Создать график прогноза веса"""
        if not HAS_MATPLOTLIB:
            return None
        
        # Простая линейная проекция
        weight_diff = target_weight - current_weight
        daily_change = weight_diff / days
        
        dates = [date.today() + timedelta(days=i) for i in range(days+1)]
        weights = [current_weight + daily_change * i for i in range(days+1)]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(dates, weights, 'b-', linewidth=2, marker='o', markersize=4, label='Прогноз веса')
        ax.axhline(y=target_weight, color='green', linestyle='--', linewidth=2, label=f'Цель: {target_weight} кг')
        ax.axhline(y=current_weight, color='gray', linestyle=':', linewidth=1, label=f'Старт: {current_weight} кг')
        
        ax.set_xlabel('Дата', fontsize=12)
        ax.set_ylabel('Вес (кг)', fontsize=12)
        ax.set_title('📈 Прогноз изменения веса', fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(alpha=0.3)
        
        # Форматирование дат
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def export_to_json(self, days=30, output_path='/workspace/analytics/nutrition_data.json'):
        """Экспорт данных в JSON"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        meals = get_meals_by_date_range(self.user_id, start_date, end_date)
        
        # Конвертируем weekly stats для JSON
        weekly_stats = self.get_weekly_stats()
        weekly_stats_json = {
            'start_date': str(weekly_stats['start_date']),
            'end_date': str(weekly_stats['end_date']),
            'daily_data': {str(k): v for k, v in weekly_stats['daily_data'].items()},
            'averages': weekly_stats['averages'],
            'totals': weekly_stats['totals'],
        }
        
        data = {
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'export_date': datetime.now().isoformat(),
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
            },
            'meals': [
                {
                    'id': m.id,
                    'name': m.name,
                    'meal_type': m.meal_type,
                    'calories': m.calories,
                    'protein': m.protein,
                    'fat': m.fat,
                    'carbs': m.carbs,
                    'amount': m.amount,
                    'date': m.meal_date.isoformat(),
                }
                for m in meals
            ],
            'summary': weekly_stats_json,
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return output_path


def run_analytics_demo():
    """Демо-запуск аналитики"""
    print("=" * 60)
    print("📊 Аналитика питания HealthAI")
    print("=" * 60)
    
    # Получаем первого пользователя
    user = get_user()
    if not user:
        print("❌ Пользователь не найден. Создайте пользователя сначала.")
        return
    
    analytics = NutritionAnalytics(user.id)
    
    print(f"\n👤 Пользователь: {user.name}")
    print(f"🎯 Цель: {user.target_calories} ккал/день")
    
    # Прогресс за сегодня
    progress = analytics.get_progress_to_goal()
    print(f"\n📈 Прогресс за сегодня:")
    print(f"   Съедено: {progress['consumed']} / {progress['target']} ккал ({progress['percent']}%)")
    print(f"   Осталось: {progress['remaining']} ккал")
    print(f"   БЖУ: {progress['macros']['protein']}г / {progress['macros']['fat']}г / {progress['macros']['carbs']}г")
    
    # Статистика за неделю
    weekly = analytics.get_weekly_stats()
    print(f"\n📅 Средняя за неделю:")
    print(f"   Калории: {int(weekly['averages']['calories'])} ккал")
    print(f"   Белки: {int(weekly['averages']['protein'])}г")
    print(f"   Жиры: {int(weekly['averages']['fat'])}г")
    print(f"   Углеводы: {int(weekly['averages']['carbs'])}г")
    
    # Распределение макронутриентов
    macros = analytics.get_macros_distribution()
    print(f"\n🥗 Распределение БЖУ:")
    print(f"   Белки: {macros['protein_percent']}%")
    print(f"   Жиры: {macros['fat_percent']}%")
    print(f"   Углеводы: {macros['carbs_percent']}%")
    
    # Создание графиков
    if HAS_MATPLOTLIB:
        print("\n📊 Создание графиков...")
        
        chart1 = analytics.create_weekly_chart()
        if chart1:
            print(f"   ✅ График калорий: {chart1}")
        
        chart2 = analytics.create_macros_pie_chart()
        if chart2:
            print(f"   ✅ Диаграмма БЖУ: {chart2}")
    else:
        print("\n⚠️ Matplotlib не установлен, графики не созданы")
    
    # Экспорт в JSON
    json_path = analytics.export_to_json()
    print(f"\n💾 Экспорт данных: {json_path}")
    
    print("\n✅ Готово!")
    print("=" * 60)


if __name__ == '__main__':
    run_analytics_demo()
