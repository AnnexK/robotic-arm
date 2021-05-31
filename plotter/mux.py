from util.singleton import Singleton


class LinkNotFound(Exception):
    pass


class MPLink:
    def __init__(self, name, plotter):
        self.x = self.y = 0.0
        self._name = name
        # Todo: Сделать weakref чтобы не было утечек
        self.P = plotter

    @property
    def name(self):
        return self._name

    def forward_notification(self):
        self.P.plot_point(self)


class PMLink:
    def __init__(self, name):
        self.x = self.y = 0.0
        self._name = name

    @property
    def name(self):
        return self._name
# Коммутатор запросов от объектов с данными для графиков
# до объектов, выполняющих обработку данных
# (плоттеров/писателей)
class Mux(metaclass=Singleton):
    class MPPair:
        def __init__(self, T, R):
            self.t = T
            self.r = R
    
    def __init__(self):
        self.pm = dict()
        self.mp = []

    def register_plottable_link(self, P, L):
        if L not in self.pm:
            self.pm[L] = P

    def register_plotter_link(self, Pr, Pt, Rname, Tname):
        print(self.pm)
        print(Pt)
        try:
            # Получаем линк, принадлежащий Pt с именем Tname
            PL = next(filter(lambda x: x.name == Tname and self.pm[x] is Pt, self.pm))
            # Делаем линк от коммутатора до плоттера
            self.mp.append(Mux.MPPair(PL, MPLink(Rname, Pr)))
        except StopIteration as e:
            raise LinkNotFound() from e

    def deregister_plottable(self, P):
        self.pm = {k: v for k, v in self.pm.items() if v is not P}
        self.mp = [x for x in self.mp if x.t not in self.pm]

    def deregister_plotter(self, P):
        self.mp = [x for x in self.mp if x.r is not P]
    
    def notify(self, L):
        for receiver in map(lambda x: x.r, filter(lambda x: x.t is L, self.mp)):
            receiver.x = L.x
            receiver.y = L.y
            receiver.forward_notification()
