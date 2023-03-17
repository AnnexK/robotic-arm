from env.types import Vector3
from env.robot import Robot
from math import inf
from logger import log
from .manager import WeightManager
from ..vertex import GGVertex


class RobotWeight(WeightManager):
    def __init__(self, R: Robot):
        self.origin = R.get_effector()
        self.R = R
        self.w = R.kin_eps

    def get_weight(self, v: GGVertex, w: GGVertex) -> float:
        def moved_normally(R: Robot, target: Vector3):
            m = R.move_to(target)
            col = R.check_collisions()
            if col:
                log()['COLLISION'].log('collision detected')
            return m and not col
        o = self.origin

        e = self.w

        w_real: Vector3 = (o[0]+e*w[0],
                           o[1]+e*w[1],
                           o[2]+e*w[2])
        state = self.R.state
        ret = self.w if moved_normally(self.R, w_real) else inf
        self.R.state = state

        return ret
