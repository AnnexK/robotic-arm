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


class AntPath:
    class PathNode:
        def __init__(self, data=None, prev=None, next=None):
            self.data = data
            self.next = self if next is None else next
            self.prev = self if prev is None else prev

    def __init__(self, v):
        self.sent = AntPath.PathNode()
        self.sent.next = AntPath.PathNode(v, self.sent, self.sent)
        self.sent.prev = self.sent.next

    class PathIter:
        def __init__(self, path):
            self.cur = path.start
            self.end = path.end

        def __next__(self):
            if self.cur == self.end.next:
                raise StopIteration

            ret = self.cur.data
            self.cur = self.cur.next
            return ret

    @property
    def start(self):
        return self.sent.next

    @property
    def end(self):
        return self.sent.prev

    def __iter__(self):
        return AntPath.PathIter(self)

    def append(self, data):
        new = AntPath.PathNode(data, self.end, self.sent)
        self.end.next = new
        self.sent.prev = new

    def extract(self, start, end):
        start.prev.next = end.next
        end.next.prev = start.prev
        cur = start
        while cur != end:
            cur = cur.next
            cur.prev.next = None
            cur.prev = None

    def pop(self):
        ret = self.end.data
        self.extract(self.end, self.end)
        return ret

    def clear(self):
        self.sent.prev = self.sent
        self.sent.next = self.sent


class Ant:
    """Класс, моделирующий поведение муравья"""
    def __init__(self, a, b, g, graph, robot, start, end):
        self.alpha = a
        self.beta = b
        self.gamma = g
        self.assoc_graph = graph
        self.robot = robot
        self.origin = self.robot.get_effector()

        self._path = AntPath(AntPathData(start,
                                         0.0,
                                         self.robot.state))

        self.target = end

    @property
    def pos(self):
        return self._path.end.data

    @pos.setter
    def pos(self, value):
        self._path.append(value)

    @property
    def path(self):
        return self._path

    @property
    def path_len(self):
        ret = sum(v.weight for v in self.path)
        return ret

    def _orient_angle(self, v, w):
        move_vec = tuple(w_i - v_i for w_i, v_i in zip(w, v))
        end_vec = tuple(e_i - p_i for e_i, p_i in zip(self.target,
                                                      self.pos.vertex))

        end_vec_len = sqrt(sum(c * c for c in end_vec))
        dot_pr = sum(a * b for a, b in zip(move_vec, end_vec))

        theta = acos(dot_pr / end_vec_len)
        return theta

    def edge_attractions(self, w_list, p_list, orn_list):
        return [p ** self.alpha * (1/w ** self.beta) * (1/(1+th)) ** self.gamma
                for p, w, th in zip(p_list, w_list, orn_list)]

    def _fall_back(self):
        self.path.pop()
        self.robot.state = self.pos.state

    def pick_edge(self):
        """Совершает перемещение в одну из соседних точек в графе G"""

        step = self.robot.kin_eps
        v = self.pos.vertex
        G = self.assoc_graph

        targets = list(G.get_adjacent(v))
        weights = [G.get_weight(v, t)
                   for t in targets]
        phi = [G.get_phi(v, t)
               for t in targets]
        orients = [self._orient_angle(v, t)
                   for t in targets]
        # привлекательности ребер
        attrs = self.edge_attractions(weights, phi, orients)

        total_attr = sum(attrs)

        if total_attr == 0.0:
            log()['ATTR_DEBUG'].log('Total attr is 0, falling back')
            self._fall_back()
            return

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
        step = self.robot.kin_eps


    def remove_cycles(self):
        """Извлекает циклы из пути"""
        cur_left = self._path.start
        while cur_left != self._path.end:
            cur_right = self._path.end
            while cur_right != cur_left:
                if cur_left.data.vertex == cur_right.data.vertex:
                    self._path.extract(cur_left.next, cur_right)
                    break
                cur_right = cur_right.prev
            cur_left = cur_left.next
        self.robot.state = self.path.start.data.state

    def deposit_pheromone(self, Q):
        """Распространяет феромон по всем пройденным ребрам"""
        G = self.assoc_graph
        phi = Q / self.path_len

        n = self._path.start
        while n != self._path.end:
            G.add_phi(n.data.vertex, n.next.data.vertex, phi)
            n = n.next

    def reset(self):
        """Возвращает муравья к начальному состоянию"""
        pos = self.path.start.data
        self._path.clear()
        self._path.append(pos)

    def clone(self):
        ret = Ant(self.alpha,
                  self.beta,
                  self.gamma,
                  self.assoc_graph,
                  self.robot,
                  self.pos.vertex,
                  self.target)
        ret._path = deepcopy(self._path)
        ret.origin = self.origin
        return ret
