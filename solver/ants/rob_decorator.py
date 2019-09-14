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
        pos = self.pos
        
        self.robot.move_to(tuple(self.origin[i] + step * pos[i] for i in range(3)))

