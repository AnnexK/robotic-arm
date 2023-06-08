from typing import Iterable, TypeVar
from roboticarm.solver.daemons.daemon import Daemon
from roboticarm.graphs.phigraph import PhiGraph
from roboticarm.solver.ants import BaseAnt
from .ant_system import AntSystem


V = TypeVar("V")


class ASRank(AntSystem[V]):
    def __init__(
        self,
        G: PhiGraph[V],
        Q: float,
        decay: float,
        limit: int,
        rank_num: int,
        daemon: Daemon,
    ):
        super().__init__(G, Q, decay, limit, daemon)
        self.rank_n = rank_num

    def update_pheromone(self, ants: Iterable[BaseAnt[V]]):
        self.graph.evaporate(self.rate)
        seq = list(ants)
        seq.sort(key=lambda a: a.path_len)

        # если муравьев меньше, чем рангов,
        # то использовать количество муравьев
        # вместо количества рангов
        ranked_ants = min(self.rank_n, len(seq))

        for r in range(ranked_ants):
            phi = self.ant_power * (ranked_ants - r)
            seq[r].deposit_pheromone(phi)
