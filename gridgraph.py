from sortedcontainers import SortedDict # ассоц. массив
from math import inf
from common_math import isclose_wrap


def metric_static(args):
    # возвращает 1
    return 1.0

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
    def __init__(self, start_point, end_point, grid_step=0.1, metfoo=metric_static, edge_type=GraphEdge):
        """Инициализировать граф с угловыми точками и заданной метрикой"""

        if not issubclass(edge_type, GraphEdge):
            raise ValueError("Передан класс не типа GraphEdge")

        self.allocator = edge_type
        
        # начальная и конечная точки
        self.start = [min(x, y) for x,y in zip(start_point,end_point)]
        self.end = [max(x, y) for x,y in zip(start_point,end_point)]

        self.step = grid_step
        
        # количество ребер в каждой размерности
        self.x_nedges = int(abs(start_point[0] - end_point[0]) * (1/grid_step))
        self.y_nedges = int(abs(start_point[1] - end_point[1]) * (1/grid_step))
        self.z_nedges = int(abs(start_point[2] - end_point[2]) * (1/grid_step))

        # метрика графа
        self.metric = metfoo

        # X, Y, Z
        self.edges = [SortedDict(), SortedDict(), SortedDict()]
        
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
            return tuple(round(c * mult) for c in [x-lx, y-ly, z-lz])
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

    def get_edge(self, start, end, metric_data):
        """get_edge : tuple, tuple, (data) -> [float, float]
Возвращает данные ребра с началом в точке start и концом в
точке end (коорд. сетки)
Если ребро еще не было посещено ни разу, создается новое
с метрикой, посчитанной по данным metric_data и помещается
в граф"""
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
            raise ValueError("Вектор не является ортом, параллельным осям")

        # вычисление координат точки в решетке
        point = tuple(p - (v == -1) for p, v in zip(start, [dx,dy,dz])) 

        # не следует хранить в массивах точки, для которых нет ребра
        # поэтому вычитаем модули
        in_x = 0 <= point[0] <= self.x_nedges - abs(dx)
        in_y = 0 <= point[1] <= self.y_nedges - abs(dy)
        in_z = 0 <= point[2] <= self.z_nedges - abs(dz)

        if in_x and in_y and in_z:
            try:
                return self.edges[edges_idx][point]
            except KeyError as ke: # элемента нет в ассоц. массиве
                # длина
                edge = self.allocator(self.metric(metric_data))                
                self.edges[edges_idx][point] = edge
                return self.edges[edges_idx][point]
        else:
            return self.allocator(inf) # ребра нет
