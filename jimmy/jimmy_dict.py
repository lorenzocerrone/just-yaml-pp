from collections.abc import Mapping
from dataclasses import asdict, is_dataclass, dataclass


class JimmyMap(Mapping):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def _as_dict(self):
        if is_dataclass(self):
            return asdict(self)
        return self.__dict__

    def __setitem__(self, *args):
        if is_dataclass(self):
            raise NotImplementedError('__setitem__ is not implemented for dataclasses')

        key, *values = args
        setattr(self, key, *values)

    def __getitem__(self, key):
        return getattr(self, key)

    def __iter__(self):
        return iter(self._as_dict().keys())

    def __len__(self):
        return len(self._as_dict())


def jimmy_dataclass(cls: JimmyMap, slots=True, frozen=True):
    return dataclass(slots=slots, frozen=frozen)(cls)
