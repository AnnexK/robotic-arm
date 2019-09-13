from env.robot import Robot
from math import inf

class ConstWeight:
    def __init__(self, c=1.0):
        self.w = c

    def get(self, v, w):
        return self.w
    

class BoundedConstWeight:
    def __init__(self, vx, vy, vz, c):
        self.x = vx
        self.y = vy
        self.z = vz
        self.w = c

    def _in_bounds(self, v):
        return 0 <= v[0] < self.x and 0 <= v[1] < self.y and 0 <= v[2] < self.z
    
    def get(self, v, w):
        if self._in_bounds(v) and self._in_bounds(w):
            return self.w
        else:
            return inf

        
class RobotWeight:
    def __init__(self, R : Robot):
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
