import sys
import numpy as np

import cv2 as cv
import math

import datetime

import core.get_binary_frame as bf
from config import Config

background_image = None


def is_inside(old_bb, new_bb):
    new_point = (new_bb[0] + new_bb[2]/2, new_bb[1] + new_bb[3]/2)

    if old_bb[0] + old_bb[2] > new_point[0] > old_bb[0] and old_bb[1] + old_bb[3] > new_point[1] > old_bb[1]:
        return True

    return False
    
def get_background_frame(path_to_video_background: str) -> object:
    global background_image
        
    if not path_to_video_background:
        return background_image

    capBackground = cv.VideoCapture(path_to_video_background)
    success, frame_background = capBackground.read()

    if not success:
        print('Failed to read video')
        sys.exit(1)

    return frame_background


def get_background_frame_from_original_video(path_to_video: str, path_to_workspace: str):
    global background_image
    
    print('START CREATING BACKGROUND')

    capBackground = cv.VideoCapture(path_to_video)
    success, frame_background = capBackground.read()
        
    avg1 = np.float32(frame_background)
    
    i = 0
        
    while success:
        success, frame_background = capBackground.read()
        
        if success:

            cv.accumulateWeighted(frame_background,avg1,0.01)
    
            cv.convertScaleAbs(avg1)
        
            i = i + 1
                        
            if i % 100 == 0 :
                print('Creating background frames used {0:3d}'.format(i))
                
    print('FINISH CREATING BACKGROUND')

    background_image = cv.convertScaleAbs(avg1)
    
    height , width , layers =  background_image.shape
    
    path_to_file = "{}/{}_{}.avi".format(path_to_workspace, "background",
                                                 datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
                                                   
    video_background = cv.VideoWriter(path_to_file, cv.VideoWriter_fourcc(*"MJPG"), 30,(width,height))
    
    video_background.write(background_image)
    video_background.write(background_image)
    video_background.write(background_image)
    
    video_background.release()
    
    print("[INFO] Path to background generated: {}".format(path_to_file))


def delete_closest_bb(last_BB_Set):
    delete_bb = []

    for i in range(len(last_BB_Set)):
        for j in range(i+1, len(last_BB_Set)):
            if i != j:
                bb_i = (last_BB_Set[i][0] + last_BB_Set[i][2]/2, last_BB_Set[i][1] + last_BB_Set[i][3]/2)
                bb_j = (last_BB_Set[j][0] + last_BB_Set[j][2]/2, last_BB_Set[j][1] + last_BB_Set[j][3]/2)
                if math.hypot(bb_i[0] - bb_j[0], bb_i[1] - bb_j[1]) < 7:
                    delete_bb.append(last_BB_Set[j])

    for delete in delete_bb:
        if delete in last_BB_Set:
            last_BB_Set.remove(delete)

    return last_BB_Set


def get_tracking_position_and_direction(frame, path_to_video_background, precision):
    
    size = Config().get_variable("TRACKING", "element_size", 'int')

    background_frame = get_background_frame(path_to_video_background)
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (size, size))
    
    binary_frame_draw = bf.get_binary_frame(frame, background_frame, precision)
    
    boxes = []
    
    for precision in range(25, 50, 5):

        binary_frame = bf.get_binary_frame(frame, background_frame, precision)
        thresh = cv.morphologyEx(binary_frame, cv.MORPH_OPEN, kernel)
        #erosion = cv.erode(thresh,kernel,iterations = 1)
        contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        
        if len(contours) == 0: 
            break
        
        bbInside = {}
    
        for contour in contours:
            
            isNewBB = True
            newBB = cv.boundingRect(contour)
            
            if newBB[2] * newBB[3] < 10:
                continue
            
            for oldBB in boxes:
                
                if is_inside(oldBB, newBB):
                    
                    if oldBB in bbInside :
                        bbInside[oldBB].append(newBB)
                    else:
                        bbInside[oldBB] = [newBB]
                    
                    isNewBB = False
            
            if isNewBB:
                boxes.append(newBB)
                
        for key, value in bbInside.items():
            
            if len(value) > 1:
                boxes.remove(key)
                boxes = boxes + value
                
    binary_frame = cv.cvtColor(binary_frame_draw, cv.COLOR_GRAY2BGR)

    return binary_frame, boxes


def get_bb_from_frame(frame, background_frame, precision = 18):

    last_BB_Set = []
    actual_precision = precision

    while True:

        binary_frame = bf.get_binary_frame(frame, background_frame, actual_precision)
        contours, _ = cv.findContours(binary_frame, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        if len(contours) == 0 or actual_precision > 50:
            break

        boxes = []
        for j, contour in enumerate(contours):
            box = cv.boundingRect(contour)
            if box[2] * box[3] > 2:
                boxes.append(box)
                for old_box in last_BB_Set:
                    if is_inside(old_box, box):
                        last_BB_Set.remove(old_box)

        last_BB_Set = last_BB_Set + boxes
        actual_precision = actual_precision + 1

    return last_BB_Set
