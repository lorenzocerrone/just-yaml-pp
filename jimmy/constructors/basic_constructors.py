from datetime import datetime

from jimmy.constructors.utils import build_check_sequential
from jimmy.jimmy_map import JimmyMap, Configurator


def jimmy_constructor(loader, node):
    node_mapping = loader.construct_mapping(node)
    return JimmyMap(**node_mapping)


def jimmy_configurator_constructor(loader, node):
    node_mapping = loader.construct_mapping(node)
    return Configurator(**node_mapping)


def time_stamp(*args):
    class TimeStamp:
        @staticmethod
        def apply(**kwargs):
            return datetime.now().strftime("%y_%m_%d_%H:%M:%S")

    return TimeStamp()


def join(loader, node):
    seq = build_check_sequential(loader, node)
    return ''.join([str(i) for i in seq])
