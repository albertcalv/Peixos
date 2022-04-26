import traceback, sys
import cv2 as cv
from core import switcher

import core.get_tracking_position_objects as tpo

from PyQt5.QtCore import QThread, pyqtSignal
from utils.output_utils import OutputHandler
from time import sleep


class Execution(QThread):

    numFramesInit = pyqtSignal(int)
    actualFrameChange = pyqtSignal(int)
    finalizeExecution = pyqtSignal()

    def __init__(self, video_path: str, background_path, output_handler: OutputHandler, first_frame=0):
        super().__init__()
        self.video_path = video_path
        self.background_path = background_path
        self.actual_frame = first_frame
        self.output_handler = output_handler

    def stop(self):
        self.running = False

    def run(self):
        try:
            cap = cv.VideoCapture(self.video_path)
            cap.set(cv.CAP_PROP_POS_FRAMES, self.actual_frame)

            self.running = True
            self.numFramesInit.emit(int(cap.get(cv.CAP_PROP_FRAME_COUNT)))

            while cap.isOpened() and self.running:

                success, frame = cap.read()
                if not success:
                    break
                binary_frame, new_tracking_objects = tpo.get_tracking_position_and_direction(frame, self.background_path)
                switcher.assign_automatically(self.output_handler, self.actual_frame, new_tracking_objects)

                self.actual_frame = self.actual_frame + 1
                self.actualFrameChange.emit(self.actual_frame)

            self.output_handler.save_to_pickle()
            self.output_handler.save_to_csv()

            cap.release()
            cv.destroyAllWindows()

            self.finalizeExecution.emit()
        except:
            traceback.print_exc()
            (exctype, value, trace) = sys.exc_info()
            print(exctype, value, trace)
            sys.excepthook(exctype, value, trace)


class Play(QThread):

    sendFrame = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.running = False
        self.quit = False
        self.fps = 20

    def pause(self):
        self.running = False

    def play(self):
        self.running = True

    def changeFPS(self, value):
        self.fps = value

    def stop(self):
        self.quit = True
        print('received stop signal from window.')
        with self._lock:
            self._do_before_done()

    def run(self):
        while True:
            if self.running:
                sleep(1.0/float(self.fps))
                self.sendFrame.emit()
            if self.quit:
                break
