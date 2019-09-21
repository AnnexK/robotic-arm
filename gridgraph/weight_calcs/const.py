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

