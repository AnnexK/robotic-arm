import numpy.random as random
from math import inf
from logger import log


class AntSystem:
    def __init__(self, G, Q, end, decay, limit):
        random.seed()
        self.graph = G
        self.ant_power = Q
        self.end = end
        self.rate = decay
        self.best_solution = {'length': inf,
                              'path': []}
        self.limit = inf if limit <= 0 else limit

    def generate_solutions(self, ants):
        lens = []
        for i, a in enumerate(ants):
            steps = 0
            log()['ANT'].log('Ant #{}'.format(i+1))
            while a.pos.vertex != self.end and steps < self.limit:
                a.pick_edge()
                steps += 1
                if steps % 1000 == 0:
                    log()['ANT'].log('{} steps'
                                     .format(steps))
            if a.pos.vertex != self.end:
                log()['ANT'].log(f'Ant #{i+1} hit the limit, aborting...')
                a.disable_deposit()
            else:
                pre_length = a.path_len

                log()['ANT'].log('Removing cycles...')
                a.remove_cycles()

                log()['ANT'].log('Cycles removed.')
                length = a.path_len
                lens.append(length)
                log()['ANT'].log('Ant #{} finished'.format(i+1))
                log()['ANT'].log('Path length: {}'.format(length))
                log()['ANT'].log('(pre-remove_cycles: {})'.format(pre_length))
                if length < self.best_solution['length']:
                    self.best_solution['length'] = length
                    self.best_solution['path'] = [(i.vertex, i.state)
                                                  for i in a.path]
            a.reset_robot()

        return (self.best_solution['length'],
                max(lens),
                sum(lens) / len(lens))

    def result(self):
        return self.best_solution['path']

    def update_pheromone(self, ants):
        # испарение
        self.graph.evaporate(self.rate)
        # отложение
        for a in ants:
            a.deposit_pheromone(self.ant_power)

    def daemon_actions(self):
        pass
