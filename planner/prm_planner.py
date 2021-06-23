from logger.logger_collection import LoggerCollection as log
from client.prmparams import PRMParams
from client.acoparams import ACOParams
from solver import BaseAnt, ElitistAS, AntSolver, NullDaemon, PRMRerouteDaemon
import plotter
from graphs.prm import PRMGraph
from graphs.prm import PRM
from graphs.prm.metrics import EuclideanMetric
import graphs.prm.nearest as near
from planner.planner import Planner, Plan
from env.environment import Environment
from env.robot import Robot



class ACOPRMPlanner(Planner):
    def __init__(self, aco: ACOParams, prm: PRMParams, out: str, plot: bool):
        self.aco = aco
        self.prm = prm
        self.out = out
        self.plot = plot

    def plan(self, env: Environment) -> Plan:
        if env.robot is None:
            raise Exception('Should not happen')
        else:
            R: Robot = env.robot
        goal = env.target
        vstart = R.state
        if R.check_collisions():
            raise Exception('Init configuration in obstacle space!')

        M = EuclideanMetric(env.robot)
        g = PRMGraph()        
        neards = near.KDTree(len(R.state), M)
        # neards = near.BruteforceNearest(M)
        prm = PRM(
            self.prm.k,
            neards,
            R,
            self.aco.phi
        )

        # PRM build phase
        for i in range(self.prm.n):
            if (i+1) % 100 == 0:
                log()['PRM'].log(f'Generating vertex {i+1}/{self.prm.n}')
            v = prm.generate_vertex()
            g.add_vertex(v)
            neards.insert(v)
        log()['PRM'].log(f'Vtx in near ds = {len(neards)}')
        for i, v in enumerate(g.vertices):
            if (i+1) % 100 == 0:
                log()['PRM'].log(f'Finding nearest for vertex {i+1}/{self.prm.n}')
            nearest = prm.find_nearest(v)
            if (i+1) % 100 == 0:
                log()['PRM'].log(f'found nearest')
            
            if (i+1) % 100 == 0:
                log()['PRM'].log(f'Connecting nearest for vertex #{i+1}/{self.prm.n}')
            for n in nearest:
                prm.try_connect(g, v, n)
            if (i+1) % 100 == 0:
                log()['PRM'].log('connected')

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
            neards.insert(vstart)
            nearest = prm.find_nearest(vstart)
            for n in nearest:
                prm.try_connect(g, vstart, n)
        except ValueError:
            pass

        try:
            g.add_vertex(vend)
            neards.insert(vend)
            nearest = prm.find_nearest(vend)
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

        reroute = PRMRerouteDaemon(NullDaemon(), g, self.prm.thresh, prm, neards)
        alg = ElitistAS(
            g,
            self.aco.q,
            self.aco.rho,
            self.aco.limit,
            reroute,
            self.aco.elite
        )

        S = AntSolver(alg, ant)

        W = plotter.csv_writer.CSVWriter(self.out, S.get_links())

        Plot = plotter.mpl_plotter.MPLPlotter() if self.plot else plotter.null.NullPlotter()
        for L in S.get_links():
            L.attach(Plot)

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