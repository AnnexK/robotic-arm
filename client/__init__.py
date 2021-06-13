from client.arg_parser import make_parser
from client.arg_parser_prm import make_parser as prm_parser

import env

from logger import log
from planner.stock_planner import ACOStockPlanner
from planner.prm_planner import ACOPRMPlanner

from .acoparams import ACOParams, ACOParamsValueError
from .prmparams import PRMParams, PRMParamsValueError

import pathlib


def main():
    """Основная функция программы ACOStock"""
    parser = make_parser()
    args = parser.parse_args()

    if args.gamma < 0.0:
        log()['MAIN'].log('gamma not in bounds')
        return

    params = ACOParams()
    try:
        params.alpha = args.alpha
        params.beta = args.beta
        params.phi = args.phi
        params.rho = args.decay
        params.q = args.ant_power
        params.m = args.ant_num
        params.i = args.iters
        params.elite = args.elite_power
        params.limit = args.limit
    except ACOParamsValueError as e:
        log()['MAIN'].log(f'{str(e)}')
        log()['MAIN'].log('Check input parameters')
        return

    log()['MAIN'].log('Loading task...')
    Env = env.load_task(pathlib.Path(args.task),
                        render=not args.silent,
                        fallback=args.fallback)

    log()['MAIN'].log('Task loaded!')
    log()['MAIN'].log('Creating solver...')

    planner = ACOStockPlanner(params, args.gamma, args.csv, args.plot)
    plan = planner.plan(Env)
    del planner

    log()['MAIN'].log('Solved!')

    log()['MAIN'].log('Saving state sequence to file...')

    with open(args.seq, 'w') as fp:
        for s in plan:
            fp.write(str(s))

    del Env
    log()['MAIN'].log('Have a nice day')


def main_prm():
    """Основная функция программы ACOPRM"""
    parser = prm_parser()
    args = parser.parse_args()

    aco = ACOParams()
    prm = PRMParams()

    try:
        aco.alpha = args.alpha
        aco.beta = args.beta
        aco.phi = args.phi
        aco.rho = args.decay
        aco.q = args.ant_power
        aco.m = args.ant_num
        aco.i = args.iters
        aco.elite = args.elite_power
        aco.limit = args.limit
    except ACOParamsValueError as e:
        log()['MAIN'].log(f'{str(e)}')
        log()['MAIN'].log('Check input parameters')
        return

    try:
        prm.thresh = args.threshold
        prm.n = args.nmax
        prm.k = args.kmax
    except PRMParamsValueError as e:
        log()['MAIN'].log(f'{str(e)}')
        log()['MAIN'].log('Check input parameters')
        return

    log()['MAIN'].log('Loading task...')
    Env = env.load_task(pathlib.Path(args.task),
                        render=not args.silent,
                        fallback=args.fallback)

    log()['MAIN'].log('Task loaded!')
    log()['MAIN'].log('Creating solver...')

    planner = ACOPRMPlanner(aco, prm, args.csv, args.plot)
    plan = planner.plan(Env)
    del planner

    log()['MAIN'].log('Solved!')

    log()['MAIN'].log('Saving state sequence to file...')

    with open(args.seq, 'w') as fp:
        for s in plan:
            fp.write(f'{s}\n')
        
    del Env
    log()['MAIN'].log('Have a nice day')
