from weakref import WeakSet


class LinkGraph:
    class GraphEdge:
        def __init__(self, wg, phi):
            self.wg = wg
            self.phi = phi

    def __init__(self):
        self._vertices = dict()
        self.edges = WeakSet()
        self.lim = 1e-8

    def add_vertex(self, v):
        if v in self.vertices:
            raise ValueError('Vertex already present')
        
        self._vertices[v] = dict()

    @property
    def vertices(self):
        return set(self._vertices)
    
    def remove_vertex(self, v):
        try:
            del self._vertices[v]
            for w in self.vertices:
                self._vertices[w] = {x: e for x, e in self._vertices[w].items() if x != v}
        except KeyError:
            pass

    def add_edge(self, v, w, wg, phi):
        if not (v in self._vertices and w in self._vertices):
            raise ValueError('One of vertices not in graph')

        edge = LinkGraph.GraphEdge(wg, phi)
        self._vertices[v][w] = edge
        self._vertices[w][v] = edge
        self.edges.add(edge)

    def remove_edge(self, v, w):
        if not (v in self._vertices and w in self._vertices):
            raise ValueError('One of vertices not in graph')
        
        del self._vertices[v][w]
        del self._vertices[w][v]

    def get_adjacent(self, v):
        if v not in self._vertices:
            raise ValueError('Vertex not in graph')

        return list(self._vertices[v])
    
    def get_weight(self, v, w):
        return self._vertices[v][w].wg

    def get_phi(self, v, w):
        return self._vertices[v][w].phi

    def add_phi(self, v, w, val):
        self._vertices[v][w].phi += val

    def evaporate(self, rate):
        for e in self.edges:
            e.phi = max(self.lim, e.phi * (1-rate))