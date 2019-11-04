from .ant_system import AntSystem


class ASRank(AntSystem):
    def __init__(self, G, Q, end, decay, rank_num):
        super().__init__(G, Q, end, decay)
        self.rank_n = rank_num

    def update_pheromone(self, ants):
        self.graph.evaporate(self.decay)

        ants.sort(key=lambda a: a.path_len)

        # если муравьев меньше, чем рангов,
        # то использовать количество муравьев
        # вместо количества рангов
        if len(ants) > self.rank_n:
            diff = 0
        else:
            diff = self.rank_n - len(self.ants)

        ranked_ants = self.rank_n - diff
        for r in range(ranked_ants):
            phi = self.ant_power * (ranked_ants - r)
            ants[r].deposit_pheromone(phi)
