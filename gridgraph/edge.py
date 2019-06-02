class GraphEdge:
    def __init__(self, w=0.0):
        self._weight = w

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, value):
        self._weight = value
