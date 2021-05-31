from .plotter import Plotter
from .mux import Mux


class CSVWriter(Plotter):
    min_name = 'min'
    max_name = 'max'
    avg_name = 'avg'
    def __init__(self, filename):
        self.fp = open(filename, 'w')
        self.wdict = {
            CSVWriter.min_name: 0.0,
            CSVWriter.max_name: 0.0,
            CSVWriter.avg_name: 0.0
        }
        self.current = 0

    def __del__(self):
        Mux().deregister_plotter(self)
        self.fp.close()

    def plot_point(self, link):
        self.wdict[link.name] = link.y
        self.current += 1
        if self.current == 3:
            self.fp.write(
                f'{self.wdict[CSVWriter.min_name]},'
                f'{self.wdict[CSVWriter.max_name]},'
                f'{self.wdict[CSVWriter.avg_name]}\n')
            self.current = 0

    