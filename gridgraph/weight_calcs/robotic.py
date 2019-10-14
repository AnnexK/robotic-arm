from env.robot import Robot
from math import inf


class RobotWeight:
    def __init__(self, R: Robot):
        self.origin = R.get_effector()
        self.R = R

    def get(self, v, w):
        def moved_normally(R, target):
            return R.move_to(target) and not R.check_collisions()

        w_real = tuple(self.origin[i] + self.R.kin_eps * w[i] for i in range(3))

        state = self.R.state
        ret = 1.0 if moved_normally(self.R, w_real) else inf
        self.R.state = state

        return ret
