class RobotizedAnt:
    def __init__(self, a, R):
        self.ant = a
        self.robot = R
        self.origin = R.get_effector()

    @property
    def pos(self):
        return self.ant.pos

    @pos.setter
    def pos(self, value):
        self.ant.pos = value

    @property
    def path_len(self):
        return self.ant.path_len

    def pick_edge(self):
        self.ant.pick_edge()
        step = self.robot.kin_eps

        self.robot.move_to(
            tuple(self.origin[i] + step * self.pos[i]
                  for i in range(3)))

    def remove_cycles(self):
        self.ant.remove_cycles()
        self.robot.move_to(self.origin)

    def deposit_pheromone(self):
        self.ant.deposit_pheromone()

    def reset(self):
        self.ant.reset()

    def clone(self):
        decorated = self.ant.clone()
        ret = RobotizedAnt(decorated, self.robot)
        ret.origin = self.origin
        return ret
