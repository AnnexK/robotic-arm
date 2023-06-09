from typing import Iterable
from weakref import WeakSet

from roboticarm.graphs.phigraph import PhiGraph
from roboticarm.env.types import State as V


class PRMGraph(PhiGraph[V]):
    class GraphEdge:
        def __init__(self, wg: float, phi: float):
            self.wg = wg
            self.phi = phi

    def __init__(self):
        self._vertices: dict[V, dict[V, PRMGraph.GraphEdge]] = dict()
        self.edges: WeakSet[PRMGraph.GraphEdge] = WeakSet()
        self.lim: float = 1e-12

    def add_vertex(self, v: V):
        if v in self.vertices:
            raise ValueError("Vertex already present")

        self._vertices[v] = dict()

    @property
    def vertices(self) -> set[V]:
        return set(self._vertices)

    def remove_vertex(self, v: V):
        try:
            for w in self.get_adjacent(v):
                del self._vertices[w][v]
            del self._vertices[v]
        except KeyError:
            pass

    def add_edge(self, v: V, w: V, wg: float, phi: float):
        if v not in self._vertices:
            raise ValueError("v not in graph")
        if w not in self._vertices:
            raise ValueError(f"w not in graph: {w}")

        edge = PRMGraph.GraphEdge(wg, phi)
        self._vertices[v][w] = edge
        self._vertices[w][v] = edge
        self.edges.add(edge)

    def remove_edge(self, v: V, w: V):
        if not (v in self._vertices and w in self._vertices):
            raise ValueError("One of vertices not in graph")

        try:
            del self._vertices[v][w]
            del self._vertices[w][v]
        except KeyError:
            pass

    def get_adjacent(self, v: V) -> Iterable[V]:
        if v not in self._vertices:
            raise ValueError("Vertex not in graph")

        return list(self._vertices[v])

    def get_weight(self, v: V, w: V) -> float:
        return self._vertices[v][w].wg

    def get_phi(self, v: V, w: V) -> float:
        return self._vertices[v][w].phi

    def add_phi(self, v: V, w: V, val: float):
        self._vertices[v][w].phi += val

    def evaporate(self, rate: float):
        for e in self.edges:
            e.phi = max(self.lim, e.phi * (1 - rate))
