from typer.testing import CliRunner

from quanto.cli import app


def test_optimize_stocks_requires_tickers():
    runner = CliRunner()
    result = runner.invoke(app, ["optimize", "--asset-class", "stocks"])
    assert result.exit_code != 0
    assert "tickers required" in result.output.lower()
