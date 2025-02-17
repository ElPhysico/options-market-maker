import pytest
from options_market_maker.pricing.black_scholes import black_scholes_price, black_scholes_greeks


def test_black_scholes_call():
    price = black_scholes_price(S=100,
                                K=100,
                                T=1,
                                r=0.05,
                                sigma=0.2,
                                option_type='call')
    assert round(price, 2) == 10.45

def test_black_scholes_put():
    price = black_scholes_price(S=100,
                                K=100,
                                T=1,
                                r=0.05,
                                sigma=0.2,
                                option_type='put')
    assert round(price, 2) == 5.57

def test_black_scholes_invalid_option():
    error_string = 'option_type must be "call" or "put"'
    with pytest.raises(ValueError, match=error_string):
        black_scholes_price(S=100,
                            K=100,
                            T=1,
                            r=0.05,
                            sigma=0.2,
                            option_type='invalid')
        
def test_black_scholes_expired_option():
    assert black_scholes_price(S=100,
                               K=100,
                               T=0,
                               r=0.05,
                               sigma=0.2,
                               option_type='call') == max(0, 100 - 100)
    
    assert black_scholes_price(S=100,
                               K=100,
                               T=0,
                               r=0.05,
                               sigma=0.2,
                               option_type='put') == max(0, 100 - 100)
    
def test_black_scholes_negative_expiry():
    error_string = 'Time to expiry \\(T\\) cannot be negative'
    with pytest.raises(ValueError, match=error_string):
        black_scholes_price(S=100,
                            K=100,
                            T=-1,
                            r=0.05,
                            sigma=0.2,
                            option_type='call')
        

def test_black_scholes_greeks():
    greeks = black_scholes_greeks(S=100,
                                  K=100,
                                  T=1,
                                  r=0.05,
                                  sigma=0.2,
                                  option_type='call')
    
    assert round(greeks['Delta'], 2) == 0.64
    assert round(greeks['Gamma'], 4) == 0.0188
    assert round(greeks['Vega'], 2) == 0.38
    assert round(greeks['Theta'], 2) == -0.02
    assert round(greeks['Rho'], 2) == 0.53