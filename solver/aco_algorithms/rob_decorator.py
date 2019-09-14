from solver.ants.rob_decorator import RobotizedAnt


class RobotizedAlgorithm:
    def __init__(self, alg, R):
        self.alg = alg
        self.robot = R
        self.origin = R.get_effector()

    def make_ants(self, amount):
        self.alg.make_ants(amount)  # TODO : сделать декоратор для муравья

    def set_proto(self, p):
        self.alg.set_proto(RobotizedAnt(p, self.robot))

    def generate_solutions(self):
        return self.alg.generate_solutions(self)

    def update_pheromone(self):
        self.alg.update_pheromone()

    def daemon_actions(self):
        self.alg.daemon_actions()
        self.robot.move_to(self.origin)
