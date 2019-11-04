#!/bin/python3

import argparse
from env import Environment
import pathlib as path


def main():
    p = argparse.ArgumentParser()
    p.add_argument('sdf')
    p.add_argument('urdf')
    p.add_argument('--state', default=None)
    args = p.parse_args()

    if args.state is None:
        state = None
    else:
        state = list(float(s) for s in args.state.split(';'))

    sdffile = str(path.Path(args.sdf).resolve())
    print(sdffile)
    E = Environment(filename=sdffile)
    urdffile = str(path.Path(args.urdf).resolve())
    E.add_robot(filename=urdffile,
                eff_name='effector')
    if state is not None:
        E.robot.state = state

    input()
    del E


if __name__ == '__main__':
    main()
