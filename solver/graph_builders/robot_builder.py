from graphs.phigraph import PhiGraph
from graphs.gridgraph import GridGraph
from graphs.gridgraph.wg_managers.euclid import EuclidWeightManager as wm
from graphs.gridgraph.phi_managers.bounded import BoundedPhiManager as pm
from .builder import GraphBuilder
from graphs.gridgraph.vertex import GGVertex
from env.robot import Robot

from math import inf


class RoboticGraphBuilder(GraphBuilder[GGVertex]):
    def __init__(self, r: Robot, base: float):
        self.robot = r
        self.phi = base
        self.lower = 1e-8

    def build_graph(self) -> PhiGraph[GGVertex]:
        ret = GridGraph(
            wm(self.robot),
            pm(self.phi, self.lower, inf)
        )

        return ret
