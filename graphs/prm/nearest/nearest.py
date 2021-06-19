import abc
from typing import Sequence
from env.types import State
from ..metrics.metric import Metric


class KNearest(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def insert(self, p: State):
        pass

    @abc.abstractmethod
    def delete(self, p: State):
        pass

    @abc.abstractmethod
    def metric(self) -> Metric:
        pass

    @abc.abstractmethod
    def nearest(self, p: State, k: int) -> Sequence[State]:
        pass