from jimmy.jimmy_map import JimmyMap
from enum import Enum
from typing import Callable


def failed_exist(**kwargs):
    return ValueError(f'{kwargs["key"]} does not exists in {kwargs["test_obj"]}')


def failed_type(**kwargs):
    return ValueError(f'{kwargs["key"]} requires type {kwargs["annotation"]}, '
                      f'but was given {type(kwargs["test_obj"][kwargs["key"]])}')


def failed_test(**kwargs):
    return ValueError(f'tests failed for key: {kwargs["key"]}, results: {kwargs["results"]}')


class Validation(Enum):
    SUCCESS = True
    FAILED_EXIST = failed_exist
    # FAILED_TYPE =  failed_type
    FAILED_TEST = failed_test


class ObjectValidator:
    def __init__(self, key, annotation: type = None, tests: list[Callable] = None):
        self.key = key
        self.annotation = annotation
        self.tests = tests

    def verify(self, test_obj: JimmyMap):
        # verify type is not yet implemented
        self.verify_exist(test_obj)
        self.run_tests(test_obj)

    def verify_exist(self, test_obj: JimmyMap) -> Validation:
        if hasattr(test_obj, self.key):
            return Validation.SUCCESS

        raise Validation.FAILED_EXIST(key=self.key, test_obj=test_obj)

    def verify_type(self, test_obj: JimmyMap) -> Validation:
        if self.annotation is None:
            return Validation.SUCCESS

        if isinstance(test_obj[self.key], self.annotation):
            return Validation.SUCCESS

        raise Validation.FAILED_TYPE(key=self.key, annotation=self.annotation, test_obj=test_obj)

    def run_tests(self, test_obj: JimmyMap) -> Validation:
        if self.tests is None:
            return Validation.SUCCESS
        results = [test(test_obj[self.key]) for test in self.tests]

        if all(results):
            return Validation.SUCCESS

        raise Validation.FAILED_TEST(key=self.key, results=results)


def jimmy_validator(validator_cls):
    class JimmyValidator:
        _name = validator_cls.__name__
        _not_initialized = True

        def __init__(self):

            self._tests = {}
            for key, value in validator_cls.__dict__.items():
                if key.find('__') != 0:
                    if isinstance(value, Callable):
                        self._tests[key] = [value]
                    elif isinstance(value, list) and all([isinstance(c, Callable) for c in value]):
                        self._tests[key] = value
                    else:
                        raise ValueError(
                            'value for JimmyValidator Objects must be either None '
                            '(not defined) or a callable test or a list of callable tests')

            self.__annotations__ = validator_cls.__annotations__
            self._validators = {}
            for key, value in self.__annotations__.items():
                setattr(self, key, None)
                self._validators[key] = ObjectValidator(key=key, annotation=value, tests=self._tests.get(key))

        def validate(self, test_obj: JimmyMap) -> None:
            for validator in self._validators.values():
                validator.verify(test_obj)

        def __call__(self):
            raise NotImplementedError(
                f'{self._name} is now an instance of {type(self).__name__}, and it can not be initialized')

        def __repr__(self):
            return f'JimmyValidator for {self._name}'

    return JimmyValidator()
