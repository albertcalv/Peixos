import pickle

import math
import numpy as np
from config import Config
from utils import math_utils as mu
import post_processing as pp


def switcher(trajectories_data, frame, object_1, object_2):

    for f in range(frame, len(trajectories_data.data)):
        actual_trajectori = trajectories_data.get_frame(f)

        temporal_object_1 = actual_trajectori[object_1]
        actual_trajectori[object_1] = actual_trajectori[object_2]
        actual_trajectori[object_2] = temporal_object_1

        trajectories_data.add_frame(actual_trajectori, f)

    return trajectories_data


def assign_new_position_to_fish(trajectories_data, frame, fish_number, new_position, reverse=False):

    init = frame+1
    final = len(trajectories_data.data)
    if reverse:
        init = 0
        final = frame

    for f in range(init, final):
        actual_trajectori = trajectories_data.get_frame(f)
        actual_trajectori[fish_number] = (-1, -1)
        trajectories_data.add_frame(actual_trajectori, f)

    actual_trajectori = trajectories_data.get_frame(frame)
    actual_trajectori[fish_number] = (int(new_position[0]), int(new_position[1]))
    trajectories_data.add_frame(actual_trajectori, frame)

    return trajectories_data


def get_positions(new_tracking_objects: list) -> list:
    positions = []

    # @TODO : Consider using enumerate instead of iterating with range and len
    for i in range(len(new_tracking_objects)):
        bounding_box = new_tracking_objects[i]
        positions.append((bounding_box[0] + bounding_box[2]/2,bounding_box[1] + bounding_box[3]/2))

    return positions


def get_estimated_position(diff_2_1, position_reference,diff_real1_estimated1):
    # diff_2_1 corresponds to the difference between fish t-2 and fish t-1
    # position_reference corresponds to the position at fish t-1
    # diff_real1_estimated1 corresponds to the error of the estimated position at t-1 (i.e. the
    #       difference between the real estimation t-1 and the estimated position at t-1)
    # we want to estimate the position at t
    return (position_reference[0] + diff_2_1[0] - diff_real1_estimated1[0],
                                             position_reference[1] + diff_2_1[1] - diff_real1_estimated1[1])


def get_candidates_information(frame: int, num_elements: int, positions: list, trajectories_data: list,
                               one_fish: bool, id_fish: int) -> dict:

    config = Config()

    dis_rule_inner = config.get_variable("RULES", "dis_rule_inner", 'int')
    max_dis_rule_inner = config.get_variable("RULES", "max_dis_rule_inner", 'int')
    dis_rule_behind = config.get_variable("RULES", "dis_rule_behind", 'int')
    max_dis_rule_behind = config.get_variable("RULES", "max_dis_rule_behind", 'int')
    dis_rule_front = config.get_variable("RULES", "dis_rule_front", 'int')
    max_dis_rule_front = config.get_variable("RULES", "max_dis_rule_front", 'int')

    front_angle = config.get_variable("RULES", "front_angle", 'int')
    behind_angle = config.get_variable("RULES", "behind_angle", 'int')

    front_rule_active = config.get_variable("RULES", "front_rule", 'bool')
    inner_rule_active = config.get_variable("RULES", "inner_rule", 'bool')
    behind_rule_active = config.get_variable("RULES", "behind_rule", 'bool')

    direct = -1
    candidates_information = {}
    
    if frame <= 0:
        return candidates_information
    
    for fish_number in range(num_elements):
        if not one_fish or (one_fish and id_fish == fish_number):
            if trajectories_data.get_frame(frame+direct)[fish_number][0] != -1 and trajectories_data.get_frame(frame)[fish_number][0] == -1:
                candidates_information[fish_number] = {}
                
                position_reference, previousPosition_t2, estimatedPosition = \
                    get_fish_information_from_previous_frames(trajectories_data, fish_number, frame, direct)
                
                distances = get_distances_to_reference_position(positions, position_reference)

                min_dis = min(distances)
                
                total_front_rule = False
                total_behind_rule = False
                total_inner_rule = False

                # @TODO: Consider using enumerate instead of iterating with range and len
                for j in range(len(distances)):

                    v1 = np.array(position_reference) - np.array(previousPosition_t2)
                    v0 = np.array(positions[j]) - np.array(position_reference)
                    angle = math.degrees(abs(np.math.atan2(np.linalg.det([v0, v1]), np.dot(v0, v1))))

                    front_rule = front_rule_active and distances[j] < min((min_dis + dis_rule_front), max_dis_rule_front) \
                                 and angle < front_angle
                    behind_rule = behind_rule_active and distances[j] < min((min_dis + dis_rule_behind), max_dis_rule_behind) \
                                  and angle > behind_angle
                    inner_rule = inner_rule_active and distances[j] < min((min_dis + dis_rule_inner), max_dis_rule_inner)
                    
                    total_front_rule = total_front_rule or front_rule
                    total_behind_rule = total_behind_rule or behind_rule
                    total_inner_rule = total_inner_rule or inner_rule

                    if inner_rule or behind_rule or front_rule:
                        candidates_information[fish_number][j] = [distances[j], angle, None, [front_rule, inner_rule, behind_rule]]

                        if frame >= 3:
                            candidates_information[fish_number][j][2] = \
                                mu.get_vector_length(mu.get_vector_between_points(positions[j], estimatedPosition))
                                
                if (not total_front_rule) and (total_behind_rule or total_inner_rule):
                                        
                    candidates_information[fish_number] = {}
                    
                    # pp.post_processing_execution_with_fix_tracking_and_frames(trajectories_data, fish_number, frame - 10 if frame - 10 > 0 else 0, 
                    #                                                           frame, config.get_variable("POST-PROCESSING", "algorithm"))
                    
                    for j in range(len(distances)):

                        v1 = np.array(position_reference) - np.array(previousPosition_t2)
                        v0 = np.array(positions[j]) - np.array(position_reference)
                        angle = math.degrees(abs(np.math.atan2(np.linalg.det([v0, v1]), np.dot(v0, v1))))
    
                        front_rule = front_rule_active and distances[j] < min((min_dis + dis_rule_front), max_dis_rule_front) \
                                     and angle < front_angle
                        behind_rule = behind_rule_active and distances[j] < min((min_dis + dis_rule_behind), max_dis_rule_behind) \
                                      and angle > behind_angle
                        inner_rule = inner_rule_active and distances[j] < min((min_dis + dis_rule_inner), max_dis_rule_inner)
    
                        if inner_rule or behind_rule or front_rule:
                            candidates_information[fish_number][j] = [distances[j], angle, None, [front_rule, inner_rule, behind_rule]]
    
                            if frame >= 3:
                                candidates_information[fish_number][j][2] = \
                                    mu.get_vector_length(mu.get_vector_between_points(positions[j], estimatedPosition))
    

    return candidates_information

def get_fish_information_from_previous_frames(trajectories_data, fish_number, frame, direction):
    position_from_previous_frame = trajectories_data.get_frame(frame + direction)[fish_number]
    if frame >= 3:
        position_from_two_previous_frame = trajectories_data.get_frame(frame + direction * 2)[fish_number]  # t-2
        position_from_three_previous_frame = trajectories_data.get_frame(frame + direction * 3)[fish_number]  # t-3

        diff_3_2 = mu.get_vector_between_points(position_from_two_previous_frame, position_from_three_previous_frame)
        estimated_1 = mu.add_vector_to_point(position_from_two_previous_frame, diff_3_2)
        # estimated_1 corresponds to the estimated position at t-1
        diff_real1_estimated1 = mu.get_vector_between_points(position_from_previous_frame, estimated_1)
        # diff_real1_estimated1 corresponds to the difference between estimated_1
        # and the real position at t-1. It is the error
        diff_2_1 = mu.get_vector_between_points(position_from_previous_frame, position_from_two_previous_frame)
        estimatedPosition = get_estimated_position(diff_2_1, position_from_previous_frame, diff_real1_estimated1)
        
        return position_from_previous_frame, position_from_two_previous_frame, estimatedPosition
    
def get_distances_to_reference_position(positions, position_reference):
    distances = []
    for positions_BB in positions:
        distances.append(mu.get_vector_length(mu.get_vector_between_points(positions_BB, position_reference)))
                                    
    return distances

def score_individual(feat_list: list, min_max_values: list) -> int:

    distance = True
    angle = False
    estimated_distance = True

    score = 0
    if distance:
        score += (feat_list[0] - min_max_values[0][0]) / (min_max_values[0][1] - min_max_values[0][0])
    if angle:
        score += (feat_list[1] - min_max_values[1][0]) / (min_max_values[1][1] - min_max_values[1][0])
    if estimated_distance:
        score += (feat_list[2] - min_max_values[2][0]) / (min_max_values[2][1] - min_max_values[2][0])
    return score


def get_score_list(candidates: dict, min_max_values: list) -> set:
    score_items = set()
    for id_element, feat_list in candidates.items():
        score_item = score_individual(feat_list, min_max_values)
        score_items.add((id_element, score_item))
    return score_items


def remove_duplicates_already_assigned(list_of_keys: list, candidates_score: list) -> list:
    list_of_keys_set = set(list_of_keys)

    aux_candidates_score = []
    for element in candidates_score:
        if element[0] not in list_of_keys_set:
            aux_candidates_score += [element]

    return aux_candidates_score


def select_best_assignation_by_minimum_estimate_candidate(num_elements, candidates_information):

    closest_assignations = [-1]*num_elements

    for num_fish, fish_candidate_information in candidates_information.items():
        closest_assignations[num_fish] = find_min_estimate_distance_candidate(fish_candidate_information)

    return closest_assignations


def find_min_estimate_distance_candidate(fish_candidate_information):
    best_candidate = -1
    best_distance = -1

    for candidate_id, information in fish_candidate_information.items():
        if best_candidate == -1 or best_distance > information[2]:
            best_candidate = candidate_id
            best_distance = information[2]

    return best_candidate


def find_fish_with_one_candidate(candidates_information):
    for candidate_id, information in candidates_information.items():
        if len(information) == 1:
            return candidate_id

    return None


def delete_BB_from_candidates(candidates_information, bounding_box):
    for fish in candidates_information:
        candidates_information[fish].pop(bounding_box, None)


def assign_fishes_with_only_one_candidate(frame, candidates_information, positions, trajectories_data):
    alone_fish = find_fish_with_one_candidate(candidates_information)

    while alone_fish:
        trajectories_data.change_position_frame(frame, alone_fish, positions[list(candidates_information[alone_fish].keys())[0]])
    
        # if not candidates_information[alone_fish][list(candidates_information[alone_fish].keys())[0]][3][0]:
        #    pp.post_processing_execution_with_fix_tracking_and_frames(trajectories_data, alone_fish, frame - 10 if frame - 10 > 0 else 0, 
        #                                                       frame, Config().get_variable("POST-PROCESSING", "algorithm"))
 
        
        delete_BB_from_candidates(candidates_information, list(candidates_information[alone_fish].keys())[0])
        candidates_information.pop(alone_fish, None)

        alone_fish = find_fish_with_one_candidate(candidates_information)


def assign_empty_elements(best_assignation, frame, candidates_information, positions, trajectories_data):

    for fish_id, information in candidates_information.items():
        if information == {} and best_assignation[fish_id] != -1:
            trajectories_data.change_position_frame(frame, fish_id, positions[best_assignation[fish_id]])


def find_best_fish_and_bb_in_candidates(candidates_information):
    best_fish = -1
    best_bb = -1
    best_distance_estimate = -1
    best_rules = []

    for fish_id, information in candidates_information.items():
        for bb_id, information_fish_bb in information.items():
            if best_fish == -1 or best_distance_estimate > information_fish_bb[2]:
                best_fish = fish_id
                best_bb = bb_id
                best_distance_estimate = information_fish_bb[2]
                best_rules = information_fish_bb[3]

    return best_fish, best_bb, best_rules


def assign_minimum_estimate_candidates(frame, candidates_information, positions, trajectories_data):
    best_fish, best_bb, best_rules = find_best_fish_and_bb_in_candidates(candidates_information)

    while best_fish != -1:
        trajectories_data.change_position_frame(frame, best_fish, positions[best_bb])
        
        # if not best_rules[0]:
        #     pp.post_processing_execution_with_fix_tracking_and_frames(trajectories_data, best_fish, frame - 10 if frame - 10 > 0 else 0, 
        #                                                               frame, Config().get_variable("POST-PROCESSING", "algorithm"))
 
        delete_BB_from_candidates(candidates_information, best_bb)
        candidates_information.pop(best_fish, None)

        best_fish, best_bb, best_rules = find_best_fish_and_bb_in_candidates(candidates_information)


def assign_best_candidate(frame: int, num_elements: int, candidates_information: dict, positions: list, trajectories_data):

    # Array with best assignations, each position saves the assignation for the element i-th
    best_assignation = select_best_assignation_by_minimum_estimate_candidate(num_elements, candidates_information)

    assign_fishes_with_only_one_candidate(frame, candidates_information, positions, trajectories_data)

    assign_minimum_estimate_candidates(frame, candidates_information, positions, trajectories_data)

    assign_empty_elements(best_assignation, frame, candidates_information, positions, trajectories_data)


def assign_automatically(trajectories_data, frame, new_tracking_objects, one_fish=False, id_fish=None,
                         num_elements: int = 40, reverse=False):

    # Get Positions for each new tracking object
    positions = get_positions(new_tracking_objects)

    # Get Candidates information for each element are calculated candidates with the following information
    # [0] Distance: proximity to the new element
    # [1] Angle : proximity to the new element
    # [2] Distance Estimated
    # [3] Norm diff real estimated:  diff between real t-1 and estimated t-1
    # [4] Norm diff: t-3 t-2, if t is the present where assignations are done
    candidates_information = get_candidates_information(frame, num_elements, positions, trajectories_data,
                                                        one_fish, id_fish)

    # Assign best candidate for each element
    assign_best_candidate(frame, num_elements, candidates_information, positions, trajectories_data)


if __name__ == '__main__':

    num_elements = 40
    frame = 28

    candidates_information = pickle.load(open("candidates_information_28.pickle", "rb"))
    positions = pickle.load(open("positions_28.pickle", "rb"))
    trajectories_data = pickle.load(open("trajectories_data_28.pickle", "rb"))

    assign_best_candidate(frame, num_elements, candidates_information, positions, trajectories_data)
