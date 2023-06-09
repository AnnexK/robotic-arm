from typing import Iterable, Dict
from .plotter import Plotter, PlotterLink


class CSVWriter(Plotter):
    def __init__(self, filename: str, links: Iterable[PlotterLink]):
        self.fp = open(filename, "w")
        self.links: Dict[PlotterLink, bool] = {L: False for L in links}
        for L in self.links:
            L.attach(self)

    def __del__(self):
        self.fp.close()

    def plot(self, link: PlotterLink):
        self.links[link] = True
        if all(self.links.values()):
            s = ",".join(str(L.get_point().y) for L in self.links)
            self.fp.write(s + "\n")
            self.links = {L: False for L in self.links}
