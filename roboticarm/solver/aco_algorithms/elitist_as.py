from .ant_system import AntSystem
from logger import log
from typing import TypeVar, Iterable
from graphs import PhiGraph
from ..daemons import Daemon
from ..ants import BaseAnt


V = TypeVar('V')


class ElitistAS(AntSystem[V]):
    def __init__(self, G: PhiGraph[V], Q: float, decay: float, limit: int, daemon: Daemon, Q_e: float):
        super().__init__(G, Q, decay, limit, daemon)
        self.elite_power = Q_e

    def update_pheromone(self, ants: Iterable[BaseAnt[V]]):
        super().update_pheromone(ants)
        L = self.best_length
        phi = self.elite_power / L
        bs = self.best_solution

        log()['EAS'].log(f'depositing {phi} pheromone on len={L}')
        for v, w in zip(bs[:-1], bs[1:]):
            self.graph.add_phi(v, w, phi)
