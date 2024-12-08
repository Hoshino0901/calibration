class FX_market_data:
    def __init__(self, sigma_atm : float, sigma_bf_25 : float, sigma_rr_25 : float, sigma_bf_10 : float, sigma_rr_10 : float):
        self._sigma_atm = sigma_atm
        self._sigma_bf_25 = sigma_bf_25
        self._sigma_rr_25 = sigma_rr_25
        self._sigma_bf_10= sigma_bf_10
        self._sigma_rr_10 = sigma_rr_10
    
    def Sigma_atm(self) -> float:
        return self._sigma_atm

    def Sigma_ms_25(self) -> float:
        return self._sigma_bf_25 + self._sigma_atm

    def Sigma_rr_25(self) -> float:
        return self._sigma_rr_25
    
    def Sigma_ms_10(self) -> float:
        return self._sigma_bf_10 + self._sigma_atm

    def Sigma_rr_10(self) -> float:
        return self._sigma_rr_10
