import numpy.random as random
from math import inf
from logger import log


class AntSystem:
    def __init__(self, G, Q, decay, limit):
        random.seed()
        self.graph = G
        self.ant_power = Q
        self.rate = decay
        self.best_solution = {'length': inf,
                              'path': []}
        self.limit = inf if limit <= 0 else limit

    def generate_solutions(self, ants):
        lens = []
        for i, a in enumerate(ants):
            steps = 0
            log()['ANT'].log('Ant #{}'.format(i+1))
            while not a.complete and steps < self.limit:
                a.pick_edge()
                steps += 1
                if steps % 10000 == 0:
                    log()['ANT'].log('{} '
                                     .format(steps))
            if not a.complete:
                log()['ANT'].log(f'Ant #{i+1} hit the limit, aborting...')
                a.disable_deposit()
            else:
                length = a.path_len
                lens.append(length)
                log()['ANT'].log('Ant #{} finished'.format(i+1))
                log()['ANT'].log('Path length: {}'.format(length))
                if length < self.best_solution['length']:
                    self.best_solution['length'] = length
                    self.best_solution['path'] = [(i.vertex, i.state)
                                                  for i in a.path]
            # вернуться к состоянию до итерации
            a.reset_iter()

        if lens == []:
            return (None, None, None)
        else:
            return (self.best_solution['length'],
                    max(lens),
                    sum(lens) / len(lens))

    def result(self):
        return self.best_solution['path']

    def update_pheromone(self, ants):
        # испарение
        self.graph.evaporate(self.rate)
        # отложение
        for i, a in enumerate(ants):
            log()['PHI_DEPOSIT'].log(f'Ant #{i+1} deposits: ')
            a.deposit_pheromone(self.ant_power)

    def daemon_actions(self):
        pass
