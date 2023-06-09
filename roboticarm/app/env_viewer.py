import argparse
import pathlib as path

import pybullet as pb


def main():
    p = argparse.ArgumentParser()
    p.add_argument("sdf")
    args = p.parse_args()

    sdffile = str(path.Path(args.sdf).resolve())
    print(sdffile)

    pb.connect(pb.GUI)
    pb.loadSDF(sdffile)

    input()


if __name__ == "__main__":
    main()
