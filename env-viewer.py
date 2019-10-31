#!/bin/python3

import argparse
import pybullet as pb


def main():
    p = argparse.ArgumentParser()
    p.add_argument('env')

    args = p.parse_args()

    s = pb.connect(pb.GUI, options='--opengl2')

    model = pb.loadSDF(args.env)

    input()


if __name__ == '__main__':
    main()
