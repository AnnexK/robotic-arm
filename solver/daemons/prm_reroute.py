class PRMRerouteDaemon:
    def __init__(self, daemon, graph, thresh, prm):
        self.daemon = daemon
        self.graph = graph
        self.threshold = thresh
        self.prm = prm

    def daemon_actions(self):
        for v in self.graph.vertices:
            for w in self.graph.get_adjacent(v):
                if self.graph.get_phi(v, w) < self.threshold:
                    self.graph.remove_edge(v, w)
        new_v = 0
        for v in self.graph.vertices:
            if not self.graph.get_adjacent(v):
                self.graph.remove_vertex(v)
                new_v += 1

        for i in range(new_v):
            v = self.prm.generate_vertex()
            self.graph.add_vertex(v)
            nearest = self.prm.find_nearest(self.graph, v)
            for n in nearest:
                self.prm.try_connect(self.graph, v, n)

        self.daemon.daemon_actions()

