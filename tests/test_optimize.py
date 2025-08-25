from quanto.optimize import milp, qaoa
from quanto.config import ExperimentConfig

CFG = ExperimentConfig.model_validate({"experiment": {"constraints": {"budget": 1500}}})


def test_milp():
    res = milp.optimize(CFG)
    assert isinstance(res["selection"], list)


def test_qaoa():
    res = qaoa.optimize(CFG)
    assert isinstance(res["selection"], list)
