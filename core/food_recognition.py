# core/food_recognition.py
"""
Распознавание еды: PyTorch ResNet50 (models/vision/resnet50.pth + imagenet_classes.txt)
или Keras .h5 с числом классов, совпадающим с class_labels.
"""

from typing import Dict, List, Optional, Tuple
import json
from pathlib import Path
from datetime import datetime


# Соответствие подстрок подписи ImageNet → ключ nutrition_database
IMAGENET_TO_FOOD: List[Tuple[str, str]] = [
    ("pizza", "pizza"),
    ("cheeseburger", "burger"),
    ("hotdog", "burger"),
    ("broccoli", "broccoli"),
    ("ice cream", "ice_cream"),
    ("soup bowl", "soup"),
    ("meat loaf", "beef_steak"),
    ("potpie", "pizza"),
    ("pineapple", "orange"),
    ("custard apple", "apple"),
    ("Granny Smith", "apple"),
    ("orange", "orange"),
    ("banana", "banana"),
    ("lemon", "orange"),
    ("fig", "orange"),
    ("pomegranate", "orange"),
    ("strawberry", "grapes"),
    ("cheese", "cheese"),
    ("butternut squash", "carrot"),
    ("cucumber", "cucumber"),
    ("corn", "rice_white"),
    ("mashed potato", "potato"),
    ("bakery", "bread_white"),
    ("bagel", "bread_white"),
    ("pretzel", "bread_white"),
    ("spaghetti squash", "pasta"),
    ("acorn squash", "carrot"),
    ("head cabbage", "broccoli"),
    ("cauliflower", "broccoli"),
    ("bell pepper", "tomato"),
    ("mushroom", "broccoli"),
    ("Granny Smith", "apple"),
    ("cardoon", "broccoli"),
    ("French loaf", "bread_white"),
    ("chocolate sauce", "chocolate"),
    ("dough", "bread_white"),
    ("meatball", "beef_steak"),
    ("plate", "salad_caesar"),
    ("guacamole", "avocado"),
    ("espresso", "milk"),
    ("cup", "milk"),
    ("eggs Benedict", "egg_fried"),
    ("omelet", "egg_fried"),
    ("carbonara", "pasta"),
    ("gnocchi", "pasta"),
    ("consomme", "soup"),
    ("hot pot", "soup"),
    ("trifle", "cake"),
    ("ice lolly", "ice_cream"),
    ("ice cream", "ice_cream"),
    ("pretzel", "bread_white"),
    ("red wine", "grapes"),
    ("beer bottle", "bread_white"),
    ("goblet", "milk"),
]


class FoodImageRecognizer:
    """Классификация: ResNet50+ImageNet или пользовательская Keras-модель."""

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.backend: Optional[str] = None  # 'torch' | 'keras'
        self._torch_model = None
        self._keras_model = None
        self.imagenet_labels: List[str] = []
        self.class_labels = self._load_class_labels()
        self.nutrition_database = self._load_nutrition_database()

        root = Path(__file__).resolve().parent.parent
        default_cls = root / "models" / "vision" / "imagenet_classes.txt"
        if default_cls.exists():
            self.imagenet_labels = default_cls.read_text(encoding="utf-8").strip().splitlines()

        if model_path and Path(model_path).exists():
            self._load_model(model_path)

    def _load_class_labels(self) -> List[str]:
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
        return {
            'apple': {'calories': 52, 'protein': 0.3, 'carbs': 14, 'fat': 0.2, 'fiber': 2.4, 'serving_size': 100},
            'banana': {'calories': 89, 'protein': 1.1, 'carbs': 23, 'fat': 0.3, 'fiber': 2.6, 'serving_size': 100},
            'orange': {'calories': 47, 'protein': 0.9, 'carbs': 12, 'fat': 0.1, 'fiber': 2.4, 'serving_size': 100},
            'grapes': {'calories': 69, 'protein': 0.7, 'carbs': 18, 'fat': 0.2, 'fiber': 0.9, 'serving_size': 100},
            'chicken_breast': {'calories': 165, 'protein': 31, 'carbs': 0, 'fat': 3.6, 'fiber': 0, 'serving_size': 100},
            'beef_steak': {'calories': 271, 'protein': 26, 'carbs': 0, 'fat': 18, 'fiber': 0, 'serving_size': 100},
            'salmon': {'calories': 208, 'protein': 20, 'carbs': 0, 'fat': 13, 'fiber': 0, 'serving_size': 100},
            'rice_white': {'calories': 130, 'protein': 2.7, 'carbs': 28, 'fat': 0.3, 'fiber': 0.4, 'serving_size': 100},
            'rice_brown': {'calories': 112, 'protein': 2.6, 'carbs': 24, 'fat': 0.9, 'fiber': 1.8, 'serving_size': 100},
            'pasta': {'calories': 131, 'protein': 5, 'carbs': 25, 'fat': 1.1, 'fiber': 1.8, 'serving_size': 100},
            'bread_white': {'calories': 265, 'protein': 9, 'carbs': 49, 'fat': 3.2, 'fiber': 2.7, 'serving_size': 100},
            'egg_boiled': {'calories': 155, 'protein': 13, 'carbs': 1.1, 'fat': 11, 'fiber': 0, 'serving_size': 100},
            'egg_fried': {'calories': 196, 'protein': 14, 'carbs': 1, 'fat': 15, 'fiber': 0, 'serving_size': 100},
            'cheese': {'calories': 402, 'protein': 25, 'carbs': 1.3, 'fat': 33, 'fiber': 0, 'serving_size': 100},
            'milk': {'calories': 42, 'protein': 3.4, 'carbs': 5, 'fat': 1, 'fiber': 0, 'serving_size': 100},
            'broccoli': {'calories': 34, 'protein': 2.8, 'carbs': 7, 'fat': 0.4, 'fiber': 2.6, 'serving_size': 100},
            'carrot': {'calories': 41, 'protein': 0.9, 'carbs': 10, 'fat': 0.2, 'fiber': 2.8, 'serving_size': 100},
            'tomato': {'calories': 18, 'protein': 0.9, 'carbs': 3.9, 'fat': 0.2, 'fiber': 1.2, 'serving_size': 100},
            'cucumber': {'calories': 15, 'protein': 0.7, 'carbs': 3.6, 'fat': 0.1, 'fiber': 0.5, 'serving_size': 100},
            'potato': {'calories': 77, 'protein': 2, 'carbs': 17, 'fat': 0.1, 'fiber': 2.2, 'serving_size': 100},
            'avocado': {'calories': 160, 'protein': 2, 'carbs': 9, 'fat': 15, 'fiber': 7, 'serving_size': 100},
            'nuts_mix': {'calories': 607, 'protein': 20, 'carbs': 21, 'fat': 54, 'fiber': 10, 'serving_size': 100},
            'oatmeal': {'calories': 68, 'protein': 2.4, 'carbs': 12, 'fat': 1.4, 'fiber': 1.7, 'serving_size': 100},
            'pizza': {'calories': 266, 'protein': 11, 'carbs': 33, 'fat': 10, 'fiber': 2.3, 'serving_size': 100},
            'burger': {'calories': 295, 'protein': 17, 'carbs': 30, 'fat': 14, 'fiber': 1.5, 'serving_size': 100},
            'fries': {'calories': 312, 'protein': 3.4, 'carbs': 41, 'fat': 15, 'fiber': 3.8, 'serving_size': 100},
            'salad_caesar': {'calories': 184, 'protein': 7, 'carbs': 9, 'fat': 13, 'fiber': 2, 'serving_size': 100},
            'salad_greek': {'calories': 120, 'protein': 6, 'carbs': 8, 'fat': 8, 'fiber': 3, 'serving_size': 100},
            'soup': {'calories': 50, 'protein': 3, 'carbs': 6, 'fat': 1.5, 'fiber': 1, 'serving_size': 100},
            'ice_cream': {'calories': 207, 'protein': 3.5, 'carbs': 24, 'fat': 11, 'fiber': 1, 'serving_size': 100},
            'cake': {'calories': 371, 'protein': 5, 'carbs': 53, 'fat': 16, 'fiber': 1.5, 'serving_size': 100},
            'cookie': {'calories': 502, 'protein': 5, 'carbs': 64, 'fat': 25, 'fiber': 2, 'serving_size': 100},
            'chocolate': {'calories': 546, 'protein': 5, 'carbs': 61, 'fat': 31, 'fiber': 7, 'serving_size': 100},
            'donut': {'calories': 452, 'protein': 5, 'carbs': 51, 'fat': 25, 'fiber': 2, 'serving_size': 100},
        }

    def _load_model(self, model_path: str) -> None:
        p = Path(model_path)
        try:
            if p.suffix.lower() == ".pth":
                import torch
                import torchvision.models as tvm

                model = tvm.resnet50(weights=None)
                try:
                    state = torch.load(p, map_location="cpu", weights_only=True)
                except TypeError:
                    state = torch.load(p, map_location="cpu")
                model.load_state_dict(state)
                model.eval()
                self._torch_model = model
                self.backend = "torch"
                return
        except Exception as e:
            print(f"PyTorch модель: {e}")

        try:
            import importlib.util
            if importlib.util.find_spec("tensorflow") is None:
                return
            import tensorflow as tf
            self._keras_model = tf.keras.models.load_model(str(p))
            self.backend = "keras"
        except Exception as e:
            print(f"Keras модель: {e}")

    @staticmethod
    def _imagenet_line_to_food(line: str) -> str:
        low = line.lower()
        for kw, key in IMAGENET_TO_FOOD:
            if kw.lower() in low:
                return key
        return "salad_caesar"

    def recognize_food(self, image_path: str, top_k: int = 3) -> List[Dict]:
        if not Path(image_path).exists():
            return [{'error': 'file_not_found', 'message': 'Файл не найден', 'path': image_path}]

        if self.backend == "torch" and self._torch_model is not None:
            return self._pytorch_recognize(image_path, top_k)
        if self.backend == "keras" and self._keras_model is not None:
            return self._keras_recognize(image_path, top_k)

        return [{
            'error': 'model_required',
            'message': 'Нет модели в models/vision (resnet50.pth) или HEALTHAI_FOOD_MODEL_PATH.',
        }]

    def _pytorch_recognize(self, image_path: str, top_k: int) -> List[Dict]:
        try:
            import torch
            import torch.nn.functional as F
            from PIL import Image
            from torchvision import transforms

            preprocess = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])
            img = Image.open(image_path).convert("RGB")
            batch = preprocess(img).unsqueeze(0)
            with torch.no_grad():
                logits = self._torch_model(batch)
                probs = F.softmax(logits[0], dim=0)
            k = min(top_k, probs.numel())
            top = torch.topk(probs, k=k)

            results = []
            for i in range(k):
                idx = int(top.indices[i].item())
                prob = float(top.values[i].item())
                line = self.imagenet_labels[idx] if idx < len(self.imagenet_labels) else f"class_{idx}"
                food_class = self._imagenet_line_to_food(line)
                nutrition = self.nutrition_database.get(food_class, self.nutrition_database['salad_caesar'])
                results.append({
                    'food_class': food_class,
                    'imagenet_label': line,
                    'confidence': prob,
                    'nutrition_per_100g': nutrition,
                    'estimated_serving': self._estimate_serving_size(food_class),
                    'total_nutrition': self._calculate_total_nutrition(nutrition, food_class),
                })
            return results
        except Exception as e:
            return [{'error': 'inference_failed', 'message': str(e)}]

    def _keras_recognize(self, image_path: str, top_k: int) -> List[Dict]:
        try:
            import tensorflow as tf
            from PIL import Image

            img = Image.open(image_path).convert("RGB")
            img = img.resize((224, 224))
            img_array = tf.keras.preprocessing.image.img_to_array(img)
            img_array = tf.expand_dims(img_array, 0)
            img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
            predictions = self._keras_model.predict(img_array, verbose=0)
            probabilities = tf.nn.softmax(predictions[0])
            k = min(top_k, int(probabilities.shape[0]))
            top_indices = tf.math.top_k(probabilities, k=k).indices.numpy()
            top_probs = tf.math.top_k(probabilities, k=k).values.numpy()
            results = []
            for idx, prob in zip(top_indices, top_probs):
                idx = int(idx)
                class_name = self.class_labels[idx] if idx < len(self.class_labels) else 'unknown'
                nutrition = self.nutrition_database.get(class_name, {})
                results.append({
                    'food_class': class_name,
                    'confidence': float(prob),
                    'nutrition_per_100g': nutrition,
                    'estimated_serving': self._estimate_serving_size(class_name),
                    'total_nutrition': self._calculate_total_nutrition(nutrition, class_name),
                })
            return results
        except Exception as e:
            return [{'error': 'inference_failed', 'message': str(e)}]

    def _estimate_serving_size(self, food_class: str) -> Dict:
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
        serving = self._estimate_serving_size(food_class)
        grams = serving.get('grams', 100)
        mult = grams / 100
        return {
            'calories': round(nutrition.get('calories', 0) * mult),
            'protein': round(nutrition.get('protein', 0) * mult, 1),
            'carbs': round(nutrition.get('carbs', 0) * mult, 1),
            'fat': round(nutrition.get('fat', 0) * mult, 1),
            'fiber': round(nutrition.get('fiber', 0) * mult, 1),
            'serving_grams': grams
        }

    def analyze_multiple_foods(self, image_path: str) -> Dict:
        recognized_foods = self.recognize_food(image_path, top_k=5)
        if not recognized_foods or 'error' in recognized_foods[0]:
            return {'error': 'Не удалось распознать продукты'}

        total_nutrition = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'fiber': 0}
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
        calories = nutrition.get('calories', 0)
        protein = nutrition.get('protein', 0)
        fat = nutrition.get('fat', 0)
        carbs = nutrition.get('carbs', 0)
        fiber = nutrition.get('fiber', 0)
        score = 50
        score += min(protein * 2, 20)
        score += min(fiber * 3, 15)
        if calories > 600:
            score -= 10
        elif calories > 400:
            score -= 5
        if fat > 30:
            score -= 10
        elif fat > 20:
            score -= 5
        return max(0, min(100, score))

    def release_native_models(self) -> None:
        """Сброс ссылок на тяжёлые нативные модели до выхода из Qt (macOS: меньше segfault при teardown)."""
        if self._torch_model is not None:
            self._torch_model = None
            try:
                import gc

                gc.collect()
            except Exception:
                pass
            try:
                import torch

                if torch.cuda.is_available():
                    torch.cuda.synchronize()
                    torch.cuda.empty_cache()
            except Exception:
                pass
        if self._keras_model is not None:
            self._keras_model = None
            try:
                import gc

                gc.collect()
            except Exception:
                pass
            try:
                import tensorflow as tf

                tf.keras.backend.clear_session()
            except Exception:
                pass
        self.backend = None

    def get_supported_foods(self) -> List[str]:
        return list(self.nutrition_database.keys())

    def save_model_info(self, output_path: str) -> str:
        info = {
            'supported_foods': self.get_supported_foods(),
            'class_count': len(self.class_labels),
            'backend': self.backend,
            'version': '2.0'
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        return output_path
