import pytest

pytest.importorskip("numpy")
from qsors.pricing import monte_carlo
from qsors.config import ExperimentConfig


def test_mc_price_close():
    cfg = ExperimentConfig.model_validate(
        {"experiment": {"pricing": {"classical": {"mc_paths": 10000, "device": "cpu"}}}}
    )
    res = monte_carlo.price("SPY", 30, "-5%", cfg)
    assert res["price"] > 0
    assert res["device"] == "cpu"
