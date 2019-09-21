from env.robot import Robot
from math import inf


class RobotWeight:
    def __init__(self, R: Robot):
        self.origin = R.get_effector()
        self.R = R

    def get(self, v, w):
        v_real = tuple(self.origin + self.R.kin_eps * v[i] for i in range(3))
        w_real = tuple(self.origin + self.R.kin_eps * w[i] for i in range(3))
        r_real = self.R.get_effector()

        if v_real != r_real:
            raise ValueError('Start vertex does not correspond to robot state')

        ret = 1.0 if self.R.move_to(w_real) else inf
        self.R.move_to(r_real)

        return ret
