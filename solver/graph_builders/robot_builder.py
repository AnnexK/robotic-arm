from graphs.graph import GridGraph
from graphs.weight_calcs.robotic import RobotWeight
from graphs.phi_managers.bounded import BoundedPhiManager as pm
from math import inf


class RoboticGraphBuilder:
    def __init__(self, r, end, base):
        self.robot = r
        self.phi = base
        self.end = end
        self.lower = 1e-8

    def make_graph(self):
        ret = GridGraph(
            RobotWeight(self.robot),
            pm(self.phi, self.lower, inf)
        )

        return ret
