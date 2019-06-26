class EdgeIterator:
    def __init__(self, g):
        self.e = g.edges # ссылка на массив ребер
        self.ei = 0 # положение в массиве по параллельности ребер
        self.xc = 0 # текущая координата x
        self.xm = g.x_nedges # макс координата x
        self.yc = 0
        self.ym = g.y_nedges
        self.zc = 0
        self.zm = g.z_nedges
        
    def __next__(self):
        if self.ei == 3:
            raise StopIteration
            
        idx = (self.xc, self.yc, self.zc)
        eidx = self.ei
        self.xc += 1
        if self.xc > self.xm - (self.ei == 0):
            self.xc = 0
            self.yc += 1
            if self.yc > self.ym - (self.ei == 1):
                self.yc = 0
                self.zc += 1
                if self.zc > self.zm - (self.ei == 2):
                    self.zc = 0
                    self.ei += 1
        return self.e[eidx][idx]

class VertIterator:
    def __init__(self, g):
        self.cur = -1
        self.xm = g.x_nedges
        self.ym = g.y_nedges
        self.zm = g.z_nedges
        self.c = self.ym * self.zm
    
    def __next__(self):
        self.cur += 1
        if self.cur == self.xm * self.ym * self.zm:
            raise StopIteration
        x = self.cur // self.c
        y = (self.cur % self.c) // self.zm
        z = self.cur % self.zm
        return x, y, z
        