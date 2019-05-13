from math import inf
from common_math import isclose_wrap
from numpy import ndarray
from functools import reduce

class GraphEdge:
    def __init__(self, w):
        self._weight = w

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, value):
        self._weight = value


class GridGraph:
    """Класс, моделирующий граф-решетку в трехмерном пространстве"""
    class GGIterator:
        def __init__(self, g):
            self.e = g.edges # ссылка на массив ребер
            self.ei = 0 # положение в массиве по параллельности ребер
            self.xc = 0 # текущая координата x
            self.xm = g.x_nedges # макс координата x
            self.yc = 0
            self.ym = g.y_nedges
            self.zc = 0
            self.zm = g.z_nedges

        def __next__(self):
            if self.ei == 3:
                raise StopIteration
            
            idx = (self.xc, self.yc, self.zc)
            eidx = self.ei
            self.xc += 1
            if self.xc > self.xm - (self.ei == 0):
                self.xc = 0
                self.yc += 1
                if self.yc > self.ym - (self.ei == 1):
                    self.yc = 0
                    self.zc += 1
                    if self.zc > self.zm - (self.ei == 2):
                        self.zc = 0
                        self.ei += 1
            return self.e[eidx][idx]
        
    def __init__(self, start_point, end_point, grid_step=0.1, edge_type=GraphEdge):
        """Инициализировать граф с угловыми точками"""

        self.allocator = edge_type
        
        # начальная и конечная точки
        self.start = [min(x, y) for x,y in zip(start_point,end_point)]
        self.end = [max(x, y) for x,y in zip(start_point,end_point)]

        self.step = grid_step
        
        # количество ребер в каждой размерности
        self.x_nedges = int(round(abs(start_point[0] - end_point[0]) * (1/grid_step)))
        self.y_nedges = int(round(abs(start_point[1] - end_point[1]) * (1/grid_step)))
        self.z_nedges = int(round(abs(start_point[2] - end_point[2]) * (1/grid_step)))

        # X, Y, Z
        self.edges = [ndarray(shape=(self.x_nedges,self.y_nedges+1,self.z_nedges+1), dtype=object),
                      ndarray(shape=(self.x_nedges+1,self.y_nedges,self.z_nedges+1), dtype=object),
                      ndarray(shape=(self.x_nedges+1,self.y_nedges+1,self.z_nedges), dtype=object)]

    def __iter__(self):
        return self.GGIterator(self)
    
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

    def get_adjacent(self, v):
        """Возвращает список смежных вершин для вершины v"""
        bound = lambda v: 0 <= v[0] <= self.x_nedges and 0 <= v[1] <= self.y_nedges and 0 <= v[2] <= self.z_nedges
        if not bound(v):
            return None
        
        sum_fun = lambda x, y : (x[0] + y[0], x[1] + y[1], x[2] + y[2])
        vecs = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]

        # точки, в которые можно попробовать попасть
        return filter(bound, map(sum_fun, [v]*6, vecs))

    def __check_args(self, args):
        """Проверка аргументов для индексаторов"""
        try:
            if len(args) != 2:
                raise ValueError("Недостаточное количество размерностей")
        except TypeError:
            raise ValueError("Недостаточное количество размерностей")

        start = args[0]
        end = args[1]

        if len(start) != 3 or len(end) != 3:
            raise ValueError("Переданы параметры, не идентифицирующие вершины")

        # проверка элементов кортежей на целочисленность
        all_ints = reduce(lambda x,y: x & y,
                          [isinstance(b, int) for b in start+end])

        if not all_ints:
            raise ValueError("Не все координаты сетки целочисленные")

        return start, end
    
    def __check_bounds(self, start, end):
        """Проверка на принадлежность ребра графу"""
        dx = end[0]-start[0]
        dy = end[1]-start[1]
        dz = end[2]-start[2]

        # выбор массива для поиска/вставки
        if abs(dx) == 1:
            edges_idx = 0
        elif abs(dy) == 1:
            edges_idx = 1
        elif abs(dz) == 1:
            edges_idx = 2
        else:
            edges_idx = -1
        
        if abs(dx)+abs(dy)+abs(dz) != 1 or edges_idx < 0:
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

        #start, end = self.__check_args(v)
        start, end = v[0], v[1]
        edges_idx, point = self.__check_bounds(start, end)
        
        if point is not None:
            return self.edges[edges_idx][point]
        else:
            return None # ребра нет

    def __setitem__(self, v, value):
        #start, end = self.__check_args(v)
        start, end = v[0], v[1]

        edges_idx, point = self.__check_bounds(start,end)

        if point is not None:
            try:
                __ = iter(value)
                self.edges[edges_idx][point] = self.allocator(*value)
            except TypeError:
                if value is None:
                    self.edges[edges_idx][point] = None
                else:
                    self.edges[edges_idx][point] = self.allocator(value)
        else:
            pass # или бросить исключение

        
