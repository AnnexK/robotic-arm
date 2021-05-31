from math import sqrt

class EffectorDisplacementMetric:
    def __init__(self, robot):
        self.robot = robot

    def __call__(self, A, B):
        self.robot.state = A
        ea = self.robot.get_effector()
        self.robot.state = B
        eb = self.robot.get_effector()

        return sqrt( sum( (a-b)*(a-b) for a, b in zip(ea, eb) ) )