"""Model portfolio as state in Hilbert space."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

try:
    import numpy as np
except Exception:  # pragma: no cover
    np = None  # type: ignore


@dataclass
class HilbertPortfolio:
    basis: List[str]
    amplitudes: np.ndarray

    def __post_init__(self) -> None:
        if np is None:
            raise ImportError("numpy is required for HilbertPortfolio")
        amps = np.asarray(self.amplitudes, dtype=float)
        if amps.shape[0] != len(self.basis):
            raise ValueError("Amplitude count does not match basis")
        norm = np.linalg.norm(amps)
        if norm == 0:
            raise ValueError("Zero vector")
        self.amplitudes = amps / norm

    def expectation(self, operator: np.ndarray) -> float:
        vec = self.amplitudes
        return float(np.vdot(vec, operator @ vec))

    def project(self, indices: Iterable[int]) -> "HilbertPortfolio":
        idx = list(indices)
        new_basis = [self.basis[i] for i in idx]
        new_amps = self.amplitudes[idx]
        return HilbertPortfolio(new_basis, new_amps)

    def probs(self) -> np.ndarray:
        return np.abs(self.amplitudes) ** 2

    def pretty(self) -> str:
        lines = ["Basis state amplitudes:"]
        for b, a, p in zip(self.basis, self.amplitudes, self.probs()):
            lines.append(f"|{b}>: amp={a:.3f}, p={p:.3f}")
        return "\n".join(lines)
