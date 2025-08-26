"""Monte Carlo option pricing with optional torch MPS.

Uses antithetic variates to reduce variance when sampling."""

from __future__ import annotations

import math
from typing import Dict

import numpy as np

from ..utils.hw import device_from_config, manual_seed
from ..utils.logging import get_logger

logger = get_logger(__name__)

try:  # torch optional
    import torch  # type: ignore[import-not-found]
except Exception:  # pragma: no cover
    torch = None  # type: ignore


class TorchWrapper:
    """Thin wrapper mapping numpy API to torch."""

    def __init__(self, device: str):
        self.device = torch.device(device)

    def randn(self, *shape: int) -> torch.Tensor:
        return torch.randn(*shape, device=self.device)

    def exp(self, t: torch.Tensor) -> torch.Tensor:
        return torch.exp(t)

    def mean(self, t: torch.Tensor) -> torch.Tensor:
        return t.mean()

    def to_numpy(self, t: torch.Tensor) -> np.ndarray:
        return t.cpu().numpy()


def price(ticker: str, dte: int, strike: str, cfg) -> Dict[str, float | str]:
    """Price an option via Monte Carlo."""
    manual_seed(0)  # ensure reproducible runs for tests and examples
    S0 = 100.0  # spot price placeholder
    # Support a range of strike expressions like "-5%", "+5%", "ATM" or
    # absolute numeric strikes.  Anything unrecognised defaults to at-the-money.
    expr = strike.strip().upper()
    if expr == "ATM":
        K = S0
    elif expr.endswith("%"):
        try:
            pct = float(expr.strip("%")) / 100.0
            K = S0 * (1 + pct)
        except ValueError:
            K = S0
    else:
        try:
            K = float(expr)
        except ValueError:
            K = S0
    r = 0.01  # risk-free rate
    sigma = 0.2  # volatility
    T = dte / 365  # convert days-to-expiry to years
    paths = cfg.experiment["pricing"]["classical"]["mc_paths"]
    device_str = cfg.experiment["pricing"]["classical"].get("device", "cpu")
    device = device_from_config(device_str)
    # Use torch on Apple silicon when available, otherwise fall back to numpy
    use_torch = device == "mps" and torch is not None
    if use_torch:
        tw = TorchWrapper(device)
        half = paths // 2
        # Generate half the random draws and reuse their negation for antithetic
        # variates, reducing variance without doubling cost
        z_half = tw.randn(half)
        z = torch.cat([z_half, -z_half])
        if paths % 2:
            z = torch.cat([z, tw.randn(1)])
        ST = S0 * tw.exp((r - 0.5 * sigma**2) * T + sigma * math.sqrt(T) * z)
        payoff = torch.clamp(ST - K, min=0.0)
        price = tw.mean(payoff) * math.exp(-r * T)
        price = float(price.cpu().numpy())
    else:
        half = paths // 2
        # Same antithetic variates approach for the numpy implementation
        z_half = np.random.randn(half)
        z = np.concatenate([z_half, -z_half])
        if paths % 2:
            z = np.append(z, np.random.randn(1))
        ST = S0 * np.exp((r - 0.5 * sigma**2) * T + sigma * math.sqrt(T) * z)
        payoff = np.maximum(ST - K, 0.0)
        price = payoff.mean() * math.exp(-r * T)
    return {"price": float(price), "device": device}
