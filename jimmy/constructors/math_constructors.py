from jimmy.constructors.utils import generic_constructor
from yaml import nodes
import numpy as np


def sum_nodes(loader, node):
    assert isinstance(node, nodes.SequenceNode)
    seq = generic_constructor(loader, node)
    return sum(seq)


def build_range(loader, node):
    assert isinstance(node, nodes.SequenceNode)
    seq = generic_constructor(loader, node)
    seq = [s if not isinstance(s, str) else float(s) for s in seq]
    return np.arange(*seq).tolist()


def build_log_space(loader, node):
    assert isinstance(node, nodes.SequenceNode)
    seq = generic_constructor(loader, node)
    seq = [s if not isinstance(s, str) else float(s) for s in seq]
    return np.logspace(*seq).tolist()


def build_lin_space(loader, node):
    assert isinstance(node, nodes.SequenceNode)
    seq = generic_constructor(loader, node)
    seq = [s if not isinstance(s, str) else float(s) for s in seq]
    return np.linspace(*seq).tolist()