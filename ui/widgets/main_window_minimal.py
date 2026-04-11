# main_window_minimal.py
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from ui.pages.dashboard import DashboardPage

app = QApplication(sys.argv)
window = QMainWindow()
window.setCentralWidget(DashboardPage(main_window=window))
window.show()
sys.exit(app.exec())
