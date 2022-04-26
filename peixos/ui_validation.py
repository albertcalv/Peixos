from config import Config
from random import randint as ri
import os.path

import cv2 as cv
import cvui
import numpy as np
import math

import core.get_tracking_position_objects as tpo
import post_processing as pp
from core import switcher
from utils.output_utils import OutputHandler


def find_next_nan(trajectories, actual_frame):
    for frame_index in range(actual_frame +1, len(trajectories.data)):
        next_trajectories = trajectories.get_frame(frame_index)
        for i in range(len(next_trajectories)):
            for j in range(len(next_trajectories[i])):
                if next_trajectories[i][j] == -1:
                    return frame_index

    return actual_frame


def actual_frame_has_nans(trajectories, actual_frame):
    next_trajectories = trajectories.get_frame(actual_frame)
    for i in range(len(next_trajectories)):
        if next_trajectories[i][0] == -1:
            return True
    return False


def rule_detection(trajectories, actual_frame):
    return actual_frame_nans_array(trajectories, actual_frame), actual_frame_same_positions_array(trajectories, actual_frame)


def actual_frame_nans(trajectories, actual_frame):
    result = ""
    next_trajectories = trajectories.get_frame(actual_frame)
    for i in range(len(next_trajectories)):
        if next_trajectories[i][0] == -1:
            result += str(i) + ", "

    return result


def actual_frame_nans_array(trajectories, actual_frame):
    result = []
    next_trajectories = trajectories.get_frame(actual_frame)
    for i in range(len(next_trajectories)):
        if next_trajectories[i][0] == -1:
            result.append(i)

    return result


def actual_frame_same_positions_array(trajectories, actual_frame):
    result = []
    if actual_frame <= 0:
        return result
    next_trajectories = trajectories.get_frame(actual_frame)
    for i in range(len(next_trajectories)):
        for j in range(i + 1, len(next_trajectories)):
            if next_trajectories[i][0] == next_trajectories[j][0] and next_trajectories[i][1] == next_trajectories[j][1]:
                result.append((i, j))
                break

    if len(result) > 0:
        print(result)
        
    return result

def analyze_video(path_to_video: str, path_to_video_background: str, path_trajectories: str, num_trackers: int,
                  start_frame: int = 0):

    config = Config()
    path_to_workspace = config.get_workspace()
    precision = config.get_variable("TRACKING", "precision", 'int')
    
    if not path_to_video_background:
        tpo.get_background_frame_from_original_video(path_to_video, path_to_workspace)
    
    #background_frame = tpo.get_background_frame(path_to_video)

    print("[INFO] Path to video: {}".format(path_to_video))
    print("[INFO] Path to video background: {}".format(path_to_video_background))
    print("[INFO] Num of elements: {}".format(num_trackers))

    config.print_log('Path to video: {}'.format(path_to_video))
    config.print_log('Path to video background: {}'.format(path_to_video_background))
    config.print_log('Num of elements: {}'.format(num_trackers))

    colors = list(map(lambda x: (ri(0, 255), ri(0, 255), ri(0, 255)), range(num_trackers)))

    cap = cv.VideoCapture(path_to_video)
    cap.set(cv.CAP_PROP_POS_FRAMES, start_frame)
    trajectories = OutputHandler(path_to_workspace, os.path.splitext(os.path.basename(path_to_video))[0], num_trackers)

    if path_trajectories:
        trajectories.load_from_pickle(path_trajectories)

    cv.namedWindow('MultiTracker', cv.WINDOW_NORMAL)
    cvui.init('MultiTracker')

    success, frame = cap.read()
    if not success:
        return

    # @TODO : Unused variable 'channels'
    height, width, channels = frame.shape
    window = np.zeros((55 + height, width + 350, 3), np.uint8)

    actual_frame = [start_frame]
    actual_frame_validator = start_frame

    play_automatic_assigantion = False
    play = False

    switch_object_1 = [0]
    switch_object_2 = [0]

    new_position = [0]
    validate_new_position = 0

    showCandidateZone = [False]
    actualShowCandidateZone = False
    showErrorZone = [False]
    actualShowErrorZone = False
    showBB = [False]
    actualShowBB = False
    showBinaryFrame = [False]
    actualShowBinaryFrame = False
    showTrace = [False]
    validateShowTrace = False
    showOnlyOneObject = [False]
    validateShowOnlyOneObject = False

    stopIfNan = [False]
    stopIfSamePosition = [False]

    position_clicked = [0, 0]

    window[:] = (49, 52, 49)

    frame = print_frame_with_tracker_marks(frame, trajectories, actual_frame[0], colors, position_clicked,
                                           path_to_video_background, actualShowBB, actualShowBinaryFrame,
                                           validateShowTrace, validateShowOnlyOneObject, new_position[0],
                                           actualShowCandidateZone, actualShowErrorZone)

    while True:
        if not cap.isOpened():
            play = False
            play_automatic_assigantion = False
            actual_frame[0] = actual_frame[0] - 1
            actual_frame_validator = actual_frame[0]
            trajectories.save_to_pickle()
            trajectories.save_to_csv()
            cap = cv.VideoCapture(path_to_video)
            cap.set(cv.CAP_PROP_POS_FRAMES, actual_frame[0])

        window[:] = (49, 52, 49)
        height, width, channels = frame.shape

        cvui.image(window, 4, 4, frame)

        cvui.text(window, width + 20, 25, 'Switch Form')
        cvui.counter(window, width + 20, 50, switch_object_1, 1)
        cvui.trackbar(window, width + 10, 75, 150, switch_object_1, 0, num_trackers - 1,
                      1, '%.0Lf', cvui.TRACKBAR_DISCRETE, 1)
        cvui.counter(window, width + 170, 50, switch_object_2, 1)
        cvui.trackbar(window, width + 160, 75, 150, switch_object_2, 0, num_trackers - 1,
                      1, '%.0Lf', cvui.TRACKBAR_DISCRETE, 1)

        cvui.text(window, width + 20, 200, 'New Position Form')
        cvui.text(window, width + 120, 225, '(' + str(position_clicked[0]) + ', ' + str(position_clicked[1]) + ')')
        cvui.counter(window, width + 20, 225, new_position, 1)
        cvui.trackbar(window, width + 10, 250, 150, new_position, 0, num_trackers - 1, 1,'%.0Lf', cvui.TRACKBAR_DISCRETE, 1)

        cvui.trackbar(window, 10, height + 5, width, actual_frame, 0, len(trajectories.data) - 1 if len(trajectories.data) > 1 else 1, 1, '%.0Lf', cvui.TRACKBAR_DISCRETE, 1)

        cvui.checkbox(window, width + 20, 410, 'Show Only One Fish', showOnlyOneObject)
        cvui.checkbox(window, width + 20, 440, 'Show Binary Frame', showBinaryFrame)
        cvui.checkbox(window, width + 20, 470, 'Show Bounding Boxes', showBB)
        cvui.checkbox(window, width + 20, 500, 'Show Trajectories', showTrace)
        cvui.checkbox(window, width + 20, 530, 'Show Candidate Zone', showCandidateZone)
        cvui.checkbox(window, width + 20, 560, 'Show Error Zone', showErrorZone)

        cvui.checkbox(window, width + 20, 600, 'Stop If Not Assigned', stopIfNan)
        cvui.checkbox(window, width + 20, 630, 'Stop If Same Position', stopIfSamePosition)

        if actual_frame_has_nans(trajectories, actual_frame[0]) and not play_automatic_assigantion:
            cvui.text(window, width + 20, 720, 'NaNs in frame (' + actual_frame_nans(trajectories,
                                                                                     actual_frame[0]) + ')')

        if showOnlyOneObject[0] != validateShowOnlyOneObject:
            validateShowOnlyOneObject = showOnlyOneObject[0]
            cap.set(cv.CAP_PROP_POS_FRAMES, actual_frame[0])
            success, frame = cap.read()
            frame = print_frame_with_tracker_marks(frame, trajectories, actual_frame[0], colors, position_clicked,
                                                   path_to_video_background, actualShowBB, actualShowBinaryFrame,
                                                   validateShowTrace, validateShowOnlyOneObject, new_position[0],
                                                   actualShowCandidateZone, actualShowErrorZone)

        if new_position[0] != validate_new_position:
            validate_new_position = new_position[0]
            if validateShowOnlyOneObject:
                cap.set(cv.CAP_PROP_POS_FRAMES, actual_frame[0])
                success, frame = cap.read()
                frame = print_frame_with_tracker_marks(frame, trajectories, actual_frame[0], colors, position_clicked,
                                                       path_to_video_background, actualShowBB, actualShowBinaryFrame,
                                                       validateShowTrace, validateShowOnlyOneObject, new_position[0],
                                                       actualShowCandidateZone, actualShowErrorZone)

        if showBinaryFrame[0] != actualShowBinaryFrame:
            actualShowBinaryFrame = showBinaryFrame[0]
            cap.set(cv.CAP_PROP_POS_FRAMES, actual_frame[0])
            success, frame = cap.read()
            frame = print_frame_with_tracker_marks(frame, trajectories, actual_frame[0], colors, position_clicked,
                                                   path_to_video_background, actualShowBB, actualShowBinaryFrame,
                                                   validateShowTrace, validateShowOnlyOneObject, new_position[0],
                                                   actualShowCandidateZone, actualShowErrorZone)

        if showTrace[0] != validateShowTrace:
            validateShowTrace = showTrace[0]
            cap.set(cv.CAP_PROP_POS_FRAMES, actual_frame[0])
            success, frame = cap.read()
            frame = print_frame_with_tracker_marks(frame, trajectories, actual_frame[0], colors, position_clicked,
                                                   path_to_video_background, actualShowBB, actualShowBinaryFrame,
                                                   validateShowTrace, validateShowOnlyOneObject, new_position[0],
                                                   actualShowCandidateZone, actualShowErrorZone)

        if showBB[0] != actualShowBB:
            actualShowBB = showBB[0]
            cap.set(cv.CAP_PROP_POS_FRAMES, actual_frame[0])
            success, frame = cap.read()
            frame = print_frame_with_tracker_marks(frame, trajectories, actual_frame[0], colors, position_clicked,
                                                   path_to_video_background, actualShowBB, actualShowBinaryFrame,
                                                   validateShowTrace, validateShowOnlyOneObject, new_position[0],
                                                   actualShowCandidateZone, actualShowErrorZone)

        if showCandidateZone[0] != actualShowCandidateZone:
            actualShowCandidateZone = showCandidateZone[0]
            cap.set(cv.CAP_PROP_POS_FRAMES, actual_frame[0])
            success, frame = cap.read()
            frame = print_frame_with_tracker_marks(frame, trajectories, actual_frame[0], colors, position_clicked,
                                                   path_to_video_background, actualShowBB, actualShowBinaryFrame,
                                                   validateShowTrace, validateShowOnlyOneObject, new_position[0],
                                                   actualShowCandidateZone, actualShowErrorZone)

        if showErrorZone[0] != actualShowErrorZone:
            actualShowErrorZone = showErrorZone[0]
            cap.set(cv.CAP_PROP_POS_FRAMES, actual_frame[0])
            success, frame = cap.read()
            frame = print_frame_with_tracker_marks(frame, trajectories, actual_frame[0], colors, position_clicked,
                                                   path_to_video_background, actualShowBB, actualShowBinaryFrame,
                                                   validateShowTrace, validateShowOnlyOneObject, new_position[0],
                                                   actualShowCandidateZone, actualShowErrorZone)

        if cvui.mouse(cvui.DOWN) and cvui.mouse().x - 4 < width and cvui.mouse().y - 4 < height:
            position_clicked[0] = cvui.mouse().x - 4
            position_clicked[1] = cvui.mouse().y - 4
            cap.set(cv.CAP_PROP_POS_FRAMES, actual_frame[0])
            success, frame = cap.read()
            frame = print_frame_with_tracker_marks(frame, trajectories, actual_frame[0], colors, position_clicked,
                                                   path_to_video_background, actualShowBB, actualShowBinaryFrame,
                                                   validateShowTrace, validateShowOnlyOneObject, new_position[0],
                                                   actualShowCandidateZone, actualShowErrorZone)

            if validateShowOnlyOneObject:
                switcher.assign_new_position_to_fish(trajectories, actual_frame[0], new_position[0], position_clicked)

                cap.set(cv.CAP_PROP_POS_FRAMES, actual_frame[0])
                success, frame = cap.read()
                position_clicked[0] = 0
                position_clicked[1] = 0
                frame = print_frame_with_tracker_marks(frame, trajectories, actual_frame[0], colors, position_clicked,
                                                       path_to_video_background, actualShowBB, actualShowBinaryFrame,
                                                       validateShowTrace, validateShowOnlyOneObject, new_position[0],
                                                       actualShowCandidateZone, actualShowErrorZone)

        if actual_frame[0] != actual_frame_validator:
            actual_frame_validator = actual_frame[0]
            cap.set(cv.CAP_PROP_POS_FRAMES, actual_frame[0])
            success, frame = cap.read()
            frame = print_frame_with_tracker_marks(frame, trajectories, actual_frame[0], colors, position_clicked,
                                                   path_to_video_background, actualShowBB, actualShowBinaryFrame,
                                                   validateShowTrace, validateShowOnlyOneObject, new_position[0],
                                                   actualShowCandidateZone, actualShowErrorZone)

        if cvui.button(window, width + 130, 1010, "Next NaN"):
            actual_frame[0] = find_next_nan(trajectories, actual_frame[0])
            cap.set(cv.CAP_PROP_POS_FRAMES, actual_frame[0])
            success, frame = cap.read()
            frame = print_frame_with_tracker_marks(frame, trajectories, actual_frame[0], colors, position_clicked,
                                                   path_to_video_background, actualShowBB, actualShowBinaryFrame,
                                                   validateShowTrace, validateShowOnlyOneObject, new_position[0],
                                                   actualShowCandidateZone, actualShowErrorZone)

        if cvui.button(window, width + 20, 125, "Switch"):

            switcher.switcher(trajectories, actual_frame[0], switch_object_1[0], switch_object_2[0])
            cap.set(cv.CAP_PROP_POS_FRAMES, actual_frame[0])
            success, frame = cap.read()
            frame = print_frame_with_tracker_marks(frame, trajectories, actual_frame[0], colors,
                                                   position_clicked, path_to_video_background, actualShowBB,
                                                   actualShowBinaryFrame, validateShowTrace, validateShowOnlyOneObject,
                                                   new_position[0], actualShowCandidateZone, actualShowErrorZone)

        if cvui.button(window, width + 20, 300, "Full New Position"):

            switcher.assign_new_position_to_fish(trajectories, actual_frame[0], new_position[0], position_clicked)
            cap.set(cv.CAP_PROP_POS_FRAMES, actual_frame[0])
            success, frame = cap.read()
            position_clicked[0] = 0
            position_clicked[1] = 0
            frame = print_frame_with_tracker_marks(frame, trajectories, actual_frame[0], colors, position_clicked,
                                                   path_to_video_background, actualShowBB, actualShowBinaryFrame,
                                                   validateShowTrace, validateShowOnlyOneObject, new_position[0],
                                                   actualShowCandidateZone, actualShowErrorZone)

        if cvui.button(window, width + 180, 300, "New &Position"):

            trajectories.data[actual_frame[0]][new_position[0]] = (int(position_clicked[0]), int(position_clicked[1]))
            cap.set(cv.CAP_PROP_POS_FRAMES, actual_frame[0])
            success, frame = cap.read()
            position_clicked[0] = 0
            position_clicked[1] = 0
            frame = print_frame_with_tracker_marks(frame, trajectories, actual_frame[0], colors, position_clicked,
                                                   path_to_video_background, actualShowBB, actualShowBinaryFrame,
                                                   validateShowTrace, validateShowOnlyOneObject, new_position[0],
                                                   actualShowCandidateZone, actualShowErrorZone)

        if cvui.button(window, width + 20, 900, "Play Automatic Assignation"):
            cap.set(cv.CAP_PROP_POS_FRAMES, actual_frame[0])
            play_automatic_assigantion = True

        if cvui.button(window, width + 170, 820, "Save"):
            trajectories.save_to_pickle()
            trajectories.save_to_csv()

        if cvui.button(window, width + 20, 820, "Post Processing"):
            pp.post_processing_execution(trajectories, config.get_variable("POST-PROCESSING", "algorithm"))

        cvui.counter(window, width + 20, 1015, actual_frame, 1)
        if cvui.button(window, width + 20, 950, "Play"):
            cap.set(cv.CAP_PROP_POS_FRAMES, actual_frame[0])
            play = True
        if cvui.button(window, width + 100, 950, "Pause"):
            if play or play_automatic_assigantion:
                actual_frame[0] = actual_frame[0] - 1
                actual_frame_validator = actual_frame[0]
            play = False
            play_automatic_assigantion = False

        if play:
            success, frame = cap.read()

            nans_arrar, same_position_array = rule_detection(trajectories, actual_frame[0])

            play = ((not stopIfNan[0]) or len(nans_arrar) == 0) and ((not stopIfSamePosition[0]) or len(same_position_array) == 0)

            frame = print_frame_with_tracker_marks(frame, trajectories, actual_frame[0], colors, position_clicked,
                                                   path_to_video_background, actualShowBB, actualShowBinaryFrame,
                                                   validateShowTrace, validateShowOnlyOneObject, new_position[0],
                                                   actualShowCandidateZone, actualShowErrorZone)

            if play:
                actual_frame[0] = actual_frame[0] + 1
                actual_frame_validator = actual_frame[0]

            if not cap.isOpened():
                play = False
                play_automatic_assigantion = False
                actual_frame[0] = actual_frame[0] - 1
                actual_frame_validator = actual_frame[0]
                trajectories.save_to_pickle()
                trajectories.save_to_csv()
                cap = cv.VideoCapture(path_to_video)
                cap.set(cv.CAP_PROP_POS_FRAMES, actual_frame[0])

        if play_automatic_assigantion:
            success, frame = cap.read()

            # @TODO: Unused variable 'binary_frame'
            binary_frame, new_tracking_objects = tpo.get_tracking_position_and_direction(frame,
                                                                                         path_to_video_background,
                                                                                         precision)

            switcher.assign_automatically(trajectories, actual_frame[0], new_tracking_objects,
                                          validateShowOnlyOneObject, validate_new_position, num_trackers)

            nans_arrar, same_position_array = rule_detection(trajectories, actual_frame[0])
                        
            # if(len(nans_arrar) != 0):
            #     for i, tracking_id in enumerate(nans_arrar):
            #         pp.post_processing_execution_with_fix_tracking_and_frames(trajectories, tracking_id, actual_frame[0] - 10 if actual_frame[0] - 10 >= 0 else 0, 
            #                                                                   actual_frame[0], config.get_variable("POST-PROCESSING", "algorithm"))
                
            #     switcher.assign_automatically(trajectories, actual_frame[0], new_tracking_objects,
            #                               validateShowOnlyOneObject, validate_new_position, num_trackers)
                                          
            # nans_arrar, jumps_array = rule_detection(trajectories, actual_frame[0])

            play_automatic_assigantion = ((not stopIfNan[0]) or len(nans_arrar) == 0) and ((not stopIfSamePosition[0])
                                                                                           or len(same_position_array) == 0)

            frame = print_frame_with_tracker_marks(frame, trajectories, actual_frame[0], colors,
                                                   position_clicked, path_to_video_background, actualShowBB,
                                                   actualShowBinaryFrame, validateShowTrace, validateShowOnlyOneObject,
                                                   new_position[0], actualShowCandidateZone, actualShowErrorZone)
            cvui.image(window, 4, 4, frame)

            if play_automatic_assigantion:
                actual_frame[0] = actual_frame[0] + 1
                actual_frame_validator = actual_frame[0]

            if not cap.isOpened():
                play = False
                play_automatic_assigantion = False
                actual_frame[0] = actual_frame[0] - 1
                actual_frame_validator = actual_frame[0]
                trajectories.save_to_pickle()
                trajectories.save_to_csv()
                cap = cv.VideoCapture(path_to_video)
                cap.set(cv.CAP_PROP_POS_FRAMES, actual_frame[0])

        cvui.imshow('MultiTracker', window)

        key = cv.waitKey(1)

        if key == 27:
            break
        if key == 110:
            actual_frame[0] = actual_frame[0] + 1
            cap.set(cv.CAP_PROP_POS_FRAMES, actual_frame[0])
            success, frame = cap.read()
            frame = print_frame_with_tracker_marks(frame, trajectories, actual_frame[0], colors, position_clicked,
                                                   path_to_video_background, actualShowBB, actualShowBinaryFrame,
                                                   validateShowTrace, validateShowOnlyOneObject, new_position[0],
                                                   actualShowCandidateZone, actualShowErrorZone)
        if key == 112:
            trajectories.data[actual_frame[0]][new_position[0]] = (int(position_clicked[0]), int(position_clicked[1]))
            cap.set(cv.CAP_PROP_POS_FRAMES, actual_frame[0])
            success, frame = cap.read()
            position_clicked[0] = 0
            position_clicked[1] = 0
            frame = print_frame_with_tracker_marks(frame, trajectories, actual_frame[0], colors, position_clicked,
                                                   path_to_video_background, actualShowBB, actualShowBinaryFrame,
                                                   validateShowTrace, validateShowOnlyOneObject, new_position[0],
                                                   actualShowCandidateZone, actualShowErrorZone)

        if key == 98:
            actual_frame[0] = actual_frame[0] - 1
            cap.set(cv.CAP_PROP_POS_FRAMES, actual_frame[0])
            success, frame = cap.read()
            frame = print_frame_with_tracker_marks(frame, trajectories, actual_frame[0], colors, position_clicked,
                                                   path_to_video_background, actualShowBB, actualShowBinaryFrame,
                                                   validateShowTrace, validateShowOnlyOneObject, new_position[0],
                                                   actualShowCandidateZone, actualShowErrorZone)

    cap.release()
    cv.destroyAllWindows()


def print_frame_with_tracker_marks(frame, trajectories, actualFrame, colors, lastClick, path_to_video_background,
                                   draw_BB, draw_BinaryFrame, validateShowTrace, validateShowOnlyOneObject, onlyObject,
                                   actualShowCandidateZone, showErrorZone, numFrames = 10):

    colorBB = (0, 0, 0)

    if draw_BB or draw_BinaryFrame:
        binary_frame, tracking_positions = tpo.get_tracking_position_and_direction(frame, path_to_video_background, Config().get_variable("TRACKING", "precision", 'int'))

        if draw_BinaryFrame:
            colorBB = (255, 255, 255)
            frame = binary_frame

        if draw_BB:
            for i, newbox in enumerate(tracking_positions):
                p1 = (int(newbox[0]), int(newbox[1]))
                p2 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
                cv.rectangle(frame, p1, p2, colorBB, 2)
                cv.putText(frame,   str(i), (int(p2[0] + 5), int(p2[1] + 5)), cv.FONT_HERSHEY_SIMPLEX, 0.5, colorBB, 2)

    if validateShowTrace:
        for f in range(0 if actualFrame < numFrames else actualFrame - numFrames, actualFrame):
            for i, point in enumerate(trajectories.get_frame(f)):
                if point[0] != -1:
                    if (not validateShowOnlyOneObject) or onlyObject == i:
                        cv.circle(frame, (int(point[0]), int(point[1])), 3, colors[i])

    for i, point in enumerate(trajectories.get_frame(actualFrame)):
        if point[0] != -1:
            if (not validateShowOnlyOneObject) or onlyObject == i:
                cv.circle(frame, (int(point[0]), int(point[1])), 3, colors[i])
                cv.putText(frame,   str(i), (int(point[0] + 5), int(point[1] + 5)), cv.FONT_HERSHEY_SIMPLEX, 0.5, colors[i], 2)
                if actualShowCandidateZone:
                    cv.circle(frame, (int(point[0]), int(point[1])), 20, colors[i])

    if actualFrame > 0:
        nans_arrar, jumps_array = rule_detection(trajectories, actualFrame)
        error_points = list(set(nans_arrar + jumps_array))
        if showErrorZone:
            old_frame = trajectories.get_frame(actualFrame-1)
            for i in error_points:
                cv.circle(frame, (int(old_frame[i][0]), int(old_frame[i][1])),
                          Config().get_variable("RULES", "max_dis_rule_front", 'int'), colors[i])

    cv.circle(frame, (int(lastClick[0]), int(lastClick[1])), 3, colorBB)
    cv.putText(frame, 'New Point', (int(lastClick[0] + 5), int(lastClick[1] + 5)), cv.FONT_HERSHEY_SIMPLEX, 0.5,
               colorBB, 2)
    return frame


if __name__ == '__main__':

    path_to_video = "../examples/Q5N40_A.avi"
    path_to_video_background = "../examples/Q25N_back.avi"
    #path_trajectories = "../workspace/Q5N40_A_clean/Q5N40_A_clean_2020-12-04_23-46-22.pickle"
    path_trajectories = "../workspace/Q5N40_A/Q5N40_A_2020-12-25_23-39-25.pickle"
    num_elements = 40

    analyze_video(path_to_video, path_to_video_background, path_trajectories, num_elements, 0)
