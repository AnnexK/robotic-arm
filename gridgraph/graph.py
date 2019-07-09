from numpy import ndarray
from functools import reduce

from gridgraph.iterator import EdgeIterator, VertIterator
from gridgraph.edge import GraphEdge

class GridGraph:
    """Класс, моделирующий граф-решетку в трехмерном пространстве"""    
    def __sum_fun(x, y):
        return x[0]+y[0], x[1]+y[1], x[2]+y[2]
    
    def __init__(self, Vx, Vy, Vz):
        """Инициализировать граф с количеством вершин Vx, Vy, Vz"""

        # количество ребер в каждой размерности
        self.x_nedges = Vx-1
        self.y_nedges = Vy-1
        self.z_nedges = Vz-1

        # X, Y, Z
        self._edges = [ndarray(shape=(Vx-1,Vy,Vz), dtype=object),
                       ndarray(shape=(Vx,Vy-1,Vz), dtype=object),
                       ndarray(shape=(Vx,Vy,Vz-1), dtype=object)]

    @property
    def edges(self):
        return EdgeIterator(self)

    @property
    def vertices(self):
        return VertIterator(self)
    
    def vert_in_graph(self, v):
        return 0 <= v[0] <= self.x_nedges and 0 <= v[1] <= self.y_nedges and 0 <= v[2] <= self.z_nedges
    
    def get_adjacent(self, v):
        """Возвращает список смежных вершин для вершины v"""
        if not self.vert_in_graph(v):
            # или выброс исключения
            return None
        
        vecs = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]

        # точки, в которые можно попробовать попасть
        return filter(self.vert_in_graph, map(GridGraph.__sum_fun, [v]*6, vecs))
    
    def __getitem__(self, v):
        start, end = v[0], v[1]
        if end in self.get_adjacent(start):
            for i in range(3):
                if abs(start[i]-end[i]) == 1:
                    edges_idx = i
                    break
            return self._edges[edges_idx][min(start,end)]
        else:
            return None # ребра нет

    def __setitem__(self, v, value):
        start, end = v[0], v[1]

        if end in self.get_adjacent(start):
            for i in range(3):
                if abs(start[i]-end[i]) == 1:
                    edges_idx = i
                    break
            self._edges[edges_idx][min(start,end)] = GraphEdge(value[0], value[1])
        else:
            raise KeyError("Вершины не смежны")
