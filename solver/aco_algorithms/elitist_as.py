from .ant_system import AntSystem
from logger import log

class ElitistAS(AntSystem):
    def __init__(self, G, Q, end, decay, Q_e):
        super().__init__(G, Q, end, decay)
        self.elite_power = Q_e

    def update_pheromone(self, ants):
        super().update_pheromone(ants)
        path_len = self.best_solution['length']
        phi = self.elite_power / path_len

        log()['EAS'].log(f'depositing {phi} pheromone on len={path_len}')
        for v, w in zip(self.best_solution['path'][:-1],
                        self.best_solution['path'][1:]):
            self.graph.add_phi(v[0], w[0], phi)
