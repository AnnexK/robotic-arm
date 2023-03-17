class ACOParamsValueError(Exception):
    pass


class ACOParams:
    def __init__(self):
        self._alpha = 1.0
        self._beta = 1.0
        self._phi = 1e-6
        self._rho = 0.0
        self._q = 1.0
        self._m: int = 1
        self._i: int = 1
        self._elite: float = 1.0
        self._limit: int = 0

    @property
    def alpha(self) -> float:
        return self._alpha

    @alpha.setter
    def alpha(self, val: float):
        if val < 0.0:
            raise ACOParamsValueError('alpha not in bounds')
        self._alpha = val

    @property
    def beta(self) -> float:
        return self._beta

    @beta.setter
    def beta(self, val: float):
        if val < 0.0:
            raise ACOParamsValueError('beta not in bounds')
        self._beta = val

    @property
    def phi(self) -> float:
        return self._phi

    @phi.setter
    def phi(self, val: float):
        if val < 0.0:
            raise ACOParamsValueError('phi not in bounds')
        self._phi = val

    @property
    def rho(self) -> float:
        return self._rho

    @rho.setter
    def rho(self, val: float):
        if val > 1.0 or val < 0.0:
            raise ACOParamsValueError('rho not in bounds')
        self._rho = val

    @property
    def q(self) -> float:
        return self._q

    @q.setter
    def q(self, val: float):
        if val <= 0.0:
            raise ACOParamsValueError('q not in bounds')
        self._q = val

    @property
    def m(self) -> int:
        return self._m

    @m.setter
    def m(self, val: int):
        if val < 1:
            raise ACOParamsValueError('m not in bounds')
        self._m = val

    @property
    def i(self) -> int:
        return self._i

    @i.setter
    def i(self, val: int):
        if val < 1:
            raise ACOParamsValueError('i not in bounds')
        self._i = val

    @property
    def elite(self) -> float:
        return self._elite

    @elite.setter
    def elite(self, val: float):
        if val < 0.0:
            raise ACOParamsValueError('elite not in bounds')
        self._elite = val

    @property
    def limit(self) -> int:
        return self._limit

    @limit.setter
    def limit(self, val: int):
        if val < 0:
            raise ACOParamsValueError('limit not in bounds')
        self._limit = val