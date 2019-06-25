from cli.arg_parser import make_parser

import env
import solver
import csv

def main():
    """Основная функция программы"""
    parser = make_parser()
    args = parser.parse_args()
    
    Robot, Env, End = env.load_task(args.task)
    S = solver.AntSolver(Robot, End, args.alpha, args.beta, args.ant_power, args.decay, args.phi)
    best, worst, avg = S.solve(args.iters, args.ant_num)

    with open(args.output, 'w', newline='') as out:
        writer = csv.writer(out)
        writer.writerow(best)
        writer.writerow(worst)
        writer.writerow(avg)
