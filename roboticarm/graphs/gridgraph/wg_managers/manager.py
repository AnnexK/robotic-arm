import abc
from roboticarm.graphs.gridgraph.vertex import GGVertex as V


class WeightManager(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_weight(self, v: V, w: V) -> float:
        pass
