"""
Виджет карточки продукта с нутриентами
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt
from ui.styles import CURRENT_THEME


class ProductCardWidget(QWidget):
    """Стильная карточка продукта с информацией о КБЖУ"""
    
    def __init__(self, product_data: dict, parent=None):
        super().__init__(parent)
        self.product_data = product_data
        self.init_ui()
        
    def init_ui(self):
        self.setFixedHeight(120)
        self.setStyleSheet("""
            ProductCardWidget {
                background-color: %s;
                border-radius: 12px;
                border: 1px solid %s;
            }
            ProductCardWidget:hover {
                border: 2px solid #4CAF50;
            }
        """ % (
            CURRENT_THEME['card_bg'],
            CURRENT_THEME['border']
        ))
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)
        
        # Иконка/категория
        icon_label = QLabel(self.get_category_icon())
        icon_label.setStyleSheet("font-size: 32px; min-width: 50px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # Основная информация
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        # Название
        name_label = QLabel(self.product_data.get('name', 'Продукт'))
        name_label.setStyleSheet("""
            font-size: 16px; 
            font-weight: bold; 
            color: %s;
        """ % CURRENT_THEME['text_primary'])
        info_layout.addWidget(name_label)
        
        # Категория
        category_label = QLabel(self.product_data.get('category', ''))
        category_label.setStyleSheet("""
            font-size: 12px; 
            color: %s;
        """ % CURRENT_THEME['text_secondary'])
        info_layout.addWidget(category_label)
        
        # Калории
        cal_label = QLabel(f"⚡ {self.product_data.get('calories', 0)} ккал / 100г")
        cal_label.setStyleSheet("""
            font-size: 13px; 
            color: #FF9800;
            font-weight: bold;
        """)
        info_layout.addWidget(cal_label)
        
        layout.addLayout(info_layout, 1)
        
        # Нутриенты
        macros_layout = QHBoxLayout()
        macros_layout.setSpacing(10)
        
        macros = [
            ('🥩', 'belki', f"{self.product_data.get('protein', 0):.1f}г"),
            ('🧈', 'ziri', f"{self.product_data.get('fat', 0):.1f}г"),
            ('🍞', 'uglevodi', f"{self.product_data.get('carbs', 0):.1f}г")
        ]
        
        for icon, key, value in macros:
            macro_frame = QFrame()
            macro_frame.setStyleSheet("""
                QFrame {
                    background-color: %s;
                    border-radius: 8px;
                    padding: 5px;
                }
            """ % CURRENT_THEME['card_bg'])
            
            macro_layout = QVBoxLayout(macro_frame)
            macro_layout.setContentsMargins(8, 5, 8, 5)
            macro_layout.setSpacing(2)
            macro_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 14px;")
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            macro_layout.addWidget(icon_lbl)
            
            value_lbl = QLabel(value)
            value_lbl.setStyleSheet("""
                font-size: 12px; 
                font-weight: bold;
                color: %s;
            """ % CURRENT_THEME['text_primary'])
            value_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            macro_layout.addWidget(value_lbl)
            
            macros_layout.addWidget(macro_frame)
        
        layout.addLayout(macros_layout)
        
    def get_category_icon(self):
        category = self.product_data.get('category', '').lower()
        icons = {
            'овощи': '🥬',
            'фрукты': '🍎',
            'мясо': '🥩',
            'рыба': '🐟',
            'молочные': '🥛',
            'крупы': '🌾',
            'бобовые': '🫘',
            'орехи': '🥜',
            'масла': '🫒',
            'сладости': '🍫',
            'напитки': '🥤'
        }
        return icons.get(category, '🍽️')
