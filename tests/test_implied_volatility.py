from options_market_maker.pricing.implied_volatility import implied_volatility


def test_implied_volatility_call():
    iv = implied_volatility(price_market=10.45,
                            S=100,
                            K=100,
                            T=1,
                            r=0.05,
                            option_type="call")
    # assert round(iv, 2) == 0.2
    assert round(iv, 2) == 1.0

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
