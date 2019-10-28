class RobotizedAnt:
    def __init__(self, a, R):
        self.ant = a
        self.robot = R
        self.origin = R.get_effector()
        self.start_state = R.state

    @property
    def pos(self):
        return self.ant.pos

    @pos.setter
    def pos(self, value):
        self.ant.pos = value

    @property
    def path(self):
        return self.ant.path

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
        self.robot.state = self.start_state

    def deposit_pheromone(self, Q):
        self.ant.deposit_pheromone(Q)

    def reset(self):
        self.ant.reset()

    def clone(self):
        decorated = self.ant.clone()
        ret = RobotizedAnt(decorated, self.robot)
        ret.start_state = self.start_state
        return ret
