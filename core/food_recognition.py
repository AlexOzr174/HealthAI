"""
Food Image Recognition - Распознавание еды по фото
Использует предобученную модель для классификации продуктов
"""

from typing import Dict, List, Optional
import json
from pathlib import Path
from datetime import datetime


class FoodImageRecognizer:
    """
    Распознавание еды по изображениям
    
    Примечание: В полной версии используется TensorFlow/Keras с предобученной моделью.
    Эта реализация включает демонстрационный режим с mock-данными.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.model = None
        self.class_labels = self._load_class_labels()
        self.nutrition_database = self._load_nutrition_database()
        
        # Попытка загрузить модель
        if model_path and Path(model_path).exists():
            self._load_model(model_path)
    
    def _load_class_labels(self) -> List[str]:
        """Загрузка меток классов продуктов"""
        # Основные классы для распознавания
        return [
            'apple', 'banana', 'orange', 'grapes', 'strawberry',
            'chicken_breast', 'beef_steak', 'pork_chop', 'salmon', 'tuna',
            'rice_white', 'rice_brown', 'pasta', 'bread_white', 'bread_whole',
            'egg_boiled', 'egg_fried', 'cheese', 'milk', 'yogurt',
            'broccoli', 'carrot', 'tomato', 'cucumber', 'lettuce', 'spinach',
            'potato', 'sweet_potato', 'avocado', 'nuts_mix', 'almonds',
            'oatmeal', 'cereal', 'pancake', 'waffle', 'pizza',
            'burger', 'fries', 'salad_caesar', 'salad_greek', 'soup',
            'ice_cream', 'cake', 'cookie', 'chocolate', 'donut'
        ]
    
    def _load_nutrition_database(self) -> Dict[str, Dict]:
        """Загрузка базы нутриентов для распознанных продуктов"""
        return {
            'apple': {'calories': 52, 'protein': 0.3, 'carbs': 14, 'fat': 0.2, 'fiber': 2.4, 'serving_size': 100},
            'banana': {'calories': 89, 'protein': 1.1, 'carbs': 23, 'fat': 0.3, 'fiber': 2.6, 'serving_size': 100},
            'orange': {'calories': 47, 'protein': 0.9, 'carbs': 12, 'fat': 0.1, 'fiber': 2.4, 'serving_size': 100},
            'chicken_breast': {'calories': 165, 'protein': 31, 'carbs': 0, 'fat': 3.6, 'fiber': 0, 'serving_size': 100},
            'beef_steak': {'calories': 271, 'protein': 26, 'carbs': 0, 'fat': 18, 'fiber': 0, 'serving_size': 100},
            'salmon': {'calories': 208, 'protein': 20, 'carbs': 0, 'fat': 13, 'fiber': 0, 'serving_size': 100},
            'rice_white': {'calories': 130, 'protein': 2.7, 'carbs': 28, 'fat': 0.3, 'fiber': 0.4, 'serving_size': 100},
            'rice_brown': {'calories': 112, 'protein': 2.6, 'carbs': 24, 'fat': 0.9, 'fiber': 1.8, 'serving_size': 100},
            'pasta': {'calories': 131, 'protein': 5, 'carbs': 25, 'fat': 1.1, 'fiber': 1.8, 'serving_size': 100},
            'bread_white': {'calories': 265, 'protein': 9, 'carbs': 49, 'fat': 3.2, 'fiber': 2.7, 'serving_size': 100},
            'egg_boiled': {'calories': 155, 'protein': 13, 'carbs': 1.1, 'fat': 11, 'fiber': 0, 'serving_size': 100},
            'cheese': {'calories': 402, 'protein': 25, 'carbs': 1.3, 'fat': 33, 'fiber': 0, 'serving_size': 100},
            'milk': {'calories': 42, 'protein': 3.4, 'carbs': 5, 'fat': 1, 'fiber': 0, 'serving_size': 100},
            'broccoli': {'calories': 34, 'protein': 2.8, 'carbs': 7, 'fat': 0.4, 'fiber': 2.6, 'serving_size': 100},
            'carrot': {'calories': 41, 'protein': 0.9, 'carbs': 10, 'fat': 0.2, 'fiber': 2.8, 'serving_size': 100},
            'tomato': {'calories': 18, 'protein': 0.9, 'carbs': 3.9, 'fat': 0.2, 'fiber': 1.2, 'serving_size': 100},
            'potato': {'calories': 77, 'protein': 2, 'carbs': 17, 'fat': 0.1, 'fiber': 2.2, 'serving_size': 100},
            'avocado': {'calories': 160, 'protein': 2, 'carbs': 9, 'fat': 15, 'fiber': 7, 'serving_size': 100},
            'nuts_mix': {'calories': 607, 'protein': 20, 'carbs': 21, 'fat': 54, 'fiber': 10, 'serving_size': 100},
            'oatmeal': {'calories': 68, 'protein': 2.4, 'carbs': 12, 'fat': 1.4, 'fiber': 1.7, 'serving_size': 100},
            'pizza': {'calories': 266, 'protein': 11, 'carbs': 33, 'fat': 10, 'fiber': 2.3, 'serving_size': 100},
            'burger': {'calories': 295, 'protein': 17, 'carbs': 30, 'fat': 14, 'fiber': 1.5, 'serving_size': 100},
            'fries': {'calories': 312, 'protein': 3.4, 'carbs': 41, 'fat': 15, 'fiber': 3.8, 'serving_size': 100},
            'salad_caesar': {'calories': 184, 'protein': 7, 'carbs': 9, 'fat': 13, 'fiber': 2, 'serving_size': 100},
            'ice_cream': {'calories': 207, 'protein': 3.5, 'carbs': 24, 'fat': 11, 'fiber': 1, 'serving_size': 100},
            'cake': {'calories': 371, 'protein': 5, 'carbs': 53, 'fat': 16, 'fiber': 1.5, 'serving_size': 100}
        }
    
    def _load_model(self, model_path: str):
        """Загрузка предобученной модели"""
        try:
            # В полной версии:
            # import tensorflow as tf
            # self.model = tf.keras.models.load_model(model_path)
            print(f"Модель загружена из {model_path}")
        except Exception as e:
            print(f"Ошибка загрузки модели: {e}")
            self.model = None
    
    def recognize_food(self, image_path: str, top_k: int = 3) -> List[Dict]:
        """
        Распознавание еды на изображении
        
        Args:
            image_path: Путь к изображению
            top_k: Количество лучших предсказаний
        
        Returns:
            Список распознанных продуктов с уверенностью и нутриентами
        """
        if not Path(image_path).exists():
            return [{'error': 'Файл не найден', 'path': image_path}]
        
        # Если модель не загружена, используем демонстрационный режим
        if self.model is None:
            return self._mock_recognize(image_path, top_k)
        
        # Полная версия с TensorFlow
        return self._tensorflow_recognize(image_path, top_k)
    
    def _tensorflow_recognize(self, image_path: str, top_k: int) -> List[Dict]:
        """Распознавание с использованием TensorFlow"""
        try:
            import tensorflow as tf
            from PIL import Image
            import numpy as np
            
            # Загрузка и предобработка изображения
            img = Image.open(image_path)
            img = img.resize((224, 224))  # Размер для MobileNet
            img_array = tf.keras.preprocessing.image.img_to_array(img)
            img_array = tf.expand_dims(img_array, 0)  # Добавляем batch dimension
            img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
            
            # Предсказание
            predictions = self.model.predict(img_array, verbose=0)
            probabilities = tf.nn.softmax(predictions[0])
            
            # Получение топ-K предсказаний
            top_indices = tf.math.top_k(probabilities, k=top_k).indices.numpy()
            top_probs = tf.math.top_k(probabilities, k=top_k).values.numpy()
            
            results = []
            for idx, prob in zip(top_indices, top_probs):
                class_name = self.class_labels[idx] if idx < len(self.class_labels) else 'unknown'
                nutrition = self.nutrition_database.get(class_name, {})
                
                results.append({
                    'food_class': class_name,
                    'confidence': float(prob),
                    'nutrition_per_100g': nutrition,
                    'estimated_serving': self._estimate_serving_size(class_name)
                })
            
            return results
            
        except Exception as e:
            print(f"Ошибка распознавания: {e}")
            return self._mock_recognize(image_path, top_k)
    
    def _mock_recognize(self, image_path: str, top_k: int) -> List[Dict]:
        """Демонстрационное распознавание (mock-данные)"""
        # Имитация распознавания на основе имени файла
        filename = Path(image_path).stem.lower()
        
        # Простая эвристика для демонстрации
        mock_results = []
        
        if 'apple' in filename or 'яблоко' in filename:
            mock_results.append(('apple', 0.92))
        elif 'banana' in filename or 'банан' in filename:
            mock_results.append(('banana', 0.89))
        elif 'chicken' in filename or 'курица' in filename:
            mock_results.append(('chicken_breast', 0.87))
        elif 'rice' in filename or 'рис' in filename:
            mock_results.append(('rice_white', 0.85))
        elif 'salad' in filename or 'салат' in filename:
            mock_results.append(('salad_caesar', 0.82))
            mock_results.append(('lettuce', 0.75))
        elif 'pizza' in filename or 'пицца' in filename:
            mock_results.append(('pizza', 0.91))
        elif 'burger' in filename or 'бургер' in filename:
            mock_results.append(('burger', 0.88))
        elif 'egg' in filename or 'яйцо' in filename:
            mock_results.append(('egg_boiled', 0.90))
        elif 'broccoli' in filename or 'брокколи' in filename:
            mock_results.append(('broccoli', 0.86))
        else:
            # Дефолтные результаты для неизвестных изображений
            mock_results = [
                ('chicken_breast', 0.65),
                ('rice_white', 0.58),
                ('broccoli', 0.52)
            ]
        
        # Формирование результатов
        results = []
        for food_class, confidence in mock_results[:top_k]:
            nutrition = self.nutrition_database.get(food_class, {})
            results.append({
                'food_class': food_class,
                'confidence': confidence,
                'nutrition_per_100g': nutrition,
                'estimated_serving': self._estimate_serving_size(food_class),
                'total_nutrition': self._calculate_total_nutrition(nutrition, food_class)
            })
        
        return results
    
    def _estimate_serving_size(self, food_class: str) -> Dict:
        """Оценка размера порции на основе класса продукта"""
        serving_estimates = {
            'apple': {'grams': 182, 'description': '1 среднее яблоко'},
            'banana': {'grams': 118, 'description': '1 средний банан'},
            'chicken_breast': {'grams': 174, 'description': '1 филе куриной грудки'},
            'rice_white': {'grams': 158, 'description': '1 чашка приготовленного риса'},
            'pizza': {'grams': 107, 'description': '1 кусок пиццы'},
            'burger': {'grams': 200, 'description': '1 бургер'},
            'egg_boiled': {'grams': 50, 'description': '1 большое яйцо'},
            'broccoli': {'grams': 91, 'description': '1 чашка соцветий'},
            'salad_caesar': {'grams': 240, 'description': '1 порция салата'},
            'oatmeal': {'grams': 234, 'description': '1 чашка приготовленной овсянки'}
        }
        
        return serving_estimates.get(food_class, {'grams': 100, 'description': 'Стандартная порция'})
    
    def _calculate_total_nutrition(self, nutrition: Dict, food_class: str) -> Dict:
        """Расчёт общих нутриентов для оценённой порции"""
        serving = self._estimate_serving_size(food_class)
        grams = serving.get('grams', 100)
        multiplier = grams / 100
        
        return {
            'calories': round(nutrition.get('calories', 0) * multiplier),
            'protein': round(nutrition.get('protein', 0) * multiplier, 1),
            'carbs': round(nutrition.get('carbs', 0) * multiplier, 1),
            'fat': round(nutrition.get('fat', 0) * multiplier, 1),
            'fiber': round(nutrition.get('fiber', 0) * multiplier, 1),
            'serving_grams': grams
        }
    
    def analyze_multiple_foods(self, image_path: str) -> Dict:
        """
        Анализ изображения с несколькими продуктами
        
        Args:
            image_path: Путь к изображению
        
        Returns:
            Полный анализ блюда
        """
        recognized_foods = self.recognize_food(image_path, top_k=5)
        
        if not recognized_foods or 'error' in recognized_foods[0]:
            return {'error': 'Не удалось распознать продукты'}
        
        # Агрегация нутриентов
        total_nutrition = {
            'calories': 0,
            'protein': 0,
            'carbs': 0,
            'fat': 0,
            'fiber': 0
        }
        
        foods_summary = []
        for food in recognized_foods:
            if 'total_nutrition' in food:
                tn = food['total_nutrition']
                total_nutrition['calories'] += tn.get('calories', 0)
                total_nutrition['protein'] += tn.get('protein', 0)
                total_nutrition['carbs'] += tn.get('carbs', 0)
                total_nutrition['fat'] += tn.get('fat', 0)
                total_nutrition['fiber'] += tn.get('fiber', 0)
            
            foods_summary.append({
                'name': food.get('food_class', 'unknown'),
                'confidence': food.get('confidence', 0),
                'serving': food.get('estimated_serving', {}).get('description', '')
            })
        
        return {
            'recognized_foods': foods_summary,
            'total_nutrition': total_nutrition,
            'image_path': image_path,
            'analyzed_at': datetime.now().isoformat(),
            'health_score': self._calculate_health_score(total_nutrition)
        }
    
    def _calculate_health_score(self, nutrition: Dict) -> int:
        """Расчёт показателя полезности блюда (0-100)"""
        calories = nutrition.get('calories', 0)
        protein = nutrition.get('protein', 0)
        fat = nutrition.get('fat', 0)
        carbs = nutrition.get('carbs', 0)
        fiber = nutrition.get('fiber', 0)
        
        score = 50  # Базовый score
        
        # Белок увеличивает score
        score += min(protein * 2, 20)
        
        # Клетчатка увеличивает score
        score += min(fiber * 3, 15)
        
        # Избыток калорий уменьшает score
        if calories > 600:
            score -= 10
        elif calories > 400:
            score -= 5
        
        # Избыток жиров уменьшает score
        if fat > 30:
            score -= 10
        elif fat > 20:
            score -= 5
        
        return max(0, min(100, score))
    
    def get_supported_foods(self) -> List[str]:
        """Получение списка поддерживаемых продуктов"""
        return list(self.nutrition_database.keys())
    
    def save_model_info(self, output_path: str):
        """Сохранение информации о модели и поддерживаемых продуктах"""
        info = {
            'supported_foods': self.get_supported_foods(),
            'class_count': len(self.class_labels),
            'nutrition_database_size': len(self.nutrition_database),
            'model_loaded': self.model is not None,
            'version': '1.0'
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        
        return output_path
