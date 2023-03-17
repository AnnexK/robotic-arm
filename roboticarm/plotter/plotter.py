from __future__ import annotations
import abc


class PlotPoint:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


class PlotterLink(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_point(self) -> PlotPoint:
        pass

    @abc.abstractmethod
    def attach(self, P: Plotter):
        pass

    @abc.abstractmethod
    def detach(self, P: Plotter):
        pass


class Plotter(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def plot(self, link: PlotterLink):
        pass
