import argparse


def make_parser():
    ret = argparse.ArgumentParser(
        description='Launch the solver with arguments specified')
    ret.add_argument('task', help='task filename')
    ret.add_argument('csv', help='csv stats filename')
    ret.add_argument('seq', help='q sequence filename')
    # PRM
    ret.add_argument('--kmax',
                     help='Amount of vertices in PRM',
                     type=int, default=1000)
    ret.add_argument('--threshold',
                     help='Pheromone threshold for reroute daemon',
                     type=float, default=1e-6)
    ret.add_argument('--nmax',
                     help='Max amount of neighbours to consider in PRM',
                     type=int, default=15)
    # ACO
    ret.add_argument('-a', '--alpha',
                     help='pheromone attractiveness modifier',
                     type=float, default=1.0)
    ret.add_argument('-b', '--beta',
                     help='weight attractiveness modifier',
                     type=float, default=1.0)
    ret.add_argument('-p', '--phi',
                     help='base pheromone level',
                     type=float, default=0.1)
    ret.add_argument('-d', '--decay',
                     help='pheromone decay rate',
                     type=float, default=0.01)
    ret.add_argument('-q', '--ant-power',
                     help='amount of pheromone an ant distributes',
                     type=float, default=1.0)
    ret.add_argument('-k', '--ant-num',
                     help='number of ants',
                     type=int, default=1)
    ret.add_argument('-i', '--iters',
                     help='number of algorithm iterations',
                     type=int, default=1)
    ret.add_argument('--plot',
                     help='draw a plot after solving',
                     action='store_true')
    ret.add_argument('--limit',
                     help='limit amount of ant steps',
                     type=int, default=250000)

    # elitist AS elite power
    # default equals 0
    ret.add_argument('-e', '--elite-power',
                     help='elite ant power (for EAS)',
                     type=float, default=0.0)

    spec_parms = ret.add_mutually_exclusive_group()
    spec_parms.add_argument('--silent', help='launch solver without GUI',
                            action='store_true')
    spec_parms.add_argument('--fallback',
                            help='launch solver in opengl2 (fallback) mode',
                            action='store_true')
    return ret
