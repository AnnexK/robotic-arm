from gridgraph.graph import GridGraph
from gridgraph.edge import GraphEdge

class PheromoneEdge(GraphEdge):
    """Класс, описывающий ребро графа с дополнительным полем значения феромона"""
    def __init__(self, w=0.0, phi=0.0):
        super().__init__(w)
        self._pheromones = phi

    @property
    def phi(self):
        return self._pheromones

    @phi.setter
    def phi(self, value):
        if value < 0.0:
            raise ValueError("Количество феромона не может быть отрицательным")
        self._pheromones = value

class ExampleGraphBuilder:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def make_graph(self):
        ret = GridGraph(self.x, self.y, self.z, PheromoneEdge)
        for v in ret:
            for w in ret.get_adjacent(v):
                if ret[v,w] is not None:
                    ret[v,w] = 1.0, 0.0
        return ret