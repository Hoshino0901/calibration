class FX_params:
    def __init__(self, r_d : float, r_f : float, maturity : float):
        self._r_d = r_d
        self._r_f = r_f
        self._maturity = maturity
    
    def R_d(self) -> float:
        return self._r_d

    def R_f(self) -> float:
        return self._r_f

    def T(self) -> float:
        return self._maturity