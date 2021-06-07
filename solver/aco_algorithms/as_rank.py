from .ant_system import AntSystem


class ASRank(AntSystem):
    def __init__(self, G, Q, decay, limit, rank_num, daemon):
        super().__init__(G, Q, decay, limit, daemon)
        self.rank_n = rank_num

    def update_pheromone(self, ants):
        self.graph.evaporate(self.decay)

        ants.sort(key=lambda a: a.path_len)

        # если муравьев меньше, чем рангов,
        # то использовать количество муравьев
        # вместо количества рангов
        ranked_ants = min(self.rank_n, len(ants))

        for r in range(ranked_ants):
            phi = self.ant_power * (ranked_ants - r)
            ants[r].deposit_pheromone(phi)
