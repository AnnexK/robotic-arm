from ..vertex import GGVertex as V
from .manager import WeightManager
from env.robot import Robot
from env.types import State, Vector3
from math import inf, sqrt
from logger import log


class EuclidWeightManager(WeightManager):
    def __init__(self, R: Robot):
        self.robot = R
        self.origin = R.get_effector()

    def get_weight(self, v: V, w: V) -> float:
        def moved_normally(R: Robot, target: Vector3):
            m = R.move_to(target)
            col = R.check_collisions()
            if col:
                log()['COLLISION'].log('collision detected')
            return m and not col

        def euclid(s: State, e: State) -> float:
            return sqrt( sum((ec-sc)**2 for ec, sc in zip(e, s)) )
        
        o = self.origin

        e = self.robot.kin_eps

        w_real: Vector3 = (o[0]+e*w[0],
                           o[1]+e*w[1],
                           o[2]+e*w[2])
        state = self.robot.state
        ret = euclid(state, self.robot.state) if moved_normally(self.robot, w_real) else inf
        self.robot.state = state
        return ret