import math
from config import Config

from utils.output_utils import OutputHandler
from utils import math_utils as mu

import matplotlib.pyplot as plt

def dotproduct(v1, v2):
    return sum((a * b) for a, b in zip(v1, v2))

def cos(v1, v2):
    
    if (mu.get_vector_length(v1) * mu.get_vector_length(v2)) != 0:
        return dotproduct(v1, v2) / (mu.get_vector_length(v1) * mu.get_vector_length(v2))
        
    return 0.2


def post_processing_execution(trajectories, post_processing_type='AVERAGE', save = True):
    if post_processing_type == 'AVERAGE':
        trajectories = execte_average_post_processing(trajectories)
        trajectories = execte_smooth_velocity_post_processing(trajectories)
        if(save):
            trajectories.save_to_pickle()
            trajectories.save_to_csv()

    if post_processing_type == 'ACUMULATE_AVERAGE':
        trajectories = execte_acumuate_average_post_processing(trajectories)
        if(save):
            trajectories.save_to_pickle()
            trajectories.save_to_csv()

    if post_processing_type == 'ACUMULATE_AVERAGE_WITH_SMOOTH':
        trajectories = execte_acumuate_average_post_processing(trajectories)
        trajectories = execte_smooth_velocity_post_processing(trajectories)
        trajectories = execte_acumuate_average_post_processing(trajectories)
        if(save):
            trajectories.save_to_pickle()
            trajectories.save_to_csv()
            
    return trajectories
        
def post_processing_execution_with_fix_tracking_and_frames(trajectories, tracking_id, start_frame, end_frame, post_processing_type='AVERAGE'):
    if post_processing_type == 'AVERAGE':
        trajectories = execte_average_post_processing_with_fix_tracking_and_frames(trajectories, tracking_id, start_frame, end_frame)
        trajectories = execte_smooth_velocity_post_processing_with_fix_tracking_and_frames(trajectories, tracking_id, start_frame, end_frame)

    if post_processing_type == 'ACUMULATE_AVERAGE':
        trajectories = execte_acumuate_average_post_processing_with_fix_tracking_and_frames(trajectories, tracking_id, start_frame, end_frame)
        trajectories = execte_smooth_velocity_post_processing_with_fix_tracking_and_frames(trajectories, tracking_id, start_frame, end_frame)


def execte_average_post_processing(trajectories):
    count_1_frame = 0
    count_2_frame = 0
    if len(trajectories.data) > 0:
        for trackingId in range(len(trajectories.data[0])):
            for frameId in range(2, len(trajectories.data) - 2):
                if trajectories.data[frameId][trackingId][0] != -1:
                    position_2_frames_ago = trajectories.data[frameId - 2][trackingId]
                    position_1_frames_ago = trajectories.data[frameId - 1][trackingId]
                    actual_position = trajectories.data[frameId][trackingId]
                    position_next_frame = trajectories.data[frameId + 1][trackingId]
                    position_next_2_frames = trajectories.data[frameId + 2][trackingId]

                    direction_between_old_positions = mu.get_vector_between_points(position_1_frames_ago,
                                                                                         position_2_frames_ago)
                    actual_direction = mu.get_vector_between_points(actual_position, position_1_frames_ago)
                    if cos(direction_between_old_positions, actual_direction) > 0.3:
                        continue

                    next_direction = mu.get_vector_between_points(position_next_frame, position_1_frames_ago)
                    if cos(direction_between_old_positions, next_direction) > 0.3:
                        count_1_frame = count_1_frame + 1
                        trajectories.data[frameId][trackingId] = (position_1_frames_ago[0] + next_direction[0] / 2,
                                                                  position_1_frames_ago[1] + next_direction[1] / 2)
                        continue

                    next_direction = mu.get_vector_between_points(position_next_2_frames, position_1_frames_ago)
                    if cos(direction_between_old_positions, next_direction) > 0.3:
                        count_2_frame = count_2_frame + 1
                        trajectories.data[frameId][trackingId] = (position_1_frames_ago[0] + next_direction[0] / 3,
                                                                  position_1_frames_ago[1] + next_direction[1] / 3)
                        continue

    print('NUM CHANGES 1 FRAME', count_1_frame)
    print('NUM CHANGES 2 FRAME', count_2_frame)
    return trajectories
    
def execte_average_post_processing_with_fix_tracking_and_frames(trajectories, tracking_id, start_frame, end_frame):
    count_1_frame = 0
    count_2_frame = 0
    if len(trajectories.data) > 0:
        for frameId in range(start_frame, end_frame - 2):
            if trajectories.data[frameId][tracking_id][0] != -1:
                position_2_frames_ago = trajectories.data[frameId - 2][tracking_id]
                position_1_frames_ago = trajectories.data[frameId - 1][tracking_id]
                actual_position = trajectories.data[frameId][tracking_id]
                position_next_frame = trajectories.data[frameId + 1][tracking_id]
                position_next_2_frames = trajectories.data[frameId + 2][tracking_id]

                direction_between_old_positions = mu.get_vector_between_points(position_1_frames_ago,
                                                                                     position_2_frames_ago)
                actual_direction = mu.get_vector_between_points(actual_position, position_1_frames_ago)
                if cos(direction_between_old_positions, actual_direction) > math.cos(math.radians(Config().get_variable("POST-PROCESSING", "degrees_error_position", 'int'))):
                    continue

                next_direction = mu.get_vector_between_points(position_next_frame, position_1_frames_ago)
                if cos(direction_between_old_positions, next_direction) >math.cos(math.radians(Config().get_variable("POST-PROCESSING", "degrees_error_position", 'int'))):
                    count_1_frame = count_1_frame + 1
                    trajectories.data[frameId][tracking_id] = (position_1_frames_ago[0] + next_direction[0] / 2,
                                                              position_1_frames_ago[1] + next_direction[1] / 2)
                    continue

                next_direction = mu.get_vector_between_points(position_next_2_frames, position_1_frames_ago)
                if cos(direction_between_old_positions, next_direction) > math.cos(math.radians(Config().get_variable("POST-PROCESSING", "degrees_error_position", 'int'))):
                    count_2_frame = count_2_frame + 1
                    trajectories.data[frameId][tracking_id] = (position_1_frames_ago[0] + next_direction[0] / 3,
                                                              position_1_frames_ago[1] + next_direction[1] / 3)
                    continue

    print('NUM CHANGES 1 FRAME', count_1_frame)
    print('NUM CHANGES 2 FRAME', count_2_frame)
    return trajectories

def execte_acumuate_average_post_processing(trajectories):
    
    count_frame = 0
    if len(trajectories.data) <= 0:
        return trajectories
        
    for trackingId in range(len(trajectories.data[0])):
                
        for frameId in range(2, len(trajectories.data) - 2):
            
            old_second_offset = 0
            
            position_2_frames_ago = trajectories.data[frameId - 2][trackingId]
            position_1_frames_ago = trajectories.data[frameId - 1][trackingId]
            
            direction_between_old_positions = mu.get_vector_between_points(position_1_frames_ago, position_2_frames_ago)
            
            while(mu.get_vector_length(direction_between_old_positions) == 0):
                old_second_offset = old_second_offset + 1
                position_2_frames_ago = trajectories.data[frameId - 2 - old_second_offset][trackingId]
                
                direction_between_old_positions = mu.get_vector_between_points(position_1_frames_ago, position_2_frames_ago)

            for offset in range(min(Config().get_variable("POST-PROCESSING", "num_frames_error_detected", 'int'), len(trajectories.data) - frameId)) :
                
                if trajectories.data[frameId + offset][trackingId][0] == -1:
                    continue
                
                actual_position = trajectories.data[frameId + offset][trackingId]
                actual_direction = mu.get_vector_between_points(actual_position, position_1_frames_ago)               
                
                if cos(direction_between_old_positions, actual_direction) > math.cos(math.radians(Config().get_variable("POST-PROCESSING", "degrees_error_position", 'int'))):
                        
                    count_frame = count_frame + offset
                    for section_id in range(offset):
                        trajectories.data[frameId + section_id][trackingId] = (
                        position_1_frames_ago[0] + (section_id + 1) * (actual_direction[0] / (offset + 1)),
                        position_1_frames_ago[1] + (section_id + 1) * (actual_direction[1] / (offset + 1)))

                    break

    print('NUM CHANGES FRAME', count_frame)
    return trajectories
    
def execte_acumuate_average_post_processing_with_fix_tracking_and_frames(trajectories, tracking_id, start_frame, end_frame):
    count_frame = 0
    if len(trajectories.data) > 0:
        acumulateError = 0
        backStep = False
        for frameId in range(start_frame, end_frame - 2):
            if trajectories.data[frameId][tracking_id][0] != -1:
                position_2_frames_ago = trajectories.data[frameId - (acumulateError + 2)][tracking_id]
                position_1_frames_ago = trajectories.data[frameId - (acumulateError + 1)][tracking_id]
                actual_position = trajectories.data[frameId][tracking_id]

                direction_between_old_positions = mu.get_vector_between_points(position_1_frames_ago, position_2_frames_ago)
                actual_direction = mu.get_vector_between_points(actual_position, position_1_frames_ago)
                
                if cos(direction_between_old_positions, actual_direction) > math.cos(math.radians(Config().get_variable("POST-PROCESSING", "degrees_error_position", 'int'))):
                    if acumulateError != 0:
                        count_frame = count_frame + acumulateError
                        for section_id in range(1, acumulateError + 1):
                            trajectories.data[frameId - (acumulateError + 1) + section_id][tracking_id] = (
                            position_1_frames_ago[0] + section_id * (actual_direction[0] / (acumulateError + 1)),
                            position_1_frames_ago[1] + section_id * (actual_direction[1] / (acumulateError + 1)))

                        acumulateError = 0

                    continue
                elif acumulateError > Config().get_variable("POST-PROCESSING", "num_frames_error_detected", 'int'):
                    if backStep and cos(direction_between_old_positions, actual_direction) > 0:
                        for section_id in range(1, acumulateError + 1):
                            trajectories.data[frameId - (acumulateError + 1) + section_id][tracking_id] = (
                            position_1_frames_ago[0] + section_id * (actual_direction[0] / (acumulateError + 1)),
                            position_1_frames_ago[1] + section_id * (actual_direction[1] / (acumulateError + 1)))
                
                    backStep = False
                    acumulateError = 0
                    continue
                else:
                    acumulateError = acumulateError + 1
                    continue

            else:
                acumulateError = acumulateError + 1

    print('NUM CHANGES FRAME', count_frame)
    return trajectories


def execte_smooth_velocity_post_processing(trajectories):

    if len(trajectories.data) > 0:
        for trackingId in range(len(trajectories.data[0])):
            for frameId in range(0, len(trajectories.data), Config().get_variable("POST-PROCESSING", "step_jumps", 'int')):
                velocity = 0
                number_frames_block = 0
                for frameBlockId in range(0, Config().get_variable("POST-PROCESSING", "step_block_average", 'int')):
                    if frameId + frameBlockId + 1 < len(trajectories.data):
                        initial = trajectories.data[frameId + frameBlockId][trackingId]
                        final = trajectories.data[frameId + frameBlockId + 1][trackingId]
                        if initial[0] != -1 and final[0] != -1:
                            velocity += mu.get_vector_length(mu.get_vector_between_points(final, initial))
                            number_frames_block += 1

                if number_frames_block == 0:
                    continue

                mid_velocity = velocity / number_frames_block

                old_initial = trajectories.data[frameId][trackingId]
                last_move = frameId

                for frameBlockId in range(0, Config().get_variable("POST-PROCESSING", "step_block_change", 'int')):
                    last_move = frameId + frameBlockId + 1
                    if frameId + frameBlockId + 1 < len(trajectories.data):
                        initial = trajectories.data[frameId + frameBlockId][trackingId]
                        final = trajectories.data[frameId + frameBlockId + 1][trackingId]
                        if initial[0] != -1 and final[0] != -1:
                            direction = mu.get_vector_between_points(final, old_initial)
                            size_vector = mu.get_vector_length(direction)
                            if size_vector == 0:
                                continue

                            direction = (direction[0] / size_vector, direction[1] / size_vector)
                            old_initial = final
                            trajectories.data[frameId + frameBlockId + 1][trackingId] = (initial[0] + direction[0] * mid_velocity, initial[1] + direction[1] * mid_velocity)

                if last_move < len(trajectories.data) - 1:
                    final = trajectories.data[last_move + 1][trackingId]
                    while old_initial[0] -1 < final[0] and old_initial[0] +1 > final[0] and old_initial[1] -1 < final[1] and old_initial[1] +1 > final[1]:
                        trajectories.data[last_move + 1][trackingId] = trajectories.data[last_move][trackingId]
                        last_move = last_move + 1
                        final = trajectories.data[last_move + 1][trackingId]
                        
    return trajectories
    
def execte_smooth_velocity_post_processing_with_fix_tracking_and_frames(trajectories, tracking_id, start_frame, end_frame):

    if len(trajectories.data) > 0:
        for frameId in range(start_frame, end_frame, Config().get_variable("POST-PROCESSING", "step_jumps", 'int')):
            velocity = 0
            number_frames_block = 0
            for frameBlockId in range(0, Config().get_variable("POST-PROCESSING", "step_block_average", 'int')):
                if frameId + frameBlockId + 1 < len(trajectories.data):
                    initial = trajectories.data[frameId + frameBlockId][tracking_id]
                    final = trajectories.data[frameId + frameBlockId + 1][tracking_id]
                    if initial[0] != -1 and final[0] != -1:
                        velocity += mu.get_vector_length((final[0] - initial[0], final[1] - initial[1]))
                        number_frames_block += 1

            if number_frames_block == 0:
                continue

            mid_velocity = velocity / number_frames_block

            for frameBlockId in range(0, Config().get_variable("POST-PROCESSING", "step_block_change", 'int')):
                if frameId + frameBlockId + 1 < len(trajectories.data):
                    initial = trajectories.data[frameId + frameBlockId][tracking_id]
                    final = trajectories.data[frameId + frameBlockId + 1][tracking_id]
                    if initial[0] != -1 and final[0] != -1:
                        direction = (final[0] - initial[0], final[1] - initial[1])
                        size_vector = mu.get_vector_length(direction)
                        if size_vector == 0:
                            continue

                        direction = (direction[0] / size_vector, direction[1] / size_vector)

                        trajectories.data[frameId + frameBlockId + 1][tracking_id] = (initial[0] + direction[0] * mid_velocity, initial[1] + direction[1] * mid_velocity)

    return trajectories
    
    
def create_plot(trajectories, num_points, num_trackers):
    
    for tracker in range(num_trackers):
        x = []
        y = []

        for frame in range(num_points):
            x.append(trajectories.data[frame][tracker][0])
            y.append(trajectories.data[frame][tracker][1])
            
        plt.plot(x, y, label = str(tracker), marker = "o")


if __name__ == '__main__':
    path_trajectories = "../workspace/tracking_Q5N40_A_2019-10-15_15-04-24_def_preprocessat.pickle"
    num_elements = 40
    
    trajectories = OutputHandler("../workspace", "", num_elements)
    trajectories.load_from_pickle(path_trajectories)
    
    create_plot(trajectories, 50, 5)
            
    plt.savefig('../workspace/plots/tracking_Q5N40_A_2019-10-15_15-04-24_def_preprocessat_figure.png')
    plt.clf()
    
    degrees_error_positions = [10, 20]
    num_frames_error_detected = [3, 5, 7]
    
    for degrees in degrees_error_positions:
        for error_frames in num_frames_error_detected:
            
            ##################################################            
            ####PRIMERA LLAMADA
            ################################################## 
            
            # CAMBIAR ANGULO
            # Config().put("POST-PROCESSING", "degrees_error_position", str(degrees))
            Config().put("POST-PROCESSING", "degrees_error_position", str('120'))
            
            Config().put("POST-PROCESSING", "num_frames_error_detected", str(error_frames))

            trajectories = OutputHandler("../workspace", 'Q5N40_degrees_' + str(degrees) + '_error_frames_' + str(error_frames) + '_before_120' , num_elements)
            trajectories.load_from_pickle(path_trajectories)
            
            result_trajectories = post_processing_execution(trajectories, 'ACUMULATE_AVERAGE', False)
            
            ##################################################            
            ####SEGUNDA LLAMADA
            ##################################################            

            # CAMBIAR ANGULO
            Config().put("POST-PROCESSING", "degrees_error_position", str(degrees))
            # Config().put("POST-PROCESSING", "degrees_error_position", str('90'))
            
            result_trajectories = post_processing_execution(trajectories, 'ACUMULATE_AVERAGE', False)
            
            result_trajectories.save_to_pickle()
            result_trajectories.save_to_csv()
            
            create_plot(result_trajectories, 50, 5)
            
            plt.savefig('../workspace/plots/Q5N40_degrees_' + str(degrees) + '_error_frames_' + str(error_frames) + '_before_120_figure.png')
            plt.clf()
