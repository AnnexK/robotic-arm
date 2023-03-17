from math import sqrt
from .metric import Metric
from env.robot import Robot, State


class EffectorDisplacementMetric(Metric):
    def __init__(self, robot: Robot):
        self.robot = robot

    def __call__(self, A: State, B: State) -> float:
        self.robot.state = A
        ea = self.robot.get_effector()
        self.robot.state = B
        eb = self.robot.get_effector()

        return sqrt( sum( (a-b)*(a-b) for a, b in zip(ea, eb) ) )