from math import inf
from copy import deepcopy
from typing import TypeVar, List, Iterable, Sequence
import logging
import numpy.random as random
from roboticarm.solver.daemons import Daemon
from roboticarm.graphs import PhiGraph
from roboticarm.solver.ants import BaseAnt
from .algorithm import ACOAlgorithm


V = TypeVar("V")

_logger = logging.getLogger(__name__)


class AntSystem(ACOAlgorithm[V]):
    def __init__(
        self, G: PhiGraph[V], Q: float, decay: float, limit: int, daemon: Daemon
    ):
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
            _logger.debug("Ant #%d", i + 1)
            while not a.complete and self.limit and steps < self.limit:
                a.pick_edge()
                steps += 1
                if steps % 10000 == 0:
                    _logger.debug("%d steps", steps)
            if not a.complete:
                _logger.warning("Ant #%d has failed to find solution")
            else:
                length = a.path_len
                _logger.debug(
                    "Ant #%d finished; path length=%f; vtxlen=%d",
                    i + 1,
                    length,
                    len(a.path),
                )
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
            _logger.debug("Ant #%d deposits ", i + 1)
            a.deposit_pheromone(self.ant_power)

    def daemon_actions(self):
        self.daemon.daemon_actions()
