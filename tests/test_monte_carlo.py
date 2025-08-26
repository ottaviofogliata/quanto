import pytest

pytest.importorskip("numpy")
from quanto.pricing import monte_carlo
from quanto.config import ExperimentConfig


@pytest.mark.parametrize("strike", ["-5%", "+5%", "ATM", "105"])
def test_mc_price_close(strike):
    cfg = ExperimentConfig.model_validate(
        {"experiment": {"pricing": {"classical": {"mc_paths": 10000, "device": "cpu"}}}}
    )
    res = monte_carlo.price("SPY", 30, strike, cfg)
    assert res["price"] > 0
    assert res["device"] == "cpu"
