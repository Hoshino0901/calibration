import math
import scipy.stats as stats
from scipy.optimize import minimize
from FX_params import FX_params
from FX_market_data import FX_market_data
from SABR_model import SABR_model
from Strike_calculator import Strike_calcurator
from  Calibrated_params import Calibrated_params

class Calibrator:
    def __init__(self, params : FX_params, F_0 : float, volas : FX_market_data, fly_adjust_param : float):
        self.params = params
        self.F_0 = F_0
        self.volas = volas
        self.sigma_25_ms = self.volas.Sigma_ms_25()
        self.sigma_10_ms = self.volas.Sigma_ms_10()
        self.fly_adjust_param = fly_adjust_param
        strike_calcurator = Strike_calcurator(params, F_0, volas)
        self.K_atm = strike_calcurator.get_atm_strike()
        self.K_25_d_p_ms = strike_calcurator.get_ms_strike(-0.25)
        self.K_25_d_c_ms = strike_calcurator.get_ms_strike(0.25)
        self.K_10_d_p_ms = strike_calcurator.get_ms_strike(-0.1)
        self.K_10_d_c_ms = strike_calcurator.get_ms_strike(0.1)

    def _calc_foreign_pips_call_delta(self, K : float, sigma : float) -> float:
        d1 = (math.log(self.F_0 / K) + 0.5 * sigma * sigma * self.params.T()) / (sigma * math.sqrt(self.params.T()))
        return stats.norm.cdf(d1)
    
    def _calc_foreign_pips_put_delta(self, K : float, sigma : float) -> float:
        d1 = -(math.log(self.F_0 / K) + 0.5 * sigma * sigma * self.params.T()) / (sigma * math.sqrt(self.params.T()))
        return stats.norm.cdf(-d1)
    
    def _objective_function(self, calibrated_params_list : list[float, ...]) -> float:
        alpha = calibrated_params_list[0]
        nu = calibrated_params_list[1]
        rho = calibrated_params_list[2]
        K_25_d_p = calibrated_params_list[3]
        K_25_d_c = calibrated_params_list[4]
        K_10_d_p = calibrated_params_list[5]
        K_10_d_c = calibrated_params_list[6]
        temp_sabr = SABR_model(self.params, self.F_0, alpha, nu, rho)
        def temp_smile(K : float) -> float:
            return temp_sabr.SABR_smile_function(K)
        sigma_25_d_ss = self.volas.Sigma_ms_25() - self.fly_adjust_param
        sigma_10_d_ss = self.volas.Sigma_ms_10() - self.fly_adjust_param
        return (
            (self.volas.Sigma_atm() - temp_smile(self.K_atm)) ** 2
            + (self.volas.Sigma_rr_25() - (temp_smile(K_25_d_c) - temp_smile(K_25_d_p))) ** 2
            + (self.volas.Sigma_rr_10() - (temp_smile(K_10_d_c) - temp_smile(K_10_d_p))) ** 2
            + (sigma_25_d_ss - (0.5 * (temp_smile(K_25_d_p) + temp_smile(K_25_d_c)) - temp_smile(self.K_atm))) ** 2
            + (sigma_10_d_ss - (0.5 * (temp_smile(K_10_d_p) + temp_smile(K_10_d_c)) - temp_smile(self.K_atm))) ** 2
            + (-0.25 - self._calc_foreign_pips_put_delta(K_25_d_p, temp_smile(K_25_d_p))) ** 2
            + (0.25 - self._calc_foreign_pips_put_delta(K_25_d_p, temp_smile(K_25_d_c))) ** 2
        )

    def _get_model_params(self, ini_calibrated_params : Calibrated_params) -> list[float, ...]:
        ini_calibrated_params_list = [
            ini_calibrated_params.Alpha(),
            ini_calibrated_params.Nu(),
            ini_calibrated_params.Rho(),
            ini_calibrated_params.K_25_d_p(),
            ini_calibrated_params.K_25_d_c(),
            ini_calibrated_params.K_10_d_p(),
            ini_calibrated_params.K_10_d_c()
        ]
        result = minimize(self._objective_function, ini_calibrated_params_list)
        if not result.success:
            raise ValueError("Least squares optimiser is not converges.")
        return Calibrated_params(result.x[0], result.x[1], result.x[2], result.x[3], result.x[4], result.x[5], result.x[6])

    def _is_converges(self, calibrated_params : Calibrated_params, tolerance = 10**(-8)) -> float:
        model = SABR_model(self.params, self.F_0, calibrated_params.Alpha(), calibrated_params.Nu(), calibrated_params.Rho())
        V_target_25 = model.calc_plain_vanilla_price_from_vola(self.K_25_d_p_ms, self.sigma_25_ms, False) + model.calc_plain_vanilla_price_from_vola(self.K_25_d_c_ms, self.sigma_25_ms, True)
        V_trial_25 = model.calc_plain_vanilla_price(self.K_25_d_p_ms, False) + model.calc_plain_vanilla_price(self.K_25_d_c_ms, True)
        V_target_10 = model.calc_plain_vanilla_price_from_vola(self.K_10_d_p_ms, self.sigma_10_ms, False) + model.calc_plain_vanilla_price_from_vola(self.K_10_d_c_ms, self.sigma_10_ms, True)
        V_trial_10 = model.calc_plain_vanilla_price(self.K_10_d_p_ms, False) + model.calc_plain_vanilla_price(self.K_10_d_c_ms, True)
        return abs(V_target_25 - V_trial_25) < tolerance and abs(V_target_10 - V_trial_10) < tolerance

    def calibrate(self, ini_calibrated_params : Calibrated_params) -> SABR_model:
        calibrated_params = ini_calibrated_params
        counter = 0
        while not self._is_converges(calibrated_params) and counter < 1000:
            if counter % 100 == 0:
                print(f"counter : {counter}")
            calibrated_params = self._get_model_params(calibrated_params)
            counter += 1
        if counter >= 1000:
            raise ValueError("This market can not calibrate.")
        else:
            print("converges!")
        return SABR_model(self.params, self.F_0, calibrated_params.Alpha(), calibrated_params.Nu(), calibrated_params.Rho())
