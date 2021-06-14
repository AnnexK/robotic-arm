import numpy.random as random
from math import inf
from logger import log
from copy import deepcopy
from typing import TypeVar, List, Iterable, Sequence
from .algorithm import ACOAlgorithm
from ..daemons import Daemon
from graphs import PhiGraph
from ..ants import BaseAnt


V = TypeVar('V')


class AntSystem(ACOAlgorithm[V]):
    def __init__(self, G: PhiGraph[V], Q: float, decay: float, limit: int, daemon: Daemon):
        random.seed()
        self.graph = G
        self.ant_power = Q
        self.rate = decay
        # последовательность вершин лучшего решения
        self.best_solution: List[V] = []
        # длина лучшего решения
        self.best_length = inf
        self.limit = limit
        self.daemon = daemon
        
    def generate_solutions(self, ants: Iterable[BaseAnt[V]]):
        for i, a in enumerate(ants):
            steps: int = 0
            log()['ANT'].log('Ant #{}'.format(i+1))
            while not a.complete and self.limit and steps < self.limit:
                a.pick_edge()
                steps += 1
                if steps % 10000 == 0:
                    log()['ANT'].log('{} steps'
                                     .format(steps))
            if not a.complete:
                log()['ANT'].log(f'Ant #{i+1} hit the limit, aborting...')
            else:
                length = a.path_len
                log()['ANT'].log('Ant #{} finished'.format(i+1))
                log()['ANT'].log('Path length: {}'.format(length))
                if length < self.best_length:
                    self.best_length = length
                    self.best_solution = deepcopy(a.path)
            # вернуться к состоянию до итерации
            a.reset()

    def result(self) -> Sequence[V]:
        return self.best_solution

    def update_pheromone(self, ants: Iterable[BaseAnt[V]]):
        # испарение
        self.graph.evaporate(self.rate)
        # отложение
        for i, a in enumerate(ants):
            log()['PHI_DEPOSIT'].log(f'Ant #{i+1} deposits: ')
            a.deposit_pheromone(self.ant_power)

    def daemon_actions(self):
        self.daemon.daemon_actions()
