class VertIterator:
    def __init__(self, g):
        self.cur = -1
        self.xm = g.x_nedges + 1
        self.ym = g.y_nedges + 1
        self.zm = g.z_nedges + 1
        self.c = self.ym * self.zm
    
    def __iter__(self):
        return self

    def __next__(self):
        self.cur += 1
        if self.cur == self.xm * self.ym * self.zm:
            raise StopIteration
        x = self.cur // self.c
        y = (self.cur % self.c) // self.zm
        z = self.cur % self.zm
        return x, y, z
        