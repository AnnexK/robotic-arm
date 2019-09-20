class AntSolver:
    """Класс, моделирующий решение задачи"""
    def __init__(self, strat):
        self.S = strat

    def solve(self, iters=1, ants_n=20):
        best_paths = []
        worst_paths = []
        avg_paths = []

        for i in range(iters):
            self.S.make_ants(ants_n)
            print('Iter #', i + 1)
            best, worst, avg = self.S.generate_solutions()
            best_paths.append(best)
            worst_paths.append(worst)
            avg_paths.append(avg)
            self.S.update_pheromone()
            self.S.daemon_actions()

        return best_paths, worst_paths, avg_paths, self.S.result()
