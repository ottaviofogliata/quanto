import pytest

pytest.importorskip("numpy")
pytest.importorskip("scipy")
from qsors.pricing.black_scholes import price_european


def test_put_call_parity():
    S = 100
    K = 100
    r = 0.05
    sigma = 0.2
    T = 30 / 365
    call = price_european(S, K, r, sigma, T, option_type="call")
    put = price_european(S, K, r, sigma, T, option_type="put")
    parity = call.price - put.price
    expected = S - K * pow(2.718281828, -r * T)
    assert abs(parity - expected) < 1e-2
