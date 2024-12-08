class Calibrated_params:
    def __init__(self, alpha : float, nu : float, rho : float, K_25_d_p : float, K_25_d_c : float, K_10_d_p : float, K_10_d_c : float):
        self._alpha = alpha
        self._nu = nu
        self._rho = rho
        self._K_25_d_p = K_25_d_p
        self._K_25_d_c = K_25_d_c
        self._K_10_d_p = K_10_d_p
        self._K_10_d_c = K_10_d_c
    
    def Alpha(self) -> float:
        return self._alpha

    def Nu(self) -> float:
        return self._nu
    
    def Rho(self) -> float:
        return self._rho
    
    def K_25_d_p(self) -> float:
        return self._K_25_d_p

    def K_25_d_c(self) -> float:
        return self._K_25_d_c

    def K_10_d_p(self) -> float:
        return self._K_10_d_p

    def K_10_d_c(self) -> float:
        return self._K_10_d_c