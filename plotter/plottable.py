from .mux import Mux


class Plottable:
    def announce_point(self, L):
        Mux().notify(L)
