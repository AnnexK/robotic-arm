from gridgraph.graph import GridGraph
from gridgraph import ConstWeight
from numpy import ndarray, inf, ceil


class ExampleGraphBuilder:
    def __init__(self, x, y, z, s, e, base):
        self.x = x
        self.y = y
        self.z = z
        self.start = s
        self.end = e
        self.phi = base

    def make_graph(self):
        ret = GridGraph(self.x, self.y, self.z, ConstWeight(), self.phi)
        return ret, self.start, self.end
