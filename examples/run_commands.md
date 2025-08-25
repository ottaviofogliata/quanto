# Example commands

```bash
poetry run quanto price --ticker SPY --dte 30 --strike -5% --method classical --config examples/config.yaml
poetry run quanto price --ticker SPY --dte 30 --strike -5% --method quantum --config examples/config.yaml
poetry run quanto optimize --config examples/config.yaml
poetry run quanto backtest --config examples/config.yaml
poetry run quanto hilbert-demo --config examples/config.yaml
```
