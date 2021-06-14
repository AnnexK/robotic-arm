from plotter.plotter import PlotterLink
from logger import log
from plotter.plottable import Plottable, Link
from math import inf
from .aco_algorithms import ACOAlgorithm
from .ants import BaseAnt
from typing import Generic, Iterable, TypeVar


import traceback


V = TypeVar('V')


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
        try:
            while i <= iters:
                ants = [self.p_ant.clone() for _ in range(ants_n)]
                log()['SOLVER'].log(f'Iter {i}')
                self.S.generate_solutions(ants)
                if not any(a.complete for a in ants):
                    log()['SOLVER'].log(f'No results on iter {i}, restarting')
                else:
                    prev_avg = self.avg_iter.y
                    self.min_iter.set_point(float(i), min(self.min_iter.y, min(a.path_len for a in ants)))
                    self.max_iter.set_point(float(i), max(a.path_len for a in ants))
                    self.avg_iter.set_point(float(i), sum(a.path_len for a in ants) / len(ants))
                    self.min_iter.announce()
                    self.max_iter.announce()
                    self.avg_iter.announce()

                    self.S.update_pheromone(ants)
                    self.S.daemon_actions()
                    if i > 1 and self.avg_iter.y == prev_avg:
                        log()['SOLVER'].log(f'Same avg, times: {repeats+1}')
                        repeats = repeats + 1
                        if repeats == 10:
                            log()['SOLVER'].log(f'Too many repeats, wrapping up')
                            i = iters
                    else:
                        repeats = 0
                    i = i + 1
        except Exception as _:
            traceback.print_exc()
            log()['SOLVER'].log('Something bad happened, saving results...')
        finally:
            return self.S.result()
