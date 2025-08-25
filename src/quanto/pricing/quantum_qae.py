"""Quantum Amplitude Estimation stub with classical fallback."""

from __future__ import annotations

from typing import Dict

from ..utils.logging import get_logger
from . import monte_carlo

logger = get_logger(__name__)

try:  # optional quantum dependencies
    from qiskit import QuantumCircuit  # type: ignore[import-untyped]
    from qiskit.primitives import Estimator  # type: ignore[import-untyped]
    from qiskit.quantum_info import SparsePauliOp  # type: ignore[import-untyped]
except Exception:  # pragma: no cover
    QuantumCircuit = None  # type: ignore
    Estimator = None  # type: ignore
    SparsePauliOp = None  # type: ignore


def price(ticker: str, dte: int, strike: str, cfg) -> Dict[str, float | str]:
    """Return price using a toy QAE circuit or Monte Carlo fallback."""
    if QuantumCircuit is None or Estimator is None or SparsePauliOp is None:
        logger.warning("QAE unavailable; using variance-reduced Monte Carlo fallback.")
        return monte_carlo.price(ticker, dte, strike, cfg)

    # Minimal stub: encode payoff amplitude on one qubit and estimate it.
    circ = QuantumCircuit(1)
    circ.rx(0.5, 0)
    est = Estimator()
    op = SparsePauliOp("Z")
    result = est.run(circ, op).result()
    value = (1 - result.values[0]) / 2  # map expectation to probability
    return {"price": float(value), "device": "qiskit_simulator"}
