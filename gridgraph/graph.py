class GridGraph:
    """Класс, моделирующий граф-решетку в трехмерном пространстве"""
    def __sum_fun(x, y):
        return x[0]+y[0], x[1]+y[1], x[2]+y[2]

    def __init__(self, weight, base):
        """Инициализировать граф с количеством вершин Vx, Vy, Vz"""

        # объект, вычисляющий веса ребер
        self.weight = weight
        # общий для всех ребер уровень феромона
        self.common_phi = base
        # уровень феромона для каждого ребра
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

    def __get_keys(self, v, w):
        for i in range(3):
            if abs(v[i]-w[i]) == 1:
                return i, min(v, w)
        # не должно выбрасываться
        raise ValueError('No edge between vertices')

    def get_weight(self, v, w):
        '''Вычисляет вес ребра между вершинами v и w'''
        return self.weight.get(v, w)

    def get_phi(self, v, w):
        '''Возвращает кол-во феромона между вершинами v и w'''
        if w in self.get_adjacent(v):
            index, key = self.__get_keys(v, w)
            # по ребру (v, w) был отложен феромон
            if key in self._phi[index]:
                return self._phi[index][key] + self.common_phi
            else:
                return self.common_phi
        else:
            raise ValueError('Vertices not adjacent')

    def add_phi(self, v, w, val):
        '''Добавляет val феромона на ребро между v и w'''
        if w in self.get_adjacent(v):
            index, key = self.__get_keys(v, w)
            if key in self._phi[index]:
                self._phi[index][key] += val
            else:
                self._phi[index][key] = val
        else:
            raise ValueError('Vertices not adjacent')

    def evaporate(self, value):
        '''Производит испарение феромона на всем графе'''
        if not (0 < value < 1):
            raise ValueError('Decay rate not in bounds (0 < rho < 1)')
        self.common_phi *= (1 - value)
        for d in self._phi:
            for k in d:
                d[k] *= (1 - value)
