"""Black-Scholes analytic pricing."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class BSResult:
    price: float
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float


def _d1(S: float, K: float, r: float, sigma: float, T: float) -> float:
    return (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))


def _d2(d1: float, sigma: float, T: float) -> float:
    return d1 - sigma * math.sqrt(T)


def price_european(
    S: float,
    K: float,
    r: float,
    sigma: float,
    T: float,
    option_type: str = "call",
) -> BSResult:
    """Return Black-Scholes price and Greeks."""
    from scipy.stats import norm

    d1 = _d1(S, K, r, sigma, T)
    d2 = _d2(d1, sigma, T)
    if option_type == "call":
        price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
        delta = norm.cdf(d1)
    else:
        price = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        delta = norm.cdf(d1) - 1
    gamma = norm.pdf(d1) / (S * sigma * math.sqrt(T))
    theta = (
        -(S * norm.pdf(d1) * sigma) / (2 * math.sqrt(T))
        - r * K * math.exp(-r * T) * norm.cdf(d2 if option_type == "call" else -d2)
    ) / 365
    vega = S * norm.pdf(d1) * math.sqrt(T) / 100
    rho = (
        K * T * math.exp(-r * T) * norm.cdf(d2 if option_type == "call" else -d2) / 100
    )
    return BSResult(price, delta, gamma, theta, vega, rho)
