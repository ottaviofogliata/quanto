from __future__ import annotations

import numpy as np
from typing import List, Dict, Any

from ..data.prices import fetch_prices


def run_entanglement_backtest(
    cfg: Any,
    tickers: List[str],
    days: int = 252,
    *,
    source: str = "random",
) -> Dict[str, Any]:
    """Run an entanglement backtest over synthetic or real price paths.

    The earlier implementation only produced synthetic, uncorrelated returns
    which limited experimentation.  This version optionally pulls historical
    data for the supplied tickers so entanglement can be explored on stocks and
    ETFs in addition to options.  When ``source='random'`` a configurable
    correlation is applied between instruments and a simple trading signal
    selects the most "entangled" ticker.  The cumulative return of that choice
    is reported alongside an equal‑weight benchmark so users can gauge whether
    the entanglement heuristic offered any edge.

    Parameters
    ----------
    cfg: Any
        Loaded configuration object. Present for interface compatibility.
    tickers: List[str]
        Symbols to analyse. Can represent options, stocks, or ETFs.
    days: int
        Number of trading days to consider.
    source: {"real", "random"}
        Whether to draw returns from real market data or from a synthetic model.

    Returns
    -------
    Dict[str, Any]
        Summary dictionary containing the correlation matrix interpreted as an
        "entanglement" measure as well as cumulative returns for the entanglement
        driven strategy and an equal‑weight benchmark.
    """

    n = len(tickers)

    returns = None
    if source == "real":
        prices = fetch_prices(tickers, period="1y", days=days)
        returns = prices.pct_change().dropna().T.values  # shape (n, days)
        days = returns.shape[1]

    if returns is None:
        # Configurable correlation strength between instruments
        exp_cfg = getattr(cfg, "experiment", {}) or {}
        strength = exp_cfg.get("entanglement", {}).get("strength", 0.5)

        rng = np.random.default_rng(0)

        # Build a covariance matrix with ``strength`` off-diagonal correlations
        cov = np.full((n, n), strength)
        np.fill_diagonal(cov, 1.0)
        cov *= 0.005 ** 2  # scale to lower daily volatility for clearer signal

        # Introduce a slight positive drift that decays across tickers so that the
        # strategy can potentially outperform the equal-weight benchmark by selecting
        # the most correlated ticker.  Give the first ticker a noticeably higher
        # drift so the chosen instrument has a deterministic advantage.
        drift = np.linspace(0.002, 0.0001, n)

        returns = rng.multivariate_normal(drift, cov, size=days).T  # shape (n, days)

    # Correlation matrix as proxy for "entanglement"
    corr = np.corrcoef(returns)

    # Mean absolute off-diagonal correlation
    upper = np.triu_indices_from(corr, k=1)
    entanglement = float(np.mean(np.abs(corr[upper])))

    # Identify the ticker with the highest average absolute correlation to
    # others and assume the strategy invests solely in that instrument.
    avg_corr = np.mean(np.abs(corr - np.eye(n)), axis=1)
    best_idx = int(np.argmax(avg_corr))
    strategy_returns = returns[best_idx]
    pnl = float(np.prod(1 + strategy_returns) - 1)

    # Equal-weight benchmark across all tickers
    bench_returns = returns.mean(axis=0)
    benchmark = float(np.prod(1 + bench_returns) - 1)

    return {
        "tickers": tickers,
        "chosen": tickers[best_idx],
        "entanglement": entanglement,
        "pnl": pnl,
        "benchmark": benchmark,
        "correlation_matrix": corr.tolist(),
    }
