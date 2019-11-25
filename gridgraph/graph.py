class GridGraph:
    """Класс, моделирующий граф-решетку в трехмерном пространстве"""
    def __sum_fun(x, y):
        return x[0]+y[0], x[1]+y[1], x[2]+y[2]

    def __init__(self, weight, phi):
        """
        Инициализировать граф 
        с весовой функцией weight
        и менеджером феромона phi
        """

        # объект, вычисляющий веса ребер
        self.weight = weight
        # объект, управляющий уровнем феромона
        self.phi = phi

    def get_adjacent(self, v):
        """Возвращает список смежных вершин для вершины v"""
        vecs = [(1, 0, 0),
                (-1, 0, 0),
                (0, 1, 0),
                (0, -1, 0),
                (0, 0, 1),
                (0, 0, -1)]

        # точки, в которые можно попробовать попасть
        return map(GridGraph.__sum_fun, [v]*6, vecs)

    def get_weight(self, v, w):
        '''Вычисляет вес ребра между вершинами v и w'''
        return self.weight.get(v, w)

    def get_phi(self, v, w):
        '''Возвращает кол-во феромона между вершинами v и w'''
        if w in self.get_adjacent(v):
            return self.phi.get_phi(v, w)
        else:
            raise ValueError('Vertices not adjacent')

    def add_phi(self, v, w, val):
        '''Добавляет val феромона на ребро между v и w'''
        if w in self.get_adjacent(v):
            self.phi.add_phi(v, w, val)
        else:
            raise ValueError('Vertices not adjacent')

    def evaporate(self, value):
        '''Производит испарение феромона на всем графе'''
        if not (0 <= value <= 1):
            raise ValueError('Decay rate not in bounds (0 < rho < 1)')
        self.phi.evaporate(value)
