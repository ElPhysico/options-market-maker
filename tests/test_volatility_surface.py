import pytest
import numpy as np
from options_market_maker.pricing.volatility_surface import fit_volatility_surface

def test_vol_surface_correct_output():
    """Test that the function returns a callable interpolation function."""
    strikes = np.array([90, 100, 110, 95, 105, 115])
    expiries = np.array([0.5, 0.5, 0.5, 1.0, 1.0, 1.0])
    market_ivs = np.array([0.22, 0.20, 0.21, 0.25, 0.22, 0.23])

    surface_function = fit_volatility_surface(strikes, expiries, market_ivs)
    assert callable(surface_function)

def test_vol_surface_interpolation():
    """Test interpolation between known data points."""
    strikes = np.array([90, 100, 110, 95, 105, 115])
    expiries = np.array([0.5, 0.5, 0.5, 1.0, 1.0, 1.0])
    market_ivs = np.array([0.22, 0.20, 0.21, 0.25, 0.22, 0.23])

    surface_function = fit_volatility_surface(strikes, expiries, market_ivs)
    
    interpolated_iv = surface_function(102, 0.75)
    assert 0.20 < interpolated_iv < 0.25  # Should be within a reasonable range

def test_vol_surface_invalid_input_lengths():
    """Test that function raises ValueError when input lists have different
    lengths."""
    strikes = np.array([90, 100, 110])
    expiries = np.array([0.5, 0.5])  # Different length
    market_ivs = np.array([0.22, 0.20, 0.21])

    with pytest.raises(ValueError, match='Input arrays "strikes", "expiries", and "market_ivs" must have the same length.'):
        fit_volatility_surface(strikes, expiries, market_ivs)

def test_vol_surface_too_few_points():
    """Test that function raises ValueError if there are fewer than 4 data
    points."""
    strikes = np.array([90])
    expiries = np.array([0.5])
    market_ivs = np.array([0.22])

    with pytest.raises(ValueError, match="At least 4 data points are required to fit a volatility surface."):
        fit_volatility_surface(strikes, expiries, market_ivs)

def test_vol_surface_spline_minimum_points():
    """Test that function works correctly with few data points."""
    strikes = np.array([90, 100, 110, 120])
    expiries = np.array([0.5, 0.55, 0.45, 0.5])
    market_ivs = np.array([0.22, 0.2, 0.21, 0.21])

    fit_volatility_surface(strikes, expiries, market_ivs)

def test_vol_surface_one_unique_strike():
    """Test that function warns and defaults to 1D interpolation when only one strike is given."""
    strikes = np.array([100, 100, 100, 100])
    expiries = np.array([0.5, 1.0, 1.5, 2.0])
    market_ivs = np.array([0.22, 0.2, 0.21, 0.23])

    with pytest.warns(UserWarning, match="Only one unique strike price detected. Defaulting to 1D interpolation."):
        surface_function = fit_volatility_surface(strikes, expiries, market_ivs)

    iv_test = surface_function(100, 1.25)
    assert 0.2 < iv_test < 0.23

def test_vol_surface_one_unique_expiry():
    """Test that function warns and defaults to 1D interpolation when only one expiry is given."""
    strikes = np.array([90, 100, 110, 120])
    expiries = np.array([0.5, 0.5, 0.5, 0.5])
    market_ivs = np.array([0.22, 0.2, 0.21, 0.21])

    with pytest.warns(UserWarning, match="Only one unique expiry detected. Defaulting to 1D interpolation."):
        surface_function = fit_volatility_surface(strikes, expiries, market_ivs)

    iv_test = surface_function(105, 0.5)
    assert 0.2 < iv_test < 0.22
