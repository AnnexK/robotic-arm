from cli.arg_parser import make_parser

import env
import solver
import csv
import pathlib

def main():
    """Основная функция программы"""
    parser = make_parser()
    args = parser.parse_args()
    
    print('Loading task...')
    Robot, Env, End, emp_best = env.load_task(pathlib.Path(args.task))
    print('Building graph...')
    G, start, end = solver.GraphBuilder(Robot, Env, End).make_graph()
    S = solver.AntSolver(G, start, end, args.alpha, args.beta, args.ant_power, args.decay, args.phi)
    print('Solving...')
    best, worst, avg = S.solve(args.iters, args.ant_num)

    with open(args.output, 'w', newline='') as out:
        writer = csv.writer(out)
        writer.writerow(best)
        writer.writerow(worst)
        writer.writerow(avg)
        # нижний предел
        writer.writerow([emp_best] * args.iters)
