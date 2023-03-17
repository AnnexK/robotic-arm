import abc
from typing import Generic, TypeVar, Iterable


V = TypeVar('V')


class PhiGraph(Generic[V], metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_weight(self, v: V, w: V) -> float:
        pass

    @abc.abstractmethod
    def get_phi(self, v: V, w: V) -> float:
        pass

    @abc.abstractmethod
    def add_phi(self, v: V, w: V, val: float):
        pass

    @abc.abstractmethod
    def evaporate(self, rate: float):
        pass

    @abc.abstractmethod
    def get_adjacent(self, v: V) -> Iterable[V]:
        pass
