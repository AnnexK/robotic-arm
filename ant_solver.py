import robot
import geometry as geom
from intersect import intersect
from gridgraph import GraphEdge, GridGraph
from common_math import isclose_wrap

import time
from functools import reduce
from numpy import abs, ndarray
from copy import copy, deepcopy
from math import inf
import random
import heapq

def metric_angle_diff(R, obj_seq, d):
    """Вычисляет сумму модулей разности углов робота R при перемещении схвата
в точку пространства d с проверкой на пересечение с объектами в obj_seq"""
    
    # в diff значения углов на которые нужно повернуть робота
    diff = robot.grip_calculate_angles(R, d[0], d[1], d[2])
    if diff is None:
        return None
    
    # а суммарное расстояние поворота можно посчитать так
    res = reduce(lambda x,y : abs(x) + abs(y), diff)
    
    R.grip_move(diff)
    # найдено пересечение - перемещение невозможно
    if intersect(R, obj_seq): 
        res = None
    # обратное перемещение
    R.grip_move([-1 * a for a in diff])
    return res


class PheromoneEdge(GraphEdge):
    """Класс, описывающий ребро графа с дополнительным полем значения феромона"""
    def __init__(self, w, phi):
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

    def pick_edge(self):
        """Совершает перемещение в одну из соседних точек в графе G"""

        # возможно, переместить в solver и инициализировать один раз?
        random.seed()

        G = self.assoc_graph

        targets = list(G.get_adjacent(self.pos))
        edges = [G[self.pos, t] for t in targets]
        
        # привлекательности ребер
        attrs = [0.0]
        total_attr = 0.0
        
        for e in edges:
            # посчитать привлекательность ребра

            # ребра нет
            if e is None:
                attr = 0.0
            else:
                attr = edge_attraction(self.base_phero + e.phi,
                                       e.weight,
                                       self.alpha,
                                       self.beta)
            
            total_attr += attr
            attrs.append(total_attr)

        # случайный выбор тут
        
        seed = total_attr * random.random()
        
        choice = None
        for i, a in enumerate(attrs):
            # выбор ребра
            decision = isclose_wrap(a, seed)
            decision = decision or a<seed<attrs[i+1]
            
            # если привлекательность ребра равна 0.0,
            # то можно применить обычное сравнение
            decision = decision and not a == attrs[i+1]
            if isclose_wrap(a, seed) or a<seed<attrs[i+1]:
                choice = i
                break

        if choice is None:
            raise Exception("Из вершины нет ни одного ребра")
        
        # добавить в стек
        self.path_edges.append(edges[choice]) 
        self.path_verts.append(targets[choice])
        self.path_len += edges[choice].weight
        self.pos = targets[choice]

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
    """Класс, моделирующий решение задачи"""
    def __init__(self,
                 R=robot.make_robot(), end=(1.2,2.3,3.4), obj_seq=[],
                 a=1.0, b=1.0, q=1.0, rho=0.01,
                 base_pheromone=0.1):

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

        self.R = deepcopy(R)
        self.objs = obj_seq

    def precalculate_edges_simple(self):
        G = self.ant_spawner.assoc_graph
        X = G.x_nedges
        Y = G.y_nedges
        Z = G.z_nedges
        EX = G.edges[0]
        EY = G.edges[1]
        EZ = G.edges[2]
        A = G.allocator
        start = time.time()
        for x in range(0, X):
            for y in range(0, Y):
                for z in range(0, Z):
                    # прямой доступ к элементам массива
                    if x < X - 1:
                        EX[x,y,z] = A(1.0,0.0)
                    if y < Y - 1:
                        EY[x,y,z] = A(1.0,0.0)
                    if z < Z - 1:
                        EZ[x,y,z] = A(1.0,0.0)
        end = time.time()
        print("precalculation finished, time: ", end-start)
        
    def precalculate_edges(self):
        G = self.ant_spawner.assoc_graph
        step = G.step
        
        start = time.time()
        for x in range(0, G.x_nedges):
            for y in range(0, G.y_nedges):
                for z in range(0, G.z_nedges):
                    rx, ry, rz = G.grid_to_origin((x, y, z))
                    diff = robot.grip_calculate_angles(self.R, rx, ry, rz)
                    if diff is None:
                        resx = None
                        resy = None
                        resz = None
                    else:
                        self.R.grip_move(diff)
                        px = rx+step, ry, rz
                        py = rx, ry+step, rz
                        pz = rx, ry, rz+step
                        mx = metric_angle_diff(self.R, self.objs, px)
                        my = metric_angle_diff(self.R, self.objs, py)
                        mz = metric_angle_diff(self.R, self.objs, pz)
                        resx = None if mx is None else (mx, 0.0)
                        resy = None if my is None else (my, 0.0)
                        resz = None if mz is None else (mz, 0.0)
                    if x < G.x_nedges - 1:
                        G.edges[0][x,y,z] = None if resx is None else G.allocator(*resx)
                    if y < G.y_nedges - 1:
                        G.edges[1][x,y,z] = None if resy is None else G.allocator(*resy)
                    if z < G.z_nedges - 1:
                        G.edges[2][x,y,z] = None if resz is None else G.allocator(*resz)
        end = time.time()
        print("Precalculation finished, time: ", end - start)
    
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
        best_paths = ants_n * [None]
        
        for i in range(0, iters):
            print('Iter #', i+1)
            # поиск решения
            a_num = 1
            for a in self.ants:
                print('Ant#', a_num)
                while a.pos != self.end:
                    a.pick_edge()
                print('Ant#', a_num, 'finished, path len:', a.path_len)
                
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

def dijkstra(G, start, end):
    X = G.x_nedges + 1
    Y = G.y_nedges + 1
    Z = G.z_nedges + 1

    # прямая и обратная ф. для отображения кортежей в числа и наоборот
    f = lambda t : t[0] + t[1] * X + t[2] * X * Y
    invf = lambda k : (k % X, (k % (X*Y)) // X, k // (X*Y))

    # расстояния
    d = [inf for i in range(X*Y*Z)]
    d[f(start)] = 0.0

    # очередь с приоритетами
    heap = [(0.0, start)]
    # предки вершин
    p = [None for i in range(0, X*Y*Z)]

    cur = None
    dest = end

    while heap:
        # достать вершину с минимальным расстоянием из очереди
        weight, cur = heapq.heappop(heap)
        if cur == dest: # найден нужный путь
            break

        for w in G.get_adjacent(cur):
            # индексы в массиве расстояний
            fw = f(w)
            fcur = f(cur)
            edge = G[cur,w]
            if edge is not None and d[fw] > d[fcur] + edge.weight:
                d[fw] = d[fcur] + edge.weight
                heapq.heappush(heap, (d[fw], w))
                p[fw] = cur

    path = [dest]
    i = f(path[0])

    if d[i] == inf:
        return None
    
    while p[i] is not None:
        path.append(p[i])
        i = f(path[-1])
    
    return (d[f(dest)], path)
