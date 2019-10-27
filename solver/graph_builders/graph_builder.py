from gridgraph.graph import GridGraph
from gridgraph.weight_calcs.const import BoundedConstWeight
from gridgraph.phi_managers.base import PhiManager


class ExampleGraphBuilder:
    def __init__(self, dims, s, e, base):
        self.dims = dims
        self.start = s
        self.end = e
        self.phi = base

    def make_graph(self):
        ret = GridGraph(
            BoundedConstWeight(self.dims, 1.0),
            PhiManager(self.phi)
        )
        return ret, self.start, self.end
