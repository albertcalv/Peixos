# -*- coding: utf-8 -*-
import pickle
import datetime
import os


class OutputHandler:

    def __init__(self, path_to_workspace: str, id_job: str, num_trackers: int):
        self.path_to_workspace = path_to_workspace
        self.id_job = id_job
        self.path_to_save_data = self.path_to_workspace + "/" + str(self.id_job)
        if not os.path.exists(self.path_to_save_data):
            os.makedirs(self.path_to_save_data)

        self.num_trackers = num_trackers
        self.data = []

    def add_frame(self, frame: list, frame_position: int = -1):
        """
        Insert a new frame in data structure
        :param frame : Frame to insert
        :param frame_position: Position to insert the frame, if argument is empty is inserted at the end optional)
        """
        if frame_position == -1:
            self.data += [frame]

        elif frame_position < len(self.data):
            self.data[frame_position] = frame

        else:
            self.create_data_to_limit(frame_position + 1)
            self.data[frame_position] = frame

    def get_frame(self, frame_position: int):
        self.create_data_to_limit(frame_position + 1)
        return self.data[frame_position]

    def change_position_frame(self, frame_position: int, id_tracking: int, position):
        self.create_data_to_limit(frame_position)
        self.data[frame_position][id_tracking] = position

    def save_to_csv(self, frame_id: int = -1):
        if frame_id == -1 or frame_id % 10 == 0:
            columns_csv = ["Frame", "ID_Element", "X_axis", "Y_axis"]
            path_to_file = "{}/{}_{}.csv".format(self.path_to_save_data, self.id_job,
                                                 datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))

            f = open(path_to_file, 'w')
            f.write(','.join(str(x) for x in columns_csv) + " \n")
            for idx_frame, frame in enumerate(self.data):
                for idx_element, element in enumerate(frame):
                    f.write("{}, {}, {}, {} \n".format(idx_frame, idx_element, element[0], element[1]))

            print("[DEBUG] Save into {}".format(path_to_file))

    def load_from_pickle(self, path_to_file: str):
        self.data = pickle.load(open(path_to_file, "rb"))
        print("[DEBUG] Loaded data picke {}".format(path_to_file))

    def save_to_pickle(self, frame_id: int = -1) -> str:
        if frame_id == -1 or frame_id % 10 == 0:
            path_to_file = "{}/{}_{}.pickle".format(self.path_to_save_data, self.id_job,
                                                    datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
            pickle.dump(self.data, open(path_to_file, "wb"))
            print("[DEBUG] Save into {}".format(path_to_file))
            return path_to_file

    def create_data_to_limit(self, limit: int):
        if limit > len(self.data):
            # @TODO : Unused variable 'f'
            for f in range(len(self.data), limit):
                self.data += [list(map(lambda x: (-1, -1), range(0, self.num_trackers)))]


if __name__ == '__main__':

    data = [[(22.9493, 43.5393), (12.9493, 44.5393), (12.9493, 94.5393), (82.9493, 41.5393), (22.9493, 44.593)],
            [(22.9493, 43.5393), (12.9493, 44.5393), (12.9493, 94.5393), (82.9493, 41.5393), (22.9493, 44.593)],
            [(22.9493, 43.5393), (12.9493, 44.5393), (12.9493, 94.5393), (82.9493, 41.5393), (22.9493, 44.593)]]
    single_frame = [(22, 22), (22, 22), (22, 22), (22, 22), (22, 22)]

    path_to_workspace = "../../workspace"
    id_job = "peixos_unit_test"

    oh = OutputHandler(path_to_workspace, id_job, 10)
    oh.data = data
    oh.save_to_pickle()
    oh.save_to_csv()

    oh.load_from_pickle(path_to_workspace + "/peixos_unit_test_frame_3.pickle")
