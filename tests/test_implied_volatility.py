import json
from pathlib import Path
from options_market_maker.pricing.implied_volatility import implied_volatility


# theoretical tests
def test_implied_volatility_call():
    iv = implied_volatility(price_market=10.45,
                            S=100,
                            K=100,
                            T=1,
                            r=0.05,
                            option_type="call")
    assert round(iv, 2) == 0.2

def test_implied_volatility_put():
    iv = implied_volatility(price_market=5.57,
                            S=100,
                            K=100,
                            T=1,
                            r=0.05,
                            option_type="put")
    assert round(iv, 2) == 0.2

def test_implied_volatility_no_solution():
    iv = implied_volatility(price_market=1000,
                            S=100,
                            K=100,
                            T=1,
                            r=0.05,
                            option_type="call")
    assert iv != iv  # Expect NaN when no solution exists (NaN != NaN)


# tests against real historical market data
ROOT_DIR = Path.cwd()
symbol = 'AAPL'
date = '2023-09-19'
samples_path = ROOT_DIR / f'data/samples/options/{symbol}/{symbol}_{date}.json'
samples = json.loads(samples_path.read_text())

def test_real_implied_volatility_call():
    n = samples['ncalls'] // 2
    option = samples['calls'][n]
    price = (option['bid'] + option['ask']) / 2
    S = samples['symbol_close']
    K = option['strike']
    T = option['time-to-expiry']
    r = 0.055   # risk-free rate is hard-coded from internet
    sigma = option['implied_volatility']
    predicted_sigma = implied_volatility(price, S, K, T, r, 'call')

    assert abs(sigma - predicted_sigma) / sigma < 0.05

def test_real_implied_volatility_put():
    n = samples['nputs'] // 2
    option = samples['puts'][n]
    price = (option['bid'] + option['ask']) / 2
    S = samples['symbol_close']
    K = option['strike']
    T = option['time-to-expiry']
    r = 0.055   # risk-free rate is hard-coded from internet
    sigma = option['implied_volatility']
    predicted_sigma = implied_volatility(price, S, K, T, r, 'put')

    assert abs(sigma - predicted_sigma) / sigma < 0.05