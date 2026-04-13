"""
Диалог загрузки и анализа фотографий еды
"""
from __future__ import annotations

import logging

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QTextEdit, QWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QCloseEvent, QPixmap, QIcon

from ui.dialog_chrome import STANDARD_LIGHT_FORM_DIALOG_QSS, apply_light_dialog_chrome
from ui.file_dialog_utils import get_open_image_path
from ui.components.press_feedback import attach_press_flash

_log = logging.getLogger(__name__)


class ImageAnalyzerThread(QThread):
    """Поток для анализа изображения"""
    analysis_complete = pyqtSignal(dict)
    analysis_error = pyqtSignal(str)
    
    def __init__(self, image_path: str):
        super().__init__()
        self.image_path = image_path
    
    def run(self):
        try:
            # Имитация анализа (в реальности здесь будет ML модель или API)
            result = self._analyze_image_mock(self.image_path)
            self.analysis_complete.emit(result)
        except Exception as e:
            self.analysis_error.emit(str(e))
    
    def _analyze_image_mock(self, image_path: str) -> dict:
        """Имитация анализа изображения"""
        # В реальной реализации здесь будет вызов ML модели
        return {
            'foods': [
                {
                    'name': 'Цезарь салат',
                    'confidence': 0.92,
                    'calories': 350,
                    'protein': 25,
                    'carbs': 12,
                    'fat': 22,
                    'portion': '250г'
                },
                {
                    'name': 'Томаты черри',
                    'confidence': 0.87,
                    'calories': 45,
                    'protein': 2,
                    'carbs': 8,
                    'fat': 0.5,
                    'portion': '100г'
                }
            ],
            'total': {
                'calories': 395,
                'protein': 27,
                'carbs': 20,
                'fat': 22.5
            },
            'health_score': 78,
            'recommendations': [
                'Отличный выбор! Блюдо богато белком.',
                'Добавьте цельнозерновой хлеб для сложных углеводов.'
            ]
        }


# Поток ещё в run() — нельзя deleteLater(QThread), иначе abort «Destroyed while thread is still running».
_ORPHAN_IMAGE_ANALYZER_THREADS: list[ImageAnalyzerThread] = []


class PhotoUploadDialog(QDialog):
    """Диалог загрузки и анализа фото еды"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        apply_light_dialog_chrome(self)
        self.setWindowTitle("📸 Распознавание еды по фото")
        self.setMinimumSize(600, 700)
        self.image_path = None
        self.analyzer_thread: ImageAnalyzerThread | None = None
        self._progress_timer = None
        self.setup_ui()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._progress_timer is not None and self._progress_timer.isActive():
            self._progress_timer.stop()
        t = self.analyzer_thread
        if t is not None:
            self.analyzer_thread = None
            try:
                t.disconnect(self)
            except TypeError:
                pass
            t.blockSignals(True)
            if t.isRunning():
                t.requestInterruption()
                t.wait(15000)
            if t.isRunning():
                _log.warning(
                    "ImageAnalyzerThread не завершился за 15 с — удерживаем QThread до выхода процесса (без deleteLater)."
                )
                _ORPHAN_IMAGE_ANALYZER_THREADS.append(t)
            else:
                t.deleteLater()
        super().closeEvent(event)

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title = QLabel("🍽️ Загрузите фото блюда для анализа")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Область для изображения
        self.image_label = QLabel()
        self.image_label.setMinimumHeight(300)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #bdc3c7;
                border-radius: 10px;
                background-color: #ecf0f1;
                color: #7f8c8d;
            }
        """)
        self.image_label.setText("Перетащите фото сюда\nили нажмите кнопку ниже")
        layout.addWidget(self.image_label)
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        
        self.upload_btn = QPushButton("📷 Загрузить фото")
        self.upload_btn.setMinimumHeight(40)
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #1a1a1a;
                border: 2px solid #1a1a1a;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #EBF5FB;
            }
        """)
        self.upload_btn.clicked.connect(self.upload_image)
        btn_layout.addWidget(self.upload_btn)
        
        self.analyze_btn = QPushButton("🔍 Анализировать")
        self.analyze_btn.setMinimumHeight(40)
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #1a1a1a;
                border: 2px solid #1B5E20;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E8F5E9;
            }
            QPushButton:disabled {
                background-color: #EEEEEE;
                color: #757575;
                border: 2px solid #9E9E9E;
            }
        """)
        self.analyze_btn.clicked.connect(self.analyze_image)
        self.analyze_btn.setEnabled(False)
        btn_layout.addWidget(self.analyze_btn)
        
        layout.addLayout(btn_layout)
        
        # Прогресс бар
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
            }
        """)
        layout.addWidget(self.progress)
        
        # Результаты анализа
        results_label = QLabel("📊 Результаты анализа:")
        results_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(results_label)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMinimumHeight(200)
        self.results_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                padding: 10px;
                background-color: #ffffff;
                font-family: monospace;
            }
        """)
        layout.addWidget(self.results_text)
        
        # Кнопки действий
        action_layout = QHBoxLayout()
        
        self.add_meal_btn = QPushButton("✅ Добавить в дневник")
        self.add_meal_btn.setMinimumHeight(40)
        self.add_meal_btn.setStyleSheet("""
            QPushButton {
                background-color: #E8F5E9;
                color: #1a1a1a;
                border: 2px solid #1B5E20;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #C8E6C9;
            }
            QPushButton:disabled {
                background-color: #EEEEEE;
                color: #757575;
                border: 2px solid #9E9E9E;
            }
        """)
        self.add_meal_btn.clicked.connect(self.add_to_diary)
        self.add_meal_btn.setEnabled(False)
        action_layout.addWidget(self.add_meal_btn)
        
        cancel_btn = QPushButton("❌ Отмена")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFEBEE;
                color: #1a1a1a;
                border: 2px solid #C0392B;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FFCDD2;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        action_layout.addWidget(cancel_btn)
        
        layout.addLayout(action_layout)
        
        self.setLayout(layout)

        for w in (
            self.upload_btn,
            self.analyze_btn,
            self.add_meal_btn,
            cancel_btn,
        ):
            attach_press_flash(w)

        self.setStyleSheet(STANDARD_LIGHT_FORM_DIALOG_QSS)

    def upload_image(self):
        """Загрузка изображения"""
        file_path = get_open_image_path(self, "Выберите изображение")
        
        if file_path:
            self.image_path = file_path
            
            # Отображение изображения
            pixmap = QPixmap(file_path)
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.setText("")
            
            # Активация кнопки анализа
            self.analyze_btn.setEnabled(True)
    
    def analyze_image(self):
        """Анализ изображения"""
        if not self.image_path:
            return
        
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.analyze_btn.setEnabled(False)
        self.results_text.clear()
        
        # Запуск анализа в отдельном потоке
        self.analyzer_thread = ImageAnalyzerThread(self.image_path)
        self.analyzer_thread.analysis_complete.connect(self.on_analysis_complete)
        self.analyzer_thread.analysis_error.connect(self.on_analysis_error)
        self.analyzer_thread.start()
        
        # Анимация прогресса
        from PyQt6.QtCore import QTimer

        if self._progress_timer is not None and self._progress_timer.isActive():
            self._progress_timer.stop()
        self._progress_timer = QTimer(self)
        self._progress_timer.timeout.connect(self.update_progress)
        self._progress_timer.start(100)
    
    def update_progress(self):
        """Обновление прогресс бара"""
        value = self.progress.value() + 5
        if value >= 90:
            if self._progress_timer is not None:
                self._progress_timer.stop()
        else:
            self.progress.setValue(value)
    
    def on_analysis_complete(self, result: dict):
        """Обработка результатов анализа"""
        if self._progress_timer is not None:
            self._progress_timer.stop()
        self.progress.setValue(100)
        
        # Форматирование результатов
        text = "<h3>🍽️ Обнаруженные продукты:</h3>"
        
        for food in result.get('foods', []):
            confidence = int(food['confidence'] * 100)
            text += f"""
            <div style="background-color: #ecf0f1; padding: 10px; margin: 5px; border-radius: 5px;">
                <b>{food['name']}</b> (уверенность: {confidence}%)<br>
                Порция: {food['portion']}<br>
                🔥 {food['calories']} ккал | 
                🥩 {food['protein']}г белков | 
                🍞 {food['carbs']}г углеводов | 
                🧈 {food['fat']}г жиров
            </div>
            """
        
        total = result.get('total', {})
        text += f"""
        <h3>📊 Итого:</h3>
        <div style="background-color: #d5f5e3; padding: 15px; margin: 10px; border-radius: 8px; font-size: 16px;">
            🔥 <b>{total.get('calories', 0)}</b> ккал<br>
            🥩 {total.get('protein', 0)}г белков | 
            🍞 {total.get('carbs', 0)}г углеводов | 
            🧈 {total.get('fat', 0)}г жиров
        </div>
        """
        
        health_score = result.get('health_score', 0)
        score_color = "#27ae60" if health_score > 70 else "#f39c12" if health_score > 40 else "#e74c3c"
        text += f"""
        <h3>💚 Health Score:</h3>
        <div style="background-color: {score_color}; color: white; padding: 10px; 
                    margin: 10px; border-radius: 8px; font-size: 18px; text-align: center;">
            {health_score}/100
        </div>
        """
        
        if result.get('recommendations'):
            text += "<h3>💡 Рекомендации:</h3><ul>"
            for rec in result['recommendations']:
                text += f"<li>{rec}</li>"
            text += "</ul>"
        
        self.results_text.setHtml(text)
        self.add_meal_btn.setEnabled(True)
        self.analyze_btn.setEnabled(True)
        
        # Сохранение результатов
        self.analysis_result = result
    
    def on_analysis_error(self, error: str):
        """Обработка ошибки анализа"""
        if self._progress_timer is not None:
            self._progress_timer.stop()
        self.progress.setVisible(False)
        self.analyze_btn.setEnabled(True)
        
        from ui.components.dialogs import show_error

        show_error(
            self,
            "Ошибка анализа",
            f"Не удалось проанализировать изображение:\n{error}",
        )
    
    def add_to_diary(self):
        """Добавление результатов в дневник питания"""
        if not hasattr(self, 'analysis_result'):
            return
        
        # Здесь будет интеграция с базой данных
        from ui.components.dialogs import show_message

        show_message(self, "Успешно", "Данные добавлены в дневник питания!")
        
        self.accept()
    
    def dragEnterEvent(self, event):
        """Обработка перетаскивания файла"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """Обработка отпускания файла"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                self.image_path = file_path
                
                pixmap = QPixmap(file_path)
                scaled_pixmap = pixmap.scaled(
                    self.image_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
                self.image_label.setText("")
                self.analyze_btn.setEnabled(True)
