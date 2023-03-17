import abc
from typing import Iterable, TypeVar, Generic, Sequence
from ..ants import BaseAnt


V = TypeVar('V')


class ACOAlgorithm(Generic[V], metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def generate_solutions(self, ants: Iterable[BaseAnt[V]]):
        pass

    @abc.abstractmethod
    def update_pheromone(self, ants: Iterable[BaseAnt[V]]):
        pass

    @abc.abstractmethod
    def daemon_actions(self):
        pass

    @abc.abstractmethod
    def result(self) -> Sequence[V]:
        pass