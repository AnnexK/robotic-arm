from .ant_system import AntSystem


class ASRank(AntSystem):
    def __init__(self, G, Q, end, decay, rank_num):
        super().__init__(G, Q, end, decay)
        self.rank_n = rank_num

    def update_pheromone(self):
        self.graph.evaporate(self.decay)

        self.ants.sort(key=lambda a: a.path_len)

        # если муравьев меньше, чем рангов,
        # то использовать количество муравьев
        # вместо количества рангов
        if len(self.ants) > self.rank_n:
            diff = 0
        else:
            diff = self.rank_n - len(self.ants)

        ranked_ants = self.rank_n - diff
        for r in range(ranked_ants):
            phi = self.ant_power * (ranked_ants - r)
            self.ants[r].update_pheromone(phi)
