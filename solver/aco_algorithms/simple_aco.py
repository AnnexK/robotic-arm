import numpy.random as random
from math import inf


class SimpleACO:
    def __init__(self, G, end, decay):
        random.seed()
        self.graph = G
        self.end = end
        self.rate = decay
        self.ants = None
        self.proto_ant = None
        self.best_solution = {'length': inf,
                              'path': []}

    def make_ants(self, amount):
        if self.proto_ant is None:
            raise TypeError('No ant specified')

        if self.ants is None:
            self.ants = [self.proto_ant.clone()
                         for i in range(amount)]

    def generate_solutions(self):
        lens = []
        for i, a in enumerate(self.ants):
            print('Ant #', i + 1)
            while a.pos != self.end:
                a.pick_edge()
            pre_length = a.path_len
            a.remove_cycles()
            length = a.path_len
            lens.append(length)
            print('Ant # {} finished, length: {} ({})'
                  .format(i+1, length, pre_length))
            if length < self.best_solution['length']:
                self.best_solution['length'] = length
                self.best_solution['path'] = [i[0] for i in a.path]
        return (min(lens),
                max(lens),
                sum(lens) / len(lens))

    def result(self):
        return self.best_solution['path']

    def set_proto(self, p):
        self.proto_ant = p

    def update_pheromone(self):
        # испарение
        self.graph.evaporate(self.rate)
        # отложение
        for a in self.ants:
            a.deposit_pheromone()
            a.reset()

    def daemon_actions(self):
        pass