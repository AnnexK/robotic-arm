import logging
from typing import TypeVar, Iterable
from roboticarm.solver.ants import BaseAnt
from roboticarm.graphs import PhiGraph
from roboticarm.solver.daemons import Daemon
from .ant_system import AntSystem


V = TypeVar("V")
_logger = logging.getLogger(__name__)


class ElitistAS(AntSystem[V]):
    def __init__(
        self,
        G: PhiGraph[V],
        Q: float,
        decay: float,
        limit: int,
        daemon: Daemon,
        Q_e: float,
    ):
        super().__init__(G, Q, decay, limit, daemon)
        self.elite_power = Q_e

    def update_pheromone(self, ants: Iterable[BaseAnt[V]]):
        super().update_pheromone(ants)
        L = self.best_length
        phi = self.elite_power / L
        bs = self.best_solution

        _logger.debug("Depositing %f pheromone", phi)
        for v, w in zip(bs[:-1], bs[1:]):
            self.graph.add_phi(v, w, phi)
