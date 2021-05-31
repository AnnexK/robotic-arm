from logger import log
from plotter.plottable import Plottable
from plotter.mux import Mux, PMLink
from math import inf


import traceback


class AntSolver(Plottable):
    """Класс, моделирующий решение задачи"""
    def __init__(self, strat, ant):
        self.S = strat
        self.p_ant = ant
        self.min_iter = PMLink('min')
        self.max_iter = PMLink('max')
        self.avg_iter = PMLink('avg')
        Mux().register_plottable_link(self,self.min_iter)
        Mux().register_plottable_link(self,self.max_iter)
        Mux().register_plottable_link(self,self.avg_iter)
        self.min_iter.y = inf

    def __del__(self):
        Mux().deregister_plottable(self)
    
    def solve(self, iters=1, ants_n=20):
        i = 1
        repeats = 0
        try:
            while i <= iters:
                ants = [self.p_ant.clone() for i in range(ants_n)]
                log()['SOLVER'].log(f'Iter {i}')
                self.S.generate_solutions(ants)
                if not any(a.complete for a in ants):
                    log()['SOLVER'].log(f'No results on iter {i}, restarting')
                else:
                    prev_avg = self.avg_iter.y
                    self.min_iter.y = min(self.min_iter.y, min(a.path_len for a in ants))
                    self.max_iter.y = max(a.path_len for a in ants)
                    self.avg_iter.y = sum(a.path_len for a in ants) / len(ants)
                    self.min_iter.x = self.max_iter.x = self.avg_iter.x = float(i)
                    self.announce_point(self.min_iter)
                    self.announce_point(self.max_iter)
                    self.announce_point(self.avg_iter)

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
        except Exception as e:
            traceback.print_exc()
            log()['SOLVER'].log('Something bad happened, saving results...')
        finally:
            return self.S.result()
