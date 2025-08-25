"""Very small backtest engine."""

from __future__ import annotations

import random
from typing import Dict

from ..utils.logging import get_logger

logger = get_logger(__name__)


def run_backtest(cfg) -> Dict[str, float]:
    random.seed(0)
    days = 10
    pnl = [random.gauss(0, 1) for _ in range(days)]
    total = sum(pnl)
    return {"days": days, "pnl": total}
