from math import inf
import numpy.random as random

def edge_attraction(phi, dist, alpha, beta):
    """Вычисляет привлекательность ребра по формуле"""
    return phi ** alpha * (1 / dist) ** beta

class Ant:
    """Класс, моделирующий поведение муравья"""
    # коэф привлекательности по феромону
    alpha = 0.0
    # коэф привлекательности по длине ребра
    beta = 0.0
    # базовый уровень феромона
    base_phero = 0.0
    # граф, в котором происходит поиск решения (reference)
    assoc_graph = None
    # сколько всего феромона откладывает муравей
    Q = 1.0
    
    def __init__(self, pos):
        self.pos = pos # текущее положение в сетке
        self.path_len = 0.0 # длина текущего пути
        self.path_edges = [] # стек с ребрами
        self.path_verts = [pos] # стек с вершинами

    @property
    def pos(self):
        return self._grid_pos

    @pos.setter
    def pos(self, value):
        if not isinstance(value, tuple):
            raise TypeError("Передан не кортеж")
        if not len(value) == 3:
            raise ValueError("Значение не является точкой")
        # NB : использовать другой метод
        if not Ant.assoc_graph.grid_to_origin(value):
            raise ValueError("Точка не принадлежит графу")
        self._grid_pos = value

    def pick_edge(self):
        """Совершает перемещение в одну из соседних точек в графе G"""

        G = self.assoc_graph

        targets = list(G.get_adjacent(self.pos))
        edges = [G[self.pos, t] for t in targets]
        
        # привлекательности ребер
        attr = [edge_attraction(self.base_phero + e.phi,
                                e.weight,
                                self.alpha,
                                self.beta)
                if e.weight != inf # inf значит ребра нет
                else 0.0
                for e in edges]
        
        total_attr = sum(attr)
        attr = [a / total_attr for a in attr]
        
        # случайный выбор тут
        choice = random.choice(len(edges), p=attr)
        
        # добавить в стек
        self.path_edges.append(edges[choice]) 
        self.path_verts.append(targets[choice])
        self.path_len += edges[choice].weight
        self.pos = targets[choice]

    def distribute_pheromone(self):
        """Распространяет феромон по всем пройденным ребрам"""
        phi = self.Q / self.path_len
        
        for e in self.path_edges:
            e.phi = e.phi + phi

    def unwind_path(self):
        """Возвращает муравья к начальному состоянию и возвращает
длину пройденного им пути"""
        ret = self.path_len

        self.pos = self.path_verts[0]
        self.path_verts.clear()
        self.path_verts.append(self.pos)
        
        self.path_edges.clear()
        self.path_len = 0.0
        
        return ret