from .mux import Mux
from abc import ABCMeta, abstractmethod

# Объект-звено от коммутатора до плоттера
# Коммутатор записывает в него данные с звена от объекта данных
# и заставляет звено направить оповещение связанному со звеном
# плоттеру

class Plotter(metaclass=ABCMeta):
    @abstractmethod
    def plot_point(self, link):
        pass