import pytest

pytest.importorskip("numpy")
from qsors.pricing import quantum_qae
from qsors.config import ExperimentConfig


def test_quantum_fallback():
    cfg = ExperimentConfig.model_validate(
        {"experiment": {"pricing": {"classical": {"mc_paths": 1000, "device": "cpu"}}}}
    )
    res = quantum_qae.price("SPY", 30, "-5%", cfg)
    assert "price" in res
