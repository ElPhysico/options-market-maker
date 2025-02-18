import json
from pathlib import Path
import pytest
from options_market_maker.pricing.black_scholes import black_scholes_price, black_scholes_greeks


# theoretical tests
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


# tests against real historical market data
ROOT_DIR = Path.cwd()
symbol = 'AAPL'
date = '2023-09-19'
samples_path = ROOT_DIR / f'data/samples/options/{symbol}/{symbol}_{date}.json'
samples = json.loads(samples_path.read_text())

def test_real_black_scholes_call():
    n = samples['ncalls'] // 2
    option = samples['calls'][n]
    price = (option['bid'] + option['ask']) / 2
    S = samples['symbol_close']
    K = option['strike']
    T = option['time-to-expiry']
    r = 0.055   # risk-free rate is hard-coded from internet
    sigma = option['implied_volatility']
    predicted_price = black_scholes_price(S, K, T, r, sigma, 'call')

    assert abs(price - predicted_price) / price < 0.05

def test_real_black_scholes_put():
    n = samples['nputs'] // 2
    option = samples['puts'][n]
    price = (option['bid'] + option['ask']) / 2
    S = samples['symbol_close']
    K = option['strike']
    T = option['time-to-expiry']
    r = 0.055   # risk-free rate is hard-coded from internet
    sigma = option['implied_volatility']
    predicted_price = black_scholes_price(S, K, T, r, sigma, 'put')

    assert abs(price - predicted_price) / price < 0.05

def test_real_black_scholes_greeks():
    # calls greeks
    n = samples['ncalls'] // 2
    option = samples['calls'][n]
    S = samples['symbol_close']
    K = option['strike']
    T = option['time-to-expiry']
    r = 0.055   # risk-free rate is hard-coded from internet
    sigma = option['implied_volatility']
    greeks = black_scholes_greeks(S, K, T, r, sigma, 'call')
    for g in greeks:
        assert abs(option[g] - greeks[g]) / option[g] < 0.05

    # puts greeks
    n = samples['nputs'] // 2
    option = samples['puts'][n]
    S = samples['symbol_close']
    K = option['strike']
    T = option['time-to-expiry']
    r = 0.055   # risk-free rate is hard-coded from internet
    sigma = option['implied_volatility']
    greeks = black_scholes_greeks(S, K, T, r, sigma, 'put')
    for g in greeks:
        assert abs(option[g] - greeks[g]) / option[g] < 0.05