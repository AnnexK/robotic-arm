from weakref import WeakSet
from graphs.phigraph import PhiGraph
from typing import Dict, Set, Iterable
from env.types import State as V


class PRMGraph(PhiGraph[V]):
    class GraphEdge:
        def __init__(self, wg: float, phi: float):
            self.wg = wg
            self.phi = phi

    def __init__(self):
        self._vertices: Dict[V, Dict[V, PRMGraph.GraphEdge]] = dict()
        self.edges: WeakSet[PRMGraph.GraphEdge] = WeakSet()
        self.lim: float = 1e-12

    def add_vertex(self, v: V):
        if v in self.vertices:
            raise ValueError('Vertex already present')
        
        self._vertices[v] = dict()

    @property
    def vertices(self) -> Set[V]:
        return set(self._vertices)
    
    def remove_vertex(self, v: V):
        try:
            del self._vertices[v]
            for w in self.vertices:
                self._vertices[w] = {x: e for x, e in self._vertices[w].items() if x != v}
        except KeyError:
            pass

    def add_edge(self, v: V, w: V, wg: float, phi: float):
        if not (v in self._vertices and w in self._vertices):
            raise ValueError('One of vertices not in graph')

        edge = PRMGraph.GraphEdge(wg, phi)
        self._vertices[v][w] = edge
        self._vertices[w][v] = edge
        self.edges.add(edge)

    def remove_edge(self, v: V, w: V):
        if not (v in self._vertices and w in self._vertices):
            raise ValueError('One of vertices not in graph')
        
        del self._vertices[v][w]
        del self._vertices[w][v]

    def get_adjacent(self, v: V) -> Iterable[V]:
        if v not in self._vertices:
            raise ValueError('Vertex not in graph')

        return list(self._vertices[v])
    
    def get_weight(self, v: V, w: V) -> float:
        return self._vertices[v][w].wg

    def get_phi(self, v: V, w: V) -> float:
        return self._vertices[v][w].phi

    def add_phi(self, v: V, w: V, val: float):
        self._vertices[v][w].phi += val

    def evaporate(self, rate: float):
        for e in self.edges:
            e.phi = max(self.lim, e.phi * (1-rate))