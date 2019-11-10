import env
import argparse
import pathlib
from time import sleep


p = argparse.ArgumentParser()
p.add_argument('task')
p.add_argument('seq')
p.add_argument('-t', type=float, default=0.5)
p.add_argument('--fallback', action='store_true')

args = p.parse_args()

E, end, emp = env.load_task(pathlib.Path(args.task),
                            render=True,
                            fallback=args.fallback)

R = E.robot

with open(args.seq, 'r') as seqfile:
    S = seqfile.readlines()

Q = []
for s in S:
    Q.append(list(float(q) for q in s[1:-3].split(',')))

for q in Q:
    sleep(args.t)
    R.state = q
    print(R.check_collisions())

input()

del E
