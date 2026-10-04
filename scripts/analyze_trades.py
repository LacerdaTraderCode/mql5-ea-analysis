"""CLI: loads an exported trade log CSV and prints a performance report.

Usage:
    python -m scripts.analyze_trades sample_data/ma_crossover_trades_sample.csv
"""

import sys

from analysis.metrics import expectancy, max_drawdown, profit_factor, win_rate
from analysis.trade_log import load_trade_log


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python -m scripts.analyze_trades path/to/trades.csv", file=sys.stderr)
        raise SystemExit(1)

    trades = load_trade_log(sys.argv[1])

    print(f"Trades:               {trades.height}")
    print(f"Win rate:             {win_rate(trades):.1%}")
    print(f"Profit factor:        {profit_factor(trades):.2f}")
    print(f"Expectancy per trade: {expectancy(trades):.2f}")
    print(f"Max drawdown:         {max_drawdown(trades):.1%}")


if __name__ == "__main__":
    main()
