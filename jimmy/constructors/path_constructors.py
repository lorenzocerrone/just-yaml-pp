import pathlib
from jimmy.constructors.utils import generic_constructor, build_check_sequential
from yaml import nodes


def _join_paths(seq: list[str]):
    return_path = pathlib.Path()
    for path in seq:
        return_path = return_path / path
    return return_path


def join_paths(loader, node):
    seq = build_check_sequential(loader, node)
    return _join_paths(seq)


def join_paths_glob(loader, node):
    seq = build_check_sequential(loader, node)
    return_path = _join_paths(seq[:-1])
    return list(return_path.glob(seq[-1]))


def home_path(*args, **kwargs):
    path = pathlib.Path('.')
    return path.home()


def here_path(*args, path=None, **kwargs):
    path = pathlib.Path(path)
    return path.absolute().parent


def _recurrent_unique_path(path: pathlib.Path, idx: int = 1, ignore_name=None):
    if not path.exists():
        return path

    identifier = f'_v{idx}'

    if ignore_name is None:
        new_path = path.parent / f'{path.stem}{identifier}{path.suffix}'
    else:
        new_path = path.parent.parent / f'{path.parent.name}{identifier}' / path.name

    if new_path.exists():
        return _recurrent_unique_path(path, idx + 1, ignore_name=ignore_name)
    else:
        return new_path


def unique_path(loader, node):
    assert isinstance(node, nodes.ScalarNode) or isinstance(node, nodes.SequenceNode)

    class UniquePath:
        def __init__(self, current):
            self.current = pathlib.Path(current)

        def apply(self, experiment_key=None, **kwargs):
            if self.current.suffix == '':
                return self.dir_apply(experiment_key=experiment_key)
            else:
                return self.file_apply(experiment_key=experiment_key)

        def dir_apply(self, experiment_key=None):
            out_path = self.current if experiment_key is None else self.current / experiment_key
            return _recurrent_unique_path(out_path, ignore_name=experiment_key)

        def file_apply(self, experiment_key=None):
            out_path = self.current if experiment_key is None else self.current.parent / f'{self.current.stem}_' \
                                                                                         f'{experiment_key}' \
                                                                                         f'{self.current.suffix}'
            return _recurrent_unique_path(out_path, ignore_name=experiment_key)

    path = generic_constructor(loader, node, first_element=True)
    return UniquePath(path)


def make_absolute(loader, node):
    path = make_path(loader, node)
    return path.absolute()


def make_path(loader, node):
    assert isinstance(node, nodes.ScalarNode) or isinstance(node, nodes.SequenceNode), \
        '"!make-path" is implemented only for ScalarNodes and SequenceNode.'
    path = generic_constructor(loader, node, first_element=True)
    path = pathlib.Path(path)
    return path
