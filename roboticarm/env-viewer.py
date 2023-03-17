import argparse
import pybullet as pb
import pathlib as path


def main():
    p = argparse.ArgumentParser()
    p.add_argument('sdf')
    args = p.parse_args()

    sdffile = str(path.Path(args.sdf).resolve())
    print(sdffile)

    pb.connect(pb.GUI)  # type: ignore
    pb.loadSDF(sdffile)  # type: ignore

    input()


if __name__ == '__main__':
    main()
