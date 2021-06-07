import matplotlib.pyplot as plt
from .plotter import Plotter, Mux


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class MPLPlotter(Plotter):
    num = 0

    def __init__(self):
        self.id = MPLPlotter.num
        self.point_rows = dict()
        MPLPlotter.num += 1
        plt.show(block=False)

    def __del__(self):
        Mux().deregister_plotter(self)
        plt.show()

    def plot_point(self, link):
        if link not in self.point_rows:
            self.point_rows[link] = [Point(link.x, link.y)]
        else:
            self.point_rows[link].append(Point(link.x, link.y))
        f = plt.figure(self.id)
        f.clear()
        for r in self.point_rows:
            points = self.point_rows[r]
            plt.plot([p.x for p in points], [p.y for p in points])
        plt.draw()
        plt.pause(0.1)
