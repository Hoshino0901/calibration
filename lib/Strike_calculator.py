import scipy.stats as stats
import math
from FX_params import FX_params
from FX_market_data import FX_market_data

class Strike_calcurator:
    def __init__(self, params : FX_params, F_0 : float, volas : FX_market_data):
        self.params = params
        self.F_0 = F_0
        self.volas = volas

    # using pip delta
    def get_atm_strike(self) -> float:
        return self.F_0 * math.exp(0.5 * self.volas.Sigma_atm() * self.volas.Sigma_atm() * self.params.T())

    def get_ms_strike(self, percent : float) -> float:
        x = stats.norm.ppf(abs(percent) * math.exp(self.params.R_f() * self.params.T()))
        if percent > 0:
            if percent == 0.1:
                sigma = self.volas.Sigma_atm() + self.volas.Sigma_ms_10()
            elif percent == 0.25:
                sigma = self.volas.Sigma_atm() + self.volas.Sigma_ms_25()
            else:
                raise ValueError(f"Percent for delta ({percent * 100} %) is inappropriate.")

            return self.F_0 / math.exp(x * sigma * math.sqrt(self.params.T()) - 0.5 * sigma * sigma * self.params.T())
        else:
            if percent == -0.1:
                sigma = self.volas.Sigma_atm() + self.volas.Sigma_ms_10()
            elif percent == -0.25:
                sigma = self.volas.Sigma_atm() + self.volas.Sigma_ms_25()
            else:
                raise ValueError(f"Percent for delta ({percent * 100} %) is inappropriate.")

            return self.F_0 / math.exp(-x * sigma * math.sqrt(self.params.T()) - 0.5 * sigma * sigma * self.params.T())

        