import numpy.random as random
from math import inf


class PRM:
    def __init__(self, n, metric, robot, phi):
        self.n = n
        self.metric = metric
        self.robot = robot
        self.rng = random.default_rng()
        self.nsteps = 25
        self.phi = phi

    def generate_vertex(self):
        size = len(self.robot.state)
        while True:
            s = self.rng.random(size)
            print(s)
            v = tuple(
                (u-l) * s[i] + l for i, (u, l) in enumerate(
                    zip(
                        self.robot.upper,
                        self.robot.lower
                    )
                )
            )
            print(v)
            self.robot.state = v
            if not self.robot.check_collisions():
                return v

    def find_nearest(self, graph, v):
        M = [(m, self.metric(v, m)) for m in graph.vertices if v != m]
        ret = []

        def order(x):
            # print(x)
            if x in ret:
                return inf
            else:
                return x[1]
        
        for i in range(self.n):
            print(i)
            print(ret)
            ret.append( min( M, key=order ) )
        return [r[0] for r in ret]

    def try_connect(self, graph, v, w):
        diff = tuple( (wc-vc)/self.nsteps for wc, vc in zip(w,v) )
        def next_config(cur):
            return tuple(c+d for c, d in zip(cur, diff))
        cur = next_config(v)
        for i in range(self.nsteps):
            self.robot.state = cur
            if self.robot.check_collisions():
                return
        graph.add_edge(v, w, self.metric(v, w), self.phi)
