from collections.abc import Mapping
import copy
from dataclasses import asdict, is_dataclass, dataclass
from typing import Union


class JimmyMap(Mapping):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self, out_str='JimmyMap'):
        divider = '; '
        out_str = f'{out_str}('
        for key, values in self.to_dict().items():
            if isinstance(values, JimmyMap):
                values = 'JimmyMap(**)'
            out_str += f'{key}={values}{divider}'

        out_str = out_str[:-len(divider)] + ')'
        return out_str

    def to_dict(self):
        if is_dataclass(self):
            return asdict(self)
        return self.__dict__

    def pop(self, key: str):
        return self.to_dict().pop(key)

    def __setitem__(self, *args):
        if is_dataclass(self):
            raise NotImplementedError('__setitem__ is not implemented for dataclasses')

        key, *values = args
        setattr(self, key, *values)

    def __getitem__(self, key):
        return getattr(self, key)

    def __contains__(self, item):
        return True if item in self.to_dict() else False

    def __iter__(self):
        return iter(self.to_dict().keys())

    def __len__(self):
        return len(self.to_dict())


def to_jimmy_dataclass(cls: JimmyMap, slots=True, frozen=True):
    return dataclass(slots=slots, frozen=frozen)(cls)


def split_jimmy_map(jmap, key='jimmy'):
    j_dict = copy.copy(jmap.to_dict())
    popped_dict = j_dict.pop(key)
    return JimmyMap(**j_dict), JimmyMap(**popped_dict)


GenericDict = Union[JimmyMap, dict]


class Configurator(JimmyMap):
    name: str
    kwargs: GenericDict

    def __init__(self, name: str, kwargs: JimmyMap = None):
        kwargs = kwargs if kwargs is not None else JimmyMap()

        super().__init__(name=name, kwargs=kwargs)
        assert hasattr(self, 'name'), "'name' arguments not found in config"
        assert isinstance(self.name, str), "'name' must be a string"

        assert hasattr(self, 'kwargs'), "'kwargs' arguments not found in config"
        assert isinstance(self.kwargs, JimmyMap) or isinstance(self.kwargs, dict), \
            "'kwargs' must be a either a JimmyMap or a dict"

    def __repr__(self, out_str='Configurator'):
        return super().__repr__(out_str=out_str)

    def configure(self, available_options: GenericDict):
        return available_options[self.name](**self.kwargs)
