import env
import argparse
import pathlib
from time import sleep


def make_sequence(S):
    ret = []
    for s in S:
        ret.append(list(float(q) for q in s[1:-3].split(',')))
    return ret


p = argparse.ArgumentParser()
p.add_argument('task')
p.add_argument('seq')
p.add_argument('--fps', type=int, default=5)
p.add_argument('--fallback', action='store_true')

args = p.parse_args()
if args.fps <= 0:
    raise ValueError('FPS too small')

slp = 1/args.fps
E, end, emp = env.load_task(pathlib.Path(args.task),
                            render=True,
                            fallback=args.fallback)

R = E.robot

with open(args.seq, 'r') as seqfile:
    S = seqfile.readlines()

Q = make_sequence(S)

for q in Q:
    sleep(slp)
    R.state = q

input()

del R
del E
