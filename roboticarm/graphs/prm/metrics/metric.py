import abc
from roboticarm.env.types import State


class Metric(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __call__(self, a: State, b: State) -> float:
        pass
