from roboticarm.graphs.gridgraph.vertex import GGVertex
from roboticarm.solver import RoboticGraphBuilder, CartesianAnt, ElitistAS, AntSolver
from roboticarm.solver import NullDaemon
from roboticarm.solver.aco_algorithms import ACOAlgorithm
import roboticarm.plotter as plotter
from roboticarm.plotter.null import NullPlotter
from roboticarm.env import Environment, Robot, State
from .acoparams import ACOParams
from .planner import Planner, Plan


class ACOStockPlanner(Planner):
    def __init__(self, aco: ACOParams, gamma: float, out: str, plot: bool):
        self.aco = aco
        self.gamma = gamma
        self.out = out
        self.plot = plot

    def plan(self, env: Environment, goal_state: State) -> Plan:
        if env.robot is None:
            raise Exception("Should not happen")
        else:
            R: Robot = env.robot
        ret: list[State] = [R.state]
        goal = env.target

        g = RoboticGraphBuilder(R, self.aco.phi).build_graph()

        eps = R.kin_eps

        origin = R.get_effector()
        diff = (
            goal[0] - origin[0],
            goal[1] - origin[1],
            goal[2] - origin[2],
        )

        vstart: GGVertex = (0, 0, 0)
        vend: GGVertex = (
            round(diff[0] / eps),
            round(diff[1] / eps),
            round(diff[2] / eps),
        )

        ant = CartesianAnt(
            self.aco.alpha, self.aco.beta, self.gamma, g, R, vstart, vend
        )

        alg: ACOAlgorithm[GGVertex] = ElitistAS(
            g, self.aco.q, self.aco.rho, self.aco.limit, NullDaemon(), self.aco.elite
        )

        S = AntSolver(alg, ant)
        W = plotter.csv_writer.CSVWriter(self.out, S.get_links())
        P = plotter.mpl_plotter.MPLPlotter() if self.plot else NullPlotter()
        for L in S.get_links():
            L.attach(P)

        path = S.solve(self.aco.i, self.aco.m)

        for v in path[1:]:
            o = (
                origin[0] + eps * v[0],
                origin[1] + eps * v[1],
                origin[2] + eps * v[2],
            )
            R.move_to(o)
            ret.append(R.state)

        del P
        del S
        del alg
        del ant
        del W

        return ret
