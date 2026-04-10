"""
Виджет загрузки и анализа фото еды
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QFileDialog, QFrame, QScrollArea, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont, QIcon
from ui.styles import CURRENT_THEME


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
        shadow.setColor(Qt.GlobalColor.black)
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
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_image_path = None
        self.init_ui()
        
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
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 25px;
                padding: 12px 30px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
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
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 25px;
                padding: 15px 40px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: %s;
                color: %s;
            }
        """ % (CURRENT_THEME['border'], CURRENT_THEME['text_secondary']))
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
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите фото еды",
            "",
            "Images (*.png *.xpm *.jpg *.jpeg *.bmp)"
        )
        
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
        """Анализировать фото (симуляция)"""
        self.analyze_button.setEnabled(False)
        self.analyze_button.setText("⏳ Анализ...")
        
        # TODO: Интеграция с реальной ML моделью
        # Симуляция результатов
        simulated_results = {
            'products': [
                {
                    'name': 'Греческий салат',
                    'confidence': 0.92,
                    'calories': 320,
                    'macros': {'protein': 12.5, 'fat': 24.0, 'carbs': 8.5}
                },
                {
                    'name': 'Куриная грудка',
                    'confidence': 0.87,
                    'calories': 165,
                    'macros': {'protein': 31.0, 'fat': 3.6, 'carbs': 0}
                }
            ],
            'total_calories': 485,
            'total_macros': {'protein': 43.5, 'fat': 27.6, 'carbs': 8.5}
        }
        
        # Отобразить результаты
        self.display_results(simulated_results)
        
        self.analyze_button.setEnabled(True)
        self.analyze_button.setText("🔍 Проанализировать снова")
        
        # Отправить сигнал
        self.photo_analyzed.emit(simulated_results)
        
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
        
        self.results_layout.addStretch()
        self.results_scroll.show()
        
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
