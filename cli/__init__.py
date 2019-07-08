from cli.arg_parser import make_parser

import env
import solver
import csv
import pathlib
import writer

def main():
    """Основная функция программы"""
    parser = make_parser()
    args = parser.parse_args()
    
    print('Loading task...')
    Robot, Env, End, emp_best = env.load_task(pathlib.Path(args.task))
    print('Building graph...')
    G, start, end = solver.GraphBuilder(Robot, Env, End, args.phi).make_graph()
    strat = solver.SimpleACO(G, start, end, args.alpha, args.beta, args.ant_power, args.decay)
    S = solver.AntSolver(strat)
    
    print('Solving...')
    best, worst, avg = S.solve(args.iters, args.ant_num)

    w = writer.ColumnWriter(open(args.output, 'w', newline=''), ' ')
    w.write(best, worst, avg, [emp_best] * args.iters)
    del w # закрыть связанный файл
