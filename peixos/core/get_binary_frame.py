import cv2 as cv
from config import Config


def get_binary_frame(frame, background_frame, precision):
    if len(frame) != len(background_frame) or len(frame[0]) != len(background_frame[0]):
        background_frame = cv.resize(background_frame, (len(frame[0]), len(frame)), interpolation = cv.INTER_AREA)
        
    binary_frame = cv.subtract(background_frame, frame)
    binary_frame = cv.cvtColor(binary_frame,cv.COLOR_RGB2GRAY) 
    if Config().get_variable("TRACKING", "use_bilateral_filter", 'bool'):
        binary_frame = cv.bilateralFilter(binary_frame,21,41,41) 
    # binary_frame = cv.cvtColor(binary_frame, cv.COLOR_BGR2GRAY)
    # binary_frame = cv.adaptiveThreshold(binary_frame, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 3, 1)
    (thresh, binary_frame) = cv.threshold(binary_frame, precision, 255, cv.THRESH_BINARY)
    return binary_frame
