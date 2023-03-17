import abc
from typing import Generic, TypeVar
from graphs import PhiGraph


V = TypeVar('V')


class GraphBuilder(Generic[V], metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def build_graph(self) -> PhiGraph[V]:
        pass
