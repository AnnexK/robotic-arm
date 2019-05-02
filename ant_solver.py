import robot
import geometry as geom
from intersect import intersect
from gridgraph import GraphEdge, GridGraph
from common_math import isclose_wrap

from functools import reduce
from numpy import abs
from copy import deepcopy
from math import inf
import random

def metric_angle_diff(args):
    """Вычисляет сумму модулей разности углов робота R при перемещении схвата
в точку пространства d с проверкой на пересечение с объектами в obj_seq"""
    R = args[0] # RoboticArm
    obj_seq = args[1] # последовательность geom.Object
    d = args[2] # tuple из трех float'ов

    # в diff значения углов на которые нужно повернуть робота
    diff = robot.grip_calculate_angles(R, d[0], d[1], d[2])
    if diff is None:
        return inf
    
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
    # сколько всего феромона откладывает муравей
    Q = 1.0
    
    def __init__(self, pos):
        self.pos = pos # текущее положение в сетке
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
            
            total_attr += attr
            attrs.append(total_attr)

        # случайный выбор тут
        
        seed = total_attr * random.random()
        
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

        while len(self.path_verts) > 1:
            ret[0].append(self.path_verts.pop())

        ret[0].append(self.path_verts[0])
        self.path_edges.clear()
        
        return ret


class Solver:
    """"""
    def __init__(self,
                 R, end, obj_seq,
                 a, b, q, rho,
                 base_pheromone=0.01):

        O = R.origin
        e = R.edges
        min_point = (O.x - e[1].len - e[2].len,
                     O.y - e[1].len - e[2].len,
                     O.z + e[0].len - e[3].len - e[1].len - e[2].len)
        max_point = (O.x + e[1].len + e[2].len,
                     O.y + e[1].len + e[2].len,
                     O.z + e[0].len - e[3].len + e[1].len + e[2].len)

        G = GridGraph(min_point,
                      max_point,
                      grid_step=0.1,
                      metfoo=metric_angle_diff,
                      edge_type=PheromoneEdge)
        
        self.ant_spawner = Ant
        self.ant_spawner.alpha = a
        self.ant_spawner.assoc_graph = G
        self.ant_spawner.beta = b
        self.ant_spawner.Q = q
        self.ant_spawner.base_phero = base_pheromone
        self.decay = rho
        
        start = R.calculate_grip()
        self.start = G.origin_to_grid((start.x, start.y, start.z))
        self.end = G.origin_to_grid(end)

        self.robot = deepcopy(R)
        self.objects = obj_seq
        
    def pheromone_decay(self):
        self.ant_spawner.base_phero *= (1 - self.decay)
        for d in self.ant_spawner.assoc_graph.edges.values():
            for e in d.values():
                e.phi *= (1 - self.decay)

    def create_ants(self, amount):
        self.ants = [self.ant_spawner(self.start) for i in range(0,amount)]
    
    def solve(self, iters=1, ants_n=20):

        # создаем муравьев один раз,
        # а потом в каждой итерации откатываем их состояние
        # к начальному        
        self.create_ants(ants_n)
        best_paths = len(self.ants) * [None]
        
        for i in range(0, iters):
            print('Iter #', i+1)
            # поиск решения
            a_num = 1
            for a in self.ants:
                print('Ant#', a_num)
                while a.pos != self.end:
                    a.pick_edge([self.robot, self.objects])
                    # переместить робота
                    real_point = self.ant_spawner.assoc_graph.grid_to_origin(a.pos)                
                    cur_pos = robot.grip_calculate_angles(self.robot,
                                                          real_point[0],
                                                          real_point[1],
                                                          real_point[2])
                    self.robot.grip_move(cur_pos)
                print('Ant#', a_num, 'finished, path len:', a.path_len)
                # вернуть обратно
                real_point = self.ant_spawner.assoc_graph.grid_to_origin(a.path_verts[0])
                cur_pos = robot.grip_calculate_angles(self.robot,
                                                      real_point[0],
                                                      real_point[1],
                                                      real_point[2])
                self.robot.grip_move(cur_pos)
                
            # обновление феромона
            self.pheromone_decay()
            for k, a in enumerate(self.ants):
                a.distribute_pheromone()
                cur_path = a.unwind_path()
                if i==0 or cur_path[1] < best_paths[k][1]:
                    best_paths[k] = cur_path

        best_est_path = min(best_paths, key=lambda p : p[1])
        return list(map(self.ant_spawner.assoc_graph.grid_to_origin,
                        best_est_path[0])),best_est_path[1]
    
