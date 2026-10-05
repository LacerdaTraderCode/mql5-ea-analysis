"""Tests for the trade performance metrics."""

import polars as pl

from analysis.metrics import expectancy, max_drawdown, profit_factor, win_rate


def _trades(profits: list[float], balances: list[float]) -> pl.DataFrame:
    return pl.DataFrame(
        {
            "close_time": [f"2026.01.{i + 1:02d} 00:00:00" for i in range(len(profits))],
            "profit": profits,
            "balance_after": balances,
        }
    )


def test_win_rate_counts_only_profitable_trades():
    trades = _trades(profits=[10, -5, 20, -15], balances=[10, 5, 25, 10])

    assert win_rate(trades) == 0.5


def test_win_rate_on_an_empty_log_is_zero():
    trades = _trades(profits=[], balances=[])

    assert win_rate(trades) == 0.0


def test_profit_factor_is_gross_profit_over_gross_loss():
    trades = _trades(profits=[30, 10, -10, -10], balances=[30, 40, 30, 20])

    assert profit_factor(trades) == 2.0


def test_profit_factor_is_infinite_with_no_losing_trades():
    trades = _trades(profits=[10, 20], balances=[10, 30])

    assert profit_factor(trades) == float("inf")


def test_expectancy_is_the_average_profit_per_trade():
    trades = _trades(profits=[10, -4, 6], balances=[10, 6, 12])

    assert round(expectancy(trades), 4) == 4.0


def test_max_drawdown_measures_the_deepest_drop_from_a_prior_peak():
    # Balance goes 100 -> 150 (peak) -> 90 -> 120; the deepest drop is from
    # the 150 peak down to 90, a 40% drawdown.
    trades = _trades(profits=[50, -60, 30], balances=[150, 90, 120])

    assert round(max_drawdown(trades), 4) == round((150 - 90) / 150, 4)


def test_max_drawdown_on_an_always_rising_balance_is_zero():
    trades = _trades(profits=[10, 10, 10], balances=[110, 120, 130])

    assert max_drawdown(trades) == 0.0


def test_metrics_are_well_formed_on_the_shipped_sample_data(sample_trades):
    assert 0.0 <= win_rate(sample_trades) <= 1.0
    assert profit_factor(sample_trades) >= 0.0
    assert 0.0 <= max_drawdown(sample_trades) <= 1.0
