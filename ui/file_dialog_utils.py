"""
Диалог выбора файла: на macOS стиль «macintosh» плохо дружит с QSS; Fusion + свой светлый
стиль на самом диалоге — чтобы окно не «тонуло» в тёмной теме приложения.
"""
from __future__ import annotations

from typing import Optional

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QDialog, QFileDialog, QStyleFactory, QWidget

# Светлая тема только для этого окна (перебивает глобальный тёмный QSS).
_LIGHT_FILE_DIALOG_QSS = """
QFileDialog {
    background-color: #F0F2F5;
    color: #141414;
}
QFileDialog QWidget {
    color: #141414;
}
QFileDialog QLabel {
    color: #141414;
    background-color: transparent;
}
QFileDialog QFrame {
    background-color: #F0F2F5;
    border: none;
}
QFileDialog QSplitter::handle {
    background-color: #D5DAE3;
}
QFileDialog QTreeView,
QFileDialog QListView,
QFileDialog QTableView,
QFileDialog QAbstractItemView {
    background-color: #FFFFFF;
    color: #141414;
    alternate-background-color: #F7F9FC;
    selection-background-color: #B8DAFF;
    selection-color: #000000;
    border: 1px solid #B0B8C4;
    outline: none;
}
QFileDialog QTreeView::item,
QFileDialog QListView::item {
    color: #141414;
    padding: 4px 6px;
}
QFileDialog QTreeView::item:selected,
QFileDialog QListView::item:selected {
    background-color: #B8DAFF;
    color: #000000;
}
QFileDialog QTreeView::item:hover,
QFileDialog QListView::item:hover {
    background-color: #E8F2FF;
}
QFileDialog QHeaderView::section {
    background-color: #E4E9F0;
    color: #141414;
    padding: 8px;
    border: 1px solid #B0B8C4;
    font-weight: 600;
}
QFileDialog QLineEdit {
    background-color: #FFFFFF;
    color: #141414;
    border: 1px solid #8FA0B3;
    border-radius: 5px;
    padding: 7px 9px;
    selection-background-color: #B8DAFF;
    selection-color: #000000;
}
QFileDialog QComboBox {
    background-color: #FFFFFF;
    color: #141414;
    border: 1px solid #8FA0B3;
    border-radius: 5px;
    padding: 5px 10px;
    padding-right: 28px;
    min-height: 28px;
}
QFileDialog QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 26px;
    border: none;
    border-left: 1px solid #8FA0B3;
    background-color: #EEF1F6;
}
QFileDialog QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    color: #141414;
    selection-background-color: #B8DAFF;
    selection-color: #000000;
    border: 1px solid #8FA0B3;
    outline: none;
}
QFileDialog QComboBox QAbstractItemView::item {
    min-height: 28px;
    padding: 6px 10px;
    color: #141414;
}
QFileDialog QPushButton {
    background-color: #FFFFFF;
    color: #141414;
    border: 2px solid #3D4F63;
    border-radius: 7px;
    padding: 8px 18px;
    min-width: 92px;
    min-height: 36px;
    font-weight: 600;
}
QFileDialog QPushButton:hover {
    background-color: #EEF2F8;
}
QFileDialog QPushButton:pressed {
    background-color: #DDE4EE;
    padding-top: 9px;
    padding-bottom: 7px;
}
QFileDialog QPushButton:default {
    background-color: #E3F0FF;
    border-color: #2563A8;
}
QFileDialog QToolButton {
    background-color: #FFFFFF;
    color: #141414;
    border: 1px solid #8FA0B3;
    border-radius: 4px;
    padding: 4px;
}
QFileDialog QToolButton:hover {
    background-color: #EEF2F8;
}
QFileDialog QScrollBar:vertical {
    background-color: #E8ECF2;
    width: 12px;
    border-radius: 5px;
}
QFileDialog QScrollBar::handle:vertical {
    background-color: #A8B4C4;
    border-radius: 5px;
    min-height: 28px;
}
QFileDialog QScrollBar:horizontal {
    background-color: #E8ECF2;
    height: 12px;
    border-radius: 5px;
}
QFileDialog QScrollBar::handle:horizontal {
    background-color: #A8B4C4;
    border-radius: 5px;
    min-width: 28px;
}
"""


def _apply_light_dialog_chrome(dlg: QFileDialog) -> None:
    dlg.setStyleSheet(_LIGHT_FILE_DIALOG_QSS)
    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window, QColor("#F0F2F5"))
    pal.setColor(QPalette.ColorRole.WindowText, QColor("#141414"))
    pal.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
    pal.setColor(QPalette.ColorRole.AlternateBase, QColor("#F7F9FC"))
    pal.setColor(QPalette.ColorRole.Text, QColor("#141414"))
    pal.setColor(QPalette.ColorRole.Button, QColor("#FFFFFF"))
    pal.setColor(QPalette.ColorRole.ButtonText, QColor("#141414"))
    pal.setColor(QPalette.ColorRole.Highlight, QColor("#B8DAFF"))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#000000"))
    dlg.setPalette(pal)


def get_open_image_path(
    parent: Optional[QWidget],
    title: str = "Выберите фото еды",
    directory: str = "",
    name_filter: str = "Images (*.png *.xpm *.jpg *.jpeg *.bmp)",
) -> str:
    dlg = QFileDialog(parent)
    dlg.setWindowTitle(title)
    if directory:
        dlg.setDirectory(directory)
    dlg.setNameFilters([name_filter])
    dlg.setFileMode(QFileDialog.FileMode.ExistingFile)
    dlg.setOption(QFileDialog.Option.DontUseNativeDialog, True)
    fusion = QStyleFactory.create("Fusion")
    if fusion is not None:
        dlg.setStyle(fusion)
    _apply_light_dialog_chrome(dlg)
    if dlg.exec() != QDialog.DialogCode.Accepted:
        return ""
    files = dlg.selectedFiles()
    return files[0] if files else ""
