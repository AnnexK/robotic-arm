from numpy import ndarray
from functools import reduce

from gridgraph.iterator import GGIterator
from gridgraph.edge import GraphEdge

class GridGraph:
    """Класс, моделирующий граф-решетку в трехмерном пространстве"""    
    def __sum_fun(x, y):
        return x[0]+y[0], x[1]+y[1], x[2]+y[2]
    
    def __init__(self, Vx, Vy, Vz, edge_type=GraphEdge):
        """Инициализировать граф с количеством вершин Vx, Vy, Vz"""

        self.allocator = edge_type
                
        # количество ребер в каждой размерности
        self.x_nedges = Vx-1
        self.y_nedges = Vy-1
        self.z_nedges = Vz-1

        # X, Y, Z
        self.edges = [ndarray(shape=(Vx-1,Vy,Vz), dtype=object),
                      ndarray(shape=(Vx,Vy-1,Vz), dtype=object),
                      ndarray(shape=(Vx,Vy,Vz-1), dtype=object)]

    def __iter__(self):
        return GGIterator(self)

    def __vert_in_graph(self, v):
        return 0 <= v[0] <= self.x_nedges and 0 <= v[1] <= self.y_nedges and 0 <= v[2] <= self.z_nedges
    
    def get_adjacent(self, v):
        """Возвращает список смежных вершин для вершины v"""
        if not self.__vert_in_graph(v):
            return None
        
        vecs = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]

        # точки, в которые можно попробовать попасть
        return filter(self.__vert_in_graph, map(GridGraph.__sum_fun, [v]*6, vecs))
    
    def __getitem__(self, v):
        start, end = v[0], v[1]
        if end in self.get_adjacent(start):
            for i in range(3):
                if abs(start[i]-end[i]) == 1:
                    edges_idx = i
                    break
            return self.edges[edges_idx][min(start,end)]
        else:
            return None # ребра нет

    def __setitem__(self, v, value):
        start, end = v[0], v[1]

        if end in self.get_adjacent(start):
            for i in range(3):
                if abs(start[i]-end[i]) == 1:
                    edges_idx = i
                    break
            if isinstance(value, tuple):
                self.edges[edges_idx][min(start,end)] = self.allocator(*value)
            else:
                self.edges[edges_idx][min(start,end)] = None if value is None else self.allocator(value)
        else:
            raise KeyError("Вершины не смежны")
