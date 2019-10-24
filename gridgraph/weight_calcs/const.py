from math import inf


class ConstWeight:
    def __init__(self, c=1.0):
        self.w = c

    def get(self, v, w):
        return self.w


class BoundedConstWeight:
    def __init__(self, dims, c):
        self.dims = dims
        self.w = c

    def _in_bounds(self, v):
        return all(map(lambda v, b: 0 <= v < b, v, self.dims))

    def get(self, v, w):
        if self._in_bounds(v) and self._in_bounds(w):
            return self.w
        else:
            return inf
