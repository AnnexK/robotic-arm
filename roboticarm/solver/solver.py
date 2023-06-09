import logging
from math import inf
from typing import Generic, Iterable, TypeVar, Deque
from collections import deque
import traceback

from roboticarm.plotter.plotter import PlotterLink
from roboticarm.plotter.plottable import Plottable, Link

from .aco_algorithms import ACOAlgorithm
from .ants import BaseAnt


V = TypeVar("V")
_logger = logging.getLogger(__name__)


class AvgCalculator:
    def __init__(self, d: int):
        self.sample: Deque[float] = deque(maxlen=d)

    def recalculate(self, val: float) -> float:
        self.sample.append(val)
        return sum(self.sample) / len(self.sample)


class AntSolver(Generic[V], Plottable):
    """Класс, моделирующий решение задачи"""

    def __init__(self, strat: ACOAlgorithm[V], ant: BaseAnt[V]):
        self.S = strat
        self.p_ant = ant
        self.min_iter = Link()
        self.max_iter = Link()
        self.avg_iter = Link()
        self.min_iter.set_point(0.0, inf)

    def get_links(self) -> Iterable[PlotterLink]:
        return (self.min_iter, self.max_iter, self.avg_iter)

    def solve(self, iters: int, ants_n: int):
        i: int = 1
        repeats: int = 0
        fails: int = 0
        max_repeats: int = 25
        avg = AvgCalculator(max_repeats)
        try:
            while i <= iters:
                ants = [self.p_ant.clone() for _ in range(ants_n)]
                _logger.debug("Iter %d", i)
                self.S.generate_solutions(ants)
                self.S.update_pheromone(ants)
                self.S.daemon_actions()

                ncompleted = 0
                for a in ants:
                    if a.complete:
                        ncompleted += 1

                if ncompleted == 0:
                    _logger.debug("No one completed on iter %d, restarting", i)
                    fails += 1
                    # TODO: убрать в конфиг
                    if fails == 10:
                        _logger.warning("Retry threshold exceeded; aborting")
                        i = iters
                else:
                    self.min_iter.set_point(
                        float(i),
                        min(
                            self.min_iter.y, min(a.path_len for a in ants if a.complete)
                        ),
                    )
                    self.max_iter.set_point(
                        float(i), max(a.path_len for a in ants if a.complete)
                    )
                    self.avg_iter.set_point(
                        float(i),
                        sum(a.path_len for a in ants if a.complete) / ncompleted,
                    )
                    self.min_iter.announce()
                    self.max_iter.announce()
                    self.avg_iter.announce()

                    it_avg = self.avg_iter.y
                    avg_avg = avg.recalculate(it_avg)
                    if abs(it_avg - avg_avg) / avg_avg < 0.01:
                        _logger.debug(
                            "No improvement on average for %d iters", repeats + 1
                        )
                        repeats = repeats + 1
                        if repeats == max_repeats:
                            _logger.debug("No improvement for too many iters")
                            i = iters
                    else:
                        repeats = 0
                    i = i + 1

        except Exception:
            traceback.print_exc()
            _logger.exception("Exception caught while solving, saving results")
        finally:
            return self.S.result()
