import abc
from .plotter import Plotter, PlotterLink, PlotPoint
from weakref import WeakSet
from typing import Iterable


class Link(PlotterLink):
    def __init__(self):
        self._plotters: WeakSet[Plotter] = WeakSet()
        self.x = self.y = 0.0
        
    def get_point(self) -> PlotPoint:
        return PlotPoint(self.x, self.y)

    def attach(self, P: Plotter):
        self._plotters.add(P)

    def detach(self, P: Plotter):
        self._plotters.discard(P)

    def set_point(self, x: float, y: float):
        self.x = x
        self.y = y

    def announce(self):
        for p in self._plotters:
            p.plot(self)


class Plottable(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_links(self) -> Iterable[PlotterLink]:
        pass