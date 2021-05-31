from cli.arg_parser import make_parser, check_args
from cli.arg_parser_prm import make_parser as prm_parser, check_args as prm_check

import env

from logger import log
from planner.prm_planner import ACOStockPlanner, ACOPRMPlanner

import pathlib
import writer


class ACOParams:
    def __init__(self, args):
        self.alpha = args.alpha
        self.beta = args.beta
        self.phi = args.phi
        self.rho = args.decay
        self.q = args.ant_power
        self.m = args.ant_num
        self.i = args.iters


class PRMParams:
    def __init__(self, args):
        self.k = args.kmax
        self.n = args.nmax
        self.thresh = args.threshold
    

def main():
    """Основная функция программы ACOStock"""
    parser = make_parser()
    args = parser.parse_args()
    if not check_args(args):
        raise ValueError('one of the args has wrong value')

    params = ACOParams(args)
    log()['MAIN'].log('Loading task...')
    Env, End, emp_best = env.load_task(pathlib.Path(args.task),
                                       render=not args.silent,
                                       fallback=args.fallback)

    states = [Env.robot.state]

    log()['MAIN'].log('Task loaded!')
    log()['MAIN'].log('Creating solver...')
    
    planner = ACOStockPlanner(params, args.gamma, args.limit, args.elite_power)
    path = planner.plan(Env, End)
    del planner

    log()['MAIN'].log('Solved!')

    for v in path[1:]:
        Env.robot.move_to(v)
        states.append(Env.robot.state)
    log()['MAIN'].log('Saving state sequence to file...')

    with writer.PlainWriter(args.seq) as w:
        w.write(states)

    del Env
    log()['MAIN'].log('Have a nice day')


def main_prm():
    """Основная функция программы ACOPRM"""
    parser = prm_parser()
    args = parser.parse_args()
    if not prm_check(args):
        raise ValueError('one of the args has wrong value')

    aco = ACOParams(args)
    prm = PRMParams(args)

    log()['MAIN'].log('Loading task...')
    Env, End, emp_best = env.load_task(pathlib.Path(args.task),
                                       render=not args.silent,
                                       fallback=args.fallback)

    log()['MAIN'].log('Task loaded!')
    log()['MAIN'].log('Creating solver...')
    
    planner = ACOPRMPlanner(aco, prm, args.limit, args.elite_power)
    path = planner.plan(Env, End)
    del planner

    log()['MAIN'].log('Solved!')

    log()['MAIN'].log('Saving state sequence to file...')

    with writer.PlainWriter(args.seq) as w:
        w.write(path)

    del Env
    log()['MAIN'].log('Have a nice day')