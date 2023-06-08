from __future__ import annotations

import logging
from typing import Generic, TypeVar
from copy import deepcopy
from numpy import inf
import numpy.random as random

from roboticarm.graphs import PhiGraph

_logger = logging.getLogger(__name__)
V = TypeVar("V")


class BaseAnt(Generic[V]):
    """Класс, моделирующий поведение муравья"""

    def __init__(self, a: float, b: float, graph: PhiGraph[V], start: V, end: V):
        self.alpha = a
        self.beta = b
        self.g = graph
        self.target = end

        # мн-во посещенных вершин
        self.visited = set([start])
        # длина отступления
        self.fallback_len: int = 0
        # сколько еще нужно возвращаться после отступления
        self.required_fallback: int = 0
        # путь
        self.path = [start]

    @property
    def pos(self) -> V:
        return self.path[-1]

    @pos.setter
    def pos(self, value: V):
        self.path.append(value)

    @property
    def path_len(self) -> float:
        P = self.path
        ret = sum(self.g.get_weight(v, w) for v, w in zip(P[:-1], P[1:]))
        return ret

    @property
    def complete(self) -> bool:
        return self.pos == self.target

    # overridable base
    def attraction(self, v: V, w: V):
        Wg = self.g.get_weight(v, w)
        if Wg == inf:
            return 0.0
        else:
            Wg = 1 / Wg
        p = self.g.get_phi(v, w)
        return p**self.alpha * Wg**self.beta

    def reset(self):
        pass

    # overridable base
    def _fall_back(self):
        v = self.path.pop()
        if not self.path:
            if self.fallback_len == 1:
                raise RuntimeError("Something something terrible news!")
            else:
                self.path.append(v)
                self.fallback_len = 0
        else:
            self.visited.remove(v)

    def pick_edge(self) -> None:
        """Совершает перемещение в одну из соседних точек в графе G"""
        v = self.pos

        eligible = set(self.g.get_adjacent(v)) - self.visited
        targets = list(eligible)
        # привлекательности ребер
        attrs = [self.attraction(v, t) for t in targets]

        total_attr: float = sum(attrs)

        # некуда идти
        if total_attr == 0.0:
            _logger.debug("Total attraction value is 0, falling back")
            self.fallback_len += 1
            for _ in range(self.fallback_len - self.required_fallback):
                self._fall_back()
            self.required_fallback = self.fallback_len
        # есть куда идти
        else:
            attr = [a / total_attr for a in attrs]
            # случайный выбор тут
            choice: int = random.choice(len(targets), p=attr)

            # добавить в путь
            self.pos = targets[choice]

            self.visited.add(targets[choice])
            if self.required_fallback > 0:
                self.required_fallback -= 1
            else:
                self.fallback_len = 0

    def deposit_pheromone(self, Q: float):
        """Распространяет феромон по всем пройденным ребрам"""
        if self.complete:
            G = self.g
            phi = Q / self.path_len
            _logger.debug("Depositing %f pheromone", phi)
            for v, w in zip(self.path[:-1], self.path[1:]):
                G.add_phi(v, w, phi)
        else:
            _logger.debug("Depositing no pheromone")

    # overridable base
    def clone(self) -> BaseAnt[V]:
        ret: BaseAnt[V] = BaseAnt(self.alpha, self.beta, self.g, self.pos, self.target)

        ret.path = deepcopy(self.path)
        ret.visited = deepcopy(self.visited)
        ret.fallback_len = self.fallback_len
        ret.required_fallback = self.required_fallback

        return ret
