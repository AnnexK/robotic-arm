class GraphEdge:
    def __init__(self, w, phi):
        self.weight = w
        self._phi = phi

    @property
    def phi(self):
        return self._phi

    @phi.setter
    def phi(self, value):
        if value <= 0.0:
            raise ValueError('Assigned pheromone too low')
        self._phi = value