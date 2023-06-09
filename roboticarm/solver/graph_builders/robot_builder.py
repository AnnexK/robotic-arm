from math import inf
from roboticarm.graphs.phigraph import PhiGraph
from roboticarm.graphs.gridgraph import GridGraph
from roboticarm.graphs.gridgraph.wg_managers.euclid import EuclidWeightManager as wm
from roboticarm.graphs.gridgraph.phi_managers.bounded import BoundedPhiManager as pm

from roboticarm.graphs.gridgraph.vertex import GGVertex
from roboticarm.env.robot import Robot
from .builder import GraphBuilder


class RoboticGraphBuilder(GraphBuilder[GGVertex]):
    def __init__(self, r: Robot, base: float):
        self.robot = r
        self.phi = base
        self.lower = 1e-8

    def build_graph(self) -> PhiGraph[GGVertex]:
        ret = GridGraph(wm(self.robot), pm(self.phi, self.lower, inf))

        return ret
