import ui_validation as ui
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--path_to_video', default=False, required=True, type=str, help='Path to video')
    parser.add_argument('--path_to_video_back', default=False, required=True, type=str, help='Path to Background video')
    parser.add_argument('--path_to_trajectories', default=False, required=False, type=str, help='Path to trajectories')
    parser.add_argument('--num_of_elements', default=False, required=True, type=int, help='Num of elements')

    args = parser.parse_args()
    path_to_video = args.path_to_video
    path_to_video_background = args.path_to_video_back
    path_trajectories = args.path_to_trajectories
    num_of_elements = args.num_of_elements



    ui.analyze_video(path_to_video, path_to_video_background, path_trajectories, num_of_elements, 0)
