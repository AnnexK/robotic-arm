from solver import BaseAnt, ElitistAS, AntSolver, NullDaemon, PRMRerouteDaemon
import plotter
from graphs.linkgraph import LinkGraph
from graphs.prm.prm import PRM
from graphs.metrics.eff_movement import EffectorDisplacementMetric
from graphs.metrics.euclid import EuclideanMetric

class ACOPRMPlanner:
    def __init__(self, aco, prm, limit, elite):
        self.aco = aco
        self.limit = limit
        self.elite = elite
        self.prm = prm

    def plan(self, env, goal):
        R = env.robot
        vstart = R.state
        if R.check_collisions():
            raise Exception('Init configuration in obstacle space!')

        g = LinkGraph()
        prm = PRM(
            self.prm.n,
            EuclideanMetric(),
            R,
            self.aco.phi
        )

        # PRM build phase
        for i in range(self.prm.k):
            v = prm.generate_vertex()
            g.add_vertex(v)
        for v in g.vertices:
            nearest = prm.find_nearest(g, v)
            for n in nearest:
                prm.try_connect(g, v, n)

        R.state = vstart
        gen_tries = 0
        max_tries = 15000
        # Goal config generation
        while gen_tries < max_tries:
            if R.move_to(goal) and not R.check_collisions():
                break
            R.state = prm.generate_vertex()
            gen_tries += 1
        if gen_tries == max_tries:
            raise Exception('Could not generate goal state!')
        vend = R.state

        # добавить начальную и конечную вершины если их еще не добавило
        try:
            g.add_vertex(vstart)
            nearest = prm.find_nearest(g, vstart)
            for n in nearest:
                prm.try_connect(g, vstart, n)
        except ValueError:
            pass

        try:
            g.add_vertex(vend)
            nearest = prm.find_nearest(g, vend)
            for n in nearest:
                prm.try_connect(g, vend, n)
        except ValueError:
            pass

        ant = BaseAnt(
            self.aco.alpha,
            self.aco.beta,
            g,
            vstart,
            vend
        )

        reroute = PRMRerouteDaemon(NullDaemon(), g, self.prm.thresh, prm)
        alg = ElitistAS(
            g,
            self.aco.q,
            self.aco.rho,
            self.limit,
            reroute,
            self.elite
        )

        S = AntSolver(alg, ant)

        W = plotter.csv_writer.CSVWriter('current.csv')
        plotter.mux.Mux().register_plotter_link(W, S, W.min_name, 'min')
        plotter.mux.Mux().register_plotter_link(W, S, W.max_name, 'max')
        plotter.mux.Mux().register_plotter_link(W, S, W.avg_name, 'avg')

        Plot = plotter.mpl_plotter.MPLPlotter()
        plotter.mux.Mux().register_plotter_link(Plot, S, 'min', 'min')
        plotter.mux.Mux().register_plotter_link(Plot, S, 'max', 'max')
        plotter.mux.Mux().register_plotter_link(Plot, S, 'avg', 'avg')
        path = S.solve(self.aco.i, self.aco.m)

        del S
        del alg
        del ant
        del reroute
        del prm
        del g
        del W
        del Plot

        return path