"""Market data adapters with CSV fallback."""

from __future__ import annotations

DATA = {
    "SPY": 450.0,
    "QQQ": 370.0,
    "IWM": 190.0,
    "HYG": 75.0,
    "GLD": 180.0,
}


def get_spot(ticker: str) -> float:
    """Return a synthetic spot price for *ticker*.

    The function uses a small in-memory mapping as a lightweight stand‑in for a
    real market data provider.  Unknown tickers default to a nominal value so
    that examples and tests continue to function.
    """
    return DATA.get(ticker.upper(), 100.0)


def get_risk_free(rate_source: str = "SOFR") -> float:
    """Return a crude risk‑free rate in decimal form.

    ``rate_source`` is accepted for API completeness but currently unused – the
    function always returns a constant placeholder rate.
    """
    return 0.01


def get_iv(ticker: str, dte: int, strike: str) -> float:
    """Return an implied volatility estimate for ``ticker``.

    The simplified model ignores the supplied parameters and provides a fixed
    value which is sufficient for unit tests and examples.
    """
    return 0.2
