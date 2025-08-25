import pytest
from qsors.portfolio.hilbert import HilbertPortfolio

np = pytest.importorskip("numpy")


def test_hilbert_normalization_and_expectation():
    basis = ["a", "b"]
    amps = np.array([1.0, 1.0])
    hp = HilbertPortfolio(basis, amps)
    assert np.isclose(hp.probs().sum(), 1.0)
    op = np.diag([1.0, 2.0])
    exp = hp.expectation(op)
    assert np.isclose(exp, 1.5)
