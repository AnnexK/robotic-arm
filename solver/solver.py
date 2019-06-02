from gridgraph.graph import GridGraph
from gridgraph.edge import GraphEdge
from solver.ant import Ant

import time
import numpy.random as nprand
from functools import reduce
from numpy import abs, ndarray
from math import inf

class PheromoneEdge(GraphEdge):
    """Класс, описывающий ребро графа с дополнительным полем значения феромона"""
    def __init__(self, w=0.0, phi=0.0):
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

class AntSolver:
    """Класс, моделирующий решение задачи"""
    def __init__(self,
                 R, end,
                 a=1.0, b=1.0, q=1.0, rho=0.01,
                 base_pheromone=0.1):

        # добавить построение графа
        pass
    
        self.ant_spawner = Ant
        self.ant_spawner.alpha = a
        self.ant_spawner.assoc_graph = G
        self.ant_spawner.beta = b
        self.ant_spawner.Q = q
        self.ant_spawner.base_phero = base_pheromone
        self.decay = rho
        
        # добавить определение начальных и конечных точек
        self.start = R.get_effector()
        self.end = end

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
        print("precalculation finished, time: ", end-start) # ~15s for 120x120x120 graph
        
    def precalculate_edges(self):
        G = self.ant_spawner.assoc_graph

        start = time.time()
        for x in range(0, G.x_nedges):
            for y in range(0, G.y_nedges):
                for z in range(0, G.z_nedges):
                    # добавить обработку столкновений и вставку ребер
                    pass
        end = time.time()
        print("Precalculation finished, time: ", end - start)
    
    def pheromone_decay(self):
        """Уменьшение кол-ва феромона"""
        self.ant_spawner.base_phero *= (1 - self.decay)
 
        for arr in self.ant_spawner.assoc_graph.edges:
            for e in arr:
                e.phi *= (1 - self.decay)

    def create_ants(self, amount):
        self.ants = [self.ant_spawner(self.start) for i in range(amount)]
    
    def solve(self, iters=1, ants_n=20):

        nprand.seed()
        # создаем муравьев один раз,
        # а потом в каждой итерации откатываем их состояние
        # к начальному        
        self.create_ants(ants_n)
        
        best_paths = []
        worst_paths = []
        avg_paths = []
        
        for i in range(iters):
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
            for a in self.ants:
                a.distribute_pheromone()
            
            paths = [a.unwind_path() for a in self.ants]
            best_paths.append(min(paths))
            worst_paths.append(max(paths))
            avg_paths.append(sum(paths)/ants_n)

        return best_paths, worst_paths, avg_paths

