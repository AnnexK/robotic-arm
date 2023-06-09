from copy import deepcopy

from math import acos, sqrt

from roboticarm.graphs.gridgraph.vertex import GGVertex as V
from roboticarm.graphs import PhiGraph
from roboticarm.env.robot import Robot
from roboticarm.env.types import Vector3
from .base import BaseAnt as Ant


class CartesianAnt(Ant[V]):
    """Класс, моделирующий поведение муравья для старого алгоритма"""

    def __init__(
        self,
        a: float,
        b: float,
        g: float,
        graph: PhiGraph[V],
        robot: Robot,
        start: V,
        end: V,
    ):
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
    def pos(self) -> V:
        return super().pos

    @pos.setter
    def pos(self, value: V):
        # вычисляем вес и добавляем в список
        prev_pos = super().pos

        # вызов сеттера для свойства базового класса
        super(CartesianAnt, CartesianAnt).pos.fset(self, value)  # type: ignore

        self.weights.append(self.g.get_weight(prev_pos, value))

        # перемещаем робота в вершину
        step = self.robot.kin_eps
        new_eff: Vector3 = (
            self.origin[0] + step * value[0],
            self.origin[1] + step * value[1],
            self.origin[2] + step * value[2],
        )

        self.robot.move_to(new_eff)
        self.states.append(self.robot.state)

    @property
    def path_len(self) -> float:
        return sum(self.weights)

    def _orient_angle(self, v: V, w: V) -> float:
        if self.gamma == 0.0:
            return 1.0

        move_vec = tuple(w_i - v_i for w_i, v_i in zip(w, v))
        end_vec = tuple(e_i - p_i for e_i, p_i in zip(self.target, self.pos))

        end_vec_len = sqrt(sum(c * c for c in end_vec))
        dot_pr = sum(a * b for a, b in zip(move_vec, end_vec))

        theta = acos(dot_pr / end_vec_len)
        return theta

    def attraction(self, v: V, w: V) -> float:
        val = super().attraction(v, w)
        th = self._orient_angle(v, w)
        u = 1 / (1 + th)
        return val * u**self.gamma

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
    def clone(self) -> Ant[V]:
        ret = CartesianAnt(
            self.alpha, self.beta, self.gamma, self.g, self.robot, self.pos, self.target
        )
        ret.path = deepcopy(self.path)
        ret.states = deepcopy(self.states)
        ret.weights = deepcopy(self.weights)
        ret.visited = deepcopy(self.visited)
        ret.origin = self.origin
        ret.fallback_len = self.fallback_len
        ret.required_fallback = self.required_fallback
        return ret
