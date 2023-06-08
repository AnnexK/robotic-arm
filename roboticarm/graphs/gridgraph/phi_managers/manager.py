import abc
from roboticarm.graphs.gridgraph.vertex import GGVertex as V


class PhiManager(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_phi(self, v: V, w: V) -> float:
        pass

    @abc.abstractmethod
    def add_phi(self, v: V, w: V, val: float):
        pass

    @abc.abstractmethod
    def evaporate(self, rate: float):
        pass
