from typing import Iterable, Sequence, Tuple

from roboticarm.graphs.prm.metrics.metric import Metric
from roboticarm.env.types import State
from roboticarm.util.quickselect import quickselect

from .nearest import KNearest


class BruteforceNearest(KNearest):
    def __init__(self, metric: Metric, states: Iterable[State] = []):
        self.states = set(states)
        self._metric = metric

    def insert(self, p: State):
        self.states.add(p)

    def delete(self, p: State):
        self.states.discard(p)

    def _less(self, x: Tuple[State, float], y: Tuple[State, float]) -> bool:
        return x[1] < y[1]

    def metric(self) -> Metric:
        return self._metric

    def nearest(self, p: State, k: int) -> Sequence[State]:
        ret = list((s, self._metric(p, s)) for s in self.states)
        quickselect(ret, k, self._less)
        return [r[0] for r in ret[:k]]

    def __len__(self) -> int:
        return len(self.states)
