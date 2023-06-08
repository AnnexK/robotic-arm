import matplotlib.pyplot as plt
from .plotter import Plotter, PlotPoint, PlotterLink


class MPLPlotter(Plotter):
    num = 0

    def __init__(self):
        self.id: int = MPLPlotter.num
        self.point_rows: dict[PlotterLink, list[PlotPoint]] = dict()
        MPLPlotter.num += 1
        plt.show(block=False)

    def __del__(self):
        plt.show()

    def plot(self, link: PlotterLink):
        point = link.get_point()
        if link not in self.point_rows:
            self.point_rows[link] = [point]
        else:
            self.point_rows[link].append(point)
        f = plt.figure(self.id)
        f.clear()
        for r in self.point_rows:
            points = self.point_rows[r]
            plt.plot([p.x for p in points], [p.y for p in points])
        plt.draw()
        plt.pause(1)
