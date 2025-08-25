"""Hardware detection and memory guards."""

from __future__ import annotations

from typing import Optional

try:
    import torch  # type: ignore[import-not-found]
except Exception:  # pragma: no cover - torch optional
    torch = None  # type: ignore


TOTAL_MEMORY_BYTES = 36 * 1024**3
SAFE_FRACTION = 0.6


def has_mps() -> bool:
    """Return True if torch with MPS backend is available."""
    return bool(
        torch
        and getattr(torch.backends, "mps", None)
        and torch.backends.mps.is_available()
    )


def device_from_config(device_str: str) -> str:
    """Resolve device string respecting availability."""
    if device_str == "mps":
        return "mps" if has_mps() else "cpu"
    if device_str == "auto":
        return "mps" if has_mps() else "cpu"
    return "cpu"


def memory_guard(num_states: int, bytes_per_amp: int = 16) -> None:
    """Guard against allocations that exceed safe memory threshold."""
    required = num_states * bytes_per_amp
    if required > TOTAL_MEMORY_BYTES * SAFE_FRACTION:
        raise MemoryError("State vector allocation exceeds safe memory threshold")


def manual_seed(seed: Optional[int] = None) -> None:
    """Seed numpy and torch if available."""
    import numpy as np

    if seed is None:
        seed = 0
    np.random.seed(seed)
    if torch:
        torch.manual_seed(seed)
