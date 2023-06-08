from typing import Tuple, Dict
from .manager import PhiManager

from roboticarm.graphs.gridgraph.vertex import GGVertex as V


class BasePhiManager(PhiManager):
    def __init__(self, base: float):
        self.common_phi = base
        self.phi: Dict[Tuple[V, V], float] = {}

    def _get_key(self, v: V, w: V) -> Tuple[V, V]:
        return min(v, w), max(v, w)

    def get_phi(self, v: V, w: V):
        key = self._get_key(v, w)
        ret = self.common_phi

        if key in self.phi:
            ret += self.phi[key]

        return ret

    def add_phi(self, v: V, w: V, val: float):
        key = self._get_key(v, w)

        if key in self.phi:
            self.phi[key] += val
        else:
            self.phi[key] = val

    def evaporate(self, rate: float):
        self.common_phi *= 1 - rate
        for k in self.phi:
            self.phi[k] *= 1 - rate
