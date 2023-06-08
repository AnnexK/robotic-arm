from typing import Sequence

import numpy.random as random

from roboticarm.env.types import State
from roboticarm.env.robot import Robot

from .nearest.nearest import KNearest
from .prmgraph import PRMGraph


class PRM:
    def __init__(self, n: int, near: KNearest, robot: Robot, phi: float):
        self.n = n
        self.near = near
        self.robot = robot
        self.rng: random.Generator = random.default_rng()
        self.nsteps = 25
        self.phi = phi

    def generate_vertex(self) -> State:
        size = len(self.robot.state)
        while True:
            s = self.rng.random(size)
            v = tuple(
                (u - l) * s[i] + l
                for i, (u, l) in enumerate(zip(self.robot.upper, self.robot.lower))
            )
            self.robot.state = v
            if not self.robot.check_collisions():
                return v

    def find_nearest(self, v: State) -> Sequence[State]:
        return self.near.nearest(v, self.n)

    def try_connect(self, graph: PRMGraph, v: State, w: State):
        diff = tuple((wc - vc) / self.nsteps for wc, vc in zip(w, v))

        def next_config(cur: State) -> State:
            return tuple(c + d for c, d in zip(cur, diff))

        cur = next_config(v)
        for _ in range(self.nsteps):
            self.robot.state = cur
            if self.robot.check_collisions():
                return
            cur = next_config(cur)
        graph.add_edge(v, w, self.near.metric()(v, w), self.phi)
