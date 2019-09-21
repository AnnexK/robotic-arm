class GridGraph:
    """Класс, моделирующий граф-решетку в трехмерном пространстве"""
    def __sum_fun(x, y):
        return x[0]+y[0], x[1]+y[1], x[2]+y[2]

    def __init__(self, weight, base):
        """Инициализировать граф с количеством вершин Vx, Vy, Vz"""

        # количество ребер в каждой размерности
        self.weight = weight
        self.common_phi = base
        # X, Y, Z
        self._phi = [{},
                     {},
                     {}]

    def get_adjacent(self, v):
        """Возвращает список смежных вершин для вершины v"""
        vecs = [(1,0,0),
                (-1,0,0),
                (0,1,0),
                (0,-1,0),
                (0,0,1),
                (0,0,-1)]

        # точки, в которые можно попробовать попасть
        return map(GridGraph.__sum_fun, [v]*6, vecs)

    def get_weight(self, v, w):
        return self.weight.get(v, w)

    def get_phi(self, v, w):
        if w in self.get_adjacent(v):
            for i in range(3):
                if abs(v[i]-w[i]) == 1:
                    index = i
                    break
            if min(v,w) in self._phi[index]:
                return self._phi[index][min(v,w)] + self.common_phi
            else:
                return self.common_phi
        else:
            return None

    def add_phi(self, v, w, val):
        if w in self.get_adjacent(v):
            for i in range(3):
                if abs(v[i]-w[i]) == 1:
                    index = i
                    break
            if min(v,w) in self._phi[index]:
                self._phi[index][min(v,w)] += val
            else:
                self._phi[index][min(v,w)] = val
        else:
            raise ValueError('Vertices not adjacent')

    def evaporate(self, value):
        self.common_phi *= (1 - value)
        for d in self._phi:
            for k in d:
                d[k] *= (1-value)
