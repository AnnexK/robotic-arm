from numpy import inf
import numpy.random as random
from copy import deepcopy

from logger import log
from math import acos, sqrt
from .base import BaseAnt as Ant


class CartesianAnt(Ant):
    """Класс, моделирующий поведение муравья для старого алгоритма"""
    def __init__(self, a, b, g, graph, robot, start, end):
        super().__init__(a, b, graph, start, end)

        # derived-specific
        self.robot = robot
        self.origin = self.robot.get_effector()
        # /derived-specific
        # состояния робота
        self.states = [self.robot.state]
        self.weights = [0.0]
        self.gamma = g

    @property
    def pos(self):
        return super().pos
    
    @pos.setter
    def pos(self, value):
        # вычисляем вес и добавляем в список
        prev_pos = super().pos
        super(CartesianAnt, CartesianAnt).pos.fset(self,value)
        self.weights.append(self.g.get_weight(prev_pos, value))

        # перемещаем робота в вершину
        step = self.robot.kin_eps
        new_eff = tuple(o+step*v
                        for o, v in zip(self.origin, value))
        self.robot.move_to(new_eff)
        self.states.append(self.robot.state)

    @property
    def path_len(self):
        return sum(self.weights)

    # derived-specific
    def _orient_angle(self, v, w):
        if self.gamma == 0.0:
            return 1.0

        move_vec = tuple(w_i - v_i for w_i, v_i in zip(w, v))
        end_vec = tuple(e_i - p_i for e_i, p_i in zip(self.target,
                                                      self.pos))

        end_vec_len = sqrt(sum(c * c for c in end_vec))
        dot_pr = sum(a * b for a, b in zip(move_vec, end_vec))

        theta = acos(dot_pr / end_vec_len)
        return theta
    # /derived-specific

    def attraction(self, v, w):
        val = super().attraction(v, w)
        th = self._orient_angle(v, w)
        u = 1 / (1 + th)
        return val * u ** self.gamma

    # overridable base
    def _fall_back(self):
        super()._fall_back()
        if len(self.path) < len(self.states):
            self.states.pop()
            self.robot.state = self.states[-1]

    def reset(self):
        super().reset()
        self.robot.state = self.states[0]
    
    # overridable base
    def clone(self):
        ret = CartesianAnt(self.alpha,
                           self.beta,
                           self.gamma,
                           self.g,
                           self.robot,
                           self.pos,
                           self.target)
        ret.path = deepcopy(self.path)
        ret.states = deepcopy(self.states)
        ret.weights = deepcopy(self.weights)
        ret.visited = deepcopy(self.visited)
        ret.origin = self.origin
        ret.fallback_len = self.fallback_len
        ret.required_fallback = self.required_fallback
        return ret
