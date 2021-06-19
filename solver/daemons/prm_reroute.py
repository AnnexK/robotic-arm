from graphs.prm.nearest.nearest import KNearest
from .daemon import Daemon
from graphs.prm.prmgraph import PRMGraph
from graphs.prm.prm import PRM
from logger import log

class PRMRerouteDaemon(Daemon):
    def __init__(self, daemon: Daemon, graph: PRMGraph, thresh: float, prm: PRM, near: KNearest):
        self.daemon = daemon
        self.graph = graph
        self.threshold = thresh
        self.prm = prm
        self.near = near

    def daemon_actions(self):
        for v in self.graph.vertices:
            for w in self.graph.get_adjacent(v):
                if self.graph.get_phi(v, w) < self.threshold:
                    self.graph.remove_edge(v, w)
        new_v = 0
        
        for v in self.graph.vertices:
            if not self.graph.get_adjacent(v):
                self.graph.remove_vertex(v)
                self.near.delete(v)
                new_v += 1
        log()['REROUTE'].log(f'Removed {new_v} vertices')
        for _ in range(new_v):
            v = self.prm.generate_vertex()
            self.graph.add_vertex(v)
            self.near.insert(v)
            nearest = self.prm.find_nearest(v)
            for n in nearest:
                self.prm.try_connect(self.graph, v, n)

        self.daemon.daemon_actions()

