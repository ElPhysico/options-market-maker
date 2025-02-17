import numpy as np
import warnings
from scipy.interpolate import SmoothBivariateSpline, interp1d

def fit_volatility_surface(strikes, expiries, market_ivs, smoothing=0.1):
    """
    Fits a smooth volatility surface to given implied volatility data for a
    single underlying using spline interpolation.

    Parameters:
        strikes (array): List of strike prices.
        expiries (array): List of time-to-expiry values.
        market_ivs (array): Corresponding implied volatilities.
        smoothing (float, optional): Smoothing factor for the spline fit.
    
    Returns:
        surface_function (callable): A function sigma(K, T) that interpolates IVs.

    Raises:
        ValueError: If input arrays have different lengths or fewer than 1 data points.
    """

    strikes = np.asarray(strikes)
    expiries = np.asarray(expiries)
    market_ivs = np.asarray(market_ivs)

    if not (len(strikes) == len(expiries) == len(market_ivs)):
        raise ValueError('Input arrays "strikes", "expiries", and "market_ivs" must have the same length.')

    num_points = len(strikes)

    if num_points < 4:
        raise ValueError("At least 4 data points are required to fit a volatility surface.")
    
    unique_strikes = np.unique(strikes)
    unique_expiries = np.unique(expiries)

    if len(unique_strikes) == 1:
        warnings.warn("Only one unique strike price detected. Defaulting to 1D interpolation.", UserWarning)
        interp_1d = interp1d(expiries, market_ivs, kind="linear", fill_value="extrapolate")

        def surface_function(K, T):
            return interp_1d(T)  # Use 1D interpolation on expiry time

        return surface_function

    if len(unique_expiries) == 1:
        warnings.warn("Only one unique expiry detected. Defaulting to 1D interpolation.", UserWarning)
        interp_1d = interp1d(strikes, market_ivs, kind="linear", fill_value="extrapolate")

        def surface_function(K, T):
            return interp_1d(K)  # Use 1D interpolation on strike price

        return surface_function

    if num_points < 9:
        kx, ky = 1, 1  # Linear spline
    elif num_points < 16:
        kx, ky = 2, 2  # Quadratic spline
    else:
        kx, ky = 3, 3  # Full cubic spline

    spline_fit = SmoothBivariateSpline(strikes, expiries, market_ivs, kx=kx, ky=ky, s=smoothing)

    def surface_function(K, T):
        return spline_fit.ev(K, T)

    return surface_function
