from numpy import inf
import numpy.random as random
from copy import deepcopy

from logger import log
from math import acos, sqrt


class AntPathData:
    """Содержимое запоминаемого пути муравья"""
    def __init__(self, v, weight, state):
        self.vertex = v
        self.weight = weight
        self.state = state


class Ant:
    """Класс, моделирующий поведение муравья"""
    def __init__(self, a, b, g, graph, robot, start, end):
        self.alpha = a
        self.beta = b
        self.gamma = g
        self.assoc_graph = graph
        self.robot = robot
        self.origin = self.robot.get_effector()

        self.path = [AntPathData(start, 0.0, self.robot.state)]
        self.target = end

        # мн-во посещенных вершин
        self.visited = set([start])
        # длина отступления
        self.fallback_len = 0
        # сколько еще нужно возвращаться после отступления
        self.required_fallback = 0

    @property
    def pos(self):
        return self.path[-1]

    @pos.setter
    def pos(self, value):
        self.path.append(value)

    @property
    def path_len(self):
        ret = sum(v.weight for v in self.path)
        return ret

    @property
    def complete(self):
        return self.pos.vertex == self.target

    def _orient_angle(self, v, w):
        move_vec = tuple(w_i - v_i for w_i, v_i in zip(w, v))
        end_vec = tuple(e_i - p_i for e_i, p_i in zip(self.target,
                                                      self.pos.vertex))

        end_vec_len = sqrt(sum(c * c for c in end_vec))
        dot_pr = sum(a * b for a, b in zip(move_vec, end_vec))

        theta = acos(dot_pr / end_vec_len)
        return theta

    def edge_attractions(self, w_list, p_list, orn_list):
        def attraction(w, p, th):
            if w == inf:
                return 0.0
            else:
                d = 1/w
                ang = 1/(1+th)
                return p ** self.alpha * (d ** self.beta) * ang ** self.gamma

        return [attraction(w, p, th)
                for p, w, th in zip(p_list, w_list, orn_list)]

    def _fall_back(self):
        v = self.path.pop()
        if not self.path:
            if self.fallback_len == 1:
                raise RuntimeError('Something something terrible news!')
            else:
                self.path.append(v)
                self.fallback_len = 0
        else:
            self.robot.state = self.pos.state
            self.visited.remove(v.vertex)

    def pick_edge(self):
        """Совершает перемещение в одну из соседних точек в графе G"""

        step = self.robot.kin_eps
        v = self.pos.vertex
        G = self.assoc_graph

        eligible = set(G.get_adjacent(v)) - self.visited
        targets = list(eligible)
        weights = [G.get_weight(v, t)
                   for t in targets]
        phi = [G.get_phi(v, t)
               for t in targets]
        orients = [self._orient_angle(v, t)
                   for t in targets]
        # привлекательности ребер
        attrs = self.edge_attractions(weights, phi, orients)

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

            self.robot.move_to(
                tuple(o + step * v
                      for o, v in zip(self.origin, targets[choice])))

            # добавить в путь (вершина, вес, состояние)
            self.pos = AntPathData(targets[choice],
                                   weights[choice],
                                   self.robot.state)
            self.visited.add(targets[choice])
            if self.required_fallback > 0:
                self.required_fallback -= 1
            else:
                self.fallback_len = 0

    def reset_iter(self):
        self.robot.state = self.path[0].state
        self.visited = set()
        self.visited.add(self.path[0].vertex)

    def disable_deposit(self):
        v = self.path[0]
        self.path.clear()
        self.path.append(v)

    def deposit_pheromone(self, Q):
        """Распространяет феромон по всем пройденным ребрам"""
        if self.complete:
            G = self.assoc_graph
            phi = Q / self.path_len
            log()['PHI_DEPOSIT'].log(f'{phi} pheromone.')
            for v, w in zip(self.path[0:-1], self.path[1:]):
                G.add_phi(v.vertex, w.vertex, phi)
        else:
            log()['PHI_DEPOSIT'].log('no pheromone.')

    def reset(self):
        """Возвращает муравья к начальному состоянию"""
        self.disable_deposit()
        self.visited = set()
        self.visited.add(self.path[0].vertex)
        self.fallback_len = 0
        self.required_fallback = 0

    def clone(self):
        ret = Ant(self.alpha,
                  self.beta,
                  self.gamma,
                  self.assoc_graph,
                  self.robot,
                  self.pos.vertex,
                  self.target)
        ret.path = deepcopy(self.path)
        ret.visited = deepcopy(self.visited)
        ret.origin = self.origin
        ret.fallback_len = self.fallback_len
        ret.required_fallback = self.required_fallback
        return ret
