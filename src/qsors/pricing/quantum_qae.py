"""Quantum Amplitude Estimation stub with classical fallback."""

from __future__ import annotations

from typing import Dict

from ..utils.logging import get_logger
from . import monte_carlo

logger = get_logger(__name__)

try:  # optional quantum dependencies
    from qiskit import QuantumCircuit
    from qiskit.primitives import Estimator
except Exception:  # pragma: no cover
    QuantumCircuit = None  # type: ignore
    Estimator = None  # type: ignore


def price(ticker: str, dte: int, strike: str, cfg) -> Dict[str, float]:
    """Return price using QAE or fallback Monte Carlo."""
    if QuantumCircuit is None:
        logger.warning("QAE unavailable; using variance-reduced Monte Carlo fallback.")
        return monte_carlo.price(ticker, dte, strike, cfg)
    # Minimal stub since real QAE is expensive; just demonstrate interface.
    # Build trivial circuit estimating expected payoff using two qubits.
    circ = QuantumCircuit(2)
    # For simplicity we just simulate expectation via Estimator of Pauli Z.
    est = Estimator()
    result = est.run([circ], observables="Z" * 2).result()
    value = result.values[0]
    return {"price": float(value), "device": "qiskit_simulator"}
