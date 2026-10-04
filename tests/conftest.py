"""Shared pytest fixtures for the test suite."""

import pytest

from analysis.sample_data import generate_sample_trade_log


@pytest.fixture
def sample_trades():
    return generate_sample_trade_log(trade_count=80, seed=42)
