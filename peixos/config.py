import logging
import os
import time
from configparser import ConfigParser


def singleton(cls):
    instance = [None]

    def wrapper(*args, **kwargs):
        if instance[0] is None:
            instance[0] = cls(*args, **kwargs)
        return instance[0]

    return wrapper


@singleton
class Config:

    def load_conf(self) -> object:
        config = ConfigParser()
        config.read('peixos_conf.ini')

        return config

    def set_log(self, workspace_path: str, log_name: str):
        path_to_dump = workspace_path + "/log_files"
        if not os.path.exists(path_to_dump):
            os.makedirs(path_to_dump)
        logging.basicConfig(filename=workspace_path + '/log_files/{}.log'.format(log_name), filemode='w',
                            format='%(asctime)s - %(message)s', level=logging.INFO)

    def print_log(self, msg: str):
        if self.log:
            logging.info('{}'.format(msg))

    def get_variable(self, category: str, name: str, type: str = 'str') -> str:
        if type == "int":
            return self.config.getint(category, name)
        if type == "float":
            return self.config.getfloat(category, name)
        if type == "bool":
            return self.config.getboolean(category, name)
        return self.config.get(category, name)

    def __init__(self):
        log_name = "tracking_log_{}".format(time.strftime("%d_%m_%y_%H_%M"))
        self.config = self.load_conf()
        self.path_to_workspace = self.config.get('WORKSPACE', 'path_to_workspace')

        self.log = self.get_variable("WORKSPACE", "use_log", 'bool')
        if self.log:
            self.set_log(self.path_to_workspace, log_name)
        self.print_log('Path to workspace {}'.format(self.path_to_workspace))

    def get_workspace(self) -> str:
        return self.path_to_workspace

    def get_config(self) -> object:
        return self.config

    def put(self, category, name, value):
        self.config.set(category, name, value)


if __name__ == '__main__':

    config = Config()
