from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import pyqtSignal


class LabelMouseTracker(QLabel):
    clickSignal = pyqtSignal(int, int)

    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        self.clickSignal.emit(event.x(), event.y())
