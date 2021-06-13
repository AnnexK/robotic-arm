from typing import Iterable
from ..phigraph import PhiGraph
from .wg_managers.manager import WeightManager
from .phi_managers.manager import PhiManager
from .vertex import GGVertex


class GridGraph(PhiGraph[GGVertex]):
    """Класс, моделирующий граф-решетку в трехмерном пространстве"""
    @staticmethod
    def __sum_fun(x: GGVertex, y: GGVertex) -> GGVertex:
        return x[0]+y[0], x[1]+y[1], x[2]+y[2]

    def __init__(self, weight: WeightManager, phi: PhiManager):
        """
        Инициализировать граф
        с весовой функцией weight
        и менеджером феромона phi
        """

        # объект, вычисляющий веса ребер
        self.weight = weight
        # объект, управляющий уровнем феромона
        self.phi = phi

    def get_adjacent(self, v: GGVertex) -> Iterable[GGVertex]:
        """Возвращает список смежных вершин для вершины v"""
        vecs = [(1, 0, 0),
                (-1, 0, 0),
                (0, 1, 0),
                (0, -1, 0),
                (0, 0, 1),
                (0, 0, -1)]

        # точки, в которые можно попробовать попасть
        return map(GridGraph.__sum_fun, [v]*6, vecs)

    def get_weight(self, v: GGVertex, w: GGVertex) -> float:
        '''Вычисляет вес ребра между вершинами v и w'''
        return self.weight.get_weight(v, w)

    def get_phi(self, v: GGVertex, w: GGVertex) -> float:
        '''Возвращает кол-во феромона между вершинами v и w'''
        if w in self.get_adjacent(v):
            return self.phi.get_phi(v, w)
        else:
            raise ValueError('Vertices not adjacent')

    def add_phi(self, v: GGVertex, w: GGVertex, val: float):
        '''Добавляет val феромона на ребро между v и w'''
        if w in self.get_adjacent(v):
            self.phi.add_phi(v, w, val)
        else:
            raise ValueError('Vertices not adjacent')

    def evaporate(self, rate: float):
        '''Производит испарение феромона на всем графе'''
        if not (0.0 <= rate <= 1.0):
            raise ValueError('Decay rate not in bounds (0 < rho < 1)')
        self.phi.evaporate(rate)
