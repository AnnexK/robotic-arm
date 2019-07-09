from gridgraph.graph import GridGraph
from gridgraph.edge import GraphEdge
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
        ret = GridGraph(self.x, self.y, self.z)
        for v in ret.vertices:
            for w in ret.get_adjacent(v):
                if ret[v,w] is None:
                    ret[v,w] = 1.0, self.phi
        return ret, self.start, self.end


class GraphBuilder:
    def __init__(self, R, Env, Endpoint, base):
        self.r = R
        self.e = Env
        self.end = Endpoint
        self.phi = base
        self.mult = 100 # обратное к 1/100

    def make_graph(self):
        end = self.end
        start = self.r.get_effector()
        low_corner = tuple(min(start[i], end[i]) for i in range(3))
        high_corner = tuple(max(start[i], end[i]) for i in range(3))
        dx, dy, dz = (high_corner[i]-low_corner[i] for i in range(3))
        vx, vy, vz = (int(ceil(d * self.mult))+1 for d in (dx, dy, dz))
        G = GridGraph(vx, vy, vz)
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
                G[v,w] = (1/self.mult if legals[v] and legals[w] else inf), self.phi
        
        return G, space_to_grid(start), space_to_grid(end)
