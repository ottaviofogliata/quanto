# Example commands

```bash
poetry run qsors price --ticker SPY --dte 30 --strike -5% --method classical --config examples/config.yaml
poetry run qsors price --ticker SPY --dte 30 --strike -5% --method quantum --config examples/config.yaml
poetry run qsors optimize --config examples/config.yaml
poetry run qsors backtest --config examples/config.yaml
poetry run qsors hilbert-demo --config examples/config.yaml
```
