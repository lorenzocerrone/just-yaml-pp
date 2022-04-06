from jimmy.constructors.utils import generic_constructor
from jimmy.jimmy_dict import JimmyDict
from yaml import nodes
from datetime import datetime


def jimmy_constructor(loader, node):
    node_mapping = loader.construct_mapping(node)
    return JimmyDict(**node_mapping)


def time_stamp(*args):
    class TimeStamp:
        @staticmethod
        def apply(**kwargs):
            return datetime.now().strftime("%y_%m_%d_%H:%M:%S")

    return TimeStamp()


def join(loader, node):
    assert isinstance(node, nodes.SequenceNode)
    seq = generic_constructor(loader, node)
    return ''.join([str(i) for i in seq])
