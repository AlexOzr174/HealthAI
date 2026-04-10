"""
AI Analytics Widget - Виджет предиктивной аналитики и графиков
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QScrollArea, QGridLayout,
                             QProgressBar, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

try:
    import matplotlib
    matplotlib.use('QtAgg')
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class PredictionCard(QFrame):
    """Карточка с прогнозом"""
    def __init__(self, title, value, unit, icon, color="#4CAF50"):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 10px;
                border-left: 5px solid {color};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Заголовок
        title_label = QLabel(f"{icon} {title}")
        title_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #666;")
        layout.addWidget(title_label)
        
        # Значение
        value_label = QLabel(f"{value} {unit}")
        value_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(value_label)


class AIAnalyticsWidget(QWidget):
    """Виджет аналитики с графиками и прогнозами"""
    def __init__(self, ai_engine, user_id, parent=None):
        super().__init__(parent)
        self.ai_engine = ai_engine
        self.user_id = user_id
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Заголовок
        header = QLabel("📊 Предиктивная Аналитика")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header.setStyleSheet("color: #2c3e50;")
        main_layout.addWidget(header)
        
        # Скролл для контента
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        
        # Карточки прогнозов
        predictions_layout = QGridLayout()
        predictions_layout.setSpacing(15)
        
        self.weight_pred = PredictionCard(
            "Прогноз веса (30 дней)", 
            "--", "кг", "⚖️", "#2196F3"
        )
        self.calorie_pred = PredictionCard(
            "Рекомендуемые калории", 
            "--", "ккал", "🔥", "#FF9800"
        )
        self.goal_pred = PredictionCard(
            "Достижение цели", 
            "--", "дней", "🎯", "#4CAF50"
        )
        
        predictions_layout.addWidget(self.weight_pred, 0, 0)
        predictions_layout.addWidget(self.calorie_pred, 0, 1)
        predictions_layout.addWidget(self.goal_pred, 1, 0, 1, 2)
        
        content_layout.addLayout(predictions_layout)
        
        # График веса
        if MATPLOTLIB_AVAILABLE:
            graph_section = QLabel("📈 Тренд веса")
            graph_section.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            graph_section.setStyleSheet("color: #2c3e50; margin-top: 10px;")
            content_layout.addWidget(graph_section)
            
            self.fig = Figure(figsize=(8, 4), facecolor='white')
            self.canvas = FigureCanvas(self.fig)
            self.canvas.setStyleSheet("background-color: white; border-radius: 10px;")
            content_layout.addWidget(self.canvas)
            
            # Кнопки периода
            period_layout = QHBoxLayout()
            period_layout.addStretch()
            
            for days, label in [(7, "7 дней"), (14, "14 дней"), (30, "30 дней")]:
                btn = QPushButton(label)
                btn.setFixedWidth(100)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e0e0e0;
                        border-radius: 5px;
                        padding: 8px;
                    }
                    QPushButton:hover {
                        background-color: #d0d0d0;
                    }
                """)
                btn.clicked.connect(lambda checked, d=days: self.update_graph(d))
                period_layout.addWidget(btn)
            
            content_layout.addLayout(period_layout)
        else:
            no_graph = QLabel("⚠️ Установите matplotlib для отображения графиков: pip install matplotlib")
            no_graph.setStyleSheet("color: #f44336; padding: 20px;")
            content_layout.addWidget(no_graph)
        
        # Инсайты
        insights_section = QLabel("💡 Персональные инсайты")
        insights_section.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        insights_section.setStyleSheet("color: #2c3e50; margin-top: 10px;")
        content_layout.addWidget(insights_section)
        
        self.insights_label = QLabel("Загрузите данные о весе для получения инсайтов")
        self.insights_label.setWordWrap(True)
        self.insights_label.setStyleSheet("""
            QLabel {
                background-color: #fff3e0;
                border-radius: 10px;
                padding: 15px;
                color: #e65100;
            }
        """)
        content_layout.addWidget(self.insights_label)
        
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll, 1)
        
        # Кнопка обновления
        refresh_btn = QPushButton("🔄 Обновить аналитику")
        refresh_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        refresh_btn.setFixedHeight(50)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_analytics)
        main_layout.addWidget(refresh_btn)
        
    def update_predictions(self, weight_history):
        """Обновить карточки прогнозов"""
        if not weight_history or len(weight_history) < 2:
            return
            
        try:
            analysis = self.ai_engine.get_weight_analysis(
                user_id=self.user_id,
                weight_history=weight_history
            )
            
            # Прогноз веса
            if 'prediction_30' in analysis:
                pred_weight = analysis['prediction_30']
                self.weight_pred.findChild(QLabel).setText(f"{pred_weight:.1f} кг")
                
            # Достижение цели
            if 'goal_prediction' in analysis:
                goal_info = analysis['goal_prediction']
                if goal_info.get('reachable'):
                    days = goal_info.get('days_to_goal', 0)
                    self.goal_pred.findChild(QLabel).setText(f"{days} дней")
                else:
                    self.goal_pred.findChild(QLabel).setText("Недостижимо")
                    
            # Инсайты
            if 'insights' in analysis and analysis['insights']:
                insight_text = "\n".join(f"• {insight}" for insight in analysis['insights'][:3])
                self.insights_label.setText(insight_text)
                
        except Exception as e:
            print(f"Ошибка обновления прогнозов: {e}")
            
    def update_graph(self, days=30):
        """Обновить график веса"""
        if not MATPLOTLIB_AVAILABLE:
            return
            
        # Пример данных (в реальности брать из БД)
        import random
        from datetime import datetime, timedelta
        
        dates = []
        weights = []
        base_date = datetime.now() - timedelta(days=days)
        base_weight = 85.0
        
        for i in range(days):
            dates.append(base_date + timedelta(days=i))
            weights.append(base_weight + random.uniform(-0.5, 0.5) + (i * 0.05))
        
        # Очистка графика
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        
        # Построение графика
        ax.plot(dates, weights, linewidth=2, color='#4CAF50', marker='o', markersize=4)
        ax.fill_between(dates, weights, alpha=0.3, color='#4CAF50')
        
        # Стилизация
        ax.set_title(f"Тренд веса за {days} дней", fontsize=12, fontweight='bold')
        ax.set_xlabel("Дата")
        ax.set_ylabel("Вес (кг)")
        ax.grid(True, alpha=0.3)
        
        # Поворот подписей дат
        self.fig.autofmt_xdate()
        self.fig.tight_layout()
        
        self.canvas.draw()
        
    def refresh_analytics(self):
        """Обновить всю аналитику"""
        # В реальности загружать данные из БД
        import random
        weight_history = [85.0 + random.uniform(-1, 1) + (i * 0.1) for i in range(30)]
        self.update_predictions(weight_history)
        self.update_graph(30)
