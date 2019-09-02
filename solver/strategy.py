from solver.ant import Ant
import numpy.random as random

class SimpleACO:
    def __init__(self, G, start, end, a, b, q, decay):
        random.seed()
        self.graph = G
        self.start = start
        self.end = end
        self.alpha = a
        self.beta = b
        self.qual = q
        self.rate = decay

    def make_ants(self, amount):
        self.ants = [Ant(self.alpha,self.beta,self.qual,self.graph,self.start) for i in range(amount)]

    def generate_solutions(self):
        lens = []
        for i, a in enumerate(self.ants):
            print('Ant #', i + 1)
            while a.pos != self.end:
                a.pick_edge()
            a.remove_cycles()
            length = a.path_len
            lens.append(length)
            print('Ant #', i + 1, 'finished, length:', length)
        return min(lens), max(lens), sum(lens) / len(lens)

    def update_pheromone(self):
        # испарение
        self.graph.evaporate(self.rate)
        # отложение
        for a in self.ants:
            a.deposit_pheromone()
            a.unwind_path()

    def daemon_actions(self):
        self.graph.weight_calculator.reset()
