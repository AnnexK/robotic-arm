class PRMParamsValueError(Exception):
    pass


class PRMParams:
    def __init__(self):
        self._k: int = 1
        self._n: int = 1
        self._thresh: float = 1e-8

    @property
    def k(self) -> int:
        return self._k

    @k.setter
    def k(self, val: int):
        if val < 1:
            raise PRMParamsValueError('kmax not in bounds')
        if val > self._n:
            raise PRMParamsValueError('nmax is less than kmax')
        self._k = val

    @property
    def n(self) -> int:
        return self._n

    @n.setter
    def n(self, val: int):
        if val < 1:
            raise PRMParamsValueError('nmax not in bounds')
        if val < self._k:
            raise PRMParamsValueError('nmax is less than kmax')
        self._n = val

    @property
    def thresh(self) -> float:
        return self._thresh

    @thresh.setter
    def thresh(self, val: float):
        if val < 0.0:
            raise PRMParamsValueError('threshold not in bounds')
        self._thresh = val