"""Tests for loading and validating an exported trade log."""

import pytest

from analysis.trade_log import load_trade_log


def test_loads_the_shipped_sample_file():
    trades = load_trade_log("sample_data/ma_crossover_trades_sample.csv")

    assert trades.height == 80
    assert "profit" in trades.columns


def test_close_time_is_parsed_as_a_datetime():
    trades = load_trade_log("sample_data/ma_crossover_trades_sample.csv")

    assert trades["close_time"].dtype.is_temporal()


def test_raises_a_clear_error_when_a_required_column_is_missing(tmp_path):
    bad_file = tmp_path / "bad_log.csv"
    bad_file.write_text("close_time,symbol,profit\n2026.01.01 00:00:00,EURUSD,10.0\n")

    with pytest.raises(ValueError, match="missing expected columns"):
        load_trade_log(str(bad_file))
