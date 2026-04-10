"""
Виджет кругового прогресс-бара для отображения целей
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont
from PyQt6.QtCore import Qt, QRectF
from ui.styles import CURRENT_THEME


class CircularProgressWidget(QWidget):
    """Круговой индикатор прогресса (калории, вода, шаги)"""
    
    def __init__(self, title: str, current: float, target: float, 
                 unit: str = '', color: str = '#4CAF50', parent=None):
        super().__init__(parent)
        self.title = title
        self.current = current
        self.target = target
        self.unit = unit
        self.color = QColor(color)
        self.setFixedSize(180, 200)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Центрирование
        center_x = self.width() // 2
        center_y = 90
        radius = 60
        
        # Прогресс
        progress = min(self.current / max(self.target, 1), 1.0)
        angle_span = int(360 * 16 * progress)
        
        # Фоновый круг
        bg_pen = QPen(QColor(CURRENT_THEME['border']), 12)
        bg_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(bg_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(
            QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2),
            0, 360 * 16
        )
        
        # Круг прогресса
        pen = QPen(self.color, 12)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(
            QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2),
            90 * 16, -angle_span  # По часовой стрелке от верха
        )
        
        # Текст в центре
        text_color = QColor(CURRENT_THEME['text_primary'])
        painter.setPen(text_color)
        painter.setFont(QFont('Arial', 20, QFont.Weight.Bold))
        
        value_text = f"{int(self.current)}{self.unit}"
        text_rect = QRectF(center_x - 40, center_y - 15, 80, 30)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, value_text)
        
        # Подпись
        painter.setFont(QFont('Arial', 11))
        label_color = QColor(CURRENT_THEME['text_secondary'])
        painter.setPen(label_color)
        label_rect = QRectF(0, 150, self.width(), 30)
        painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, self.title)
        
        # Цель
        if self.target > 0:
            goal_text = f"из {int(self.target)}{self.unit}"
            painter.setFont(QFont('Arial', 9))
            goal_rect = QRectF(0, 175, self.width(), 20)
            painter.drawText(goal_rect, Qt.AlignmentFlag.AlignCenter, goal_text)
    
    def update_progress(self, current: float, target: float):
        """Обновить прогресс"""
        self.current = current
        self.target = target
        self.update()


class MacroProgressWidget(QWidget):
    """Виджет с тремя прогресс-барами для БЖУ"""
    
    def __init__(self, protein: dict, fats: dict, carbs: dict, parent=None):
        """
        protein/fats/carbs: {'current': 100, 'target': 150}
        """
        super().__init__(parent)
        self.protein = protein
        self.fats = fats
        self.carbs = carbs
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Заголовок
        title = QLabel("Макронутриенты")
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: %s;
        """ % CURRENT_THEME['text_primary'])
        layout.addWidget(title)
        
        # Прогресс бары
        macros = [
            ('Белки', self.protein, '#FF6B6B'),
            ('Жиры', self.fats, '#4ECDC4'),
            ('Углеводы', self.carbs, '#FFE66D')
        ]
        
        for name, data, color in macros:
            current = data.get('current', 0)
            target = data.get('target', 100)
            percent = min((current / max(target, 1)) * 100, 100)
            
            macro_widget = QWidget()
            macro_layout = QVBoxLayout(macro_widget)
            macro_layout.setContentsMargins(0, 0, 0, 0)
            macro_layout.setSpacing(5)
            
            # Название и значение
            header_layout = QHBoxLayout()
            name_label = QLabel(name)
            name_label.setStyleSheet(f"font-size: 13px; color: {color}; font-weight: bold;")
            
            value_label = QLabel(f"{current}г / {target}г")
            value_label.setStyleSheet(f"font-size: 12px; color: {CURRENT_THEME['text_secondary']};")
            
            header_layout.addWidget(name_label)
            header_layout.addStretch()
            header_layout.addWidget(value_label)
            
            macro_layout.addLayout(header_layout)
            
            # Фон прогресс бара
            bg_widget = QWidget()
            bg_widget.setFixedHeight(10)
            bg_widget.setStyleSheet(f"""
                background-color: {CURRENT_THEME['border']};
                border-radius: 5px;
            """)
            
            # Прогресс
            progress_widget = QWidget(bg_widget)
            progress_widget.setFixedHeight(10)
            progress_widget.move(0, 0)
            progress_width = int((percent / 100) * bg_widget.width())
            progress_widget.resize(progress_width, 10)
            progress_widget.setStyleSheet(f"""
                background-color: {color};
                border-radius: 5px;
            """)
            
            macro_layout.addWidget(bg_widget)
            layout.addWidget(macro_widget)
