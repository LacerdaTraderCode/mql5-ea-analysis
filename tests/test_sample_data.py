"""Tests for the synthetic sample trade log generator."""

from analysis.sample_data import generate_sample_trade_log
from analysis.trade_log import EXPECTED_COLUMNS


def test_generates_the_requested_number_of_trades():
    trades = generate_sample_trade_log(trade_count=25, seed=1)

    assert trades.height == 25


def test_output_matches_the_trade_log_schema_the_ea_exports():
    trades = generate_sample_trade_log(trade_count=5, seed=1)

    assert set(trades.columns) == set(EXPECTED_COLUMNS)


def test_the_same_seed_produces_the_same_trade_log():
    first = generate_sample_trade_log(trade_count=30, seed=7)
    second = generate_sample_trade_log(trade_count=30, seed=7)

    assert first.equals(second)


def test_balance_after_reflects_the_cumulative_profit():
    trades = generate_sample_trade_log(trade_count=20, starting_balance=1000.0, seed=3)

    running_balance = 1000.0
    for row in trades.iter_rows(named=True):
        running_balance += row["profit"]
        assert round(running_balance, 2) == round(row["balance_after"], 2)
