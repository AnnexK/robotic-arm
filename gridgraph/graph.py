from math import inf
from common_math import isclose_wrap
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

    # эти - отдельно
    def origin_to_grid(self, point):
        """origin_to_grid : tuple -> tuple
Преобразует координаты точки в пространстве к координатам ближайшей к ней точки в графе
Возвращает (-1,) если точка не находится в решетке"""
        lx = self.start[0]
        ly = self.start[1]
        lz = self.start[2]

        rx = self.end[0]
        ry = self.end[1]
        rz = self.end[2]

        x = point[0]
        y = point[1]
        z = point[2]

        # находится ли точка в решетке?
        in_x = lx<x<rx or isclose_wrap(lx,x) or isclose_wrap(rx,x)
        in_y = ly<y<ry or isclose_wrap(ly,y) or isclose_wrap(ry,y)
        in_z = lz<z<rz or isclose_wrap(lz,z) or isclose_wrap(rz,z)

        if in_x and in_y and in_z:
            mult = 1/self.step
            return tuple(int(round(c * mult)) for c in [x-lx, y-ly, z-lz])
        else:
            return -1,

    def grid_to_origin(self, point):
        """grid_to_origin : tuple -> tuple/None
Преобразует координаты сетки в координаты точки пространства
Возвращает None, если преобразование невозможно"""
        mult = 1/self.step

        if point == (-1,): # возвращается origin_to_grid
            return None
        
        in_x = 0 <= point[0] <= self.x_nedges
        in_y = 0 <= point[1] <= self.y_nedges
        in_z = 0 <= point[2] <= self.z_nedges

        if in_x and in_y and in_z:
            return tuple(self.start[i] + self.step * point[i] for i in range(0,3))
        else:
            return None

    def __vert_in_graph(self, v):
        return 0 <= v[0] <= self.x_nedges and 0 <= v[1] <= self.y_nedges and 0 <= v[2] <= self.z_nedges
    
    def get_adjacent(self, v):
        """Возвращает список смежных вершин для вершины v"""
        if not self.__vert_in_graph(v):
            return None
        
        vecs = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]

        # точки, в которые можно попробовать попасть
        return filter(self.__vert_in_graph, map(GridGraph.__sum_fun, [v]*6, vecs))
    
    def __check_bounds(self, start, end):
        """Проверка на принадлежность ребра графу"""
        dx = abs(end[0]-start[0])
        dy = abs(end[1]-start[1])
        dz = abs(end[2]-start[2])

        # выбор массива для поиска/вставки
        if dx == 1:
            edges_idx = 0
        elif dy == 1:
            edges_idx = 1
        elif dz == 1:
            edges_idx = 2
        else:
            return None, None
        if dx+dy+dz != 1:
            return None, None
        
        # вычисление координат точки в решетке
        point = tuple(p - (v == -1) for p, v in zip(start, [dx,dy,dz])) 

        # не следует хранить в массивах точки, для которых нет ребра
        # поэтому вычитаем модули
        in_x = 0 <= point[0] <= self.x_nedges - abs(dx)
        in_y = 0 <= point[1] <= self.y_nedges - abs(dy)
        in_z = 0 <= point[2] <= self.z_nedges - abs(dz)

        if in_x and in_y and in_z:
            return edges_idx, point
        else:
            return None, None
        
    def __getitem__(self, v):
        start, end = v[0], v[1]
        edges_idx, point = self.__check_bounds(start, end)
        
        if point is not None:
            return self.edges[edges_idx][point]
        else:
            return None # ребра нет

    def __setitem__(self, v, value):
        start, end = v[0], v[1]

        edges_idx, point = self.__check_bounds(start,end)

        if point is not None:
            try:
                __ = iter(value)
                self.edges[edges_idx][point] = self.allocator(*value)
            except TypeError:
                if value is None:
                    self.edges[edges_idx][point] = self.allocator()
                else:
                    self.edges[edges_idx][point] = self.allocator(value)
        else:
            pass # или бросить исключение
