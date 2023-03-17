import abc
from env.types import State


class Metric(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __call__(self, a: State, b: State) -> float:
        pass
