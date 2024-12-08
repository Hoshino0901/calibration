import numpy as np 
import numpy.random as npr
import math
import scipy.stats as stats
from scipy.optimize import root_scalar
from FX_params import FX_params

import pdb

class SABR_model:
    def  __init__(self, params : FX_params, F_0 : float, alpha : float, nu : float, rho : float, beta=1.0):
        self.params = params
        self.F_0 = F_0
        self.alpha = alpha
        self.beta = beta
        self.nu = nu
        self.rho = rho
    
    def SABR_params(self) -> dict[float, ...]:
        return {'alpha' : self.alpha, 'beta' : self.beta, 'nu' : self.nu, 'rho' : self.rho}
    
    def SABR_smile_function(self, K) -> float:
        alpha = self.alpha
        beta = self.beta
        nu = self.nu
        rho = self.rho
        F_0 = self.F_0
        T = self.params.T()

        z = nu / alpha * (F_0 * K) ** ((1 - beta) * 0.5) * math.log(F_0 / K)
        temp_for_debag = (math.sqrt(1 - 2 * rho * z + z * z) + z - rho)
        print(f"z : {z}")
        print(f"rho : {rho}")
        print(f"分子 : {temp_for_debag}")
        chi = math.log((math.sqrt(1 - 2 * rho * z + z * z) + z - rho) / (1 - rho))

        sigma_denominator = (F_0 * K) ** ((1 - beta) * 0.5) * (1 + (1 - beta) ** 2 / 24 * (math.log(F_0 / K)) ** 2 + (1 - beta) ** 4 / 1920 * (math.log(F_0 / K)) ** 4)
        sigma_last_part = 1 + ((1 - beta) ** 2 / 24 * alpha * alpha / (F_0 * K) ** (1 - beta) + 0.25 * rho * beta * nu * alpha / (F_0 * K) ** ((1 - beta) * 0.5) + (2 - 3 * rho * rho) / 24 * nu * nu) * T
        return alpha / sigma_denominator * z / chi * sigma_last_part

    def calc_plain_vanilla_price_from_vola(self, K : float, sigma : float, is_call : bool) -> float:
        d1 = (math.log(self.F_0 / K) + 0.5 * sigma * sigma * self.params.T()) / (sigma * math.sqrt(self.params.T()))
        d2 = d1 - sigma * math.sqrt(self.params.T())
        if is_call:
            return math.exp(-self.params.R_d() * self.params.T()) * (self.F_0 * stats.norm.cdf(d1) - K * stats.norm.cdf(d2))
        else:
            return -math.exp(-self.params.R_d() * self.params.T()) * (self.F_0 * stats.norm.cdf(-d1) - K * stats.norm.cdf(-d2))
    
    def calc_plain_vanilla_price(self, K, is_call : bool) -> float:
        vola = self.SABR_smile_function(K)
        return self.calc_plain_vanilla_price_from_vola(K, vola, is_call)