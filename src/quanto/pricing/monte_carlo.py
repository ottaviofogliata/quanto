"""Monte Carlo option pricing with optional torch MPS."""

from __future__ import annotations

import math
from typing import Dict

import numpy as np

from ..utils.hw import device_from_config, manual_seed
from ..utils.logging import get_logger

logger = get_logger(__name__)

try:  # torch optional
    import torch
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


def price(ticker: str, dte: int, strike: str, cfg) -> Dict[str, float]:
    """Price an option via Monte Carlo."""
    manual_seed(0)
    S0 = 100.0
    K = S0 * (1 - 0.05) if strike.startswith("-") else S0
    r = 0.01
    sigma = 0.2
    T = dte / 365
    paths = cfg.experiment["pricing"]["classical"]["mc_paths"]
    device_str = cfg.experiment["pricing"]["classical"].get("device", "cpu")
    device = device_from_config(device_str)
    use_torch = device == "mps" and torch is not None
    if use_torch:
        tw = TorchWrapper(device)
        z = tw.randn(paths)
        ST = S0 * tw.exp((r - 0.5 * sigma**2) * T + sigma * math.sqrt(T) * z)
        payoff = torch.clamp(ST - K, min=0.0)
        price = tw.mean(payoff) * math.exp(-r * T)
        price = float(price.cpu().numpy())
    else:
        z = np.random.randn(paths)
        ST = S0 * np.exp((r - 0.5 * sigma**2) * T + sigma * math.sqrt(T) * z)
        payoff = np.maximum(ST - K, 0.0)
        price = payoff.mean() * math.exp(-r * T)
    return {"price": float(price), "device": device}
