import pathlib
from jimmy.constructors.utils import generic_constructor
from yaml import nodes


def join_paths(loader, node):
    assert isinstance(node, nodes.SequenceNode)
    seq = generic_constructor(loader, node)
    return_path = pathlib.Path()
    for path in seq:
        return_path = return_path / path
    return return_path


def home_path(*args, **kwargs):
    path = pathlib.Path('.')
    return path.home()


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

            if out_path.exists():
                ...
            return out_path

        def file_apply(self, experiment_key=None):
            out_path = self.current if experiment_key is None else self.current.parent / f'{self.current.stem}_' \
                                                                                         f'{experiment_key}' \
                                                                                         f'{self.current.suffix}'

            if out_path.exists():
                ...
            return out_path

    path = generic_constructor(loader, node, first_element=True)
    return UniquePath(path)


def make_absolute(loader, node):
    assert isinstance(node, nodes.ScalarNode) or isinstance(node, nodes.SequenceNode), \
        '"!make-absolute" is implemented only for ScalarNodes and SequenceNode.'

    path = generic_constructor(loader, node, first_element=True)
    path = pathlib.Path(path)
    return path.absolute()