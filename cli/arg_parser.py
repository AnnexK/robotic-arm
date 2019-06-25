import argparse

def make_parser():
    ret = argparse.ArgumentParser(description='Launch the solver with arguments specified')
    ret.add_argument('task', help='task filename')
    ret.add_argument('output', help='output filename')      
    ret.add_argument('-a', '--alpha', help='pheromone attractiveness modifier', type=float, default=1.0)
    ret.add_argument('-b', '--beta', help='weight attractiveness modifier', type=float, default=1.0)
    ret.add_argument('-p', '--phi', help='base pheromone level', type=float, default=0.1)
    ret.add_argument('-d', '--decay', help='pheromone decay rate', type=float, default=0.01)
    ret.add_argument('-q', '--ant-power', help='total amount of pheromone an ant distributes', type=float, default=1.0)
    ret.add_argument('-k', '--ant-num', help='amount of ants', type=int, default=1)
    ret.add_argument('-i', '--iters', help='amount of algorithm iterations', type=int, default=1)
    return ret
