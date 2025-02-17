import numpy as np
from scipy.stats import norm


def black_scholes_price(S, K, T, r, sigma, option_type='call'):
    """Compute the Black-Scholes price for European call or put options.

    Parameters:
        S (float): Current stock price
        K (float): Strike price
        T (float): Time-to-expiry (in years)
        r (float): Risk-free interest rate (annualized)
        sigma (float): Volatility of underlying asset (annualized)
        option_type (str): 'call' or 'put'

    Returns:
        float: Option price
    """
    if T < 0:
        raise ValueError('Time to expiry (T) cannot be negative')

    if T == 0:
        return max(0, S - K) if option_type == 'call' else max(0, K - S)
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == 'call':
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    elif option_type == 'put':
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    else:
        raise ValueError('option_type must be "call" or "put"')
    

def black_scholes_greeks(S, K, T, r, sigma, option_type='call'):
    """Compute the Greeks (Delta, Gamma, Vega, Theta, Rho) for European options.

    Parameters:
        S (float): Current stock price
        K (float): Strike price
        T (float): Time-to-expiry (in years)
        r (float): Risk-free interest rate (annualized)
        sigma (float): Volatility of underlying asset (annualized)
        option_type (str): 'call' or 'put'

    Returns:
        dict: A dictionary containing the values of all Greeks.
    """
    if T < 0:
        raise ValueError('Time to expiry (T) cannot be negative')
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    # V = option price, d -> partial derivative
    # delta = dV / dS
    delta = norm.cdf(d1) if option_type == 'call' else norm.cdf(d1) - 1
    # gamma = ddelta / dS
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    # vega = dV / dsigma
    vega = S * norm.pdf(d1) * np.sqrt(T)
    # theta dV / dT
    theta_call = - S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
    theta_call -= r * K * np.exp(-r * T) * norm.cdf(d2)
    theta_put = - S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
    theta_put += r * K * np.exp(-r * T) * norm.cdf(-d2)
    theta = theta_call if option_type == 'call' else theta_put
    # rho = dV / dr
    rho_call = K * T * np.exp(-r*T) * norm.cdf(d2)
    rho_put = -K * T * np.exp(-r*T) * norm.cdf(-d2)
    rho = rho_call if option_type == 'call' else rho_put

    return {
        "Delta": delta,
        "Gamma": gamma,
        "Vega": vega / 100, # per 1% change in volatility
        "Theta": theta / 365, # per day
        "Rho": rho / 100 # per 1% change in interest rate
    }
