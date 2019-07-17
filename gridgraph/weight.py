class ConstWeight:
    def __init__(self, c=1.0):
        self.w = c

    def get(self, v, w):
        return self.w
    
    def set(self, v, w, val):
        raise NotImplementedError('Assigning to const weight')
