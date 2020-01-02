from logger import log


class AntSolver:
    """Класс, моделирующий решение задачи"""
    def __init__(self, strat, ant):
        self.S = strat
        self.p_ant = ant
        self.ants = None

    def make_ants(self, num):
        if self.ants is None:
            self.ants = [self.p_ant.clone() for i in range(num)]
        else:
            for a in self.ants:
                a.reset()
        return self.ants

    def solve(self, iters=1, ants_n=20):
        best_paths = []
        worst_paths = []
        avg_paths = []
        i = 1
        repeats = 0
        while i <= iters:
            ants = self.make_ants(ants_n)
            log()['SOLVER'].log(f'Iter {i}')
            best, worst, avg = self.S.generate_solutions(ants)
            if best is None:
                log()['SOLVER'].log(f'No results on iter {i}, restarting')
            else:
                best_paths.append(best)
                worst_paths.append(worst)
                avg_paths.append(avg)
                self.S.update_pheromone(ants)
                self.S.daemon_actions()
                if i > 1 and avg_paths[-1] == avg_paths[-2]:
                    log()['SOLVER'].log(f'Same avg, times: {repeats+1}')
                    repeats = repeats + 1
                    if repeats == 10:
                        log()['SOLVER'].log(f'Too many repeats, wrapping up')
                        best_paths += [best_paths[-1]] * (iters-i)
                        worst_paths += [worst_paths[-1]] * (iters-i)
                        avg_paths += [avg_paths[-1]] * (iters-i)
                        i = iters
                else:
                    repeats = 0
            i = i + 1


        return best_paths, worst_paths, avg_paths, self.S.result()
