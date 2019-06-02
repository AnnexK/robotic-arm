class GGIterator:
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
