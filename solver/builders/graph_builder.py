from gridgraph.graph import GridGraph
from gridgraph.weight import BoundedConstWeight


class ExampleGraphBuilder:
    def __init__(self, x, y, z, s, e, base):
        self.x = x
        self.y = y
        self.z = z
        self.start = s
        self.end = e
        self.phi = base

    def make_graph(self):
        ret = GridGraph(
            BoundedConstWeight(self.x, self.y, self.z, 1.0), self.phi)
        return ret, self.start, self.end
