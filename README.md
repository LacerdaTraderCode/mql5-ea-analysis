# MQL5 EA + Python Analysis

A moving-average-crossover Expert Advisor for MetaTrader 5, written in MQL5, paired with a Polars-based Python pipeline that analyzes the trade log it exports.

## What's here

- **`ea/MovingAverageCrossoverEA.mq5`** — a real, complete MQL5 Expert Advisor: fast/slow EMA crossover entries, percent-risk position sizing from the stop-loss distance, and a CSV trade log written from `OnTradeTransaction` so every closed trade is captured, however it closed.
- **`analysis/`** — loads that CSV with Polars and computes win rate, profit factor, expectancy, and max drawdown.
- **`sample_data/ma_crossover_trades_sample.csv`** — a generated example log in the EA's exact export schema, since this environment cannot compile or run MQL5 to produce a real one. See [`docs/architecture.md`](docs/architecture.md) for the honest story on that.

## Running the EA

Copy `ea/MovingAverageCrossoverEA.mq5` into a MetaTrader 5 terminal's `MQL5/Experts` folder, compile it in MetaEditor, and attach it to a chart (or run it in the Strategy Tester). Trades close out to `MQL5/Files/Common/ma_crossover_trades.csv`, shared across every terminal on the machine.

## Running the analysis

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m scripts.analyze_trades sample_data/ma_crossover_trades_sample.csv
```

```
Trades:               80
Win rate:             53.8%
Profit factor:        1.31
Expectancy per trade: 2.76
Max drawdown:         1.2%
```

Point it at a real export from the EA the same way.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

The suite covers trade-log validation, every metric against hand-checked values (including that a profit-factor with no losing trades returns infinity rather than dividing by zero), and that the sample generator's logged profit and running balance always agree exactly.

## License

MIT — see [LICENSE](LICENSE).
