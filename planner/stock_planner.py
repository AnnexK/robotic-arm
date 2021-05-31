from solver import RoboticGraphBuilder, CartesianAnt, ElitistAS, AntSolver, NullDaemon
import plotter


class ACOStockPlanner:
    def __init__(self, aco, gamma, limit, elite):
        self.aco = aco
        self.gamma = gamma
        self.limit = limit
        self.elite = elite

    def plan(self, env, goal):
        R = env.robot
        ret = [R.state]

        g = RoboticGraphBuilder(
            R,
            goal,
            self.aco.phi
        ).make_graph()

        eps = R.kin_eps

        origin = R.get_effector()
        diff = tuple(goal[i] - origin[i] for i in range(3))

        vstart = (0, 0, 0)
        vend = tuple(round(diff[i] / eps) for i in range(3))

        ant = CartesianAnt(
            self.aco.alpha,
            self.aco.beta,
            self.gamma,
            g,
            R,
            vstart,
            vend
        )

        alg = ElitistAS(
            g,
            self.aco.q,
            self.aco.rho,
            self.limit,
            NullDaemon(),
            self.elite
        )

        S = AntSolver(alg, ant)

        W = plotter.csv_writer.CSVWriter('current.csv')
        plotter.mux.Mux().register_plotter_link(W, S, W.min_name, 'min')
        plotter.mux.Mux().register_plotter_link(W, S, W.max_name, 'max')
        plotter.mux.Mux().register_plotter_link(W, S, W.avg_name, 'avg')

        path = S.solve(self.aco.m, self.aco.i)

        for v in path[1:]:
            o = tuple(origin[i] + eps * v[i] for i in range(3))
            R.move_to(o)
            ret.append(R.state)

        del S
        del alg
        del ant
        del W

        return ret