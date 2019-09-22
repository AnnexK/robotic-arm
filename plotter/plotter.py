import matplotlib.pyplot as plt

class Plot:
    num = 0

    def __init__(self):
        self.id = Plot.num
        Plot.num += 1

    def plot(self, *data):
        plt.figure(self.id)
        
        for d in data:
            e = enumerate(d)
            x, y = [], []
            for p in e:
                x.append(p[0]+1)
                y.append(p[1])
            plt.plot(x, y)

        plt.show()
