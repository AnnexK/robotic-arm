from math import inf, sqrt
from logging import getLogger
from roboticarm.graphs.gridgraph.vertex import GGVertex as V
from roboticarm.env.robot import Robot
from roboticarm.env.types import State, Vector3
from .manager import WeightManager


_logger = getLogger(__name__)


class EuclidWeightManager(WeightManager):
    def __init__(self, R: Robot):
        self.robot = R
        self.origin = R.get_effector()

    def get_weight(self, v: V, w: V) -> float:
        def moved_normally(R: Robot, target: Vector3) -> bool:
            m = R.move_to(target)
            col = R.check_collisions()
            if col:
                _logger.debug("Collision detected")
            return m and not col

        def euclid(s: State, e: State) -> float:
            return sqrt(sum((ec - sc) ** 2 for ec, sc in zip(e, s)))

        o = self.origin

        e = self.robot.kin_eps

        w_real: Vector3 = (o[0] + e * w[0], o[1] + e * w[1], o[2] + e * w[2])
        state = self.robot.state
        ret = (
            euclid(state, self.robot.state)
            if moved_normally(self.robot, w_real)
            else inf
        )
        self.robot.state = state
        return ret
