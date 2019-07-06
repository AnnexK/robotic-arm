from gridgraph.graph import GridGraph
from gridgraph.edge import GraphEdge
from solver.ant import AntFactory

import numpy.random as nprand
from functools import reduce
from numpy import abs, ndarray, inf

class AntSolver:
    """Класс, моделирующий решение задачи"""
    def __init__(self,
                 G, start, end,
                 a=1.0, b=1.0, q=1.0, rho=0.01):
    
        self.graph = G
        self.ant_spawner = AntFactory(a, b, q, G, start)
        self.decay = rho
        
        # добавить определение начальных и конечных точек
        self.start = start
        self.end = end
   
    def pheromone_decay(self):
        """Уменьшение кол-ва феромона"""
        for e in self.graph.edges:
            e.phi *= (1 - self.decay)

    def solve(self, iters=1, ants_n=20):

        nprand.seed()
        # создаем муравьев один раз,
        # а потом в каждой итерации откатываем их состояние
        # к начальному        
        ants = self.ant_spawner.make_ants(ants_n)
        
        best_paths = []
        worst_paths = []
        avg_paths = []
        
        for i in range(iters):
            paths = []
            print('Iter #', i+1)
            # поиск решения
            for a_num, a in enumerate(ants):
                print('Ant#', a_num+1)
                while a.pos != self.end:
                    a.pick_edge()
                a.remove_cycles()
                length = a.path_len
                print('Ant#', a_num+1, 'finished, path len:', length)
                paths.append(length)
                
            # обновление феромона
            self.pheromone_decay()
            for a in ants:
                a.distribute_pheromone()
                a.unwind_path()
            
            best_paths.append(min(paths))
            worst_paths.append(max(paths))
            avg_paths.append(sum(paths)/ants_n)

        return best_paths, worst_paths, avg_paths

