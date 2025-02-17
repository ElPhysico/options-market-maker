import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq
from options_market_maker.pricing.black_scholes import black_scholes_price


def implied_volatility(price_market, S, K, T, r, option_type='call', tol=1e-6):
    """Compute the implied volatility using Brent's method.

    Parameters:
        price_market (float): Market price of option
        S (float): Current stock price
        K (float): Strike price
        T (float): Time-to-expiry (in years)
        r (float): Risk-free interest rate (annualized)
        option_type (str): 'call' or 'put'
        tol (float): Tolerance for the root-finding algorithm

    Returns:
        float: Implied volatility (sigma)
    """
    if T <= 0:
        raise ValueError("Time to expiration (T) must be positive.")
    
    def objective_function(sigma):
        p = black_scholes_price(S, K, T, r, sigma, option_type)
        return p - price_market

    lower_bound = 1e-8 # very close to 0 but still positive
    upper_bound = 1000 # very large to allow for extreme cases

    try:
        iv = brentq(objective_function, lower_bound, upper_bound, xtol=tol)
    except ValueError:
        iv = np.nan

    return iv