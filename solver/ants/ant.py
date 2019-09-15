from numpy import inf
import numpy.random as random


def edge_attraction(edge, alpha, beta):
    """Вычисляет привлекательность ребра по формуле"""
    if edge[0] == inf:
        return 0.0
    return edge[1] ** alpha * (1 / edge[0]) ** beta


class AntPath:
    class PathNode:
        def __init__(self, data=None, prev=None, next=None):
            self.d = data
            self.next = self if next is None else next
            self.prev = self if prev is None else prev

    def __init__(self, v):
        self.sent = AntPath.PathNode()
        self.sent.next = AntPath.PathNode(v, self.sent, self.sent)
        self.sent.prev = self.sent.next

    @property
    def start(self):
        return self.sent.next

    @property
    def end(self):
        return self.sent.prev

    def append(self, v):
        new = AntPath.PathNode(v, self.end, self.sent)
        self.end.next = new
        self.sent.prev = new

    def extract(self, start, end):
        start.prev.next = end.next
        end.next.prev = start.prev

    def clear(self):
        self.sent.prev = self.sent
        self.sent.next = self.sent


class Ant:
    """Класс, моделирующий поведение муравья"""
    def __init__(self, a, b, Q, G, pos):
        self.alpha = a
        self.beta = b
        self.Q = Q
        self.assoc_graph = G
        self.path = AntPath((pos, 0.0))

    @property
    def pos(self):
        return self.path.end.d[0]

    @pos.setter
    def pos(self, value):
        self.path.append(value)

    @property
    def path_len(self):
        ret = 0.0
        n = self.path.start
        while n != self.path.sent:
            ret += n.d[1]
            n = n.next
        return ret

    def pick_edge(self):
        """Совершает перемещение в одну из соседних точек в графе G"""

        G = self.assoc_graph

        targets = list(G.get_adjacent(self.pos))
        # следует переделать в объект
        edges = [(G.get_weight(self.pos, t), G.get_phi(self.pos, t))
                 for t in targets]

        # привлекательности ребер
        attr = [edge_attraction(e,
                                self.alpha,
                                self.beta)
                for e in edges]

        total_attr = sum(attr)
        attr = [a / total_attr for a in attr]

        # случайный выбор тут
        choice = random.choice(len(edges), p=attr)

        # добавить в путь (вершина, вес)
        self.pos = targets[choice], edges[choice][0]

    def remove_cycles(self):
        """Извлекает циклы из пути"""
        cur_left = self.path.start
        while cur_left != self.path.end:
            cur_right = self.path.end
            while cur_right != cur_left:
                if cur_left.d[0] == cur_right.d[0]:
                    self.path.extract(cur_left.next, cur_right)
                    break
                cur_right = cur_right.prev
            cur_left = cur_left.next

    def deposit_pheromone(self):
        """Распространяет феромон по всем пройденным ребрам"""
        G = self.assoc_graph
        phi = self.Q / self.path_len

        n = self.path.start
        while n != self.path.end:
            G.add_phi(n.d[0], n.next.d[0], phi)
            n = n.next

    def reset(self):
        """Возвращает муравья к начальному состоянию"""

        pos = self.path.start.d
        self.path.clear()
        self.path.append(pos)
