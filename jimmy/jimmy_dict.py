from collections import UserDict


class JimmyDict(UserDict):
    def __setitem__(self, *args):
        key, *values = args
        self.__setattr__(key, *values)
        super().__setitem__(*args)