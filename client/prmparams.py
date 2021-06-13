class PRMParamsValueError(Exception):
    pass


class PRMParams:
    def __init__(self):
        self._k: int = 15
        self._n: int = 1000
        self._thresh: float = 1e-8

    @property
    def k(self) -> int:
        return self._k

    @k.setter
    def k(self, val: int):
        if val < 1:
            raise PRMParamsValueError('k not in bounds')
        self._k = val

    @property
    def n(self) -> int:
        return self._n

    @n.setter
    def n(self, val: int):
        if val < 1:
            raise PRMParamsValueError('n not in bounds')
        self._n = val

    @property
    def thresh(self) -> float:
        return self._thresh

    @thresh.setter
    def thresh(self, val: float):
        if val < 0.0:
            raise PRMParamsValueError('thresh not in bounds')
        self._thresh = val