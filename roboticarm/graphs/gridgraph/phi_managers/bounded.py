from .base import BasePhiManager
from ..gridgraph import GGVertex as V


class BoundedPhiManager(BasePhiManager):
    def __init__(self, base: float, lower: float, upper: float):
        if not (lower <= base <= upper):
            raise ValueError('Base phi not in bounds')

        super().__init__(base)
        self.lower = lower
        self.upper = upper
        self.frozen: bool = False

    def evaporate(self, rate: float):
        delta = 0.0
        # если общее кол-во феромона еще не равно
        # минимальному
        if not self.frozen:
            super().evaporate(rate)
            # дополнительное испарение не нужно
            custom_evap: int = 0

            if self.common_phi < self.lower:
                # значение общего уровня феромона
                # теперь меньше минимального.
                # установим его в минимум
                # и "заморозим", предотвращая дальнейшие
                # попытки его изменить.
                delta = self.lower - self.common_phi
                self.common_phi = self.lower
                self.frozen = True
        else:
            # раз значение общего ур. феромона
            # заморожено, то нужно уменьшить
            # уровень феромона на каждом посещенном ребре
            # для непосещенных делать этого нет необходимости,
            # т. к. для них уже установлен нижний предел
            # (phi_min + 0)
            delta = rate * self.common_phi
            # нужно дополнительное испарение
            custom_evap: int = 1

        # если нужно модифицировать значения
        # для каждого посещенного ребра:
        if self.frozen:
            for k in self.phi:
                self.phi[k] = max((1-rate*custom_evap) * self.phi[k] - delta,
                                  0.0)

    def add_phi(self, v: V, w: V, val: float):
        delta = self.upper - self.common_phi
        key = self._get_key(v, w)
        if key not in self.phi:
            self.phi[key] = val
        else:
            self.phi[key] += val
        if self.phi[key] > delta:
            self.phi[key] = delta
