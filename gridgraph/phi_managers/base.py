class PhiManager:
    def __init__(self, base):
        self.common_phi = base
        self.phi = {}

    def _get_key(self, v, w):
        return min(v, w), max(v, w)

    def get_phi(self, v, w):
        key = self._get_key(v, w)
        ret = self.common_phi

        if key in self.phi:
            ret += self.phi[key]

        return ret

    def add_phi(self, v, w, val):
        key = self._get_key(v, w)

        if key in self.phi:
            self.phi[key] += val
        else:
            self.phi[key] = val

    def evaporate(self, rho):
        self.common_phi *= (1 - rho)
        for k in self.phi:
            self.phi[k] *= (1 - rho)
