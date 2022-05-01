import configparser
import os
from typing import List

config = configparser.ConfigParser()


def _create_default_path_list(file_name: str) -> List[str]:
    starting_dir = os.path.dirname(__file__)
    return [
        os.path.join("config", file_name),
        os.path.join(starting_dir, file_name),
        os.path.join("config_private", file_name),
    ]


def load_config(path_list=None) -> List[str]:
    if path_list is None:
        path_list = _create_default_path_list("config.ini")
    return config.read(path_list)


load_config()


def read_config(section: str, value: str, raw: bool = False) -> str:
    return config.get(section, value, raw=raw)
