from env.types import State
from math import sqrt
from .metric import Metric
from env.types import State
from env.robot import Robot, JointType
from math import pi


class EuclideanMetric(Metric):
    def __init__(self, R: Robot):
        self.types = R.types

    def __call__(self, A: State, B: State) -> float:
        def diffval(a: float, b: float, t: JointType):
            if t is JointType.CONTNIUOUS:
                diff = abs(a-b)
                return min(diff, 2*pi-diff)
            else:
                return a-b
            
        return sqrt( sum( diffval(a, b, t)**2 for a, b, t in zip(A, B, self.types) ) )