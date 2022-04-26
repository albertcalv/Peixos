import copy
import os.path
import sys
from random import randint as ri

import cv2 as cv
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QWidget, QProgressBar, QPushButton, QFileDialog, QLabel, QVBoxLayout, \
    QCheckBox, QHBoxLayout, QSpinBox

import core.get_tracking_position_objects as tpo
from config import Config
from core import switcher
from core.gui.custom_components import LabelMouseTracker
import ui_validation as uiv


class Application(QWidget):
    stopExecution = pyqtSignal()
    playSignal = pyqtSignal()
    pauseSignal = pyqtSignal()
    changefps = pyqtSignal(int)

    def __init__(self, app, config):
        super().__init__()
        self.config = config
        self.app = app
        self.initUI()

    def initUI(self):

        self.createdControls = False
        self.setWindowTitle('Tracking')

        self.general_layout = QHBoxLayout(self)

        self.layout_viewer = QVBoxLayout()
        self.general_layout.addLayout(self.layout_viewer)

        self.label_video = LabelMouseTracker()
        self.layout_viewer.addWidget(self.label_video)
        self.layout = QVBoxLayout()
        self.general_layout.addLayout(self.layout)

        # Layout Control Automatic assignation
        self.layout_automatic_controls = QVBoxLayout()
        self.layout.addLayout(self.layout_automatic_controls)

        self.layout_video_selector = QHBoxLayout()
        self.layout_automatic_controls.addLayout(self.layout_video_selector)
        self.video_selector = QPushButton('Select Video')
        self.video_selected_label = QLabel()
        self.video_selector.clicked.connect(self.selectFile)
        self.layout_video_selector.addWidget(self.video_selector)
        self.layout_video_selector.addWidget(self.video_selected_label)

        self.layout_background_selector = QHBoxLayout()
        self.layout_automatic_controls.addLayout(self.layout_background_selector)
        self.background_selector = QPushButton('Select Background')
        self.background_selector_label = QLabel()
        self.background_selector.clicked.connect(self.selectFileBackground)
        self.layout_background_selector.addWidget(self.background_selector)
        self.layout_background_selector.addWidget(self.background_selector_label)

        self.layout_output_selector = QHBoxLayout()
        self.layout_automatic_controls.addLayout(self.layout_output_selector)
        self.output_selector = QPushButton('Select Input Output Traectories')
        self.output_selector_label = QLabel()
        self.output_selector.clicked.connect(self.selectFileIO)
        self.layout_output_selector.addWidget(self.output_selector)
        self.layout_output_selector.addWidget(self.output_selector_label)

        self.num_fish = 40
        self.colors = list(map(lambda x: (ri(0, 255), ri(0, 255), ri(0, 255)), range(self.num_fish)))
        self.layout_play = QHBoxLayout()
        self.layout_automatic_controls.addLayout(self.layout_play)
        self.layout_play.addWidget(QLabel("Number of trackings"))
        self.number_fish_spiner = QSpinBox()
        self.number_fish_spiner.setValue(self.num_fish)
        self.layout_play.addWidget(self.number_fish_spiner)
        self.number_fish_spiner.valueChanged.connect(self.numberFishChange)
        
        self.layout_execution = QHBoxLayout()
        self.layout_automatic_controls.addLayout(self.layout_execution)
        self.execute_button = QPushButton('Execute')
        self.execute_button.clicked.connect(self.onButtonClick)
        self.layout_execution.addWidget(self.execute_button)

        self.show()

    def onButtonClick(self):
        uiv.analyze_video(self.video_path, self.background_path, None, self.num_fish, 0)

    def selectFile(self):
        self.video_path = str(QFileDialog.getOpenFileName()[0])
        self.video_selected_label.setText(os.path.basename(self.video_path))
        self.capture = cv.VideoCapture(self.video_path)
        self.num_frames_in_video = int(self.capture.get(cv.CAP_PROP_POS_FRAMES))

    def selectFileBackground(self):
        self.background_path = str(QFileDialog.getOpenFileName()[0])
        self.background_frame = tpo.get_background_frame(self.background_path)
        self.background_selector_label.setText(os.path.basename(self.background_path))

    def selectFileIO(self):
        self.io_path = str(QFileDialog.getOpenFileName()[0])
        self.output_selector_label.setText(os.path.basename(self.io_path))

    def numberFishChange(self):
        self.num_fish = int(self.number_fish_spiner.value())


if __name__ == "__main__":
    config = Config()
    print(config.get_workspace())
    app = QApplication(sys.argv)
    window = Application(app, Config().config)
    window.show()

    sys.exit(app.exec_())
