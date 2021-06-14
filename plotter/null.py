from .plotter import Plotter, PlotterLink


class NullPlotter(Plotter):
    def plot(self, link: PlotterLink):
        pass
