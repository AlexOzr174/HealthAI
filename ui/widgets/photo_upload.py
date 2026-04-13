"""
Виджет загрузки и анализа фото еды
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QFrame, QScrollArea, QGraphicsDropShadowEffect, QTextEdit)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont, QIcon, QColor

from typing import Optional

from core.config import get_food_model_path
from core.food_display_ru import food_name_ru
from core.food_recognition import FoodImageRecognizer
from ai_engine.llm_chat_backend import LLMChatBackend
from ui.file_dialog_utils import get_open_image_path
from ui.styles import CURRENT_THEME

try:
    from utils.chat_text_sanitize import sanitize_assistant_markdown
except ImportError:
    def sanitize_assistant_markdown(t: str) -> str:
        return t


def _recognition_to_ui_results(recognizer: FoodImageRecognizer, image_path: str) -> dict:
    """Преобразует вывод FoodImageRecognizer в формат виджета результатов."""
    raw = recognizer.recognize_food(image_path, top_k=5)
    if raw and raw[0].get('error'):
        msg = raw[0].get('message', raw[0].get('error', 'Неизвестная ошибка'))
        return {
            'products': [{
                'name': msg,
                'confidence': 0.0,
                'calories': 0,
                'macros': {'protein': 0, 'fat': 0, 'carbs': 0},
            }],
            'total_calories': 0,
            'total_macros': {'protein': 0, 'fat': 0, 'carbs': 0},
            'source': 'error',
        }

    products = []
    total_cal = 0
    tot_p = tot_f = tot_c = 0.0
    for r in raw:
        if 'error' in r:
            continue
        fc = str(r.get("food_class", "unknown"))
        imagenet = (r.get("imagenet_label") or "").strip()
        # Для Ollama — сырой английский текст ImageNet; иначе внутренний ключ как текст
        label_en = imagenet if imagenet else fc.replace("_", " ")
        name = food_name_ru(fc)
        conf = float(r.get('confidence', 0))
        tn = r.get('total_nutrition') or {}
        cal = int(tn.get('calories', 0))
        p = float(tn.get('protein', 0))
        f = float(tn.get('fat', 0))
        c = float(tn.get('carbs', 0))
        products.append({
            'name': name,
            'label_en': label_en,
            'food_class': fc,
            'confidence': conf,
            'calories': cal,
            'macros': {'protein': p, 'fat': f, 'carbs': c},
        })
        total_cal += cal
        tot_p += p
        tot_f += f
        tot_c += c

    if not products:
        return {
            'products': [{
                'name': 'Модель не вернула классы с достаточной уверенностью.',
                'confidence': 0.0,
                'calories': 0,
                'macros': {'protein': 0, 'fat': 0, 'carbs': 0},
            }],
            'total_calories': 0,
            'total_macros': {'protein': 0, 'fat': 0, 'carbs': 0},
            'source': 'empty',
        }
    return {
        'products': products,
        'total_calories': total_cal,
        'total_macros': {'protein': tot_p, 'fat': tot_f, 'carbs': tot_c},
        'source': 'model',
    }


class FoodAnalysisResultWidget(QFrame):
    """Виджет с результатами анализа одного продукта"""
    
    def __init__(self, product_name: str, confidence: float, 
                 calories: float, macros: dict, parent=None):
        super().__init__(parent)
        self.init_ui(product_name, confidence, calories, macros)
        
    def init_ui(self, name, confidence, calories, macros):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: %s;
                border-radius: 12px;
                border: 2px solid %s;
                padding: 15px;
            }
        """ % (CURRENT_THEME['card_bg'], '#4CAF50'))
        
        # Тень
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(3)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 90))
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Заголовок с названием и уверенностью
        header_layout = QHBoxLayout()
        
        name_label = QLabel(f"🍽️ {name}")
        name_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: %s;
        """ % CURRENT_THEME['text_primary'])
        header_layout.addWidget(name_label)
        
        confidence_label = QLabel(f"✓ {confidence:.0%}")
        confidence_label.setStyleSheet("""
            font-size: 13px;
            color: #4CAF50;
            font-weight: bold;
            background-color: rgba(76, 175, 80, 0.1);
            padding: 5px 10px;
            border-radius: 15px;
        """)
        header_layout.addWidget(confidence_label)
        
        layout.addLayout(header_layout)
        
        # Калории
        cal_label = QLabel(f"⚡ {calories:.0f} ккал")
        cal_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #FF9800;
        """)
        layout.addWidget(cal_label)
        
        # Макросы
        macros_layout = QHBoxLayout()
        macros_layout.setSpacing(15)
        
        macro_items = [
            ('🥩 Белки', macros.get('protein', 0), '#FF6B6B'),
            ('🧈 Жиры', macros.get('fat', 0), '#4ECDC4'),
            ('🍞 Углеводы', macros.get('carbs', 0), '#FFE66D')
        ]
        
        for label_text, value, color in macro_items:
            macro_frame = QFrame()
            macro_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {CURRENT_THEME['bg']};
                    border-radius: 8px;
                    padding: 8px;
                }}
            """)
            
            macro_layout = QVBoxLayout(macro_frame)
            macro_layout.setContentsMargins(10, 5, 10, 5)
            macro_layout.setSpacing(3)
            macro_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            lbl = QLabel(label_text)
            lbl.setStyleSheet(f"font-size: 11px; color: {color};")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            macro_layout.addWidget(lbl)
            
            val_lbl = QLabel(f"{value:.1f}г")
            val_lbl.setStyleSheet(f"""
                font-size: 14px;
                font-weight: bold;
                color: {CURRENT_THEME['text_primary']};
            """)
            val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            macro_layout.addWidget(val_lbl)
            
            macros_layout.addWidget(macro_frame)
        
        layout.addLayout(macros_layout)


class PhotoUploadWidget(QWidget):
    """Виджет для загрузки и анализа фото еды"""
    
    photo_analyzed = pyqtSignal(dict)  # Сигнал с результатами анализа
    
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window
        self.current_image_path = None
        self._food_model_path = get_food_model_path()
        self._recognizer: Optional[FoodImageRecognizer] = None
        self._llm = LLMChatBackend()
        self.init_ui()

    def _get_recognizer(self) -> FoodImageRecognizer:
        if self._recognizer is None:
            self._recognizer = FoodImageRecognizer(model_path=self._food_model_path)
        return self._recognizer

    def _profile_context(self) -> str:
        if not self.main_window or not getattr(self.main_window, "current_user", None):
            return ""
        u = self.main_window.current_user
        return (
            f"цель={getattr(u, 'goal', '')}; вес={getattr(u, 'weight', '')}; "
            f"рост={getattr(u, 'height', '')}; возраст={getattr(u, 'age', '')}"
        )
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Заголовок
        title = QLabel("📸 Анализ еды по фото")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: %s;
        """ % CURRENT_THEME['text_primary'])
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Область загрузки
        self.upload_area = QFrame()
        self.upload_area.setFixedHeight(300)
        self.upload_area.setStyleSheet("""
            QFrame {
                background-color: %s;
                border: 3px dashed %s;
                border-radius: 20px;
            }
            QFrame:hover {
                border: 3px dashed #4CAF50;
                background-color: %s;
            }
        """ % (
            CURRENT_THEME['card_bg'],
            CURRENT_THEME['border'],
            CURRENT_THEME['bg']
        ))
        
        upload_layout = QVBoxLayout(self.upload_area)
        upload_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upload_layout.setSpacing(15)
        
        # Иконка камеры
        camera_icon = QLabel("📷")
        camera_icon.setStyleSheet("font-size: 64px;")
        camera_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upload_layout.addWidget(camera_icon)
        
        # Текст
        info_label = QLabel("Перетащите фото сюда или нажмите для выбора")
        info_label.setStyleSheet("""
            font-size: 16px;
            color: %s;
        """ % CURRENT_THEME['text_secondary'])
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upload_layout.addWidget(info_label)
        
        # Кнопка загрузки
        upload_button = QPushButton("Выбрать фото")
        upload_button.setCursor(Qt.CursorShape.PointingHandCursor)
        upload_button.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #1a1a1a;
                border: 2px solid #1a1a1a;
                border-radius: 25px;
                padding: 12px 30px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E8F5E9;
            }
        """)
        upload_button.clicked.connect(self.select_photo)
        upload_layout.addWidget(upload_button)
        
        layout.addWidget(self.upload_area)
        
        # Область предпросмотра
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("""
            background-color: %s;
            border-radius: 15px;
        """ % CURRENT_THEME['bg'])
        self.preview_label.hide()
        layout.addWidget(self.preview_label)
        
        # Кнопка анализа
        self.analyze_button = QPushButton("🔍 Проанализировать")
        self.analyze_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.analyze_button.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #1a1a1a;
                border: 2px solid #1a1a1a;
                border-radius: 25px;
                padding: 15px 40px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E3F2FD;
            }
            QPushButton:disabled {
                background-color: #EEEEEE;
                color: #616161;
                border: 2px solid #9E9E9E;
            }
        """)
        self.analyze_button.setEnabled(False)
        self.analyze_button.clicked.connect(self.analyze_photo)
        self.analyze_button.hide()
        layout.addWidget(self.analyze_button)
        
        # Результаты анализа
        self.results_scroll = QScrollArea()
        self.results_scroll.setWidgetResizable(True)
        self.results_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.results_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setSpacing(15)
        
        self.results_scroll.setWidget(self.results_container)
        self.results_scroll.hide()
        layout.addWidget(self.results_scroll, 1)
        
    def select_photo(self):
        """Выбрать фото через диалог"""
        file_path = get_open_image_path(self, "Выберите фото еды")
        
        if file_path:
            self.load_photo(file_path)
            
    def load_photo(self, file_path: str):
        """Загрузить и отобразить фото"""
        self.current_image_path = file_path
        
        # Отобразить превью
        pixmap = QPixmap(file_path)
        scaled_pixmap = pixmap.scaled(
            self.upload_area.width() - 40,
            250,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        self.preview_label.setPixmap(scaled_pixmap)
        self.preview_label.show()
        
        # Показать кнопку анализа
        self.analyze_button.show()
        self.analyze_button.setEnabled(True)
        
        # Скрыть область загрузки
        self.upload_area.hide()
        
    def analyze_photo(self):
        """Анализ фото через загруженную модель TensorFlow/Keras."""
        self.analyze_button.setEnabled(False)
        self.analyze_button.setText("⏳ Анализ...")
        
        if not self.current_image_path:
            self.analyze_button.setEnabled(True)
            self.analyze_button.setText("🔍 Проанализировать")
            return

        results = _recognition_to_ui_results(self._get_recognizer(), self.current_image_path)
        if results.get("source") == "model":
            label_entries: list[tuple[str, str]] = []
            for p in results.get("products", []):
                le = (p.get("label_en") or "").strip()
                fc = (p.get("food_class") or "unknown").strip()
                en = le if le else fc.replace("_", " ")
                label_entries.append((en, fc))
            ru_names = self._llm.translate_food_labels_to_ru(label_entries)
            if ru_names and len(ru_names) == len(results["products"]):
                for p, ru in zip(results["products"], ru_names):
                    p["name"] = ru
        results["narration"] = self._llm.narrate_photo_analysis(results, self._profile_context())
        self.display_results(results)

        self.analyze_button.setEnabled(True)
        self.analyze_button.setText("🔍 Проанализировать снова")

        self.photo_analyzed.emit(results)
        
    def display_results(self, results: dict):
        """Отобразить результаты анализа"""
        # Очистить предыдущие результаты
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Заголовок результатов
        total_label = QLabel(f"📊 Всего: {results['total_calories']} ккал")
        total_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #FF9800;
            padding: 10px;
        """)
        self.results_layout.addWidget(total_label)
        
        # Продукты
        for product in results.get('products', []):
            result_widget = FoodAnalysisResultWidget(
                product['name'],
                product['confidence'],
                product['calories'],
                product['macros']
            )
            self.results_layout.addWidget(result_widget)

        narr = results.get("narration") or ""
        if narr.strip():
            cap = QLabel("💬 Разбор фото (Markdown; Ollama — что на снимке, калории и советы)")
            cap.setWordWrap(True)
            cap.setStyleSheet(
                "font-size: 14px; font-weight: bold; color: %s;" % CURRENT_THEME["text_primary"]
            )
            self.results_layout.addWidget(cap)
            self.narration_edit = QTextEdit()
            self.narration_edit.setReadOnly(True)
            self.narration_edit.setFrameShape(QFrame.Shape.NoFrame)
            self.narration_edit.document().setDocumentMargin(8)
            self.narration_edit.setMarkdown(
                sanitize_assistant_markdown(narr)
            )
            self.narration_edit.setMinimumHeight(220)
            self.narration_edit.setStyleSheet(
                "background-color: %s; border: 1px solid %s; border-radius: 8px; padding: 8px;"
                % (CURRENT_THEME["input_bg"], CURRENT_THEME["border"])
            )
            self.results_layout.addWidget(self.narration_edit)

        self.results_layout.addStretch()
        self.results_scroll.show()
        
    def release_ml_resources(self) -> None:
        """Освободить ResNet/TF до закрытия главного окна."""
        if self._recognizer is not None:
            try:
                self._recognizer.release_native_models()
            except Exception:
                pass
            self._recognizer = None

    def reset(self):
        """Сбросить виджет"""
        self.current_image_path = None
        self.preview_label.hide()
        self.preview_label.clear()
        self.upload_area.show()
        self.analyze_button.hide()
        self.results_scroll.hide()
        
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
