from .base import PhiManager


class BoundedPhiManager(PhiManager):
    def __init__(self, base, lower, upper):
        if not (lower <= base <= upper):
            raise ValueError('Base phi not in bounds')

        super().__init__(base)
        self.lower = lower
        self.upper = upper
        self.frozen = False

    def evaporate(self, rho):
        # если общее кол-во феромона еще не равно
        # минимальному
        if not self.frozen:
            super().evaporate(rho)
            # значение общего уровня феромона
            # теперь меньше минимального.
            # установим его в минимум
            # и "заморозим", предотвращая дальнейшие
            # попытки его изменить.
            if self.common_phi < self.lower:
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
            delta = rho * self.common_phi

        # если нужно модифицировать значения
        # для каждого посещенного ребра:
        if self.frozen:
            for k in self.phi:
                self.phi[k] = self.phi[k] - delta
                if self.phi[k] < 0.0:
                    self.phi[k] = 0.0

    def add_phi(self, v, w, val):
        delta = self.upper - self.common_phi
        key = self._get_key(v, w)
        if key not in self.phi:
            self.phi[key] = val
        else:
            self.phi[key] += val
        if self.phi[key] > delta:
            self.phi[key] = delta
