from jimmy.constructors.utils import build_check_sequential
import numpy as np


def sum_nodes(loader, node):
    seq = build_check_sequential(loader, node)
    return sum(seq)


def build_range(loader, node):
    seq = build_check_sequential(loader, node, expected_len=3)
    seq = [s if not isinstance(s, str) else float(s) for s in seq]
    return np.arange(*seq).tolist()


def build_log_space(loader, node):
    seq = build_check_sequential(loader, node, expected_len=3)
    seq = [s if not isinstance(s, str) else float(s) for s in seq]
    return np.logspace(*seq).tolist()


def build_lin_space(loader, node):
    seq = build_check_sequential(loader, node, expected_len=3)
    seq = [s if not isinstance(s, str) else float(s) for s in seq]
    return np.linspace(*seq).tolist()
