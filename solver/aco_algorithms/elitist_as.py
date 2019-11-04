from .ant_system import AntSystem


class ElitistAS(AntSystem):
    def __init__(self, G, Q, end, decay, Q_e):
        super().__init__(G, Q, end, decay)
        self.elite_power = Q_e

    def update_pheromone(self, ants):
        super().update_pheromone(ants)
        phi = self.elite_power / self.best_solution['length']

        for v, w in zip(self.best_solution['path'][:-1],
                        self.best_solution['path'][1:]):
            self.graph.add_phi(v, w, phi)
