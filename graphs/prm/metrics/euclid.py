from env.types import State
from math import sqrt
from .metric import Metric
from env.types import State


class EuclideanMetric(Metric):
    def __init__(self):
        pass

    def __call__(self, A: State, B: State) -> float:
        return sqrt( sum( (a-b)*(a-b) for a, b in zip(A, B) ) )