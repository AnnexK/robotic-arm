from .ant_system import AntSystem
from logger import log

class ElitistAS(AntSystem):
    def __init__(self, G, Q, decay, limit, daemon, Q_e):
        super().__init__(G, Q, decay, limit, daemon)
        self.elite_power = Q_e

    def update_pheromone(self, ants):
        super().update_pheromone(ants)
        L = self.best_length
        phi = self.elite_power / L
        bs = self.best_solution

        log()['EAS'].log(f'depositing {phi} pheromone on len={L}')
        for v, w in zip(bs[:-1], bs[1:]):
            self.graph.add_phi(v, w, phi)
