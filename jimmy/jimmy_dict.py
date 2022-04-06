from collections import UserDict


class JimmyDict(UserDict):
    def __setitem__(self, *args):
        key, *values = args
        if key == 'data':
            raise ValueError('"data" is a reserved key, please use a different name.')

        self.__setattr__(key, *values)
        super().__setitem__(*args)
