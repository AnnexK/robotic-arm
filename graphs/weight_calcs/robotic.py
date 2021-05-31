from env.robot import Robot
from math import inf
from logger import log


class RobotWeight:
    def __init__(self, R: Robot):
        self.origin = R.get_effector()
        self.R = R
        self.w = R.kin_eps

    def get(self, v, w):
        def moved_normally(R, target):
            m = R.move_to(target)
            col = R.check_collisions()
            if col:
                log()['COLLISION'].log('collision detected')
            return m and not col

        w_real = tuple(self.origin[i] + self.R.kin_eps * w[i]
                       for i in range(3))
        try:
            state = self.R.state
            ret = self.w if moved_normally(self.R, w_real) else inf
            self.R.state = state
        except ValueError:
            log()['FATAL'].log(f'reset state error, state was {state}')
            raise

        return ret
