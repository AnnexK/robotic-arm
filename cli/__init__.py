from cli.arg_parser import make_parser, check_args

import env

from logger import log

from solver.graph_builders.robot_builder import RoboticGraphBuilder
from solver.ants.ant import Ant
from solver.aco_algorithms.ant_system import AntSystem
from solver.solver import AntSolver
from plotter.plotter import Plot


import pathlib
import writer


def main():
    """Основная функция программы"""
    parser = make_parser()
    args = parser.parse_args()
    if not check_args(args):
        raise ValueError('one of the args has wrong value')

    log()['MAIN'].log('Loading task...')
    Env, End, emp_best = env.load_task(pathlib.Path(args.task),
                                       render=not args.silent,
                                       fallback=args.fallback)

    log()['MAIN'].log('Task loaded!')
    log()['MAIN'].log('Creating solver...')
    G, start, end = RoboticGraphBuilder(
        Env.robot, End, args.phi).make_graph()

    log()['GRAPH_GRASP'].log('s = {}; e = {}'
                             .format(start, end))
    a = Ant(args.alpha,
            args.beta,
            args.gamma,
            G,
            Env.robot,
            start,
            end)

    strat = AntSystem(G, args.ant_power, args.decay, args.limit)

    S = AntSolver(strat, a)
    log()['MAIN'].log('Solver created! Solving...')
    best, worst, avg, path = S.solve(args.iters, args.ant_num)

    log()['MAIN'].log('Solved!')
    with writer.ColumnWriter(args.csv, ' ') as w:
        w.write(best, worst, avg)

    log()['MAIN'].log('Saving state sequence to file...')

    with writer.PlainWriter(args.seq) as w:
        w.write(list(p[1]) for p in path)

    if args.plot:
        log()['MAIN'].log('Plotting')
        p = Plot()
        p.plot(best, worst, avg)

    del Env
    log()['MAIN'].log('Have a nice day')
