"""Performance metrics computed from a trade log, expressed as Polars operations."""

import polars as pl


def win_rate(trades: pl.DataFrame) -> float:
    if trades.height == 0:
        return 0.0
    wins = trades.filter(pl.col("profit") > 0).height
    return wins / trades.height


def profit_factor(trades: pl.DataFrame) -> float:
    gross_profit = trades.filter(pl.col("profit") > 0)["profit"].sum() or 0.0
    gross_loss = trades.filter(pl.col("profit") < 0)["profit"].sum() or 0.0

    if gross_loss == 0:
        return float("inf") if gross_profit > 0 else 0.0
    return gross_profit / abs(gross_loss)


def expectancy(trades: pl.DataFrame) -> float:
    if trades.height == 0:
        return 0.0
    return trades["profit"].mean()


def max_drawdown(trades: pl.DataFrame) -> float:
    """The largest peak-to-trough drop in `balance_after`, as a fraction of the peak."""
    if trades.height == 0:
        return 0.0

    with_drawdown = (
        trades.sort("close_time")
        .with_columns(running_peak=pl.col("balance_after").cum_max())
        .with_columns(
            drawdown=(pl.col("running_peak") - pl.col("balance_after")) / pl.col("running_peak")
        )
    )
    return float(with_drawdown["drawdown"].max())
