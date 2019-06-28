from gridgraph.graph import GridGraph
from gridgraph.edge import GraphEdge
from math import inf, ceil
from numpy import ndarray

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
        for v in ret.vertices:
            for w in ret.get_adjacent(v):
                if ret[v,w] is None:
                    ret[v,w] = 1.0, 0.0
        return ret

class GraphBuilder:
    def __init__(self, R, Env, Endpoint):
        self.r = R
        self.e = Env
        self.end = Endpoint
        self.mult = 100 # обратное к 1/100

    def make_graph(self):
        end = self.end
        start = self.r.get_effector()
        low_corner = tuple(min(start[i], end[i]) for i in range(3))
        high_corner = tuple(max(start[i], end[i]) for i in range(3))
        dx, dy, dz = (high_corner[i]-low_corner[i] for i in range(3))
        vx, vy, vz = (int(ceil(d * self.mult))+1 for d in (dx, dy, dz))
        G = GridGraph(vx, vy, vz, PheromoneEdge)
        print('vertices: {}x{}x{}'.format(vx,vy,vz))

        # функции преобразования из пространства в граф и обратно
        grid_to_space = lambda v : tuple(low_corner[i] + v[i] / self.mult for i in range(3))
        space_to_grid = lambda v : tuple(ceil((v[i] - low_corner[i]) * self.mult) for i in range(3))

        # проверка на доступность вершин
        legals = ndarray(shape=(vx,vy,vz), dtype=bool)
        for v in G.vertices:
            space_v = grid_to_space(v)
            legals[v] = self.r.move_to(space_v) and not self.r.check_collisions()

        # заполнение графа
        for v in G.vertices:
            for w in G.get_adjacent(v):
                G[v,w] = (1/self.mult if legals[v] and legals[w] else inf), 0.0
        
        return G, space_to_grid(start), space_to_grid(end)
