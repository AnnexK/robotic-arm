from cli.arg_parser import make_parser, check_args

import env

from logger import log

from solver.builders.robot_builder import RoboticGraphBuilder
from solver.ants.ant import Ant
from solver.ants.rob_decorator import RobotizedAnt
from solver.aco_algorithms.ant_system import AntSystem
from solver.solver import AntSolver

import pathlib
import writer


def main():
    """Основная функция программы"""
    parser = make_parser()
    args = parser.parse_args()
    if not check_args(args):
        raise ValueError('one of the args has wrong value')

    log()['MAIN'].log('Loading task...')
    Robot, Env, End, emp_best = env.load_task(pathlib.Path(args.task))
    log()['MAIN'].log('Task loaded!')
    log()['MAIN'].log('Creating solver...')
    G, start, end = RoboticGraphBuilder(
        Robot, End, args.phi).make_graph()

    a = Ant(args.alpha,
            args.beta,
            args.ant_power,
            G,
            start)
    rob_ant = RobotizedAnt(a, Robot)

    strat = AntSystem(G, end, args.decay)
    strat.set_proto(rob_ant)

    S = AntSolver(strat)
    log()['MAIN'].log('Solver created! Solving...')
    best, worst, avg = S.solve(args.iters, args.ant_num)

    log()['MAIN'].log('Solved!')
    with writer.ColumnWriter(input('Input save file name: '), ' ') as w:
        w.write(best, worst, avg)
