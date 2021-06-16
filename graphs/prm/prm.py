from typing import Sequence, Tuple, List
from env.types import State
import numpy.random as random
from math import inf
from .metrics import Metric
from .prmgraph import PRMGraph
from env.robot import Robot


class PRM:
    def __init__(self, n: int, metric: Metric, robot: Robot, phi: float):
        self.n = n
        self.metric = metric
        self.robot = robot
        self.rng: random.Generator = random.default_rng()
        self.nsteps = 25
        self.phi = phi

    def generate_vertex(self) -> State:
        size = len(self.robot.state)
        while True:
            s = self.rng.random(size)
            v = tuple(
                (u-l) * s[i] + l for i, (u, l) in enumerate(
                    zip(
                        self.robot.upper,
                        self.robot.lower
                    )
                )
            )
            self.robot.state = v
            if not self.robot.check_collisions():
                return v

    def find_nearest(self, graph: PRMGraph, v: State) -> Sequence[State]:
        M = [(m, self.metric(v, m)) for m in graph.vertices if v != m]
        ret: List[State] = []

        def order(x: Tuple[State, float]):
            if x[0] in ret:
                return inf
            else:
                return x[1]
        
        for _ in range(self.n):
            ret.append( min( M, key=order )[0] )
        return ret

    def try_connect(self, graph: PRMGraph, v: State, w: State):
        diff = tuple( (wc-vc)/self.nsteps for wc, vc in zip(w,v) )
        def next_config(cur: State) -> State:
            return tuple(c+d for c, d in zip(cur, diff))
        cur = next_config(v)
        for _ in range(self.nsteps):
            self.robot.state = cur
            if self.robot.check_collisions():
                return
            cur = next_config(cur)
        graph.add_edge(v, w, self.metric(v, w), self.phi)
