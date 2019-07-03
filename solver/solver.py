from gridgraph.graph import GridGraph
from gridgraph.edge import GraphEdge
from solver.ant import Ant

import time
import numpy.random as nprand
from functools import reduce
from numpy import abs, ndarray
from math import inf

class AntSolver:
    """Класс, моделирующий решение задачи"""
    def __init__(self,
                 G, start, end,
                 a=1.0, b=1.0, q=1.0, rho=0.01,
                 base_pheromone=0.1):
    
        self.ant_spawner = Ant
        self.ant_spawner.alpha = a
        self.ant_spawner.assoc_graph = G
        self.ant_spawner.beta = b
        self.ant_spawner.Q = q
        self.ant_spawner.base_phero = base_pheromone
        self.decay = rho
        
        # добавить определение начальных и конечных точек
        self.start = start
        self.end = end
   
    def pheromone_decay(self):
        """Уменьшение кол-ва феромона"""
        self.ant_spawner.base_phero *= (1 - self.decay)
 
        for e in self.ant_spawner.assoc_graph.edges:
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
            paths = []
            print('Iter #', i+1)
            # поиск решения
            for a_num, a in enumerate(self.ants):
                print('Ant#', a_num+1)
                while a.pos != self.end:
                    a.pick_edge()
                a.remove_cycles()
                length = a.path_len
                print('Ant#', a_num+1, 'finished, path len:', length)
                paths.append(length)
                
            # обновление феромона
            self.pheromone_decay()
            for a in self.ants:
                a.distribute_pheromone()
                a.unwind_path()
            
            best_paths.append(min(paths))
            worst_paths.append(max(paths))
            avg_paths.append(sum(paths)/ants_n)

        return best_paths, worst_paths, avg_paths

