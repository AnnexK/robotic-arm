from math import sqrt


class EuclideanMetric:
    def __init__(self):
        pass

    def __call__(self, A, B):
        return sqrt( sum( (a-b)*(a-b) for a, b in zip(A, B) ) )