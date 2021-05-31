from numpy import inf
import numpy.random as random
from copy import deepcopy

from logger import log


class BaseAnt:
    """Класс, моделирующий поведение муравья"""
    def __init__(self, a, b, graph, start, end):
        self.alpha = a
        self.beta = b
        self.g = graph
        self.target = end

        # мн-во посещенных вершин
        self.visited = set([start])
        # длина отступления
        self.fallback_len = 0
        # сколько еще нужно возвращаться после отступления
        self.required_fallback = 0
        # путь
        self.path = [start]

    @property
    def pos(self):
        return self.path[-1]

    @pos.setter
    def pos(self, value):
        self.path.append(value)

    @property
    def path_len(self):
        P = self.path
        ret = sum(self.g.get_weight(v, w) for v, w in zip(P[:-1], P[1:]))
        return ret

    @property
    def complete(self):
        return self.pos == self.target

    # overridable base
    def attraction(self, v, w):
        Wg = self.g.get_weight(v, w)
        if Wg == inf:
            return 0.0
        else:
            Wg = 1 / Wg
        p = self.g.get_phi(v, w)
        return p ** self.alpha * Wg ** self.beta

    def reset(self):
        pass

    # overridable base
    def _fall_back(self):
        v = self.path.pop()
        if not self.path:
            if self.fallback_len == 1:
                raise RuntimeError('Something something terrible news!')
            else:
                self.path.append(v)
                self.fallback_len = 0
        else:
            self.visited.remove(v)

    def pick_edge(self):
        """Совершает перемещение в одну из соседних точек в графе G"""
        v = self.pos

        eligible = set(self.g.get_adjacent(v)) - self.visited
        targets = list(eligible)
        # привлекательности ребер
        attrs = [self.attraction(v, t) for t in targets]

        total_attr = sum(attrs)

        # некуда идти
        if total_attr == 0.0:
            log()['ATTR_DEBUG'].log('Total attr is 0, falling back')
            self.fallback_len += 1
            for i in range(self.fallback_len - self.required_fallback):
                self._fall_back()
            self.required_fallback = self.fallback_len
        # есть куда идти
        else:
            attr = [a / total_attr for a in attrs]
            # случайный выбор тут
            choice = random.choice(len(targets), p=attr)

            # добавить в путь
            self.pos = targets[choice]

            self.visited.add(targets[choice])
            if self.required_fallback > 0:
                self.required_fallback -= 1
            else:
                self.fallback_len = 0

    def deposit_pheromone(self, Q):
        """Распространяет феромон по всем пройденным ребрам"""
        if self.complete:
            G = self.g
            phi = Q / self.path_len
            log()['PHI_DEPOSIT'].log(f'{phi} pheromone.')
            for v, w in zip(self.path[:-1], self.path[1:]):
                G.add_phi(v, w, phi)
        else:
            log()['PHI_DEPOSIT'].log('no pheromone.')

    # overridable base
    def clone(self):
        ret = BaseAnt(self.alpha,
                    self.beta,
                    self.g,
                    self.pos,
                    self.target)

        ret.path = deepcopy(self.path)
        ret.visited = deepcopy(self.visited)
        ret.fallback_len = self.fallback_len
        ret.required_fallback = self.required_fallback

        return ret
