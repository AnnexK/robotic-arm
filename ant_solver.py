import robot
import geometry as geom
from intersect import intersect

from numpy import abs
from gridgraph import GraphEdge, GridGraph
from common_math import isclose_wrap

import random

def metric_angle_diff(args):
    """Вычисляет сумму модулей разности углов робота R при перемещении схвата
в точку пространства d с проверкой на пересечение с объектами в obj_seq"""
    R = args[0] # RoboticArm
    obj_seq = args[1] # последовательность geom.Object
    d = args[2] # tuple из трех float'ов

    # в diff значения углов на которые нужно повернуть робота
    diff = grip_calculate_angles(R, d[0], d[1], d[2])
    # а суммарное расстояние поворота можно посчитать так
    res = reduce(lambda x,y : abs(x) + abs(y), diff)
    
    R.grip_move(diff)
    # найдено пересечение - перемещение невозможно
    if intersect(R, obj_seq): 
        res = inf
    # обратное перемещение
    R.grip_move([-1 * a for a in diff])
    return res


class PheromoneEdge(GraphEdge):
    """Класс, описывающий ребро графа с дополнительным полем значения феромона"""
    def __init__(self, w, phi=0.0):
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

def edge_attraction(phi, dist, alpha, beta):
    """Вычисляет привлекательность ребра по формуле"""
    return phi ** alpha * (1 / dist) ** beta


class Ant:
    """Класс, моделирующий поведение муравья"""
    # коэф привлекательности по феромону
    alpha = 0.0
    # коэф привлекательности по длине ребра
    beta = 0.0
    # базовый уровень феромона
    base_phero = 0.0
    # граф, в котором происходит поиск решения (reference)
    assoc_graph = None
    
    def __init__(self, pos, Q=1.0):
        self.pos = pos # текущее положение в сетке
        self.Q = Q # сколько всего будет отложено феромона (общий или частный?)
        self.path_len = 0.0 # длина текущего пути
        self.path_edges = list() # стек с ребрами
        self.path_verts = [pos] # стек с вершинами

    @property
    def pos(self):
        return self._grid_pos

    @pos.setter
    def pos(self, value):
        if not isinstance(value, tuple):
            raise TypeError("Передан не кортеж")
        if not len(value) == 3:
            raise ValueError("Значение не является точкой")
        if not Ant.assoc_graph.grid_to_origin(value):
            raise ValueError("Точка не принадлежит графу")
        self._grid_pos = value

    def pick_edge(self, metric_args=[]):
        """Совершает перемещение в одну из соседних точек в графе G"""

        # возможно, переместить в solver и инициализировать один раз?
        random.seed()

        G = self.assoc_graph
        
        # сложение точек
        sum_fun = lambda x, y : (x[0] + y[0], x[1] + y[1], x[2] + y[2])
        vecs = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]

        # точки, в которые можно попробовать попасть
        target_points = list(map(sum_fun, [self.pos]*6, vecs))

        print('Target points: ', target_points)
        # ребра, по которым можно пройти
        edges = [G.get_edge(self.pos,t,metric_args+[G.grid_to_origin(t)])
                 for t in target_points]

        # привлекательности ребер
        attrs = [0.0]
        total_attr = 0.0
        
        for i in range(0,6):
            # посчитать привлекательность ребра

            # обход случая когда beta = 0, а ребра не существует
            if edges[i].weight == inf:
                p = 0.0
            else:
                p = self.base_phero + edges[i].phi
            
            attr = edge_attraction(p,
                                   edges[i].weight,
                                   self.alpha,
                                   self.beta)
            print('Iter=', i, '; attr=', attr)
            
            total_attr += attr
            attrs.append(total_attr)

        # случайный выбор тут
        
        seed = total_attr * random.random()

        print('Attractiveness thresholds: ', attrs)
        
        choice = 0
        for i in range(0,6):
            # выбор ребра
            decision = isclose_wrap(attrs[i], seed)
            decision = decision or attrs[i]<seed<attrs[i+1]
            
            # если один из вызовов edge_attraction вернул 0.0,
            # то можно применить обычное сравнение
            # для опознания абсолютно непривлекательного ребра
            decision = decision and not attrs[i] == attrs[i+1]
            if isclose_wrap(attrs[i], seed) or attrs[i]<seed<attrs[i+1]:
                choice = i
                break

        # добавить в стек
        self.path_edges.append(edges[choice]) 
        self.path_verts.append(target_points[choice])
        self.path_len += edges[choice].weight
        self.pos = target_points[choice]

    def distribute_pheromone(self):
        """Распространяет феромон по всем пройденным ребрам"""
        phi = self.Q / self.path_len
        
        for e in self.path_edges:
            e.phi = e.phi + phi

    def unwind_path(self):
        ret = ([], self.path_len)

        self.pos = self.path_verts[0]

        while len(self.path_verts) > 0:
            ret[0].append(self.path_verts.pop())

        return ret
