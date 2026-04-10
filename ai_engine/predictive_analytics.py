"""
Predictive Analytics Engine - Предиктивная аналитика и прогнозирование
Использует машинное обучение для прогнозирования веса, прогресса и рекомендаций
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')


class PredictiveAnalytics:
    """
    Система предиктивной аналитики для прогнозирования:
    - Динамики веса
    - Прогресса по целям
    - Оптимальной калорийности
    - Времени достижения целей
    """
    
    def __init__(self):
        self.weight_model = None
        self.calorie_model = None
        self.progress_cache = {}
        
    def analyze_weight_trend(self, weight_history: List[Dict]) -> Dict:
        """
        Анализ тренда веса и прогноз
        
        Args:
            weight_history: Список записей [{'date': '2024-01-01', 'weight': 75.5}, ...]
        
        Returns:
            Dict с анализом и прогнозом
        """
        if len(weight_history) < 3:
            return {
                'status': 'insufficient_data',
                'message': 'Недостаточно данных для анализа (минимум 3 записи)',
                'min_records': 3,
                'current_records': len(weight_history)
            }
        
        # Подготовка данных
        dates = []
        weights = []
        for record in weight_history:
            try:
                date = datetime.fromisoformat(record['date']) if isinstance(record['date'], str) else record['date']
                dates.append(date)
                weights.append(record['weight'])
            except (KeyError, ValueError):
                continue
        
        if len(weights) < 3:
            return {
                'status': 'insufficient_data',
                'message': 'Недостаточно валидных записей',
                'current_records': len(weights)
            }
        
        # Преобразование дат в числовой формат (дни от начала)
        start_date = min(dates)
        days = [(d - start_date).days for d in dates]
        X = np.array(days).reshape(-1, 1)
        y = np.array(weights)
        
        # Линейная регрессия для тренда
        lin_model = LinearRegression()
        lin_model.fit(X, y)
        lin_pred = lin_model.predict(X)
        
        # Полиномиальная регрессия (степень 2) для нелинейных трендов
        if len(days) >= 5:
            poly = PolynomialFeatures(degree=2)
            X_poly = poly.fit_transform(X)
            poly_model = Ridge(alpha=1.0)
            poly_model.fit(X_poly, y)
            poly_pred = poly_model.predict(X_poly)
            
            # Выбор лучшей модели
            lin_mse = mean_squared_error(y, lin_pred)
            poly_mse = mean_squared_error(y, poly_pred)
            
            best_model = 'polynomial' if poly_mse < lin_mse else 'linear'
            r2 = r2_score(y, poly_pred) if best_model == 'polynomial' else r2_score(y, lin_pred)
        else:
            best_model = 'linear'
            poly_model = None
            r2 = r2_score(y, lin_pred)
        
        # Текущий тренд
        daily_change = lin_model.coef_[0]
        weekly_change = daily_change * 7
        monthly_change = daily_change * 30
        
        # Классификация тренда
        if abs(daily_change) < 0.05:
            trend_type = 'stable'
            trend_description = 'Вес стабилен'
        elif daily_change < 0:
            trend_type = 'decreasing'
            trend_description = 'Вес снижается'
        else:
            trend_type = 'increasing'
            trend_description = 'Вес растёт'
        
        # Прогноз на 4 недели вперёд
        future_days = list(range(max(days) + 1, max(days) + 29))
        X_future = np.array(future_days).reshape(-1, 1)
        
        if best_model == 'polynomial' and poly_model:
            poly = PolynomialFeatures(degree=2)
            X_future_poly = poly.fit_transform(X_future)
            future_predictions = poly_model.predict(X_future_poly)
        else:
            future_predictions = lin_model.predict(X_future)
        
        # Прогнозируемая дата достижения цели (если цель задана)
        current_weight = weights[-1]
        
        return {
            'status': 'success',
            'current_weight': current_weight,
            'trend': {
                'type': trend_type,
                'description': trend_description,
                'daily_change': round(daily_change, 3),
                'weekly_change': round(weekly_change, 3),
                'monthly_change': round(monthly_change, 3)
            },
            'model_quality': {
                'type': best_model,
                'r2_score': round(r2, 3),
                'confidence': 'high' if r2 > 0.7 else 'medium' if r2 > 0.4 else 'low'
            },
            'forecast': {
                'week_1': round(future_predictions[6], 2),
                'week_2': round(future_predictions[13], 2),
                'week_3': round(future_predictions[20], 2),
                'week_4': round(future_predictions[27], 2)
            },
            'statistics': {
                'min_weight': round(min(weights), 2),
                'max_weight': round(max(weights), 2),
                'avg_weight': round(np.mean(weights), 2),
                'std_weight': round(np.std(weights), 2),
                'records_count': len(weights),
                'date_range': {
                    'start': dates[0].strftime('%Y-%m-%d'),
                    'end': dates[-1].strftime('%Y-%m-%d'),
                    'days': (dates[-1] - dates[0]).days
                }
            }
        }
    
    def predict_goal_achievement(self, current_weight: float, goal_weight: float,
                                  daily_calorie_deficit: int) -> Dict:
        """
        Прогноз достижения цели по весу
        
        Args:
            current_weight: Текущий вес (кг)
            goal_weight: Целевой вес (кг)
            daily_calorie_deficit: Ежедневный дефицит/профицит калорий
        
        Returns:
            Dict с прогнозом достижения цели
        """
        weight_diff = goal_weight - current_weight
        
        # 1 кг жира ≈ 7700 ккал
        kcal_per_kg = 7700
        
        if daily_calorie_deficit == 0:
            return {
                'status': 'no_progress',
                'message': 'При нулевом дефиците/профиците вес не изменится',
                'recommendation': 'Создайте дефицит для похудения или профицит для набора массы'
            }
        
        # Расчёт времени достижения
        if daily_calorie_deficit > 0:  # Дефицит (похудение)
            if weight_diff >= 0:
                return {
                    'status': 'wrong_direction',
                    'message': 'Вы хотите набрать вес, но создаёте дефицит калорий',
                    'recommendation': 'Для набора веса нужен профицит калорий'
                }
            days_needed = abs(weight_diff) * kcal_per_kg / daily_calorie_deficit
            process_type = 'weight_loss'
        else:  # Профицит (набор массы)
            if weight_diff <= 0:
                return {
                    'status': 'wrong_direction',
                    'message': 'Вы хотите похудеть, но создаёте профицит калорий',
                    'recommendation': 'Для похудения нужен дефицит калорий'
                }
            days_needed = abs(weight_diff) * kcal_per_kg / abs(daily_calorie_deficit)
            process_type = 'weight_gain'
        
        days_needed = int(days_needed)
        weeks_needed = days_needed / 7
        months_needed = days_needed / 30
        
        # Проверка на реалистичность
        is_realistic = True
        warnings_list = []
        
        if days_needed < 14:
            is_realistic = False
            warnings_list.append('⚠️ Слишком быстрый темп! Рекомендуется 0.5-1 кг в неделю')
        elif days_needed > 365:
            warnings_list.append('💡 Цель очень масштабная. Рассмотрите промежуточные цели')
        
        if process_type == 'weight_loss' and daily_calorie_deficit > 1000:
            warnings_list.append('⚠️ Дефицит более 1000 ккал может быть небезопасен')
            is_realistic = False
        elif process_type == 'weight_gain' and abs(daily_calorie_deficit) > 500:
            warnings_list.append('⚠️ Профицит более 500 ккал может привести к набору жира')
        
        # Рекомендуемый темп
        if process_type == 'weight_loss':
            recommended_deficit = 500  # 0.5 кг в неделю
            recommended_days = abs(weight_diff) * kcal_per_kg / recommended_deficit
            optimal_weekly_loss = 0.5
        else:
            recommended_deficit = -300  # 0.3 кг в неделю
            recommended_days = abs(weight_diff) * kcal_per_kg / abs(recommended_deficit)
            optimal_weekly_gain = 0.3
        
        target_date = datetime.now() + timedelta(days=days_needed)
        optimal_target_date = datetime.now() + timedelta(days=int(recommended_days))
        
        return {
            'status': 'success',
            'process_type': process_type,
            'weight_to_change': abs(round(weight_diff, 2)),
            'current_calorie_strategy': daily_calorie_deficit,
            'prediction': {
                'days_to_goal': days_needed,
                'weeks_to_goal': round(weeks_needed, 1),
                'months_to_goal': round(months_needed, 1),
                'estimated_completion_date': target_date.strftime('%Y-%m-%d')
            },
            'optimal_strategy': {
                'recommended_daily_deficit': recommended_deficit,
                'days_to_goal_optimal': int(recommended_days),
                'weeks_to_goal_optimal': round(recommended_days / 7, 1),
                'estimated_completion_date_optimal': optimal_target_date.strftime('%Y-%m-%d'),
                'optimal_weekly_change': optimal_weekly_loss if process_type == 'weight_loss' else optimal_weekly_gain
            },
            'is_realistic': is_realistic,
            'warnings': warnings_list,
            'milestones': self._calculate_milestones(current_weight, goal_weight, days_needed)
        }
    
    def _calculate_milestones(self, current: float, goal: float, total_days: int) -> List[Dict]:
        """Расчёт промежуточных этапов"""
        milestones = []
        total_diff = goal - current
        
        percentages = [0.25, 0.5, 0.75]
        labels = ['Первая четверть пути', 'Полпути', 'Финишная прямая']
        
        for pct, label in zip(percentages, labels):
            milestone_weight = current + total_diff * pct
            milestone_days = int(total_days * pct)
            milestone_date = datetime.now() + timedelta(days=milestone_days)
            
            milestones.append({
                'progress': f"{int(pct * 100)}%",
                'label': label,
                'weight': round(milestone_weight, 2),
                'days': milestone_days,
                'date': milestone_date.strftime('%Y-%m-%d')
            })
        
        return milestones
    
    def optimize_calories_for_goal(self, user_profile: Dict, goal: Dict) -> Dict:
        """
        Оптимизация калорийности для достижения цели
        
        Args:
            user_profile: Профиль пользователя (вес, рост, возраст, активность)
            goal: Цель (target_weight, timeframe_weeks)
        
        Returns:
            Оптимальная калорийность и БЖУ
        """
        weight = user_profile.get('weight', 70)
        height = user_profile.get('height', 170)
        age = user_profile.get('age', 30)
        gender = user_profile.get('gender', 'female')
        activity = user_profile.get('activity_level', 1.2)
        
        target_weight = goal.get('target_weight', weight)
        timeframe_weeks = goal.get('timeframe_weeks', 12)
        
        # Расчёт TDEE (формула Миффлина-Сан Жеора)
        if gender == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        
        tdee = bmr * activity
        
        # Необходимое изменение веса
        weight_diff = target_weight - weight
        weeks = max(timeframe_weeks, 1)
        weekly_change = weight_diff / weeks
        
        # Рекомендуемый темп: 0.5-1 кг в неделю для похудения, 0.25-0.5 для набора
        if weekly_change < 0:  # Похудение
            if weekly_change < -1:
                recommended_weekly = -0.75
                warning = 'Ваш темп слишком агрессивный, скорректирован до безопасного'
            else:
                recommended_weekly = weekly_change
            calorie_adjustment = recommended_weekly * 7700 / 7  # ккал в день
            goal_type = 'weight_loss'
        elif weekly_change > 0:  # Набор
            if weekly_change > 0.5:
                recommended_weekly = 0.35
                warning = 'Ваш темп слишком быстрый, скорректирован до оптимального'
            else:
                recommended_weekly = weekly_change
            calorie_adjustment = recommended_weekly * 7700 / 7
            goal_type = 'weight_gain'
        else:
            calorie_adjustment = 0
            warning = None
            goal_type = 'maintain'
        
        optimized_calories = tdee + calorie_adjustment
        
        # Безопасные границы
        min_calories = 1200 if gender == 'female' else 1500
        max_calories = tdee * 1.3
        
        if optimized_calories < min_calories:
            optimized_calories = min_calories
            warning = 'Калорийность увеличена до минимально безопасной'
        elif optimized_calories > max_calories:
            optimized_calories = max_calories
            warning = 'Калорийность уменьшена до разумного максимума'
        
        # Расчёт БЖУ
        protein_per_kg = 1.6 if goal_type == 'weight_loss' else 2.0 if goal_type == 'weight_gain' else 1.4
        protein_g = weight * protein_per_kg
        protein_cal = protein_g * 4
        
        fat_per_kg = 0.8
        fat_g = weight * fat_per_kg
        fat_cal = fat_g * 9
        
        remaining_cal = optimized_calories - protein_cal - fat_cal
        carbs_g = max(remaining_cal / 4, 100)  # Минимум 100г углеводов
        
        return {
            'status': 'success',
            'goal_type': goal_type,
            'tdee': round(tdee),
            'optimized_calories': round(optimized_calories),
            'macros': {
                'protein': {
                    'grams': round(protein_g, 1),
                    'calories': round(protein_cal),
                    'percentage': round(protein_cal / optimized_calories * 100, 1)
                },
                'fat': {
                    'grams': round(fat_g, 1),
                    'calories': round(fat_cal),
                    'percentage': round(fat_cal / optimized_calories * 100, 1)
                },
                'carbs': {
                    'grams': round(carbs_g, 1),
                    'calories': round(carbs_g * 4),
                    'percentage': round(carbs_g * 4 / optimized_calories * 100, 1)
                }
            },
            'weekly_projection': round(recommended_weekly, 2),
            'warning': warning,
            'meal_distribution': {
                'breakfast': round(optimized_calories * 0.25),
                'lunch': round(optimized_calories * 0.35),
                'dinner': round(optimized_calories * 0.30),
                'snacks': round(optimized_calories * 0.10)
            }
        }
    
    def detect_plateau(self, weight_history: List[Dict], days_window: int = 14) -> Dict:
        """
        Обнаружение плато (застоя) в прогрессе
        
        Args:
            weight_history: История взвешиваний
            days_window: Период анализа (дни)
        
        Returns:
            Dict с информацией о плато
        """
        if len(weight_history) < 3:
            return {'plateau_detected': False, 'reason': 'Недостаточно данных'}
        
        # Фильтрация записей за последние days_window дней
        cutoff_date = datetime.now() - timedelta(days=days_window)
        recent_weights = []
        
        for record in weight_history:
            try:
                date = datetime.fromisoformat(record['date']) if isinstance(record['date'], str) else record['date']
                if date >= cutoff_date:
                    recent_weights.append(record['weight'])
            except (KeyError, ValueError):
                continue
        
        if len(recent_weights) < 3:
            return {'plateau_detected': False, 'reason': 'Недостаточно данных за период'}
        
        # Статистический анализ
        weight_std = np.std(recent_weights)
        weight_range = max(recent_weights) - min(recent_weights)
        avg_weight = np.mean(recent_weights)
        
        # Плато: если стандартное отклонение < 0.5 кг и диапазон < 1 кг
        plateau_detected = weight_std < 0.5 and weight_range < 1.0
        
        analysis = {
            'plateau_detected': plateau_detected,
            'analysis_period_days': days_window,
            'measurements_count': len(recent_weights),
            'statistics': {
                'average_weight': round(avg_weight, 2),
                'std_deviation': round(weight_std, 3),
                'weight_range': round(weight_range, 2),
                'min_weight': round(min(recent_weights), 2),
                'max_weight': round(max(recent_weights), 2)
            }
        }
        
        if plateau_detected:
            analysis['recommendations'] = [
                '🔄 Попробуйте изменить тип тренировок',
                '📊 Пересчитайте калорийность (возможно, нужен рефид)',
                '😴 Проверьте качество сна и уровень стресса',
                '💧 Убедитесь в достаточном потреблении воды',
                '⏱️ Рассмотрите интервальное голодание'
            ]
            analysis['possible_causes'] = [
                'Адаптация метаболизма',
                'Недостаточный дефицит/профицит калорий',
                'Задержка жидкости',
                'Недостаток восстановления'
            ]
        else:
            analysis['status'] = 'progress_normal'
            analysis['message'] = 'Прогресс продолжается, плато не обнаружено'
        
        return analysis
    
    def generate_insights(self, analytics_data: Dict) -> List[str]:
        """
        Генерация инсайтов и рекомендаций на основе аналитики
        
        Args:
            analytics_data: Данные из других методов аналитики
        
        Returns:
            Список инсайтов
        """
        insights = []
        
        # Анализ тренда веса
        if 'trend' in analytics_data:
            trend = analytics_data['trend']
            if trend['type'] == 'decreasing':
                if trend['weekly_change'] < -1.5:
                    insights.append('⚠️ Вы теряете вес слишком быстро! Это может привести к потере мышечной массы.')
                elif trend['weekly_change'] > -0.3:
                    insights.append('💡 Темп похудения медленный. Попробуйте немного увеличить дефицит калорий.')
                else:
                    insights.append('✅ Отличный темп похудения! Продолжайте в том же духе.')
            elif trend['type'] == 'increasing':
                if trend['weekly_change'] > 1.0:
                    insights.append('⚠️ Вес растёт слишком быстро. Возможно, вы набираете больше жира, чем мышц.')
                else:
                    insights.append('✅ Хороший темп набора массы.')
        
        # Анализ прогноза
        if 'prediction' in analytics_data:
            pred = analytics_data['prediction']
            if pred['days_to_goal'] > 180:
                insights.append('🎯 До цели ещё далеко. Разбейте путь на промежуточные этапы для мотивации!')
            elif pred['days_to_goal'] < 30:
                insights.append('🏆 Финишная прямая! Осталось совсем немного до цели!')
        
        # Анализ БЖУ
        if 'macros' in analytics_data:
            macros = analytics_data['macros']
            if macros['protein']['percentage'] < 25:
                insights.append('🥩 Увеличьте потребление белка для сохранения мышц.')
            if macros['fat']['percentage'] < 20:
                insights.append('🥑 Не забывайте про полезные жиры для гормонального здоровья.')
        
        if not insights:
            insights.append('✨ Всё идёт по плану! Продолжайте следить за питанием и тренировками.')
        
        return insights


# Экспорт класса
__all__ = ['PredictiveAnalytics']
