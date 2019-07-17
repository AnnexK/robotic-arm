from numpy import full
from functools import reduce

from gridgraph.iterator import VertIterator

class GridGraph:
    """Класс, моделирующий граф-решетку в трехмерном пространстве"""    
    def __sum_fun(x, y):
        return x[0]+y[0], x[1]+y[1], x[2]+y[2]
    
    def __init__(self, Vx, Vy, Vz, weight, base):
        """Инициализировать граф с количеством вершин Vx, Vy, Vz"""

        # количество ребер в каждой размерности
        self.weight = weight
        self.x_nedges = Vx-1
        self.y_nedges = Vy-1
        self.z_nedges = Vz-1

        # X, Y, Z
        self._phi = [full(shape=(Vx-1,Vy,Vz), dtype=float, fill_value=base),
                     full(shape=(Vx,Vy-1,Vz), dtype=float, fill_value=base),
                     full(shape=(Vx,Vy,Vz-1), dtype=float, fill_value=base)]

    def __iter__(self):
        return VertIterator(self)
    
    def vert_in_graph(self, v):
        return 0 <= v[0] <= self.x_nedges and 0 <= v[1] <= self.y_nedges and 0 <= v[2] <= self.z_nedges
    
    def get_adjacent(self, v):
        """Возвращает список смежных вершин для вершины v"""
        if not self.vert_in_graph(v):
            raise ValueError('Vertex not in graph')
        
        vecs = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]

        # точки, в которые можно попробовать попасть
        return filter(self.vert_in_graph, map(GridGraph.__sum_fun, [v]*6, vecs))

    @property
    def weight_calculator(self):
        return self.weight

    def get_weight(self, v, w):
        if w in self.get_adjacent(v):
            return self.weight.get(v, w)
        else:
            return None

    def set_weight(self, v, w, val):
        if w in self.get_adjacent(v):
            self.weight.set(v, w, val)
        else:
            raise ValueError('Vertices not adjacent')

    def get_phi(self, v, w):
        if w in self.get_adjacent(v):
            for i in range(3):
                if abs(v[i]-w[i]) == 1:
                    index = i
                    break
            return self._phi[index][min(v,w)]
        else:
            return None

    def set_phi(self, v, w, val):
        if w in self.get_adjacent(v):
            for i in range(3):
                if abs(v[i]-w[i]) == 1:
                    index = i
                    break
            self._phi[index][min(v,w)] = val
        else:
            raise ValueError('Vertices not adjacent')

    def evaporate(self, value):
        for arr in self._phi:
            arr *= (1 - value)